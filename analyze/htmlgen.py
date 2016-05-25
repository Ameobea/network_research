# HTML report generator
# Converts the JSON results file from the processor/analyzer into a
# formatted HTML document that can be viewed in a web browser.
#
# Casey Primozic
#
# Usage:
# python htmlgen.py # defaults to "../process/results.json" and "./report.html"
# python htmlgen.py injson.json outhtml.html # both arguments or none.

import json, sys

def generate(inData):
  html = "<html>\n<head>\n<title>Network analysis report</title>\n"
  html += "<script src='https://ameobea.me/sources/jquery-2.1.0.min.js'></script>\n<style>\n"
  with open("resources/report.css") as cssFile:
    html += cssFile.read()
  html += "</style>\n<script>\n"
  with open("resources/cruncher.js") as jsFile:
    html += jsFile.read()
  html += "\n</script>\n</head>\n<body>"
  for network in inData.iteritems(): # for each network
    res = tableHeaderGen(network)
    headerHtml = res[0]
    gMapping = res[1]
    html += "<table><tr><td><h1>" + network[0] + "</h1>\n<table id='resTable'>\n" + headerHtml + "\n"
    for cIndex, calc in enumerate(network[1]): # for each calculation
      html += "<tr><td><b>" + calc["name"] + "</b></td>\n"
      virtRow = ["<td></td>"] * len(gMapping)
      for a in calc["data"].iteritems(): # for each subcalculation
        if a[0] == "error":
          virtRow[0] = "<td><span class='error'>" + str(a[1]) + "</span></td>\n"
        else:
          result = str(a[1])
          if len(result) > 50:
            virtRow[gMapping.index(a[0])] = "<td><span class='long'>" + result + "</span></td>\n"
          else:
            virtRow[gMapping.index(a[0])] = "<td>" + result + "</td>\n"
      for td in virtRow:
        html += td
      html += "</tr>\n"
    html += "</table></td><td><div id='maximize'></div></td></tr></table>"
  html += "</body></html>"
  return html

def tableHeaderGen(network):
  gMapping = ["res"]
  html = "<tr><th>Calculation</th><th>Result</th>"
  for cIndex, calc in enumerate(network[1]):
    for name, val in calc["data"].iteritems(): # for each data point
      if not(name) in gMapping:
        gMapping.append(name)
        html += "<th>" + name + "</th>"
  html += "</tr>"
  return (html, gMapping,)

try:
  inFileName = sys.argv[1]
except Exception, e:
  inFileName = "../process/results.json"

try:
  outFileName = sys.argv[2]
except Exception, e:
  outFileName = "./report.html"

with open(inFileName, "r") as inFile:
  inData = json.load(inFile)
  html = generate(inData)

with open(outFileName, "w") as outFile:
  outFile.write(html)

print("Report saved to " + outFileName)
