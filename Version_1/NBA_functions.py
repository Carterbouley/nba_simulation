import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import collections

df = pd.read_csv('clean_df.csv')

def get_player_position_dict(team):
    
    
    # This function collects all the players names of the team, and inputs it into
    # A dictionary, along with each player prospective position.

    
    home_team_lineup = df.loc[(df['Tm'] == team) & (df['Date'] >= '2017-10-17 00:00:00')][['Player','Pos']]
    home_team_lineup = home_team_lineup.drop_duplicates().sort_values(by = 'Player')
    home_team_lineup_list = list(home_team_lineup['Player'])
    home_team_position_list = list(home_team_lineup['Pos'])
    team_player_position_dict = dict(zip(home_team_lineup_list, home_team_position_list ))
    
    return team_player_position_dict
    

def player_total_points_func(home_team, away_team):
    
    #This function generates builds normal distributions for various attributing offensive factors to points scoring for each player, such as time played and points scored per minute. It also looks at defensive factors, such as how much the opposting team is conceding in general from players in these repective positions. It then randomly selects, from those distributions (based on their probabilities of occuring) and the final number is an average of these two offensive and defensive factors. 
    
    # Collect player names of the home_team

    home_team_player_position_dict = get_player_position_dict(home_team)
    home_team_lineup_list = (home_team_player_position_dict.keys())
    
     # Collect player names of the away_team

    away_team_player_position_dict = get_player_position_dict(away_team)
    away_team_lineup_list = (away_team_player_position_dict.keys())
    
    home_player_scores_dict = {}
    
    for x in home_team_lineup_list:
        
        # How long an individual home team player plays at home
    
        home_minutes_played = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['MP'].mean(),
                                          df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['MP'].std())
        
        # How effective they are at scoring points at home
        home_player_scoring_effectiveness =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['scoring_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['scoring_rate'].std())

    # How often does the team that is away concede when they are away, broken down by location
    # Note here location is also technically 'home' because we are looking at them as an Opp
    
        away_conceding_avg = pd.DataFrame(df.loc[(df['Opp'] == away_team)
                                                 & (df['Location'] == 'Home')].groupby('Pos').mean()).reset_index()
        away_conceding_std = pd.DataFrame(df.loc[(df['Opp'] == away_team) & (df['Location'] == 'Home')].groupby('Pos').std()).reset_index()

        away_concede_by_position_avg = away_conceding_avg.loc[away_conceding_avg['Pos'] == home_team_player_position_dict[x]]['PTS']
        away_concede_by_position_std = away_conceding_std.loc[away_conceding_std['Pos'] == home_team_player_position_dict[x]]['PTS']

        away_positional_conceding = np.random.normal(away_concede_by_position_avg, away_concede_by_position_std)
        
             
        # Force negatives to be 0
        parameters = [home_minutes_played, home_player_scoring_effectiveness, away_positional_conceding]
        parameters = [0 if x<= 0 else x for x in parameters]
        
        # Convert to integer as we cannot score 0.5 points
        try:
            home_player_score = int((((parameters[0] * parameters[1]) + parameters[2])/2))
        except:
            home_player_score = 'NA'
        home_player_scores_dict[x] = home_player_score
        
    # Same for the Away Team
        
    away_player_scores_dict = {}    
    for x in away_team_lineup_list:

        # How long an individual away team player plays
        away_minutes_played = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['MP'].mean(),
                                          df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['MP'].std())
        # How effective they are at scoring points
        away_player_scoring_effectiveness =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['scoring_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['scoring_rate'].std())

        
    # How often does the team that is home concede when they are home 
    # Note here location is also technically 'away' because we are looking at them as an Opp
        home_conceding_avg = pd.DataFrame(df.loc[(df['Opp'] == home_team) & (df['Location'] == 'Away')].groupby('Pos').mean()).reset_index()
        home_conceding_std = pd.DataFrame(df.loc[(df['Opp'] == home_team) & (df['Location'] == 'Away')].groupby('Pos').std()).reset_index()

        home_concede_by_position_avg = home_conceding_avg.loc[home_conceding_avg['Pos'] == away_team_player_position_dict[x]]['PTS']
        home_concede_by_position_std = home_conceding_std.loc[home_conceding_std['Pos'] == away_team_player_position_dict[x]]['PTS']

        home_positional_conceding = np.random.normal(home_concede_by_position_avg, home_concede_by_position_std)
        
        # Force negatives to be 0
        
        parameters = [away_minutes_played, away_player_scoring_effectiveness, home_positional_conceding]
        parameters = [0 if x<= 0 else x for x in parameters]
        
        try:
            away_player_score = int((((parameters[0] * parameters[1]) + parameters[2])/2))
        except:
            away_player_score = 'NA'
            
        away_player_scores_dict[x] = away_player_score
        

    return home_player_scores_dict, away_player_scores_dict



def player_3Pers_func(home_team, away_team):
    
      #This function Performs similarly to the one above, but with the obvious focus on three pointers. Here with have data on attempts and % success, so this is included on the offensive & defensive stats.

    home_team_player_position_dict = get_player_position_dict(home_team)
    home_team_lineup_list = (home_team_player_position_dict.keys())
    
     # Collect player names of the away_team

    away_team_player_position_dict = get_player_position_dict(away_team)
    away_team_lineup_list = (away_team_player_position_dict.keys())

    home_player_3P_dict = {}
    
    for x in home_team_lineup_list:
        
        # How long an individual home team player plays
        
        home_minutes_played = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['MP'].mean(),
                                          df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['MP'].std())
        # How effective they are at scoring 3pointers points by time
        
        home_player_3per_scoring_effectiveness_by_minute =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['3p_scoring_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['3p_scoring_rate'].std())
        # How many attempts they make
        
        home_player_3PA = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['3PA'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['3PA'].std())
        # How many of those attempts go in
        
        home_player_3Ppcnt = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['3P%'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['3P%'].std())

    # How often does the team that is away concede when they are away by position
    # Note here location is also technically 'home' because we are looking at them as an Opp
    
        away_conceding_avg = pd.DataFrame(df.loc[(df['Opp'] == away_team) & (df['Location'] == 'Home')].groupby('Pos').mean()).reset_index()
        away_conceding_std = pd.DataFrame(df.loc[(df['Opp'] == away_team) & (df['Location'] == 'Home')].groupby('Pos').std()).reset_index()

        away_concede_3P_by_position_avg = away_conceding_avg.loc[away_conceding_avg['Pos'] == home_team_player_position_dict[x]]['3P']
        away_concede_3P_by_position_std = away_conceding_std.loc[away_conceding_std['Pos'] == home_team_player_position_dict[x]]['3P']

        away_positional_3P_conceding = np.random.normal(away_concede_3P_by_position_avg, away_concede_3P_by_position_std)
        
        away_concede_3PA_by_position_avg = away_conceding_avg.loc[away_conceding_avg['Pos'] == home_team_player_position_dict[x]]['3PA']
        away_concede_3PA_by_position_std = away_conceding_std.loc[away_conceding_std['Pos'] == home_team_player_position_dict[x]]['3PA']
            
        away_concede_3Ppcnt_by_position_avg = away_conceding_avg.loc[away_conceding_avg['Pos'] == home_team_player_position_dict[x]]['3P%']
        away_concede_3Ppcnt_by_position_std = away_conceding_std.loc[away_conceding_std['Pos'] == home_team_player_position_dict[x]]['3P%']
        
        away_positional_3PA_conceding = np.random.normal(away_concede_3PA_by_position_avg, away_concede_3PA_by_position_std)
        away_positional_3Ppcnt_coneding = np.random.normal(away_concede_3Ppcnt_by_position_avg, away_concede_3Ppcnt_by_position_std)
                                                        
        
             
        # Force negatives to be 0
        parameters = [home_minutes_played, home_player_3per_scoring_effectiveness_by_minute, home_player_3PA, home_player_3Ppcnt, away_positional_3P_conceding, away_positional_3PA_conceding, away_positional_3Ppcnt_coneding]
        parameters = [0 if x<= 0 else x for x in parameters]
        
        
        try:
            player_3pts = int((((parameters[0] * parameters[1]) + (parameters[2] * parameters[3]))) + (parameters[4]) + (parameters[5] * parameters[6])/4)
        except:
            player_3pts = 'NA'
        
        home_player_3P_dict[x] = player_3pts
    
    away_player_3P_dict = {}
    
    for x in away_team_lineup_list:
        
        # How long an individual home team player plays
        away_minutes_played = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['MP'].mean(),
                                          df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['MP'].std())
        # How effective they are at scoring 3pointers points by time
        away_player_3per_scoring_effectiveness_by_minute =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['3p_scoring_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['3p_scoring_rate'].std())
        # How many attempts they make
        away_player_3PA = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['3PA'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['3PA'].std())
        # How many of those attempts go in
        away_player_3Ppcnt = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['3P%'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['3P%'].std())

    # How often does the team that is away concede when they are away by position
    # Note here location is also technically 'home' because we are looking at them as an Opp
    
        home_conceding_avg = pd.DataFrame(df.loc[(df['Opp'] == home_team) & (df['Location'] == 'Away')].groupby('Pos').mean()).reset_index()
        home_conceding_std = pd.DataFrame(df.loc[(df['Opp'] == home_team) & (df['Location'] == 'Away')].groupby('Pos').std()).reset_index()

        home_concede_3P_by_position_avg = home_conceding_avg.loc[home_conceding_avg['Pos'] == away_team_player_position_dict[x]]['3P']
        home_concede_3P_by_position_std = home_conceding_std.loc[home_conceding_std['Pos'] == away_team_player_position_dict[x]]['3P']

        home_positional_3P_conceding = np.random.normal(home_concede_3P_by_position_avg, home_concede_3P_by_position_std)
        
        home_concede_3PA_by_position_avg = home_conceding_avg.loc[home_conceding_avg['Pos'] == away_team_player_position_dict[x]]['3PA']
        home_concede_3PA_by_position_std = home_conceding_std.loc[home_conceding_std['Pos'] == away_team_player_position_dict[x]]['3PA']
        
        home_concede_3Ppcnt_by_position_avg = home_conceding_avg.loc[home_conceding_avg['Pos'] == away_team_player_position_dict[x]]['3P%']
        home_concede_3Ppcnt_by_position_std = home_conceding_std.loc[home_conceding_std['Pos'] == away_team_player_position_dict[x]]['3P%']
        
        
        home_positional_3PA_conceding = np.random.normal(home_concede_3PA_by_position_avg, home_concede_3PA_by_position_std)
        home_positional_3Ppcnt_coneding = np.random.normal(home_concede_3Ppcnt_by_position_avg, home_concede_3Ppcnt_by_position_std)
                                                        
        
             
        # Force negatives to be 0
        parameters = [away_minutes_played, away_player_3per_scoring_effectiveness_by_minute, away_player_3PA, away_player_3Ppcnt, home_positional_3P_conceding, home_positional_3PA_conceding, home_positional_3Ppcnt_coneding]
        parameters = [0 if x<= 0 else x for x in parameters]
        
        
        try:
            player_3pts = int((((parameters[0] * parameters[1]) + (parameters[2] * parameters[3]))) + (parameters[4]) + (parameters[5] * parameters[6])/4)
        except:
            player_3pts = 'NA'
            
        away_player_3P_dict[x] = player_3pts
        
    return home_player_3P_dict, away_player_3P_dict



def player_assists_func(home_team, away_team):
    
    # Collect player names of the home_team

    home_team_player_position_dict = get_player_position_dict(home_team)
    home_team_lineup_list = (home_team_player_position_dict.keys())
    
     # Collect player names of the away_team

    away_team_player_position_dict = get_player_position_dict(away_team)
    away_team_lineup_list = (away_team_player_position_dict.keys())
    
    home_player_assists_dict = {}
    
    for x in home_team_lineup_list:
        
        # How long an individual home team player plays
        home_minutes_played = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['MP'].mean(),
                                          df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['MP'].std())
        # How effective they are at generating assists
        home_player_assist_effectiveness_by_minute =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['assist_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['assist_rate'].std())
        
        # How often does the team that is away concede assists they are away by position
        # Note here location is also technically 'home' because we are looking at them as an Opp
    
        away_conceding_avg = pd.DataFrame(df.loc[(df['Opp'] == away_team) & (df['Location'] == 'Home')].groupby('Pos').mean()).reset_index()
        away_conceding_std = pd.DataFrame(df.loc[(df['Opp'] == away_team) & (df['Location'] == 'Home')].groupby('Pos').std()).reset_index()
        
        away_concede_assists_by_position_avg = away_conceding_avg.loc[away_conceding_avg['Pos'] == home_team_player_position_dict[x]]['AST']
        away_concede_assists_by_position_std = away_conceding_std.loc[away_conceding_std['Pos'] == home_team_player_position_dict[x]]['AST']
        
        away_positional_assist_conceding = np.random.normal(away_concede_assists_by_position_avg, away_concede_assists_by_position_std)

        
        # Force negatives to be 0
        parameters = [home_minutes_played, home_player_assist_effectiveness_by_minute, away_positional_assist_conceding ]
        parameters = [0 if x<= 0 else x for x in parameters]
        
        try:
            player_assists = int((((parameters[0] * parameters[1]) + parameters[2])/4))
        except:
            player_assists = 'NA'
            
        home_player_assists_dict[x] = player_assists
    
    away_player_assists_dict = {}
    
    for x in away_team_lineup_list:
        
        # How long an individual away team player plays
        away_minutes_played = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['MP'].mean(),
                                          df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['MP'].std())
        # How effective they are at generating assists
        away_player_assist_effectiveness_by_minute =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['assist_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['assist_rate'].std())
        
       
        # How often does the team that is away concede assists they are away by position
        # Note here location is also technically 'home' because we are looking at them as an Opp
    
        home_conceding_avg = pd.DataFrame(df.loc[(df['Opp'] == home_team) & (df['Location'] == 'Away')].groupby('Pos').mean()).reset_index()
        home_conceding_std = pd.DataFrame(df.loc[(df['Opp'] == home_team) & (df['Location'] == 'Away')].groupby('Pos').std()).reset_index()
        
        home_concede_assists_by_position_avg = home_conceding_avg.loc[home_conceding_avg['Pos'] == away_team_player_position_dict[x]]['AST']
        home_concede_assists_by_position_std = home_conceding_std.loc[home_conceding_std['Pos'] == away_team_player_position_dict[x]]['AST']
        
        home_positional_assist_conceding = np.random.normal(home_concede_assists_by_position_avg, home_concede_assists_by_position_std)

        
        # Force negatives to be 0
        parameters = [away_minutes_played, away_player_assist_effectiveness_by_minute, home_positional_assist_conceding]
        parameters = [0 if x<= 0 else x for x in parameters]
        
        
        try:
            player_assists = int((((parameters[0] * parameters[1]) + parameters[2])/4))
        except:
            player_assists = 'NA'
        
        away_player_assists_dict[x] = player_assists
        
    return home_player_assists_dict, away_player_assists_dict
                                     
def player_rebounds_func(home_team, away_team):
    
    # Collect player names of the home_team

    home_team_player_position_dict = get_player_position_dict(home_team)
    home_team_lineup_list = (home_team_player_position_dict.keys())
    
     # Collect player names of the away_team

    away_team_player_position_dict = get_player_position_dict(away_team)
    away_team_lineup_list = (away_team_player_position_dict.keys())
    
    home_player_rebounds_dict = {}
    
    for x in home_team_lineup_list:
        
        # How long an individual home team player plays
        home_minutes_played = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['MP'].mean(),
                                          df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['MP'].std())
        # How effective they are at generating assists
        home_player_orb_effectiveness_by_minute =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['orb_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['orb_rate'].std())
        
        home_player_drb_effectiveness_by_minute =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['drb_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['drb_rate'].std())
        
        # How often does the team that is away concede assists they are away by position
        # Note here location is also technically 'home' because we are looking at them as an Opp
    
        away_conceding_avg = pd.DataFrame(df.loc[(df['Opp'] == away_team) & (df['Location'] == 'Home')].groupby('Pos').mean()).reset_index()
        away_conceding_std = pd.DataFrame(df.loc[(df['Opp'] == away_team) & (df['Location'] == 'Home')].groupby('Pos').std()).reset_index()
        
        away_concede_drb_by_position_avg = away_conceding_avg.loc[away_conceding_avg['Pos'] == home_team_player_position_dict[x]]['DRB']
        away_concede_drb_by_position_std = away_conceding_std.loc[away_conceding_std['Pos'] == home_team_player_position_dict[x]]['DRB']
        
        away_positional_drb_conceding = np.random.normal(away_concede_drb_by_position_avg, away_concede_drb_by_position_std)
        
        away_concede_orb_by_position_avg = away_conceding_avg.loc[away_conceding_avg['Pos'] == home_team_player_position_dict[x]]['ORB']
        away_concede_orb_by_position_std = away_conceding_std.loc[away_conceding_std['Pos'] == home_team_player_position_dict[x]]['ORB']
        
        away_positional_orb_conceding = np.random.normal(away_concede_orb_by_position_avg, away_concede_orb_by_position_std)
        
        
        # Force negatives to be 0
        parameters = [home_minutes_played, home_player_orb_effectiveness_by_minute, home_player_drb_effectiveness_by_minute, away_positional_drb_conceding, away_positional_orb_conceding]
        parameters = [0 if x<= 0 else x for x in parameters]
        
        try: 
            player_rebounds = int((((parameters[0] * parameters[1]) + parameters[4])/2) + (((parameters[0] * parameters[2]) + parameters[3])/2))
        except:
            player_rebounds = 'NA'
        
        home_player_rebounds_dict[x] = player_rebounds
        
    
    away_player_rebounds_dict = {}
        
    for x in away_team_lineup_list:
        
        # How long an individual home team player plays
        away_minutes_played = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['MP'].mean(),
                                          df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['MP'].std())
        # How effective they are at generating assists
        away_player_orb_effectiveness_by_minute =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['orb_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['orb_rate'].std())
        
        away_player_drb_effectiveness_by_minute =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['drb_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['drb_rate'].std())
        
        
        ##
        
        # How often does the team that is away concede assists they are away by position
        # Note here location is also technically 'home' because we are looking at them as an Opp
    
        home_conceding_avg = pd.DataFrame(df.loc[(df['Opp'] == home_team) & (df['Location'] == 'Away')].groupby('Pos').mean()).reset_index()
        home_conceding_std = pd.DataFrame(df.loc[(df['Opp'] == home_team) & (df['Location'] == 'Away')].groupby('Pos').std()).reset_index()
        
        home_concede_drb_by_position_avg = home_conceding_avg.loc[home_conceding_avg['Pos'] == away_team_player_position_dict[x]]['DRB']
        home_concede_drb_by_position_std = home_conceding_std.loc[home_conceding_std['Pos'] == away_team_player_position_dict[x]]['DRB']
        
        home_positional_drb_conceding = np.random.normal(home_concede_drb_by_position_avg, home_concede_drb_by_position_std)
        
        home_concede_orb_by_position_avg = home_conceding_avg.loc[home_conceding_avg['Pos'] == away_team_player_position_dict[x]]['ORB']
        home_concede_orb_by_position_std = home_conceding_std.loc[home_conceding_std['Pos'] == away_team_player_position_dict[x]]['ORB']
        
        home_positional_orb_conceding = np.random.normal(home_concede_orb_by_position_avg, home_concede_orb_by_position_std)
        
        
        # Force negatives to be 0
        
        parameters = [away_minutes_played, away_player_orb_effectiveness_by_minute, away_player_drb_effectiveness_by_minute, home_positional_drb_conceding, home_positional_orb_conceding]
        parameters = [0 if x <= 0 else x for x in parameters]
        
        try: 
            player_rebounds = int((((parameters[0] * parameters[1]) + parameters[4])/2) + (((parameters[0] * parameters[2]) + parameters[3])/2))
        except:
            player_rebounds = 'NA'
        
        
        away_player_rebounds_dict[x] = player_rebounds
    
    return home_player_rebounds_dict, away_player_rebounds_dict

def player_steals_func(home_team, away_team):
    
    # Collect player names of the home_team

    home_team_player_position_dict = get_player_position_dict(home_team)
    home_team_lineup_list = (home_team_player_position_dict.keys())
    
     # Collect player names of the away_team

    away_team_player_position_dict = get_player_position_dict(away_team)
    away_team_lineup_list = (away_team_player_position_dict.keys())
    
    home_player_steals_dict = {}
    
    
    for x in home_team_lineup_list:
        # How long an individual home team player plays
        home_minutes_played = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['MP'].mean(),
                                          df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['MP'].std())
        # How effective they are at generating steals
        home_player_steal_effectiveness_by_minute =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['steal_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['steal_rate'].std())
        
        # How often does the team that is away concede steals they are away by position
        # Note here location is also technically 'home' because we are looking at them as an Opp
    
        away_conceding_avg = pd.DataFrame(df.loc[(df['Opp'] == away_team) & (df['Location'] == 'Home')].groupby('Pos').mean()).reset_index()
        away_conceding_std = pd.DataFrame(df.loc[(df['Opp'] == away_team) & (df['Location'] == 'Home')].groupby('Pos').std()).reset_index()
        
        away_concede_stl_by_position_avg = away_conceding_avg.loc[away_conceding_avg['Pos'] == home_team_player_position_dict[x]]['STL']
        away_concede_stl_by_position_std = away_conceding_std.loc[away_conceding_std['Pos'] == home_team_player_position_dict[x]]['STL']
        
        away_positional_stl_conceding = np.random.normal(away_concede_stl_by_position_avg, away_concede_stl_by_position_std)
        
        # Force negatives to be 0
        parameters = [home_minutes_played, home_player_steal_effectiveness_by_minute, away_positional_stl_conceding]
        parameters = [0 if x<= 0 else x for x in parameters]
        
        try: 
            player_steals = int((((parameters[0] * parameters[1]) + parameters[2])/2))
        except:
            player_steals = 'NA'
        
        home_player_steals_dict[x] = player_steals
        
        
    away_player_steals_dict = {}  
    
    for x in away_team_lineup_list:
        # How long an individual home team player plays
        away_minutes_played = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['MP'].mean(),
                                          df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['MP'].std())
        # How effective they are at generating steals
        away_player_steal_effectiveness_by_minute =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['steal_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['steal_rate'].std())
        
        # How often does the team that is away concede steals they are away by position
        # Note here location is also technically 'home' because we are looking at them as an Opp
    
        home_conceding_avg = pd.DataFrame(df.loc[(df['Opp'] == home_team) & (df['Location'] == 'Away')].groupby('Pos').mean()).reset_index()
        home_conceding_std = pd.DataFrame(df.loc[(df['Opp'] == home_team) & (df['Location'] == 'Away')].groupby('Pos').std()).reset_index()
        
        home_concede_stl_by_position_avg = home_conceding_avg.loc[home_conceding_avg['Pos'] == away_team_player_position_dict[x]]['STL']
        home_concede_stl_by_position_std = home_conceding_std.loc[home_conceding_std['Pos'] == away_team_player_position_dict[x]]['STL']
        
        home_positional_stl_conceding = np.random.normal(home_concede_stl_by_position_avg, home_concede_stl_by_position_std)
        
        # Force negatives to be 0
        parameters = [away_minutes_played, away_player_steal_effectiveness_by_minute, home_positional_stl_conceding]
        parameters = [0 if x<= 0 else x for x in parameters]
        
        try: 
            player_steals = int((((parameters[0] * parameters[1]) + parameters[2])/2))
        except:
            player_steals = 'NA'
        
        away_player_steals_dict[x] = player_steals
        
    return home_player_steals_dict, away_player_steals_dict
 
    
def player_blocks_func(home_team, away_team):
    
    # Collect player names of the home_team

    home_team_player_position_dict = get_player_position_dict(home_team)
    home_team_lineup_list = (home_team_player_position_dict.keys())
    
    # Collect player names of the away_team

    away_team_player_position_dict = get_player_position_dict(away_team)
    away_team_lineup_list = (away_team_player_position_dict.keys())
    
    home_player_blocks_dict = {}
    
    for x in home_team_lineup_list:
    
        # How long an individual home team player plays
        home_minutes_played = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['MP'].mean(),
                                              df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['MP'].std())
        # How effective they are at generating blocks
        home_player_blk_effectiveness_by_minute =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['block_rate'].mean()
                         ,df.loc[(df['Player'] == x) & (df['Location'] =='Home')]['block_rate'].std())

        # How often does the team that is away concede steals they are away by position
        # Note here location is also technically 'home' because we are looking at them as an Opp

        away_conceding_avg = pd.DataFrame(df.loc[(df['Opp'] == away_team) & (df['Location'] == 'Home')].groupby('Pos').mean()).reset_index()
        away_conceding_std = pd.DataFrame(df.loc[(df['Opp'] == away_team) & (df['Location'] == 'Home')].groupby('Pos').std()).reset_index()

        away_concede_blk_by_position_avg = away_conceding_avg.loc[away_conceding_avg['Pos'] == home_team_player_position_dict[x]]['BLK']
        away_concede_blk_by_position_std = away_conceding_std.loc[away_conceding_std['Pos'] == home_team_player_position_dict[x]]['BLK']

        away_positional_blk_conceding = np.random.normal(away_concede_blk_by_position_avg, away_concede_blk_by_position_std)

        # Force negatives to be 0
        parameters = [home_minutes_played, home_player_blk_effectiveness_by_minute, away_positional_blk_conceding]
        parameters = [0 if x<= 0 else x for x in parameters]

        try: 
            player_blocks = int((((parameters[0] * parameters[1]) + parameters[2])/2))
        except:
            player_blocks = 'NA'

        home_player_blocks_dict[x] = player_blocks
        
        
    away_player_blocks_dict = {}  
    
    for x in away_team_lineup_list:
        
        # How long an individual home team player plays
        away_minutes_played = np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['MP'].mean(),
                                          df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['MP'].std())
        # How effective they are at generating blocks
        away_player_blk_effectiveness_by_minute =  np.random.normal(df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['block_rate'].mean()
                     ,df.loc[(df['Player'] == x) & (df['Location'] =='Away')]['block_rate'].std())
        
        # How often does the team that is away concede steals they are away by position
        # Note here location is also technically 'home' because we are looking at them as an Opp
    
        home_conceding_avg = pd.DataFrame(df.loc[(df['Opp'] == home_team) & (df['Location'] == 'Away')].groupby('Pos').mean()).reset_index()
        home_conceding_std = pd.DataFrame(df.loc[(df['Opp'] == home_team) & (df['Location'] == 'Away')].groupby('Pos').std()).reset_index()
        
        home_concede_blk_by_position_avg = home_conceding_avg.loc[home_conceding_avg['Pos'] == away_team_player_position_dict[x]]['BLK']
        home_concede_blk_by_position_std = home_conceding_std.loc[home_conceding_std['Pos'] == away_team_player_position_dict[x]]['BLK']
        
        home_positional_blk_conceding = np.random.normal(home_concede_blk_by_position_avg, home_concede_blk_by_position_std)
        
        # Force negatives to be 0
        parameters = [away_minutes_played, away_player_blk_effectiveness_by_minute, home_positional_blk_conceding]
        parameters = [0 if x<= 0 else x for x in parameters]
        
        try: 
            player_blocks = int((((parameters[0] * parameters[1]) + parameters[2])/2))
        except:
            player_blocks = 'NA'
        
        away_player_blocks_dict[x] = player_blocks
        
    return home_player_blocks_dict, away_player_blocks_dict

def get_player_score(player, home_team, away_team, x, ns, display = True):
    
    player_score = {}
    for i in range(ns):
        score = player_total_points_func(home_team, away_team)[x][player]
        
        if score in player_score:
                player_score[score] += 1
        else:
                player_score[score] = 1
                
    probability_sum = 0
    for k, v in player_score.items():
        player_score[k] = round(((v/ns)), 2)
        probability_sum += v/ns
    if display == True:
        
        od1 = collections.OrderedDict(sorted(player_score.items()))
        for k, v in od1.items(): print('Player: {} Score: {} : {}'.format(player, k, v))
    else:
        pass
    return player_score

def get_player_3P(player, home_team, away_team, x, ns, display = True):
    
    player_score = {}
    for i in range(ns):
        score = player_3Pers_func(home_team, away_team)[x][player]
        
        if score in player_score:
                player_score[score] += 1
        else:
                player_score[score] = 1
                
    probability_sum = 0
    for k, v in player_score.items():
        player_score[k] = round(((v/ns)), 2)
        probability_sum += v/ns
    if display == True:
        
        od1 = collections.OrderedDict(sorted(player_score.items()))
        for k, v in od1.items(): print('Player: {} 3 Pointers: {} : {}'.format(player, k, v))
    else:
        pass
    return player_score

def get_player_assists(player, home_team, away_team, x, ns, display = True):
    
    player_score = {}
    for i in range(ns):
        score = player_assists_func(home_team, away_team)[x][player]
        
        if score in player_score:
                player_score[score] += 1
        else:
                player_score[score] = 1
                
    probability_sum = 0
    for k, v in player_score.items():
        player_score[k] = round(((v/ns)), 2)
        probability_sum += v/ns
    if display == True:
        
        od1 = collections.OrderedDict(sorted(player_score.items()))
        for k, v in od1.items(): print('Player: {} Assists: {} : {}'.format(player, k, v))
    else:
        pass
    return player_score

def get_player_rebounds(player, home_team, away_team, x, ns, display = True):
    
    player_score = {}
    for i in range(ns):
        score = player_rebounds_func(home_team, away_team)[x][player]
        
        if score in player_score:
                player_score[score] += 1
        else:
                player_score[score] = 1
                
    probability_sum = 0
    for k, v in player_score.items():
        player_score[k] = round(((v/ns)), 2)
        probability_sum += v/ns
    if display == True:
        
        od1 = collections.OrderedDict(sorted(player_score.items()))
        for k, v in od1.items(): print('Player: {} Rebounds: {} : {}'.format(player, k, v))
    else:
        pass
    return player_score

def get_player_steals(player, home_team, away_team, x, ns, display = True):
    
    player_score = {}
    for i in range(ns):
        score = player_steals_func(home_team, away_team)[x][player]
        
        if score in player_score:
                player_score[score] += 1
        else:
                player_score[score] = 1
                
    probability_sum = 0
    for k, v in player_score.items():
        player_score[k] = round(((v/ns)), 2)
        probability_sum += v/ns
    if display == True:
        
        od1 = collections.OrderedDict(sorted(player_score.items()))
        for k, v in od1.items(): print('Player: {} Steals: {} : {}'.format(player, k, v))
    else:
        pass
    return player_score

def get_player_blocks(player, home_team, away_team, x, ns, display = True):
    
    player_score = {}
    for i in range(ns):
        score = player_blocks_func(home_team, away_team)[x][player]
        
        if score in player_score:
                player_score[score] += 1
        else:
                player_score[score] = 1
                
    probability_sum = 0
    for k, v in player_score.items():
        player_score[k] = round(((v/ns)), 2)
        probability_sum += v/ns
    if display == True:
        
        od1 = collections.OrderedDict(sorted(player_score.items()))
        for k, v in od1.items(): print('Player: {} Blocks: {} : {}'.format(player, k, v))
    else:
        pass
    return player_score

def FullGameSim(home_team, away_team, ns, display):
    
    # Collect player names of the home_team

    home_team_player_position_dict = get_player_position_dict(home_team)
    home_team_lineup_list = (home_team_player_position_dict.keys())
    
    
    # Collect player names of the away_team

    away_team_player_position_dict = get_player_position_dict(away_team)
    away_team_lineup_list = (away_team_player_position_dict.keys())
    
    line_up_length = len(home_team_lineup_list) + len(away_team_lineup_list)
    
    home_gamesout = []
    home_full_team_score = {}
    home_full_team_3Pers = {}
    home_full_team_assists = {}
    home_full_team_rebounds = {}
    home_full_team_steals = {}
    home_full_team_blocks = {}
    
    away_gamesout = []
    away_full_team_score = {}
    away_full_team_3Pers = {}
    away_full_team_assists = {}
    away_full_team_rebounds = {}
    away_full_team_steals = {}
    away_full_team_blocks = {}
    
    progress = 0
    
    for player in home_team_lineup_list:

        
        print('Progress: {}%'.format(round((progress/(line_up_length*6))*100), 4))

        home_full_team_score[player] = get_player_score(player, home_team, away_team, 0, ns, display = display)
        progress += 1
        print('Progress: {}%'.format(round((progress/(line_up_length*6))*100), 4))
        
        home_full_team_3Pers[player] = get_player_3P(player, home_team, away_team, 0, ns, display = display)
        progress += 1
        print('Progress: {}%'.format(round((progress/(line_up_length*6))*100), 4))
        home_full_team_assists[player] = get_player_assists(player, home_team, away_team, 0, ns, display = display)
        progress += 1
        print('Progress: {}%'.format(round((progress/(line_up_length*6))*100), 4))
        home_full_team_rebounds[player] = get_player_rebounds(player, home_team, away_team, 0, ns, display = display)
        progress += 1
        print('Progress: {}%'.format(round((progress/(line_up_length*6))*100), 4))
        home_full_team_steals[player] = get_player_steals(player, home_team, away_team, 0, ns, display = display)
        progress += 1
        print('Progress: {}%'.format(round((progress/(line_up_length*6))*100), 4))
        home_full_team_blocks[player] = get_player_blocks(player, home_team, away_team, 0, ns, display = display)
        progress += 1
        print('Progress: {}%'.format((progress/line_up_length*6)*100))
    
    home_team_dicts = [home_full_team_score, home_full_team_3Pers, 
                       home_full_team_assists,home_full_team_rebounds, home_full_team_steals, home_full_team_blocks ]
     
    for player in away_team_lineup_list:
        
        print('Progress: {}%'.format(progress/line_up_length))
        
        away_full_team_score[player] = get_player_score(player, home_team, away_team, 1, ns, display = display)
        progress += 1
        print('Progress: {}%'.format(round((progress/(line_up_length*6))*100), 4))
        away_full_team_3Pers[player] = get_player_3P(player, home_team, away_team, 1, ns, display = display)
        progress += 1
        print('Progress: {}%'.format(round((progress/(line_up_length*6))*100), 4))
        away_full_team_assists[player] = get_player_assists(player, home_team, away_team, 1, ns, display = display)
        progress += 1
        print('Progress: {}%'.format(round((progress/(line_up_length*6))*100), 4))
        away_full_team_rebounds[player] = get_player_rebounds(player, home_team, away_team, 1, ns, display = display)
        progress += 1
        print('Progress: {}%'.format(round((progress/(line_up_length*6))*100), 4))
        away_full_team_steals[player] = get_player_steals(player, home_team, away_team, 1, ns, display = display)
        progress += 1
        print('Progress: {}%'.format(round((progress/(line_up_length*6))*100), 4))
        away_full_team_blocks[player] = get_player_blocks(player, home_team, away_team, 1, ns, display = display)
        progress += 1
        print('Progress: {}%'.format(round((progress/(line_up_length*6))*100), 4))
        
    
    away_team_dicts = [away_full_team_score, away_full_team_3Pers, 
                       away_full_team_assists,away_full_team_rebounds, away_full_team_steals, away_full_team_blocks ]
    
    
            
    return home_team_dicts, away_team_dicts

def get_player_point_lines(test_dict, n):
    
    total_df = pd.DataFrame(columns = ['player', 'points', 'points_probability', 'cumulative_points_probability','player_0.5_total_point_line'])
    for player in test_dict[n][0]:

        newer_df = pd.DataFrame.from_records([test_dict[n][0][player]])
        player_df = newer_df.T.reset_index()
        player_df = player_df.rename(columns={'index': 'points', 0: 'probability'})
        player_df['player'] = player
        player_df = player_df.sort_values(by = 'points')

        player_df['cumulative_points_probability'] = float(0)
        running_total = float(0)
        player_df.reset_index(drop= True, inplace = True)
        player_df['player_0.5_total_point_line'] = 0

        for i in range(0, len(player_df)):

            running_total += player_df['probability'][i]
            player_df['cumulative_points_probability'][i] = running_total

        player_df.loc[(player_df['cumulative_points_probability']-0.5).abs().argsort()[:1], 'player_0.5_total_point_line'] = player_df['points']

        total_df = pd.concat([total_df,player_df])

    total_point_line_output_df = total_df.loc[total_df['player_0.5_total_point_line'] != 0]

    total_point_line_output_df = total_point_line_output_df[['player', 'player_0.5_total_point_line', 'cumulative_points_probability']]

    return total_point_line_output_df

def get_player_3PT_lines(test_dict, n):
    
    total_df = pd.DataFrame(columns = ['player', '3P', '3P_probability', 'cumulative_3P_probability','player_0.5_3P_line'])
    
    for player in test_dict[n][1]:

        newer_df = pd.DataFrame.from_records([test_dict[n][1][player]])
        player_df = newer_df.T.reset_index()
        player_df = player_df.rename(columns={'index': '3P', 0: '3P_probability'})
        player_df['player'] = player
        player_df = player_df.sort_values(by = '3P')

        player_df['cumulative_3P_probability'] = float(0)
        running_total = float(0)
        player_df.reset_index(drop= True, inplace = True)
        player_df['player_0.5_3P_line'] = 'NA'

        for i in range(0, len(player_df)):

            running_total += player_df['3P_probability'][i]
            player_df['cumulative_3P_probability'][i] = running_total

        player_df.loc[(player_df['cumulative_3P_probability']-0.5).abs().argsort()[:1], 'player_0.5_3P_line'] = player_df['3P']

        total_df = pd.concat([total_df,player_df])

    total_df = total_df.loc[total_df['player_0.5_3P_line'] != 'NA']

    total_df = total_df[['player', 'player_0.5_3P_line', 'cumulative_3P_probability']]

    return total_df

def get_player_assist_lines(test_dict, n):
    
    total_df = pd.DataFrame(columns = ['player', 'Assists', 'Assist_probability', 'cumulative_assist_probability','player_0.5_assist_line'])
    
    for player in test_dict[n][2]:

        newer_df = pd.DataFrame.from_records([test_dict[n][2][player]])
        player_df = newer_df.T.reset_index()
        player_df = player_df.rename(columns={'index': 'Assists', 0: 'Assist_probability'})
        player_df['player'] = player
        player_df = player_df.sort_values(by = 'Assists')

        player_df['cumulative_assist_probability'] = float(0)
        running_total = float(0)
        player_df.reset_index(drop= True, inplace = True)
        player_df['player_0.5_assist_line'] = 'NA'

        for i in range(0, len(player_df)):

            running_total += player_df['Assist_probability'][i]
            player_df['cumulative_assist_probability'][i] = running_total

        player_df.loc[(player_df['cumulative_assist_probability']-0.5).abs().argsort()[:1], 'player_0.5_assist_line'] = player_df['Assists']

        total_df = pd.concat([total_df,player_df])

    total_df = total_df.loc[total_df['player_0.5_assist_line'] != 'NA']

    total_df = total_df[['player', 'player_0.5_assist_line', 'cumulative_assist_probability']]

    return total_df

def get_player_rebound_lines(test_dict, n):
    
    total_df = pd.DataFrame(columns = ['player', 'Rebounds', 'Rebound_probability', 'cumulative_rebound_probability','player_0.5_rebound_line'])
    
    for player in test_dict[n][3]:

        newer_df = pd.DataFrame.from_records([test_dict[n][3][player]])
        player_df = newer_df.T.reset_index()
        player_df = player_df.rename(columns={'index': 'Rebounds', 0: 'Rebound_probability'})
        player_df['player'] = player
        player_df = player_df.sort_values(by = 'Rebounds')

        player_df['cumulative_rebound_probability'] = float(0)
        running_total = float(0)
        player_df.reset_index(drop= True, inplace = True)
        player_df['player_0.5_rebound_line'] = 'NA'

        for i in range(0, len(player_df)):

            running_total += player_df['Rebound_probability'][i]
            player_df['cumulative_rebound_probability'][i] = running_total

        player_df.loc[(player_df['cumulative_rebound_probability']-0.5).abs().argsort()[:1], 'player_0.5_rebound_line'] = player_df['Rebounds']

        total_df = pd.concat([total_df,player_df])

    total_df = total_df.loc[total_df['player_0.5_rebound_line'] != 'NA']

    total_df = total_df[['player', 'player_0.5_rebound_line', 'cumulative_rebound_probability']]

    return total_df


def get_player_steal_lines(test_dict, n):
    
    total_df = pd.DataFrame(columns = ['player', 'Steals', 'Steal_probability', 'cumulative_steal_probability','player_0.5_steal_line'])
    
    for player in test_dict[n][4]:

        newer_df = pd.DataFrame.from_records([test_dict[n][4][player]])
        player_df = newer_df.T.reset_index()
        player_df = player_df.rename(columns={'index': 'Steals', 0: 'Steal_probability'})
        player_df['player'] = player
        player_df = player_df.sort_values(by = 'Steals')

        player_df['cumulative_steal_probability'] = float(0)
        running_total = float(0)
        player_df.reset_index(drop= True, inplace = True)
        player_df['player_0.5_steal_line'] = 'NA'

        for i in range(0, len(player_df)):

            running_total += player_df['Steal_probability'][i]
            player_df['cumulative_steal_probability'][i] = running_total

        player_df.loc[(player_df['cumulative_steal_probability']-0.5).abs().argsort()[:1], 'player_0.5_steal_line'] = player_df['Steals']

        total_df = pd.concat([total_df,player_df])

    total_df = total_df.loc[total_df['player_0.5_steal_line'] != 'NA']

    total_df = total_df[['player', 'player_0.5_steal_line', 'cumulative_steal_probability']]

    return total_df

def get_player_block_lines(test_dict, n):
    
    total_df = pd.DataFrame(columns = ['player', 'Blocks', 'Block_probability', 'cumulative_block_probability','player_0.5_block_line'])
    
    for player in test_dict[n][5]:

        newer_df = pd.DataFrame.from_records([test_dict[n][5][player]])
        player_df = newer_df.T.reset_index()
        player_df = player_df.rename(columns={'index': 'Blocks', 0: 'Block_probability'})
        player_df['player'] = player
        player_df = player_df.sort_values(by = 'Blocks')

        player_df['cumulative_block_probability'] = float(0)
        running_total = float(0)
        player_df.reset_index(drop= True, inplace = True)
        player_df['player_0.5_block_line'] = 'NA'

        for i in range(0, len(player_df)):

            running_total += player_df['Block_probability'][i]
            player_df['cumulative_block_probability'][i] = running_total

        player_df.loc[(player_df['cumulative_block_probability']-0.5).abs().argsort()[:1], 'player_0.5_block_line'] = player_df['Blocks']

        total_df = pd.concat([total_df,player_df])

    total_df = total_df.loc[total_df['player_0.5_block_line'] != 'NA']

    total_df = total_df[['player', 'player_0.5_block_line', 'cumulative_block_probability']]

    return total_df

from functools import reduce

def final_game_line_df(test_dict, n):
    
    point_line_df = get_player_point_lines(test_dict, n)
    three_point_df = get_player_3PT_lines(test_dict, n)
    assist_df = get_player_assist_lines(test_dict, n)
    rebound_df = get_player_rebound_lines(test_dict, n)
    steal_df = get_player_steal_lines(test_dict, n)
    block_df = get_player_block_lines(test_dict, n)
    
    dfs = [point_line_df, three_point_df, assist_df, rebound_df, steal_df, block_df]
    
    df_final = reduce(lambda left,right: pd.merge(left,right,on='player'), dfs)
    
    return df_final
