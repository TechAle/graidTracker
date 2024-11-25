import json
import os

import requests


class graidManager:
    @staticmethod
    def get_config() -> dict:
        if os.path.exists("config.json"):
            file = open("config.json", "r").read()
        else:
            file = open("config.json", "w")
            file.write(json.dumps(graidManager.getDefaultConfig()))
            file.close()
            file = graidManager.getDefaultConfig()
        return json.loads(file)

    @staticmethod
    def getDefaultConfig() -> dict:
        return {
            "guilds": []
        }


    def __init__(self):
        self.config = self.get_config()
        self.playerRaids = self.getPlayerRaids()

    def getPlayerRaids(self) -> dict:
        player_raids = {}
        for guild in self.config["guilds"]:
            response = requests.get(f"https://api.wynncraft.com/v3/guild/guild/{guild}")
            if response.status_code == 200:
                data = response.json()
                players = [member["name"] for member in data["members"]]
                player_raids[guild] = {}
                for player in players:
                    player_response = requests.get(f"https://api.wynncraft.com/v3/player/{player}")
                    if player_response.status_code == 200:
                        player_data = player_response.json()
                        player_raids[guild][player] = player_data
                    else:
                        player_raids[guild].append({"name": player, "error": "Failed to retrieve player data"})
            else:
                player_raids[guild] = []
        return player_raids
