import json
import os
import time
import inspect
from telegram import *
from telegram.ext import *
from commands import *
import misc
from gitnotifier import *
from webserver import keep_alive
import requests
from datetime import datetime
import pytz

apiurl = misc.apiurl

def query(update, context):
  global chatid, qresponse, ufid, queryreturn
  ufid = inspect.stack()[0][3]
  chatid = update.message.chat_id
  qresponse = requests.get(f"{apiurl}/api?m=search&q={update.message.text}").json()
  keyboard = [[InlineKeyboardButton(f"{' '*20}[{i + 1}] {anime['title']}{' '*20}", callback_data=f"{i + 1}")]for i, anime in enumerate(qresponse['data'])] + [[InlineKeyboardButton("> EXIT", callback_data="exit")]]
  queryreturn = context.bot.send_message(chat_id=chatid, text="<b><i>Select anime: </i></b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
  logs = ((datetime.now(pytz.timezone("Asia/Kolkata"))).strftime("[%d/%m/%Y %H:%M:%S] "), f'User ({update.message.chat.first_name}, @{update.message.chat.username}, {update.message.chat.id}) says: "{str(update.message.text)}"')
  print(logs)
  with open("log.txt", "a+") as fileout:
    fileout.write(f"{logs}\n")

def episodequery(update, context, xpage=1):
  global eresponse, ufid, equeryreturn, equrl, zpage, ephotoreturn
  zpage = xpage
  ufid = inspect.stack()[0][3]
  chatid = update.effective_chat.id
  equrl = f"{apiurl}/api?m=release&id={selectedanime['session']}&sort=episode_asc&page={zpage}"
  eresponse = requests.get(equrl).json()
  ephotoreturn=context.bot.send_photo(chatid, selectedanime["poster"], caption=f'<b>Title: </b><code>{selectedanime["title"]}</code> \n<b>Total Episodes: </b> {(selectedanime["episodes"])} \n<b>Data type: </b>{selectedanime["type"]} \n<b>Released on: </b>{selectedanime["year"]} \n<b>Status: </b><code>{selectedanime["status"]}</code> \n<b>Rating: </b>{selectedanime["score"]}\n<b>URL: </b><a href="{apiurl}/anime/{selectedanime["session"]}">{selectedanime["title"]}</a>', parse_mode="html")
  keyboard = [[InlineKeyboardButton(f"{' '*25}[{i + 1}] • E{episode['episode']}{' '*25}", callback_data=f"{i + 1}")] for i, episode in enumerate(eresponse['data'])] + [[InlineKeyboardButton("> EXIT", callback_data="exit")]]
  if eresponse['next_page_url'] != None:
    keyboard += [[InlineKeyboardButton("~ / / Next / / ~", callback_data="888")]]
  if eresponse['prev_page_url'] != None:
    keyboard += [[InlineKeyboardButton("~ / / Previous / / ~", callback_data="999")]]
  equeryreturn = context.bot.send_message(chatid, text="<b><i>Select episode: </i></b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

def wrappup(update, context):
  sentmessage = context.bot.send_message(chat_id=update.effective_chat.id, text="<b><i>~ / / / Started scraping links / / / ~</i></b>", parse_mode='html')
  quotejson=requests.get('https://zenquotes.io/api/random').json()
  quotecontent = quotejson[0]['q'] 
  quoteauthor = quotejson[0]['a']
  # with open(os.path.join("data", "UserData", f"{update.effective_chat.id}.json"), "r") as f:
  #     userinfo=json.load(f)
  keyboard = []
  linkdata = subprocess.check_output(f"animdl -x grab '{apiurl}/anime/{selectedanime['session']}' -r {selectedepisode['episode']}" ,shell=True, stderr=subprocess.DEVNULL).decode('utf-8')
  linkdata=json.loads(linkdata)
  for quality in linkdata["streams"]:
    with requests.get(quality["stream_url"], stream=True) as response:
      content_length = int(response.headers.get('Content-Length')) / 1048576 
    if "dub" in quality["stream_url"].lower():
      dubstat = "[Dub]"
    else:
      dubstat = ""
    keyboard += [[InlineKeyboardButton(f'Episode {selectedepisode["episode"]} {dubstat} | {quality["quality"]}p ({content_length:.2f}MB) | {selectedanime["title"]}', url=quality["stream_url"])]]
  context.bot.delete_message(chat_id=update.effective_chat.id, message_id=sentmessage.message_id)
  context.bot.send_message(chat_id=update.effective_chat.id, text=f"<b>{quotecontent}</b>\n~<code>{quoteauthor}</code>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
  with open(os.path.join(os.path.join("data", "UserData"), f"{chatid}.json"), "r+") as f:
    writejson = json.load(f)
    writejson["lastseentitle"] = selectedanime["title"]
    writejson["lastseenurl"] = equrl
    writejson["lastseenslug"] = selectedanime["session"]
    writejson["year"] = selectedanime["year"]
    writejson["status"] = selectedanime["status"]
    writejson["snapshot"] = selectedepisode['snapshot']
    writejson["poslastepisode"] = selectedepisode['episode'] - 1
    writejson["duration"] = selectedepisode['duration']
    writejson["created_at"] = selectedepisode['created_at']
    f.seek(0)
    json.dump(writejson, f, indent=4)
    f.truncate()
  

def Button(update, context):
  global selectedanime, selectedepisode, zpage
  query = update.callback_query
  data = query.data
  if data == "exit":
    context.bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text="Exited")
    update.callback_query.edit_message_reply_markup(None)
    if ufid == "query":
      context.bot.delete_message(chat_id=update.effective_chat.id, message_id=queryreturn.message_id)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Make Another Search: ")
    elif ufid == "episodequery":
      context.bot.delete_message(chat_id=update.effective_chat.id, message_id=equeryreturn.message_id)
      context.bot.send_message(chat_id=update.effective_chat.id, text="Make Another Search: ")
  buttoncallback = int(data)
  context.bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text="Selected")
  update.callback_query.edit_message_reply_markup(None)
  if ufid == "query":
    selectedanime = qresponse['data'][buttoncallback - 1]
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=queryreturn.message_id)
    episodequery(update, context, xpage=1)
  elif ufid == "episodequery":
    if buttoncallback == 888:
        zpage += 1
        query.answer()
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=ephotoreturn.message_id)
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=equeryreturn.message_id)
        episodequery(update, context, zpage)
    elif buttoncallback == 999:
        zpage -= 1
        query.answer()
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=ephotoreturn.message_id)
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=equeryreturn.message_id)
        episodequery(update, context, zpage)
    else:
      selectedepisode = eresponse['data'][buttoncallback - 1]
      context.bot.delete_message(chat_id=update.effective_chat.id, message_id=equeryreturn.message_id)
      wrappup(update, context)   
  else:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Error! Make new request")



# Log errors
def error(update, context):
  errorlog = (datetime.now(pytz.timezone("Asia/Kolkata"))).strftime("[%d/%m/%Y %H:%M:%S] "), f'Update {update} caused error {context.error}'
  with open("error.txt", "a+") as fileout:
    fileout.write(f"{errorlog}\n\n{'-'*20}\n\n")
  print(errorlog)



#================================== STARTING THE PROGRAM ==================================
if __name__ == '__main__':
  keep_alive()
  print("===================Starting BetterFlix-Bot-Telegram===================")
  updater = Updater(misc.botkey, use_context=True)
  dp = updater.dispatcher

  # Commands
  #dp.add_handler(CommandHandler('name', name))
  dp.add_handler(CommandHandler('start', start_command))
  dp.add_handler(CommandHandler('help', help_command))
  dp.add_handler(CommandHandler('c', command))
  dp.add_handler(CommandHandler('next', next))

  # Messages
  dp.add_handler(MessageHandler(Filters.text, query))
  
  # InlineKeyboardButton
  dp.add_handler(CallbackQueryHandler(Button))

  # Log all errors
  dp.add_error_handler(error)

  # Run the bot
  updater.start_polling(1.0)

  while True:
    check_for_commits()
    time.sleep(600) # Sleep for 10 minutes before checking again

  updater.idle()

#================================== END OF THW SCRIPT ==================================