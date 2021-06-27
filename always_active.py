from flask import Flask, request
from threading import Thread
import sys
import os

app = Flask('')

@app.route('/')
def home():
    if request.headers.get('attok') == os.getenv('RESTART_TOKEN'):
      os.execv(sys.executable, ['python'] + sys.argv)
      return "Restarting"

    return "Bot is ready"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():  
    t = Thread(target=run)
    t.start()