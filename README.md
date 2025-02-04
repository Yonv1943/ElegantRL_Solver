# ElegantRL_Solver: High-performance RL Solvers

We aim to find high-quality optimum, or even (nearly) global optimum, for nonconvex or nonlinear optimizations (continuous variables) and combinatorial optimizations (discrete variables).

We provide pretrained neural networks to perform real-time inference for convex optimization problems.

[Benchmark](http://plato.asu.edu/bench.html) for combinatorial optimization problems.

This project is built on [ElegantRL](https://github.com/AI4Finance-Foundation/ElegantRL) and [OpenAI Gym](https://github.com/openai/gym).

The following two key technologies are under active development: 

- **Massively parallel simuations** of gym-environments on GPU, using thousands of CUDA cores and tensor cores.

- **Podracer scheduling** on a GPU cloud, e.g., DGX-2 SuperPod.

Key references:

- Mazyavkina, Nina, et al. "Reinforcement learning for combinatorial optimization: A survey." Computers & Operations Research 134 (2021): 105400.

- Bengio, Yoshua, Andrea Lodi, and Antoine Prouvost. "Machine learning for combinatorial optimization: a methodological tour d’horizon." European Journal of Operational Research 290.2 (2021): 405-421.

- Makoviychuk, Viktor, et al. "Isaac Gym: High performance GPU based physics simulation for robot learning." Thirty-fifth Conference on Neural Information Processing Systems Datasets and Benchmarks Track (Round 2). 2021.

- Nair, Vinod, et al. "Solving mixed integer programs using neural networks." arXiv preprint arXiv:2012.13349 (2020).

## News
- We are currently developing optimization (OPT) environments that utilizes massive parallel simulation on GPU, the first version of which will be available at the end of January 2023. We welcome any suggestions or feedback!"

## Environments

ElegantRL_Solver includes the following environments with the support of massively parallel simulation on GPUs.
* MIMO Beamforming in 5G/6G.
* Classical Simulation of Quantum Circuits.
* Compressive Sensing.
* Portfolio Management.
* OR-Gym.

## Outline

- [File Structure](#File-Structure)

## File Structure

```
RLSolver
├── optimal
|   ├──branch-and-bound.py
|   └──cutting_plane.py
├── helloworld
|   ├──milp
|   ├──tsp
|   └──graph_maxcut
└── rlsolver (main folder)
    ├── envs
    |   (nonconvex optimizations)
    |   ├── learn2optimize
    |   └── mimo_beamforming 
    |   (combinatorial optimizations)
    |   ├── portfolio_management
    |   ├── quantum_circuits
    |   ├── vehicle_routing
    |   ├── virtual_machine_placement
    |   └── chip_design
    |── rlsolver_learn2optimize
    |── rlsolver_mimo_beamforming
    |── rlsolver_portfolio_management
    |── rlsolver_quantum_circuits
    └── utils


```

## Progress

- [x] mimo_beamforming
- [ ] graph_maxcut
- [ ] traveling salesman problem
- [ ] portfolio_management
