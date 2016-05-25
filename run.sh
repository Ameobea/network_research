#!/bin/bash
# Executes the processor, analyzer, and generates a HTML report
cd process
python processAll.py
cd ../analyze
python analyzer.py
python htmlgen.py "../process/results.json" "../report.html"
