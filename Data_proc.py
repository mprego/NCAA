# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 12:10:54 2016

@author: Matt
"""

import pandas as pd
import numpy as np
from data_proc_v2 import make_url_worthy

def make_2015_data():
    # read in data
    reg_season=pd.read_csv('RegularSeasonDetailedResults.csv')
    print 'test of reading in data'
    print len(reg_season)
    
    post_season=pd.read_csv('TourneyDetailedResults.csv')
    reg_season=reg_season.append(post_season)
    print len(reg_season)
    
    # read in top teams
#    top_teams=pd.read_csv('Top_Teams.csv')
#    print 'test of reading in top teams'
#    print len(top_teams)
    
    team_id=pd.read_csv('Teams.csv')
#    print 'test of reading team IDs'
#    print len(team_id)
    
#    top_teams_id=pd.merge(left=top_teams, right=team_id, left_on='Team', right_on='Team_Name')
#    top_teams_id.drop('Team_Name', axis=1, inplace=True)
##    print 'test of merged team list'
##    print len(top_teams_id)
#    
#    matches=top_teams['Team'].isin(top_teams_id['Team'])
#    missing_teams=top_teams[~matches]
#    print missing_teams
    
    # filter data to 2015 season and post season
    reg_season_2015=reg_season[reg_season['Season']==2015]
#    print 'test of 2015 regular season'
#    print len(reg_season_2015)
    
    # filter data to top teams
#    winners=pd.merge(left=reg_season_2015, right=top_teams_id, left_on='Wteam', right_on='Team_Id')
#    losers=pd.merge(left=reg_season_2015, right=top_teams_id, left_on='Lteam', right_on='Team_Id')
#    print 'test of filtered 2015 regular season top teams'
#    print len(winners)
    
    # creates a list for the winning and losing teams in each matchup
    winners=pd.merge(left=reg_season_2015, right=team_id, left_on='Wteam', right_on='Team_Id', suffixes=['', '_W'])
    winners=pd.merge(left=winners, right=team_id, left_on='Lteam', right_on='Team_Id', suffixes=['', '_L'])
    losers=pd.merge(left=reg_season_2015, right=team_id, left_on='Lteam', right_on='Team_Id', suffixes=['', '_L'])
    losers=pd.merge(left=losers, right=team_id, left_on='Wteam', right_on='Team_Id', suffixes=['', '_W'])

    winners.rename(columns={'Team_Name': 'Team', 'Team_Name_L': 'Team_L'}, inplace=True)
    losers.rename(columns={'Team_Name': 'Team', 'Team_Name_W': 'Team_W'}, inplace=True)    
    
    # calculate 4 metrics for each game
    winner_df=pd.DataFrame()
    winner_df['Team']=winners['Team']
    winner_df['Day']=winners['Daynum']
    winner_df['EFG']=(winners['Wfgm']+.5*winners['Wfgm3'])/winners['Wfga']
    winner_df['TOV']=winners['Wto']/(winners['Wfga']+.44*winners['Wfta']+winners['Wto'])
    winner_df['ORB']=winners['Wdr']/(winners['Lor']+winners['Wdr'])
    winner_df['FTFGA']=winners['Wftm']/winners['Wfga']
    winner_df['O_Team']=winners['Team_L']
    
#    winner_df['O_EFG']=(winners['Lfgm']+.5*winners['Lfgm3'])/winners['Lfga']
#    winner_df['O_TOV']=winners['Lto']/(winners['Lfga']+.44*winners['Lfta']+winners['Lto'])
#    winner_df['O_ORB']=winners['Ldr']/(winners['Wor']+winners['Ldr'])
#    winner_df['O_FTFGA']=winners['Lftm']/winners['Lfga']
    winner_df['Won']=1
    
    loser_df=pd.DataFrame()
    loser_df['Team']=losers['Team']
    #loser_df['O_Team']=losers[']
    loser_df['Day']=losers['Daynum']
    loser_df['EFG']=(losers['Lfgm']+.5*losers['Lfgm3'])/losers['Lfga']
    loser_df['TOV']=losers['Lto']/(losers['Lfga']+.44*losers['Lfta']+losers['Lto'])
    loser_df['ORB']=losers['Ldr']/(losers['Wor']+losers['Ldr'])
    loser_df['FTFGA']=losers['Lftm']/losers['Lfga']
    loser_df['O_Team']=losers['Team_W']
    
#    loser_df['O_EFG']=(losers['Wfgm']+.5*losers['Wfgm3'])/losers['Wfga']
#    loser_df['O_TOV']=losers['Wto']/(losers['Wfga']+.44*losers['Wfta']+losers['Wto'])
#    loser_df['O_ORB']=losers['Wdr']/(losers['Lor']+losers['Wdr'])
#    loser_df['O_FTFGA']=losers['Wftm']/losers['Wfga']
    loser_df['Won']=0

    reg_season_2015=winner_df.append(loser_df)
    print 'test of calculating 4 metrics'
    print (len(winner_df)+ len(loser_df)), len(reg_season_2015)
    reg_season_2015.to_csv('2015_games.csv', index=False)
    # make a subschedule of top teams
    print 'test of filtering top teams'
    print len(reg_season_2015)
    reg_season_2015_top=pd.merge(left=reg_season_2015, right=top_teams_id, left_on='Team', right_on='Team')
    print len(reg_season_2015_top)
    
    # for each team, calculate their last n game stats
    reg_2015_stats=pd.DataFrame()
    print 'test of finding last games'
    
    for index, row in reg_season_2015.iterrows():
        team=row['Team']
        day=row['Day']
        prev_games=reg_season_2015[reg_season_2015['Team']==team]
        prev_games=prev_games[prev_games['Day']<day]
        
        reg_2015_stats.set_value(index, 'Team', team)
        reg_2015_stats.set_value(index, 'Day', day)
        reg_2015_stats.set_value(index, 'Won', row['Won'])
        reg_2015_stats.set_value(index, 'EFG avg', np.mean(prev_games['EFG']))
        reg_2015_stats.set_value(index, 'TOV avg', np.mean(prev_games['TOV']))
        reg_2015_stats.set_value(index, 'ORB avg', np.mean(prev_games['ORB']))        
        reg_2015_stats.set_value(index, 'FTFGA avg', np.mean(prev_games['FTFGA'])) 
        reg_2015_stats.set_value(index, 'win avg', np.mean(prev_games['Won']))
        
        # Repeat for the other team
        o_team=row['O_Team']
        #day=row['Day']
        o_prev_games=reg_season_2015[reg_season_2015['Team']==o_team]
        o_prev_games=o_prev_games[o_prev_games['Day']<day]
        
        reg_2015_stats.set_value(index, 'O_Team', o_team)
        #reg_2015_stats.set_value(index, 'Day', day)
        #reg_2015_stats.set_value(index, 'Won', row['Won'])
        reg_2015_stats.set_value(index, 'O EFG avg', np.mean(o_prev_games['EFG']))
        reg_2015_stats.set_value(index, 'O TOV avg', np.mean(o_prev_games['TOV']))
        reg_2015_stats.set_value(index, 'O ORB avg', np.mean(o_prev_games['ORB']))        
        reg_2015_stats.set_value(index, 'O FTFGA avg', np.mean(o_prev_games['FTFGA'])) 
        reg_2015_stats.set_value(index, 'O win avg', np.mean(o_prev_games['Won']))
    
    reg_2015_stats.to_csv('2015_stats.csv', index=False)
        
        #next to do: make sure the opponent's name is in my game list, so i can then later find their last n games stats
        
#==============================================================================
# To test out joining team names between cbb and kaggle
#==============================================================================
if __name__ == '__main__':
    games=pd.read_csv('sched_stats_v2.csv')
    cbb_names=games.drop_duplicates('School_url')
    kagg_games=pd.read_csv('2015_games.csv')
    kagg_games=make_url_worthy(kagg_games, 'O_Team', 'O_Team_url')
#   agg_names[~kagg_names.O_Team_url.isin(cbb_names.School_url)].to_csv('kagg_excl.csv')
    key=pd.read_csv('key.csv')    
    print len(kagg_games)
    kagg_games1=pd.merge(kagg_games, key, how='inner', left_on='O_Team_url', right_on='old')
    kagg_games1['Team']=kagg_games1['new']
    print len(kagg_games1)
    kagg_games2=kagg_games[kagg_games.O_Team_url.isin(cbb_names.School_url)]
    print len(kagg_games2)
    kagg_games2['Team']=kagg_games2['O_Team_url']
    kagg_games=kagg_games1.append(kagg_games2)
    kagg_games=kagg_games[['Team', 'EFG', 'FTFGA', 'ORB', 'TOV', 'Won']]
    kagg_games.to_csv('2015_games_rev.csv')
    