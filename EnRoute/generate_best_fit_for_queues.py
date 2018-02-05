import pandas as pd
import matplotlib.pyplot as plt
import os
import scipy.stats as st
import multiprocessing
import itertools
from multiprocessing import freeze_support

distributions = [st.expon, st.norm,st.gamma,st.weibull_max,st.weibull_min,st.logistic,st.beta]

def get_best_fits(col, name, group):
    data  = group[col]
    mles = []

    for distribution in distributions:
        pars = distribution.fit(data)
        mle = distribution.nnlf(pars, data)
        mles.append(mle)

    temp = sorted(zip(distributions, mles), key=lambda d: d[1])
    return [name, temp[0][0].name, temp[1][0].name, temp[2][0].name, temp[3][0].name, temp[4][0].name]

def getbestfits1_star(n_g):
    return get_best_fits("lane_queueing_length",*n_g)

def getbestfits2_star(n_g):
    return get_best_fits("lane_queueing_time",*n_g)


if (__name__ == "__main__"):
    freeze_support()

    store = pd.HDFStore("london_dua60.h5")
    qdf = store["queue_df"]
    qdf["edge_id"] =qdf["lane_id"].str.replace("_[0-9]$","")
    qdf_no_na = qdf.dropna()

    lane_len_groups = qdf_no_na[["lane_id","lane_queueing_length"]].groupby("lane_id")
    lane_time_groups = qdf_no_na[["lane_id","lane_queueing_time"]].groupby("lane_id")
    edge_len_groups = qdf_no_na[["edge_id","lane_queueing_length"]].groupby("edge_id")
    edge_time_groups = qdf_no_na[["edge_id","lane_queueing_time"]].groupby("edge_id")

    #counter = multiprocessing.Value("i",0)
    pool_size = multiprocessing.cpu_count()/2

    pool = multiprocessing.Pool(pool_size)#,initializer=init,initargs=(counter,))

    best_fits_lane_length =  pool.map(getbestfits1_star, lane_len_groups)

    best_fits_lane_time = pool.map(getbestfits2_star, lane_time_groups)

    best_fits_edge_length =  pool.map(getbestfits1_star, edge_len_groups)

    best_fits_edge_time =  pool.map(getbestfits2_star, edge_time_groups)
    

    pd.DataFrame(best_fits_lane_length).to_csv("queue_lane_length_best_fit.csv",index=False)
    pd.DataFrame(best_fits_lane_time).to_csv("queue_lane_time_best_fit.csv",index=False)
    pd.DataFrame(best_fits_edge_length).to_csv("queue_edge_length_best_fit.csv",index=False)
    pd.DataFrame(best_fits_edge_time).to_csv("queue_edge_time_best_fit.csv",index=False)