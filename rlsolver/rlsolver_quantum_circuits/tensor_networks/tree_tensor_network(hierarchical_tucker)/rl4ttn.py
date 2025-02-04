import torch
import torch as th
import torch.nn as nn
import numpy as np
# from functorch import vmap
from copy import deepcopy

np.set_printoptions(suppress=True)


class Env():
    def __init__(self, N=31, episode_length=6, num_env=100, max_dim=2, epsilon=0.9, device=torch.device("cuda:0")):
        self.N = N
        def power_of_two(n):
            count = 0
            while n > 1:
                if n % 2 == 1:
                    return None
                count += 1
                n //= 2
            return count
        self.X = (power_of_two(self.N + 1))
        self.device = device
        self.num_env = num_env
        self.episode_length = episode_length
        self.max_dim = max_dim
        self.mask_state = th.zeros(self.N + 2, self.N + 2).to(self.device)
        for i in range(1, 2 ** (self.X - 1)):
            self.mask_state[(i * 2), i] = 1
            self.mask_state[(i * 2) + 1, i] = 1
        self.mask_state = self.mask_state.reshape(-1).repeat(1, self.num_env).reshape(self.num_env, self.N + 2,
                                                                                      self.N + 2).to(self.device)
        with open(f"test_data_tensor_ring_N={N}.pkl", 'rb') as f:
            import pickle as pkl
            self.test_state = pkl.load(f)
        self.permute_base = th.as_tensor([i for i in range(self.N - 1)]).repeat(1, self.num_env).reshape(self.num_env,
                                                                                                         -1).to(
            self.device)
        self.zero = th.zeros(self.N - 1).to(self.device)
        self.epsilon = epsilon

    def reset(self, test=False):
        if test:
            self.num_env = self.test_state.shape[0]
        else:
            self.num_env = self.permute_base.shape[0]
        self.state = torch.randint(0, self.max_dim, (self.num_env, self.N + 2, self.N + 2), device=self.device).to(
            torch.float32)
        self.state = th.mul(self.state, self.mask_state[:self.num_env])
        self.state += th.ones_like(self.state)
        self.reward = th.zeros(self.num_env, self.episode_length).to(self.device)
        self.reward_no_prob = th.zeros(self.num_env, self.episode_length).to(self.device)
        self.if_test = test
        self.stend = torch.zeros((self.N, self.N), device=self.device).to(
            torch.float32)
        for i in range(1, self.N):
            self.stend[i, i] = 1
        self.stend = self.stend.reshape(-1).repeat(1, self.num_env).reshape(self.num_env, self.N,
                                                                                      self.N).to(self.device)
        self.mask = th.ones(self.num_env, self.N - 1).to(self.device)
        if test:
            self.state = deepcopy(self.test_state)
            # print(self.test_state)
        self.num_steps = 0
        self.done = False
        initial_action = th.rand(self.num_env, self.N - 1).to(self.device)
        initial_action /= initial_action.sum(dim=-1, keepdim=True)
        return (self.state, self.stend, self.mask, initial_action)

    def step(self, action):
        reward = 0
        reward_no_prob = 0
        mask = deepcopy(self.mask)
        action_mask = th.mul(mask, action)
        action_mask = action_mask / action_mask.sum(dim=-1, keepdim=True)
        # if self.if_test:
        #     print(self.state)


        # order
        if self.if_test:
            print(self.num_steps, action_mask[0].detach().cpu().numpy(), self.reward_no_prob[0].detach().cpu().numpy(),
                  self.epsilon)
        for k in range(action.shape[0]):
            state = self.state[k]
            x = th.rand(1).item()
            if x > self.epsilon or self.if_test:
                selected_edge_id = th.max(action_mask[k], dim=-1)[1].item()
            else:
                selected_edge_id = th.randint(low=0, high=self.N - 1, size=(1, 1)).item()
            self.mask[k, selected_edge_id] = 0
            r = 1
            if ((selected_edge_id // 2 + 1) * 2 < self.N):
                r = r * state[(selected_edge_id // 2 + 1) * 2, selected_edge_id // 2 + 1] * state[(selected_edge_id // 2 + 1) * 2 + 1, selected_edge_id // 2 + 1] \
                    * state[(selected_edge_id // 2 + 1), (selected_edge_id // 2 + 1) // 2]
            if ((selected_edge_id + 2) * 2 < self.N):
                r = r * state[(selected_edge_id + 2) * 2, (selected_edge_id + 2)] * state[(selected_edge_id + 2) * 2 + 1, (selected_edge_id + 2)]
            # if self.if_test:
            #     print(state)
            #     print(self.start, self.end)1
            # if (self.stend[k, tmp1 - 1, selected_edge_id + 1] == 1):
            #     r = r *
            # if (self.stend[k, tmp1, selected_edge_id + 1] == 1):
            #     r = r *
            if ((selected_edge_id + 2) * 2 < self.N and self.stend[k, selected_edge_id // 2 + 1, (selected_edge_id) // 2] == 1):
                r = r * state[(selected_edge_id + 2) * 2, selected_edge_id // 2 + 2] * state[(selected_edge_id + 2) * 2 + 1, selected_edge_id // 2 + 1]
            if ((selected_edge_id + 3) * 2 < self.N and self.stend[k, selected_edge_id // 2 + 2, (selected_edge_id) // 2] == 1):
                r = r * state[(selected_edge_id + 3) * 2, selected_edge_id // 2 + 2] * state[(selected_edge_id + 3) * 2 + 1, selected_edge_id // 2 + 1]
            #
            # tmp1 = self.start[k, selected_edge_id + 1]
            # tmp2 = self.start[k, (selected_edge_id) / 2]
            # for i in range(N):
            #     if ((self.start[k, i] == tmp1) or (self.start[k, i] ==tmp2)):

            # 去除重用部分
            # r /= 2
            # if (N - self.num_steps == 2):
            #     r /= 2
            self.stend[k, selected_edge_id + 1, selected_edge_id // 2] = 1
            state[selected_edge_id + 2, selected_edge_id // 2 + 1] = 1
            # s1 = 0+self.start[k, selected_edge_id]
            # s2 = 0+self.start[k, (selected_edge_id + 1) % N]
            # start_new = min(self.start[k, selected_edge_id], self.start[k, (selected_edge_id + 1) % N])
            # end_new = max(self.end[k, selected_edge_id], self.end[k, (selected_edge_id + 1) % N])
            # for i in range(N):
            #     if ((self.start[k, i] == s1) or (self.start[k, i] == s2)):
            #         self.start[k, i] = start_new
            #         self.end[k, i] = end_new
            r_no_prob = r
            r = r * action_mask[k, selected_edge_id]
            reward = reward + r
            reward_no_prob += r_no_prob
            self.reward[k, self.num_steps] = r
            self.reward_no_prob[k, self.num_steps] = r_no_prob

        self.num_steps += 1
        self.done = True if self.num_steps >= self.episode_length else False
        if self.done and self.if_test:
            action_mask_ = th.mul(self.mask, action)
            # order
            print(self.num_steps, action_mask_[0].detach().cpu().numpy(), self.reward_no_prob[0].detach().cpu().numpy())
        return (self.state, self.stend, self.mask, action.detach()), reward, self.done


class Policy_Net(nn.Module):
    def __init__(self, mid_dim=1024, N=31):
        super(Policy_Net, self).__init__()
        self.N = N + 2
        self.action_dim = N - 1
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.mid_dim = mid_dim
        self.net = nn.Sequential(
            nn.Linear((N + 2) * (N + 2) + N * N + (N - 1), mid_dim * 2),
            nn.Linear(mid_dim * 2, mid_dim * 2), nn.ReLU(),
            nn.Linear(mid_dim * 2, mid_dim * 2), nn.ReLU(),
            nn.Linear(mid_dim * 2, self.action_dim),
        )
        self.output_layer = nn.Softmax().to(self.device)

    def forward(self, state):
        s, stend, mask, previous_action = state
        action = self.output_layer(self.net(th.cat((s.reshape(s.shape[0], -1), stend.reshape(s.shape[0], -1), mask), dim=-1)))
        return action


def train_curriculum_learning(policy_net, optimizer, device, N=7, num_epochs=100000000, num_env=100, gamma=0.9,
                              best_reward=None, if_wandb=False):
    env = Env(N=N, device=device, num_env=num_env, episode_length=N - 1)
    for epoch in range(num_epochs):
        test = False
        if epoch % 10 == 0:
            test = True
        state = env.reset(test)
        env.epsilon = max(0.98, 0.5 + 0.5 * (1 - epoch / 100))
        while (1):
            action = policy_net(state)
            next_state, reward, done = env.step(action)
            state = next_state
            if done and test == False:
                discounted_reward = th.zeros(num_env).to(device)
                loss_ = th.zeros(num_env).to(device)
                for i in range(N - 2, -1, -1):
                    discounted_reward = discounted_reward + env.reward_no_prob[:, i]
                    loss_ = loss_ + env.reward[:, i] / env.reward_no_prob[:, i] * discounted_reward
                    discounted_reward = discounted_reward * gamma
                loss = loss_.mean()
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                break
            if done and test == True:
                temp_reward = env.reward_no_prob.sum().item() / env.num_env
                best_reward = min(best_reward, temp_reward) if best_reward is not None else temp_reward
                print(env.reward.sum().item() / env.num_env, temp_reward, best_reward, epoch)
                # print(best_reward, epoch)
                if if_wandb:
                    wandb.log({"flops": env.reward, "flops_no_prob": env.reward_no_prob})
                break


if __name__ == "__main__":
    N = 31
    def power_of_two(n):
        count = 0
        while n > 1:
            if n % 2 == 1:
                return None
            count += 1
            n //= 2
        return count
    X = (power_of_two(N + 1))
    mid_dim = 256
    learning_rate = 5e-5
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    policy_net = Policy_Net(mid_dim=mid_dim, N=N).to(device)
    optimizer = torch.optim.Adam(policy_net.parameters(), lr=learning_rate)
    if_wandb = False
    if if_wandb:
        import wandb

        wandb.init(
            project='classical_simulation',
            entity="beamforming",
            sync_tensorboard=True,
        )
    train_curriculum_learning(policy_net, optimizer, N=N, device=device, if_wandb=if_wandb)
