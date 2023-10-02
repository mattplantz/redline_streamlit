# relevant packages
import streamlit as st
import pandas as pd
import espnfantasyfootball as espn
import requests

#Streamlit formatting section
st.title("Red Line Data Wizard")
st.header("Good luck nerds")
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

matchup_response = requests.get(url, 
                                params={"leagueId" : league_id,
                                       "seasonId" : year,
                                       "matchupPeriodId" : week,
                                       "view": "mMatchup"},
                               cookies={"swid" : swid,
                                       "espn_s2" : espn_s2})

team_response = requests.get(url, 
                                params={"leagueId" : league_id,
                                       "seasonId" : year,
                                       "matchupPeriodId" : week,
                                       "view": "mTeam"},
                               cookies={"swid" : swid,
                                       "espn_s2" : espn_s2},)

# Transform the response into a json
matchup_json = matchup_response.json()
team_json = team_response.json()
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
for i, row in matchup_df.iterrows():
  if row.loc[i, 'Score1'] row.loc[i, 'Score2']:
    matchup_df.loc[i, 'Winner'] = matchup_df.loc[i, 'Team1']
  elif row['Score1'] < row['Score2']:
    matchup_df.loc[i, 'Winner'] = matchup_df.loc[i, 'Team2']
  else:
    matchup_df.loc[i, 'Winner'] = 'Somehow a tie'
def row_style(row):
    if row['Score1'] <= row['Score2']:
        return pd.Series('background-color: lightcoral', row.index)
    else:
        return pd.Series('background-color: limegreen', row.index)

st.dataframe(data = matchup_df.style.apply(row_style, axis=1, subset=['Score1','Score2']))


