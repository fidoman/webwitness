#!/usr/bin/python3

# 1. Connect to cluster. Use configured cluster name and try all known nodes/witnesses
# 2. Receive fresh configuration and update local copy
# 3. Start to issue keep-alive requests periodically
# 4. On shutdown event take down local services and issue explicit node down request to nodes and witnesses

import os
import ast

CONFIG="cluster.dat"
# local configuration:
#   cluster name
#   cluster id
#   node name
#   node key
#   admin e-mail
# common configuration:
#   witness list
#   cluster parameters

badstates = set() # notify admin when adding or removing badstate

def sendmessage(msg):
  print(config["admin"],"<<", msg)

def checkbad(message, check):
  """ if check is True set badstate (message) and return True """
  isbad = message in badstate
  if check and not isbad:
    badstates.add(message)
    sendmessage("Bad state: "+message)
  elif not check and isbad:
    badstates.remove(message)
    sendmessage("Cleared: "+message)


class Config:
  def __init__(self, filename):
    self.filename = filename
    if os.path.exists(filename):
      self.data = ast.literal_eval(open(filename).read())
    else:
      self.data = {}

  def __getitem__(self, x):
    return self.data[x]

  def __setitem__(self, x, y):
    self.data[x] = y
    #self.save()

  def __delitem__(self, x):
    del self.data[x]
    #self.save()

  def save(self):
    open(self.filename, "w").write(repr(self.data))


config = Config(CONFIG)

# what to do if we get non-uniform cluster configuration from witnesses?
# If it have different version number, use newest.
# It is normal situation when some configs are of Nth version and some - of (N-1)th
# else 
# 1) notify admin
# 2) keep current configuration until all configs are uniform and 
# if all except some witness are uniform and they say that other witnesses do not exist use that configuration
#  (uncontrollable witness removal)

# after applying new configuration send to witnesses version of applied config

shutdown = False
pullall = True # when pulling full config use option ignore_inaccessible_witness
# if it is set consider only answered witnesses
# else consider situation with inaccessible witnesses as badstate and do not update local config

while not shutdown:
  if pullall:
    newconfig = {}
  else:
    newconfig = 
  for w in config["witness"]:
    # connect and receive info
    addr = config["witness"].get("address")
    if check_bad("witness without address", address is None):
      continue
    .. query witness (use pullall flag)
    if pull

