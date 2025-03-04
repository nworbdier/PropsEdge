import requests
import csv

LEAGUE_TO_SPORT = {
    'NBA': 'BASKETBALL',
    'CBB': 'BASKETBALL',
    'WNBA': 'BASKETBALL',
    'NFL': 'FOOTBALL',
    'CFB': 'FOOTBALL',
    'NHL': 'HOCKEY',
    'MLB': 'BASEBALL',
    'CS': 'ESPORTS',
    'CLUBSOCCER': 'SOCCER'
}

def get_players():
    headers = {
        'Host': 'api.sleeper.app',
        'x-amp-session': '1724697278937',
        'accept': 'application/json',
        'authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdmF0YXIiOiIxNWQ3Y2YyNTliYzMwZWFiOGY2MTIwZjQ1ZjY1MmZiNiIsImRpc3BsYXlfbmFtZSI6IlNoYXdudGhlcmVhbHNoYWR5IiwiZXhwIjoxNzU2MjMzMzEyLCJpYXQiOjE3MjQ2OTczMTIsImlzX2JvdCI6ZmFsc2UsImlzX21hc3RlciI6ZmFsc2UsInJlYWxfbmFtZSI6bnVsbCwidXNlcl9pZCI6NzI5MjAyODc1NTk4Nzc0MjcyLCJ2YWxpZF8yZmEiOiJwaG9uZSJ9.hvc8FXdweWwNkBvrhCJ8ytRcBkX5ilDZa77IQtgleJM',
        'x-api-client': 'api.cached',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Sleeper/93.1.0 CFNetwork/1496.0.7 Darwin/23.5.0',
        'x-device-id': '71009696-F347-40AA-AE8C-5247A63041DF',
        'x-platform': 'ios',
        'x-build': '93.1.0',
        'x-bundle': 'com.blitzstudios.sleeperbot',
    }
    response = requests.get("https://api.sleeper.app/players", headers=headers)
    data = response.json()

    players_data = []
    for player_info in data:
        player_id = player_info.get('player_id')
        league = player_info.get('sport').upper()  # This is actually the league
        sport = LEAGUE_TO_SPORT.get(league, 'unknown')  # Map league to sport
        player_data = {
            'player_id': player_id,
            'league': league,
            'sport': sport,
            'first_name': player_info.get('first_name'),
            'last_name': player_info.get('last_name'),
        }
        players_data.append(player_data)

    csv_file = "sleeper_players.csv"
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['player_id', 'league', 'sport', 'first_name', 'last_name']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(players_data)
    except Exception as e:
        print(f"An error occurred: {e}")
        