library(jsonlite)
library(dplyr)
library(DBI)
library(RPostgreSQL)

####
# CONNECT TO DB #
########## DB is not active but the data is saved to the project/data folder #######
####
db creds 
db_user <- #
db_pw <- #
db_name <- #
db_port <- #
db_host <- #

# connecting to db
#tryCatch({
#    conn <- dbConnect(RPostgreSQL::PostgreSQL(), 
#                      dbname = db_name,
                      host = db_host, 
                      port = db_port,
                      user = db_user, 
                      password = db_pw
                      #user= rstudioapi::askForPassword("Database username"),
                      #password = rstudioapi::askForPassword("Database password")
    )
    print("Connected")
},
error=function(cond) {
    print("Unable to connect....")
})

####
# PROCESS JSON DATA, CLEAN SOME INCONSISTENCIES AND IMPORT TO DB #
####

table_names <- c("international_box_player_season",
                "nba_box_player_season",
                "player")

# looping thru each file, prepping it for db load, 
# and loading it to the existing db table in the provided db
lapply(table_names, function(table){
    
    # building the file path to the data in the project folder
    folder = "api_data_files\\"
    extension = ".json"
    file_path <- paste0(folder, table, extension)
    table_name = as.character(table)
    
    # reading in the json data to a dataframe
    json <- read_json(file_path, simplifyVector = TRUE)
    table <- as.data.frame(json)
    
    # standardizing first and last names to match across tables
    table <- table %>%
        rowwise %>%
        
        # it appears that the nba json has full last names and suffixes
        # while the other 2 jsons don't include suffixes, and only include
        # the first part of last names that have multiple names w/spaces.
        # this mutate() is removing the second parts of names and suffixes
        # in the nba json to match with the other 2 data sets.
        mutate(last_name = strsplit(last_name, " ")[[1]][1]) %>%
        as.data.frame() %>%
        
        # setting all names to lowercase for matching across tables
        mutate(
            first_name = tolower(first_name),
            last_name = tolower(last_name)
        )
    
    
    # some percentages are in decimal form and some are in percent
    # converting all of them to be in percent form
    if(table_name != 'player'){
        table <- table %>% 
            mutate(
                true_shooting_percentage = true_shooting_percentage * 100,
                three_point_attempt_rate = three_point_attempt_rate * 100,
                free_throw_rate = free_throw_rate * 100
            )
    }
    
    # appending the data to the existing db tables with same name
    # as the json files
    dbWriteTable(conn, 
                 table_name, 
                 table,
                 row.names = FALSE,
                 append = TRUE)
    
})

dbDisconnect(conn)
