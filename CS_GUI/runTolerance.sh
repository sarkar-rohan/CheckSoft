#!/bin/bash
source ./progress_bar.sh
export MPJ_HOME=$(pwd)/libraries/mpj-v0_44/
export PATH=$MPJ_HOME/bin:$PATH
rm -r Results/CSLatency.csv
rm -r Results/CSNoise.csv
let count=0
for (( i = 1; i <= 10; i=i+1 ))      ### Outer for loop ###
do
    for (( j = 1; j <= 10; j=j+1 ))
    do 
    	for (( k = 1 ; k <= $1; k++ )) ### Inner for loop ###
    	do
	  let count++
	  #echo -n "$i/10 -- $j/10 -- $k"#
	  python Sim/Simulator.py 100 40 $i $j > /dev/null 2>&1
	  mpjrun.sh -np 40  CheckSoft Data/ $i $j
	  let prog=count/$1
	  draw_progress_bar $prog
    	done
    done
  echo "" #### print the new line ###
done
destroy_scroll_area
python Sim/plotTolerance.py $1
