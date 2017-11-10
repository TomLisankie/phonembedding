import numpy as np
import scipy.stats as st
from random import seed

from data import readdata
from svd import getsvd
from w2v import getw2v
from correlation import getsimmatrix, correlation
from features import getphonfeatures
from rnn import initmodel,encode,decode,update, train

seed(42)
np.random.seed(43)

# To test 
N = 20
P = 0.99

def confidenceival(a):
    return st.t.interval(P, len(a)-1, loc=np.mean(a), scale=st.sem(a))

def truncate(m,d):
    return m[0:m.shape[0],0:d]

def matshuf(m):
    res = np.array(m)
    np.random.shuffle(res)
    return res

def getsvdembs(data,cencoder,embchars,cdecoder):
    svdembedding = getsvd(data,cencoder)
    svdembeddings = [truncate(svdembedding,n) for n in [5,15,30]]
    return svdembeddings

def getw2vembs(data,cencoder,embchars,cdecoder):
    return [getw2v(data,embchars,5,cdecoder),
            getw2v(data,embchars,15,cdecoder),
            getw2v(data,embchars,30,cdecoder)]

def checkr(ival,r):
    if ival[0] < r and ival[1] < r:
        return "<"
    else:
        return ">"

def correlation_experiment(file,lan,embf,name):
    data, cencoder, tencoder, embchars = readdata(file,lan)
    cdecoder = {v:k for k,v in cencoder.items()}
    features = getphonfeatures()
    lanfeatures = [np.array(features[cdecoder[f]]) 
                   if cdecoder[f] in features 
                   else None for f in range(len(cencoder))]

    featsim = getsimmatrix(lanfeatures,len(cencoder), embchars)

    embeddings = embf(data,cencoder,embchars,cdecoder)

    sims = [getsimmatrix(m,len(cencoder), embchars) for m in embeddings]
    rs = [correlation(featsim,sims[i])[0] for i in [0,1,2]]
    print("%s %s:" % (lan,name))
    print(" PEARSON R FOR EMBEDDING AND FEATURE REPR. SIMILARITIES:")
    print("  %s,DIM=5" % lan,rs[0])
    print("  %s,DIM=15" % lan,rs[1])
    print("  %s,DIM=30" % lan,rs[2])

    randrs = [[], [], []]
    for i in range(N):
        ranembeddings = [matshuf(m) for m in embeddings]
        ransims = [getsimmatrix(m,len(cencoder), embchars) for m in ranembeddings]
        randrs[0].append(correlation(featsim,ransims[0])[0])
        randrs[1].append(correlation(featsim,ransims[1])[0])
        randrs[2].append(correlation(featsim,ransims[2])[0])

    print((" P=%.2f CONF. INTERVALS FOR PEARSON R OF RANDOM ASSIGNMENT OF\n" % P) +
          " EMBEDDINGS TO PHONEMES AND PHONETIC FEATURE DESCRIPTIONS:")
    civals = [confidenceival(randrs[i]) for i in [0,1,2]]
    print("  %s,DIM=5" % lan, confidenceival(randrs[0]),checkr(civals[0],rs[0]),rs[0])
    print("  %s,DIM=15" % lan, confidenceival(randrs[1]),checkr(civals[1],rs[1]),rs[1])
    print("  %s,DIM=30" % lan, confidenceival(randrs[2]),checkr(civals[2],rs[2]),rs[2])
    print()


if __name__=="__main__":
    print("1. CORRELATION EXPERIMENTS")
    print("--------------------------")
    print()
#    correlation_experiment("../data/finnish","FI",getsvdembs,"SVD")
#    correlation_experiment("../data/turkish","TUR",getsvdembs,"SVD")
#    correlation_experiment("../data/spanish","ES",getsvdembs,"SVD")

#    correlation_experiment("../data/finnish","FI",getw2vembs,"W2V")
#    correlation_experiment("../data/turkish","TUR",getw2vembs,"W2V")
#    correlation_experiment("../data/spanish","ES",getw2vembs,"W2V")

#    correlation_experiment("../data/finnish","FI",getrnnembs,"RNN")
#    correlation_experiment("../data/turkish","TUR",getrnnembs,"RNN")
#    correlation_experiment("../data/spanish","ES",getrnnembs,"RNN")

    data, cencoder, tencoder, embchars = readdata('../data/finnish',"FI")
    modeld = initmodel(cencoder,tencoder,15)
    encoded = encode(data[0][1],data[0][2],modeld)
    train(data,modeld)
#    for i in range(100):
#        print(update(data[0][1],data[0][2],data[0][0],modeld))

