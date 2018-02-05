# coding: utf-8
import pandas as pd
import numpy as np
from enroute_utilities.graph import *
from enroute_utilities.matrix import *
from enroute_utilities.sumo import *
from enroute_utilities.xml import *
from os.path import join as path_join, normpath as norm_path, isfile as is_file
import networkx as nx
#from matplotlib import pyplot as plt
import pickle
from scipy.stats import lognorm
from math import exp
from scipy.optimize import nnls
from numpy import linalg
from lxml import etree
#from timeit import default_timer as timer
import sys

sys.path.append(r"C:\Program Files (x86)\DLR\Sumo\tools")

"""
PARAMETERS SECTION
"""
no_of_cameras = 90 # WILL BE OVERWRITTEN BY len(camerasdf)
K = [3] #number of shortest paths ot use
mu = [7.0] #np.arange(6,7,0.1)
sigma = [0.5] #[0.6,1,1.4,1.8,2.2,2.6,3]
b_min = 1
b_max = 1.1
b_step = 0.5
"""
END OF PARAMETERS SECTION
"""

"""
INPUT FILES SECTION
"""
csv_extension = ".csv"
txt_extension = ".txt"

origin_path = norm_path(r'C:\Users\Roozbeh\Sumo\WDC_FewerEdgesMap\All cameras in data 106') #path were sampled data are

camera_input_file_path = norm_path(path_join(origin_path,"cameras_3_08_09"+csv_extension))
camera_dist_file_path = norm_path(path_join(origin_path,"camdist_3_08_09"+csv_extension))
flows_data_file_path = norm_path(path_join(origin_path,"data_1h_sum_avg_20101121_08_09_rand"+csv_extension))
od_generation_log_file_path = norm_path(path_join(origin_path,"od_generation_log.txt"))

kshortest_paths_dump_path = norm_path(path_join(origin_path,str(no_of_cameras)+"_cameras_"+str(K)+"_shortest_paths.dump"))
A_matrix_dump_addr = norm_path(path_join(origin_path,str(no_of_cameras)+"_cameras_A_matrix"))
net_file_path = norm_path(path_join(origin_path,"../wdc.net.xml"))
camera_with_closest_edge_file_path = norm_path(path_join(origin_path,"cameras_3_8_9_with_closest_edge"+csv_extension))
"""
END of INPUT FILES SECTION
"""

def get_closest_edge_dataframe(camera_with_closest_edge_file_path,net_file_path):
    if is_file(camera_with_closest_edge_file_path):
        print "Camera file with closest edge already exists! Loading!"
        #camerasdf = pd.read_csv(camera_with_closest_edge_file_path)[["CAMERA_ID","EASTING","NORTHING","GEO_LAT","GEO_LON","CLOSEST_EDGE_1","CLOSEST_EDGE_2","CLOSEST_EDGE_3"]]
        camerasdf = pd.read_csv(camera_with_closest_edge_file_path)[
            ["CAMERA_ID", "GEO_LAT", "GEO_LON", "CLOSEST_EDGE_1", "CLOSEST_EDGE_2", "CLOSEST_EDGE_3"]
        ]
    else:
        print "Camera file with closest edge not found! Generate and Writing the file! This might take a while"
        #camerasdf = pd.read_csv(camera_input_file_path)[["CAMERA_ID", "EASTING", "NORTHING", "GEO_LAT", "GEO_LON"]]
        camerasdf = pd.read_csv(camera_input_file_path)[["CAMERA_ID", "GEO_LAT", "GEO_LON"]]
        net_file,closest_edges = get_closest_edges(net_file_path,camerasdf) #if we have the net object we can pass it on as third param so it doesn't load again
        camerasdf["CLOSEST_EDGE_1"], camerasdf["CLOSEST_EDGE_2"], camerasdf["CLOSEST_EDGE_3"] = zip(*closest_edges)
        camerasdf.to_csv(camera_with_closest_edge_file_path,index=False)
    return camerasdf

def get_k_shortest_paths(kshortest_paths_dump_path,no_of_cameras,_k,G):
    if (is_file(kshortest_paths_dump_path)):
        print str(_k) + " Shortest path dump already exists. Loading!"
        a = pickle.load(open(kshortest_paths_dump_path, "r"))
    else:
        print str(_k) + " Shortest path dump not existed. Generate and dumping to file! It might take a while!"
        a = k_shortest_paths(no_of_cameras, _k, G)
        pickle.dump(a, open(kshortest_paths_dump_path, "w"))
    return a

if __name__ == '__main__':

    camerasdf = get_closest_edge_dataframe(camera_with_closest_edge_file_path, net_file_path)

    #number of cameras updated according to camerasdf length
    no_of_cameras = len(camerasdf)

    distdf = pd.read_csv(camera_dist_file_path)[["CAMERA_ID_FROM", "CAMERA_ID_TO", "TIME", "DISTANCE"]]
    if distdf["TIME"].dtype == str:
        distdf["TIME"] = distdf["TIME"].str.replace("[^0-9]+", "").astype(np.int)

    matrix = get_distance_matrix(distdf,camerasdf)

    G = nx.from_numpy_matrix(matrix)

    flowsdf = pd.read_csv(flows_data_file_path)
    flowsdf.columns= ["Detector","Flow"]
    #flowsdf.columns = ["Detector","Flow","Speed"]
    #flowsdf = flowsdf[["Detector","Flow"]]

    taz_root = get_taz_xml_root(camerasdf) #camerasdf should have closest edge

    taz_file_path = norm_path(path_join(origin_path,"wdc.taz.xml"))

    with open(taz_file_path, 'w') as f:
        f.write(etree.tostring(taz_root,pretty_print=True))

    for _u in mu:
        for _sig in sigma:
            lnpdf = lambda x: lognorm.pdf(x, s=_sig, loc= 0, scale=exp(_u))
            #b = np.array(get_b_vector_lognorm(flowsdf, distdf, lnpdf, 30)) # we use lognormal results, 30 for 30 minutes
            b=np.array(get_b_vector_lognorm(flowsdf,distdf,lnpdf))

            for _k in K:
                parameter_config_str = str(no_of_cameras) + "cameras_u" + str(_u) + \
                                       "_std" + str(_sig) + "_" + str(_k) + "sp";
                kshortest_paths_dump_path = norm_path( path_join(origin_path,str(no_of_cameras)+"_cameras_"+
                                                                 str(_k)+"_shortest_paths.dump") )

                a = get_k_shortest_paths(kshortest_paths_dump_path,no_of_cameras,_k,G)

                A_matrix = get_A_matrix(a, lnpdf, no_of_cameras)

                #np.savetxt(A_matrix_dump_addr+txt_extension,A_matrix,fmt="%3.8f")
                #np.save(A_matrix_dump_addr,A_matrix)

                for idx,_b in enumerate([i*b for i in np.arange(b_min,b_max,b_step)]):
                    x,rnorm = nnls(A_matrix,_b)
                    current_b = b_step*idx+b_min
                    #x,residuals,rank,singulars = linalg.lstsq(A_matrix,b)
                    #print no_of_cameras,_u,_sig,_k,current_b, sum(x),rnorm
                    with open(od_generation_log_file_path,"a") as f:
                        f.write( parameter_config_str + "_" + str(current_b) + "bmult\t" + str(sum(x)) + "\t" + str(rnorm) + "\n")
                    #x_vector_dump_addr = norm_path(path_join(origin_path,str(no_of_cameras)+"_cameras_A_matrix"))
                    np.savetxt(norm_path(path_join(origin_path,"x_vector_"+parameter_config_str+"_"+str(current_b)+csv_extension)),x)

                    #np.save(x_vector_dump_addr,x)

                    od_file_path = norm_path(path_join(origin_path, parameter_config_str + str(current_b) + "_8_9_rand_bmult.od.txt"))

                    with open(od_file_path, "w") as f:
                        lines = get_formatted_OD(x,camerasdf,no_of_cameras)
                        for line in lines:
                            f.write(line+"\n")

"""
Use OD2Trips and them DUAROUTER (or other routing)

C:\Users\Roozbeh\Sumo\London\overlay>od2trips -n london.taz.xml -d london.od.txt -o london.trip.xml

C:\Users\Roozbeh\Sumo\London\overlay>duarouter -n ../../london.net.xml -t london.trip.xml -o london.rou.xml --routing-threads 4
"""