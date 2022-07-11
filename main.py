# Control beamspot image overlay 
# Derek Fujimoto
# Aug 2021

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bccd import fits
import os
from datetime import datetime
from matplotlib.patches import Circle
from tqdm import tqdm
from bccd.backend.functions import gaussian2D

# local imports
from check_exposure import check_exposure 
from get_spot import get_spot 
from parse_filename import parse_filename
from settings import *

# switches
do_all              = True
do_check_exposures  = False
do_get_spots        = False
do_get_overlap      = True
do_gen_tex          = True

# make directory structure
os.makedirs('beamspot_images', exists_ok=True)

# check exposures -------------------------------------------------------------
if do_check_exposures or do_all:
    is_one_exposure, exposures = check_exposure()
    
    if not is_one_exposure:
        raise RuntimeError('WARNING: Not all exposure times consistent (%s)' % str(exposures))
    else:
        print('Exposure times are consistent (%s s)' % str(exposures[0]))

# get beamspots and overlap ---------------------------------------------------
if do_get_spots or do_all:
    
    files = get_paths()
    all_spots = []
    
    # get spots
    print('Fitting beamspots and calculating overlap')
    for f in tqdm(files):
                
        fit = fits(f)
        
        # get spot
        df = get_spot(fit, black=black, white=white, draw=True)
        
        # get overlap
        df['overlap'] = fit.get_gaussian2D_overlap(ylo, yhi, xlo, xhi)
        
        # get tune and kV
        df['tune'], df['bias_kV'], _ = parse_filename(f)
        
        # save result
        all_spots.append(df)
        
        # draw sample position
        circle_smpl = Circle((x0, y0), r, facecolor='none', linewidth=4, edgecolor='w')
        fit.plt.gca().add_patch(circle_smpl)
        
        # resize image
        fit.plt.xlim([x0-4*r, x0+4*r])
        fit.plt.ylim([y0-4*r, y0+4*r])
        
        # save image
        img_name = os.path.splitext(f)[0]
        img_name = os.path.basename(img_name)
        img_name = img_name + '.png'
        plt.savefig(os.path.join(bs_fit_img_dir, img_name))
        
        # show image
        plt.pause(0.05)
        fit.plt.cla()
            
    # ~ plt.close('all')
            
    # write results to file
    with open(spot_file, 'w') as fid:
        
        header = [  "# Beamspot finding",
                    "# Fit with 2D gaussian using scipy.optimize.curve_fit",
                    "# Reference image: %s" % reference_image,
                    "# Overlap integrated with",
                    "#     x0 = %f" % x0,
                    "#     y0 = %f" % y0,
                    "#     r  = %f" % r,
                    "# File written %s" % str(datetime.now()),
                    "# \n"]
        fid.write('\n'.join(header))
    
    all_spots = pd.concat(all_spots)
    all_spots.to_csv(spot_file, mode='a')
                
# get overlap ----------------------------------------------------------------
if do_get_overlap and not do_all:
    
    files = get_paths()
    
    # get spot results
    df = pd.read_csv(spot_file, comment='#')
    df.set_index('filename', inplace=True)    
    
    # get spots
    print('Re-calculating overlap')
    for f in tqdm(files):
                
        fit = fits(f)
        
        filename = os.path.basename(f)
        filename = os.path.splitext(filename)[0]
        
        s = df.loc[filename]
        
        par = s[['x0', 'y0', 'sigmax', 'sigmay', 'amp', 'theta']].values
        
        # get overlap
        df.loc[filename, 'overlap'] = fit.get_gaussian2D_overlap(ylo, yhi, xlo, xhi, par)
        
        # draw the image
        if black is not None:   b = black * 1e4
        else:                   b = black
        if white is not None:   w = white * 1e4
        else:                   w = white
        
        fit.draw(black=b, white=w)
        contours = fit.draw_2Dfit(gaussian2D, *par[:4], 1, 0)
        fit.plt.gca().clabel(contours, inline=True, fontsize='x-small', fmt='%g')
        
        # draw sample position
        circle_smpl = Circle((x0, y0), r, facecolor='none', linewidth=4, edgecolor='w')
        fit.plt.gca().add_patch(circle_smpl)
        
        # title
        plt.title(filename, fontsize='x-small')
        
        # resize image
        fit.plt.xlim([x0-4*r, x0+4*r])
        fit.plt.ylim([y0-4*r, y0+4*r])
        
        # save image
        img_name = os.path.splitext(f)[0]
        img_name = os.path.basename(img_name)
        img_name = img_name + '.png'
        plt.savefig(os.path.join(bs_fit_img_dir, img_name))
        
        # show image
        plt.pause(0.01)
        fit.plt.cla()
            
    # ~ plt.close('all')
            
    # write results to file
    with open(spot_file, 'w') as fid:
        
        header = [  "# Beamspot finding",
                    "# Fit with 2D gaussian using scipy.optimize.curve_fit",
                    "# Reference image: %s" % reference_image,
                    "# Overlap integrated with",
                    "#     x0 = %f" % x0,
                    "#     y0 = %f" % y0,
                    "#     r  = %f" % r,
                    "# File written %s" % str(datetime.now()),
                    "# \n"]
        fid.write('\n'.join(header))
    
    df.to_csv(spot_file, mode='a')
  
# generate pdf --------------------------------------------------------------
if do_gen_tex or do_all:
    import gen_tex    
