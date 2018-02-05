import pandas as pd
import scipy.stats as st
from multiprocessing import freeze_support
import sys
import multiprocessing

counter = None

def init(args):
	global counter
	counter = args

distributions = [st.expon, st.norm,st.gamma,st.weibull_max,st.weibull_min,st.logistic,st.beta]
def get_best_fits(name, group):
    global counter
    with counter.get_lock():
        counter.value += 1
    data = group["entered_or_departed"]

    mles = []
    for distribution in distributions:
        pars = distribution.fit(data)
        mle = distribution.nnlf(pars, data)
        mles.append(mle)

    with counter.get_lock():
        if (counter.value % 200 == 0):
            print counter.value

    temp = sorted(zip(distributions, mles), key=lambda d: d[1])
    return [name ,temp[0][0].name, temp[0][1], temp[1][0].name,temp[1][1], temp[2][0].name,temp[2][1],
                  temp[3][0].name, temp[4][1], temp[4][0].name,temp[5][1]]

def getbestfits_star(n_g):
	return get_best_fits(*n_g)

if (__name__ == "__main__"):
    freeze_support()
    if (len(sys.argv) != 2):
        print("No input file specified")
        sys.exit(1)

    print "starting"
    df = pd.read_csv(sys.argv[1], header=None, names=["edge_id", "entered_or_departed"])

    grouped = df.groupby("edge_id").filter(lambda x: len(x) > 20).groupby("edge_id")
    print "total number of groups:", len(grouped)

    counter = multiprocessing.Value("i", 0)
    pool = multiprocessing.Pool(processes=64, initializer=init, initargs=(counter,))
    results = pool.map(getbestfits_star, grouped)
    # results = Parallel(n_jobs=num_cores)(delayed(getbestfits)(n,g) for n,g in lane_groups)
    outdf = pd.DataFrame(results,
                         columns=["edge_id", "first_dist","first_mle","second_dist","second_mle",
                                  "third_dist", "third_mle", "fourth_dist", "fourth_mle", "fifth_dist", "fifth_mle"])
    outdf.to_csv("best_fit_results_" + sys.argv[1] + ".csv")