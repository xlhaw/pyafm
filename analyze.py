import os,pandas as pd,numpy as np,matplotlib.pyplot as plt
from pyspm import Bruker
from configs import *
from profiler import plot_all
plt.style.use('seaborn')

def read_afm(fpath):
    return Bruker(fpath).get_channel()
def smooth(data,k = 5):
    kernel = np.ones(k) / k
    return np.convolve(data, kernel, mode='same')
def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w
def find_min_loc(series):
    return np.argmin(series)
def find_max_loc(series):
    return np.argmax(series)
def get_mean_trend(series,axis=0,smoothed=False):
    series=series.mean(axis=axis)
    if smoothed:
        series=smooth(series)
    return series
def get_list(fpath,suffix='',join=True):
    lists=[]
    if os.path.isfile(fpath):
        with open(fpath) as f:
            while True:
                line=f.readline()
                if line=='':
                     break
                elif line[-1]=='\n':
                     lists.append(line[:-1])
                else:
                    lists.append(line)
    elif os.path.isdir(fpath):
        if suffix=='': #return folder list
            lists=next(os.walk(fpath))[1]
        else:
            lists=[i for i in os.listdir(fpath) if i.lower().endswith(suffix)]
        if join:
            return [f'{fpath}\\{item}' for item in lists]
    return lists

def get_profile(afm,smoothed=False,plot=True,fname=None):
    #global H,W,X_PPU,Y_PPU
    #H=afm.shape[0]
    #W=afm.shape[1]
    h_2,w_2=int(H/2),int(W/2)
    #Y_PPU=1500/H
    #X_PPU=3000/W    
    center=afm[h_2-32:h_2+32,:]
    right=afm[h_2-32:h_2+32,w_2:]
    bot=afm[-12:,:]
    top=afm[:12,:]
    
    # Get Mean Trends
    a_mean,c_mean,r_mean,t_mean,b_mean=[get_mean_trend(arr,axis=0,smoothed=smoothed) 
                                        for arr in [afm,center,right,top,bot]]
    ## Get S2A Location
    s2a_right=find_min_loc(r_mean)+w_2
    s2a_left=find_min_loc(a_mean[w_2:s2a_right-10])+w_2

    ## Get BG Location
    top_bg=w_2+find_min_loc(t_mean[w_2:])
    bot_bg=w_2+find_min_loc(b_mean[w_2:])
    if abs(top_bg-bot_bg)<8:
        bg=max(top_bg,bot_bg)
    else:
        bg=256+find_min_loc(t_mean[w_2:]+b_mean[w_2:])
        #raise Exception("")
        
    ##Get MR center
    bg_area=afm[:,bg-10:bg+10]
    bg_mean=bg_area.mean(axis=1)
    y_center=int((find_max_loc(smooth(bg_mean)[:40])+H-40+find_max_loc(smooth(bg_mean)[-40:]))/2)

    # Return Measurements
    sf=afm[:,bg+BG_OFFSET:bg+BG_OFFSET+int(BOX_2_W/X_PPU)]
    sf_mean=get_mean_trend(sf,axis=1,smoothed=smoothed)  
    Valley=sf_mean.min()
    Peak=sf_mean.max()
    P_V=Peak-Valley
    
    mr_b_box=afm[y_center-int(MR_B_BOX[1]/Y_PPU/2):y_center+int(MR_B_BOX[1]/Y_PPU/2),
             bg+BG_OFFSET:bg+BG_OFFSET+int(MR_B_BOX[0]/X_PPU)]  
    MR_M=mr_b_box.mean(axis=1).max()
    
    profile=get_mean_trend(afm[y_center-int(BOX_1_H/Y_PPU/2):y_center+int(BOX_1_H/Y_PPU/2),:],
                           axis=0,smoothed=smoothed)
    s2a_max=profile[s2a_left:s2a_right].max()
    s2b_mr_max=profile[s2a_right:s2a_right+int(MR_X_RNG/X_PPU)].max()

    output=pd.DataFrame({'MAX':[round(Peak,4)],'MIN':[round(Valley,4)],'P-V':[round(P_V,4)],
            'MidMR \nMax':[round(MR_M,4)],'S2A-S2B':[round(s2a_max,4)],'MR-S2B':[round(s2b_mr_max,4)]})
    output.index=['Unit [nm]']
    if plot:
        fig=plot_all(afm,profile,bg,y_center,s2a_right,s2a_left,w_2,sf_mean,output)
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.5)
        if fname:
            fig.savefig(f'{fname}.jpg',bbox_inches='tight')
            plt.close('all')
    return output
