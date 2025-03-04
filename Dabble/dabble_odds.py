import requests
import csv

def get_odds():
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
        'CLUBSOCCER': 'SOCCER'
    }

    STAT_MAP = {
        'assists': 'Player Assists',
        'double-double': 'Player Double Double',
        'first-quarter-points': 'Player Points Q1',
        'points': 'Player Points',
        'assists_points': 'Player Points + Assists',
        'points_rebounds': 'Player Points + Rebounds',
        'assists_points_rebounds': 'Player Points + Assists + Rebounds',
        'rebounds': 'Player Rebounds',
        'assists_rebounds': 'Player Assists + Rebounds',
        'three-made': 'Player Threes',
        'blocks': 'Player Blocks',
        'steals': 'Player Steals',
        'turnovers': 'Player Turnovers',
        'first-quarter-assists': 'Player Assists Q1',
        'first-quarter-rebounds': 'Player Rebounds Q1',
        'blocks_steals': 'Player Blocks + Steals',
        'goals': 'Player Goals',
        'shots': 'Player Shots',
        'blocked_shots': 'Player Blocked Shots',
        'powerplay_points': 'Player Power Play Points',
        'headshots_maps_1_2': 'Player Headshots Map 1 + 2',
        'kills_maps_1_2': 'Player Kills Map 1 + 2',
    }
    def fetch_events_from_api(competition_id):
        """Fetches events data from the Dabble API for a given competition ID."""
        url = f"https://api.dabble.com/competitions/{competition_id}/sport-fixtures"
        response = requests.get(url)
        data = response.json()
        if 'data' in data and isinstance(data['data'], list):
            return data['data']
        else:
            print(f"No 'data' array found or 'data' is not a list for competition ID: {competition_id}")
            return None

    def parse_market_name(market_name, resulting_type, selection_name):
        """Extracts player name and line information from selection name.
        Example: "Tim Hardaway Jr. assists + points 13.5 over" -> ("Tim Hardaway Jr.", "13.5", "Over")
        """
        # First find the numeric value (line) as it's the most reliable separator
        parts = selection_name.split()
        line = None
        is_over = None
        name_end_idx = 0
        
        # Find the first number (the line)
        for i, part in enumerate(parts):
            if part.replace('.', '').isdigit():
                line = part
                name_end_idx = i
                # Check for over/under after the number
                if i < len(parts) - 1:
                    is_over = parts[i + 1].lower() == 'over'
                break
        
        # Get everything before the line number
        full_text_before_line = ' '.join(parts[:name_end_idx]).strip()
        
        # Find where the stat types begin by looking for known stat keywords
        stat_indicators = list(STAT_MAP.keys())
        
        name_end_pos = len(full_text_before_line)
        for indicator in stat_indicators:
            pos = full_text_before_line.lower().find(indicator)
            if pos != -1 and pos < name_end_pos:
                name_end_pos = pos
        
        # Extract player name (everything before the stats)
        player_name = full_text_before_line[:name_end_pos].strip()
        
        over_under = 'Over' if is_over else 'Under' if is_over is not None else ''
        
        return player_name, line, over_under

    def decimal_to_american(decimal_odds):
        """Convert decimal odds to American odds."""
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))

    # Define schema fields for CSV
    fieldnames = [
        'gid',
        'sport',
        'league',
        'game_time',
        'home',
        'away',
        'sb_name',
        'player_name',
        'price',
        'updated',
        'line',
        'market',
        'matchup',
        'bet_url',
        'sid',
    ]

    # Process the data and write to CSV
    with open('dabble_sports.csv', 'r') as sports_csvfile, \
        open('dabble_odds.csv', 'w', newline='', encoding='utf-8') as markets_csvfile:

        reader = csv.DictReader(sports_csvfile)
        writer = csv.DictWriter(markets_csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            competition_id = row['id']
            events = fetch_events_from_api(competition_id)
            if events is None:
                continue

            for event in events:
                matchup = event.get('name', '')
                away, home = (matchup.split(' @ ') if '@' in matchup else ['', ''])
                gid = event.get('id', '')
                game_time = event.get('advertisedStart', '')
                competition = event.get('competition', {})
                competition_code = competition.get('code')

                if competition_code not in LEAGUE_TO_SPORT:
                    continue

                sport = LEAGUE_TO_SPORT[competition_code]
                
                # Create lookup dictionaries for markets and selections
                markets_dict = {market['id']: market for market in event.get('markets', [])}
                selections_dict = {selection['id']: selection for selection in event.get('selections', [])}

                for price_info in event.get('prices', []):
                    market_id = price_info.get('marketId')
                    selection_id = price_info.get('selectionId')
                    
                    if not (market_id and selection_id):
                        continue
                        
                    market = markets_dict.get(market_id)
                    selection = selections_dict.get(selection_id)
                    
                    if not (market and selection):
                        continue

                    resulting_type = market.get('resultingType', '')
                    market_name = STAT_MAP.get(resulting_type.lower().replace(' ', '-'), resulting_type)
                    
                    if market_name not in STAT_MAP.values():
                        continue

                    player_name, line, over_under = parse_market_name(
                        market.get('name', ''),
                        resulting_type,
                        selection.get('name', '')
                    )

                    decimal_price = price_info.get('price', 0)
                    american_odds = decimal_to_american(decimal_price) if decimal_price > 0 else ''

                    # Format player name to include Over/Under when line exists
                    formatted_player_name = f"{player_name} {over_under} {line}" if line and over_under else player_name

                    row = {
                        'gid': gid,
                        'sport': sport,
                        'league': competition_code,
                        'game_time': game_time,
                        'home': home,
                        'away': away,
                        'sb_name': 'Dabble',
                        'player_name': formatted_player_name,
                        'price': american_odds,
                        'updated': price_info.get('updated', ''),
                        'line': line or '',
                        'market': market_name,
                        'matchup': matchup,
                        'bet_url': '',
                        'sid': selection_id,
                    }
                    writer.writerow(row)

    print("Data has been saved to dabble_odds.csv")