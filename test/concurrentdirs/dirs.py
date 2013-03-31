#!/usr/bin/python3

import os
import sys

base = sys.argv[1]
myid = sys.argv[2]
count = int(sys.argv[3])

n = 0
done = 0
while done<count:
  name = os.path.join(base, "%s-%03d"%(myid, n))
  try:
    os.mkdir(name)
    open(os.path.join(name, "test"), "w").write("file for %s #%d\n"%(myid, done))
    done += 1
  except:
    pass
  n = n+1
