#!/usr/bin/python3

# First phase of protocol: cluster registration
# the only argument - desired cluster name
# Returns unique ID on this whitness and shared key
# Must be called over SSL
# webwitness.py?newcluster=name

import os
import cgi
import re
import cgitb
import base64
import json
import hmac
cgitb.enable()

MAXCLUSTERNAME=20
CLUSTERS="/home/sergey/webwitness/clusters"
KEYLENGTH=128//8 # length in bytes

validname = re.compile("[A-Z0-9_\-+]+$") # never allow '#' here
def validatename(s):
  if len(s)>MAXCLUSTERNAME:
    return False
  if validname.match(s) is None:
    return False
  return True

def cluster_dir(name, key):
  return name+"#"+str(key)

def register_cluster(name):
  registered = False
  i = 0
  while not registered:
    dirname=cluster_dir(name, i)
    try:
      os.mkdir(os.path.join(CLUSTERS, dirname))
    except OSError as e:
      if e.errno==17:
        i += 1
        continue
      else:
        raise e
    registered = True

  key = b"xxx\1\2\3"
  keyfile = open(os.path.join(CLUSTERS, dirname, "key"), "w")
  keyfile.write(repr((key, "md5")))
  keyfile.close()
  return i, key, "md5"

def get_cluster_key(name, i):
  try:
    keyfile = open(os.path.join(CLUSTERS, cluster_dir(name, i), "key"), "r")
    data=eval(keyfile.read())
    keyfile.close()
  except:
    return None
  return data

def register_node(cluster, i, node):
  # create node file in cluster directory
  pass


log=open("/tmp/webwitness.log", "w")

data = cgi.FieldStorage()
issecure = "HTTPS" in os.environ
print("Content-Type: application/json\n\n")

if "newcluster" in data:
  if issecure:
    clustername = data.getfirst("newcluster").upper()
    if validatename(clustername):
      clusterid, clusterkey, hmacalg = register_cluster(clustername)
      print (json.dumps((True, clustername, clusterid, base64.b64encode(clusterkey).decode("ascii"), hmacalg)))
    else:
      print (json.dumps((False, "bad name "+repr(clustername))))
  else:
    print(json.dumps((False, "please use HTTPS")))

elif "newnode" in data and "cluster" in data and "id" in data and "hmac" in data:
  nodename = data.getfirst("newnode").upper()
  clustername = data.getfirst("cluster").upper()
  i = data.getfirst("id").upper()
  providedhmac = data.getfirst("hmac").lower()
  msg = ("|".join((clustername, i, nodename))).encode("ascii")
  #print(repr(clustername), repr(i))
  key, hmacalg = get_cluster_key(clustername, i) or (None, "md5")
  #print(repr(key))
  msghmac = hmac.new(key or b"-"*KEYLENGTH, msg).hexdigest()
  #print(repr(providedhmac))
  #print(repr(msghmac))
  authentic = hmac.compare_digest(providedhmac, msghmac) and (key is not None)
  if authentic:
    print ("will register")
  else:
    print(json.dumps((False, "not authenticated")))


else:
  print(json.dumps((False, "invalid parameter")))

