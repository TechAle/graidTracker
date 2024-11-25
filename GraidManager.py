import json
import os
import zlib

import requests


class graidManager:

    raids = {
        "grootslangSrGuilds": "Nest of the Grootslangs",
        "colossusSrGuilds": "The Canyon Colossus",
        "namelessSrGuilds": "The Nameless Anomaly",
        "orphionSrGuilds": "Orphion's Nexus of Light"
    }

    @staticmethod
    def get_config() -> dict:
        if os.path.exists("config.json"):
            file = json.loads(open("config.json", "r").read())
        else:
            file = open("config.json", "w")
            file.write(json.dumps(graidManager.getDefaultConfig()))
            file.close()
            file = graidManager.getDefaultConfig()
        return file

    @staticmethod
    def getDefaultConfig() -> dict:
        return {
            "guilds": ["Sequoia"]
        }


    def __init__(self):
        self.config = self.get_config()
        self.playerRaids = self.getPlayerRaids()
        self.guildRaids = self.getGuildRaids()

    def getPlayerRaids(self) -> dict:
        player_raids = {}
        for guild in self.config["guilds"]:
            response = requests.get(f"https://api.wynncraft.com/v3/guild/{guild}")
            if response.status_code == 200:
                data = response.json()
                players = [data["members"][rank] for rank in data["members"] if rank != "total"]
                players = [key for kind in players for key in kind]
                player_raids[guild] = {}
                for player in players:
                    player_response = requests.get(f"https://api.wynncraft.com/v3/player/{player}")
                    if player_response.status_code == 200:
                        player_data = player_response.json()
                        player_raids[guild][player] = player_data["globalData"]["raids"]["list"]
                    else:
                        print("Error getting player data" + player)
            else:
                player_raids[guild] = []
        return player_raids

    def getGuildRaids(self) -> dict:
        output = {}
        for raid in graidManager.raids:
            response = requests.get(f"https://api.wynncraft.com/v3/leaderboards/{raid}")
            output[raid] = {}
            if response.status_code == 200:
                data = response.json()
                for guild in data:
                    output[raid][data[guild]["name"]] = data[guild]["metadata"]["completions"]

            else:
                print("Error getting guild data" + raid)
        print(output)
        return output
