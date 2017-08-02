import numpy as np
import os
import re
from matplotlib import pyplot as plt
import SignalProcess as sp
import PeakProcess as pp
import wfm_reader_lite as wfm


# def align_by_voltage_front_old(data,                # an instance of SignalsData class
#                            voltage_col,         # index or label of voltage curve in SignalsData
#                            level=-0.2,          # level of voltage front to be set as time zero
#                            is_positive=False):  # positive polarity of curve or not
#     # INPUT CHECK
#     if not isinstance(data, sp.SignalsData):
#         raise TypeError("Data must be an instance of SignalsData class")
#     if isinstance(voltage_col, str):
#         curve_idx = data.labels[voltage_col]
#     else:
#         curve_idx = voltage_col
#
#     # VOLTAGE FRONT TIME POS
#     smoothed_voltage = sp.smooth_voltage(data.curves[curve_idx].get_x(), data.curves[curve_idx].get_y())
#     front_x, front_y = pp.find_voltage_front(data.curves[curve_idx].get_x(), smoothed_voltage, level, is_positive)
#
#     print "Voltage front time = " + str(front_x) + " ns"
#
#     # TIMELINE CORRECTION
#     if front_x:
#         delay = [front_x if idx % 2 == 0 else 0 for idx in range(data.count * 2)]
#         data = sp.multiplier_and_delay(data, None, delay)
#     return data


def add_to_log(m):
    print(m)

def offset_by_voltage(voltage, level, delay, time_multiplier=1, is_positive=False):
    '''This function finds the time point of voltage front on level
    'level', recalculates input delays of all time columns (odd 
    elements of the input delay list) to make that time point be zero
    and correspondingly offset other curves
    
    NOTE: the voltage curve is not multiplied yet, so the 'level' 
    value must be in raw voltage data units
    
    voltage -- an instance of SingleCurve
    level -- level of voltage front
    delay -- list of floats (delays) for each column in SignalsData
    time_multiplier -- multiplier of time column of voltage curve
        default 1 (for time points in seconds) (1e9 for nanoseconds)
    is_positive -- set to True if voltage have positive polarity
        else False (default)
        
    return -- list of recalculated delays (floats)
    '''

    if not isinstance(voltage, sp.SingleCurve):
        raise TypeError("voltage_curve must be an instance "
                        "of SingleCurve class")

    # smooth voltage curve to improve accuracy of front search
    smoothed_voltage = sp.smooth_voltage(voltage.get_x(),
                                         voltage.get_y(),
                                         time_multiplier)
    front_x, front_y = pp.find_voltage_front(voltage.get_x(),
                                             smoothed_voltage,
                                             level, is_positive,
                                             visualize=False)
    # plt.plot(voltage.get_x(), voltage.get_y(), '-b')
    # plt.plot(voltage.get_x(), smoothed_voltage, '-r')
    # plt.plot([front_x], [front_y], '*g')
    # plt.show()
    return front_x


if __name__ == '__main__':
    # ===========================================================================================================
    # -----     MAIN     -----------------------------
    # ===========================================================================================================
    def make_final():
        # GET FOLDERs PATHs
        path_dict = dict()
        path_list = list()
        osc_list = ["DPO7054", "HMO3004", "TDS2024C", "LeCroy"]

        path_dict["DPO7054"] = ("/media/shpakovkv/6ADA8899DA886365/WORK/2017/2017 05 12-19 ERG" +
                                "/2017 05 13 ERG Input united/DPO7054")
        path_dict["HMO3004"] = ("/media/shpakovkv/6ADA8899DA886365/WORK/2017/2017 05 12-19 ERG/" +
                                "2017 05 13 ERG Input united/HMO3004")

        path_dict["TDS2024C"] = ("/media/shpakovkv/6ADA8899DA886365/WORK/2017/2017 05 12-19 ERG/" +
                                 "2017 05 13 ERG Input united/TDS2024C")

        path_dict["LeCroy"] = ("/media/shpakovkv/6ADA8899DA886365/WORK/2017/2017 05 12-19 ERG/" +
                               "2017 05 13 ERG Input united/LeCroy")
        save_to_folder = "/media/shpakovkv/6ADA8899DA886365/WORK/2017/2017 05 12-19 ERG/2017 05 13 ERG Output final"

        # path_dict["DPO7054"] = "G:\\WORK\\2017 05 13-19 ERG\\2017 05 13 ERG Input united\\2017 05 13 DPO7054 united_CSV"
        # path_dict["HMO3004"] = "G:\\WORK\\2017 05 13-19 ERG\\2017 05 13 ERG Input united\\2017 05 13 HMO3004 united_CSV"
        # path_dict["TDS2024C"] = "G:\\WORK\\2017 05 13-19 ERG\\2017 05 13 ERG Input united\\2017 05 13 TDS2024C united_CSV"
        # path_dict["LeCroy"] = "G:\\WORK\\2017 05 13-19 ERG\\2017 05 13 ERG Input united\\2017 05 13 LeCroy united_CSV"
        # save_to_folder = "G:\\WORK\\2017 05 13-19 ERG\\2017 05 13 ERG Output final"


        file_dict = dict()
        multiplier = dict()
        delay = dict()
        cols_label = dict()

        # GET MULTIPLIERs & DELAYs
        multiplier["DPO7054"] = [1e9, 1.216, 1e9, 0.991, 1e9, 1, 1e9, 0.994]
        delay["DPO7054"] = [134.7, 0, 117.7, 0, 121.7, 0, 131.7, 0]
        cols_label["DPO7054"] = ["Time1", "PMTD1", "Time2", "PMTD2", "Time3", "PMTD3", "Time4", "PMTD4"]

        multiplier["HMO3004"] = [1e9, 0.272, 1e9, 0.951, 1e9, 1.138, 1e9, 1.592]
        delay["HMO3004"] = [87, 0, 124, 0, 142, 0, 124, 0]

        multiplier["TDS2024C"] = [1e9, 1.261, 1e9, 1.094, 1e9, 1.222, 1e9, 1.59]
        delay["TDS2024C"] = [126.5, 0, 111.5, 0, 104.5, 0, 129.5, 0]

        multiplier["LeCroy"] = [1e9, 0.697, 1e9, 4.554, 1e9, 0.25]
        delay["LeCroy"] = [80.3, 0, 367.1, 0, 0, 0]

        all_multiplier = [multiplier[osc][i] for osc in osc_list for i in range(len(multiplier[osc]))]
        all_delay = [delay[osc][i] for osc in osc_list for i in range(len(delay[osc]))]

        voltage_idx = 12    # zero-based index of voltage pair (time-value columns)
        voltage_front_level = -0.2
        is_positive = False

        # GET FILE GROUPS
        for key in path_dict:   # unsorted order
            file_dict[key] = sp.get_file_list_by_ext(path_dict[key], ".CSV", sort=False)

        shoots_count = len(file_dict["DPO7054"])
        for key in path_dict:
            if shoots_count != len(file_dict[key]):
                raise IndexError("The number of .csv files in osc-directories must be the same.")


        # arr = np.genfromtxt("/media/shpakovkv/6ADA8899DA886365/WORK/2017/2017 05 12-19 ERG" +
        #                         "/2017 05 13 ERG Input united/LeCroy/0026.csv", delimiter=",")
        # x = arr[:, 0]
        # y = arr[:, 1]
        # y_smooth = sp.smooth_voltage(x, y, 1)
        # front_x, front_y = pp.find_voltage_front(x, y_smooth,-0.2/0.697)
        # print front_x
        # print str(front_x * 1e9 - 80.3)
        # plt.plot(x, y, "-b")
        # plt.plot(x, y_smooth, "-r")
        # plt.show()

        # READ CSV
        for number in range(shoots_count):      # zero-based index of shoot
            data = sp.SignalsData()
            for osc in osc_list:    # sorted order
                print "Reading " + file_dict[osc][number]
                temp = np.genfromtxt(file_dict[osc][number], delimiter=",")         # read data
                # temp = sp.multiplier_and_delay(temp, multiplier[osc], delay[osc])   # corr data
                data.append(temp)                                                   # add data to array
            # smoothed_voltage = sp.smooth_voltage(data.curves[voltage_idx].get_x(), data.curves[voltage_idx].get_y(), 1)
            # print "voltage level RAW = " + str(raw_level)
            # front_x_raw, front_y_raw = pp.find_voltage_front(data.curves[voltage_idx].get_x(), smoothed_voltage, )
            # time_corr = front_x_raw * all_multiplier[voltage_idx * 2]
            # print "voltage front = " + str(front_x_raw) + "     (" + str(time_corr) + " ns)"

            # print all_delay
            # if front_x_raw:
            #     local_delay = [all_delay[i] + time_corr if i % 2 == 0 else all_delay[i] for i in range(len(all_delay))]
            #
            # else:
            #     local_delay = all_delay[:]

            # time_multiplier = 1     # raw time data is written in seconds by default
            if is_positive:
                add_to_log("Positive polarity")
            else:
                add_to_log("Neagative polarity")
            add_to_log("Searching voltage front at level = " + str(voltage_front_level))
            raw_level = (voltage_front_level + all_delay[voltage_idx * 2 + 1]) / all_multiplier[voltage_idx * 2 + 1]
            front_raw = offset_by_voltage(data.curves[voltage_idx], raw_level, all_delay, is_positive=is_positive)
            if front_raw:
                add_to_log("Raw voltage front level = " + str(raw_level))
                # offset voltage front and compensate voltage delay
                time_offset = (front_raw * all_multiplier[voltage_idx * 2] -
                               all_delay[voltage_idx * 2])
                add_to_log("Time offset by voltage = " + str(time_offset))
                # recalculate delays for time columns (even zero-based indexes)
                local_delay = [all_delay[idx] + time_offset if idx % 2 == 0 else
                               all_delay[idx] for idx in range(len(all_delay))]
            else:
                add_to_log("No voltage front detected!\nTime offset by voltage = 0")
                local_delay = all_delay
            data = sp.multiplier_and_delay(data, all_multiplier, local_delay)
            # data = align_by_voltage_front(data, 12, level=-0.2, is_positive=False)

            table = data.get_array()
            add_to_log("Curves count = " + str(data.count) +
                       "     Columns count = " + str(table.shape[1]) +
                       "     Rows count = " + str(table.shape[0]))

            # print table[len(table) - 1,:]

            # for idx in range(0, data.count, 1):
            #     plt.plot(data.curves[idx].get_x(), data.curves[idx].get_y())
            #     print("Curve #0" + str(idx + 1))
            #     plt.show()

            # for idx in range(0, table.shape[1], 2):
            #     if int(idx // 2 + 1) == 12:
            #         plt.plot(table[:, idx], table[:, idx + 1])
            #         print("Curve #0" + str(idx // 2 + 1))
            #         plt.show()

            file_name = "ERG_" + sp.get_name_from_group_of_files([file_dict["DPO7054"][number]], 4) + "_new.csv"
            save_to = os.path.join(save_to_folder, file_name)
            add_to_log("Saving " + save_to)
            sp.save_ndarray_csv(save_to, table)
            add_to_log("Done!\n")

        # TIME CORR

        # SAVE UNITED FINAL DATA

        # FIND PEAKS

        # data = np.genfromtxt(file_name, delimiter=",")
        # print os.path.basename(file_name) + "    " + str(data.shape)

    def go_peak_process():
        folder = "/media/shpakovkv/6ADA8899DA886365/WORK/2017/2017 05 12-19 ERG/2017 05 13 ERG Output final"
        type = "csv"
        curves_list = [1,2,3,4,5,6,7,8,9,10,11,12]
        file_list = sp.get_file_list_by_ext(folder, ".CSV", sort=True)
        for filename in file_list:
            data = sp.SignalsData(np.genfromtxt(filename, delimiter=','))
            print("Curves count = " + str(data.count))
            peaks = []
            for idx in curves_list:
                # sub_data = sp.SignalsData(data.curves[idx].data)
                sp.save_ndarray_csv("neg_peaks.csv", data.curves[idx].data)
                print("Curve #" + str(idx))
                peaks.append(
                    pp.peak_finder(
                        data.curves[idx].get_x(),
                        data.curves[idx].get_y(),
                        -1, diff_time=25, tnoise=100, graph=True
                    )
                )
            break

    def test_peak_process():
        filename = "pos_peaks.csv"
        data = sp.SignalsData(np.genfromtxt(filename, delimiter=','))
        # data = np.genfromtxt(filename, delimiter=',')
        # data[:,1] = -data[:,1]
        # sp.save_ndarray_csv("pos_peaks.csv", data)
        peaks = []
        for curve in data.curves:
            peaks.append(
                pp.peak_finder(
                    curve.get_x(), curve.get_y(), 1,
                    diff_time=25, tnoise=100,
                    is_negative=False, graph=True
                )
            )


    go_peak_process()
    # test_peak_process()