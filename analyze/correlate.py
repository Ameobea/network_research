# Network attribute correlator
#
# Analyzes the attributes of networks for correlations by grouping the results into pairs
# and searching for patterns in their distribution.
#
# Casey Primozic
#
# Usage: python correlate.py -i res.json -o out.json # input is the results file from `process`/`analyze`
# python correlate.py # defaults to -i ../process/results.json ./correlation_pairs.json

import json, getopt, sys

try:
  opts, args = getopt.getopt(sys.argv, "i:o:", ["in=", "out="])
except getopt.GetoptError:
  print("Usage: python correlate.py -i res.json -o out.json")
  sys.exit(2)

inFileName = "../process/results.json"
outfileName = "./correlation_pairs.json"

for opt, arg in opts:
  if opt == "-h":
    print("Usage: python compare.py -i res.json -o out.json")
  elif opt == "-i":
    inFileName = arg
  elif opt == "-o":
    outfileName = arg

inFile = open(inFileName, "r")
inData = json.load(inFile)

pairs = {}
