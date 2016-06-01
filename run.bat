REM Executes the processor, analyzer, and generates a HTML report
REM Written by Casey Primozic
cd process
python processAll.py
del /S temp\*.pk1
cd ..\analyze
python analyzer.py
python htmlgen.py "../process/results.json" "../report.html"
python compare.py -o ../comparison_results.json
python correlate.py -o ../correlation_results.json
del /S ..\correlation_plots\*
python plotCorrelations.py
cd ..
echo "All networks processed, analyzed, correlated, and plotted."
pause
