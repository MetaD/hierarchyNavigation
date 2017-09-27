from neurodesign import geneticalgorithm, generate, msequence

EXP = geneticalgorithm.experiment(
    TR = 1.0,
    P = [0.5, 0.5],
    C = [[1.0, 0.0], [0.0, 1.0], [0.5, -0.5]],
    rho = 0.3,
    n_stimuli = 2,
    n_trials = 24,
    resolution = 1.0,
    stim_duration = 6.0,
    t_pre = 2.0,
    t_post = 3.0,
    maxrep = 5,
    hardprob = False,
    confoundorder = 3,
    ITImodel = 'uniform',
    ITImin = 4.0,
    ITImean = 6.0,
    ITImax = 8.0,
    restnum = 0,
    restdur = 0.0)


POP = geneticalgorithm.population( 
    experiment = EXP,
    G = 20,
    R = [0, 1, 0],
    q = 0.01,
    weights = [0.0, 0.5, 0.25, 0.25],
    I = 4,
    preruncycles = 10000,
    cycles = 10000,
    convergence = 1000,
    seed = 8467,
    folder = '~/Repos/hierarchy/navigation/neurodesign/',
    outdes = 10)


POP.naturalselection()
POP.download()
