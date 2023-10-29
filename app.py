from flask import Flask, render_template
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Define the fantasy teams
teams = {
    'Archie': ['Golden State Warriors', 'Milwaukee Bucks', 'Los Angeles Clippers', 'Dallas Mavericks', 'Houston Rockets'],
    'Boone': ['Miami Heat', 'Los Angeles Lakers', 'Sacramento Kings', 'Brooklyn Nets', 'Chicago Bulls'],
    'Theo': ['Denver Nuggets', 'Memphis Grizzlies', 'Oklahoma City Thunder', 'Utah Jazz', 'Charlotte Hornets'],
    'Mitch': ['Phoenix Suns', 'San Antonio Spurs', 'Indiana Pacers', 'Orlando Magic', 'Detroit Pistons'],
    'Bucky': ['Boston Celtics', 'Philadelphia 76ers', 'Cleveland Cavaliers', 'New Orleans Pelicans', 'Atlanta Hawks'],
    'Puh': ['Toronto Raptors', 'New York Knicks', 'Minnesota Timberwolves', 'Portland Trail Blazers', 'Washington Wizards']
}

# get NBA data from the web
data = pd.read_html('https://www.basketball-reference.com/leagues/NBA_2024_standings.html')

# create df
east = pd.DataFrame(data[0])
east = east.set_index('Eastern Conference', drop=True)
west = pd.DataFrame(data[1])
west = west.set_index('Western Conference', drop=True)
df = pd.concat([east, west])
df = df.sort_values('W', ascending=False)
df['NBA rank'] = range(1, len(df) + 1)
rank = df.pop('NBA rank')
df.insert(0, 'NBA rank', rank)
# Remove any "*" from index names
df.index = df.index.str.replace(r'\(.*\)', '', regex=True)
df.index = df.index.str.replace('*', '', regex=False)

# Initialize a new DataFrame for the custom standings
custom_standings = pd.DataFrame(columns=['W', 'L', 'PS/G', 'PA/G'])

df['Team'] = df.index
df['Team'] = df['Team'].str.replace('\xa0', '')

# Calculate the combined W - L totals, PS/G, and PA/G for each group of teams
for team, team_list in teams.items():
    custom_standings.loc[team, 'W'] = df.loc[df['Team'].isin(team_list), 'W'].sum()
    custom_standings.loc[team, 'L'] = df.loc[df['Team'].isin(team_list), 'L'].sum()
    custom_standings.loc[team, 'PS/G'] = df.loc[df['Team'].isin(team_list), 'PS/G'].mean()
    custom_standings.loc[team, 'PA/G'] = df.loc[df['Team'].isin(team_list), 'PA/G'].mean()

# Convert W and L to int for calculations
custom_standings['W'] = custom_standings['W'].astype(int)
custom_standings['L'] = custom_standings['L'].astype(int)

# Calculate and format Win % with 3 decimals
custom_standings['Win %'] = custom_standings['W'] / (custom_standings['W'] + custom_standings['L'])
custom_standings['Win %'] = custom_standings['Win %'].apply(lambda x: round(x, 3))

# Sort custom_standings by "Win %" in descending order
custom_standings = custom_standings.sort_values('Win %', ascending=False)

pd.options.display.float_format = "{:.3f}".format
now = datetime.now()
now = now.strftime("%Y-%m-%d %H:%M")
line = "=" * 55
print(line)
print(f"Statistics are current as the latest www.basketball-reference.com update checked at {now}")
print()
print("Win % Standings")
print()
print(custom_standings[['W', 'L', 'Win %']])

# Calculate and print average PS/G for each team in the same order as Win %
average_psg = custom_standings[['PS/G']].copy()
average_psg.sort_values('PS/G', ascending=False, inplace=True)

print("Average PS/G Standings")
print()
print(average_psg.to_string(index=True))  # Keep index in the output
print(line)

# Calculate and print average PA/G for each team in the same order as Win %
average_pag = custom_standings[['PA/G']].copy()
average_pag.sort_values('PA/G', ascending=True, inplace=True)

print("Average PA/G Standings")
print()
print(average_pag.to_string(index=True))  # Keep index in the output
print(line)

# Calculate and print standings for each team
for team, team_list in teams.items():
    team_standings = pd.DataFrame(columns=['Team', 'W', 'L', 'Win %', 'PS/G', 'PA/G'])
    team_standings['Team'] = team_list
    team_standings['W'] = df.loc[df['Team'].isin(team_list), 'W'].values
    team_standings['L'] = df.loc[df['Team'].isin(team_list), 'L'].values
    team_standings['Win %'] = team_standings['W'] / (team_standings['W'] + team_standings['L'])
    team_standings['PS/G'] = df.loc[df['Team'].isin(team_list), 'PS/G'].values
    team_standings['PA/G'] = df.loc[df['Team'].isin(team_list), 'PA/G'].values
    team_standings = team_standings.sort_values('Win %', ascending=False)


    print(f"\n{team}'s Trams")
    print()
    print(team_standings.to_string(index=False))
    print(line)
    
# Create a dictionary to store individual team statistics
team_stats = {}

# Calculate and store individual team statistics
for team, team_list in teams.items():
    team_standings = pd.DataFrame(columns=['Team', 'W', 'L', 'Win %', 'PS/G', 'PA/G'])
    team_standings['Team'] = team_list
    team_standings['W'] = df.loc[df['Team'].isin(team_list), 'W'].values
    team_standings['L'] = df.loc[df['Team'].isin(team_list), 'L'].values
    team_standings['Win %'] = team_standings['W'] / (team_standings['W'] + team_standings['L'])
    team_standings['PS/G'] = df.loc[df['Team'].isin(team_list), 'PS/G'].values
    team_standings['PA/G'] = df.loc[df['Team'].isin(team_list), 'PA/G'].values
    team_stats[team] = team_standings

@app.route('/')
def index():
    return render_template('index.html', custom_standings=custom_standings, average_psg=average_psg, average_pag=average_pag, team_stats=team_stats)

if __name__ == '__main__':
    app.run(debug=True)
