# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 21:06:36 2016

@author: Matt

Gets game by game data from R and calculates past statistics for each game
"""
import pandas as pd
import numpy as np
from datetime import datetime as dt
from Data_proc import *

#==============================================================================
# Restricts values of predictor variables to +/- 2 std deviations
#==============================================================================
def cap_and_floor(data, exclusions):
    for col in data.columns:
        if col not in exclusions:
            print col
            mean=np.mean(data[col])
            std_dev=np.std(data[col])
            upper_bound=mean+2*std_dev
            lower_bound=mean-2*std_dev
            data[col]=[min(upper_bound, x) for x in data[col]]
            data[col]=[max(lower_bound, x) for x in data[col]]
    return data


#==============================================================================
# Gets 'sched_stats.cvs' from R and finds last n game stats
#==============================================================================
def create_stats():
    #gets this data from R
    games=pd.read_csv('sched_stats_v2.csv')
    
    #gets this data from kaggle for 2014-2015 season
#    
#    old_games=pd.read_csv('2015_games_rev.csv')   
#    old_games_v1=pd.DataFrame()
#    old_games_v1[']
    
    #Adds in Date for sorting
    games['Date']=[x[5:] for x in games['Date']]
    games['Date']=[dt.strptime(x, "%b %d, %Y") for x in games['Date']]
    games.sort_values(by='Date', inplace=True)
    games=games.reset_index(drop=True)
    
    #Iterates through sorted list and calculates last game stats
    game_stats=pd.DataFrame(index=range(len(games)))
    for index, row in games.iterrows():
        if index>0:        
            team=row['School_url']
            o_team=row['Opponent_url']
#            print index, team
            game_list=games.ix[0:index-1,:]
#            print len(game_list)
            game_list=game_list[game_list['School_url']==o_team]
#            print len(game_list)
            
            game_stats.set_value(index,'Team', team)
            game_stats.set_value(index,'games', len(game_list))
            game_stats.set_value(index, 'Win', row['Var.8'])
            game_stats.set_value(index, 'T_Pace', np.mean(game_list['Pace']))
            game_stats.set_value(index, 'T_EFG', np.mean(game_list['EFG']))
            game_stats.set_value(index, 'T_ORB', np.mean(game_list['ORB']))
            game_stats.set_value(index, 'T_TOV', np.mean(game_list['TOV']))
            game_stats.set_value(index, 'T_FTFGA', np.mean(game_list['FTFGA']))
            
            game_stats.set_value(index,'Team_stats', o_team)
            game_stats.set_value(index, 'O_EFG', np.mean(game_list['O_EFG']))
            game_stats.set_value(index, 'O_ORB', np.mean(game_list['O_ORB']))
            game_stats.set_value(index, 'O_TOV', np.mean(game_list['O_TOV']))
            game_stats.set_value(index, 'O_FTFGA', np.mean(game_list['O_FTFGA']))
            
        if index%100==0:
            print index
            
    #Gets rid of games with NaN
    game_stats=game_stats[game_stats['games']>1]
    
    #Adds SOS to dataset for entire season
    sos=pd.read_csv('adv_stats.csv')
    sos=sos[['School', 'SOS']]    
    
    game_stats=pd.merge(game_stats, sos, left_on='Team_stats', right_on='School')
    
    game_stats.to_csv('game_stats.csv', index=False)
    
    game_stats['SOS']=[float(x) for x in game_stats['SOS']]    
    
    game_stats=cap_and_floor(game_stats, ['Team', 'games', 'Win', 'Team_stats', 'School'])
    
    game_stats.to_csv('game_stats_v2.csv', index=False)