import matplotlib.pyplot as plt
import numpy as np

from py_vollib.black_scholes import black_scholes as py_vollib_black_scholes
from py_vollib.black_scholes.implied_volatility import implied_volatility as py_vollib_implied_volatility
from py_vollib.black_scholes.greeks.analytical import delta as py_vollib_delta
from py_vollib.black_scholes.greeks.analytical import gamma as py_vollib_gamma
from py_vollib.black_scholes.greeks.analytical import theta as py_vollib_theta
from py_vollib.black_scholes.greeks.analytical import vega as py_vollib_vega
from py_vollib.black_scholes.greeks.analytical import rho as py_vollib_rho

import bsm
import zakamouline


def plot_zakamouline_bands(bsm_deltas, up_bands, down_bands, l, h, savefig = None):

    # figure
    fig, ax = plt.subplots(figsize=(16, 9))

    # set the plots
    ax.plot(bsm_deltas, bsm_deltas,  label="BSM Delta",  linewidth=1, color='black')
    ax.plot(bsm_deltas, up_bands,    label="Up Band",    linewidth=2, color='red')
    ax.plot(bsm_deltas, down_bands,  label="Down Band",  linewidth=2, color='blue')

    plt.yticks(np.arange(l, h+.1, .1))
    plt.xticks(np.arange(l, h+.1, .1))

    # turn on the grid
    ax.grid(True, axis='x', which='major', alpha=0.5)
    ax.grid(True, axis='y', which='major', alpha=0.5)

    ax.set_ylabel('Band Delta')
    ax.set_xlabel('Option Position Delta')

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

    # assert abs(up_band      - 0.0129)       < .01
    # assert abs(down_band    - (-0.2233))    < .01


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

        if bsm_delta > .99 or bsm_delta < -.99:
            continue

        bsm_deltas.append(bsm_delta)
        up_bands.append(up_band)
        down_bands.append(down_band)

    plot_zakamouline_bands(bsm_deltas, up_bands, down_bands, -1, 1, "README_test_zakamouline_plot.png")


def test_sinclair_long_call():

    bsm_deltas  = []
    up_bands    = []
    down_bands  = []

    for i in range(0, 200):

        try: 
            call = bsm.BsmOption(True, 'C', i, 100, 365, 0, sigma=0.3)
            long_call = bsm.OptionPosition([call])

            up_band, down_band = zakamouline.hedgebands(long_call, 0.02, 1)
        
        except ZeroDivisionError as e:
            continue

        bsm_delta = long_call.delta()

        if bsm_delta > .99 or bsm_delta < .01:
            continue

        bsm_deltas.append(bsm_delta)
        up_bands.append(up_band)
        down_bands.append(down_band)

    plot_zakamouline_bands(bsm_deltas, up_bands, down_bands, 0, 1, "README_test_sinclair_long_call.png")


def test_sinclair_short_call():

    bsm_deltas  = []
    up_bands    = []
    down_bands  = []

    for i in range(0, 200):

        try: 
            call = bsm.BsmOption(False, 'C', i, 100, 365, 0, sigma=0.3)
            short_call = bsm.OptionPosition([call])

            up_band, down_band = zakamouline.hedgebands(short_call, 0.02, 1)
        
        except ZeroDivisionError as e:
            continue

        bsm_delta = short_call.delta()

        if bsm_delta > -.01 or bsm_delta < -.99:
            continue

        bsm_deltas.append(bsm_delta)
        up_bands.append(down_band)
        down_bands.append(up_band)

    plot_zakamouline_bands(bsm_deltas, up_bands, down_bands, -1, 0, "README_test_sinclair_short_call.png")


def calc_greeks_black_scholes(put_or_call_flag, underlying_price, strike, years_to_expiry, volatility, risk_free_rate:float = 0):

    # t = ((expiration_time - quote_time).total_seconds() / 86400) / 365
    # assert t > 0

    return (
        py_vollib_delta(
            put_or_call_flag.lower()
        ,   underlying_price
        ,   strike
        ,   years_to_expiry
        ,   risk_free_rate
        ,   volatility
        )
    ,   py_vollib_gamma(
            put_or_call_flag.lower()
        ,   underlying_price
        ,   strike
        ,   years_to_expiry
        ,   risk_free_rate
        ,   volatility
        )
    ,   py_vollib_theta(
            put_or_call_flag.lower()
        ,   underlying_price
        ,   strike
        ,   years_to_expiry
        ,   risk_free_rate
        ,   volatility
        )
    ,   py_vollib_vega(
            put_or_call_flag.lower()
        ,   underlying_price
        ,   strike
        ,   years_to_expiry
        ,   risk_free_rate
        ,   volatility
        )
    ,   py_vollib_rho(
            put_or_call_flag.lower()
        ,   underlying_price
        ,   strike
        ,   years_to_expiry
        ,   risk_free_rate
        ,   volatility
        )
    )


def calc_price_black_scholes(put_or_call_flag, underlying_price, strike, years_to_expiry, volatility, risk_free_rate:float = 0):

    # years_to_expiry = ((expiration_time - quote_time).total_seconds() / 86400) / 365
    # assert years_to_expiry > 0

    return py_vollib_black_scholes(
        put_or_call_flag.lower()
    ,   underlying_price
    ,   strike
    ,   years_to_expiry
    ,   risk_free_rate
    ,   volatility
    )


def test_py_vollib_long_call():

    lambda_         = .02
    gamma_lower     = 1

    isLong = True

    bsm_deltas  = []
    up_bands    = []
    down_bands  = []

    for i in range(0, 200):

        try: 
            # call = bsm.BsmOption(True, 'C', i, 100, 365, 0, sigma=0.3)
            # long_call = bsm.OptionPosition([call])

            put_or_call_flag = 'C'
            underlying_price = i
            strike = 100
            years_to_expiry = 1
            volatility = 0.3
            risk_free_rate = 0

            delta, gamma = (
                py_vollib_delta(
                    put_or_call_flag.lower()
                ,   underlying_price
                ,   strike
                ,   years_to_expiry
                ,   risk_free_rate
                ,   volatility
                )
            ,   py_vollib_gamma(
                    put_or_call_flag.lower()
                ,   underlying_price
                ,   strike
                ,   years_to_expiry
                ,   risk_free_rate
                ,   volatility
                )
            )

            k   = zakamouline.getK(lambda_, years_to_expiry, risk_free_rate, volatility, gamma_lower, underlying_price, gamma)
            h0  = zakamouline.getH0(lambda_, gamma_lower, underlying_price, volatility, years_to_expiry)
            h1  = zakamouline.getH1(lambda_, years_to_expiry, risk_free_rate, volatility, gamma, gamma_lower)

            sigma_m = zakamouline.getSigmaModified(volatility, k, isLong) #Applies to NOTE 2
            delta_m = py_vollib_delta(
                put_or_call_flag.lower()
            ,   underlying_price
            ,   strike
            ,   years_to_expiry
            ,   risk_free_rate
            ,   sigma_m
            )

            up_band     = delta_m + (h1 + h0)
            down_band   = delta_m - (h1 + h0)
        
        except ZeroDivisionError as e:
            continue

        bsm_delta = delta

        if bsm_delta > .99 or bsm_delta < .01:
            continue

        bsm_deltas.append(bsm_delta)
        up_bands.append(up_band)
        down_bands.append(down_band)

    plot_zakamouline_bands(bsm_deltas, up_bands, down_bands, 0, 1, "README_test_py_vollib_long_call.png")


def test_py_vollib_short_call():

    lambda_         = .02
    gamma_lower     = 1

    isLong = False

    bsm_deltas  = []
    up_bands    = []
    down_bands  = []

    for i in range(0, 200):

        try: 
            # call = bsm.BsmOption(True, 'C', i, 100, 365, 0, sigma=0.3)
            # long_call = bsm.OptionPosition([call])

            put_or_call_flag = 'C'
            underlying_price = i
            strike = 100
            years_to_expiry = 1
            volatility = 0.3
            risk_free_rate = 0

            delta, gamma = (
                py_vollib_delta(
                    put_or_call_flag.lower()
                ,   underlying_price
                ,   strike
                ,   years_to_expiry
                ,   risk_free_rate
                ,   volatility
                )
            ,   py_vollib_gamma(
                    put_or_call_flag.lower()
                ,   underlying_price
                ,   strike
                ,   years_to_expiry
                ,   risk_free_rate
                ,   volatility
                )
            )

            k   = zakamouline.getK(lambda_, years_to_expiry, risk_free_rate, volatility, gamma_lower, underlying_price, gamma)
            h0  = zakamouline.getH0(lambda_, gamma_lower, underlying_price, volatility, years_to_expiry)
            h1  = zakamouline.getH1(lambda_, years_to_expiry, risk_free_rate, volatility, gamma, gamma_lower)

            sigma_m = zakamouline.getSigmaModified(volatility, k, isLong) #Applies to NOTE 2
            delta_m = py_vollib_delta(
                put_or_call_flag.lower()
            ,   underlying_price
            ,   strike
            ,   years_to_expiry
            ,   risk_free_rate
            ,   sigma_m
            )

            up_band     = delta_m + (h1 + h0)
            down_band   = delta_m - (h1 + h0)
        
        except ZeroDivisionError as e:
            continue

        bsm_delta = delta

        if bsm_delta > .99 or bsm_delta < .01:
            continue

        bsm_deltas.append(bsm_delta)
        up_bands.append(up_band)
        down_bands.append(down_band)

    plot_zakamouline_bands(bsm_deltas, up_bands, down_bands, 0, 1, "README_test_py_vollib_short_call.png")

