import json
import os
import threading

import requests

import time
from functools import wraps

created = False


def run_minute(interval_minutes):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def run():
                while not created:
                    time.sleep(1)
                while True:
                    func(*args, **kwargs)
                    for i in range(interval_minutes):
                        if graidManager.STOP:
                            return
                        time.sleep(60)

            thread = threading.Thread(target=run, daemon=True)
            thread.start()

        # Start the thread automatically but handle 'self' in class methods
        def auto_start(instance, *args, **kwargs):
            wrapper(instance, *args, **kwargs)  # Pass 'self' explicitly

        return auto_start

    return decorator
class graidManager:

    THREADS = []
    STOP = False

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
        global created
        self.playerRaids = None
        self.guildRaids = self.getGuildRaids()

    def getPlayerRaids(self) -> dict:
        player_raids = {}
        for guild in self.config["guilds"]:
            response = requests.get(f"https://api.wynncraft.com/v3/guild/{guild}")
            if response.status_code == 200:
                data = response.json()
                players = [data["members"][rank] for rank in data["members"] if rank != "total"]
                players = [key for kind in players for key in kind]
                player_raids[guild] = self.getPlayersRaids(players)
            else:
                player_raids[guild] = []
        return player_raids

    def getPlayersRaids(self, players) -> dict:
        output = {}
        for player in players:
            player_response = requests.get(f"https://api.wynncraft.com/v3/player/{player}")
            if player_response.status_code == 200:
                player_data = player_response.json()
                output[player] = player_data["globalData"]["raids"]["list"]
            else:
                print("Error getting player data" + player)
        return output


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

    @run_minute(1)
    def checking(self):
        if self.playerRaids is None:
            return
        newGuildRaids = self.getGuildRaids()
        # Check for differenes in guild raids
        for raid in newGuildRaids:
            for guild in newGuildRaids[raid]:
                completedRaid = []
                if self.guildRaids[raid][guild] < newGuildRaids[raid][guild]:
                    completedRaid.append(raid)
                if len(completedRaid) > 0:
                    # Find who has completed the raid
                    playerRaids = self.getPlayersRaids([ x for x in self.playerRaids[guild]])
                    for raid in completedRaid:
                        for player in playerRaids:
                            if self.playerRaids[player][raid] < playerRaids[player][raid]:
                                print("Player " + player + " has completed " + raid + " in guild " + guild)
                    self.playerRaids[guild] = playerRaids
        self.guildRaids = newGuildRaids

    @run_minute(60 * 24)
    def updatePlayers(self):
        self.playerRaids = self.getPlayerRaids()

    def managerMenu(self):
        self.checking()
        while True:
            a = input("Press q to quit")
            if a == "q":
                graidManager.STOP = True
                for thread in graidManager.THREADS:
                    thread.join()
                break
            else:
                print("Invalid input")
