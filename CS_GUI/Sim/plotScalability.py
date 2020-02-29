#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 21:28:37 2019

@author: ubuntu
"""
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import csv
#data = np.zeros(shape=(9,9))
latency = dict()
#from matplotlib.ticker import PercentFormatter
count = 0
sum = 0
iteration = int(sys.argv[1]);
event_label = ["HumanEnter", "StorageInstantiate","HumanExit", "StorageReturn","HandIn", "HandOut","StorageUpdate","averageLatency" ];
with open('Results/CSLatency.csv', 'r') as csvFile:
    reader = csv.reader(csvFile)
    temp = []
    for row in reader:
        temp.append([float(k) for k in row])
        if(count % iteration == iteration-1):
            i = count/iteration
            data = np.mean(np.asarray(temp),axis=0)
            print("==============================================")
            print("Level Of Concurrency: ",data[0])
            print("==============================================")
            for j, label in enumerate(event_label):
                print(label,"=",data[j+1])
            latency[data[0]] = dict((key, value) for (key, value) in zip(event_label, data[1:]))
            temp = []
        count = count + 1 
csvFile.close()

import matplotlib as mpl
mpl.use('TkAgg')
from pylab import *
#from Simulator import *
print(latency)

nProc = [20, 30, 40, 50, 60, 70, 80, 90, 100]
averageLatency = [latency[n]['averageLatency'] for n in nProc]
events = ['HumanEnter', 'StorageInstantiate','HumanExit', 'StorageReturn','HandIn', 'HandOut','StorageUpdate',];

# Plot 1: #process vs average latency
fig = plt.figure()
marker_on = [1]
colors = ['y', 'k', 'c', 'm', 'b', 'r', 'g','0.75']  # For category of algorithms
mstyle = ['*', '^', 'o', 's', 'p', 'x', 'd', 'h','.']
lstyle = ['-.'] + ['-'] * 7
# legend_elements = [
#     Line2D([0], [0], color=colors[i], marker=mstyle[i], markersize=9,
#            fillstyle='none', lw=lwidth[i],
#            linestyle=lstyle[i], label=alg_list[i]) for i in range(len(alg_list))
# ]
plot(nProc, averageLatency, label='All events', markevery=1, color=colors[0], marker=mstyle[0], markersize=15)
for i, event in enumerate(events):
    j = i + 1
    plot(nProc, [latency[n][event] for n in nProc],
         label=event, markevery=1, color=colors[j], marker=mstyle[j], markersize=5)

xlabel('Level of Concurrency')
ylabel('Average Latency (s)')
title('Average Latency vs Level of Concurrency')
legend(loc='upper left')

# Plot 2: pie chart of events
events = ['HandIn', 'HandOut', 'HumanEnter', 'HumanExit', 'StorageInstantiate', 'StorageReturn']
#sizes = array([latency[100][e] for e in events])
#sizes = sizes / sizes.max() * 100
# indices = permutation(len(sizes))
# sizes = sizes[indices]
# labels = array(events)[indices]

#fig1, ax1 = plt.subplots()
#ax1.pie(sizes, labels=events, autopct='%1.1f%%', shadow=True, startangle=90)
#ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
#ax1.set_title('Relative Average Latency with 100 Processes')
fig.savefig('Results/plot_scalability.png')
#plt.show()

