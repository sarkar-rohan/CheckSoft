#!/bin/bash
source ./progress_bar.sh
export MPJ_HOME=$(pwd)/libraries/mpj-v0_44/
export PATH=$MPJ_HOME/bin:$PATH
rm -r Results/CSLatency.csv
rm -r Results/CSNoise.csv
for (( i = 20; i <= 100; i=i+10 ))      ### Outer for loop ###
do
    for (( j = 1 ; j <= $1; j++ )) ### Inner for loop ###
    do
	  python2 Sim/Simulator.py 1000 $i 1 1 > /dev/null 2>&1
	  mpjrun.sh -np $i  CheckSoft Data/ 1 1
	  let prog=i-10+j*10/$1
	  draw_progress_bar $prog
    done

  echo "" #### print the new line ###
done
destroy_scroll_area
python2 Sim/plotScalability.py $1

