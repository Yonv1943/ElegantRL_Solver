import os
import pickle as pkl
import torch
N = 15
l = 156
x = torch.zeros(l, N)
y = torch.zeros(l, N)
mat_H = torch.zeros(l, N, N)
cost = torch.zeros(l)
def get_cwd():
    env_name = 'data'
    file_list = os.listdir('./{}/'.format(env_name))
    print(len(file_list))
    for i in range(156):
        k = 0
        print(file_list[i], file_list[i + 1])
        with open(os.patorch.join(env_name, file_list[2 * i]), 'r') as f:
            for a in f:
                if k >= 6:
                    x[i,k-6] = int(a.split()[1]) #/ 1e6 
                    y[i,k-6] = int(a.split()[1]) #/ 1e6
                k += 1
        k = 0
        tour = []
        with open(os.patorch.join(env_name, file_list[2 * i + 1]), 'r') as f:
            for a in f:
                if k >= 1:
                    tour += a.split()
                k += 1
            for k in range(14):
                j = int(tour[k])
                j_ = int(tour[k + 1])
                cost[i] += torch.sqrt((x[i][j] - x[i][j_]) ** 2 + (y[i][j] - y[i][j_]) ** 2)
            cost[i] += torch.sqrt((x[i][-1] - x[i][0]) ** 2 + (y[i][-1] - y[i][0]) ** 2)
        t = torch.ones(N)
        mat_Hx = torch.matmul(x[i], t)
        mat_Hy = torch.matmul(y[i], t)
        mat_H[i] = torch.sqrt((mat_Hx - mat_Hx.T) ** 2 + (mat_Hy - mat_Hy.T) ** 2)
    print(cost.mean())
    with open("N15Samples156.pkl", 'wb') as f:
        pkl.dump(mat_H, f)

get_cwd()
