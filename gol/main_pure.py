import numpy as np
from gol.pure.automata import Automata
from gol.utils import init_gol_board_neighborhood_rule

def main_pure(
        size = 16,
        rule = None, # default to GoL
        initial_state = 'random', # 'random', 'square', 'filename.npy'
        density = 0.5, # only used on initial_state=='random'
        seed = 123,
        iterations=100,
        torus = True,
        animate = False, # if False do benchmark
        show_last_frame = False, # only applicable for benchmark
        save_last_frame = None, # only applicable for benchmark
        use_fft = False,
        use_poly_update = False,
        torch_device = None,
    ):

    # init gol board and rule
    board, neighborhood, rule = init_gol_board_neighborhood_rule(
        size = size,
        rule = rule,
        initial_state = initial_state,
        density = density,
        seed = seed
    )

    # init automata
    automata = Automata(
        board = board,
        neighborhood = neighborhood,
        rule = rule,
        torus = torus,
        use_fft = use_fft,
        use_poly_update = use_poly_update,
        torch_device = torch_device,
    )

    if animate:
        # Animate automata
        interval = 0 # as fast as possible
        automata.animate(
            iterations = iterations,
            interval = interval #ms
        )
    else:
        # Benchmark automata
        automata.benchmark(iterations)
        if show_last_frame:
            automata.show_current_frame()
        if save_last_frame:
            automata.save_last_frame(save_last_frame)

    return automata

def manual_check():

    automata = main_pure(
        size = 4,
        initial_state = 'random',
        density = 0.5,
        seed = 123,
        iterations=0,
        torus = True,
        animate = False,
        use_fft = False,
        torch_device = None, # None for numpy
    )

    automata.save_last_frame('output/manual/test_0.png')
    automata.update_board()
    automata.save_last_frame('output/manual/test_1.png')

def check_reproducible():

    def run(params):
        return main_pure(
            size = 4,
            initial_state = 'random',
            density = 0.5,
            seed = 123,
            iterations=1,
            torus = True,
            animate = False,
            **params
        )

    # gold: Numpy FFT
    gold_params = {
        'torch_device': None, # numpy
        'use_fft': True,
    }

    automata = run(gold_params)
    gold_state = automata.get_board_numpy()

    # test 1: Numpy Conv
    test_name = 'Numpy Conv'
    test_params = {
        'torch_device': None, # numpy
        'use_fft': False, # conv2d
    }

    automata = run(test_params)
    test_state = automata.get_board_numpy()

    print(f'{test_name} test succeded:', np.all(gold_state==test_state))

    # test 2: Torch Conv
    test_name = 'Torch MPS'
    test_params = {
        'torch_device': 'mps', # numpy
        'use_fft': False, # conv2d
    }

    automata = run(test_params)
    test_state = automata.get_board_numpy()

    print(f'{test_name} test succeded:', np.all(gold_state==test_state))

def reproduce_animation():
    main_pure(
        size = 16,
        initial_state = 'random',
        density = 0.5,
        seed = 123,
        iterations=100,
        torus = True,
        animate = True,
        use_fft = False, # False for conv2d
        use_poly_update = False,
        torch_device = None # use None for (numpy)
    )

def test_square(
        size = 16,
        rule = [[1,2,3],[2,3,4,5]] # GoL is [[2,3],[3]]
    ):
    automata = main_pure(
        size = size,
        rule = rule,
        initial_state = 'square2',
        iterations=100,
        torus = True,
        animate = True,
        use_fft = False, # False for conv2d
        use_poly_update = False,
        torch_device = None # use None for (numpy)
    )

    # from matplotlib import pyplot as plt
    # automata.show_current_frame('state 0', force_show=False)
    # automata.update_board()
    # automata.show_current_frame('state 1', force_show=False)
    # plt.show()

def main():
    # CONWAY GAME OF LIFE
    main_pure(
        size = 2**10, # 2**10 == 1024,
        initial_state = 'random', # 'square', 'filenmae.npy'
        density = 0.5, # only used with initial_state=='random'
        seed = 123, # only used with initial_state=='random'
        iterations = 1000,
        torus = True,
            # - fft (numpy, torch) always True TODO: fix me
            # - conv2d
            #   - numpy: works :)
            #   - torch: works :)
        animate = True, # benchmark if False
        show_last_frame = False, # only applicable for benchmark
        save_last_frame = None, # 'test.png' '100k.npy'
        use_fft = False, # conv2d (more efficient)
        # torch_device = 'cpu', # torch cpu
        # torch_device = 'cuda', # torch cuda
        torch_device = 'mps', # torch mps
        # torch_device = None, # numpy
    )

if __name__ == "__main__":

    '''
    The main code
    '''
    # main()

    '''
    Run manual check and verify manually 4x4 GoL
    '''
    # manual_check()

    '''
    Check all is working fine (all models have consistent results)
    '''
    # check_reproducible()

    '''
    Reproduce the animation which should look familiar
    '''
    reproduce_animation()

    '''
    Test square (carpet)
    '''
    # test_square()



