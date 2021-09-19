import numpy as np,matplotlib.patches as mpatch,matplotlib.pyplot as plt
from configs import *

def plot_afm(array,ax):
    std=array.std()
    vmax,vmin=np.percentile(array,95)+std,np.percentile(array,5)-std
    ax.imshow(array,cmap='afmhot',aspect=2,vmax=vmax,vmin=vmin)
    #ax=plt.gca()
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,pos:'{0:.1f}'.format(x*X_PPU/1000)))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,pos:'{0:.1f}'.format(x*Y_PPU/1000)))
    ax.set_xlabel('x [um]',fontsize=14)
    ax.set_ylabel('y [um]',fontsize=14)
def drawbox(xy,w,h,ax,color='r'):
    rect = mpatch.Rectangle(xy, w,h,linewidth=1, edgecolor=color, facecolor='none') #xy top right corner
    ax.add_patch(rect)
def plot_all(afm,profile,bg,y_center,s2a_right,s2a_left,w_2,sf_mean,output):
    fig=plt.figure(figsize=(12,5.9))
    gs=fig.add_gridspec(4,2,width_ratios=[4,6],height_ratios=[1,2,2,1])
    img_ax=plt.subplot(gs[:-2,0])
    profile_ax=plt.subplot(gs[0:2,1])
    plot_afm(afm,img_ax)
    drawbox((bg+BG_OFFSET,0),500/X_PPU,127,img_ax,color='k') # sf_box
    drawbox((0,y_center-int(BOX_1_H/Y_PPU/2)),W-BG_OFFSET,BOX_1_H/Y_PPU,img_ax,color='r') #profile_box
    drawbox((s2a_left,0),s2a_right-s2a_left,127,img_ax,color='k') #s2a_box
    #drawbox((bg+BG_OFFSET,y_center-int(MR_B_BOX[1]/Y_PPU/2)),500/X_PPU,MR_B_BOX[1]/Y_PPU,img_ax,color='k') #mr_b_box
    drawbox((s2a_left,0),s2a_right-s2a_left,127,img_ax,color='k') 
    
    img_ax.grid(False)
    profile_ax.plot(profile,color='r')
    profile_ax.set_ylabel('Z [nm]')
    profile_ax.set_xlabel('x [um]')
    profile_ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,pos:'{0:.1f}'.format(x*X_PPU/1000)))
    ylim=profile_ax.get_ylim()
    #profile_ax.vlines([bg,bg+int(500/X_PPU),],ymin=ylim[0],ymax=ylim[1],color='r',ls=':')
    profile_ax.vlines([s2a_right,s2a_left,s2a_right+MR_X_RNG/X_PPU],ymin=ylim[0],ymax=ylim[1],color='k',ls=':')
    profile_ax.set_ylim(ylim)
    profile_ax.set_xlim(0,511)
    profile_ax.set_xticks(np.linspace(0,W,6))
    
    sf_ax=plt.subplot(gs[-2:,1])
    sf_ax.plot(sf_mean,color='k')
    sf_ax.set_ylabel('Z [nm]')
    sf_ax.set_xlabel('y [um]')
    sf_ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,pos:'{0:.1f}'.format(x*Y_PPU/1000)))
    ylim=sf_ax.get_ylim()
    sf_ax.vlines([y_center-int(MR_B_BOX[1]/Y_PPU/2),y_center+int(MR_B_BOX[1]/Y_PPU/2)],
                 ymin=ylim[0],ymax=ylim[1],color='k',ls=':')
    sf_ax.set_ylim(ylim)
    sf_ax.set_xlim(0,127)
    sf_ax.set_xticks(np.linspace(0,H,6))
    
    sum_ax=plt.subplot(gs[3,0])
    table=sum_ax.table(cellText=output.values,
          rowLabels=output.index,
          colLabels=output.columns,
          #colWidths=[0.03*len(x) for x in output.columns],
          cellLoc = 'center', rowLoc = 'center',
          loc='top')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1,1.8)
    sum_ax.axis('tight')
    sum_ax.axis('off')
    return fig
