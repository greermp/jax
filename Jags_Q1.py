#!/usr/bin/python3
# coding: utf-8

#Import packages
import pandas as pd
import numpy as np
import colored
import math
import datetime as dt
from datetime import date
import re
import time

start = time.time()

def findDistance (x1, y1, x2, y2):
    return math.sqrt(((x2-x1)**2 + (y2-y1)**2))

def findSpeed (d, t1, t2):
    diff = t2-t1
    frac=diff.microseconds/1000000
    if frac==0:
        return 0
    return (d/frac)
week1 = pd.read_csv('week1.csv')


#Make small version
week1 = week1.loc[(week1['nflId'] == 310) | (week1['nflId'] == 2495454)]
#Remake playerIDs (test only)
playerIds = pd.unique(week1['nflId'])


def summarize_dataframe(df):
    """Summarize a dataframe, and report missing values."""
    missing_values = pd.DataFrame({'Variable Name': df.columns,
                                   'Data Type': df.dtypes,
                                   'Missing Values': df.isnull().sum(),
                                   'Unique Values': [df[name].nunique() for name in df.columns]}
                                 ).set_index('Variable Name')
    with pd.option_context("display.max_rows", 1000):
        display(pd.concat([missing_values, df.describe(include='all').transpose()], axis=1).fillna(""))

week1['d_calc']=0
week1['d_calc_postsnap']=0
week1['s_calc']=0

#Controls what debug prints you see
# 0 - minimal, 1- lots, 2 =  a sshit  ton
verbose=3

week1['time1'] = pd.to_datetime(week1.time).dt.tz_localize(None)

for player in playerIds :
    if(verbose>=0): print(colored.fg("red") + "Analyzing player {}".format(player))
    # analyzePlayer = week1['nflId']==player
    # currentDF = 
    #print(colored.fg("white"))
    frameCounter=0
    total=0
    speed=0
 
    playerDF = week1.loc[week1['nflId'] == player]
    # print(playerDF)
    plays=pd.unique(playerDF['playId'])
    distTravelled=0
    psDistTravelled=0
    # Go through each play for a given player
    print(colored.fg("green"))
    for play in plays :
        if(verbose>1): print( (colored.fg("green")+ "analyzing play: {}".format(play), end='...')
        # print('\rbar', end='', flush=True)
        #Create a DF for each play
        playdf = playerDF[playerDF['playId']==play]
        #Figure out how many frames in current play
        maxFrame = playdf['frameId'].max()
        
        frame=1
        
        disHolder=0
        speedHolder=0
        ps_holder=0
        ballSnapped= False
        # Go through each timestep in a given play
        while frame+1 <= maxFrame :
            frameCounter+=1
            if(verbose>1):print("frame: {}".format(frame), end=' ')
            # Grab x and y values for current and next frame
            x1 = playdf.loc[playdf['frameId'] == frame, 'x'].iloc[0]
            y1 = playdf.loc[playdf['frameId'] == frame, 'y'].iloc[0]
            x2 = playdf.loc[playdf['frameId'] == frame+1, 'x'].iloc[0]
            y2 = playdf.loc[playdf['frameId'] == frame+1, 'y'].iloc[0]
            #find distance
            dis = findDistance (x1, y1, x2, y2)
            
                     
            week1.loc[(week1['nflId'] == player) & (week1['playId'] == play) & 
                (week1['frameId'] == frame), 'd_calc'] = dis
            # week1.loc[(m1) & (m2) & (m3), 'd_calc'] = dis
            
            
            d = playdf.loc[playdf['frameId'] == frame, 'd_calc'].iloc[0]
            t1 = playdf.loc[playdf['frameId'] == frame, 'time1'].iloc[0]
            t2 = playdf.loc[playdf['frameId'] == frame+1, 'time1'].iloc[0]
            speed = findSpeed(d, t1, t2)
            week1.loc[(week1['nflId'] == player) & (week1['playId'] == play) & 
                (week1['frameId'] == frame), 's_calc'] = speed
            
            frame+=1
            speedHolder += speed
            total+= speed

            # Have we snapped the ball yet in this play?
            if ( not ballSnapped) :
                # if not, get the 'event' of th current frame
                m1 = week1['nflId'] == player
                m2 = week1['playId'] == play
                m3 = week1['frameId'] == frame
                snp=week1[m1&m2&m3]['event'].values[0]
                print(snp)
                #if the event is a snap, set ballSnapped to true
                if  (snp=='ball_snap') :
                    if(verbose>1):print(colored.fg("red") + "On frame {}, BALL SNAPPD".format(frame),end=' ')
                    ballSnapped= True
            
            disHolder += dis
            if ballSnapped :
                ps_holder += dis
                week1.loc[(week1['nflId'] == player) & (week1['playId'] == play) & 
                (week1['frameId'] == frame), 'd_calc_postsnap'] = dis
                
            if(verbose>2):print("{} yards, ".format(round(dis,1)), end= ' ') 
            if(verbose>2):print("{} y/s.".format(round(speed,3))) 
            
        
        avgspeed = speedHolder/frame
    
        if(verbose>1):print (colored.fg("blue") + "Play {} complete, {} total yards, {} post snap".format(play, disHolder, ps_holder)) 
        if(verbose>1):print (colored.fg("blue") + "Play {} complete, {} y/s average".format(play, avgspeed)) 
        
        distTravelled += disHolder
        psDistTravelled += ps_holder
        
        if(verbose>1):print("Current totals: All: {} Post-snap: {}".format(round(distTravelled,1),round(psDistTravelled,1)))
        
    if(verbose>0):print(colored.fg("cyan") + "\n Player {} travelled {} yards total".format(player,distTravelled))
    if(verbose>0):print(colored.fg("cyan") + "\n Player {} travelled {} yards after snap".format(player,psDistTravelled))
    
    bigAvg = total/frameCounter
    if(verbose>0): print(colored.fg("cyan") + "\nComplete with player {}.  Average speed of {} y/s over {} frames ".format(player,bigAvg,frameCounter))



week1['time1'] = pd.to_datetime(week1.time).dt.tz_localize(None)
verbose=2
#speed calc
for player in playerIds :
    if(verbose>=0): print(colored.fg("red") + "Analyzing player {}".format(player))
    counter=0
    total=0
    speed=0
    #print(colored.fg("red") + "Analyzing player {}".format(player))
    #print(colored.fg("white"))
 
    playerDF = week1.loc[week1['nflId'] == player]
    # print(playerDF)
    plays=pd.unique(playerDF['playId'])

    # Go through each play for a given player
    for play in plays :
        #print(colored.fg("white") + "analyzing play: {}".format(play))
        #Create a DF for each play
        playdf = playerDF[playerDF['playId']==play]
        #Figure out how many frames in current play
        maxFrame = playdf['frameId'].max()
        
        frame=1
        
        holder=0
        # Go through each timestep in a given play
        while frame+1 <= maxFrame :
            counter+=1
            d = playdf.loc[playdf['frameId'] == frame, 'd_calc'].iloc[0]
            t1 = playdf.loc[playdf['frameId'] == frame, 'time1'].iloc[0]
            t2 = playdf.loc[playdf['frameId'] == frame+1, 'time1'].iloc[0]
            speed = findSpeed(d, t1, t2)
            week1.loc[(week1['nflId'] == player) & (week1['playId'] == play) & 
                (week1['frameId'] == frame), 's_calc'] = speed
            # week1[(week1['nflId'] == player) & (week1['playId'] == play) & (week1['frameId'] == frame)] ['d_calc'] = distTravelled
            # print(colored.fg("blue") + "x1: {} y1: {} \nx2: {} y2: {}".format(x1,y1,x2,y2))
            # print(colored.fg("green") + "Dist tranvelled: {} ".format(findDistance(x1,y1,x2,y2)))
            frame+=1
            holder += speed
            total+= speed
        avgspeed = holder/frame
        
        if(verbose>1): print(colored.fg("green") + "On play {}, player {} averaged {} y/s.".format(play,player,round(avgspeed,1))) 
    bigAvg = total/counter
    print(colored.fg("red") + "\nComplete with player {}.  Average speed of {} y/s over {} frames ".format(player,bigAvg,counter))

week1.to_csv('final.csv')

end = time.time()
print(f"Runtime of the program is {end - start}")
