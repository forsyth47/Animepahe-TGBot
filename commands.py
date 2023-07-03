import misc
from misc import *
from telegram.ext import *
from telegram import *
import os
import requests
import json
import subprocess
import urllib.request
from datetime import datetime
import pytz

apiurl = misc.apiurl

def start_command(update, context):
  createjsoninfo(update)
  update.message.reply_text("Bot is Under Development 🏗️\nEnter Anime name: ")

def help_command(update, context):
  update.message.reply_text("PM @JoshuaForsyth for any help!")
  
def command(update, context):
  chat_id = update.message.chat_id
  if str(update.message.chat.username).lower() == str(misc._admin_username).lower():
    inputtext=str(update.message.text)[3:]
    if len(inputtext) != 0:
        context.bot.send_message(chat_id, text=(subprocess.check_output(inputtext, shell=True)).decode("utf-8"))
    else:
      context.bot.send_message(chat_id, "*Send a UNIX/Windows machine command in this format:* \n \n       `/c \\<Your command here\\!\\>` \n \n*Example: '`/c tail log\\.txt`' \n\\(Grabs log\\.txt contexts for UNIX machines\\)*", parse_mode='MarkdownV2')
  else:
    context.bot.send_message(chat_id, "Sorry! Only the owner has permission to use this command!\n\n <b>Host your own bot to use this command :D</b>", parse_mode="html", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Host your own bot! 🤖", url="https://github.com/forsyth47/Animepahe-TGBot")]]))


def next(update, context):
  chat_id=update.message.chat_id
  with open(os.path.join("data", "UserData", f"{chat_id}.json"), "r") as f:
      userinfo=json.load(f)
  eresponse = requests.get(userinfo['lastseenurl']).json()
  posnewep = userinfo['poslastepisode'] + 1
  if posnewep >= eresponse['total']:
    context.bot.send_message(chat_id=update.effective_chat.id, text="<b><i>~ / / / Episode Doesn't exists / / / ~</i></b>", parse_mode='html')
    return
  datanewep = eresponse['data'][posnewep]
  context.bot.send_photo(chat_id=update.effective_chat.id, photo=datanewep['snapshot'],  caption=f'<b>Title: </b><code>{userinfo["lastseentitle"]}</code> \n<b>Episode Number: </b> {(datanewep["episode"])} \n<b>Duration: </b>{datanewep["duration"]} \n<b>Released on: </b>{userinfo["year"]} \n<b>Status: </b><code>{userinfo["status"]}</code>', parse_mode="html")
  sentmessage = context.bot.send_message(chat_id=update.effective_chat.id, text="<b><i>~ / / / Started scraping links / / / ~</i></b>", parse_mode='html')
  keyboard = []
  for quality in ['1080', '720', '360']:
    context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=sentmessage.message_id, text=f"<b><i>~ / / / Scraping <code>{quality}p</code> Link . . . / / / ~</i></b>", parse_mode='html')
    url = subprocess.check_output(f"bash animepahe-dl/animepahe-dl.sh -l -s {userinfo['lastseenslug']} -e {datanewep['episode']} -o {userinfo['language']} -r {quality}" ,shell=True).decode('utf-8')
    m3u8_content = subprocess.check_output(f"curl -s -H 'Referer: https://kwik.cx/' {url}" ,shell=True).decode('utf-8')
    new_content = ''
    for line in m3u8_content.split('\n'):
        if line.startswith('#EXT-X-VERSION:'):
            new_content += line + '\n' + '#EXT-X-SESSION-DATA:REFERER=https://kwik.cx/\n'
        else:
            new_content += line + '\n'
    files = {'file': ('modified_index.m3u8', new_content)}
    response = requests.post('https://ttm.sh', files=files)
    surl = response.text
    keyboard += [[InlineKeyboardButton(f'{userinfo["lastseentitle"]} | Episode {datanewep["episode"]} | {quality}p', url=surl)]]
  context.bot.delete_message(chat_id=update.effective_chat.id, message_id=sentmessage.message_id)
  context.bot.send_message(chat_id=update.effective_chat.id, text=f"<code>Spread Love 💛</code>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
  with open(os.path.join(os.path.join("data", "UserData"), f"{update.effective_chat.id}.json"), "r+") as f:
    writejson = json.load(f)
    writejson["snapshot"] = datanewep['snapshot']
    writejson["poslastepisode"] = posnewep
    writejson["duration"] = datanewep['duration']
    writejson["created_at"] = datanewep['created_at']
    f.seek(0)
    json.dump(writejson, f, indent=4)
    f.truncate()

  logs = ((datetime.now(pytz.timezone("Asia/Kolkata"))).strftime("[%d/%m/%Y %H:%M:%S] "), f'User ({update.message.chat.first_name}, @{update.message.chat.username}, {update.message.chat.id}) Plays next of: "{userinfo["lastseentitle"]}, Episode: {datanewep["episode"]}"')
  print(logs)
  with open("log.txt", "a+") as fileout:
    fileout.write(f"{logs}\n")
    