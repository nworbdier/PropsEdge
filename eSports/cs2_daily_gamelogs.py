import requests
import json
import csv
from datetime import date, timedelta

base_url_matches_list = "https://api.bo3.gg/api/v2/matches/finished"
base_url_match_details = "https://api.bo3.gg/api/v1/matches/"
base_url_game_player_stats = "https://api.bo3.gg/api/v1/games/" # Added base URL for game player stats
date_str = date.today().isoformat() # Today's date in ISO format
utc_offset = -18000
bo_types = "2,3,5"
tiers = "s,a,b"
discipline_id = 1

current_date = date.fromisoformat(date_str)

csv_file_path = 'eSports/cs2_daily_gamelogs.csv'
try:
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
        csv_writer = csv.writer(f)

        # Write header row
        header = [
            'player_id', 'player_slug', 'player_nickname', 'player_image_url', 'team_clan_name', 'enemy_clan_name',
            'kills', 'deaths', 'assists', 'headshots',
            'game_id', 'map_number', 'match_id', 'match_slug', 'team1_id', 'team2_id', 'team1_slug', 'team1_name', 'team1_image_url',
            'team2_slug', 'team2_name', 'team2_image_url', 'team1_result', 'team2_result', 'team1_score', 'team2_score',
            'bo_type', 'start_date', 'tier', 'tournament_id', 'tournament_name'
        ]
        csv_writer.writerow(header)


        date_str = current_date.isoformat()
        url_matches_list = f"{base_url_matches_list}?date={date_str}&utc_offset={utc_offset}&filter%5Bbo_type%5D%5Bin%5D={bo_types}&filter%5Btier%5D%5Bin%5D={tiers}&filter%5Bdiscipline_id%5D%5Beq%5D={discipline_id}"

        print(f"Fetching URL: {url_matches_list}") # Added console log for matches list URL
        response_matches_list = requests.get(url_matches_list)
        response_matches_list.raise_for_status()
        matches_list_data = response_matches_list.json()


        if 'data' in matches_list_data and 'tiers' in matches_list_data['data']:
            tiers_data = matches_list_data['data']['tiers']

            for tier_name, tier_data in tiers_data.items():
                if isinstance(tier_data, dict):
                    matches = tier_data.get('matches', [])
                    for match_summary in matches:
                        status = match_summary.get('status')
                        if status == "finished":
                            slug = match_summary.get('slug')
                            if slug:
                                match_details_url = f"{base_url_match_details}{slug}?with=games"
                                print(f"Fetching URL: {match_details_url}") # Added console log for match details URL
                                try:
                                    response_match_details = requests.get(match_details_url)
                                    response_match_details.raise_for_status()
                                    match_details_data = response_match_details.json()

                                    if 'team1_id' in match_details_data and 'team2_id' in match_details_data and 'winner_team_id' in match_details_data and 'team1' in match_details_data and 'team2' in match_details_data:
                                        team1_id = str(match_details_data.get('team1_id'))
                                        team2_id = str(match_details_data.get('team2_id'))
                                        winner_team_id = str(match_details_data.get('winner_team_id'))
                                        team1_name_from_details = match_details_data['team1'].get('name').strip() # Get team names for player stats association and trim whitespace
                                        team2_name_from_details = match_details_data['team2'].get('name').strip() # Get team names for player stats association and trim whitespace

                                        if winner_team_id == team1_id:
                                            team1_result = 'W'
                                            team2_result = 'L'
                                        elif winner_team_id == team2_id:
                                            team1_result = 'L'
                                            team2_result = 'W'
                                        else:
                                            team1_result = 'N/A'
                                            team2_result = 'N/A'


                                        for game in match_details_data.get('games', []):
                                            game_id = game.get('id')
                                            game_number = game.get('number')
                                            if game_id and game_number in [1, 2]:
                                                game_player_stats_url = f"{base_url_game_player_stats}{game_id}/players_stats"
                                                try:
                                                    response_game_player_stats = requests.get(game_player_stats_url)
                                                    response_game_player_stats.raise_for_status()
                                                    game_player_stats_data = response_game_player_stats.json()

                                                    for player_stats in game_player_stats_data:
                                                        player_info = player_stats.get('steam_profile', {}).get('player', {})
                                                        team_clan_name = player_stats.get('clan_name', '')
                                                        enemy_clan_name = player_stats.get('enemy_clan_name', '') # Added enemy_clan_name

                                                        player_dict = {
                                                            'player_id': player_info.get('id'),
                                                            'player_slug':player_info.get('slug'),
                                                            'player_nickname': player_info.get('nickname'),
                                                            'player_image_url': player_info.get('image_url'),
                                                            'team_clan_name': team_clan_name, # Added team_clan_name
                                                            'enemy_clan_name': enemy_clan_name # Added enemy_clan_name
                                                        }

                                                        stats_dict = {
                                                            'kills': player_stats.get('kills'),
                                                            'deaths': player_stats.get('death'), # Corrected key to 'death'
                                                            'assists': player_stats.get('assists'),
                                                            'headshots': player_stats.get('headshots'),
                                                        }

                                                        event_dict = {
                                                            'game_id': game_id,
                                                            'map_number': game_number, # Added game_number to event details
                                                            'match_id': match_details_data.get('id'),
                                                            'match_slug': slug,
                                                            'team1_id': team1_id,
                                                            'team2_id': team2_id,
                                                            'team1_slug': match_details_data['team1'].get('slug'),
                                                            'team1_name': team1_name_from_details,
                                                            'team1_image_url': match_details_data['team1'].get('image_url'),
                                                            'team2_slug': match_details_data['team2'].get('slug'),
                                                            'team2_name': team2_name_from_details,
                                                            'team2_image_url': match_details_data['team2'].get('image_url'),
                                                            'team1_result': team1_result,
                                                            'team2_result': team2_result,
                                                            'team1_score': match_details_data.get('team1_score'),
                                                            'team2_score': match_details_data.get('team2_score'),
                                                            'bo_type': match_details_data.get('bo_type'),
                                                            'start_date': match_details_data.get('start_date'),
                                                            'tier': match_details_data.get('tier'),
                                                            'tournament_id': match_details_data.get('tournament_id'),
                                                            'tournament_name': match_details_data.get('tournament', {}).get('name'),
                                                        }


                                                        # Write data row immediately
                                                        row = [
                                                            player_dict.get('player_id'), player_dict.get('player_slug'), player_dict.get('player_nickname'), player_dict.get('player_image_url'), player_dict.get('team_clan_name'), player_dict.get('enemy_clan_name'),
                                                            stats_dict.get('kills'), stats_dict.get('deaths'), stats_dict.get('assists'), stats_dict.get('headshots'),
                                                            event_dict.get('game_id'), event_dict.get('map_number'), event_dict.get('match_id'), event_dict.get('match_slug'), event_dict.get('team1_id'), event_dict.get('team2_id'), event_dict.get('team1_slug'), event_dict.get('team1_name'), event_dict.get('team1_image_url'),
                                                            event_dict.get('team2_slug'), event_dict.get('team2_name'), event_dict.get('team2_image_url'), event_dict.get('team1_result'), event_dict.get('team2_result'), event_dict.get('team1_score'), event_dict.get('team2_score'),
                                                            event_dict.get('bo_type'), event_dict.get('start_date'), event_dict.get('tier'), event_dict.get('tournament_id'), event_dict.get('tournament_name')
                                                        ]
                                                        csv_writer.writerow(row)


                                                except requests.exceptions.RequestException as e:
                                                    print(f"Request error for game {game_id} player stats: {e}")
                                                except json.JSONDecodeError as e:
                                                    print(f"JSON decode error for game {game_id} player stats: {e}")
                                                except Exception as e:
                                                    print(f"An unexpected error occurred for game {game_id} player stats: {e}")


                                        # match_info is no longer needed in this structure

                                    else:
                                        print(f"Missing team or winner ID in match details for slug: {slug}")

                                except requests.exceptions.RequestException as e:
                                    print(f"Request error for match slug {slug}: {e}")
                                except json.JSONDecodeError as e:
                                    print(f"JSON decode error for match slug {slug}: {e}")
                                except Exception as e:
                                    print(f"An unexpected error occurred for match slug {slug}: {e}")
                            else:
                                print("Slug not found for a match.")
                        else:
                            print(f"Skipping match due to status: {status}")
                else:
                    print(f"Unexpected data type for {tier_name}: {type(tier_data)}")
        else:
            print("No 'data.tiers' data found in the response.")


    print(f"Data saved to {csv_file_path}")


except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
