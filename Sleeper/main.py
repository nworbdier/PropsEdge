import requests
import csv
from sleeper_odds import *
from sleeper_players import *


def main():
    get_players()
    get_odds()
    
if __name__ == "__main__":
    main()