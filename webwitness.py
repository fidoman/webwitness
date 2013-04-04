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
import traceback
from Crypto.Hash import HMAC
from Crypto import Random
from Crypto.Cipher import AES
cgitb.enable()

MAXCLUSTERNAME=20
CLUSTERS="/home/sergey/webwitness/clusters"
KEYLENGTH=128//8 # length in bytes

def compare_hashes(a, b):
  s = 0
  for i in range(min(len(a), len(b))):
    s += abs(ord(a[i])-ord(b[i]))
  s += abs(len(a)-len(b))
  return s==0

def new_key():
  return Random.get_random_bytes(KEYLENGTH)


validname = re.compile("[A-Z0-9_\-+]+$") # never allow '#' here
def validatename(s):
  if len(s)>MAXCLUSTERNAME:
    return False
  if validname.match(s) is None:
    return False
  return True

def cluster_dir(name, idx):
  return name+"#"+str(idx)

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

  key = new_key()
  keyfile = open(os.path.join(CLUSTERS, dirname, "key"), "wb")
  keyfile.write(key)
  keyfile.close()
  halgfile = open(os.path.join(CLUSTERS, dirname, "hashalg"), "wb")
  halgfile.write(b"md5")
  halgfile.close()
  return i, key, "md5"

def get_cluster_info(name, i, info):
  print("get_cluster_info", name, i, info)
  try:
    infofile = open(os.path.join(CLUSTERS, cluster_dir(name, i), info), "rb")
    data=infofile.read()
    infofile.close()
  except:
    #traceback.print_exc()
    return None
  return data

def register_node(cluster, i, node):
  # create node file in cluster directory
  clusterdir = os.path.join(CLUSTERS, cluster_dir(cluster, i))
  if not os.path.isdir(clusterdir):
    return False, "no such cluster"
  nodefile = os.path.join(clusterdir, node+"#key")
  try:
    nodef = os.fdopen(os.open(nodefile, os.O_CREAT | os.O_EXCL | os.O_WRONLY), "wb")
  except OSError as e:
    return False, "node already exists"
  nodekey = new_key()
  nodef.write(nodekey)
  nodef.close()
  return True, nodekey


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
  if not validatename(nodename) or not validatename(clustername) or not validatename(i):
    print(json.dumps((False, "bad name")))
  else:
    providedhmac = data.getfirst("hmac").lower()
    msg = ("|".join((clustername, i, nodename))).encode("ascii")
    print(repr(clustername), repr(i))
    key = get_cluster_info(clustername, i, "key")
    hmacalg = get_cluster_info(clustername, i, "hashalg") or "md5"
    print("key=", repr(key))
    msghmac = HMAC.new(key or b"-"*KEYLENGTH, msg).hexdigest()
    print("provided=", repr(providedhmac))
    print("calculated=", repr(msghmac))
    authentic = compare_hashes(providedhmac, msghmac) and (key is not None)
    if authentic:
      print ("will register")
      res, data = register_node(clustername, i, nodename)
      if res:
        print ("encrypt", repr(data), "with", repr(key))
      else:
        print(json.dumps((False, data)))

    else:
      print(json.dumps((False, "not authenticated")))


else:
  print(json.dumps((False, "invalid parameter")))

