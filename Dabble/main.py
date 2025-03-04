import requests
import csv
from dabble_odds import get_odds
from dabble_sports import get_sports


def main():
    get_sports()
    get_odds()
    
if __name__ == "__main__":
    main()