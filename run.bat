REM Executes the processor, analyzer, and generates a HTML report
REM Written by Casey Primozic
cd process
py processAll.py
del /S temp\*.pk1
cd ..\analyze
py analyzer.py
py htmlgen.py "../process/results.json" "../report.html"
py compare.py -o ../comparison_results.json
py correlate.py -o ../correlation_results.json
del /S ..\correlation_plots\*
python plotCorrelations.py
cd ..
echo "All networks processed, analyzed, correlated, and plotted."
pause
