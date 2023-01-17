import pandas as pd
import numpy as np
import statistics
import matplotlib.pyplot as plt
from collections import Counter


#Global variables
timestamp   =   ['TIME_STAMP']
mac_tput_col=   ['5G KPI Total Info Layer2 MAC DL Throughput [Mbps]']
ca_col=         ['5G KPI Total Info DL CA Type']
carrier_tput_cols   =   \
                ['5G KPI PCell Layer2 MAC DL Throughput [Mbps]',
                '5G KPI SCell[1] Layer2 MAC DL Throughput [Mbps]',
                '5G KPI SCell[2] Layer2 MAC DL Throughput [Mbps]',
                '5G KPI SCell[3] Layer2 MAC DL Throughput [Mbps]',
                '5G KPI SCell[4] Layer2 MAC DL Throughput [Mbps]',
                '5G KPI SCell[5] Layer2 MAC DL Throughput [Mbps]',
                '5G KPI SCell[6] Layer2 MAC DL Throughput [Mbps]',
                '5G KPI SCell[7] Layer2 MAC DL Throughput [Mbps]']

data_dir    =  '/home/dinhp/data/wowmom_ext/ca/atnt/single/' 
send_rates = ['10', '50', '100',
            '200', '225', '250', 
            '275', '300', '500',
             '1000','1500','max']
run_nums = [1,2,3,4,5]
clients =   ['phone_1']
operator    =   'atnt'
fig_size   =   (20, 10)

def preprocess_df(csv_file):
    """
    Clean na and convert time stamp to index
    """
    df  =   pd.read_csv(csv_file, low_memory=False)
    df  =   df[timestamp+mac_tput_col+ca_col+carrier_tput_cols]
    df.drop(df.tail(8).index,inplace=True)

    #convert 'TIME_STAMP' to datetime object 
    df['TIME_STAMP']   =   pd.to_datetime(df['TIME_STAMP'],
                                        format='%Y-%m-%d %H:%M:%S.%f')
    df.set_index('TIME_STAMP', inplace=True)

    #atnt is seperated by a bursts of very low throughput, the following
    #help the seperation and also excluding very low value
    df  =   df[df[mac_tput_col]>2]
    result  =   df.dropna(subset=mac_tput_col)
    return result

def get_per_rate_sub_df(df):
    """
    Get all sub_df containing the info of each run
    """
    result =   []
    last_time_stamp =   df.index[-1]

    start_time  =   df.index[0]
    end_time    =   start_time+pd.Timedelta(seconds=20)
    
    carrier_tputs   =   []
    while end_time <= last_time_stamp:
        per_rate_df  =  df[start_time:end_time] 
        result.append(per_rate_df)
        start_time =   end_time+pd.Timedelta(seconds=5)
        end_time   =   start_time+pd.Timedelta(seconds=20)
    return result

def bar_plot_send_rate_throughput(csv_file_list):
    """
    Plot average throughput per sending rate for all runs
    """
    fig, axs    =   plt.subplots(nrows  =   len(csv_file_list),
                                ncols   =   len(clients),
                                sharex=True)
    fig.set_size_inches(fig_size)
    for csv_file in csv_file_list:
        avgs    =   []
        stds    =   []
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        for sub_df in sub_df_list:
            avgs += np.mean(sub_df[mac_tput_col]).tolist()
            stds += np.std(sub_df[mac_tput_col]).tolist()

        container  =   axs[csv_file_list.index(csv_file)].bar(x=send_rates, 
                                                    height=avgs, yerr=stds)
        axs[csv_file_list.index(csv_file)].bar_label(container)
    fig.savefig(f"figures/{len(clients)}_clients_{operator}_average_tput")

if __name__ == '__main__':
   
    csv_file_list   =   []
    for run_num in run_nums:
        csv_file_list.append(data_dir+ str(run_num)+'.csv')

    bar_plot_send_rate_throughput(csv_file_list)

