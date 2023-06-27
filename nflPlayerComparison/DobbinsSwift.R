library(tidyverse)
library(ggrepel)
library(ggimage)
library(ggjoy)
library(nflfastR)

#import 2020 season pbp
data_raw <- readRDS(url('https://raw.githubusercontent.com/guga31bb/nflfastR-data/master/data/play_by_play_2020.rds'))

###filter to match offical stats - no plays with penalities nor 2-pt conversions 
###but this doesn't count scrambles as rushes
#filter(season_type == 'REG',down <=4, play_type == 'run')
## to truly match NFL stats need to use + the fantasy column to group. there is no rusher
## name on scrambles it groups as NA
#filter(season_type == 'REG', down <=4, play_type_nfl == 'RUSH')

#use data column 'fantasy' instead of 'rusher' to assign QB scrambles as rushes
#I chose to do remove the scrambles with !is.na(rusher) when calculating 
#run share for a better picture of the called run play share
data_raw %>%  filter((season_type == 'REG' & down <=4 & play_type == 'run' & !is.na(rusher)),
       (posteam == 'DET' |posteam == 'BAL')) ->
   data

#### weekly comps ##

#percent of called run plays
weeklyRunShare <- data %>% 
   group_by(posteam, 
            week, 
            rusher
   ) %>% 
   summarize(
      plays= n(), 
      yds= sum(yards_gained), 
      ypc= mean(yards_gained), 
      #rushShare = n() / length(bdata$play_type == 'run') *100
   ) %>%
   arrange(posteam,
           week, 
           -plays
   ) %>%
   mutate(rushShare = plays / sum(plays) * 100)

#weekly run share plot - Swift Vs Dobbins
weeklyRunShare %>% 
   filter(rusher == 'J.Dobbins' | rusher == 'D.Swift') %>%
   ggplot() +
      geom_line(aes(x= week, y=rushShare, color=rusher), size=1)+
      scale_color_manual(values = c("dodgerblue3", "purple3")) +
      ggtitle('Weekly Rush share') +
      theme_light()

#weekly run share plot  - AP versus Swift
weeklyRunShare %>% 
   filter(rusher == 'A.Peterson' | rusher == 'D.Swift') %>%
   ggplot() +
   geom_line(aes(x= week, y=rushShare, color=rusher), size=1)+
   scale_color_manual(values = c("dodgerblue3", "gray")) +
   ggtitle('Weekly Rush share') +
   theme_light()


#### season totals ####

#season rush share and rushing stats
seasonRushShare <- data %>% 
   group_by(posteam, 
            rusher
   ) %>% 
   summarize(
      plays= n(), 
      yds= sum(yards_gained), 
      ypc= mean(yards_gained), 
      #rushShare = n() / length(bdata$play_type == 'run') *100
   ) %>%
   arrange(posteam,
           -plays
   ) %>%
   mutate(rushShare = plays / sum(plays) * 100) %>%
   filter(rusher == 'J.Dobbins' | rusher == 'D.Swift')

#big plays
bigPlays <- data %>% 
   filter((rusher =='J.Dobbins' | rusher =='D.Swift')
   ) %>%
   select(rusher, yards_gained) %>%
   mutate(playtype= case_when(
      yards_gained < 10 ~ '<10yds',
      yards_gained >= 10 & yards_gained < 20 ~ '10-19yds',
      yards_gained >= 20 ~ '20+ yds')
   ) %>%
   group_by(rusher, playtype) %>%
   count()

#big play comp by count
bigPlays %>% ggplot(aes(x= playtype, y=n)) +
   geom_bar(aes(fill=rusher), position='dodge',stat='identity') +
   scale_fill_manual(values = c("dodgerblue3", "purple3")) +
   xlab('yards gained') +
   ylab('plays')+
   theme_light()

#plotting the run play distribution by yardage
data %>% 
   filter((rusher =='J.Dobbins' | rusher =='D.Swift')) %>%
   ggplot(aes(x = yards_gained, y = rusher, fill=rusher)) +
   geom_joy(scale = 3) +
   theme_joy() +
   #scale_fill_manual(values=rep(c("dodgerblue3", "purple3"), length(rushing_stats$Rusher)/2)) +
   scale_fill_manual(values=c("dodgerblue3", "purple3"))+
   scale_y_discrete(expand = c(0.01, 0)) +
   scale_x_continuous(expand = c(0, 0)) +
   theme(legend.position="none") +
   labs(x="Yards gained per rush play" ,y="")

# avg score difference when used
data %>% 
   filter((rusher =='J.Dobbins' | rusher =='D.Swift')) %>%
   select(rusher,score_differential) %>%
   group_by(rusher) %>%
   summarize(mean_score_diff_usage = mean(score_differential))


# redzone carries
data_raw %>% 
   filter((fantasy =='J.Dobbins' | fantasy =='D.Swift'),
          yardline_100 <=20) %>%
   group_by(fantasy) %>%
   count()
#red zone TDs
data_raw %>% 
   filter((fantasy =='J.Dobbins' | fantasy=='D.Swift'),
          yardline_100 <=20,
          touchdown ==1) %>%
   group_by(fantasy) %>%
   count()

# g2g carries
data_raw %>% 
   filter((fantasy =='J.Dobbins' | fantasy =='D.Swift'),
          goal_to_go == 1) %>%
   group_by(fantasy) %>%
   count()
#g2g TDs
data_raw %>% 
   filter((fantasy =='J.Dobbins' | fantasy=='D.Swift'),
          goal_to_go == 1,
          touchdown ==1) %>%
   group_by(fantasy) %>%
   count()






