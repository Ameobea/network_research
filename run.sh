#!/bin/bash
# Executes the processor, analyzer, and generates a HTML report
cd process
python processAll.py
rm temp/*
cd ../analyze
python analyzer.py
python htmlgen.py "../process/results.json" "../report.html"
python compare.py -o ../comparison_results.json
python correlate.py -o ../correlation_results.json
rm correlation_results/*
python plotCorrelations.py
echo "All networks processed, analyzed, correlated, and plotted."
