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

"""

# imports
import argparse
import numpy as np
from iapws import IAPWS97
import matplotlib.pyplot as plt

# constants

# functions


def kelvin_to_celsius(temperature):
    '''
    Convert Kelvin to Celsius
    '''
    return temperature - 273.15


def celsius_to_kelvin(temperature):
    '''
    Convert Celsius to Kelvin
    '''
    return temperature + 273.15


def psat_IAPWS97(tsat, delta_tsat=0, delta_psat=0):
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
        It is mostly for the Psat + 110 bar abs curve that quickly skyrocket.
    '''
    # Convert to Kelvin, filter out of bound values and apply delta tsat.
    # I do like lambda function and generator/
    tsat = [
        celsius_to_kelvin(item - delta_tsat)
        if celsius_to_kelvin(item - delta_tsat) >= 273.15
        and celsius_to_kelvin(item - delta_tsat) <= 647.096
        else 647.096  # Set to critical point when out of bounds
        for item in tsat]
    pressure = [IAPWS97(T=temperature, x=0).P * 10 +
                delta_psat for temperature in tsat]
    return pressure


def main(args):
    '''
    Plot the socks diagram
    '''

    # Let define the temperature ranges
    trange_full = np.arange(10, 306)  # Full temperature range 10-306°c
    trange_RRA = np.arange(10, 160)  # RRA temperature range 10°c - 160°c
    # AN/GV temperature range 160°c - 297.2°c
    trange_ANGV = np.arange(160, 297)
    trange_RP = np.arange(297, 306)  # RP temperature range 297.2°c - 306.5°c

    # upper limit of AN/RRA
    prange_RRA_max = np.repeat(31, len(trange_RRA))

    # lower limit of AN/RRA
    prange_RRA_min = np.concatenate([
        np.repeat(5, 70 - 10),
        np.repeat(25, 160 - 70)])

    # upper limit of AN/GV domaine
    prange_ANGV_max = np.minimum(
        np.minimum(
            psat_IAPWS97(trange_ANGV, -110, 0),
            psat_IAPWS97(trange_ANGV, 0, 110)),
        np.repeat(float(155), len(trange_ANGV)))

    # lower limit of AN/GV domaine
    prange_ANGV_min = np.maximum(
        np.maximum(
            psat_IAPWS97(trange_ANGV, -30, 0),
            psat_IAPWS97(trange_ANGV, 0, 17)),
        np.repeat(float(27), len(trange_ANGV)))

    # RP this is the easy one
    prange_RP = np.repeat(155, len(trange_RP))

    # mathplot figure parameters
    fig, main_ax = plt.subplots()
    main_ax.set_xlim(0, 350)
    main_ax.set_ylim(0, 160)
    main_ax.set_xlabel('temperature(°C)')
    main_ax.set_ylabel('Pression (bar abs.)')
    main_ax.set_title('Diagram Pression, temperature')

    # plots cruves
    plt.plot(
        trange_full,
        psat_IAPWS97(trange_full),
        linestyle='dashed',
        label='Courbe de saturation')
    plt.plot(
        trange_ANGV,
        psat_IAPWS97(trange_ANGV, 0, 17),
        linestyle='dashed',
        label='NPSH approximation')
    plt.plot(trange_RRA, prange_RRA_min)
    plt.plot(trange_RRA, prange_RRA_max)
    plt.plot(trange_ANGV, prange_ANGV_max)
    plt.plot(trange_ANGV, prange_ANGV_min)
    plt.plot(trange_RP, prange_RP)

    # Plots rectangles
    plt.gca().add_patch(plt.Rectangle(
        [10, 0], 50, 5, fill=False, linewidth=1.5))  #  API domaine
    # AN/GV at RRA connection conditions
    plt.gca().add_patch(plt.Rectangle([160, 27], 20, 4, fill=False, linewidth=1.5))

    # vertical lines eye candy
    plt.hlines(155, 0, 350, label='155 bar', linewidth=0.5, linestyle='dashed')
    plt.vlines(297, 0, 200, label='', linewidth=0.5, linestyle='dashed')
    plt.vlines(
        10,
        prange_RRA_min[0],
        prange_RRA_max[0],
        label='limit inf temp AN/RRA')
    plt.vlines(
        160,
        prange_RRA_min[-1],
        prange_ANGV_max[0],
        label='limit inf temp AN/GV')
    plt.vlines(
        297,
        prange_ANGV_min[-1],
        prange_ANGV_max[-1],
        label='limit sup temp AN/GV')
    # Text
    plt.text(30, 20, 'AN/GV')
    plt.text(200, 80, 'AN/RRA')
    # Render the graph
    plt.show()

    return None


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
