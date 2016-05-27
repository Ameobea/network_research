# Network attribute correlation plotter
#
# Takes in the correlation pairs generated in `correlate.py` as input and
# generates graphics that can be used for manual analysis of the correlations.
#
# Casey Primozic
#
# Usage: python plotCorrelations.py -i res.json -o ./out_dir # input is the results file from `correlate.py`
# python plotCorrelations.py # defaults to -i ./correlation_pairs.json -o ./correlationPlots

import json, getopt, sys, os
import matplotlib.pyplot as plt

try:
  opts, args = getopt.getopt(sys.argv, "i:o:", ["in=", "out="])
except getopt.GetoptError:
  print("Usage: python correlate.py -i res.json -o out.json")
  sys.exit(2)

inFileName = "./correlation_pairs.json"
outDirectory = "./correlation_plots"

for opt, arg in opts:
  if opt == "-h":
    print("Usage: python compare.py -i res.json -o out.json")
  elif opt == "-i":
    inFileName = arg
  elif opt == "-o":
    outDirectory = os.path.relpath(arg)

if not(os.path.isdir(outDirectory)):
  os.mkdir(outDirectory)

inFile = open(inFileName, "r")
inData = json.load(inFile)

for pairName, pairData in inData.iteritems():
  plt.scatter(pairData[0], pairData[1], s=5)
  plt.savefig(outDirectory + "/" + pairName + ".png")
  plt.clf()
