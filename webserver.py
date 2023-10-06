from flask import Flask

from threading import Thread

app = Flask('')


@app.route('/')
def home():
  fline = ""
  with open ('log.txt','r') as f:
    for line in f.readlines():
      fline += line + "<br>"
  return fline

@app.route('/animepahe.mp4')
def proxy_link():
    full_url = request.full_path
    link = full_url.split('/animepahe.mp4?url=')[1]
    headers = {'Content-Type': 'video/mp4'}
    custom_response = Response("", status=302, headers=headers)
    custom_response.headers['Location'] = link
    return custom_response

def run():

  app.run(host='0.0.0.0', port=8080)


def keep_alive():

  t = Thread(target=run)

  t.start()
