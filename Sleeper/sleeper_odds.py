import requests
import csv
import datetime

# League to sport mapping
LEAGUE_TO_SPORT = {
    'NBA': 'BASKETBALL',
    'CBB': 'BASKETBALL',
    'WNBA': 'BASKETBALL',
    'NFL': 'FOOTBALL',
    'CFB': 'FOOTBALL',
    'NHL': 'HOCKEY',
    'MLB': 'BASEBALL',
    'CS': 'ESPORTS',
}


STAT_MAP = {
    'assists': 'Player Assists',
    'double_double': 'Player Double Double',
    'first_qtr_points': 'Player Points Q1',
    'points': 'Player Points',
    'points_and_assists': 'Player Points + Assists',
    'points_and_rebounds': 'Player Points + Rebounds',
    'pts_reb_ast': 'Player Points + Assists + Rebounds',
    'rebounds': 'Player Rebounds',
    'rebounds_and_assists': 'Player Rebounds + Assists',
    'threes_made': 'Player Threes',
    'steals': 'Player Steals',
    'turnovers': 'Player Turnovers',
    'first_qtr_assists': 'Player Assists Q1',
    'first_qtr_rebounds': 'Player Rebounds Q1',
    'blocks_and_steals': 'Player Blocks + Steals',
    'blocks': 'Player Blocks',
    'goals': 'Player Goals',
    'shots': 'Player Shots',
    'blocked_shots': 'Player Blocked Shots',
    'powerplay_points': 'Player Power Play Points',
    'headshots_maps_1_2': 'Player Headshops Map 1 + 2',
    'kills_maps_1_2': 'Player Kills Map 1 + 2',
}


def get_player_names_from_csv(csv_file="sleeper_players.csv"):
    player_names = {}
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                player_id = row.get('player_id')
                league = row.get('league')  # Changed from sport to league
                first_name = row.get('first_name')
                last_name = row.get('last_name')
                position = row.get('position')
                if player_id and league:
                    # Create a composite key using both player_id and league
                    key = (str(player_id), league)
                    player_names[key] = (first_name, last_name, position)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found.")
    except Exception as e:
        print(f"An error occurred while reading {csv_file}: {e}")
    return player_names


def get_odds():
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
    response = requests.get("https://api.sleeper.app/lines/available", headers=headers)
    data = response.json()

    def decimal_to_american(decimal_odds):
        if decimal_odds >= 2.0:
            return "+" + str(int((decimal_odds - 1) * 100))
        else:
            return str(int(-100 / (decimal_odds - 1)))

    player_names_dict = get_player_names_from_csv()

    odds_data = []
    for item in data:
        league = item.get('sport').upper()  # This is actually the league
        if league not in LEAGUE_TO_SPORT:
            continue
        sport = LEAGUE_TO_SPORT.get(league, 'unknown')  # Map league to sport
        updated_at_timestamp_ms = item.get('updated_at')
        updated_at_datetime = datetime.datetime.fromtimestamp(updated_at_timestamp_ms / 1000, tz=datetime.timezone.utc)
        updated_at = updated_at_datetime.isoformat().replace('+00:00', 'Z')
        wager_type = item.get('wager_type')

        options = item.get('options', [])
        if len(options) < 2:
            continue

        option0 = options[0]
        option1 = options[1]
        
        option0_outcome = option0.get('outcome')
        if option0_outcome:
            if option0_outcome.lower() == 'over':
                option0_outcome = 'Over'
            elif option0_outcome.lower() == 'under':
                option0_outcome = 'Under'

        option1_outcome = option1.get('outcome')
        if option1_outcome:
            if option1_outcome.lower() == 'over':
                option1_outcome = 'Over'
            elif option1_outcome.lower() == 'under':
                option1_outcome = 'Under'

        option0_game_id = option0.get('game_id')
        option1_game_id = option1.get('game_id')

        option0_subject_id = str(option0.get('subject_id'))
        option1_subject_id = str(option1.get('subject_id'))

        option0_payout_multiplier_decimal = option0.get('payout_multiplier')
        option1_payout_multiplier_decimal = option1.get('payout_multiplier')

        option0_payout_multiplier_american = decimal_to_american(float(option0_payout_multiplier_decimal))
        option1_payout_multiplier_american = decimal_to_american(float(option1_payout_multiplier_decimal))

        # Create composite keys for player lookup using league instead of sport
        option0_key = (option0_subject_id, league)
        option1_key = (option1_subject_id, league)

        option0_player_info = player_names_dict.get(option0_key, ("Player Not Found", "", ""))
        option1_player_info = player_names_dict.get(option1_key, ("Player Not Found", "", ""))

        # Parse game_time, home, and away from gid
        gid_parts_option0 = option0_game_id.split('_') if option0_game_id else []
        gid_parts_option1 = option1_game_id.split('_') if option1_game_id else []

        if len(gid_parts_option0) == 3:
            game_time_str_option0 = gid_parts_option0[0]
            game_time_option0 = f"{game_time_str_option0[:4]}-{game_time_str_option0[4:6]}-{game_time_str_option0[6:]}"
            home_team_option0 = gid_parts_option0[1]
            away_team_option0 = gid_parts_option0[2]
        else:
            game_time_option0 = ''
            home_team_option0 = ''
            away_team_option0 = ''

        if len(gid_parts_option1) == 3:
            game_time_str_option1 = gid_parts_option1[0]
            game_time_option1 = f"{game_time_str_option1[:4]}-{game_time_str_option1[4:6]}-{game_time_str_option1[6:]}"
            home_team_option1 = gid_parts_option1[1]
            away_team_option1 = gid_parts_option1[2]
        else:
            game_time_option1 = ''
            home_team_option1 = ''
            away_team_option1 = ''


        line_data_option0 = {
            'gid': option0_game_id,
            'sport': sport,
            'league': league,
            'game_time': game_time_option0,
            'home': home_team_option0,
            'away': away_team_option0,
            'sb_name': 'Sleeper', # Source of the odds is Sleeper API
            'player_name': f"{option0_player_info[0]} {option0_player_info[1]} {option0_outcome} {option0.get('outcome_value')}",
            'price': option0_payout_multiplier_american,
            'updated': updated_at,
            'line': option0.get('outcome_value'),
            'market': STAT_MAP.get(wager_type, wager_type),
            'matchup': f"{home_team_option0} vs {away_team_option0}",
            'bet_url': '', # bet_url not available
            'sid': 'None', # sid not available
        }
        odds_data.append(line_data_option0)

        line_data_option1 = {
            'gid': option1_game_id,
            'sport': sport,
            'league': league,
            'game_time': game_time_option1,
            'home': home_team_option1,
            'away': away_team_option1,
            'sb_name': 'Sleeper', # Source of the odds is Sleeper API
            'player_name': f"{option1_player_info[0]} {option1_player_info[1]} {option1_outcome} {option1.get('outcome_value')}",
            'price': option1_payout_multiplier_american,
            'updated': updated_at,
            'line': option1.get('outcome_value'),
            'market': STAT_MAP.get(wager_type, wager_type),
            'matchup': f"{home_team_option1} vs {away_team_option1}",
            'bet_url': '', # bet_url not available
            'sid': 'None', # sid not available
        }
        odds_data.append(line_data_option1)

    csv_file = "sleeper_odds.csv"
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['gid', 'sport', 'league', 'game_time', 'home', 'away', 'sb_name', 'player_name', 'price', 'updated', 'line', 'market', 'matchup', 'bet_url', 'sid']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(odds_data)
    except Exception as e:
        print(f"An error occurred: {e}")
