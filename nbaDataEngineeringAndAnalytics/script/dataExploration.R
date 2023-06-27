library(jsonlite)
library(dplyr)
library(DBI)
library(RPostgreSQL)

########################################
# DATA IMPORT
########################################

# json file paths inside the .Rproj enviro 
file_int_player <- "api_data_files\\international_box_player_season.json"
file_nba_player <- "api_data_files\\nba_box_player_season.json"
file_player <- "api_data_files\\player.json"

# reading the json files into memory
data_int_player <- read_json(file_int_player, simplifyVector = TRUE)
data_nba_player <- read_json(file_nba_player, simplifyVector = TRUE)
data_player <- read_json(file_player, simplifyVector = TRUE)

# converting the json to dataframes
df_ply <- as.data.frame(data_player)
df_int <- as.data.frame(data_int_player)
df_nba <- as.data.frame(data_nba_player)



# combining first and last names so that they can be cross checked against
# each json file. 
ply_names <- df_ply %>% 
    mutate(name = paste0(first_name, " ", last_name)) %>%
    select(name)
nba_names <- df_nba %>% 
    mutate(name = tolower(paste0(first_name, " ", last_name))) %>%
    select(name)
int_names <- df_int %>% 
    mutate(name = paste0(first_name, " ", last_name)) %>%
    select(name)

# this will return any values in the first input that are not present
# in the second input. 
setdiff(nba_names, ply_names)             
setdiff(int_names, ply_names)

# player and international JSON have no mismatches so they require no edits
# nba has mismatches due to including suffixes and full last names
# player and international only include the first part of the last name
# so I will adjust the nba data set to match that style by removing
# suffixes and any part of the last name after a space.  Example:
# "Van Willis" would become Van  and Geld Jr. would become Geld
# nba also is in camel case while the other 2 are all lower case. I 
# will lower nba to match the other 2


# fixing the last name issue and lowercasing NBA
df_nba <- df_nba %>%
    rowwise %>%
    mutate(last_name = strsplit(last_name, " ")[[1]][1])%>%
    as.data.frame() %>%
    mutate(last_name = tolower(last_name),
           first_name = tolower(first_name))

nba_names <- df_nba %>% 
    mutate(name = tolower(paste0(first_name, " ", last_name))) %>%
    select(name)

setdiff(nba_names, ply_names)


