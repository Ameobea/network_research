# Automated network processing script
# Written by Sammantha Nowak-Wolff and Casey Primozic

import networkx as nx
import os, threading
import Queue, sys, trace

maxRunTime = 300

def processAll():
  processAll(False)

# Searches given directory for network files, imports them, and runs process() on each
def processAll(dir):
  if not(dir):
    dir="./"
  else:
    dir=os.path.relpath(dir)
  for file in os.listdir(dir):
    ext = file.split(".")[-1]
    if ext == "gml" or ext == "net":
      print("\nProcessing " + file + ":")
      g=loadNetwork(dir+"/"+file)
      if(g):
        process(g)

# Applies various network analysis functions to the given network
# and prints the results.
def process(a):
  try:
    chordal= nx.is_chordal(a)
    print("Chordal: " + str(chordal))
  except Exception, e:
    print("Chordal: " + str(e))

  try:
    radius= nx.radius(a)
    print("Radius: " + str(radius))
  except Exception, e:
    print("Radius: "+str(e))

  try:
    center= nx.center(a)
    print("Center: " + str(center))
  except Exception, e:
    print("Center: " + str(e))

  try:
    transitivity = nx.transitivity(a)
    print("Transitivity: " + str(transitivity))
  except Exception, e:
    print("Transitivity: " + str(e))

  try:
    connected= nx.is_connected(a)
    print("Connected: " + str(connected))
  except Exception, e:
    print("Connected: " + str(e))
    
  print(nx.info(a))

  res=calc(nx.average_neighbor_degree, (a,), [getAverage, getMax])
  print("Average average neighbor degree: " + str(res[0]))
  print("Max average neighbor degree: " + str(res[1]))

  res=calc(nx.average_clustering, (a,), False)
  print("Average clustering: " + str(res))

  try:
    res=calc(nx.triangles, (a,), [getAverage, getMax])
  except Exception, e:
    print("Triangles: " + str(e))

  res=calc(nx.closeness_centrality, (a,), [getAverage, getMax])
  print("Average closeness centrality: " + str(res[0]))
  print("Max closeness centrality: " + str(res[1]))

  try:
    res=calc(nx.eigenvector_centrality, (a,), [getAverage, getMax])
  except Exception, e:
    print("Eigenvector centrality: " + str(e))
  print("Average eigenvector centrality: " + str(res[0]))
  print("Max eigenvector centrality: " + str(res[1]))

# Parses a .gml or pajek-formatted network and loads as a networkx network object
def loadNetwork(f):
  try:
    return nx.read_gml(f)
  except Exception, e:
    try:
      return nx.read_pajek(f)
    except Exception, e:
      print("Network cannot be parsed.")
      return False

# Returns the average value for a dictionary of numbers
def getAverage(d):
  if d=="Took too long":
    return d

  sum=0
  for key in d:
    sum += d[key]

  if sum != 0:
    avg = sum/float(len(d))
    return avg
  else:
    return 0

# Returns the maximum value for a dictionary of numbers
def getMax(d):
  if d=="Took too long":
    return d

  max=0
  if len(d) == 0:
    return 0
  for key in d:
    if max<d[key]:
      max=d[key]

  return max

def calc(func, args):
  return calc(func, args, False)

class workerThread(threading.Thread):
  def __init__(self, func, args, q, postProc):
    threading.Thread.__init__(self)
    self.func = func
    self.args = args
    self.q=q
    self.postProc = postProc
    self.killed=False

  def start(self):
    self.__run_backup = self.run
    self.run = self.__run
    threading.Thread.start(self)

  def __run(self):
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup

  def globaltrace(self, frame, why, arg):
    if why == 'call':
      return self.localtrace
    else:
      return None

  def localtrace(self, frame, why, arg):
    if self.killed:
      if why == 'line':
        raise SystemExit()
    return self.localtrace

  def kill(self):
    self.killed = True

  def run(self):
    res=self.func(*self.args)
    if(self.postProc):
      res2=[]
      for proc in self.postProc:
        if res=="error":
          res2.append(res)
        else:
          res2.append(proc(res))
      self.q.put(res2)
    else:
      self.q.put(res)

# args in the form of a tuple, cannot contain q as an argument
# postProc in the form of a list which contains functions which are run on the result of func
def calc(func, args, postProc):
  q = Queue.Queue()
  t = workerThread(calcProcess, (func, args, q,), q, postProc)
  t.start()
  t.join(maxRunTime)
  if t.isAlive():
    t.kill()
    if not(postProc):
      return "Took too long"
    else:
      res=[]
      for proc in postProc:
        res.append("Took too long")
    return res
  else:
    return q.get()

# Function called by the worker thread in calc()
def calcProcess(func, args, q):
  try:
    return func(*args)
  except Exception, e:
    return "error"
