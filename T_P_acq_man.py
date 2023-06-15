from T_P_acq_func import T_P_acq_csv

"""
Purpose:
    Save P and T data to a csv file when executed

    Description:
        This script records a csv file containing T and P
        values. You can change acquisition parameters by modifying 
        T_P_acq_csv() arguments

"""


T_P_acq_csv(channels_134 = (0, 1), channels_128 = (0, 1), acq_frequency = 10, N_measures = 50, terminal_output = True, data_filename = "data.csv",  alarm_on = True, pressure_alarm = 130)
