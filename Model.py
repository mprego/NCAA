# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 17:25:32 2016

@author: Matt

Develops a model for each team and also scores the model during the simulation
"""

import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import KFold
from sklearn import grid_search


#==============================================================================
# Returns with the best mode for a given team
#==============================================================================
def make_model(team, data, target, drop_list):
    #makes model for this team
    game_list=data[data['Team']==team]
    y=np.ravel(game_list[target])
    x=game_list.drop(drop_list, axis=1)
#    x=game_list.drop(['Team', 'games', 'Win', 'Team_stats', 'School'], axis=1)
#    print len(game_list)
#    if team=='Villanova':
#        return (29/34)
#    if team=='Kansas':
#        best_svm=-1
#    else:
    parameters={'kernel':('linear', 'rbf', 'poly'), 'C':[0.1,.5, 1, 5,10], 'degree':[1,2,3,4]}
    svr=SVC(probability=True)
    svm=grid_search.GridSearchCV(svr, parameters)
    svm=grid_search.GridSearchCV(svr, parameters)
    svm.fit(x,y)    
    best_svm=svm.best_score_
    parameters={'n_estimators':[5,10,20,30,40,50], 'criterion':['gini', 'entropy']}
    rfm=RandomForestClassifier()
    rfm_g=grid_search.GridSearchCV(rfm, parameters)
    rfm_g.fit(x,y)
    best_rfm= rfm_g.best_score_
    
    if best_svm>best_rfm:
        return svm
    else:
        return rfm_g
        

#==============================================================================
# Uses grid search and CV to find best SVM for the data
#==============================================================================
def svm_model(x,y):
    # SVM modeling
    parameters={'kernel':('linear', 'rbf', 'poly'), 'C':[0.1,.5, 1, 5,10], 'degree':[1,2,3,4]}
    svr=SVC()
    svm=grid_search.GridSearchCV(svr, parameters)
    svm=grid_search.GridSearchCV(svr, parameters)
    svm.fit(x,y)
    print svm.best_score_
    print svm.best_params_


#==============================================================================
# Uses grid search and CV to find the best Random Forest model for the data
#==============================================================================
def ran_forest_model(x,y):
    # Random Forest Modeling
    parameters={'n_estimators':[5,10,20,30,40,50], 'criterion':['gini', 'entropy']}
    rfm=RandomForestClassifier()
    rfm_g=grid_search.GridSearchCV(rfm, parameters)
    rfm_g.fit(x,y)
    print rfm_g.best_score_
    print rfm_g.best_params_
    
    
#==============================================================================
# Returns the probability that the team will win using the team's best model
#==============================================================================
def prob_win(model, x_test):    
    if model.best_estimator_.classes_[0]=='W':
        return model.predict_proba(x_test)[0][0]
    else:
        return model.predict_proba(x_test)[0][1]
        
def prob_win_kagg(model, x_test):    
    if model.best_estimator_.classes_[0]==1:
        return model.predict_proba(x_test)[0][0]
    else:
        return model.predict_proba(x_test)[0][1]