import requests
import csv

def get_sports():
    url = "https://api.dabble.com/competitions/active/"

    response = requests.get(url)
    data = response.json()

    active_competitions = data.get('data', {}).get('activeCompetitions', [])

    with open('dabble_sports.csv', 'w', newline='') as csvfile:
        fieldnames = ['id', 'code', 'sportname', 'sportid']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for competition in active_competitions:
            writer.writerow({
                'id': competition.get('id'),
                'code': competition.get('code'),
                'sportname': competition.get('sportName'),
                'sportid': competition.get('sportId')
            })
    print("Data has been saved to dabble_sports.csv")