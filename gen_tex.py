# Generate latex file for viewing beamspot comparison
# Derek Fujimoto
# Aug 2021

import pandas as pd
from settings import *
import os, subprocess

# get beamspot filenames
df = pd.read_csv(spot_file, comment='#')

# get filenames for matching beamspots
df.set_index('bias_kV', inplace=True)

figure_strings = []

def add_graphic(s, fig_str, width):
    img_path = os.path.join('..', bs_fit_img_dir, s['filename']+'.png')
    fig_str.append(r'\includegraphics[keepaspectratio=true, width=%f\textwidth]{%s}' \
                    % (width, img_path))
    return fig_str
    
def add_caption(s, fig_str):
    tune = s['tune'].replace('_', '\\_')
    caption = 'tune %s, overlap: \SI{%.2g}' % (tune, s['overlap']*100)
    caption = caption + r'{\%}'
    fig_str.append(r'\caption{%s}' % caption)
    return fig_str
    
# get summary table
df2 = df.copy()
df2.reset_index(inplace=True)
summary_table = df2.to_latex(float_format='%.2f', 
                            columns=['bias_kV', 'filename', 'x0', 'y0', 'overlap'], 
                            position='H', caption='Beamspot positions and overlaps (all images)',
                            index=False,
                            label='summary_table')

# drop recheck
df2 = df.copy()
df2.reset_index(inplace=True)
for i in df2.index:
    if 'recheck' in df2.loc[i, 'filename']:
        df2.loc[i, 'overlap'] = np.nan
df2.dropna(inplace=True, axis='index')

df2.set_index('tune', inplace=True)
df_summary = []


for t in df2.index.unique():
    d = df2.loc[t, :]
    d.rename(columns={'overlap':t}, inplace=True)
    d.set_index('bias_kV', inplace=True)
    df_summary.append(pd.DataFrame(d[t]))
df_summary = pd.concat(df_summary, axis='columns')     

df_summary.reset_index(inplace=True)

compare_table = df_summary.to_latex(float_format='%.2f', 
                            position='H', 
                            index = False,
                            na_rep = '',
                            caption='Comparison of beamspot overlaps between tunes',
                            label='compare_table')
    
# get info
fig_str = []
for bias in sorted(df.index.unique()):
    d = df.loc[bias]
    
    if type(d) is pd.Series:
        d = pd.DataFrame(d).transpose()
        
    fig_str.extend([ r'\begin{figure}[ht]',
                     r'\centering',])

    # one image
    if len(d.index) == 1:
        
        s = d.iloc[0]
        
        # graphics
        fig_str = add_graphic(s, fig_str, 0.5)
        
        # caption
        tune = s['tune'].replace('_', '\\_')
        caption = r'\SI{%.2f}{\kV}, tune %s, overlap: \SI{%.2g}' % (s.name, tune, s['overlap']*100)
        caption = caption + r'{\%}'
        fig_str.append(r'\caption[%.2f kV]{%s}' % (s.name, caption))
    
        # label
        label = '%.2f_kV' % s.name
        label.replace('.', 'p')
        fig_str.append(r'\label{%s}' % label)
    
        
    # multi-image
    else:
        n_img = len(d.index)
        
        # figure width 
        w = 0.95/n_img
        
        for i in range(n_img):
        
            # add subfigure
            fig_str.extend([r'\begin{subfigure}[t]{%f\textwidth}' % w,
                            r'\centering'])
            
            # add graphic
            fig_str = add_graphic(d.iloc[i], fig_str, 1)
            
            # add caption
            fig_str = add_caption(d.iloc[i], fig_str)
            
            # close subfigure
            fig_str.extend([r'\end{subfigure}',
                            r'%'])
        # caption figure
        caption = '\SI{%.2f}{\kV}' % bias
        fig_str.append(r'\caption[%s]{%s}' % (caption, caption))
    
        # label figure
        label = '%.2f_kV' % bias
        label.replace('.', 'p')
        fig_str.append(r'\label{%s}' % label)
    
    # end figure
    fig_str.append(r'\end{figure}')    
    fig_str.append('')   
    
# write tex body
with open(os.path.join(tex_dir, 'body.tex'), 'w') as fid:
    
    fid.write(r"""Sample reference image:
    \begin{itemize}[noitemsep]
        \item %s
    \end{itemize}
    """ % reference_image)
    fid.write('\n')
    
    fid.write(r"""Target position and size:
    \begin{itemize}[noitemsep]
        \item $x_0 = %f$
        \item $y_0 = %f$
        \item $r = %f$
    \end{itemize}
    """ % (x0, y0, r))
    fid.write('\n')
    
    fid.write(r"""Image processing settings:
    \begin{itemize}[noitemsep]
        \item black = %s
        \item white = %s
    \end{itemize}
    """ % (str(black), str(white)))
    fid.write('\n')
    
    fid.write(r'\listoftables')
    fid.write('\n')
    fid.write(r'\listoffigures')
    fid.write('\n')
    
    fid.write(compare_table)
    fid.write('\n\n')
    
    fid.write(summary_table)
    fid.write('\n\n')
    
    body = '\n'.join(fig_str)
    fid.write(body)
    
# compile pdf
os.chdir(tex_dir)
subprocess.run(['pdflatex', 'beamspot.tex'])
subprocess.run(['pdflatex', 'beamspot.tex'])
subprocess.run(['mv', 'beamspot.pdf', '..'])
