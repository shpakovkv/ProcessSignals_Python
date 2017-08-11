#!/usr/bin/python
# -*- coding: Windows-1251 -*-
from __future__ import print_function

from matplotlib import pyplot
import os
import bisect
import scipy.integrate as integrate


pos_polarity_labels = {'pos', 'positive', '+'}
neg_polarity_labels = {'neg', 'negative', '-'}


# def add_to_log(m, end='\n'):
#     if __name__ != "__main__":
#         from only_for_tests import log
#     else:
#         global log
#     log += m + end
#     print(m, end=end)


class SinglePeak:
    def __init__(self, time=None, value=None, index=None, sqr_l=0, sqr_r=0):
        self.time = time
        self.val = value
        self.idx = index
        self.sqr_l = sqr_l
        self.sqr_r = sqr_r

    def invert(self):
        if self.val is not None:
            self.val = -self.val

    def get_time_val(self):
        return [self.time, self.val]

    def set_time_val_idx(self, data):
        if len(data) != 3:
            raise ValueError("Wrong number of values to unpack. "
                             "3 expected, " + str(len(data)) +
                             " given.")
        self.time = data[0]
        self.val = data[1]
        self.idx = data[2]

    def set_data_full(self, data):
        if len(data) != 5:
            raise ValueError("Wrong number of values to unpack. "
                             "3 expected, " + str(len(data)) +
                             " given.")
        self.time = data[0]
        self.val = data[1]
        self.idx = data[2]
        self.sqr_l = data[3]
        self.sqr_r = data[4]

    def get_time_val_idx(self):
        return [self.time, self.val, self.idx]

    def get_data_full(self):
        return [self.time, self.val, self.idx, self.sqr_l, self.sqr_r]

    xy = property(get_time_val, doc="Get [time, value] of peak.")
    data = property(get_time_val_idx, set_time_val_idx,
                    doc="Get/set [time, value, index] of peak.")
    data_full = property(get_data_full, set_data_full,
                         doc="Get/set [time, value, index, "
                             "sqr_l, sqr_r] of peak.")


def find_nearest_idx(sorted_arr, value, side='auto'):
    """
    Returns the index of the value closest to 'value'
    
    sorted_arr -- sorted array/list of ints or floats
    value -- the number to which the closest value should be found
    side -- 'left': search among values that are lower then X
            'right': search among values that are greater then X
            'auto': handle all values (default)

    If two numbers are equally close and side='auto', 
    returns the index of the smallest one.
    """

    idx = bisect.bisect_left(sorted_arr, value)
    if idx == 0:
        if side == 'auto' or side == 'right':
            return idx
        else:
            return None

    if idx == len(sorted_arr):
        if side == 'auto' or side == 'left':
            return idx
        else:
            return None

    after = sorted_arr[idx]
    before = sorted_arr[idx - 1]
    if side == 'auto':
        if after - value < value - before:
            return idx
        else:
            return idx - 1
    elif side == 'left':
        return idx - 1
    elif side == 'right':
        return idx



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

    idx = start          # zero-based index
    if window == 0:      # window default value
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

def is_pos(polarity):
    global pos_polarity_labels
    global neg_polarity_labels
    if polarity.lower() in pos_polarity_labels:
        return True
    if polarity.lower() in neg_polarity_labels:
        return False
    else:
        raise ValueError("Wrong polarity value ({})".format(polarity))


def is_neg(polarity):
    global pos_polarity_labels
    global neg_polarity_labels
    if polarity.lower() in pos_polarity_labels:
        return False
    if polarity.lower() in neg_polarity_labels:
        return True
    else:
        raise ValueError("Wrong polarity value ({})".format(polarity))


def check_polarity(curve, time_bounds=(None, None)):
    if time_bounds[0] is None:
        time_bounds = (0, time_bounds[1])
    if time_bounds[1] is None:
        time_bounds = (time_bounds[0], curve.points)
    integr =  integrate.trapz(curve.val[time_bounds[0]:time_bounds[1]],
                       curve.time[time_bounds[0]:time_bounds[1]])
    # print("Voltage_INTEGRAL = {}".format(integr))
    if integr >= 0:
        return 'positive'
    return 'negative'


def find_voltage_front(curve,
                       level=-0.2,
                       polarity='auto',
                       save_plot=False,
                       plot_name="voltage_front.png"):
    # Find x (time) of voltage front on specific level
    # Default: Negative polarity, -0.2 MV level
    # PeakProcess.level_excess_check(x, y, level, start=0, step=1, window=0, is_positive=True):
    if polarity=='auto':
        polarity = check_polarity(curve)
        if is_pos(polarity):
            level = abs(level)
        else:
            level = -abs(level)

    front_checked, idx = level_excess_check(curve.time, curve.val, level,
                                            is_positive=is_pos(polarity))
    if front_checked:
        if save_plot:
            pyplot.close('all')
            pyplot.plot(curve.time, curve.val, '-b')
            pyplot.plot([curve.time[idx]], [curve.val[idx]], '*r')
            # pyplot.show()
            folder = os.path.dirname(plot_name)
            if folder != "" and not os.path.isdir(folder):
                os.makedirs(folder)
            pyplot.savefig(plot_name)
            pyplot.close('all')
        return curve.time[idx], curve.val[idx]
    return None, None


def peak_finder(x, y, level, diff_time, time_bounds=(None, None),
                tnoise=None, is_negative=True, graph=False,
                noise_attenuation=0.5):
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

    # diff_time - ���� ��������. ���� �� ������ ����� ��������� ������
    # ��������� ��������, �� �� ������ �������� �� ������ ����� �����������
    # ���� �� ��� ��������. � �������� ��������� "x".
    # �������������� diff_time >= tnoise (�� �� �����������)

    # graph = 0 ���� ������� ����������� ������ �� ����, �������, ���� �������
    # ����������� ������ �����

    # noise_attenuation (default 0.5)
    # ���������� ������ ��������� ��� ������������� (�������). ���� ���������
    # ���������� (�� ����������) ����� ��������-�������, �������� ��������.


    # �������� ��������� ��������
    peak_log = ""
    if level == 0:
        raise ValueError('Invalid level value!')

    if is_negative:
        y = -y
        level = -level

    if not tnoise:
        # print('tnoise parameter is empty. ')
        tnoise = x(3) - x(1)
        peak_log += 'Set "tnoise" to default 2 stops = ' + str(tnoise) + "\n"

    if len(time_bounds) != 2:
        raise ValueError("time_bounds has incorrect number of values. "
                         "2 expected, " + str(len(time_bounds)) +
                         " given.")
    # �������� ����� ��������
    if len(x) > len(y):
        raise IndexError('Length(X) > Length(Y) by ' + str(len(x) - len(y)))
    elif len(x) < len(y):
        raise IndexError('Warning! Length(X) < Length(Y) by ' + str(len(y) - len(x)))

    if time_bounds[0] is None:
        time_bounds = (x[0], time_bounds[1])
    if time_bounds[1] is None:
        time_bounds = (time_bounds[0], x[-1])
    start_idx = find_nearest_idx(x, time_bounds[0], side='right')
    stop_idx = find_nearest_idx(x, time_bounds[1], side='left')
    if start_idx is None or stop_idx is None:
        peak_log += "Time bounds is out of range.\n"
        return [], peak_log

    peak_list = []
    # ==========================================================================
    # print('Starting peaks search...')

    i = start_idx
    while i < stop_idx :
        # ������� ���������� ������
        if y[i] > level:
            # print('Overlevel occurance!')
            # ���������� ������� ������������ ��������
            max_y = y[i]
            max_idx = i

            # ���������� ��� ����� ������ diff_time ��� �� ����� ������
            while (i <= stop_idx and
                   (x[i] - x[max_idx] <= diff_time or
                    y[i] == max_y)):
                if y[i] > max_y:
                    # ���������� ������� ������������ ��������
                    max_y = y[i]
                    max_idx = i
                i += 1
            # print("local_max = [{}, {}]".format(x[max_idx], max_y))

            # print('Found max element')
            # ���������� ����� ����� �� ���� � �������� diff_time
            # ���� ������� ����� ������ - �� ��� "������" �� ������ �����
            # � �� ��������� ���
            [is_noise, _] = level_excess_check(x,
                                               y,
                                               max_y,
                                               start=max_idx,
                                               step=-1,
                                               window=diff_time,
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
                                                   -max_y * noise_attenuation,
                                                   start=max_idx,
                                                   step=1,
                                                   window=tnoise,
                                                   is_positive=False)

                if is_noise:
                    i = j
                else:
                    # �������� �� ������� � ������ ������� �� max_idx
                    [is_noise, _] = level_excess_check(x,
                                                       y,
                                                       -max_y * noise_attenuation,
                                                       start=max_idx,
                                                       step=-1,
                                                       window=tnoise,
                                                       is_positive=False)
                    # if is_noise:
                    #     print('Noise at x(' + str([x(j), y(j)]) + ')')

            # ���� �� �������, �� ����������
            if not is_noise:
                peak_list.append(SinglePeak(x[max_idx], max_y, max_idx))
                # print('Found peak!')
                continue
        i += 1

    peak_log += 'Number of peaks: ' + str(len(peak_list)) + "\n"
    # for pk in peak_list:
    #     print("[{:.3f}, {:.3f}]    ".format(pk.time, pk.val), end="")
    # print()

    # LOCAL INTEGRAL CHECK
    dt = x[1] - x[0]
    di = int(diff_time * 2 // dt)    # diff window in index units

    if di > 3:
        for idx in range(len(peak_list)):
            pk = peak_list[idx]
            # square = pk.val * dt * di
            square = pk.val * di
            integral_left = 0
            integral_right = 0
            peak_log += ("Peak[{:3d}] = [{:7.2f},   {:4.1f}]   "
                         "Square factor [".format(idx, pk.time, pk.val))
            if pk.idx - di >= 0:
                integral_left = integrate.trapz(y[pk.idx-di : pk.idx+1])
                peak_list[idx].sqr_l = integral_left / square
                peak_log += "{:.3f}".format(integral_left / square)
            peak_log += " | "
            if pk.idx + di < len(y):  # stop_idx
                integral_right = integrate.trapz(y[pk.idx: pk.idx + di + 1])
                peak_list[idx].sqr_r = integral_right / square
                peak_log += "{:.3f}".format(integral_right / square)
            peak_log += "]"
            peak_log += "  ({:.3f})".format((integral_right + integral_left) / square)
            peak_log += "\n"
        if peak_list:
            peak_log += "\n"


    if is_negative:
        y = -y
        level = -level
        for i in range(len(peak_list)):
            peak_list[i].invert()
    # ������ ����������� �������, ���� ��� ����������
    if graph:
        # plotting curve
        pyplot.plot(x[start_idx:stop_idx], y[start_idx:stop_idx], '-b')
        pyplot.xlim(time_bounds)
        # plotting level line
        pyplot.plot([x[0], x[len(x) - 1]], [level, level], ':g')
        # marking overall peaks
        peaks_x = [p.time for p in peak_list]
        peaks_y = [p.val for p in peak_list]
        pyplot.plot(peaks_x, peaks_y, 'og')
        pyplot.plot(peaks_x, peaks_y, '*r')
        pyplot.show()

    return peak_list, peak_log


def group_peaks(data, window):
    # Groups the peaks from different X-Ray detectors
    # each group corresponds to one single act of X-Ray emission
    #
    # data - list with N elements, each element represents one curve
    # curve - list witn M elements, each element represents one peak
    # peak - list with 2 float numbers: [time, value]
    #
    # data[curve_idx][peak_idx][0] = X-value of peak with peak_idx index of curve with curve_idx index
    # data[curve_idx][peak_idx][1] = Y-value of peak with peak_idx index of curve with curve_idx index
    # where curve_idx and peak_idx - zero-based index of curve and peak
    #
    # window - peaks coincide when their X values are within...
    # ... +/-window interval from average X (time) position of peak ()
    # "Average" because X (time) value of a peak may differ from curve to curve

    start_wf = 0
    for wf in range(len(data)):
        if data[wf]:
            start_wf = wf
            break

    peak_time = []                  # 1D array with average X (time) data of peak group
    for peak in data[start_wf]:
        peak_time.append(peak.time)

    dt = abs(window)                            # changes variable name for shortness
    curves_count = len(data)                    # number of waveforms
    num_peak_in_gr = [1] * len(peak_time)       # 1D array with numbers of peaks in each group

    peak_map = [[True] * len(peak_time)]            # (peak_map[curve_idx][group_idx] == True) means "there IS a peak"
    for curve in range(1, curves_count):          # False value means...
        peak_map.append([False] * len(peak_time))   # ..."this curve have not peak at this time position"

    peak_data = [[]]
    for peak in data[start_wf]:    # peaks of first curve
        peak_data[0].append(SinglePeak(*peak.data_full))

    for curve_idx in range(0, start_wf):
        peak_data.insert(0, [None] * len(peak_time))
    for curve_idx in range(start_wf + 1, curves_count):
        peak_data.append([None] * len(peak_time))

    if curves_count <= 1:                           # if less than 2 elements = no comparison
        return peak_data, peak_map

    # ---------- making groups of peaks ------------------------------
    # makes groups of peaks
    # two peaks make group when they are close enought ('X' of a peak is within +/- dt interval from 'X' of the group)
    # with adding new peak to a group, the 'X' parameter of the group changes to (X1 + X2 + ... + Xn)/n
    # where n - number of peaks in group
    #
    # for all waveforms exept first
    for wf in range(start_wf + 1, curves_count):
                # wf == 'waveform index'
        gr = 0  # gr == 'group index', zero-based index of current group
        pk = 0  # pk == 'peak index', zero-based index of current peak (in peak list of current waveform)

        while pk < len(data[wf]) and len(data[wf]) > 0:                         # for all peaks in input curve's peaks data
            # ===============================================================================================
            # ADD PEAK TO GROUP
            # check if curve[i]'s peak[j] is in +/-dt interval from peaks of group[gr]
            # print "Checking Group[" + str(gr) + "]"
            next_is_closer = False
            if abs(peak_time[gr] - data[wf][pk].time) <= dt:
                if (len(data[wf]) > pk + 1 and
                        (abs(peak_time[gr] - data[wf][pk].time) >
                         abs(peak_time[gr] - data[wf][pk + 1].time))):
                    peak_time.insert(gr, data[wf][pk].time)  # insert new group of peaks into the groups table
                    num_peak_in_gr.insert(gr, 1)  # update the number of peaks in current group
                    peak_map[wf].insert(gr, True)  # insert row to current wf column of peak map table
                    peak_data[wf].insert(gr, SinglePeak(
                        *data[wf][pk].data_full))  # insert row to current wf column of peak data table
                    for curve_i in range(curves_count):
                        if curve_i != wf:
                            peak_map[curve_i].insert(gr, False)  # new row to other columns of peak map table
                            peak_data[curve_i].insert(gr, None)  # new row to other columns of peak data table
                    pk += 1
                else:
                    # print "Waveform[" + str(wf) + "] Peak[" + str(pk) + "]   action:    " + "group match"
                    peak_time[gr] = ((peak_time[gr] * num_peak_in_gr[gr] + data[wf][pk].time) /
                                     (num_peak_in_gr[gr] + 1))        # recalculate average X-position of group
                    num_peak_in_gr[gr] = num_peak_in_gr[gr] + 1         # update count of peaks in current group
                    peak_map[wf][gr] = True                         # update peak_map
                    peak_data[wf][gr] = SinglePeak(*data[wf][pk].data_full)          # add peak to output peak data array
                    pk += 1                                         # go to the next peak

            # ===============================================================================================
            # INSERT NEW GROUP
            # check if X-position of current peak of curve[wf] is to the left of current group by more than dt
            elif data[wf][pk].time < peak_time[gr] - dt:
                # print "Waveform[" + str(wf) + "] Peak[" + str(pk) + "]   action:    " + "left insert"
                peak_time.insert(gr, data[wf][pk].time)       # insert new group of peaks into the groups table
                num_peak_in_gr.insert(gr, 1)                # update the number of peaks in current group
                peak_map[wf].insert(gr, True)               # insert row to current wf column of peak map table
                peak_data[wf].insert(gr, SinglePeak(*data[wf][pk].data_full))   # insert row to current wf column of peak data table
                for curve_i in range(curves_count):
                    if curve_i != wf:
                        peak_map[curve_i].insert(gr, False)  # new row to other columns of peak map table
                        peak_data[curve_i].insert(gr, None)  # new row to other columns of peak data table
                pk += 1                                      # go to the next peak of current curve

            # ===============================================================================================
            # APPEND NEW GROUP
            # check if X-position of current peak of curve[wf] is to the right of current group by more than dt
            # and current group is the latest in the groups table
            elif (data[wf][pk].time > peak_time[gr] + dt) and (gr >= len(peak_time) - 1):
                # print "Waveform[" + str(wf) + "] Peak[" + str(pk) + "]   action:    " + "insert at the end"
                peak_time.append(data[wf][pk].time)           # add new group at the end of the group table
                num_peak_in_gr.append(1)                    # update count of peaks and groups
                peak_map[wf].append(True)                   # add row to current wf column of peak map table
                peak_data[wf].append(SinglePeak(*data[wf][pk].data_full))           # add row to current wf column of peak data table
                for curve_i in range(curves_count):
                    if curve_i != wf:
                        peak_map[curve_i].append(False)  # add row to other columns of peak map table
                        peak_data[curve_i].append(None)  # add row to other columns of peak data table
                pk += 1                                  # go to the next peak...
                gr += 1                                  # ... and the next group

            # ===============================================================================================
            # APPEND NEW GROUP
            # if we are here then the X-position of current peak of curve[curve_i]
            # is to the right of current group by more than dt
            # so go to the next group
            if gr < len(peak_time) - 1:
                gr += 1
    # END OF GROUPING
    # =======================================================================================================
    # print peak_time
    # print num_peak_in_gr
    return peak_data, peak_map


if __name__ == '__main__':
    print('Done!!!')