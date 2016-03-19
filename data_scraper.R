today_dt<-Sys.Date()   #'2015-01-06'  #date that we want to analyze

# old_old_sched<-create_sched('2012-10-01','2013-07-15')
# old_old_sched<-add_factors(old_old_sched)
# old_old_sched%>>%write.csv("old_old_sched.csv", row.names=FALSE)
# old_old_sched<-read.csv("old_old_sched.csv")
# old_old_sched$Date<-as.Date(old_old_sched$Date)
# old_old_sched_stat<-sched_stats(old_old_sched, old_old_sched, 5)
# old_old_sched_stat%>>%write.csv("old_old_sched_stat.csv",row.names=FALSE)
old_old_sched_stat<-read.csv("old_old_sched_stat.csv")
old_old_sched_stat$Date<-as.Date(old_old_sched_stat$Date)

#old_sched<-create_sched('2013-10-01','2014-07-15')
#old_sched<-add_factors(old_sched)
#old_sched%>>%write.csv("old_sched.csv", row.names=FALSE)
# old_sched<-read.csv("old_sched.csv")
# old_sched$Date<-as.Date(old_sched$Date)
# old_sched_stat<-sched_stats(old_sched, old_sched, 5)
# old_sched_stat%>>%write.csv("old_sched_stat.csv",row.names=FALSE)
old_sched_stat<-read.csv("old_sched_stat.csv")
old_sched_stat$Date<-as.Date(old_sched_stat$Date)

#new_sched<-create_sched('2014-10-02', Sys.Date())
#new_sched<-add_factors(new_sched)
#new_sched%>>%write.csv("new_sched.csv", row.names=FALSE)
new_sched<-read.csv("new_sched.csv")
new_sched$Date<-as.Date(new_sched$Date)

#new_sched_stat<-sched_stats(new_sched, new_sched, 5)
#new_sched_stat%>>%write.csv("new_sched_stat.csv", row.names=FALSE)
new_sched_stat<-read.csv("new_sched_stat.csv")
new_sched_stat$Date<-as.Date(new_sched_stat$Date)

sched5<-rbind(old_old_sched_stat, old_sched_stat, new_sched_stat)
sched5%>>%write.csv("nba_seasons_12-15.csv", row.names=FALSE)
today<-date_subsched('2014-12-25', Sys.Date(), sched5)

today<-filter_count(today, 2)
sched5<-filter_count(sched5, 2)

#makes result vector
sched5_res<-date_subsched('2013-12-01', '2014-09-25', sched5)
sched5_res<-rbind(sched5_res, date_subsched('2014-12-01', '2014-12-25', sched5))
sched5_res<-rbind(sched5_res, date_subsched('2012-12-01', '2013-09-25', sched5))
attach(sched5_res)
result<-glm(H_win~h_adv_avg+a_adv_avg+h_win_per+a_win_per+h_b2b+a_b2b, family=binomial(link="logit"))

temp<-prob_win(today, result)
colnames(temp)<-c("lr_prob", "lr_corr")
today<-cbind(today, temp)

temp_sched<-date_subsched('2013-12-01', '2014-09-25', sched5)
temp_sched<-rbind(temp_sched, date_subsched('2014-12-01', '2014-12-25', sched5))
#temp_sched<-rbind(temp_sched, date_subsched('2012-12-01', '2013-09-25', sched5))
temp<-var(today, temp_sched, 15)
colnames(temp)<-c("var_prob", "var_corr")
today<-cbind(today, temp)
today<-cbind(today, match=0, match_corr=0)
for(i in 1:nrow(today)) {
  if(today[i, "lr_prob"]>.5&&today[i,"var_prob"]>.5){
    today[i,"match"]<-1
  }
  if(today[i, "lr_prob"]<.5&&today[i,"var_prob"]<.5){
    today[i,"match"]<-1
  }
}
for(i in 1:nrow(today)) {
  if(today[i, "lr_corr"]*today[i,"var_corr"]==1) {
    today[i, "match_corr"]<-1
  }
}

today_write<-subset(today, select=c(Date, Away, Home, Away.Pts, Home.Pts,lr_prob, lr_corr, var_prob, var_corr, match, match_corr))
today_write%>>%write.csv("today.csv", row.names=FALSE)

pred<-create_sched(Sys.Date(), Sys.Date()+1)
pred$Date<-as.Date(pred$Date)
pred<-add_win_per(pred, new_sched)
pred<-sched_stats(pred, new_sched, 5)
pred<-filter_count(pred, 2)
pred<-cbind(pred,lr_prob=predict(result, newdata=pred, type="response"))
temp<-var(pred, temp_sched, 15)
pred<-cbind(pred, var_prob=temp[,1])
pred%>>%write.csv("pred.csv", row.names=FALSE)

say("Done")
##########################################################################################
#loads necessary packages
##########################################################################################
setwd("~/Documents/!Research/Github/NCAA")
library(devtools)
#library(sqldf)
c('rvest','dplyr','pipeR') -> packages 
lapply(packages, library, character.only = T) #loops through the packages and loads them



##########################################################################################
#creates necessary functions for my code to work
##########################################################################################
say <- function(what) system(sprintf('say "%s"', what))

##finds variation from set of known games
var<-function(today, schedule,num) {
  pred<-data.frame(today$Home, pred_win=0.0, correct=0.0)
  pred<-pred[,-1]
  n=num   #14 is the best
  w1=.1
  w2=.1
  w3=.3
  w4=.3
  w5=.1
  w6=.1

  for(k in 1:nrow(today)) {
    var<-cbind(var=0.0, schedule)
    
    for(i in 1:nrow(schedule)) {
      var[i,1]<-w1*(today[k,"h_adv_avg"]-schedule[i, "h_adv_avg"])
      var[i,1]<-var[i,1]+w2*abs(today[k,"a_adv_avg"]-schedule[i,"a_adv_avg"])
      var[i,1]<-var[i,1]+w3*abs(today[k,"h_win_per"]-schedule[i,"h_win_per"])
      var[i,1]<-var[i,1]+w4*abs(today[k,"a_win_per"]-schedule[i,"a_win_per"])
      var[i,1]<-var[i,1]+w5*abs(today[k,"h_b2b"]-schedule[i,"h_b2b"])
      var[i,1]<-var[i,1]+w6*abs(today[k,"a_b2b"]-schedule[i,"a_b2b"])
    }
    
    var<-var[order(var$var),]
    var<-var[1:n,]
    sum<-sum(c(1:n))
    h<-1/(n-sum/(1+n))
    for(i in 1:n) {
      pred[k, "pred_win"]=pred[k,"pred_win"]+(h-h*i/(1+n))*as.numeric(var[i,"H_win"])
    }
    
#     var<-var[order(var$var),]
#     var<-var[1:n,]
#     max<-max(var$var)
#     sum<-sum(var$var)
#     for(i in 1:n) {
#       pred[k, "pred_win"]=pred[k,"pred_win"]+(max-var[i, "var"])/(n*max-sum)*as.numeric(var[i,"H_win"])
#     }

  if(as.numeric(today[k,"Home.Pts"])>as.numeric(today[k,"Away.Pts"])) {  #if home team wins
    if(pred[k,"pred_win"]>.5) {
      pred[k,"correct"]=1
    }
  }
  else {
    if(pred[k,"pred_win"]<.5) {
      pred[k,"correct"]=1
    }
  }

  
  }
  return(pred)
}

##filters out entries with less than some count of games
filter_count<-function(schedule, count) {
  temp<-schedule[1,]
  temp<-temp[-1,]
  for(i in 1:nrow(schedule)) {
    if(schedule[i, "a_count"]>=count&&schedule[i, "h_count"]>=count) {
      temp<-rbind(temp, schedule[i,])
    }    
  }
  return(temp)
}


##function that gives me offensive and defensive rating for a given game
getRatings <- function(date, h.team_id, v.team_id){
  if(date>='2014-10-01'&&date<'2015-10-01'){   #2014-2015 season
    team_names<-read.csv("team_names.csv", header=FALSE)  
  }
  if(date>='2013-10-01'&&date<'2014-10-01'){   #2013-2014 season
    team_names<-read.csv("team_names_old.csv", header=FALSE)  
  }
  if(date>='2012-10-01'&&date<'2013-10-01'){   #2012-2013 season
    team_names<-read.csv("team_names_old_2013.csv", header=FALSE)  
  }
  
  team_names<-team_names[,-2]
  names(team_names)<-c("abbrev", "Team_ID")
  
  h.team<-""
  for(i in 1:nrow(team_names))  {
    if(team_names[i,"Team_ID"]==h.team_id)  {
      h.team<-team_names[i,"abbrev"]
    }
  } 
  
  css_page<-'#four_factors'
  date_format<-format(date, "%Y%m%d")%>>%paste0('0')
  #url<-'http://www.sports-reference.com/cbb/boxscores/' %>>% paste0(date_format, h.team, ".html")
  url<-'http://www.sports-reference.com/cbb/boxscores/2016-01-02-virginia.html'
  url %>>%
    html%>>%
    html_nodes(css_page)%>>%
    html_table(header = F) %>>%
    data.frame() %>>%
    tbl_df() -> total_table
  colnames(total_table)<-total_table[2,]
  total_table<-total_table[-c(1,2),]
  return(total_table)
}


#makes a list of all games in season
create_sched<-function(b_date, e_date) {
  css_page<-'#page_content'
    url<-'http://www.sports-reference.com/cbb/conferences/acc/2016-schedule.html'
    team_names<-read.csv("team_names.csv", header=FALSE)

  url %>>%
    html%>>%
    html_nodes(css_page)%>>%
    html_table(header = F) %>>%
    data.frame() %>>%
    tbl_df() -> sched
  sched<-sched[-1,]
  sched<-sched[,c(-2,-7,-8)]
  for (i in 1:nrow(sched)) {
    sched[i,1]=substring(sched[i,1],6)  
  }
  sched$X.1=as.Date(sched$X.1, '%b %d, %Y')
  names(sched)<-c("Date", "Away", "Away.Pts", "Home", "Home.Pts")
  
  #adds team name abbreviations
  names(team_names)<-c("abbrev", "Name", "Team_ID")
  sched<-merge(sched,team_names, by.x="Home", by.y="Name" )
  sched<-sched[,-6]
  names(sched)[6]<-"Home_ID"
  sched<-merge(sched, team_names, by.x="Away", by.y="Name")
  sched<-sched[,-7]
  names(sched)[7]<-"Away_ID"
  
  ##cuts sched to just games played so far
  sched<-date_subsched(b_date, e_date, sched)  
  
#   #adds money line info
#   css_page<-'.colCenter-1-3'
#   date<-as.Date('2015-01-01')
#   date_format<-format(date, "%Y%m%d")
#   url<-'http://www.donbest.com/nba/odds/money-lines/' %>>% paste0(date_format,".html")
#   url %>>%
#     html%>>%
#     html_nodes(css_page)%>>%
#     html_table(header = F) %>>%
#     data.frame() %>>%
#     tbl_df() -> total_table
#   
  
  return (sched)
}

add_win_per<-function(today, schedule) {
  pred<-cbind(today, h_win_per=0.0, a_win_per=0.0)
  for(i in 1:nrow(pred)) {
    home_sched<-team_subsched(pred[i,"Home"], schedule)
    home_sched<-home_sched[order(home_sched$Date),]
    if(home_sched[nrow(home_sched), "Home"]==pred[i,"Home"]) {      #if the home team played its last game at home
      pred[i, "h_win_per"]=home_sched[nrow(home_sched), "h_win_per"]
    }
    else {
      pred[i, "h_win_per"]=home_sched[nrow(home_sched), "a_win_per"]
    }
    
  
    away_sched<-team_subsched( pred[i,"Away"], schedule)
    away_sched<-away_sched[order(away_sched$Date),]
    if(away_sched[nrow(away_sched), "Home"]==pred[i,"Away"]) {      #if the away team played its last game at home
      pred[i, "a_win_per"]=away_sched[nrow(away_sched), "h_win_per"]
    }
    else {
      pred[i, "a_win_per"]=away_sched[nrow(away_sched), "a_win_per"]
    }
  }
  
return(pred)
  
}

add_factors<-function(schedule ) {
  df<-cbind(schedule, h_orate=0.0, h_efg=0.0, h_tov=0.0, h_orb=0.0, h_ftfga=0.0,a_orate=0.0,a_efg=0.0, a_tov=0.0, a_orb=0.0, a_ftfga=0.0, H_win=0, h_win_per=0.0, a_win_per=0.0)
  df<-df[order(df$Date),]  #orders data by date
  
  team_wins<-data.frame(wins=as.numeric(character()))
  team_count<-data.frame(games=as.numeric(character()))
  
  for(i in 1:nrow(df))  {
    factors<-getRatings(df[i,"Date"], df[i,"Home_ID"], df[i,"Away_ID"])
    df[i,"h_efg"]<-as.numeric(factors[2,3])
    df[i,"h_tov"]<-as.numeric(factors[2,4])
    df[i,"h_orb"]<-as.numeric(factors[2,5])
    df[i, "h_ftfga"]<-as.numeric(factors[2,6])
    df[i, "h_orate"]<-as.numeric(factors[2,7])
    df[i,"a_efg"]<-as.numeric(factors[1,3])
    df[i,"a_tov"]<-as.numeric(factors[1,4])
    df[i,"a_orb"]<-as.numeric(factors[1,5])
    df[i, "a_ftfga"]<-as.numeric(factors[1,6])
    df[i, "a_orate"]<-as.numeric(factors[1,7])
    
    if (is.null(team_wins[1,df[i, "Home"]]))  {       #sets up team wins and count for season
      team_wins[1,df[i,"Home"]]<-0
      team_count[1,df[i,"Home"]]<-0
    } 
      df[i,"h_win_per"]=team_wins[1,df[i,"Home"]]/team_count[1,df[i,"Home"]]
    if(team_count[1,df[i,"Home"]]==0) {
      df[i,"h_win_per"]=.5
    }
      team_count[1,df[i,"Home"]]<-team_count[1,df[i,"Home"]]+1
  
    if (is.null(team_wins[1,df[i, "Away"]]))  {       #sets up team wins and count for season
      team_wins[1,df[i,"Away"]]<-0
      team_count[1,df[i,"Away"]]<-0
    } 
      df[i,"a_win_per"]=team_wins[1,df[i,"Away"]]/team_count[1,df[i,"Away"]]
    if(team_count[1,df[i,"Away"]]==0) {
      df[i,"a_win_per"]=.5
    }
      team_count[1,df[i,"Away"]]<-team_count[1,df[i,"Away"]]+1
    #updates wins
    if(as.numeric(df[i,"Home.Pts"])>as.numeric(df[i,"Away.Pts"])) {
      df[i,"H_win"]<-1
      team_wins[1,df[i,"Home"]]<-team_wins[1,df[i,"Home"]]+1
    }
    else {
      team_wins[1,df[i,"Away"]]<-team_wins[1,df[i,"Away"]]+1
    }
  }
  
  
  #normalizes all these factors
  efg<-c(df[,"h_efg"], df[,"a_efg"])
  m_efg<-mean(efg)
  sd_efg<-sd(efg)
  tov<-c(df[,"h_tov"], df[,"a_tov"])
  m_tov<-mean(tov)
  sd_tov<-sd(tov)
  orb<-c(df[,"h_orb"], df[,"a_orb"])
  m_orb<-mean(orb)
  sd_orb<-sd(orb)
  ftfga<-c(df[,"h_ftfga"], df[,"a_ftfga"])
  m_ftfga<-mean(ftfga)
  sd_ftfga<-sd(ftfga)
  win_per<-c(df[,"h_win_per"], df[,"a_win_per"])
  m_win_per<-mean(win_per, na.rm=TRUE)
  sd_win_per<-sd(win_per, na.rm=TRUE)

  for(i in 1:nrow(df)) {
    df[i,"h_efg"]<-(df[i,"h_efg"]-m_efg)/sd_efg
    df[i,"h_tov"]<-(df[i,"h_tov"]-m_tov)/sd_tov
    df[i,"h_orb"]<-(df[i,"h_orb"]-m_orb)/sd_orb
    df[i, "h_ftfga"]<-(df[i, "h_ftfga"]-m_ftfga)/sd_ftfga
    
    df[i,"a_efg"]<-(df[i,"a_efg"]-m_efg)/sd_efg
    df[i,"a_tov"]<-(df[i,"a_tov"]-m_tov)/sd_tov
    df[i,"a_orb"]<-(df[i,"a_orb"]-m_orb)/sd_orb
    df[i, "a_ftfga"]<-(df[i, "a_ftfga"]-m_ftfga)/sd_ftfga

    df[i,"h_win_per"]<-(df[i,"h_win_per"]-m_win_per)/sd_win_per
    df[i,"a_win_per"]<-(df[i,"a_win_per"]-m_win_per)/sd_win_per
    
    df[i,"h_off"]<-.4*df[i,"h_efg"]-.25*df[i,"h_tov"]+.2*df[i,"h_orb"]+.15*df[i,"h_ftfga"]+.25*df[i,"a_win_per"]-.068
    df[i,"a_off"]<-.4*df[i,"a_efg"]-.25*df[i,"a_tov"]+.2*df[i,"a_orb"]+.15*df[i,"a_ftfga"]+.25*df[i,"h_win_per"]+.05
  }
  
  return(df)
}

#fill in average historical stats for past few games
sched_stats<-function(today_sched, schedule, days_back) {
  schedule_stats<-cbind(today_sched, h_adv_avg=0.0,  a_adv_avg=0.0,a_b2b=0,h_b2b=0, h_count=0, a_count=0)
  for(i in 1:nrow(schedule_stats)) {
    h_count<-0
    a_count<-0
    h_adv<-0
    a_adv<-0
    h_team<-as.character(schedule_stats[i,"Home"])
    a_team<-as.character(schedule_stats[i,"Away"])
    e_date<-as.Date(schedule_stats[i,"Date"])
    b_date<-e_date-days_back
    #home team stats
    h_subsched<-team_subsched(h_team, schedule)
    h_subsched<-date_subsched(b_date, e_date, h_subsched)
    if(as.numeric(nrow(h_subsched))>0){       #ensures that there's at least one game in the past
      for(j in 1:nrow(h_subsched)) {
        h_count<-h_count+1
        if(as.character(h_subsched[j, "Home"])==h_team) { #in the case this team was the past home team
          h_adv<-h_adv+(h_subsched[j,"h_off"]-h_subsched[j,"a_off"])
        }
        else {
          h_adv<-h_adv+(h_subsched[j,"a_off"]-h_subsched[j,"h_off"])
        }
        if(h_subsched[j,"Date"]==as.Date(e_date)-1) {    #checks for back to back games for home team
          schedule_stats[i, "h_b2b"]=1
        }
      }
      schedule_stats[i,"h_count"]<-h_count
      schedule_stats[i, "h_adv_avg"]<-h_adv/h_count
    }
    #away team stats
    a_subsched<-team_subsched(a_team, schedule)
    a_subsched<-date_subsched(b_date, e_date, a_subsched)
    if(as.numeric(nrow(a_subsched))>0) {
      for(j in 1:nrow(a_subsched)) {
        a_count<-a_count+1
        if(as.character(a_subsched[j, "Home"])==a_team) {
          a_adv<-a_adv+(a_subsched[j,"h_off"]-a_subsched[j,"a_off"])
        }
        else {
          a_adv<-a_adv+(a_subsched[j,"a_off"]-a_subsched[j,"h_off"])
        }
        if(a_subsched[j,"Date"]==as.Date(e_date)-1) {    #checks for back to back games for home team
          schedule_stats[i, "a_b2b"]=1
        }
      }
      schedule_stats[i,"a_count"]<-a_count
      schedule_stats[i, "a_adv_avg"]<-a_adv/a_count
    }
  }
  return(schedule_stats)
}

prob_win<-function(schedule,res) {
  coeff<-res$coefficients
  df<-cbind(schedule, prob_win=0, correct=0)
  for(i in 1:nrow(schedule)) {
    logodds<-coeff[1]
    if(!is.na(coeff["h_off"])) {
      logodds<-logodds+coeff["h_off"]*schedule[i, "h_off"]
    }
    if(!is.na(coeff["h_def"])) {
      logodds<-logodds+coeff["h_def"]*schedule[i, "h_def"]
    }
    if(!is.na(coeff["a_off"])) {
      logodds<-logodds+coeff["a_off"]*schedule[i, "a_off"]
    }
    if(!is.na(coeff["a_def"])) {
      logodds<-logodds+coeff["a_def"]*schedule[i, "a_def"]
    }
    if(!is.na(coeff["h_b2b"])) {
      logodds<-logodds+coeff["h_b2b"]*schedule[i, "h_b2b"]
    }
    if(!is.na(coeff["a_b2b"])) {
      logodds<-logodds+coeff["a_b2b"]*schedule[i, "a_b2b"]
    }
    if(!is.na(coeff["h_win_per"])) {
      logodds<-logodds+coeff["h_win_per"]*schedule[i, "h_win_per"]
    }
    if(!is.na(coeff["a_win_per"])) {
      logodds<-logodds+coeff["a_win_per"]*schedule[i, "a_win_per"]
    }
    if(!is.na(coeff["h_off_adv"])) {
      logodds<-logodds+coeff["h_off_adv"]*schedule[i, "h_off_adv"]
    }
    if(!is.na(coeff["a_off_adv"])) {
      logodds<-logodds+coeff["a_off_adv"]*schedule[i, "a_off_adv"]
    }
    if(!is.na(coeff["h_orate_avg"])) {
      logodds<-logodds+coeff["h_orate_avg"]*schedule[i, "h_orate_avg"]
    }
    if(!is.na(coeff["a_orate_avg"])) {
      logodds<-logodds+coeff["a_orate_avg"]*schedule[i, "a_orate_avg"]
    }    
    if(!is.na(coeff["h_orate_davg"])) {
      logodds<-logodds+coeff["h_orate_davg"]*schedule[i, "h_orate_davg"]
    }
    if(!is.na(coeff["a_orate_davg"])) {
      logodds<-logodds+coeff["a_orate_davg"]*schedule[i, "a_orate_davg"]
    }
    if(!is.na(coeff["h_adv_avg"])) {
      logodds<-logodds+coeff["h_adv_avg"]*schedule[i, "h_adv_avg"]
    }    
    if(!is.na(coeff["a_adv_avg"])) {
      logodds<-logodds+coeff["a_adv_avg"]*schedule[i, "a_adv_avg"]
    }    
    prob_win<-exp(logodds)/(1+exp(logodds))
    df[i,"prob_win"]<-prob_win
    if(!is.null(schedule[i,"Home.Pts"])) {
      if(as.numeric(schedule[i,"Home.Pts"])>as.numeric(schedule[i,"Away.Pts"])) {  #if home team wins
        if(prob_win>.5) {
          df[i,"correct"]=1
        }
      }
      else {
        if(prob_win<.5) {
          df[i,"correct"]=1
        }
      }
    }
  }
  df<-cbind(df$prob_win, df$correct)
  return (df)
}

correct<-function(schedule, result){
  temp<-prob_win(schedule, result)
  count=0
  for(i in 1:nrow(temp)) {
    count=count+temp[i,2]
  }
  return(count/nrow(temp))
}