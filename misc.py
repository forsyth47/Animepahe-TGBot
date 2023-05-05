import os
import subprocess
import json
from telegram import *
from telegram.ext import *

apiurl = 'https://animepahe.ru'
botkey = os.environ['botkey']

def createjsoninfo(update):
  cache_dir = os.path.join("data", "UserData")
  if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
  data_file = os.path.join(cache_dir, f"{update.message.chat_id}.json")
  if not os.path.exists(data_file) or len(str((subprocess.check_output("cat "+data_file, shell=True)).decode("utf-8")))==0:
    with open(data_file, "w") as f:
      json.dump({"FirstName":update.message.chat.first_name, "chat_id":update.message.chat_id, "lastseenurl": f"{apiurl}/api?m=release&id=d349af0f-a767-96a0-2219-85cc7caba212&sort=episode_asc&page=1", "snapshot":"https://i.animepahe.com/snapshots/bd07788b5984baf856c0c85dd16eaebbb6a0d8223ee203445b276ebed2fde187.jpg", "poslastepisode": 1-1, "duration": "00:23:52","created_at": "2023-04-10 16:04:19"}, f, indent=4)