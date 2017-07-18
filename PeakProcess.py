#!/usr/bin/python
# -*- coding: Windows-1251 -*-
from matplotlib import pyplot
import scipy.signal as signal

def level_excess_check(x, y, level, start=0, step=1, window=0, is_positive=True):
    # ������� ���������, ������� �� �������� �� ��� Y �� �������� ������ level
    # ����������� �������� �� x(start) �� x(start) +/- window
    #
    # step > 0 ����������� �������� ������ �� ���������� �������� (i = start)
    # step < 0 ����������� �������� ����� �� ���������� �������� (i = start)
    #
    # is_positive == True: ������� ���������, ����������� �� �������� 'y' ���� �������� 'level'
    # is_positive == False: ������� ���������, ���������� �� �������� 'y' ���� �������� 'level'
    # ���� ��, �� ������� True � ������ ������� �������� ������� ���������� �� 'level'
    # ���� ���, �� ������� False � ������ ���������� ������������ ��������


    idx = start                       # zero-based index
    if window == 0:                 # window default value
        window = x[-1] - x[start]

    while (idx >= 0) and (idx < len(y)) and (abs(x[idx] - x[start]) <= window):
        if not is_positive and (y[idx] < level):
            # �������� �� ����� �������� �� ������� ������ level (� ������� ����������)
            return True, idx
        elif is_positive and (y[idx] > level):
            # �������� �� ����� �������� �� ������� ������ level (� ������� ����������)
            return True, idx
        idx += step
    return False, idx


def peak_finder(x, y, level, diffwindow, tnoise=None, is_negative=True, graph=False):
    # ����� ����� (������������� ��� �������������)
    # ������:
    # Peaks = PeakFinder_v4( x, y, -1, 5E-9, 0.8, 5E-9, 1);
    # Peaks = PeakFinder_v4( x, y, -1, 5, 0.8, 5, 1);

    # x - ����� (������ ���������� ��������������� ��������)
    # y - �������� (������)

    # level - ������� ��� ���������� �������� (�� ������) ������
    # ��������� �����. ��� level > 0 ���� ����� ������������� �����,
    # ��� level < 0 ���� ����� ������������� �����.

    # tnoise - ������������ ���������� ��������� ������� (����� ����� ���������� � ��������� �����).

    # fflevel - (FrontFallLevel) �������� ����� �������� ����. ���� ������ �������� Y
    # ��������� ���� ������������ ���� �� ��������� (fflevel), �� �� ���������
    # ����� �������� ���������� ����� ���������� ���������

    # diffwindow - ���� ��������. ���� �� ������ ����� ��������� ������
    # ��������� ��������, �� �� ������ �������� �� ������ ����� �����������
    # ���� �� ��� ��������. � �������� ��������� "x".
    # �������������� diffwindow >= tnoise (�� �� �����������)

    # graph = 0 ���� ������� ����������� ������ �� ����, �������, ���� �������
    # ����������� ������ �����
    # ���������� ������ ��������� ��� ������������� (�������). ���� ���������
    # ���������� (�� ����������) ����� ��������-�������, �������� ��������.
    noise_attenuation = 0.7

    # �������� ��������� ��������

    if level == 0:
        raise ValueError('Invalid level value!')

    if is_negative:
        y = -y
        level = -level

    if not tnoise:
        # print('tnoise parameter is empty. ')
        tnoise = x(3) - x(1)
        print('Set "tnoise" to default 2 stops = ' + str(tnoise))

    # �������� ����� ��������
    if len(x) > len(y):
        print('Warning! Length(X) > Length(Y) by ' + str(len(x) - len(y)))
    elif len(x) < len(y):
        print('Warning! Length(Y) > Length(X) by ' + str(len(y) - len(x)))

    peak_x = []
    peak_y = []
    peak_idx = []
    # ==========================================================================
    # print('Starting peaks search...')

    max_y = 0
    max_idx = 0

    i = 1
    while i < len(y):
        # ������� ���������� ������
        if y[i] > level:
            # print('Overlevel occurance!')
            # ���������� ������� ������������ ��������
            max_y = y[i]
            max_idx = i

            is_noise = False
            # ���������� ��� ����� ������ diffwindow ��� �� ����� ������
            while i <= len(y) and x[i] - x[max_idx] <= diffwindow:
                if y[i] > max_y:
                    # ���������� ������� ������������ ��������
                    max_y = y[i]
                    max_idx = i
                i += 1
            # print('Found max element')
            # ���������� ����� ����� �� ���� � �������� diffwindow
            # ���� ������� ����� ������ - �� ��� "������" �� ������ �����
            # � �� ��������� ���
            [is_noise, j] = level_excess_check(x,
                                               y,
                                               max_y,
                                               start=max_idx,
                                               step=-1,
                                               window=diffwindow,
                                               is_positive=True)
            # print('Right window check completed.')
            # if is_noise:
            #     print('Left Excess at x(' + str([x(j), y(j)]) + ')')

            # �������� ���� (������� ��� ���)
            # ���������� �� max_idx ������ ��� ����� � �������� tnoise
            # ��� �� ����� ������

            if not is_noise:
                # �������� �� ������������� ����� �� level � ������ ����������
                # ������ ��������� NoiseAttenuation
                [is_noise, j] = level_excess_check(x,
                                                   y,
                                                   -level * noise_attenuation,
                                                   start=max_idx,
                                                   step=1,
                                                   window=tnoise,
                                                   is_positive=False)

                if is_noise:
                    i = j
                else:
                    # �������� �� ������� � ������ ������� �� max_idx
                    [is_noise, j] = level_excess_check(x,
                                                       y,
                                                       -level * noise_attenuation,
                                                       start=max_idx,
                                                       step=-1,
                                                       window=tnoise,
                                                       is_positive=False)
                    # if is_noise:
                    #     print('Noise at x(' + str([x(j), y(j)]) + ')')

            # ���� �� �������, �� ����������
            if not is_noise:
                peak_y.append(max_y)
                peak_x.append(x[max_idx])
                peak_idx.append(max_idx)
                # print('Found peak!')
                continue
        i += 1

    print('Number of peaks: ' + str(len(peak_y)))

    if is_negative:
        y = -y
        level = -level
        for i in range(len(peak_y)):
            peak_y[i] = -peak_y[i]
    print('Peaks searching: done.')
    print('--------------------------------------------------------')
    # ������ ����������� �������, ���� ��� ����������
    if graph:
        # plotting curve
        pyplot.plot(x, y, '-k')
        # plotting level line
        pyplot.plot([x[0], x[len(x) - 1]], [level, level], ':g')
        # marking overall peaks
        pyplot.plot(peak_x, peak_y, '*g')
        pyplot.show()
    return [peak_x, peak_y]


def smooth_voltage(x, y):
    poly_order = 3       # 3 is optimal polyorder value for speed and accuracy
    window_len = 101    # value 101 is optimal for 1 ns resolution of voltage waveform
                        # for 25 kV charging voltage of ERG installation

    # window_len correction
    time_step = x[1] - x[0]
    window_len = int(window_len / time_step)
    if window_len % 2 == 0:
        window_len += 1
    if window_len < 5:
        window_len = 5

    # smooth
    y_smoothed = signal.savgol_filter(y, window_len, poly_order)
    return y_smoothed

def find_voltage_front(x, y, level=-0.2, is_positive=False):
    # Find x (time) of voltage front on specific level
    # Default: Negative polarity, -0.2 MV level

    # PeakProcess.level_excess_check(x, y, level, start=0, step=1, window=0, is_positive=True):
    front_checked, idx = level_excess_check(x, y, level, is_positive=is_positive)
    if front_checked:
        return x[idx], y[idx]
    return None, None


def group_peaks():
    pass