# Network attribute analyzer
# Takes computed network attributes from `processor` as input and
# performs preliminary analysis such as calculating averages, maximums,
# minimums, etc.
#
# Casey Primozic with code from Sammantha Nowak-Wolff
#
# Usage:
# python analyzer.py                  # Uses default results file in ../process/results.json
# python analyzer.py "../other.json"  # Uses supplied results file

import json, pprint, sys

nodeDicts = ["degree", "averageNeighborDegree", "trianglesPerNode", "eigenvectorCentrality",
  "closenessCentrality", "betweenessCentrality", "averageDegreeConnectivity"]
special = [
  "center", # returns list of nodes
  "degreeAssortativityCoefficient" # requires numpy to be installed
]

def dictAverage(inDict):
  sum = 0
  for key in inDict:
    sum += inDict[key]
  if sum != 0:
    return sum/float(len(inDict))
  else:
    return 0

def dictMax(inDict):
  maxNum = 0
  if len(inDict) == 0:
    return 0
  for key in inDict:
    if maxNum < inDict[key]:
      maxNum = inDict[key]
  return maxNum

def dictMin(inDict):
  minNum = "null"
  if len(inDict) == 0:
    return 0
  for key in inDict:
    if minNum == "null":
      minNum = inDict[key]
    if minNum > inDict[key]:
      minNum = inDict[key]
  return minNum

# perform some basic operations on dictionary-based results
def processNodeDict(network):
  network['average'] = dictAverage(network)
  network['max'] = dictMax(network)
  network['min'] = dictMin(network)
  return network

def analyze(inData, filename):
  for network in inData.iteritems():
    for cIndex, calc in enumerate(network[1]):
      if "res" in calc["data"] and not("error" in calc["data"]):
        if calc["name"] in nodeDicts:
          inData[network[0]][cIndex] = processNodeDict(calc["data"]["res"])
  with open(filename, "w") as outFile:
    outFile.write(json.dumps(inData))
  print("Done analyzing network.")

def loadAndProcess():
  if sys.argv[1:] != []:
    inFileName = sys.argv[1]
  else:
    inFileName = "../process/results.json"

  with open(inFileName) as inFile:
    inData = json.load(inFile)
    analyze(inData, inFileName)

loadAndProcess()
