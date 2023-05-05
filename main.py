import json
import os
from telegram import *
from telegram.ext import *
from misc import *
import gitnotifier
import requests

apiurl = 'https://animepahe.ru'

def query(update, context):
  global chatid, qresponse, ufid, queryreturn
  ufid = inspect.stack()[0][3]
  chatid = update.message.chat_id
  qresponse = requests.get(f"{apiurl}/api?m=search&q={update.message}").json()
  keyboard = [[InlineKeyboardButton(f"{i + 1}. {anime['title']}", callback_data=f"{i + 1}")]for i, anime in enumerate(response['data'])] + [[InlineKeyboardButton("> EXIT", callback_data="exit")]]
  queryreturn = context.bot.send_message(chat_id, text="<b><i>Select anime: </i></b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

def episodequery(update, context, xpage=1):
  global eresponse, ufid, equeryreturn, xpage, equrl
  ufid = inspect.stack()[0][3]
  chatid = update.effective_chat.id
  equrl = f"{apiurl}/api?m=release&id={selectedanime['session']}&sort=episode_asc&page={xpage}"
  eresponse = requests.get(equrl).json()
  context.bot.send_photo(chatid, selectedanime["poster"], caption=f'<b>Title: </b><code>{selectedanime["title"]}</code> \n<b>Total Episodes: </b> {(selectedanime["episodes"])} \n<b>Data type: </b>{selectedanime["type"]} \n<b>Released on: </b>{selectedanime["year"]} \n<b>Status: </b><code>{selectedanime["status"]}</code> \n<b>IMDb Rating: </b>{selectedanime["score"]}\n<b>URL: </b>({selectedanime["title"]})[{apiurl + '/anime/' + ["session"]}]', parse_mode="html")
  keyboard = [[InlineKeyboardButton(f"{episode['episode']} [{episode['created_at']}]", callback_data=f"{i + 1}")]for i, episode in enumerate(eresponse['data'])]
  if eresponse['next_page_url'] != 'null':
    keyboard += [InlineKeyboardButton("~//NEXT//~", callback_data="888")]
  if eresponse['prev_page_url'] != 'null':
    keyboard += [InlineKeyboardButton("~//PREVIOUS//~", callback_data="999")]
  keyboard += [InlineKeyboardButton("> EXIT", callback_data="exit")]
  equeryreturn = context.bot.send_message(chatid, text="<b><i>Select episode: </i></b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

def wrappup(update, context):
  msglink = InlineKeyboardButton(f"{selectedanime["title"]} | Episode {selectedepisode['episode']}", url=f"{apiurl} /play/ {selectedanime['session']}/{selectedepisode['session']}")
  quotejson=requests.get('https://api.quotable.io/random').json()
  context.bot.send_message(chat_id, text=f"<b>{quotejson['content']}</b>\n~<code>{quotejson['author']}</code>", reply_markup=InlineKeyboardMarkup(msglink), parse_mode="html")
  with open(os.path.join(os.path.join("data", "UserData"), f"{chatid}.json"), "r+") as f:
    writejson = json.load(f)
    writejson["lastseenurl"] = equrl
    writejson["snapshot"] = selectedepisode['snapshot']
    writejson["poslastepisode"] = selectedepisode['episode'] - 1
    writejson["duration"] = selectedepisode['duration']
    writejson["created_at"] = selectedepisode['created_at']
    f.seek(0)
    json.dump(writejson, f, indent=4)
    f.truncate()
  

def Button(update, context):
  global selectedanime, selectedepisode, xpage
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
    episodequery(update, context, xpage)
  elif ufid == "episodequery":
    if buttoncallback == 888:
        xpage += 1
        query.answer()
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=episodequery.message_id)
        episodequery(update, context, xpage)
    elif buttoncallback == 999:
        xpage -= 1
        query.answer()
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=episodequery.message_id)
        episodequery(update, context, xpage)
    else:
      selectedepisode = eresponse['data'][buttoncallback - 1]
      context.bot.delete_message(chat_id=update.effective_chat.id, message_id=episodequery.message_id)
      wrappup(update, context)   
  else:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Error! Make new request")



# Log errors
def error(update, context):
  print ((datetime.now(pytz.timezone("Asia/Kolkata"))).strftime("[%d/%m/%Y %H:%M:%S] "), f'Update {update} caused error {context.error}')



#================================== STARTING THE PROGRAM ==================================
if __name__ == '__main__':
  print("===================Starting BetterFlix-Bot-Telegram===================")
  updater = Updater(misc.botkey, use_context=True)
  dp = updater.dispatcher

  # Commands
  #dp.add_handler(CommandHandler('name', name))
  dp.add_handler(CommandHandler('start', start_command))
  dp.add_handler(CommandHandler('help', help_command))
  dp.add_handler(CommandHandler('next', next))
  dp.add_handler(CommandHandler('continue', continuewatching))

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
    time.sleep(600) # Sleep for an hour before checking again

  updater.idle()

#================================== END OF THW SCRIPT ==================================