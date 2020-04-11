#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2020 Guiral Lacotte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

TODO
- need an approximation of NPSH lower limit in AN/GV


"""

# imports
import argparse
import numpy as np
from iapws import IAPWS97
import matplotlib.pyplot as plt

# constants

# functions


def Kelvin_to_Celsius(temperature):
    '''
    Convert Kelvin to Celsius
    '''
    return(temperature - 273.15)


def Celsius_to_Kelvin(temperature):
    '''
    Convert Celsius to Kelvin
    '''
    return(temperature + 273.15)


def Psat_IAPWS97(tsat, delta_tsat=0, delta_psat=0):
    '''
    IAPWS 97 Formulas (input Kelvin, output MPa)
    Return P saturation function of T
    input
    - temperature in °c  with  273.15°K ≤ T ≤ 647.096°K
    - delta_tsat in °c
    - delta_psat in bar abs
    ouput psat as an interger
    Psat in bar abs.

        -- Warning --
        temperature above 647°K will return the critical point value
        It is incorrect and only done to prevent handling error and missing point.
    '''
    # Convert to Kelvin, filter out of bound values and apply delta tsat.
    # I do love lambda function and generator/
    tsat = [
        Celsius_to_Kelvin(item - delta_tsat)
        if 273.15 <= Celsius_to_Kelvin(item - delta_tsat)
        and Celsius_to_Kelvin(item - delta_tsat) <= 647.096
        else 647.096  # Set to critical point when out of bounds
        for item in tsat]
    p = [IAPWS97(T=temperature, x=0).P * 10 +
         delta_psat for temperature in tsat]
    return(p)


def main(args):
    '''
    Plot the socks diagram
    '''

    # Let define the temperature ranges
    Trange_full = np.arange(10, 306)  # Full temperature range 10-306°c
    Trange_RRA = np.arange(10, 160)  # RRA temperature range 10°c - 160°c
    # AN/GV temperature range 160°c - 297.2°c
    Trange_ANGV = np.arange(160, 297)
    Trange_RP = np.arange(297, 306)  # FP temperature range 297.2°c - 306.5°c

    # upper limit of AN/RRA
    Prange_RRA_max = np.repeat(31, len(Trange_RRA))

    # lower limit of AN/RRA
    Prange_RRA_min = np.concatenate([
        np.repeat(5, 70 - 10),
        np.repeat(25, 160 - 70)])

    # upper limit of AN/GV domaine
    Prange_ANGV_max = np.minimum(np.minimum(
        Psat_IAPWS97(Trange_ANGV, -110, 0),
        Psat_IAPWS97(Trange_ANGV, 0, 110)),
        np.repeat(float(155), len(Trange_ANGV)))

    # lower limit of AN/GV domaine
    Prange_ANGV_min = np.maximum(
        Psat_IAPWS97(Trange_ANGV, -30, 0),
        np.repeat(float(27), len(Trange_ANGV))
    )
    # RP this one is easy
    Prange_RP = np.repeat(155, len(Trange_RP))

    # graph parameters
    fig, main_ax = plt.subplots()
    main_ax.set_xlim(0, 350)
    main_ax.set_ylim(0, 160)
    main_ax.set_xlabel('temperature(°C)')
    main_ax.set_ylabel('Pression (bar abs.)')
    main_ax.set_title('Diagram Pression, temperature')

    # plots
    plt.plot(
        Trange_full,
        Psat_IAPWS97(Trange_full),
        linestyle='dashed',
        label='Courbe de saturation')
    plt.plot(Trange_RRA, Prange_RRA_min)
    plt.plot(Trange_RRA, Prange_RRA_max)
    plt.plot(Trange_ANGV, Prange_ANGV_max)
    plt.plot(Trange_ANGV, Prange_ANGV_min)
    plt.plot(Trange_RP, Prange_RP)

    '''
    plt.hlines(155, 0, 350, label='155 bar')
    plt.hlines(27, 0, 350, label='155 bar')
    '''
    plt.vlines(
        160,
        Prange_ANGV_min[0],
        Prange_ANGV_max[0],
        label='limit inf temp AN/GV')
    plt.vlines(297,
               Prange_ANGV_min[-1],
               Prange_ANGV_max[-1],
               label='limit sup temp AN/GV')
    # plt.vlines(306.5, 0, 155, label='limit sup temp RP')

    plt.show()

    return(None)


# main
if __name__ == '__main__':
    # command line parameters
    parser = argparse.ArgumentParser(description='Generate a socks diagram')
    parser.add_argument(
        '--output',
        dest='output',
        default='output.png',
        help='output png file (default: output.png)')
    args = parser.parse_args()
    # Main function
    main(args)
