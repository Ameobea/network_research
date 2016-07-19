# Automated network processing script
# Written by Sammantha Nowak-Wolff, Casey Primozic, and AnnaLee Knapp
# Modified by Charles Morris

import networkx as nx
import os, threading
import Queue, sys, trace, os, pickle
import json, uuid, getopt, subprocess, time
import hashlib
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

# Searches for mtx files and converts them to txt - CM
  for fileName in os.listdir(dir):
    ext = fileName.split(".")[-1]	
    if ext == "mtx":
      lines = open(dir+"/"+fileName).readlines()
      grph = fileName.split(".")[0]
      open(dir+"/"+grph+'.txt', 'w').writelines(lines[2:])

  for fileName in os.listdir(dir):
    ext = fileName.split(".")[-1]
    if ext == "gml" or ext == "net" or ext == "txt":
      g=loadNetwork(dir+"/"+fileName, ext)
      if not(type(g) == bool):
        tempFileName = "temp/" + str(uuid.uuid4()) + ".pk1"
        pickle.dump((g,), open(tempFileName, "w")) # dump args to temp file
        with open(dir + "/" + fileName, 'rb') as afile:
          hasher = hashlib.sha1()
          buf = afile.read(65536)
          while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(65536)
        process(tempFileName, fileName, hasher.hexdigest())

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
def process(argFileName, networkName, networkHash):
  queueCalc("nx.degree", "Degree", argFileName, "degree", networkName, networkHash)
  queueCalc("nx.density", "Density", argFileName, "density", networkName, networkHash)
  queueCalc("nx.is_directed", "Directed", argFileName, "isDirected", networkName, networkHash)
  queueCalc("nx.number_of_nodes", "Node Count", argFileName, "nodeCount", networkName, networkHash)
  queueCalc("nx.number_of_edges", "Edge Count", argFileName, "edgeCount", networkName, networkHash)
  queueCalc("nx.is_chordal", "Chordal", argFileName, "isChordal", networkName, networkHash)
  queueCalc("nx.radius", "Radius", argFileName, "radius", networkName, networkHash)
  queueCalc("nx.center", "Center", argFileName, "center", networkName, networkHash)
  queueCalc("nx.transitivity", "Transitivity", argFileName, "transitivity (global clustering coefficient)", networkName, networkHash)
  queueCalc("nx.is_connected", "Connected", argFileName, "isConnected", networkName, networkHash)
  queueCalc("nx.average_neighbor_degree", "Average Neighbor Degree", argFileName,
      "averageNeighborDegree", networkName, networkHash)
  queueCalc("nx.average_clustering", "Average Clustering", argFileName,
      "averageClustering", networkName, networkHash)
  queueCalc("nx.triangles", "Triangles per Node", argFileName, "trianglesPerNode",
      networkName, networkHash)
  queueCalc("nx.closeness_centrality", "Closeness Centrality", argFileName,
      "closenessCentrality", networkName, networkHash)
  queueCalc("nx.eigenvector_centrality", "Eigenvector Centrality", argFileName,
      "eigenvectorCentrality", networkName, networkHash)
  queueCalc("nx.betweenness_centrality", "Betweeness Centrality", argFileName,
      "betweennessCentrality", networkName, networkHash)
  queueCalc("nx.graph_clique_number", "Clique Number", argFileName, "cliqueNumber",
      networkName, networkHash)
  #queueCalc("nx.average_node_connectivity", "Average Node Connectivity", argFileName,
      #"averageNodeConnectivity", networkName, networkHash)
  queueCalc("nx.average_degree_connectivity", "Average Degree Connectivity", argFileName,
      "averageDegreeConnectivity", networkName, networkHash)
  queueCalc("nx.number_connected_components", "Number of Distinct Connected Components",
      argFileName, "numberConnectedComponents", networkName, networkHash)
  queueCalc("nx.degree_assortativity_coefficient", "Degree Assortativity Coefficient",
      argFileName, "degreeAssortativityCoefficient", networkName, networkHash)
  queueCalc("nx.is_eulerian", "Eulerian", argFileName, "isEulerian", networkName, networkHash)
  queueCalc("nx.triadic_census", "Triadic Census", argFileName, "triadicCensus",
      networkName, networkHash)
  #queueCalc("nx.dispersion", "Dispersion", argFileName, "dispersion", networkName, networkHash)
  queueCalc("nx.bipartite.is_bipartite", "Bipartite", argFileName, "isBipartite",
      networkName, networkHash)
  queueCalc("nx.eccentricity", "Eccentricity", argFileName, "eccentricity",
      networkName, networkHash)
  queueCalc("nx.rich_club_coefficient", "Rich Club Coefficient", argFileName,
      "richClubCoefficient", networkName, networkHash)
  #queueCalc("nx.flow_hierarchy", "Flow Heirarchy", argFileName, "flowHierarchy",
      #networkName, networkHash)

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
def queueCalc(func, clearName, argFileName, name, networkName, networkHash):
  calcQ.append({"name": name, "clearName": clearName, "func": func,
      "argFileName": argFileName, "hash": networkHash,
      "started": False, "networkName": networkName})

# Starts a new calculation on an idle worker
def calcNext():
  for taskIndex, task in enumerate(calcQ):
    if not(calcQ[taskIndex]["started"]): # Finds first unstarted task
      calcQ[taskIndex]["started"] = True
      calcQ[taskIndex]["startTime"] = datetime.now()
      for workerIndex, worker in enumerate(workerQ):
        if not(worker):
          # Start calculation on newly avaliable worker on a new thread
          workerQ[workerIndex] = calcOne(task["func"], task["clearName"], task["argFileName"],
              task["name"], task["networkName"], task["hash"])
          print("Starting calculation " + task["name"])
          break
      break

# Initiate a worker process
def calcOne(func, clearName, argFileName, calcName, networkName, networkHash):
  scriptArgs = ["python", "processor.py", func, argFileName, calcName, str(maxRunTime),
      networkName, networkHash, clearName]

  try:
    return subprocess.Popen(scriptArgs, stdout=subprocess.PIPE)
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
          communication = worker.communicate()
          resultFiles.append(communication[0].strip()) # get the result file from worker and save it
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
      resObject = {"name": res["name"], "clearName": res["clearName"],
          "data": res["data"], "runTime": diff.seconds + diff.microseconds/1000000.0,
          "hash": res["hash"]}
      if res["networkName"] in j:
        j[res["networkName"]].append(resObject)
      else:
        j[res["networkName"]] = [resObject]
  with open("results.json", "w") as outFile:
    outFile.write(json.dumps(j))

# python samm_script.py func argFile calcName maxTime filename
# args are filenames containing pickled arguments
if sys.argv[1:] != []:
  with open(sys.argv[2], "r") as argFile:
    args = pickle.load(argFile)
  res = doCalc(eval(sys.argv[1]), args, int(sys.argv[4]))
  resObject = {"networkName": sys.argv[5], "clearName": sys.argv[7], "name": sys.argv[3], "data": res, "endTime": datetime.now(), "hash": sys.argv[6]}
  resFileName = "temp/" + str(uuid.uuid4()) + ".pk1"
  pickle.dump(resObject, open(resFileName, "w")) # store results in temporary file
  print(resFileName)
  sys.exit(0)
