# Network attribute correlator
#
# Analyzes the attributes of networks for correlations by grouping the results into pairs
# and searching for patterns in their distribution.
#
# Casey Primozic
#
# Usage: python correlate.py -i res.json -o out.json # input is the results file from `process`/`analyze`
# python correlate.py # defaults to -i ../process/results.json -o ./correlation_pairs.json

import json, getopt, sys
import numpy, pprint

try:
  opts, args = getopt.getopt(sys.argv, "i:o:", ["in=", "out="])
except getopt.GetoptError:
  print("Usage: python correlate.py -i res.json -o out.json")
  sys.exit(2)

inFileName = "../process/results.json"
outfileName = "./correlation_pairs.json"

for opt, arg in opts:
  if opt == "-h":
    print("Usage: python correlate.py -i res.json -o out.json")
  elif opt == "-i":
    inFileName = arg
  elif opt == "-o":
    outfileName = arg

inFile = open(inFileName, "r")
inData = json.load(inFile)

allPairs = {} # allPairs["pairName"] = (baseValues, compValues)

for network in inData.iteritems():
  pairs = {} # (baseValues, compValues)
  subCalcs = []
  for calc in network[1]:
    for subCalc in calc["data"].iteritems():
      if not(calc["name"] + "-" + subCalc[0] in subCalc) and \
          isinstance(subCalc[1], (int, long, float,)): # only compare numeric values
        subCalcs.append((calc["name"] + "-" + subCalc[0], subCalc[1],))
  for baseSubcalc in subCalcs:
    for compSubcalc in subCalcs:
      pairName = baseSubcalc[0] + "_" + compSubcalc[0]
      if not(baseSubcalc == compSubcalc) and not(pairName in pairs) and \
          not(compSubcalc[0] + "_" + baseSubcalc[0] in pairs): # no self-comparisons, no reverse duplicates
        pairs[pairName] = (baseSubcalc[1], compSubcalc[1],)
  for pairName, pairValue in pairs.iteritems():
    if pairName in allPairs:
      newBaseValues = allPairs[pairName][0] + [pairValue[0]]
      newCompValues = allPairs[pairName][1] + [pairValue[1]]
    else:
      newBaseValues = [pairValue[0]]
      newCompValues = [pairValue[1]]
    allPairs[pairName] = (newBaseValues, newCompValues,)

for pairName, pairValue in allPairs.iteritems():
  correlation = numpy.corrcoef(pairValue).tolist()
  allPairs[pairName] = allPairs[pairName] + (correlation,)


with open(outfileName, "w") as outFile:
  outFile.write(json.dumps(allPairs))
print("All calculations processed and pairs saved to " + outfileName)
