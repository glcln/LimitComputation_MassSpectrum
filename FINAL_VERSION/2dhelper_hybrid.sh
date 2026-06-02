python3 extractZPrimeXsecLimits_hybrid.py 

python3 harvestToContours.py --inputFile ZPrimeLimits.json  -x m2 -y m1 --useUpperLimit --debug --forbiddenFunction 2\*x --xMax 1400 -o output_BR100pct.root

python3 harvestToContours.py --inputFile ZPrimeLimits.json  -x m2 -y m1 --useUpperLimit --debug --forbiddenFunction 2\*x --xMax 1400 --level 0.1 -o output_BR10pct.root

python3 harvestToContours.py --inputFile ZPrimeLimits.json  -x m2 -y m1 --useUpperLimit --debug --forbiddenFunction 2\*x --xMax 1400 --level 0.001 -o output_BR1pct.root

python3 2dplot_new_hybrid.py outputGraphs.root
