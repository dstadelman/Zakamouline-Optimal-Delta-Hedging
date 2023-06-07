import matplotlib.pyplot as plt

import bsm
import zakamouline


def plot_zakamouline_bands(bsm_deltas, up_bands, down_bands, savefig = None):

    # figure
    fig, ax = plt.subplots(figsize=(16, 9))

    # set the plots
    ax.plot(bsm_deltas, bsm_deltas,  label="BSM Delta",  linewidth=1, color='black')
    ax.plot(bsm_deltas, up_bands,    label="Up Band",    linewidth=2, color='red')
    ax.plot(bsm_deltas, down_bands,  label="Down Band",  linewidth=2, color='blue')

    # turn on the grid
    ax.grid(True, axis='x', which='major', alpha=0.5)
    ax.grid(True, axis='y', which='major', alpha=0.5)

    ax.set_ylabel('Band Delta')
    ax.set_xlabel('Position Delta')

    # set the legend
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)    

    if savefig is not None:
        plt.savefig(savefig)
        plt.cla()
    else:
        plt.show()


def test_zakamouline():

    '''@Init Call & Put
    Spot = 100
    Strike = 100
    DTE = 60
    RFR = 5%
    Volatility = 30%'''
    call = bsm.BsmOption(False, 'C', 100, 100, 60, 0.05, sigma=0.3)
    put = bsm.BsmOption(False, 'P', 100, 100, 60, 0.05, sigma=0.3)

    #Init short straddle position
    short_straddle = bsm.OptionPosition([call, put])

    #Get hedgebands at current spot price
    '''Position = short_straddle
    Proportional transaction cost lambda where (tc = lambda * num_shares * spot) = 2%
    Risk aversion parameter (higher results in tighter bands) = 1'''
    up_band, down_band = zakamouline.hedgebands(short_straddle, 0.02, 1)

    assert abs(up_band      - 0.0129)       < .01
    assert abs(down_band    - (-0.2233))    < .01


def test_zakamouline_plot():

    bsm_deltas  = []
    up_bands    = []
    down_bands  = []

    for i in range(0, 200):

        try: 
            call = bsm.BsmOption(False, 'C', i, 100, 60, 0.05, sigma=0.3)
            put = bsm.BsmOption(False, 'P', i, 100, 60, 0.05, sigma=0.3)
            short_straddle = bsm.OptionPosition([call, put])

            up_band, down_band = zakamouline.hedgebands(short_straddle, 0.02, 1)
        
        except ZeroDivisionError as e:
            continue

        bsm_delta = short_straddle.delta()

        if bsm_delta > .9999 or bsm_delta < -.9999:
            continue

        bsm_deltas.append(bsm_delta)
        up_bands.append(up_band)
        down_bands.append(down_band)

    plot_zakamouline_bands(bsm_deltas, up_bands, down_bands, "test_zakamouline_plot.png")

