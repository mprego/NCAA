setwd("~/Documents/!Research/Github/NCAA")
library(devtools)
c('rvest','dplyr','pipeR') -> packages 
lapply(packages, library, character.only = T) #loops through the packages and loads them


# So i need to get a list of each school's name according to sportsrefernce.com
teams=read.csv('cbb_teams_v2.csv', header=TRUE)
teams=teams[,3]
teams=as.character(teams)
sched=data.frame()
for(i in 1:length(teams))  {
  print (i)
  print (teams[i])
  sched=rbind(sched, cbind('Team_ID'=teams[i], get_team_sched(teams[i])))
} 
sched%>>%write.csv("sched.csv", row.names=FALSE)


# Then i can combine the scheudle and get rid of duplicate games


# Then i need to scrape its schedule 
sched2_orig=read.csv('sched_v2.csv')
sched2=sched2_orig
for(i in 8000:nrow(sched2)) {
  print (i)
  if(sched2[i,3]=='@') {
    a=1
    b=2
    team=sched2[i,8]
  }
  else {
   a=2
   b=1
  team=sched2[i,6]
  }
  team=as.character(team)
  if(team=='vmi') {
    team='virginia-military-institute'
  }
  print (team)
  date_str=as.character(sched2[i,2])
  stats=get_four_factors(team, date_str)
  sched2[i,'Pace']=stats[1,'Pace']
  sched2[i,'EFG']=stats[a,3]
  sched2[i,'TOV']=stats[a,4]
  sched2[i,'ORB']=stats[a,5]
  sched2[i,'FTFGA']=stats[a,6]
  sched2[i,'O_EFG']=stats[b,3]
  sched2[i,'O_TOV']=stats[b,4]
  sched2[i,'O_ORB']=stats[b,5]
  sched2[i,'O_FTFGA']=stats[b,6]
}
sched2%>>%write.csv('sched_stats_v2.csv', row.names=FALSE)
# Then i need to go through its schedule and scrape the 4 factors plus pace
# export the giant game schedule in a csv

get_four_factors <- function(team, date_str) {
  mnth=substr(date_str,6,8)
  mnth=match(tolower(mnth), tolower(month.abb))
  if(mnth<10)
    mnth=paste0('0', mnth)
  day=substr(date_str,10,nchar(date_str)-6)
  if(as.integer(day)<10)
    day=paste0('0',day)
  year=substr(date_str, nchar(date_str)-3,nchar(date_str))
  date=paste0(year,'-',mnth,'-',day,'-')
  
  css_page<-'#four_factors'
  url<-'http://www.sports-reference.com/cbb/boxscores/' %>>% paste0(date) %>>% paste0(team) %>>% paste0('.html')
  print (url)
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


get_team_sched <- function(team) {
  css_page<-'#schedule'
  url<-'http://www.sports-reference.com/cbb/schools/' %>>% paste0(team) %>>% paste0('/2016-schedule.html')
  url %>>%
    html%>>%
    html_nodes(css_page)%>>%
    html_table(header = F) %>>%
    data.frame() %>>%
    tbl_df() -> total_table
  colnames(total_table)<-total_table[1,]
  total_table<-total_table[-1,c(2,4,5,6,7,8,9)]
  return(total_table)
}


