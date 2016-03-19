# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 19:48:29 2016

@author: Matt

Creates and scores models for each game in bracket
Then simulates the tournament and prints out results
"""
import pandas as pd
import numpy as np
from Model import make_model, prob_win


if __name__ == '__main__':
    bracket=pd.read_csv('bracket_16.csv')
    team_stats=get_ye_stats(bracket, 'adv_opp_stats.csv', 'adv_stats.csv')
    team_models=create_models(bracket,pd.read_csv('game_stats_v2.csv'))
    simulate_tourn(bracket, team_stats, team_models, 'cons_2016_results.csv', 100)
 

#==============================================================================
# Gets year-end stats for teams in bracket
#==============================================================================
def get_ye_stats(bracket, stats, opp_stats):    
    # Reads in year-end stats for each team in the tournament
    all_opp_stats=pd.read_csv(opp_stats)
    all_stats=pd.read_csv(stats)    
    
    # Creates table of end of year stats for each team in teh tournament.  Used in model scoring
    team_stats=pd.DataFrame()
    for index, row in bracket.iterrows():
        team_stats.set_value(index, 'Team', row['Team'])
        stats=all_stats[all_stats['School']==row['Team']].reset_index(drop=True)
        opp_stats=all_opp_stats[all_opp_stats['School']==row['Team']].reset_index(drop=True)
        team_stats.set_value(index,'T_Pace', stats.ix[0,'Pace'])
        team_stats.set_value(index,'T_EFG',stats.ix[0,'eFG%'])
        team_stats.set_value(index,'T_ORB',stats.ix[0,'ORB%'])
        team_stats.set_value(index,'T_TOV',stats.ix[0,'TOV%'])
        team_stats.set_value(index,'T_FTFGA',stats.ix[0,'FT/FGA'])
        team_stats.set_value(index,'O_EFG',opp_stats.ix[0,'eFG%'])
        team_stats.set_value(index,'O_ORB',opp_stats.ix[0,'ORB%'])
        team_stats.set_value(index,'O_TOV',opp_stats.ix[0,'TOV%'])
        team_stats.set_value(index,'O_FTFGA',opp_stats.ix[0,'FT/FGA'])
        team_stats.set_value(index,'SOS',stats.ix[0,'SOS'])
    return team_stats
                 
                 
#==============================================================================
# Creates model for each team.  Warning: takes several minutes
#==============================================================================
def create_models(bracket, game_stats):
    team_models={}   
    for team in bracket['Team']:
        team_models[team]=make_model(team, game_stats) 
    return team_models
    
    
#==============================================================================
# Simulates each region and then the final four
# Outputs results in 'records.csv' and 'cons_records.csv'
#==============================================================================
def simulate_tourn(bracket, team_stats, team_models, output, n):
    records=pd.DataFrame(0,index=bracket['Team'],columns=range(100,100*(6+1)))
    
    south_probs=simulate_region(1, team_stats, team_models, bracket,records, n)
    west_probs=simulate_region(2, team_stats, team_models, bracket, records,n)
    east_probs=simulate_region(3, team_stats, team_models, bracket,records, n)
    midwest_probs=simulate_region(4, team_stats, team_models, bracket,records, n)
    sim_final_four(south_probs, west_probs, east_probs, midwest_probs, team_stats, team_models, records, n)
    
    records.to_csv('records.csv')
    
    cons_records=pd.DataFrame()
    for col in records.columns:
        col_sum=np.sum(records[col])
        if col_sum>0:
            col_data=records[col].sort_values(ascending=False).reset_index()
            cons_records[(str(col)+'_Teams')]=col_data['Team']
            cons_records[col]=col_data[col]
    cons_records.to_csv(output, index=False)


#==============================================================================
# Simulates a round in the NCAA Tournament
# Given a region, team stats, and models, it outputs the probabilities of winners and a simulated winner
#==============================================================================
def sim_round(data, stats, models, region_id):
    round1=pd.DataFrame(index=range(0,len(data)/2),columns=['Seed','Team1', 'Team2', 'P_Win_1', 'Team', 'Place_ID'])
    for i in range(len(data)/2):
        team1=data.ix[i+1, 'Team']
        team2=data.ix[len(data)-i, 'Team']
#        print team1,team2
        team1_stats=stats[stats['Team']==team1].drop(['Team'], axis=1)
        team2_stats=stats[stats['Team']==team2].drop(['Team'],axis=1)
        team1_model=models[team1]
        team2_model=models[team2]
        #Villanova is hard-coded because they don't have enough losses in 2015-2016 season
        if team1=='Villanova':
            prob1=29.0/34.0
        else:
            prob1=prob_win(team1_model, team2_stats)
#        print prob1
        if team2=='Villanova':
            prob2=29.0/34.0
        else:
            prob2=prob_win(team2_model, team1_stats)
#        print prob2
        prob=(prob1+(1-prob2))/2
        round1.ix[i,'Seed']=i+1
        round1.ix[i,'Team1']=team1
        round1.ix[i,'Team2']=team2
        round1.ix[i,'P_Win_1']=prob
        if np.random.rand()<prob:
            round1.ix[i,'Team']=team1
        else:
            round1.ix[i, 'Team']=team2
        round1.ix[i,'Place_ID']=100*region_id+(5-np.log2(len(data)))*10+i
    return round1
    
    
#==============================================================================
# Records the simulated results and tallies it up
#==============================================================================
def record_results(data, result):
    for index, row in result.iterrows():
        win_team=row['Team']
        seed_id=row['Place_ID']
        data.set_value(win_team, seed_id, data.ix[win_team, seed_id]+1)
#    print result
    return data
    
    
#==============================================================================
# Simulates an entire region for n times
#==============================================================================
def simulate_region(region_id, team_stats, team_models, bracket, records,n_sims):
    south=bracket[bracket['Region']==region_id].sort_values(by='Seed').set_index('Seed')
    
    for i in range(n_sims):
        south1=sim_round(south,team_stats, team_models, region_id)
        records=record_results(records,south1)
        
        south2=sim_round(south1.sort_values(by='Seed').set_index('Seed'),team_stats,team_models,region_id)
        records=record_results(records,south2)
        
        south3=sim_round(south2.sort_values(by='Seed').set_index('Seed'),team_stats,team_models,region_id)
        records=record_results(records,south3)
        
        south4=sim_round(south3.sort_values(by='Seed').set_index('Seed'),team_stats,team_models,region_id)
        records=record_results(records,south4)
    return records
    
    
#==============================================================================
# Simulates the final four by starting with simulated final four teams
#==============================================================================
def sim_final_four(s, w, e, mw, team_stats, team_models, records, sims):
    for i in range(sims):
        ff_bracket=pd.DataFrame()
        #South
        ff_bracket.set_value(0,'Region',5)
        ff_bracket.set_value(0,'Team',return_rand_team(s,140))
        ff_bracket.set_value(0,'Seed',1)
        
        ff_bracket.set_value(1,'Region',5)
        ff_bracket.set_value(1,'Team',return_rand_team(w,240))
        ff_bracket.set_value(1,'Seed',4)    
    
        ff_bracket.set_value(2,'Region',5)
        ff_bracket.set_value(2,'Team',return_rand_team(e,340))
        ff_bracket.set_value(2,'Seed',2)
    
        ff_bracket.set_value(3,'Region',5)
        ff_bracket.set_value(3,'Team',return_rand_team(mw,440))
        ff_bracket.set_value(3,'Seed',3)
        print ff_bracket
        ff_bracket=ff_bracket.sort_values(by='Seed').set_index('Seed')
        final=sim_round(ff_bracket, team_stats, team_models, 5)
        records=record_results(records, final)
        
        champ=sim_round(final.sort_values(by='Seed').set_index('Seed'), team_stats, team_models, 6)
        records=record_results(records, champ)
    return records
    
    
#==============================================================================
# Helper method for final four simulation
# Returns a random team according to probabilities in simulation
#==============================================================================
def return_rand_team(df, col):
    rand=np.random.rand()
    sum_df=np.sum(df.ix[:,col])
    cum_sum=0
    prob_list={}
    for  index,row in df.iterrows():
        cum_sum=cum_sum+df.ix[index,col]*1.0/sum_df
        if rand<cum_sum:
#            print rand, cum_sum
            return index
        prob_list[index]=cum_sum
    return prob_list
    
