# Get beamspot location from images for BNQR
# Derek Fujimoto
# Aug 2021

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bccd import fits
import os
from datetime import datetime
from settings import *

def get_spot(fits, outfile=None, black=None, white=None, draw=True):
    
    path = fits.filename
    filename = os.path.basename(path)
    filename = os.path.splitext(filename)[0]
    f = fits
    
    # estimate dark count error
    error = get_noise(f)
    
    # set black and white levels
    if black is not None: 
        f.set_black(black*1e4)

    if white is not None: 
        f.set_white(white*1e4)

    # get fit output
    out = f.fit_gaussian2D(draw=draw, get_p0_from_center=True, pix_error=error)['result']
    
    # append filename and chi2 to output
    out = pd.concat((out, pd.Series({'filename': filename, 'chi2':f.chi2})))
    out = pd.DataFrame(out).transpose()
    out.set_index('filename', inplace=True)
    
    # title
    if draw:
        plt.title(filename, fontsize='x-small')
    
    # save to file
    if outfile is not None: 
        
        # get file extension
        outfile = os.path.splitext(outfile)[0] + '.csv'
        
        # try to read the output
        try:
            df = pd.read_csv(outfile, comment="#")
        except FileNotFoundError:
            df = pd.DataFrame(columns=['filename', 'x0', 'y0', 'sigmax', 'sigmay', 
                                       'amp', 'theta', 'chi2'])
        
        df.set_index('filename', inplace=True)
        df.loc[filename, :] = out.loc[filename, :]

        # write to file
        with open(outfile, 'w') as fid:
            
            header = [  "# Beamspot finding",
                        "# Fit with 2D gaussian using scipy.optimize.curve_fit",
                        "# File written: %s" % str(datetime.now()),
                        "# \n"]
            fid.write('\n'.join(header))
            
        df.to_csv(outfile, mode='a')
        
        return df
    return out
    
