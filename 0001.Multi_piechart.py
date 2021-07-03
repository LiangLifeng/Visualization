
import sys,os,math
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from cycler import cycler

import argparse as ap

def ParsReceiver():
	p = ap.ArgumentParser(
	formatter_class=ap.RawDescriptionHelpFormatter,	
	description='''
-------------------
	draw multi pie \n

	Version:
		V1	2021-06-22
	Author:
		Liang Lifeng
------------------'''
)
	ars = p.add_argument
	ars('-p',dest="profile",action="store",help='profile file, first column is sample ID ',required=True)
	ars('-m',dest="mapping",action="store",help='mapping file, first column is sample ID  ',required=True)
	ars('-g',dest="group",action="store",help='draw group name list ,split by : eg G1:G2:G3,"All" mean draw all Group,[Default=All]',required=False,default='All')
	ars('-M',dest="Merge",action="store",help=' merge group by mean to draw or not [Y/N] [Default=Y]',required=False,default='Y')
	ars('-G',dest="GroupTitle",action="store",help=' [group colunm name to draw, Default= Group] ',required=False,default='Group')
	#ars('-k',dest="type",action="store",help='[1,2] :draw top species[1] (-t need) or specified species [2] (-l need), [Default=1]',required=False,default='1')
	ars('-t',dest="top",action="store",help='top species to draw,[Default=4] ',required=False,default='4')
	ars('-l',dest="specific",action="store",help='specific species name list ,split by : eg S1:S2:S3, "none" mean draw top 4 species [Default=none] ',required=False,default='none')
	ars('-q',dest="prefix",action="store",help='prefix [Default=All]',required=False,default='All')
	ars('-o',dest="outdir",action="store",help='outdir [Default=./]',required=False,default='./')
	return vars(p.parse_args())


def makedir(path):
	if not os.path.exists(path):
		os.makedirs(path)

def percentage(dframe,columns):
	tempDF = dframe
	for col in columns:  
		tempDF[col] = tempDF[col] / tempDF[col].sum() * 100
	return tempDF


def getProfile(profileF, mapF, groupN,groupL, mergerG, topN, specificL ):
	profileFile = pd.read_csv(profileF, sep="\t",index_col=0,low_memory=False)
	mapFile = pd.read_csv(mapF, sep="\t",index_col=0,low_memory=False)
	
	if groupL != "All":
		groupLlist = groupL.strip().split(":")
		plotMap = mapFile.loc[:,groupN]
	else:
		groupLlist =  set(mapFile[groupN].to_list())
		plotMap = mapFile[mapFile[groupN].isin(groupLlist)].loc[:,groupN]
		
	if specificL != 'none':
		speciesList = specificL.strip().split(":")
	else:

		speciesList = profileFile.sum().sort_values(ascending = False).index.to_list()[:int(topN)]
	
	if mergerG == 'Y':
		megerPF = pd.concat([profileFile,mapFile],axis =1)
		profileFile = megerPF.groupby([groupN]).mean()

	needprofileFile =  profileFile.loc[:,speciesList]
	otherList = list(set(profileFile.columns.to_list()).difference(set(speciesList)))
	otherprofileFile = profileFile.loc[:,otherList]
	otherSum = otherprofileFile.sum(axis = 1).to_frame()
	otherSum.columns = ['Other']
	plot = pd.concat([needprofileFile,otherSum],axis =1).T
	percPlot = percentage(plot,plot.columns.to_list())
	return(percPlot)

def drawPie(df,outPreFix):
	colors = list(mpl.cm.Dark2.colors[:len(df.index.to_list())-1])
	colors.append("#bababa")
	plt.style.use('ggplot')
	nrowP = math.ceil(len(df.columns.to_list())/10)
	ncolP = len(df.columns.to_list())
	print(df.index.to_list())
	width = 1.5 * ncolP + 1 + len(sorted(df.index.to_list(),key=len)[-1])*0.2
	hight = 1.6 * nrowP + 1 
	fig, axes = plt.subplots(nrows=nrowP, ncols= ncolP)
	for ax, col in zip(axes.flat, df.columns):
		artists = ax.pie(df[col], autopct='%.2f', radius = 0.8, pctdistance=0.8, colors=colors,textprops={'fontsize': 6}) #radius = r[i], autopct="%.1f%%", pctdistance=0.9
		ax.set(ylabel='', title=col, aspect='equal')

	fig.legend(artists[0], df.index, loc='right',frameon=False,facecolor="none",fontsize=6)
	plt.show()
	fig.set_size_inches(width,hight)
	fig.savefig(outPreFix+'.multi.pie.jpeg',dpi=600)
	fig.savefig(outPreFix+'.multi.pie.pdf')
	plt.close()


def main():
	if len(sys.argv) == 1:
		sys.argv.append('-h')
		ParsReceiver()
		sys.exit()
	global pars,outpath
	pars = ParsReceiver()
	makedir(pars['outdir'])
	plotData = getProfile(pars['profile'], pars['mapping'], pars['GroupTitle'], pars['group'], pars['Merge'], pars['top'], pars['specific'])
	drawPie(plotData, pars['outdir']+'/'+pars['prefix'])

if __name__ == '__main__':
	main()
