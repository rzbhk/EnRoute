
# coding: utf-8

# In[1]:

import pandas as pd


# In[2]:

import sys


# In[3]:

def samplecameras(inp,n,out=False):
    df = pd.read_csv(inp)
    sdf = df.sample(n=n)    
    if out:
        sdf.to_csv(out)
    else:
        return sdf


# In[5]:




# In[6]:

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "samplecameras.py <input-file.csv> <number-of-cameras> <output-file.csv>"
        #sys.exit(2)
    else:
        samplecameras(sys.argv[1],int(sys.argv[2]),sys.argv[3])

