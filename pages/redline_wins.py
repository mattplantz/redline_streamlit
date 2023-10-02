# relevant packages
import streamlit as st
import pandas as pd
import espnfantasyfootball as espn
import requests
import numpy as np

#Streamlit formatting section
st.title("Red Line Intra-League Wins")
matchup_df = None # need to establish this to avoid errors

# red line section - lots of clean up to do 
# pull in red line data
# red line secrets
swid = st.secrets['jt']
league_id = st.secrets['league_id']
year = st.secrets['year']
espn_s2 = st.secrets['espn']

# url for redline
url = f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}"
week = 4 # UDPATE TO DYNAMIC -- use date function and cut offs?

@st.cache
def matchup_response():
  response = requests.get(url, 
                                params={"leagueId" : league_id,
                                       "seasonId" : year,
                                       #"matchupPeriodId" : week,
                                       "view": "mMatchup"},
                               cookies={"swid" : swid,
                                       "espn_s2" : espn_s2})
  return response.json()

def team_response():
  response = requests.get(url, 
                                params={"leagueId" : league_id,
                                       "seasonId" : year,
                                       #"matchupPeriodId" : week,
                                       "view": "mTeam"},
                               cookies={"swid" : swid,
                                       "espn_s2" : espn_s2},)
  return response.json()
# Transform the response into a json
matchup_json = matchup_response()
team_json = team_response()
# Transform both of the json outputs into DataFrames
matchup_df = pd.json_normalize(matchup_json['schedule'])
team_df = pd.json_normalize(team_json['teams'])

# Define the column names needed
matchup_column_names = {
    'matchupPeriodId':'Week', 
    'away.teamId':'Team1', 
    'away.totalPoints':'Score1',
    'home.teamId':'Team2', 
    'home.totalPoints':'Score2',
}

team_column_names = {
    'id':'id',
    'location':'Name1',
    'nickname':'Name2'
}

# Reindex based on column names defined above
matchup_df = matchup_df.reindex(columns=matchup_column_names).rename(columns=matchup_column_names)
team_df = team_df.reindex(columns=team_column_names).rename(columns=team_column_names)

# team names
manager_dict = {1: 'Nolan'
              ,2: 'Matt'
              ,3: 'Josh'
              ,4: 'Michael'
              ,5: 'Andrew'
              ,6: 'Dylan'}

matchup_df.replace({"Team1": manager_dict
                  , "Team2" : manager_dict}
                  , inplace = True) 
matchup_df = matchup_df[matchup_df['Score1'] > 0]
matchup_df['Winner'] = np.where(matchup_df['Score1'] >= matchup_df['Score2'], matchup_df['Team1'], matchup_df['Team2'])

stats_df = pd.DataFrame(matchup_df['Winner'].value_counts())
stats_df = stats_df.rename(columns ={'Winner':'Player', 'count':'Inter-League Wins'})

st.dataframe(stats_df)
