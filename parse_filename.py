# Parse the filenames for tune name, implantation, recheck status
# Derek Fujimoto
# Aug 2021

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def parse_filename(filename):

    # initialize
    tune = ''
    bias = -1
    recheck = False

    # get basename
    filename = os.path.basename(filename)
    filename = os.path.splitext(filename)[0]

    # split by underscore
    filespl = filename.split('_')

    # get tune
    for i, f in enumerate(filespl):
        if 'T' == f[0]:
            tune = '_'.join(filespl[i:i+2])
            tune = tune[1:]
            break
    
    # get bias
    for f in filespl:
        if 'kV' in f:
            bias = float(f.replace('kV', '').replace('p', '.'))
            break
    recheck = 'recheck' in filename

    return (tune, bias, recheck)
    

    
