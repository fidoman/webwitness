#!/usr/bin/python3

import sys
import urllib.request
import json
from Crypto.Hash import HMAC
import base64

# keep local track of cluster configuration
# file format must be the same as the one that exists on witness resource

# without proto
URL="127.0.0.1/cgi-bin/webwitness.py"


def usage():
  print("""
registercluster <name>
registernode <nodename> <cluster> <id> <key>
dropnode <nodename> <cluster> <id>
setoption clusteroption value
addwitness 
removewitness 

""")

if len(sys.argv)<2:
  usage()
  exit()

if sys.argv[1]=="registercluster":
  if len(sys.argv)!=3:
    usage()
    exit()

  name = sys.argv[2]
  req = "https://"+URL+"?newcluster="+name
  resp = urllib.request.urlopen(req)
  print ("http:", resp.status, resp.reason)
  if resp.status!=200:
    print ("bad status")
    exit()
  try:
    rawdata=resp.read().decode("ascii")
  except:
    print ("bad data")
    exit()

  print(rawdata)
  data = json.loads(rawdata)
  if data[0]:
    print("successful: name=%s id=%d key(base64)=%s hmac=%s"%tuple(data[1:]))
  else:
    print("error:", data[1])

elif sys.argv[1]=="registernode":
  if len(sys.argv)!=6:
    usage()
    exit()

  node=sys.argv[2]
  cluster=sys.argv[3]
  i=sys.argv[4]
  b64key=sys.argv[5]

  key=base64.b64decode(b64key.encode("ascii"))

  msg=("|".join((cluster, i, node))).encode("ascii")
  msghmac=HMAC.new(key, msg).hexdigest()

  print ("key=", repr(key))
  print ("msg=", msg)
  print ("HMAC=", msghmac)

  req = "http://"+URL+"?newnode="+node+"&cluster="+cluster+"&id="+i+"&hmac="+msghmac
  resp = urllib.request.urlopen(req)
  print ("http:", resp.status, resp.reason)
  if resp.status!=200:
    print ("bad status")
    exit()
  try:
    rawdata=resp.read().decode("ascii")
  except:
    print ("bad data")
    exit()

  print(rawdata)


else:
  usage()
