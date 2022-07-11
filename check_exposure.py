# Verify that the exposure times the list of files is the same
# Derek Fujimoto
# Aug 2021

import pandas as pd
import numpy as np
from bccd import fits
import os
from datetime import datetime
from settings import *

def check_exposure():
    """
        csvfile: file with all the image filenames
    """
    
    # get file names
    files = get_paths()
    
    # get exposures
    exposure = [fits(f).header['EXPOSURE'] for f in files]
    
    exp_unique = np.unique(exposure)

    is_one_exposure = len(exp_unique) == 1
    
    return (is_one_exposure, exp_unique)
