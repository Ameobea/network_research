#!/bin/bash
# Executes the processor, analyzer, and generates a HTML report
cd process
python processAll.py
rm temp/*
cd ../analyze
python analyzer.py
python htmlgen.py "../process/results.json" "../report.html"
python compare.py -o ../comparison_results.json
