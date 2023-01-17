import pandas as pd
import numpy as np
import statistics
import matplotlib.pyplot as plt
from collections import Counter

def get_info(csv_file):
    """
    Clean data and deal with timestamp
    """
    df =   pd.read_csv(csv_file)
    df.drop(df.tail(8).index,inplace=True)
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

    info_cols    =  timestamp+mac_tput_col+ca_col+carrier_tput_cols
    df  =   df[info_cols]

    #convert 'TIME_STAMP' to datetime object 
    df['TIME_STAMP']   =   pd.to_datetime(df['TIME_STAMP'],
                                        format='%Y-%m-%d %H:%M:%S.%f')


    mac_tput_lists  =   []
    ca_lists    =   []
    #Set TIME_STAMP as index
    df.set_index('TIME_STAMP', inplace=True)
    df =   df.dropna()
    last_time_stamp =   df.index[-1]

    start_time  =   df.index[0]
    end_time    =   start_time+pd.Timedelta(seconds=20)
    
    carrier_tputs   =   []
    while end_time <= last_time_stamp:
        tput_slice  =   df[mac_tput_col].loc[start_time:end_time].values
        ca_slice    =   df[ca_col].loc[start_time:end_time].values
        tput_slice  =   [i[0] for i in tput_slice]
        ca_slice    =   [i[0] for i in ca_slice]
        mac_tput_lists.append(tput_slice)
        per_carrier_tputs   =   []
        for col in carrier_tput_cols:
            carrier_tput_slice  =   df[col].loc[start_time:end_time]
            per_carrier_tputs.append(carrier_tput_slice.tolist())
        carrier_tputs.append(per_carrier_tputs)         

        start_time =   end_time+pd.Timedelta(seconds=5)
        end_time   =   start_time+pd.Timedelta(seconds=20)
    return [ca_lists, mac_tput_lists, carrier_tputs]


if __name__ == '__main__':
    data_dir    =  '/home/dinhp/data/wowmom_ext/ca/3_users_sharing/' 
    #send_rates = ['200', '225', '250', '275', '300']
    send_rates = ['10', '50', '100',
                '200', '225', '250', 
                '275', '300', '1500',
                '0M']
    run_nums = [1,2,3,4,5]


    #Plot CA

    fig, axs = plt.subplots(5,3, sharex=True)
    fig.set_size_inches(20, 10.5)

    for run_num in run_nums:
        idx =   run_num-1
        csv_file    =   data_dir+ 'phone_1/run'+str(run_num)+'.csv'
        [ca_lists,  mac_tput_lists, carrier_tputs] =   get_info(csv_file)
        carrier_tputs_dict = dict(zip(send_rates, carrier_tputs))
        carrier_tputs_df   =   pd.DataFrame(dict([ 
                    (k, pd.Series(v)) 
                    for k,v in carrier_tputs_dict.items() ]))
        carrier_tputs_df =  carrier_tputs_df.T
        carrier_tputs_df =   carrier_tputs_df.rename(columns={'index':'Send rates'})
        for c in carrier_tputs_df.columns:
            avgs_per_send_rate    =   []
            stds_per_send_rate   =   []
            for i in range(0,len(send_rates),1):
                avg =   np.mean(carrier_tputs_df[c][i])
                std =   np.std(carrier_tputs_df[c][i])
                avgs_per_send_rate.append(avg)
                stds_per_send_rate.append(std)
            carrier_tputs_df['Avg of Cell '+ str(c)] =   \
                    avgs_per_send_rate
            carrier_tputs_df['Std of Cell '+ str(c)] =   \
                    stds_per_send_rate
                
        axs[idx][0].bar(send_rates, carrier_tputs_df['Avg of Cell 0'],
                        label   =   'PCell')

        axs[idx][0].bar(send_rates, carrier_tputs_df['Avg of Cell 1'], 
                bottom =   carrier_tputs_df['Avg of Cell 0'],
                        label   =   'SC 1')

        axs[idx][0].bar(send_rates, carrier_tputs_df['Avg of Cell 2'], 
                bottom =    carrier_tputs_df['Avg of Cell 0']+
                            carrier_tputs_df['Avg of Cell 1'],
                        label   =   'SC 2')
        axs[idx][0].bar(send_rates, carrier_tputs_df['Avg of Cell 3'], 
                bottom =    carrier_tputs_df['Avg of Cell 0']+
                            carrier_tputs_df['Avg of Cell 1']+
                            carrier_tputs_df['Avg of Cell 2'],
                        label   =   'SC 3')
        axs[idx][0].bar(send_rates, carrier_tputs_df['Avg of Cell 4'], 
                bottom =    carrier_tputs_df['Avg of Cell 0']+
                            carrier_tputs_df['Avg of Cell 1']+
                            carrier_tputs_df['Avg of Cell 2']+
                            carrier_tputs_df['Avg of Cell 3'],
                        label   =   'SC 4')
        axs[idx][0].bar(send_rates, carrier_tputs_df['Avg of Cell 5'], 
                bottom =    carrier_tputs_df['Avg of Cell 0']+
                            carrier_tputs_df['Avg of Cell 1']+
                            carrier_tputs_df['Avg of Cell 2']+
                            carrier_tputs_df['Avg of Cell 3']+
                            carrier_tputs_df['Avg of Cell 4'],
                            label   =   'SC 5')
        axs[idx][0].legend(loc  =   'upper right', ncol=6, fontsize=8)


        csv_file    =   data_dir+ 'phone_3/run'+str(run_num)+'.csv'
        [ca_lists,  mac_tput_lists, carrier_tputs] =   get_info(csv_file)
        carrier_tputs_dict = dict(zip(send_rates, carrier_tputs))
        carrier_tputs_df   =   pd.DataFrame(dict([ 
                    (k, pd.Series(v)) 
                    for k,v in carrier_tputs_dict.items() ]))
        carrier_tputs_df =  carrier_tputs_df.T
        carrier_tputs_df =   carrier_tputs_df.rename(columns={'index':'Send rates'})
        for c in carrier_tputs_df.columns:
            avgs_per_send_rate    =   []
            stds_per_send_rate   =   []
            for i in range(0,len(send_rates),1):
                avg =   np.mean(carrier_tputs_df[c][i])
                std =   np.std(carrier_tputs_df[c][i])
                avgs_per_send_rate.append(avg)
                stds_per_send_rate.append(std)
            carrier_tputs_df['Avg of Cell '+ str(c)] =   \
                    avgs_per_send_rate
            carrier_tputs_df['Std of Cell '+ str(c)] =   \
                    stds_per_send_rate
                
        axs[idx][1].bar(send_rates, carrier_tputs_df['Avg of Cell 0'],
                        label   =   'PCell')

        axs[idx][1].bar(send_rates, carrier_tputs_df['Avg of Cell 1'], 
                bottom =   carrier_tputs_df['Avg of Cell 0'],
                        label   =   'SC 1')

        axs[idx][1].bar(send_rates, carrier_tputs_df['Avg of Cell 2'], 
                bottom =    carrier_tputs_df['Avg of Cell 0']+
                            carrier_tputs_df['Avg of Cell 1'],
                        label   =   'SC 2')
        axs[idx][1].bar(send_rates, carrier_tputs_df['Avg of Cell 3'], 
                bottom =    carrier_tputs_df['Avg of Cell 0']+
                            carrier_tputs_df['Avg of Cell 1']+
                            carrier_tputs_df['Avg of Cell 2'],
                        label   =   'SC 3')
        axs[idx][1].bar(send_rates, carrier_tputs_df['Avg of Cell 4'], 
                bottom =    carrier_tputs_df['Avg of Cell 0']+
                            carrier_tputs_df['Avg of Cell 1']+
                            carrier_tputs_df['Avg of Cell 2']+
                            carrier_tputs_df['Avg of Cell 3'],
                        label   =   'SC 4')
        axs[idx][1].bar(send_rates, carrier_tputs_df['Avg of Cell 5'], 
                bottom =    carrier_tputs_df['Avg of Cell 0']+
                            carrier_tputs_df['Avg of Cell 1']+
                            carrier_tputs_df['Avg of Cell 2']+
                            carrier_tputs_df['Avg of Cell 3']+
                            carrier_tputs_df['Avg of Cell 4'],
                            label   =   'SC 5')
        axs[idx][1].legend(loc  =   'upper right', ncol=6, fontsize=8)

        csv_file    =   data_dir+ 'phone_3/run'+str(run_num)+'.csv'
        [ca_lists,  mac_tput_lists, carrier_tputs] =   get_info(csv_file)
        carrier_tputs_dict = dict(zip(send_rates, carrier_tputs))
        carrier_tputs_df   =   pd.DataFrame(dict([ 
                    (k, pd.Series(v)) 
                    for k,v in carrier_tputs_dict.items() ]))
        carrier_tputs_df =  carrier_tputs_df.T
        carrier_tputs_df =   carrier_tputs_df.rename(columns={'index':'Send rates'})
        for c in carrier_tputs_df.columns:
            avgs_per_send_rate    =   []
            stds_per_send_rate   =   []
            for i in range(0,len(send_rates),1):
                avg =   np.mean(carrier_tputs_df[c][i])
                std =   np.std(carrier_tputs_df[c][i])
                avgs_per_send_rate.append(avg)
                stds_per_send_rate.append(std)
            carrier_tputs_df['Avg of Cell '+ str(c)] =   \
                    avgs_per_send_rate
            carrier_tputs_df['Std of Cell '+ str(c)] =   \
                    stds_per_send_rate
                
        axs[idx][2].bar(send_rates, carrier_tputs_df['Avg of Cell 0'],
                        label   =   'PCell')

        axs[idx][2].bar(send_rates, carrier_tputs_df['Avg of Cell 1'], 
                bottom =   carrier_tputs_df['Avg of Cell 0'],
                        label   =   'SC 1')

        axs[idx][2].bar(send_rates, carrier_tputs_df['Avg of Cell 2'], 
                bottom =    carrier_tputs_df['Avg of Cell 0']+
                            carrier_tputs_df['Avg of Cell 1'],
                        label   =   'SC 2')
        axs[idx][2].bar(send_rates, carrier_tputs_df['Avg of Cell 3'], 
                bottom =    carrier_tputs_df['Avg of Cell 0']+
                            carrier_tputs_df['Avg of Cell 1']+
                            carrier_tputs_df['Avg of Cell 2'],
                        label   =   'SC 3')
        axs[idx][2].bar(send_rates, carrier_tputs_df['Avg of Cell 4'], 
                bottom =    carrier_tputs_df['Avg of Cell 0']+
                            carrier_tputs_df['Avg of Cell 1']+
                            carrier_tputs_df['Avg of Cell 2']+
                            carrier_tputs_df['Avg of Cell 3'],
                        label   =   'SC 4')
        axs[idx][2].bar(send_rates, carrier_tputs_df['Avg of Cell 5'], 
                bottom =    carrier_tputs_df['Avg of Cell 0']+
                            carrier_tputs_df['Avg of Cell 1']+
                            carrier_tputs_df['Avg of Cell 2']+
                            carrier_tputs_df['Avg of Cell 3']+
                            carrier_tputs_df['Avg of Cell 4'],
                            label   =   'SC 5')
        axs[idx][2].legend(loc  =   'upper right', ncol=6, fontsize=8)
        fig.savefig("test.png")
