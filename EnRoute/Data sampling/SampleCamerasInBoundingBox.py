
# coding: utf-8

# In[1]:

import pandas as pd


# In[2]:

import sys


# In[3]:

def samplecameras(inp,left,bot,right,top,out=False):
    df = pd.read_csv(inp)
    sdf = df[(df.GEO_LAT <= right) & (df.GEO_LAT >= left) & (df.GEO_LON >= bot) & (df.GEO_LON <= top)]  
    if out:
        sdf.to_csv(out,index=False)
    else:
        return sdf


# In[5]:




# In[6]:

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print ("samplecameras.py <input-file.csv> bbox_bottom bbox_left bbox_top bbox_right <output-file.csv>")
        #sys.exit(2)
    else:
        samplecameras(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]),sys.argv[6])

