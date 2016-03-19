# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 19:38:52 2016

@author: Matt

Processes schedule and preps data for use in data scraping
Gets 'cbb_teams.csv' and adds column for team's url name
Does the same thing for both teams in schedule

"""

import pandas as pd

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
# Adds the team's regular name to the schedule
#==============================================================================
def clean_list():
    sched=pd.read_csv('sched.csv')
    key=pd.read_csv('cbb_teams_v2.csv')
#    print len(sched)
    sched.rename(columns={'Team': 'Team_ID'}, inplace=True)    
    sched=pd.merge(left=sched, right=key, left_on='Team_ID', right_on='School')
#    print len(sched)
    return sched


#==============================================================================
# Reads in list of colleges
#==============================================================================
#if __name__ == '__main__':
    #Creates list of colleges in CBB's database    
#    create_name_list()   

    #Then that list if passed off to R to data scrape for the schedule, 'sched.csv' 

    #Reads in Schedule of games, filters those games and then adds the url     
#    sched=pd.read_csv('sched.csv')
#    key=pd.read_csv('cbb_teams_v2.csv')
#    
#    sched=clean_list()    
#    
#    print len(sched)
#    sched=pd.merge(left=sched, right=key, left_on='Team_ID', right_on='School_url')
#    print len(sched)
#    sched=sched[sched['Type']=='REG']
#    print len(sched)
#    sched=sched[sched['Var.5']!='N']
#    print len(sched)
#    sched=sched[['Team_ID', 'Date', 'Var.5', 'Opponent', 'School', 'School_url', 'Var.8']]
#    sched=make_url_worthy(sched, 'Opponent', 'Opponent_url')
#    sched=sched.reset_index(drop=True)
#    sched.to_csv('sched_v2.csv', index=False)
#    
    
