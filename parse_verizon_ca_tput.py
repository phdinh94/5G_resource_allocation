import pandas as pd
import numpy as np
import statistics
import matplotlib.pyplot as plt
from collections import Counter
import re


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
                '5G KPI SCell[5] Layer2 MAC DL Throughput [Mbps]']

carrier_rsrp_cols   =   \
        ['5G KPI PCell RF Serving SS-RSRP [dBm]',
        '5G KPI SCell[1] RF Serving SS-RSRP [dBm]',
        '5G KPI SCell[2] RF Serving SS-RSRP [dBm]',
        '5G KPI SCell[3] RF Serving SS-RSRP [dBm]',
        '5G KPI SCell[4] RF Serving SS-RSRP [dBm]',
        '5G KPI SCell[5] RF Serving SS-RSRP [dBm]']

renamed_cols    =   ['PCell', 'SC1', 'SC2', 'SC3', 'SC4', 'SC5']
renamed_tput_dict    =   dict(zip(carrier_tput_cols, renamed_cols))
renamed_rsrp_dict    =   dict(zip(carrier_rsrp_cols, renamed_cols))

data_dir    =  '/home/dinhp/data/wowmom_ext/ca/verizon/verizon_10_max/' 

#verizon single
operator    =   'verizon'
send_rates  =   ['10', '50', '100', 
                '250', '500', '1000', '1500', 'max']
run_nums = [1,2,3,4,5]
clients =   ['phone_1']
fig_size    =   (20,10)

##verizon 2 users
#operator    =   'verizon'
#send_rates  =   ['10', '50', '100', 
#                '250', '500', '1000', '1500', 'max']
#run_nums = [1,2,3,4]
#clients =   ['phone_1', 'phone_2']
#fig_size    =   (20,10)

##verizon 3 users
#data_dir    =  '/home/dinhp/data/wowmom_ext/ca/verizon/' 
#operator    =   'verizon'
#send_rates = ['10', '50', '100',
#            '200', '225', '250', 
#            '275', '300', '500',
#             '1000','1500','max']
#run_nums = [1,2,3,4,5]
#clients =   ['phone_1', 'phone_2', 'phone_3']
#fig_size    =   (20,10)

def preprocess_df(csv_file):
    """
    Clean na and convert time stamp to index
    """
    df  =   pd.read_csv(csv_file, low_memory=False)
    df  =   df[timestamp+mac_tput_col+ca_col+
                carrier_tput_cols+carrier_rsrp_cols]
    df.drop(df.tail(8).index,inplace=True)

    #convert 'TIME_STAMP' to datetime object 
    df['TIME_STAMP']   =   pd.to_datetime(df['TIME_STAMP'],
                                        format='%Y-%m-%d %H:%M:%S.%f')
    df.set_index('TIME_STAMP', inplace=True)

    #help the seperation and also excluding very low value
    df  =   df[(df[mac_tput_col]>2).all(axis=1)]
    df  =   df.dropna(subset=mac_tput_col)
    df[carrier_tput_cols]  =   df[carrier_tput_cols].fillna(value=0)
    result  =   df
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

def bar_plot_average_tput_single_user(run_nums):
    """
    Plot average throughput per sending rate for all runs, single user
    """
    csv_file_list   =   []
    for run_num in run_nums:
        csv_file_list.append(data_dir+ 'single/' + str(run_num)+'.csv')

    fig, axs    =   plt.subplots(nrows  =   len(csv_file_list),
                                ncols   =   len(clients),
                                sharex=True)

    fig.set_size_inches(fig_size)
    for csv_file in csv_file_list:
        avgs    =   []
        stds    =   []
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        for sub_df in sub_df_list:
            avgs += round(np.mean(sub_df[mac_tput_col])).tolist()
            stds += round(np.std(sub_df[mac_tput_col])).tolist()

        container  =   axs[csv_file_list.index(csv_file)].bar(x=send_rates, 
                                                    height=avgs, yerr=stds)
        axs[csv_file_list.index(csv_file)].bar_label(container)
    fig.savefig(f"figures/{operator}/single_{operator}_average_tput")

def bar_plot_average_tput_single_user(run_nums):
    """
    Plot average throughput per sending rate for all runs, single user
    """
    csv_file_list   =   []
    for run_num in run_nums:
        csv_file_list.append(data_dir+ 'single/' + str(run_num)+'.csv')

    fig, axs    =   plt.subplots(nrows  =   len(csv_file_list),
                                ncols   =   len(clients),
                                sharex=True,
                                sharey=True)

    fig.set_size_inches(fig_size)
    for csv_file in csv_file_list:
        avgs    =   []
        stds    =   []
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        for sub_df in sub_df_list:
            avgs += round(np.mean(sub_df[mac_tput_col])).tolist()
            stds += round(np.std(sub_df[mac_tput_col])).tolist()
#
        container  =   axs[csv_file_list.index(csv_file)].bar(x=send_rates, 
                                                    height=avgs, yerr=stds)
        axs[csv_file_list.index(csv_file)].bar_label(container)
        axs[csv_file_list.index(csv_file)].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list.index(csv_file)].set_ylabel("Throughput (Mbps)",
                                                        fontsize=10)
    fig.savefig(f"figures/{operator}/single_{operator}_average_tput")

def bar_plot_average_tput_2_users(run_nums):
    """
    Plot average throughput per sending rate for all runs, 2 users
    """
    csv_file_list_1   =   []
    csv_file_list_2   =   []
    for run_num in run_nums:
        csv_file_list_1.append(data_dir+ '2_phones/phone_1/'
                                     + str(run_num)+'.csv')
        csv_file_list_2.append(data_dir+ '2_phones/phone_2/' 
                                    + str(run_num)+'.csv')

    fig, axs    =   plt.subplots(nrows  =   len(run_nums),
                                ncols   =   len(clients),
                                sharex=True,
                                sharey=True)

    fig.set_size_inches(fig_size)

    #phone_1
    for csv_file in csv_file_list_1:
        avgs    =   []
        stds    =   []
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        for sub_df in sub_df_list:
            avgs += round(np.mean(sub_df[mac_tput_col])).tolist()
            stds += round(np.std(sub_df[mac_tput_col])).tolist()

        container  =   axs[csv_file_list_1.index(csv_file)][0].bar(
                                                x=send_rates, 
                                                height=avgs, 
                                                yerr=stds)
        axs[csv_file_list_1.index(csv_file)][0].bar_label(container)
        axs[csv_file_list_1.index(csv_file)][0].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_1.index(csv_file)][0].set_ylabel("Throughput (Mbps)",
                                                        fontsize=10)

    #phone_2
    for csv_file in csv_file_list_2:
        avgs    =   []
        stds    =   []
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        for sub_df in sub_df_list:
            avgs += round(np.mean(sub_df[mac_tput_col])).tolist()
            stds += round(np.std(sub_df[mac_tput_col])).tolist()

        container  =   axs[csv_file_list_2.index(csv_file)][1].bar(
                                                x=send_rates, 
                                                height=avgs, 
                                                yerr=stds)
        axs[csv_file_list_2.index(csv_file)][1].bar_label(container)
        axs[csv_file_list_2.index(csv_file)][1].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_2.index(csv_file)][1].set_ylabel("Throughput (Mbps)",
                                                        fontsize=10)

    fig.savefig(f"figures/{operator}/2_users_{operator}_average_tput")

def bar_plot_average_tput_3_users(run_nums):
    """
    Plot average throughput per sending rate for all runs, 3 users
    """
    csv_file_list_1   =   []
    csv_file_list_2   =   []
    csv_file_list_3   =   []
    for run_num in run_nums:
        csv_file_list_1.append(data_dir+ '3_phones/phone_1/'
                                     + str(run_num)+'.csv')
        csv_file_list_2.append(data_dir+ '3_phones/phone_2/' 
                                    + str(run_num)+'.csv')
        csv_file_list_3.append(data_dir+ '3_phones/phone_3/' 
                                    + str(run_num)+'.csv')

    fig, axs    =   plt.subplots(nrows  =   len(run_nums),
                                ncols   =   len(clients),
                                sharex=True,
                                sharey=True)

    fig.set_size_inches(fig_size)

    #phone_1
    for csv_file in csv_file_list_1:
        avgs    =   []
        stds    =   []
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        for sub_df in sub_df_list:
            avgs += round(np.mean(sub_df[mac_tput_col])).tolist()
            stds += round(np.std(sub_df[mac_tput_col])).tolist()

        container  =   axs[csv_file_list_1.index(csv_file)][0].bar(
                                                x=send_rates, 
                                                height=avgs, 
                                                yerr=stds)
        axs[csv_file_list_1.index(csv_file)][0].bar_label(container)
        axs[csv_file_list_1.index(csv_file)][0].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_1.index(csv_file)][0].set_ylabel("Throughput (Mbps)",
                                                        fontsize=10)

    #phone_2
    for csv_file in csv_file_list_2:
        avgs    =   []
        stds    =   []
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        for sub_df in sub_df_list:
            avgs += round(np.mean(sub_df[mac_tput_col])).tolist()
            stds += round(np.std(sub_df[mac_tput_col])).tolist()

        container  =   axs[csv_file_list_2.index(csv_file)][1].bar(
                                                x=send_rates, 
                                                height=avgs, 
                                                yerr=stds)
        axs[csv_file_list_2.index(csv_file)][1].bar_label(container)
        axs[csv_file_list_2.index(csv_file)][1].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_2.index(csv_file)][1].set_ylabel("Throughput (Mbps)",
                                                        fontsize=10)

    #phone_3
    for csv_file in csv_file_list_3:
        avgs    =   []
        stds    =   []
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        for sub_df in sub_df_list:
            avgs += round(np.mean(sub_df[mac_tput_col])).tolist()
            stds += round(np.std(sub_df[mac_tput_col])).tolist()

        container  =   axs[csv_file_list_3.index(csv_file)][2].bar(
                                                x=send_rates, 
                                                height=avgs, 
                                                yerr=stds)
        axs[csv_file_list_3.index(csv_file)][2].bar_label(container)
        axs[csv_file_list_3.index(csv_file)][2].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_3.index(csv_file)][2].set_ylabel("Throughput (Mbps)",
                                                        fontsize=10)
    fig.savefig(f"figures/{operator}/3_users_{operator}_average_tput")

def bar_plot_ca_tput_single_user(run_nums):
    """
    Plot average throughput per sending rate + per ca for all runs, single user
    """
    csv_file_list   =   []
    for run_num in run_nums:
        csv_file_list.append(data_dir+ 'single/' + str(run_num)+'.csv')

    fig, axs    =   plt.subplots(nrows  =   len(csv_file_list))
    fig.set_size_inches(fig_size)

    for csv_file in csv_file_list:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_tputs    =   {}
        for col in carrier_tput_cols:
            carrier_average_tputs[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_tput_cols:
                carrier_average_tputs[col].append(np.mean(sub_df[col]))
        carrier_average_tputs['sending rates']   =   send_rates
        df  =   pd.DataFrame.from_dict(carrier_average_tputs)
        #rename columns
        df  =   df.rename(columns    =   renamed_tput_dict)
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols, 
                    ax  =   axs[csv_file_list.index(csv_file)],
                    stacked =   True,
                    rot=0)
        axs[csv_file_list.index(csv_file)].legend(loc   =   'upper left',
                                                ncol    =   3)
        axs[csv_file_list.index(csv_file)].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list.index(csv_file)].set_ylabel("Throughput (Mbps)",
                                                        fontsize=10)
        if(csv_file_list.index(csv_file)!=0):
            axs[csv_file_list.index(csv_file)].get_legend().remove()


    fig.savefig(f"figures/{operator}/single_{operator}_per_carrier_average_tput")

def bar_plot_ca_tput_2_users(run_nums):
    """
    Plot average throughput per sending rate + per ca for all runs, 2 users
    """
    csv_file_list_1   =   []
    csv_file_list_2   =   []
    for run_num in run_nums:
        csv_file_list_1.append(data_dir+ '2_phones/phone_1/'
                                     + str(run_num)+'.csv')
        csv_file_list_2.append(data_dir+ '2_phones/phone_2/' 
                                    + str(run_num)+'.csv')

    fig, axs    =   plt.subplots(nrows  =   len(run_nums),
                                ncols   =   len(clients),
                                sharex=True,
                                sharey=True)

    fig.set_size_inches(fig_size)
    #phone_1
    for csv_file in csv_file_list_1:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_tputs    =   {}
        for col in carrier_tput_cols:
            carrier_average_tputs[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_tput_cols:
                carrier_average_tputs[col].append(np.mean(sub_df[col]))
        carrier_average_tputs['sending rates']   =   send_rates
        df  =   pd.DataFrame.from_dict(carrier_average_tputs)
        #rename columns
        df  =   df.rename(columns    =   renamed_tput_dict)
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols, 
                    ax  =   axs[csv_file_list_1.index(csv_file)][0],
                    stacked =   True,
                    rot=0)
        axs[csv_file_list_1.index(csv_file)][0].legend(loc   =   'upper left',
                                                ncol    =   3)
        axs[csv_file_list_1.index(csv_file)][0].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_1.index(csv_file)][0].set_ylabel("Throughput (Mbps)",
                                                        fontsize=10)
        if(csv_file_list_1.index(csv_file)!=0):
            axs[csv_file_list_1.index(csv_file)][0].get_legend().remove()

    #phone_2
    for csv_file in csv_file_list_2:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_tputs    =   {}
        for col in carrier_tput_cols:
            carrier_average_tputs[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_tput_cols:
                carrier_average_tputs[col].append(np.mean(sub_df[col]))
        carrier_average_tputs['sending rates']   =   send_rates
        df  =   pd.DataFrame.from_dict(carrier_average_tputs)
        #rename columns
        df  =   df.rename(columns    =   renamed_tput_dict)
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols, 
                    ax  =   axs[csv_file_list_2.index(csv_file)][1],
                    stacked =   True,
                    rot=0)
        axs[csv_file_list_2.index(csv_file)][1].legend(loc   =   'upper left',
                                                ncol    =   3)
        axs[csv_file_list_2.index(csv_file)][1].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_2.index(csv_file)][1].set_ylabel("Throughput (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_2.index(csv_file)][1].get_legend().remove()

    fig.savefig(f"figures/{operator}/2_users_{operator}_per_carrier_average_tput")

def bar_plot_ca_tput_3_users(run_nums):

    """
    Plot average throughput per sending rate + per ca for all runs, 2 users
    """
    csv_file_list_1   =   []
    csv_file_list_2   =   []
    csv_file_list_3   =   []
    for run_num in run_nums:
        csv_file_list_1.append(data_dir+ '3_phones/phone_1/'
                                     + str(run_num)+'.csv')
        csv_file_list_2.append(data_dir+ '3_phones/phone_2/' 
                                    + str(run_num)+'.csv')
        csv_file_list_3.append(data_dir+ '3_phones/phone_3/' 
                                    + str(run_num)+'.csv')

    fig, axs    =   plt.subplots(nrows  =   len(run_nums),
                                ncols   =   len(clients),
                                sharex=True,
                                sharey=True)

    fig.set_size_inches(fig_size)
    #phone_1
    for csv_file in csv_file_list_1:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_tputs    =   {}
        for col in carrier_tput_cols:
            carrier_average_tputs[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_tput_cols:
                carrier_average_tputs[col].append(np.mean(sub_df[col]))
        carrier_average_tputs['sending rates']   =   send_rates
        df  =   pd.DataFrame.from_dict(carrier_average_tputs)
        #rename columns
        df  =   df.rename(columns    =   renamed_tput_dict)
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols, 
                    ax  =   axs[csv_file_list_1.index(csv_file)][0],
                    stacked =   True,
                    rot=0)
        axs[csv_file_list_1.index(csv_file)][0].legend(loc   =   'upper left',
                                                ncol    =   3)
        axs[csv_file_list_1.index(csv_file)][0].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_1.index(csv_file)][0].set_ylabel("Throughput (Mbps)",
                                                        fontsize=10)
        if(csv_file_list_1.index(csv_file)!=0):
            axs[csv_file_list_1.index(csv_file)][0].get_legend().remove()

    #phone_2
    for csv_file in csv_file_list_2:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_tputs    =   {}
        for col in carrier_tput_cols:
            carrier_average_tputs[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_tput_cols:
                carrier_average_tputs[col].append(np.mean(sub_df[col]))
        carrier_average_tputs['sending rates']   =   send_rates
        df  =   pd.DataFrame.from_dict(carrier_average_tputs)
        #rename columns
        df  =   df.rename(columns    =   renamed_tput_dict)
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols, 
                    ax  =   axs[csv_file_list_2.index(csv_file)][1],
                    stacked =   True,
                    rot=0)
        axs[csv_file_list_2.index(csv_file)][1].get_legend().remove()
        axs[csv_file_list_2.index(csv_file)][1].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_2.index(csv_file)][1].set_ylabel("Throughput (Mbps)",
                                                        fontsize=10)

    #phone_3
    for csv_file in csv_file_list_3:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_tputs    =   {}
        for col in carrier_tput_cols:
            carrier_average_tputs[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_tput_cols:
                carrier_average_tputs[col].append(np.mean(sub_df[col]))
        carrier_average_tputs['sending rates']   =   send_rates
        df  =   pd.DataFrame.from_dict(carrier_average_tputs)
        #rename columns
        df  =   df.rename(columns    =   renamed_tput_dict)
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols, 
                    ax  =   axs[csv_file_list_3.index(csv_file)][2],
                    stacked =   True,
                    rot=0)
        axs[csv_file_list_3.index(csv_file)][2].get_legend().remove()
        axs[csv_file_list_3.index(csv_file)][2].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_3.index(csv_file)][2].set_ylabel("Throughput (Mbps)",
                                                        fontsize=10)

    fig.savefig(f"figures/{operator}/3_users_{operator}_per_carrier_average_tput")

def plot_pcell_tput_usage_2_users(rum_nums):
    """
    Plot total throughput usage per carrier + sending rate for all runs, 2 users
    """
    csv_file_list_1   =   []
    csv_file_list_2   =   []
    for run_num in run_nums:
        csv_file_list_1.append(data_dir+ '2_phones/phone_1/'
                                     + str(run_num)+'.csv')
        csv_file_list_2.append(data_dir+ '2_phones/phone_2/' 
                                    + str(run_num)+'.csv')

    fig, axs    =   plt.subplots(nrows  =   len(run_nums),
                                ncols   =   1,
                                sharex=True,
                                sharey=True)

    fig.set_size_inches(fig_size)
    

    #phone_1
    df_list_1   =   []
    for csv_file in csv_file_list_1:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_tputs    =   {}
        for col in carrier_tput_cols:
            carrier_average_tputs[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_tput_cols:
                carrier_average_tputs[col].append(np.mean(sub_df[col]))
        df  =   pd.DataFrame.from_dict(carrier_average_tputs)
        #rename columns
        df  =   df.rename(columns    =   renamed_tput_dict)
        df_list_1.append(df)

    #phone_2
    df_list_2   =   []
    for csv_file in csv_file_list_2:
        carrier_average_tputs    =   {}
        for col in carrier_tput_cols:
            carrier_average_tputs[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_tput_cols:
                carrier_average_tputs[col].append(np.mean(sub_df[col]))
        df  =   pd.DataFrame.from_dict(carrier_average_tputs)
        #rename columns
        df  =   df.rename(columns    =   renamed_tput_dict)
        df_list_2.append(df)
   
    count   =   0
    for df_1, df_2 in zip(df_list_1, df_list_2):
        df  =   df_1 + df_2
        df['sending rates']    = send_rates
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols[0], 
                    ax  =   axs[count],
                    stacked =   True,
                    rot=0)
        container  =   axs[count].bar(x=send_rates, 
                                    height=df[renamed_cols[0]])
        axs[count].set_xlabel("Send rates (Mbps)",
                                fontsize=10)
        axs[count].set_ylabel("Throughput (Mbps)",
                                fontsize=10)
        axs[count].bar_label(container)
        count   +=1

    fig.savefig(f"figures/{operator}/2_users_{operator}_pcell_tput_usage")

def plot_pcell_tput_usage_3_users(rum_nums):
    """
    Plot total throughput usage per carrier + sending rate for all runs, 2 users
    """
    csv_file_list_1   =   []
    csv_file_list_2   =   []
    csv_file_list_3   =   []
    for run_num in run_nums:
        csv_file_list_1.append(data_dir+ '3_phones/phone_1/'
                                     + str(run_num)+'.csv')
        csv_file_list_2.append(data_dir+ '3_phones/phone_2/' 
                                    + str(run_num)+'.csv')
        csv_file_list_3.append(data_dir+ '3_phones/phone_3/' 
                                    + str(run_num)+'.csv')

    fig, axs    =   plt.subplots(nrows  =   len(run_nums),
                                ncols   =   1,
                                sharex=True,
                                sharey=True)
    

    fig.set_size_inches(fig_size)
    

    #phone_1
    df_list_1   =   []
    for csv_file in csv_file_list_1:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_tputs    =   {}
        for col in carrier_tput_cols:
            carrier_average_tputs[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_tput_cols:
                carrier_average_tputs[col].append(np.mean(sub_df[col]))
        df  =   pd.DataFrame.from_dict(carrier_average_tputs)
        #rename columns
        df  =   df.rename(columns    =   renamed_tput_dict)
        df_list_1.append(df)

    #phone_2
    df_list_2   =   []
    for csv_file in csv_file_list_2:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_tputs    =   {}
        for col in carrier_tput_cols:
            carrier_average_tputs[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_tput_cols:
                carrier_average_tputs[col].append(np.mean(sub_df[col]))
        df  =   pd.DataFrame.from_dict(carrier_average_tputs)
        #rename columns
        df  =   df.rename(columns    =   renamed_tput_dict)
        df_list_2.append(df)

    #phone_3
    df_list_3   =   []
    for csv_file in csv_file_list_3:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_tputs    =   {}
        for col in carrier_tput_cols:
            carrier_average_tputs[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_tput_cols:
                carrier_average_tputs[col].append(np.mean(sub_df[col]))
        df  =   pd.DataFrame.from_dict(carrier_average_tputs)
        #rename columns
        df  =   df.rename(columns    =   renamed_tput_dict)
        df_list_3.append(df)
   
    count   =   0

    for df_1, df_2, df_3 in zip(df_list_1, df_list_2, df_list_3):
        df  =   df_1 + df_2 +  df_3
        df['sending rates']    = send_rates
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols[0], 
                    ax  =   axs[count],
                    stacked =   True,
                    rot=0)
        container  =   axs[count].bar(x=send_rates, 
                                    height=df[renamed_cols[0]])
        axs[count].bar_label(container)
        axs[count].set_xlabel("Send rates (Mbps)",
                                fontsize=10)
        axs[count].set_ylabel("Throughput (Mbps)",
                                fontsize=10)
        count   +=1

    fig.savefig(f"figures/{operator}/3_users_{operator}_pcell_tput_usage")

def bar_plot_ca_rsrp_single_user(run_nums):
    """
    Plot average rsrp per sending rate + per ca for all runs, 2 users
    """
    csv_file_list   =   []
    for run_num in run_nums:
        csv_file_list.append(data_dir+ 'single/'
                                     + str(run_num)+'.csv')

    fig, axs    =   plt.subplots(nrows  =   len(run_nums),
                                ncols   =   len(clients),
                                sharex=True,
                                sharey=True)

    fig.set_size_inches(fig_size)
    #phone_1
    for csv_file in csv_file_list:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_rsrp    =   {}
        for col in carrier_rsrp_cols:
            carrier_average_rsrp[col]  =   []
        for sub_df  in sub_df_list:
            #Get average rsrp per carrier
            for col in carrier_rsrp_cols:
                carrier_average_rsrp[col].append(np.mean(sub_df[col]))
        carrier_average_rsrp['sending rates']   =   send_rates
        df  =   pd.DataFrame.from_dict(carrier_average_rsrp)
        #rename columns
        df  =   df.rename(columns    =   renamed_rsrp_dict)
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols, 
                    ax  =   axs[csv_file_list.index(csv_file)],
                    stacked =   False,
                    rot=0)
        axs[csv_file_list.index(csv_file)].legend(loc   =   'upper left',
                                                ncol    =   3)
        axs[csv_file_list.index(csv_file)].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list.index(csv_file)].set_ylabel("RSRP (dBm)",
                                                        fontsize=10)
        if(csv_file_list.index(csv_file)!=0):
            axs[csv_file_list.index(csv_file)].get_legend().remove()


    fig.savefig(f"figures/{operator}/single_user_{operator}_per_carrier_average_rsrp")

def bar_plot_ca_rsrp_2_users(run_nums):
    """
    Plot average rsrp per sending rate + per ca for all runs, 2 users
    """
    csv_file_list_1   =   []
    csv_file_list_2   =   []
    for run_num in run_nums:
        csv_file_list_1.append(data_dir+ '2_phones/phone_1/'
                                     + str(run_num)+'.csv')
        csv_file_list_2.append(data_dir+ '2_phones/phone_2/' 
                                    + str(run_num)+'.csv')

    fig, axs    =   plt.subplots(nrows  =   len(run_nums),
                                ncols   =   len(clients),
                                sharex=True,
                                sharey=True)

    fig.set_size_inches(fig_size)
    #phone_1
    for csv_file in csv_file_list_1:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_rsrp    =   {}
        for col in carrier_rsrp_cols:
            carrier_average_rsrp[col]  =   []
        for sub_df  in sub_df_list:
            #Get average rsrp per carrier
            for col in carrier_rsrp_cols:
                carrier_average_rsrp[col].append(np.mean(sub_df[col]))
        carrier_average_rsrp['sending rates']   =   send_rates
        df  =   pd.DataFrame.from_dict(carrier_average_rsrp)
        #rename columns
        df  =   df.rename(columns    =   renamed_rsrp_dict)
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols, 
                    ax  =   axs[csv_file_list_1.index(csv_file)][0],
                    stacked =   False,
                    rot=0)
        axs[csv_file_list_1.index(csv_file)][0].legend(loc   =   'upper left',
                                                ncol    =   3)
        axs[csv_file_list_1.index(csv_file)][0].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_1.index(csv_file)][0].set_ylabel("RSRP (dBm)",
                                                        fontsize=10)
        if(csv_file_list_1.index(csv_file)!=0):
            axs[csv_file_list_1.index(csv_file)][0].get_legend().remove()

    #phone_2
    for csv_file in csv_file_list_2:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_rsrp    =   {}
        for col in carrier_rsrp_cols:
            carrier_average_rsrp[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_rsrp_cols:
                carrier_average_rsrp[col].append(np.mean(sub_df[col]))
        carrier_average_rsrp['sending rates']   =   send_rates
        df  =   pd.DataFrame.from_dict(carrier_average_rsrp)
        #rename columns
        df  =   df.rename(columns    =   renamed_rsrp_dict)
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols, 
                    ax  =   axs[csv_file_list_2.index(csv_file)][1],
                    stacked =   False,
                    rot=0)
        axs[csv_file_list_2.index(csv_file)][1].legend(loc   =   'upper left',
                                                ncol    =   3)
        axs[csv_file_list_2.index(csv_file)][1].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_2.index(csv_file)][1].set_ylabel("RSRP (dBm)",
                                                        fontsize=10)
        axs[csv_file_list_2.index(csv_file)][1].get_legend().remove()

    fig.savefig(f"figures/{operator}/2_users_{operator}_per_carrier_average_rsrp")

def bar_plot_ca_rsrp_3_users(run_nums):
    """
    Plot average rsrp per sending rate + per ca for all runs, 2 users
    """
    csv_file_list_1   =   []
    csv_file_list_2   =   []
    csv_file_list_3   =   []
    for run_num in run_nums:
        csv_file_list_1.append(data_dir+ '3_phones/phone_1/'
                                     + str(run_num)+'.csv')
        csv_file_list_2.append(data_dir+ '3_phones/phone_2/' 
                                    + str(run_num)+'.csv')
        csv_file_list_3.append(data_dir+ '3_phones/phone_3/' 
                                    + str(run_num)+'.csv')

    fig, axs    =   plt.subplots(nrows  =   len(run_nums),
                                ncols   =   len(clients),
                                sharex=True,
                                sharey=True)

    fig.set_size_inches(fig_size)
    #phone_1
    for csv_file in csv_file_list_1:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_rsrp    =   {}
        for col in carrier_rsrp_cols:
            carrier_average_rsrp[col]  =   []
        for sub_df  in sub_df_list:
            #Get average rsrp per carrier
            for col in carrier_rsrp_cols:
                carrier_average_rsrp[col].append(np.mean(sub_df[col]))
        carrier_average_rsrp['sending rates']   =   send_rates
        df  =   pd.DataFrame.from_dict(carrier_average_rsrp)
        #rename columns
        df  =   df.rename(columns    =   renamed_rsrp_dict)
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols, 
                    ax  =   axs[csv_file_list_1.index(csv_file)][0],
                    stacked =   False,
                    rot=0)
        axs[csv_file_list_1.index(csv_file)][0].legend(loc   =   'upper left',
                                                ncol    =   3)
        axs[csv_file_list_1.index(csv_file)][0].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_1.index(csv_file)][0].set_ylabel("RSRP (dBm)",
                                                        fontsize=10)
        if(csv_file_list_1.index(csv_file)!=0):
            axs[csv_file_list_1.index(csv_file)][0].get_legend().remove()

    #phone_2
    for csv_file in csv_file_list_2:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_rsrp    =   {}
        for col in carrier_rsrp_cols:
            carrier_average_rsrp[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_rsrp_cols:
                carrier_average_rsrp[col].append(np.mean(sub_df[col]))
        carrier_average_rsrp['sending rates']   =   send_rates
        df  =   pd.DataFrame.from_dict(carrier_average_rsrp)
        #rename columns
        df  =   df.rename(columns    =   renamed_rsrp_dict)
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols, 
                    ax  =   axs[csv_file_list_2.index(csv_file)][1],
                    stacked =   False,
                    rot=0)
        axs[csv_file_list_2.index(csv_file)][1].legend(loc   =   'upper left',
                                                ncol    =   3)
        axs[csv_file_list_2.index(csv_file)][1].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_2.index(csv_file)][1].set_ylabel("RSRP (dBm)",
                                                        fontsize=10)
        axs[csv_file_list_2.index(csv_file)][1].get_legend().remove()

    #phone_3
    for csv_file in csv_file_list_3:
        sub_df_list =   get_per_rate_sub_df(preprocess_df(csv_file))
        carrier_average_rsrp    =   {}
        for col in carrier_rsrp_cols:
            carrier_average_rsrp[col]  =   []
        for sub_df  in sub_df_list:
            #Get average throughput per carrier
            for col in carrier_rsrp_cols:
                carrier_average_rsrp[col].append(np.mean(sub_df[col]))
        carrier_average_rsrp['sending rates']   =   send_rates
        df  =   pd.DataFrame.from_dict(carrier_average_rsrp)
        #rename columns
        df  =   df.rename(columns    =   renamed_rsrp_dict)
        df.plot.bar(x   =   'sending rates',
                    y   =   renamed_cols, 
                    ax  =   axs[csv_file_list_3.index(csv_file)][2],
                    stacked =   False,
                    rot=0)
        axs[csv_file_list_3.index(csv_file)][2].legend(loc   =   'upper left',
                                                ncol    =   3)
        axs[csv_file_list_3.index(csv_file)][2].set_xlabel("Send rates (Mbps)",
                                                        fontsize=10)
        axs[csv_file_list_3.index(csv_file)][2].set_ylabel("RSRP (dBm)",
                                                        fontsize=10)
        axs[csv_file_list_3.index(csv_file)][2].get_legend().remove()

    fig.savefig(f"figures/{operator}/3_users_{operator}_per_carrier_average_rsrp")

if __name__ == '__main__':
   

    #bar_plot_average_tput_single_user(run_nums)
    #bar_plot_ca_tput_single_user(run_nums)
    #bar_plot_ca_rsrp_single_user(run_nums)
    #bar_plot_average_tput_2_users(run_nums)
    #bar_plot_ca_tput_2_users(run_nums)
    #plot_pcell_tput_usage_2_users(run_nums)
    #bar_plot_ca_rsrp_2_users(run_nums)
    #bar_plot_average_tput_3_users(run_nums)
    #bar_plot_ca_tput_3_users(run_nums)
    #plot_pcell_tput_usage_3_users(run_nums)
    #bar_plot_ca_rsrp_3_users(run_nums)
