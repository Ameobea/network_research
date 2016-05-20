import networkx as nx
import os
from multiprocessing import Process, Queue
import pprint

maxRunTime=30

def processAll():
  for file in os.listdir("./"):
    ext = file.split(".")[-1]
    if ext == "gml" or ext == "net":
      print("\nProcessing " + file + ":")
      g=loadNetwork(file)
      if(g):
        process(g)


def process(a):
  try:
    chordal= nx.is_chordal(a)
    print("Chordal: " + str(chordal))
  except Exception, e:
    print(e)

  try:
    center= nx.center(a)
    print(str(center))
  except Exception, e:
    print(e)

  try:
    transitivity= nx.transitivity(a)
    print(str(transitivity))
  except Exception, e:
    print(e)

  print(nx.info(a))
  print("max average neighbor degree: ")
  shortRun(pprint.pprint, (str(getMax(nx.average_neighbor_degree(a))), ), maxRunTime)

  print("max triangles: ")
  try:
    shortRun(pprint.pprint, (str(getMax(nx.triangles(a))), ), maxRunTime)
  except Exception, e:
    print(e)

  print("max closeness centrality: ")
  shortRun(pprint.pprint, (str(getMax(nx.closeness_centrality(a))), ), maxRunTime)

  print("max eigenvector centrality: ")
  try:
    shortRun(pprint.pprint, (str(getMax(nx.eigenvector_centrality(a))), ), maxRunTime)
  except Exception, e:
    print(e)

  print("average average neighbor: ")
  shortRun(pprint.pprint, (str(average(nx.average_neighbor_degree(a))), ), maxRunTime)

  print("average triangles: ")
  try:
    shortRun(pprint.pprint, (str(average(nx.triangles(a))), ), maxRunTime)
  except Exception, e:
    print(e)

  print("average closeness centrality")
  shortRun(pprint.pprint, (str(average(nx.closeness_centrality(a))), ), maxRunTime)

  print("average eigenvector centrality: ")
  try:
    shortRun(pprint.pprint, (str(average(nx.eigenvector_centrality(a))), ), maxRunTime)
  except Exception, e:
    print(e)

def average(d):
  sum=0
  for key in d:
    sum += d[key]

  avg = sum/float(len(d))
  return avg

def loadNetwork(f):
  try:
    return nx.read_gml(f)
  except Exception, e:
    try:
      return nx.read_pajek(f)
    except Exception, e:
      print("Network cannot be parsed.")
      return False

def getMax(d):
  max=0
  for key in d:
    if max<d[key]:
      max=d[key]

  return max

def shortRun(func, args, time):
  """Runs a function with time limit

  :param func: The function to run
  :param args: The functions args, given as tuple
  :param time: The time limit in seconds
  :return: True if the function ended successfully. False if it was terminated.
  """
  p = Process(target=func, args=args)
  p.start()
  p.join(time)
  if p.is_alive():
    p.terminate()
    return "Took too long"

  return True
