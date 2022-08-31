import torch as th
import numpy as np
class MIMO_Relay():
    def __init__(self, K=2, N=2, M=2, P=10, noise_power=1, episode_length=6, num_env=4, device=th.device("cuda:0")):
        self.N = N # #antennas base stations
        self.M = M # #antennas relay
        self.K = K # #users
        self.P = P # power
        self.noise_power = noise_power
        self.basis_vectors_G, _ = th.linalg.qr(th.rand(2 * self.M * self.N, 2 * self.M * self.N, dtype=th.float))
        self.basis_vectors_H, _ = th.linalg.qr(th.rand(2 * self.N * self.K, 2 * self.N * self.K, dtype=th.float))
        self.subspace_dim = 1
        self.num_env = num_env
        self.device = device
        self.episode_length = episode_length
        self.mat_F0 = th.diag_embed(th.ones(self.num_env, self.M, dtype=th.cfloat))
        
    def reset(self,):
        if self.subspace_dim_H <= 2 * self.N * self.K:
            self.vec_H = self.generate_channel_batch(self.N, self.K, self.num_env, self.subspace_dim, self.basis_vectors_H).to(self.device)
        else:
            self.vec_H = th.randn(self.num_env, 2 * self.N * self.K, dtype=th.cfloat).to(self.device)
        if self.subspace_dim_G <= 2 * self.M * self.N:
            self.vec_G = self.generate_channel_batch(self.M, self.N, self.num_env, self.subspace_dim, self.basis_vectors_G).to(self.device)
        else:
            self.vec_G = th.randn(self.num_env, 2 * self.M * self.N, dtype=th.cfloat).to(self.device)
        self.mat_H = (self.vec_H[:, :self.N * self.K] + self.vec_H[:, self.N * self.K:] * 1.j).reshape(-1, self.N, self.K)
        self.mat_G = (self.vec_G[:, :self.M * self.N] + self.vec_G[:, self.M * self.N:] * 1.j).reshape(-1, self.M, self.N)
        self.mat_F = self.mat_F0
        print(self.mat_H.shape, self.mat_F.shape, self.mat_G.shape)
        self.mat_HFG = th.bmm(th.bmm(self.mat_H, self.mat_F), self.mat_G)
        self.mat_W = self.calc_mmse(self.mat_HFG, self.mat_F).to(self.device)
        self.num_steps = 0
        return (self.mat_HFG, self.mat_F)

    def step(self, action):
        self.mat_F = action.detach()
        self.mat_HFH = th.bmm(th.bmm(self.mat_H, self.mat_F), self.mat_G)
        self.mat_W = self.calc_mmse(self.mat_HFG, self.mat_F).to(self.device)
        self.reward = self.calc_sum_rate(self.mat_H, action, self.mat_G, self.mat_W)
        self.num_steps += 1
        self.done = True if self.num_steps >= self.episode_length else False
        return self.get_state(), self.reward, self.done
    
    def get_state(self,):
        return (self.mat_H, self.mat_F)

    def generate_channel_batch(self, N, K, batch_size, subspace_dim, basis_vectors):
        coordinates = th.randn(batch_size, subspace_dim, 1)
        basis_vectors_batch = basis_vectors[:subspace_dim].T.repeat(batch_size, 1).reshape(-1, 2 * K * N, subspace_dim)
        vec_channel = th.bmm(basis_vectors_batch, coordinates).reshape(-1 ,2 * K * N) * (( 2 * K * N / subspace_dim) ** 0.5)
        return  (N * K) ** 0.5 * (vec_channel / vec_channel.norm(dim=1, keepdim = True))
    
    def calc_mmse(self, channel, mat_F):
        channel = channel.to(self.device)
        lambda_ = th.ones(self.K).repeat((channel.shape[0], 1)) * self.P / self.K
        p = th.ones(self.K).repeat((channel.shape[0], 1)).to(self.device) * np.sqrt(self.P / self.K)
        effective_channel = channel.conj().transpose(1,2).to(th.cfloat).to(self.device)
        eye_N = (th.zeros(lambda_.shape[0], self.N) + 1).to(self.device)
        eye_N = eye_N + mat_F.flatten(start_dim=1).norm(dim=1, keepdim=True)
        eye_N = th.diag_embed(eye_N)
        lambda_ = th.diag_embed(lambda_)
        channel = th.bmm(lambda_.to(th.cfloat), channel.type(th.cfloat))
        denominator = th.inverse(eye_N + th.bmm(effective_channel,channel))
        wslnr_max = th.zeros((lambda_.shape[0], self.N, self.K), dtype=th.cfloat).to(self.device)
        wslnr_max = th.bmm(denominator, effective_channel)
        wslnr_max = wslnr_max.transpose(1,2)
        wslnr_max = wslnr_max / wslnr_max.norm(dim=2, keepdim=True)
        p = th.diag_embed(p)
        W = th.bmm(p.to(th.cfloat), wslnr_max)
        return W

    def calc_sum_rate(self, H, F, G, W):
        HF = th.bmm(H, F)
        HFGW = th.bmm(th.bmm(HF.to(th.cfloat), G), W.to(th.cfloat).transpose(-1, -2))
        S = th.abs(th.diagonal(HFGW, dim1=-2, dim2=-1))**2
        I = th.sum(th.abs(HFGW)**2, dim=-1) - th.abs(th.diagonal(HFGW, dim1=-2, dim2=-1))**2
        N = th.norm(HF, dim=-1)**2 * 1 + self.noise_power
        SINR = S/(I+N)
        return th.log2(1+SINR).sum(dim=-1).unsqueeze(-1)
