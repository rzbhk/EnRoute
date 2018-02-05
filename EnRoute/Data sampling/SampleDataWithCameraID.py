
# coding: utf-8

# In[2]:

import pandas as pd


# In[3]:

import sys


# In[3]:

def samplecameras(inp,inp_data,out=False):
    df = pd.read_csv(inp)
    ddf = pd.read_csv(inp_data)
    mdf = df.merge(ddf,how="inner",on=["CAMERA_ID","CAMERA_NAME"])
    if out:
        mdf[ddf.columns].to_csv(out)
    else:
        return mdf[ddf.columns]


# In[6]:

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "sampledatawithcameraid.py <camera-input-file.csv> <data-input-file> <data-output-file.csv>"
        #sys.exit(2)
    else:
        samplecameras(sys.argv[1],sys.argv[2],sys.argv[3])

