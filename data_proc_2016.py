# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 19:38:52 2016

@author: Matt

Processes schedule and preps data for use in data scraping
Gets 'cbb_teams.csv' and adds column for team's url name
Then gets game stats from R and calculates the last n game stats
Outputs 'game_stats_v2.csv'

"""

import pandas as pd
import numpy as np
from datetime import datetime as dt

#==============================================================================
# Reads in list of colleges
#==============================================================================
#if __name__ == '__main__':
    #Creates list of colleges in CBB's database    
#    create_name_list()   

    #Then that list is passed off to R to data scrape for the schedule, 'sched.csv' 

    #Reads in Schedule of games, filters those games and then adds the url     
#    clean_list()    

    #Creates statistics for last n games for team
#   create_stats()

    
#==============================================================================
# Adds the team's regular name to the schedule
#==============================================================================
def clean_list():
    sched=pd.read_csv('sched.csv')
    key=pd.read_csv('cbb_teams_v2.csv')
#    print len(sched)
    sched.rename(columns={'Team': 'Team_ID'}, inplace=True)    
    sched=pd.merge(left=sched, right=key, left_on='Team_ID', right_on='School')
    sched=sched[sched['Type']=='REG']
    sched=sched[sched['Var.5']!='N']
    sched=sched[['Team_ID', 'Date', 'Var.5', 'Opponent', 'School', 'School_url', 'Var.8']]
    sched=make_url_worthy(sched, 'Opponent', 'Opponent_url')
    sched=sched.reset_index(drop=True)
    sched.to_csv('sched_v2.csv', index=False) 
    return sched


#==============================================================================
# Cleans list of teams and adds url-friendly column
#==============================================================================
def create_name_list():
    team_names=pd.read_csv('cbb_teams.csv')
    print len(team_names)
    team_names=team_names[team_names['Rk']>0]
    print len(team_names)
    team_names=team_names[team_names['School']!='School']
    print len(team_names)
    team_names= make_url_worthy(team_names, 'School', 'School_url')        
    team_names.to_csv('cbb_teams_v2.csv', index=False)
    
    
#==============================================================================
# Converts School names to CBB nomenclature for URLs    
#==============================================================================
def make_url_worthy(data, old_col, new_col):
    new_data=data.copy()
    new_data[new_col]=data[old_col].copy()
    for index, row in data.iterrows():
        curr_row=data.ix[index,old_col]
        curr_row=curr_row.replace('&amp; ', '')        
        curr_row=curr_row.replace('&amp;', '')    
        curr_row=curr_row.replace('& ', '')  
        curr_row=curr_row.replace('&', '')          
        curr_row=curr_row.replace('UC-', 'California-')
        curr_row=curr_row.replace('University of ','')
        curr_row=curr_row.replace('SIU','Southern-Illinois')
        curr_row=curr_row.replace('Rio Grande Valley','pan-american')
        curr_row=curr_row.replace('\xc2\xa0','')
        curr_row=curr_row.replace("'",'')
        curr_row=curr_row.replace(".",'')
        for i in range(0,26):
            curr_row=curr_row.replace('('+str(i)+')', '')
        curr_row=curr_row.replace(' (','-')
        curr_row=curr_row.replace('(','-')
        curr_row=curr_row.replace(')','')
        curr_row=curr_row.replace(' ', '-')  
        curr_row=curr_row.lower()
        new_data.ix[index,new_col]=curr_row
    return new_data


#==============================================================================
# Gets 'sched_stats.cvs' from R and finds last n game stats
#==============================================================================
def create_stats():
    #gets this data from R
    games=pd.read_csv('sched_stats_v2.csv')
    
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
    #Caps and Floors model inputs to get rid of outliers
    game_stats=cap_and_floor(game_stats, ['Team', 'games', 'Win', 'Team_stats', 'School'])
    game_stats.to_csv('game_stats_v2.csv', index=False)
    
    
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
