# settings for beamspot analysis files
# Derek Fujimoto
# Aug 2021

import os
import pandas as pd
import numpy as np

# images filenames
all_images_file = 'images.csv'

# where the images are stored
local_dir = os.path.join(os.environ['HOME'], '.bccd', 'bnmr@bnmrexp.triumf.ca', '2022-Jul')

spot_file = 'beamspots.csv'         # save beamspot parameters here
bs_fit_img_dir = 'beamspot_images'  # save beamspot fit images here
tex_dir = 'tex'                     # save tex files here

# image processing values
black = 3.8
white = None

# sample position (circle)
reference_image = "210815\_1415\_cryofixed"
x0 = 168.188
y0 = 267.080
r  = 8.536

ylo = y0-r
yhi = y0+r

xlo = lambda y : x0-(r**2-(y-y0)**2)**0.5
xhi = lambda y : x0+(r**2-(y-y0)**2)**0.5

# worker functions -----------------------------------------------------------
def get_paths():
    df = pd.read_csv(all_images_file, comment='#')
    files = df['filename'].apply(lambda x: os.path.join(local_dir, x.strip()+'.fits'))
    return files.values

def get_noise(fits):
    dark_area = fits.data[300:, :150]
    return np.std(dark_area)
