import requests
import json
import os
import telegram
import subprocess

def check_for_commits():
    # Set the API endpoint URL and repository information
	url = 'https://api.github.com/repos/forsyth47/Animepahe-TGBot/commits'
    
    # Set the headers to include your GitHub username and personal access token
	headers = {'Authorization': os.environ['send-commit-msg-token']}
    
    # Get the latest commit information
	response = requests.get(url, headers=headers)
	response_json = response.json()
	latest_commit = response_json[0]
	
    
	if not os.path.exists('data'):
		os.mkdir('data')
	if not os.path.exists('data/commit_info.json') or len(str((subprocess.check_output("cat "+'data/commit_info.json', shell=True)).decode("utf-8")))==0:
		with open('data/commit_info.json', 'w') as f:
			json.dump(latest_commit, f, indent=4)
	with open('data/commit_info.json', 'r') as f:
			last_commit = json.load(f)
        
    
	if last_commit['sha'] != latest_commit['sha']:
		with open('data/commit_info.json', 'w') as f:
			json.dump(latest_commit, f, indent=4)
		print("New commit detected!")
		print(f"Latest commit message: {latest_commit['commit']['message']}")
		print(f"Latest commit author: {latest_commit['commit']['author']['name']}")
		print(f"Latest commit timestamp: {latest_commit['commit']['author']['date']}")
		print(f"Latest commit sha: {latest_commit['sha']}")
		bot = telegram.Bot(token=os.environ['botkey'])
		directory = 'data/UserData/'
		userids = []
		for filename in os.listdir(directory):
			if os.path.isfile(os.path.join(directory, filename)):
				id = int(filename.split('.')[0])
				userids.append(id)
		for u_chat_id in userids:
			try:
				bot.send_message(chat_id=u_chat_id, text=f"<b>Commit message [Changelogs]</b> \n<code>{latest_commit['commit']['message']}</code>\n\n<a href='{latest_commit['html_url']}'>#{latest_commit['sha'][:7]}</a>\n<b>Timestamp: </b>{latest_commit['commit']['author']['date']}", parse_mode='html')
        print(f"Sent to User {u_chat_id}")
			except:
				print(f"User {u_chat_id} has blocked the bot, message not sent.")
				continue