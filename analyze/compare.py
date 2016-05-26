# Network attribute comparer
#
# Compares all the properties of networks in a results file from `process`/`analyze`
# and returns the differences between their attributes in the form of another json file.
#
# Casey Primozic
#
# Usage: python compare.py -i res.json -o out.json # input is the results file from `process`/`analyze`
# python compare.py # defaults to -i ../process/results.json ./comparison_results.json

import json, getopt, sys

try:
  opts, args = getopt.getopt(sys.argv, "i:o:", ["in=", "out="])
except getopt.GetoptError:
  print("Usage: python compare.py -i res.json -o out.json")
  sys.exit(2)

inFileName = "../process/results.json"
outfileName = "./comparison_results.json"

for opt, arg in opts:
  if opt == "-h":
    print("Usage: python compare.py -i res.json -o out.json")
  elif opt == "-i":
    inFileName = arg
  elif opt == "-o":
    outfileName = arg

inFile = open(inFileName, "r")
inData = json.load(inFile)

# Returns a list of comparisons between the two networks.
def compareNetwork(baseNetwork, compNetwork):
  res = {}
  for baseCalc in baseNetwork[1]:
    for compCalcTemp in compNetwork[1]:
      if compCalcTemp["name"] == baseCalc["name"]:
        compCalc = compCalcTemp
        break
    if not("error" in baseCalc["data"]) and not("error" in compCalc["data"]):
      res[baseCalc["name"]] = compareCalculation(baseCalc, compCalc)
  return res
# Compares two calculations and returns an analysis of their similarities/differences
def compareCalculation(baseCalc, compCalc):
  res = {}
  for elem in baseCalc["data"].iteritems():
    if elem[0] in compCalc["data"]:
      comparison = compareValue(baseCalc["data"][elem[0]], compCalc["data"][elem[0]])
      if not(comparison is None):
        res[elem[0]] = comparison
  return res

# Compares two values of varying types and returns results
def compareValue(baseValue, compValue):
  if type(baseValue) == bool:
    return compValue == baseValue
  elif isinstance(baseValue, (int, long, float)): # Numeric
    return compValue - baseValue
  else: # Assume it is a dictionary containing per-node numbers
    return None # Do nothing; should be handled in `analyzer.py` postprocessor

# mainResults["dolphins"] =
#   {"pgp": [attributeDifferences], "othernetwork": [attributeDifferences]}
mainResults = {}

for baseNetwork in inData.iteritems(): # baseNetwork == ("name", [{calculation}, {calculation}],)
  mainResults[baseNetwork[0]] = {}
  for compNetwork in inData.iteritems():
    if compNetwork[0] != baseNetwork[0] and \
        not(compNetwork[0] in mainResults and \
        baseNetwork[0] in mainResults[compNetwork[0]]): # don't compare with self or swaps
      mainResults[baseNetwork[0]][compNetwork[0]] = compareNetwork(baseNetwork, compNetwork)

with open(outfileName, "w") as outFile:
  outFile.write(json.dumps(mainResults))
print("All networks compared.\nResults written to " + outfileName)
