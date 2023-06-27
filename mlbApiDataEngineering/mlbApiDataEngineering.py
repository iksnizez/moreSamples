import sqlite3, requests, sys
import pandas as pd
pd.set_option('display.max_columns', 500)
import numpy as np

def get_pitches(game_id, db_filepath = "gamefeed.db"):
    """
    retrieve all of the pitches for a single game from baseballsavant.mlb.com
    """
#############################
# CREATING/CONNECTING TO DB
#############################
    
    # sqlite3.connect will create the db at the file path if it does not exist
    # and if it does exist, it will only connect to it
    conn = sqlite3.connect(db_filepath)
    c = conn.cursor()

    # query to create the pitch table if it does not already exist
    sql_create_table = """
                        CREATE TABLE IF NOT EXISTS pitch (
                            play_id TEXT PRIMARY KEY,
                            inning INTEGER,
                            ab_number INTEGER,
                            outs INTEGER,
                            stand TEXT,
                            batter_name TEXT,
                            p_throws TEXT,
                            pitcher_name TEXT,
                            team_batting TEXT,
                            team_fielding TEXT,
                            result TEXT,
                            strikes INTEGER,
                            balls INTEGER,
                            pre_strikes INTEGER,
                            pre_balls INTEGER,
                            call_name TEXT,
                            pitch_type TEXT,
                            start_speed NUMERIC,
                            extension NUMERIC,
                            zone INTEGER,
                            spin_rate INTEGER,
                            hit_speed NUMERIC,
                            hit_distance INTEGER,
                            hit_angle INTEGER,
                            is_barrel INTEGER,
                            is_bip_out TEXT,
                            pitch_number INTEGER,
                            player_total_pitches INTEGER,
                            game_pk TEXT
                        );
                        """
    
    c.execute(sql_create_table)
    
    
    try:    
        # removing previous entries for the game_id if it exist in the db
        # I chose to overwrite existing game_ids with the assumption that
        # multiple runs on 1 game would be done to grab data corrections from baseballsavant
        game_id = str(game_id)

        remove_existing_game = "DELETE FROM pitch WHERE game_pk = {};".format(game_id)
        c.execute(remove_existing_game)


####################
# ACCESSING THE DATA
####################
        # baseballsavant endpoint that formats to include the provided game_id
        api_endpoint = "https://baseballsavant.mlb.com/gf?game_pk={}".format(game_id)
        
        # sending get request to api to retrieve the json data.
        # this will hold the all of the json data for the game_id
        raw_data = requests.get(api_endpoint).json()

        # plays is a list of lists containing the data for each play
        # it will become pitch_df and then sent to the SQL table
        plays = []

        ### looping through each play in the game. The plays are under separate keys in the JSON for the 
        ### team_home and team_away so the loop will be done twice.
        data_keys = ['team_home', 'team_away']

        for k in data_keys:
            for pitch in raw_data[k]:

                # pulling individual data points from the json. 
                # If one it not available it is assigned NaN or None
                keys = pitch.keys()

                play_id = pitch['play_id']
                
                if 'inning' in keys:
                    inning = pitch['inning']
                else:
                    inning = np.nan

                if 'ab_number' in keys:
                    ab_number = pitch['ab_number']
                else:
                    ab_number = np.nan

                if 'outs' in keys:
                    outs = pitch['outs']
                else:
                    outs = np.nan

                if 'stand' in keys:
                    stand = pitch['stand']
                else:
                    stand = None

                if 'batter_name' in keys:
                    batter_name = pitch['batter_name']
                else:
                    batter_name = None

                if 'p_throws' in keys:
                    p_throws = pitch['p_throws']
                else:
                    p_throws = None

                if 'pitcher_name' in keys:
                    pitcher_name = pitch['pitcher_name']
                else:
                    pitcher_name = None

                if 'team_batting' in keys:
                    team_batting = pitch['team_batting']
                else:
                    team_batting = None

                if 'team_fielding' in keys:
                    team_fielding = pitch['team_fielding']
                else:
                    team_fielding = None

                if 'result' in keys:
                    result = pitch['result']
                else:
                    result = None

                if 'strikes' in keys:
                    strikes = pitch['strikes']
                else:
                    strikes = np.nan

                if 'balls' in keys:
                    balls = pitch['balls']
                else:
                    balls = np.nan

                if 'pre_strikes' in keys:
                    pre_strikes = pitch['pre_strikes']
                else:
                    pre_strikes = np.nan

                if 'pre_balls' in keys:
                    pre_balls = pitch['pre_balls']
                else:
                    pre_balls = np.nan

                if 'call_name' in keys:
                    call_name = pitch['call_name']
                else:
                    call_name = None

                if 'pitch_type' in keys:
                    pitch_type = pitch['pitch_type']
                else:
                    pitch_type = None

                if 'start_speed' in keys:
                    start_speed = pitch['start_speed']
                else:
                    start_speed = np.nan

                if 'extension' in keys:
                    extension = pitch['extension']
                else:
                    extension = np.nan

                if 'zone' in keys:
                    zone = pitch['zone']
                else:
                    zone = np.nan

                if 'spin_rate' in keys:    
                    spin_rate = pitch['spin_rate']
                else:
                    spin_rate = np.nan

                if 'is_bip_out' in keys:    
                    is_bip_out = pitch['is_bip_out']
                else:
                    is_bip_out = None

                if 'pitch_number' in keys:    
                    pitch_number = pitch['pitch_number']
                else:
                    pitch_number = np.nan

                if 'player_total_pitches' in keys:    
                    player_total_pitches = pitch['player_total_pitches']
                else:
                    player_total_pitches = np.nan


                game_pk = pitch['game_pk']

                # single_play_data will hold the data for a single play and be appended to the plays list
                single_play_data = [play_id, inning, ab_number, outs, stand, batter_name,
                                    p_throws, pitcher_name, team_batting, team_fielding, result,
                                    strikes, balls, pre_strikes, pre_balls, call_name, pitch_type,
                                    start_speed, extension, zone, spin_rate, is_bip_out, pitch_number, 
                                    player_total_pitches, game_pk]

                # apend the single play data to the list of all plays
                plays.append(single_play_data)
                

        # pitch_df will initially hold the majority of the data from the individual pitch  
        # and will be merged with hits_df prior to the commit to the SQL table
        columns = ['play_id', 'inning', 'ab_number', 'outs', 'stand', 'batter_name', 'p_throws', 
                   'pitcher_name', 'team_batting', 'team_fielding', 'result', 'strikes', 'balls',
                   'pre_strikes', 'pre_balls', 'call_name', 'pitch_type', 'start_speed',
                   'extension', 'zone', 'spin_rate', 'is_bip_out', 'pitch_number', 
                   'player_total_pitches', 'game_pk']

        pitch_df = pd.DataFrame(plays, columns = columns)


        # retrieving the 4 data points for a hit that were missing from the json key  used above
        hits = [] 
        # checking for at least one record in exit_velocity 
        if len(raw_data['exit_velocity']) > 0:
            for hit in raw_data['exit_velocity']:

                play_id = hit['play_id']

                # testing the each hit play_id to see if the variables are returned.
                # if the variable is missing it is assigned NaN
                keys = hit.keys()
                if 'hit_speed' in keys:
                    hit_speed = hit['hit_speed']
                else:    
                    hit_speed = np.nan

                if 'hit_distance' in keys:
                    hit_distance = hit['hit_distance']
                else:    
                    hit_distance = np.nan    

                if 'hit_angle' in keys:
                    hit_angle = hit['hit_angle']
                else:    
                    hit_angle = np.nan    

                if 'is_barrel' in keys:
                    is_barrel = hit['is_barrel']
                else:    
                    is_barrel = None

                # single_hit_data will hold the data for single hit and be appended to the hits list
                single_hit_data = [play_id, hit_speed, hit_distance, hit_angle, is_barrel]

                # append the single hit data to the list of all hits
                hits.append(single_hit_data)
                
                
            # creating the hits df that will be merged with the pitch_df 
            columns2 = ['play_id','hit_speed', 'hit_distance', 'hit_angle', 'is_barrel']

            hits_df = pd.DataFrame(hits, columns = columns2)

            # merging the hit data back into pitch_df on the play_id
            pitch_df = pd.merge(pitch_df, hits_df, how="left", on=["play_id"])
            
            # rearranging the columns to match the instruction prompt
            column_order = ['play_id', 'inning', 'ab_number', 'outs', 'stand', 'batter_name', 'p_throws', 
                       'pitcher_name', 'team_batting', 'team_fielding', 'result', 'strikes', 'balls',
                       'pre_strikes', 'pre_balls', 'call_name', 'pitch_type', 'start_speed',
                       'extension', 'zone', 'spin_rate', 'hit_speed', 'hit_distance', 'hit_angle', 
                       'is_barrel', 'is_bip_out', 'pitch_number',  'player_total_pitches', 'game_pk']

            pitch_df = pitch_df[column_order]
        
        #if there are no play_ids in exit velocity then all 4 data points get np.nan in all the pitch records
        else:
            
            pitch_df['hit_speed'] = np.nan
            pitch_df['hit_distance'] = np.nan
            pitch_df['hit_angle'] = np.nan
            pitch_df['is_barrel'] = np.nan

            # rearranging the columns to match the instruction prompt
            column_order = ['play_id', 'inning', 'ab_number', 'outs', 'stand', 'batter_name', 'p_throws', 
                       'pitcher_name', 'team_batting', 'team_fielding', 'result', 'strikes', 'balls',
                       'pre_strikes', 'pre_balls', 'call_name', 'pitch_type', 'start_speed',
                       'extension', 'zone', 'spin_rate', 'hit_speed', 'hit_distance', 'hit_angle', 
                       'is_barrel', 'is_bip_out', 'pitch_number',  'player_total_pitches', 'game_pk']

            pitch_df = pitch_df[column_order]
        

###########################
# ADDING THE DATA TO THE DB
###########################

        # committing the data from the df to the db
        pitch_df.to_sql('pitch', con=conn, if_exists='append', index=False)

        # retrieving the number of rows added
        inserted_row_query = "SELECT COUNT(play_id) FROM pitch WHERE game_pk = {}".format(game_id)
        inserted_rows = c.execute(inserted_row_query).fetchone()

        # closing connection
        conn.close()

        # print a success message and return the number of rows added
        print("-----")
        print(str(inserted_rows[0]) + ' pitches inserted for game_id {} to the database {}'.format(game_id, db_filepath))
        print("-----")
        return inserted_rows[0]
    
    except Exception as ex:
        conn.close()
        print("\nThere was an error and no pitches from {} were added to the db.\n".format(game_id))
        print("-------\n")
        print("Error Message: {}".format(ex))
        print()
        return 

# handler for when the script is called directly through the command line
if __name__ == "__main__":
    # when only the game_id is provided
    if len(sys.argv) == 2:
        get_pitches(sys.argv[1])

    # when game ID and db name are provided
    elif len(sys.argv) == 3:
        get_pitches(sys.argv[1], sys.argv[2])

    # incorrect number of console arguments
    else: 
        print("\nThe first command line arguemnt should be the game_pk, the second is optional but should be a db file name  'dbName.db' if one is provided\n")
        print(">>>> Example command line: python Solution_JohnBrzezinski.py 635886")
        print(">>>> Example with 2nd arg: python Solution_JohnBrzezinski.py 635886 pitches.db\n")