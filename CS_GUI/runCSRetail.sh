#!/bin/bash
export MPJ_HOME=$(pwd)/libraries/mpj-v0_44/
export PATH=$MPJ_HOME/bin:$PATH
rm -r Results/CSLatency.csv
rm -r Results/CSNoise.csv
python2 Sim/RetailSimulator.py $1 $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11} ${12} ${13} ${14} ${15}> /dev/null 2>&1
pwd
mpjrun.sh -np $5  CheckSoftRetail Data/ $3 $7 $8 > result.txt
cd ..
