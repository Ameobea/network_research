# Automated network processing script
# Written by Sammantha Nowak-Wolff, Casey Primozic, and AnnaLee Knapp

import networkx as nx
import os, threading
import Queue, sys, trace, os, pickle
import json, uuid, getopt, subprocess, time
from datetime import datetime

if sys.argv[1:] == []:
  maxRunTime = 30
  threads = 3

  calcQ = []
  workerQ = []
  for i in range(0, threads+1):
    workerQ.append(False)

# Searches given directory for network files, imports them, and runs process() on each
def processAll(dir):
  print("Processing all networks in " + dir + "...")
  startTime = datetime.now()
  if not(dir):
    dir="./"
  else:
    dir=os.path.relpath(dir)

  for file in os.listdir(dir):
    ext = file.split(".")[-1]
    if ext == "gml" or ext == "net" or ext == "txt":
      g=loadNetwork(dir+"/"+file, ext)
      if not(type(g) == bool):
        process(g, file)

  for worker in workerQ:
    calcNext()
  time.sleep(.1)
  # This assumes that the main thread can load the networks faster than the worker threads
  # can calculate.  If not, unloaded networks may be lost.
  startWorkerManager(startTime)

# Applies various network analysis functions to the given network
# and prints the results.
# ========================================================
# DO NOT USE THE CHARACTERS _ or - in calculation names
# ========================================================
def process(a, networkFilename):
  queueCalc("nx.degree", (a,), "degree", networkFilename)
  queueCalc("nx.density", (a,), "density", networkFilename)
  queueCalc("nx.is_directed", (a,), "isDirected", networkFilename)
  queueCalc("nx.number_of_nodes", (a,), "nodeCount", networkFilename)
  queueCalc("nx.number_of_edges", (a,), "edgeCount", networkFilename)
  queueCalc("nx.is_chordal", (a,), "isChordal", networkFilename)
  queueCalc("nx.radius", (a,), "radius", networkFilename)
  queueCalc("nx.center", (a,), "center", networkFilename)
  queueCalc("nx.transitivity", (a,), "transitivity", networkFilename)
  queueCalc("nx.is_connected", (a,), "isConnected", networkFilename)
  queueCalc("nx.average_neighbor_degree", (a,), "averageNeighborDegree", networkFilename)
  queueCalc("nx.average_clustering", (a,), "averageClustering", networkFilename)
  queueCalc("nx.triangles", (a,), "trianglesPerNode", networkFilename)
  queueCalc("nx.closeness_centrality", (a,), "closenessCentrality", networkFilename)
  queueCalc("nx.eigenvector_centrality", (a,), "eigenvectorCentrality", networkFilename)
  queueCalc("nx.betweenness_centrality", (a,), "betweennessCentrality", networkFilename)
  queueCalc("nx.graph_clique_number", (a,), "cliqueNumber", networkFilename)
  queueCalc("nx.average_node_connectivity", (a,), "averageNodeConnectivity", networkFilename)
  queueCalc("nx.average_degree_connectivity", (a,), "averageDegreeConnectivity", networkFilename)
  queueCalc("nx.number_connected_components", (a,), "numberConnectedComponents", networkFilename)
  queueCalc("nx.degree_assortativity_coefficient", (a,), "degreeAssortativityCoefficient", networkFilename)
  #queueCalc("nx.k_core", (a,), "kCore", networkFilename) #returns a network, so is disabled
  queueCalc("nx.is_eulerian", (a,), "isEulerian", networkFilename)

# Parses a .gml or pajek-formatted network and loads as a networkx network object
def loadNetwork(f, ext):
  if ext == "gml":
    try:
      return nx.read_gml(f)
    except Exception, e:
      print("Couldn't load " + f + " as gml.")
      return False
  elif ext == "net":
    try:
      return nx.read_pajek(f)
    except Exception, e:
      print("Couldn't load " + f + " as pajek.")
      return False
  else: # assume it's just an adjacency list
    try:
      return nx.read_adjlist(f)
    except Exception, e:
      print(e)
      print("Couldn't load " + f + " as adjacency list.")

# This is an interruptible thread that is created by the calcOne() function
# for all of the networkx computations.  The purpose of this is to allow
# very long calculations to be interruptible and, in the future, be parallelized.
# It uses a trace that monitors each line of execution and monitors an internal `killed`
# state that can be toggled to instantly kill the thread cleanly from within.
class workerThread(threading.Thread):
  def __init__(self, func, args, q):
    threading.Thread.__init__(self)
    self.func = func
    self.args = args
    self.q=q
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
    if why == "call":
      return self.localtrace
    else:
      return None

  def localtrace(self, frame, why, arg):
    if self.killed:
      if why == "line":
        raise SystemExit()
    return self.localtrace

  def kill(self):
    self.killed = True

  def run(self):
    try:
      res = {"res": self.func(*self.args)}
    except Exception, e:
      res = {"error": str(e)}
      isError = True
    self.q.put(res)

# Queues a calculation
def queueCalc(func, args, name, networkFilename):
  calcQ.append({"name": name, "func": func, "args": args, "started": False, "networkFilename": networkFilename})

# Starts a new calculation on an idle worker
def calcNext():
  for taskIndex, task in enumerate(calcQ):
    if not(calcQ[taskIndex]["started"]): # Finds first unstarted task
      calcQ[taskIndex]["started"] = True
      calcQ[taskIndex]["startTime"] = datetime.now()
      for workerIndex, worker in enumerate(workerQ):
        if not(worker):
          # Start calculation on newly avaliable worker on a new thread
          workerQ[workerIndex] = calcOne(task["func"], task["args"], task["name"], task["networkFilename"])
          print("Starting calculation " + task["name"])
          break
      break

# Initiate a worker process
def calcOne(func, args, calcName, networkFilename):
  tempFileName = "temp/" + str(uuid.uuid4()) + ".pk1"
  pickle.dump(args, open(tempFileName, "w")) # dump args to temp file
  scriptArgs = ["python", "processor.py", func, tempFileName, calcName, str(maxRunTime), networkFilename]

  try:
    return subprocess.Popen(scriptArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  except subprocess.CalledProcessError as e:
    print("Error in worker process: " + e.output)

# Spawns a worker thread with `func` and begins the calculation.
# args in the form of a tuple, cannot contain q as an argument
def doCalc(func, args, maxTime):
  q = Queue.Queue()
  t = workerThread(func, args, q)
  t.start()
  t.join(maxTime)
  if t.isAlive():
    t.kill()
    return {"error": "Timed out"}
  else:
    return q.get()

# Continuously monitor for workers to be done and queue up new
# calculations as needed.
def startWorkerManager(startTime):
  resultFiles = []
  while workerQ:
    empty = True
    for i, worker in enumerate(workerQ):
      if worker:
        empty = False
        status = worker.poll()
        if status is not None: # Finished
          resultFiles.append(worker.communicate()[0].strip()) # get the result file from worker and save it
          workerQ[i] = False # set worker to idle state
          calcNext() # start next calculation
        else:
          time.sleep(.1)
          continue
    if empty:
      processResults(resultFiles)
      print("All networks processed in " + str(datetime.now() - startTime))
      sys.exit(0)

# Read results out of the result files and save them to a readable JSON format
def processResults(resultFiles):
  j = {}
  for resFileName in resultFiles:
    with open(resFileName, "r") as resFile:
      res = pickle.load(resFile)
      for calc in calcQ:
        if calc["name"] == res["name"]:
          diff = res["endTime"] - calc["startTime"]
          break
      resObject = {"name": res["name"], "data": res["data"], "runTime": diff.seconds + diff.microseconds/1000000.0}
      if res["networkFilename"] in j:
        j[res["networkFilename"]].append(resObject)
      else:
        j[res["networkFilename"]] = [resObject]
      #os.remove(resFileName)
  with open("results.json", "w") as outFile:
    outFile.write(json.dumps(j))

# python samm_script.py func argFile calcName maxTime filename
# args are filenames containing pickled arguments
if sys.argv[1:] != []:
  with open(sys.argv[2], "r") as argFile:
    args = pickle.load(argFile)
    #os.remove(sys.argv[2])
  res = doCalc(eval(sys.argv[1]), args, int(sys.argv[4]))
  resObject = {"networkFilename": sys.argv[5], "name": sys.argv[3], "data": res, "endTime": datetime.now()}
  resFileName = "temp/" + str(uuid.uuid4()) + ".pk1"
  pickle.dump(resObject, open(resFileName, "w")) # store results in temporary file
  print(resFileName)
  sys.exit(0)
