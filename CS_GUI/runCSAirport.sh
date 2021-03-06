#!/bin/bash
export MPJ_HOME=$(pwd)/libraries/mpj-v0_44/
export PATH=$MPJ_HOME/bin:$PATH
rm -r Results/CSLatency.csv
rm -r Results/CSNoise.csv
#python Sim/AirportSimulator_threaded.py $1 $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11} ${12} ${13} ${14} ${15}> /dev/null 2>&1
python Sim/AirportSimulator_threaded.py $1 $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11} ${12} ${13} ${14} ${15}> event_log.txt
pwd
mpjrun.sh -np $5  CheckSoftAirport Data/ $2 $3 $7 $8 > result.txt
cd ..
