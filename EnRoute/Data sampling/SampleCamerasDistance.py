
# coding: utf-8

# In[2]:

import pandas as pd


# In[3]:

import sys
from itertools import product


# In[3]:

def samplecameras(inp,dist,out=False):
    df = pd.read_csv(inp)
    camset = set(df.CAMERA_ID)
    all_pairs_list = list(product(camset,camset))
    all_pairs_df = pd.DataFrame(all_pairs_list,columns=["CAMERA_ID_FROM","CAMERA_ID_TO"])
    #df["fake_key"] = 1
    #cdf = df[["CAMERA_ID","fake_key"]].merge(df[["CAMERA_ID","fake_key"]],on="fake_key",suffixes=["_FROM","_TO"]) # cross product => every possible from_to camera_id
    ddf = pd.read_csv(dist)
    ddf.drop(["KML","TIME1"],axis=1,inplace=True)
    ddf_withnulls = ddf.merge(all_pairs_df,how="right") #on camera_id_from camera_id_to
    ddf_withnulls.ix[ddf_withnulls.CAMERA_ID_FROM == ddf_withnulls.CAMERA_ID_TO,["DISTANCE","TIME"]] = (0,0) #set self distances to 0
    ddf_withnulls.fillna({"DISTANCE":100000000,"TIME":100000},inplace=True) #set missing values to infinity!
    if out:
        ddf_withnulls.to_csv(out,index=False)
    else:
        return ddf_withnulls


# In[6]:

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print ("samplecameras.py <camera-input-file.csv> <camera-dist-input-file.csv> <camera-dist-output-file.csv>")
        #sys.exit(2)
    else:
        samplecameras(sys.argv[1],sys.argv[2],sys.argv[3])

