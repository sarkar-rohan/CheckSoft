#!/usr/bin/env python
import csv
import numpy as np
from collections import Counter
from copy import copy, deepcopy
from random import shuffle
import sys 
import threading
# Types
HUMAN = 'HUMAN'
STORAGE = 'STORAGE'

# States
UNINITIALIZED = 'UNINITIALIZED'
IDLE = 'IDLE'
EXITED = 'EXITED'
HANDSINSIDE = 'HANDSINSIDE'
UPDATEDNEEDED = 'UPDATEDNEEDED'

# Events
HUMANENTER = 'HUMANENTER'
HUMANEXIT = 'HUMANEXIT'
STORAGEENTER = 'STORAGEENTER'
STORAGEEXIT = 'STORAGEEXIT'
HANDSIN = 'HANDSIN'
HANDSOUT = 'HANDSOUT'
NOISE = 'NOISE'
STORAGEUPDATE = 'STORAGEUPDATE'
NOISEHANDSOUT = 'NOISEHANDSOUT'
# Transition tables -- (Current State, Event): Next State
humanTransitionTable = {
    (UNINITIALIZED, HUMANENTER): IDLE,
    (IDLE, HANDSIN): HANDSINSIDE,
    (IDLE, HUMANEXIT): EXITED,
    (HANDSINSIDE, HANDSOUT): IDLE,
}
storageTransitionTable = {
    (UNINITIALIZED, STORAGEENTER): IDLE,
    (IDLE, HANDSIN): HANDSINSIDE,
    (IDLE, STORAGEEXIT): EXITED,
    (HANDSINSIDE, HANDSOUT): IDLE,
}


class Entity(object):
    def __init__(self, idNum, entityType):
        super(Entity, self).__init__()
        self.type = entityType
        self.id = idNum
        self.auxiliaryId = -1
        self.currentState = UNINITIALIZED
        self.content = Counter()


class HumanEntity(Entity):
    """docstring for HumanEntity"""

    def __init__(self, idNum):
        super(HumanEntity, self).__init__(idNum, HUMAN)

    def processEvent(self, event, extraArgs=None):
        # Go to the next state according to the transition table
        if (self.currentState, event) in humanTransitionTable:
            nextState = humanTransitionTable[(self.currentState, event)]
        else:
#            print("Warning: illegal HumanEntity transition", \
#(self.currentState, event))
            nextState = self.currentState

        # Perform any necessary post-transition action
        if (self.currentState, event) == (UNINITIALIZED, HUMANENTER):
            # Initial items
            self.content.update(extraArgs)
        if (self.currentState, event) == (IDLE, HANDSIN):
            # Record the storage ID
            self.auxiliaryId = extraArgs[0]
        if (self.currentState, event) == (HANDSINSIDE, HANDSOUT):
            addedContent = set(extraArgs[0])
            removedContent = set(extraArgs[1])
            # Update the content that the human has
            self.content.update(addedContent)
            self.content.subtract(removedContent)
            self.content = self.content - Counter()  # Remove zero counts

        # Finally update the state
        self.currentState = nextState

        # Debug
        # self.printStatus()

    def printStatus(self):
        print("Human %d: currentState = %s, content = %s" %(self.id, self.currentState, self.content))


class StorageEntity(Entity):
    """docstring for StorageEntity"""

    def __init__(self, idNum):
        super(StorageEntity, self).__init__(idNum, STORAGE)

    def processEvent(self, event, extraArgs=None):
        # Go to the next state according to the transition table
        if (self.currentState, event) in storageTransitionTable:
            nextState = storageTransitionTable[(self.currentState, event)]
        else:
            print("Warning: illegal StorageEntity transition", (self.currentState, event))
            nextState = self.currentState

        # Perform any necessary post-transition action
        if (self.currentState, event) == (UNINITIALIZED, STORAGEENTER):
            # Initial items
            self.content.update(extraArgs)
        if (self.currentState, event) == (IDLE, HANDSIN):
            # Record the human ID
            self.auxiliaryId = extraArgs[0]
        if (self.currentState, event) == (HANDSINSIDE, HANDSOUT):
            addedContent = set(extraArgs[0])
            removedContent = set(extraArgs[1])
            self.auxiliaryId = -1
            # Update the content that the human has
            self.content.update(addedContent)
            self.content.subtract(removedContent)
            self.content = self.content - Counter()  # Remove zero counts

        # Finally update the state
        self.currentState = nextState

        # Debug
        # self.printStatus()

    def printStatus(self):
        print("Storage %d: currentState = %s, content = %s" %(self.id, self.currentState, self.content))


class Simulator(object):
    def __init__(self):
        super(Simulator, self).__init__()
        self.humanEntities = []
        self.storageEntities = []
        self.nObjectTypes = -1

    def generateRandomEventSequence(self, nHuman, sHuman, nStorage, sStorage, 
                                    objects, eventList, eventPDF, maxIter, maxHumans):
        
        self.humanEntities = [HumanEntity(i) for i in range(sHuman, sHuman+nHuman)]
        self.storageEntities = [StorageEntity(i) for i in range(sStorage, sStorage+nStorage)]
        self.nObjectTypes = len(set(objects))
        #print("Human Entities : ",self.humanEntities)
        #print("Storage Entities : ",self.storageEntities)
        timeStep = 0
        countHumans = 1;
        activeHumans = []
        eventSeqThread = []
        # Initial configurations
        #print("\nInitial content is: ")
        #print(self.counterToString(objects))
        #print("Initial distribution is:")
        #self.printStatus()
        
        print("\nStarting randomized simulation...")
        print("Human understandable text sequence is:")
        # Randomly distribute the objects to all storage units
        for o in list(objects.elements()):
            s = np.random.choice(self.storageEntities)
            s.content.update([o])
        # Storage units are initialized and exited outside the loop
        for i, s in enumerate(self.storageEntities):
            timeStep += 1
            s.processEvent(STORAGEENTER)
            #eventSequence.append((timeStep, STORAGEENTER, s.id, -1,
            #                      list(s.content.elements())))
            eventSeqThread.append((timeStep, STORAGEENTER, s.id, -1,
                                  []))
            #print("%d: Storage %d has entered with content %s." \
            #      % (timeStep, s.id, self.counterToString(s.content)))
        # Each iteration represents an event at a distinct time
        humanActive = True
        newHumanId = sHuman
        while humanActive and timeStep < maxIter:
            # Randomly choose an event
            event = np.random.choice(eventList, p=eventPDF)
            if(len(activeHumans)==0) : 
                event = HUMANENTER
            if event == HUMANENTER : 
                human = np.random.choice(self.humanEntities)
            else :
                if(len(activeHumans)>0):
                    human = np.random.choice(activeHumans)
            if event == HUMANENTER and countHumans < maxHumans :
                #print("Event",event)
                if human.currentState == UNINITIALIZED:
                    human.processEvent(event)
                    human.id = newHumanId
                    newHumanId += 1
                    timeStep += 1
                    eventTuple = (timeStep, HUMANENTER, human.id, -1, [])
                    eventSeqThread.append(eventTuple)
                    countHumans += 1
                    activeHumans.append(human)
                    #print("%d: Human %d has entered with content %s." \
                    #      % (timeStep, human.id,
                    #         self.counterToString(human.content)))
            elif event == HUMANEXIT:
                if human.currentState == IDLE:
                    human.processEvent(event)
                    timeStep += 1
                    eventTuple = (timeStep, HUMANEXIT, human.id)
                    eventSeqThread.append(eventTuple)
                    countHumans -= 1
                    activeHumans.remove(human)
                    #print("%d: Human %d has exited with content %s." \
                    #      % (timeStep, human.id,
                    #         self.counterToString(human.content)))
            elif event == HANDSIN:
                storage = np.random.choice(self.storageEntities)
                if human.currentState == IDLE and storage.currentState == IDLE:
                    human.processEvent(event, [storage.id])
                    storage.processEvent(event, [human.id])
                    timeStep += 1
                    eventTuple = (timeStep, HANDSIN, human.id, storage.id,
                                  deepcopy(storage.content))
                    eventSeqThread.append(eventTuple)
                    #print("%d: Human %d puts hand into storage %d." % \
                    #      (timeStep, human.id, storage.id))
            elif event == HANDSOUT:
                #print("Aux id = ",human.auxiliaryId)
                for sx in self.storageEntities:
                    if sx.id == human.auxiliaryId:
                        storage = sx
                        break
                if human.currentState == HANDSINSIDE:
                    # Give one random item and also take one
                    if len(human.content) != 0:
                        contentToStorage = [np.random.choice(
                            list(human.content.elements()))]
                    else:
                        contentToStorage = []
                    if len(storage.content) != 0:
                        contentFromStorage = [np.random.choice(
                            list(storage.content.elements()))]
                    else:
                        contentFromStorage = []
                    human.processEvent(
                        event, (contentFromStorage, contentToStorage))
                    storage.processEvent(
                        event, (contentToStorage, contentFromStorage))
                    timeStep += 1
                    eventTuple = (timeStep, HANDSOUT, human.id, storage.id,
                                  contentToStorage, contentFromStorage,
                                  deepcopy(storage.content))
                    eventSeqThread.append(eventTuple)
                    #print("%d: Human %d pulls hand out from storage %d, " \
                    #      "adding %s and removing %s." % \
                    #      (timeStep, human.id, storage.id,
                    #       contentToStorage, contentFromStorage)) 
                    # print "%d: Human %d pulls hand out from storage %d." % \
                    #       (timeStep, human.id, storage.id)
                    # timeStep += 1
                    # print "%d: Human %d added %s to and removed %s from " \
                    #       "storage %d" % \
                    #       (timeStep, human.id, contentToStorage,
                    #        contentFromStorage, storage.id)
            elif event == NOISE:
                if human.currentState == IDLE:
                    # Simulate wrong human handout when there was no handin
                    storage = np.random.choice(self.storageEntities)
                    eventTuple = (timeStep, NOISEHANDSOUT, human.id, storage.id,
                                  [], [], Counter())
                    eventSeqThread.append(eventTuple)
                    timeStep += 1
                    #print("%d: NOISE -- Human %d pulls hand out from storage " \
                    #      "%d. No item displaced." % \
                    #      (timeStep, human.id, storage.id))
                    # print "%d: NOISE -- Human %d pulls hand out from storage " \
                    #       "%d." % (timeStep, human.id, storage.id)
                    # timeStep += 1
                    # print "%d: NOISE -- no item displaced." % timeStep
                elif human.currentState == HANDSINSIDE:
                    # Simulate wrong human handin
                    pass
                else:
                    pass
            else:
                continue;
                raise "Event %s not recognized." % event

            # Exit when all human entities have exited
            humanActive = any([
                h.currentState != EXITED for h in self.humanEntities
            ])
        """
        for i, s in enumerate(self.storageEntities):
            timeStep += 1
            s.processEvent(STORAGEEXIT)
            eventSeqThread.append((timeStep, STORAGEEXIT, s.id))
        """
            #print("%d: Storage %d has exited with content %s." \
            #      % (timeStep, s.id, self.counterToString(s.content)))

        #print("\nSimulation has finished, final distribution is:")
        #self.printStatus()
        #print(eventSequence)
        return eventSeqThread

    def eventSequenceToCSV(self, eventSequence, nStorage, nObjTypes,
                           countNoiseProb=0.0, countNoiseMaxNumNoisy=5,
                           countNoiseMaxNum=10):
        """
        Write an event sequence into a main .csv file and multiple .csv files,
        one for each storage entity.
        :param eventSequence:
        :param nStorage:
        :param countNoiseProb: probability for any count to contain noise
        :param countNoiseMaxNumNoisy: max number of noisy snapshots
        :param countNoiseMaxNum: total number of snapshots
        :return:
        """
        self.nObjectTypes = nObjTypes
        # [Count, time, event, entity_type, entity_id_x, entity_id_y(optional),
        # Content(optional)]
        delimiter = ','

        storageCsvWriters = []
        storageCsvFiles = []
        for i in range(1, nStorage+1):
            csvfile = open('Data/storage_%d.csv' % i, 'wb')
            wrtr = csv.writer(csvfile, delimiter=delimiter)
            storageCsvFiles.append(csvfile)
            storageCsvWriters.append(wrtr)
        
        seq_csvfile = open('Data/eseq.csv', 'wb')
        seq_wrtr = csv.writer(seq_csvfile, delimiter=delimiter)
        contentDeltaCsvFile = open('Data/contentDelta.csv', 'wb')
        contentDeltaCsvWriter = csv.writer(contentDeltaCsvFile, delimiter=delimiter)
        for eno, eventTuple in enumerate(eventSequence):
            timeStep = eventTuple[0]
            event = eventTuple[1]
            toEntity = -1
            fromEntity = eventTuple[2]
            contentString = ''
            counterSnapshot = None
            # if np.random.random() < seqNoiseProb:
            #     addSeqNoise = True
            # else:
            #     addSeqNoise = False

            # Write to the master csv file
            if event == HUMANENTER:
                #initialContent = eventTuple[4]
                seq_wrtr.writerow((6, eno+1, 0, 0, fromEntity, timeStep))
                contentDeltaCsvWriter.writerow(())
            elif event == STORAGEENTER:
                #initialContent = eventTuple[4]
                seq_wrtr.writerow((6, eno+1, 1, 1, fromEntity, timeStep))
                contentDeltaCsvWriter.writerow(())
            elif event == HUMANEXIT:
                seq_wrtr.writerow((6, eno+1, 2, 0, fromEntity, timeStep))
                contentDeltaCsvWriter.writerow(())
            elif event == STORAGEEXIT:
                seq_wrtr.writerow((6, eno+1, 3, 1, fromEntity, timeStep))
                contentDeltaCsvWriter.writerow(())
            elif event == HANDSIN:
                toEntity = eventTuple[3]
                counterSnapshot = eventTuple[4]
                seq_wrtr.writerow((6, eno+1, 6, 1, toEntity, timeStep))
                seq_wrtr.writerow((7, eno+1, 4, 2, fromEntity, toEntity, timeStep))
                contentDeltaCsvWriter.writerow(())
                # if addSeqNoise:
                #     wrtr.writerow((6, timeStep, 4, 2, fromEntity, toEntity))
            elif event == HANDSOUT:
                toEntity = eventTuple[3]
                contentToStorage = eventTuple[4]
                contentFromStorage = eventTuple[5]
                counterSnapshot = eventTuple[6]
                c = Counter(contentToStorage)
                c.subtract(contentFromStorage)
                seq_wrtr.writerow((6, eno+1, 6, 1, toEntity, timeStep))
                seq_wrtr.writerow((7, eno+1, 5, 2, fromEntity, toEntity, timeStep))
                # timeStep += 1
                # wrtr.writerow((5, timeStep, 6, 1, toEntity))

                # if addSeqNoise:
                #     timeStep += 1
                #     wrtr.writerow((6, timeStep, 5, 2, fromEntity, toEntity))
                contentDeltaCsvWriter.writerow((
                    timeStep, fromEntity, toEntity,
                    self.counterToString(c)))
            elif event == NOISEHANDSOUT:
                toEntity = eventTuple[3]
                seq_wrtr.writerow((7, eno+1, 5, 2, fromEntity, toEntity, timeStep))
                contentDeltaCsvWriter.writerow((
                    timeStep, fromEntity, toEntity,
                    'NA')) 
            else:
                raise "Event %s not recognized." % event
            # Write to the storage-specific csv files
            for i in range(nStorage):
                storageId = i+1
                if event == HANDSIN and toEntity == storageId:
                    # Count noise is added here
                    contentString = [self.counterToString(
                        self.copyCounterWithNoise(
                            counterSnapshot, countNoiseProb)
                    ) for j in range(countNoiseMaxNumNoisy)]
                    contentString += [self.counterToString(
                        counterSnapshot)] * (countNoiseMaxNum -
                                             countNoiseMaxNumNoisy)
                    #shuffle(contentString)
                    storageCsvWriters[i].writerow(contentString)

                    # if addSeqNoise:
                    #     storageCsvWriters[i].writerow(contentString)
                elif event == HANDSOUT:
                    if toEntity == storageId:
                        # Count noise is added here
                        contentString = [self.counterToString(
                            self.copyCounterWithNoise(
                                counterSnapshot, countNoiseProb)
                        ) for j in range(countNoiseMaxNumNoisy)]
                        contentString += [self.counterToString(
                            counterSnapshot)] * (countNoiseMaxNum -
                                                 countNoiseMaxNumNoisy)
                        #shuffle(contentString)
                        storageCsvWriters[i].writerow(contentString)

                        # if addSeqNoise:
                        #     storageCsvWriters[i].writerow(contentString)
                    else:
                        storageCsvWriters[i].writerow(())
                    # Extra blank row for storage update event
                    # storageCsvWriters[i].writerow(())
                else:
                    storageCsvWriters[i].writerow(())

        # Close all csv files
        seq_csvfile.close()
        contentDeltaCsvFile.close()
        for i in range(nStorage):
            storageCsvFiles[i].close()

    def printStatus(self):
        """
        Print status of all entities: human and storage
        :return:
        """
        allEntities = self.humanEntities + self.storageEntities
        for entity in allEntities:
            entity.printStatus()

    def copyCounterWithNoise(self, counter, prob):
        """
        Add noise to a counter object. Each count in the counter has prob
        probability to be incorrect by +/-5.
        :param counter:
        :param prob:
        :return:
        """
        """
        counter = deepcopy(counter)
        for i in range(self.nObjectTypes):
            noise = np.random.randint(1,5)
            if np.random.random() < prob:
                if np.random.random() > 0.5:
                    counter[i] += noise # false detections
                else:
                    counter[i] -= noise # missed detections
                if counter[i] < 0:
                    counter[i]=0
        return counter
        """
        counter = deepcopy(counter)
        for i in range(self.nObjectTypes):
            noise = np.random.randint(1,5)
            if np.random.random() > prob:
                continue
            if counter[i] == 0:
                # Noise could only be +1
                counter[i] = noise
            else:
                # Noise could be either +1 or -1
                if np.random.random() > 0.5:
                    counter[i] += noise
                else:
                    counter[i] -= noise
                if counter[i] < 0:
                    counter[i]=0
        return counter
    
    def counterToString(self, counter):
        """
        Convert items and counts in counter to a fixed length (nObjectTypes)
        list.
        :param counter:
        :param nObjectType:
        :return:
        """
        l = [0] * self.nObjectTypes
        #print(l)
        #print(counter.items())
        for i, c in counter.items():
            l[i] = c
        return '[' + ' '.join(str(x) for x in l) + ']'
def runner(sHi,sSi,nH, nS, obj, maxIter, maxH,\
            eventList, eventPDF, countNoiseProb, contentNoiseProb, frames):
    
    sim = Simulator()
    
    es_thread = sim.generateRandomEventSequence(
            nH, sHi, nS, sSi, obj, eventList, eventPDF, maxIter, maxH)
    #print("\nEvent tuples (internal to simulator) are:")
    #for t, e in enumerate(eventSeq):
    #    print(t, e)
    lck.acquire()
    for e_t in es_thread:
        eventSequence.append(e_t)
    lck.release()

def main():
        
    nTracker, nHuman, nStorage = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])/2
    # objects = ['Apple', 'Orange', 'Grape', 'Pear', 'Banana', 'Avocado',
    #            'Pineapple', 'Watermelon', 'Blueberry', 'Coconut']
    objects = Counter({0: 1000, 1: 2000, 2: 1000, 3: 1000, 4: 2000, 5: 1000, 6: 1000, 7: 2000, 8: 1000, 9: 1000})
    nObjectTypes = len(set(objects))
    eventList = [HUMANENTER, HUMANEXIT, HANDSIN, HANDSOUT, NOISE]
    eventPDF = np.array([0.1, 0.2, 0.5, 0.5, 0.2])
    eventPDF /= np.sum(eventPDF)
    maxHumans = int(sys.argv[3])/2-5
    maxIter = 1000000
    countNoiseProb=float(sys.argv[4])/10.0
    frames=10
    contentNoiseProb=float(sys.argv[5])/10.0
    sH = []
    dH = nHuman/nTracker
    sS = []
    dS = nStorage/nTracker
    dmaxH = maxHumans/nTracker
    threads = []
    for Tracker in range(0,nTracker):
        sH.append(Tracker*dH+1)
        sS.append(Tracker*dS+1)
    print("Division of Humans :",sH)
    print("Division of Storages :",sS)
    print("Max Humans/Tracker :",dmaxH)
    for i in range(0,nTracker):
        t = threading.Thread(target = runner, args = (sH[i],sS[i],dH, dS, objects, maxIter, dmaxH,\
        eventList, eventPDF, countNoiseProb, contentNoiseProb, frames))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    eventSequence.sort(key = lambda x: x[0])
    last_event = eventSequence[-1]
    timeStep = last_event[0]
    for s in range(nStorage):
            timeStep += 1
            #s.processEvent(STORAGEEXIT)
            eventSequence.append((timeStep, STORAGEEXIT, s))
    for eno, event in enumerate(eventSequence):
        print(eno, event)
    sim = Simulator()
    sim.eventSequenceToCSV(eventSequence, nStorage, nObjectTypes, countNoiseProb, int(contentNoiseProb*frames), frames)

lck = threading.Lock()
eventSequence = []
if __name__ == '__main__':
    main()
