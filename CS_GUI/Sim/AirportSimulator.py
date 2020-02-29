#!/usr/bin/env python
import csv
import numpy as np
from sets import Set
from copy import copy, deepcopy
from collections import Counter
import sys 
from random import shuffle
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
        self.storageEntities =[]
        self.ninteract = 0
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
        #if (self.currentState, event) == (UNINITIALIZED, STORAGEENTER):
            # Initial items
            #self.content.update(extraArgs)
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
        print "Storage %d: currentState = %s, content = %s" % \
              (self.id, self.currentState, self.content)


class Simulator(object):
    def __init__(self):
        super(Simulator, self).__init__()
        self.humanEntities = []
        self.storageEntities = []
        self.nObjectTypes = -1

    def runEventSequence(self, eventSequence):
        self.humanEntities = []
        self.storageEntities = []
        print "Starting deterministic simulation..."
        for timeStep, eventTuple in enumerate(eventSequence):
            event = eventTuple[0]
            fromEntity = eventTuple[1]
            if event == HUMANENTER:
                initialContent = eventTuple[3]
                self.humanEntities.append(HumanEntity(fromEntity))
                self.humanEntities[fromEntity].processEvent(event,
                                                            initialContent)
            elif event == STORAGEENTER:
                initialContent = eventTuple[3]
                self.storageEntities.append(StorageEntity(fromEntity))
                self.storageEntities[fromEntity].processEvent(event,
                                                              initialContent)
            elif event == HUMANEXIT:
                self.humanEntities[fromEntity].processEvent(event)
            elif event == STORAGEEXIT:
                self.storageEntities[fromEntity].processEvent(event)
            elif event == HANDSIN:
                toEntity = eventTuple[2]
                self.humanEntities[fromEntity].processEvent(event, [toEntity])
                self.storageEntities[toEntity].processEvent(event, [fromEntity])
            elif event == HANDSOUT:
                toEntity = eventTuple[2]
                contentToStorage = eventTuple[3]
                contentFromStorage = eventTuple[4]
                self.humanEntities[fromEntity].processEvent(
                    event, (contentFromStorage, contentToStorage))
                self.storageEntities[toEntity].processEvent(
                    event, (contentToStorage, contentFromStorage))
                print "%d: Human %d added %s to and removed %s from " \
                      "storage %d" % \
                      (timeStep, self.humanEntities[fromEntity].id,
                       contentToStorage, contentFromStorage,
                       self.storageEntities[toEntity].id)
            else:
                raise "Event %s not recognized." % event
        print "Simulation has finished..."

    def generateRandomEventSequence(self, nHuman, 
                                    eventList, eventPDF, maxIter, maxHumans,
                                    maxStorageperHuman, maxObjectsperHuman,mininteract):
        eventSequence = []
        self.humanEntities = [HumanEntity(i + 1) for i in range(nHuman)]
        #self.storageEntities = [StorageEntity(i + 1) for i in range(maxStorageperHuman)]
        self.nObjectTypes = maxObjectsperHuman
        timeStep = 0
        countHumans = 1;
        activeHumans = []
        activeStorages = []
        """
        # Initial configurations
        print "\nInitial content is: "
        print self.counterToString(objects)
        print "Initial distribution is:"
        self.printStatus()
        """
        print "\nStarting randomized simulation..."
        print "Human understandable text sequence is:"
        """
        # Randomly distribute the objects to all storage units
        for o in list(objects.elements()):
            s = np.random.choice(self.storageEntities)
            s.content.update([o])
        # Storage units are initialized and exited outside the loop
        for i, s in enumerate(self.storageEntities):
            timeStep += 1
            s.processEvent(STORAGEENTER)
            eventSequence.append((STORAGEENTER, s.id, -1,
                                  list(s.content.elements())))
            print "%d: Storage %d has entered with content %s." \
                  % (timeStep, s.id, self.counterToString(s.content)) 
        """
        # Each iteration represents an event at a distinct time
        humanActive = True
        newHumanId = 1
        newStorageId = 1
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
                if human.currentState == UNINITIALIZED:
                    human.processEvent(event)
                    human.id = newHumanId
                    newHumanId += 1
                    timeStep += 1
                    eventTuple = (HUMANENTER, human.id, -1, [])
                    eventSequence.append(eventTuple)
                    countHumans += 1
                    activeHumans.append(human)
                    human.content=Counter(list(np.random.randint(maxObjectsperHuman, size=maxObjectsperHuman)))

                    print "%d: Human %d has entered with content %s." \
                          % (timeStep, human.id,
                             self.counterToString(human.content))
                    for i in range(maxStorageperHuman):
                        timeStep += 1
                        s = StorageEntity(newStorageId)
                        human.storageEntities.append(s)
                        newStorageId +=1
                        s.processEvent(STORAGEENTER)
                        eventSequence.append((STORAGEENTER, s.id, -1,[]))
                        print "%d: Human %d instantiated Storage %d." \
                              % (timeStep, human.id, s.id) 
            elif event == HUMANEXIT:
                if human.currentState == IDLE and human.ninteract > mininteract:
                    for i, s in enumerate(human.storageEntities):
                        timeStep += 1
                        s.processEvent(STORAGEEXIT)
                        eventSequence.append((STORAGEEXIT, s.id))
                        print "%d: Storage %d has been returned with content %s." \
                              % (timeStep, s.id, self.counterToString(s.content)) 
                    human.processEvent(event)
                    timeStep += 1
                    eventTuple = (HUMANEXIT, human.id)
                    eventSequence.append(eventTuple)
                    countHumans -= 1
                    activeHumans.remove(human)
                    print "%d: Human %d has exited with content %s." \
                          % (timeStep, human.id,
                             self.counterToString(human.content))
                    
            elif event == HANDSIN:
                storage = np.random.choice(human.storageEntities)
                if human.currentState == IDLE and storage.currentState == IDLE:
                    human.processEvent(event, [storage.id])
                    storage.processEvent(event, [human.id])
                    timeStep += 1
                    eventTuple = (HANDSIN, human.id, storage.id,
                                  deepcopy(storage.content))
                    eventSequence.append(eventTuple)
                    print "%d: Human %d puts hand into storage %d." % \
                          (timeStep, human.id, storage.id) 
            elif event == HANDSOUT:
                for s in human.storageEntities:
                    if s.auxiliaryId == human.id:
                        storage = s
                        #storage = human.storageEntities[self.auxiliaryId - 1]
                if human.currentState == HANDSINSIDE:
                    # Give one random item and also take one
                    contentToStorage = []
                    contentFromStorage = []
                    if(np.random.random() <0.5):
                        if len(human.content) != 0:
                            contentToStorage = [np.random.choice(
                                list(human.content.elements()))]
                            human.ninteract += 1
                        else:
                            contentToStorage = []
                    else:
                        if len(storage.content) != 0:
                            contentFromStorage = [np.random.choice(
                                list(storage.content.elements()))]
                            human.ninteract += 1
                        else:
                            contentFromStorage = []
                    human.processEvent(
                        event, (contentFromStorage, contentToStorage))
                    storage.processEvent(
                        event, (contentToStorage, contentFromStorage))
                    timeStep += 1
                    eventTuple = (HANDSOUT, human.id, storage.id,
                                  contentToStorage, contentFromStorage,
                                  deepcopy(storage.content))
                    eventSequence.append(eventTuple)
                    print "%d: Human %d pulls hand out from storage %d, " \
                          "adding %s and removing %s." % \
                          (timeStep, human.id, storage.id,
                           contentToStorage, contentFromStorage) 
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
                    storage = np.random.choice(human.storageEntities)
                    eventTuple = (NOISEHANDSOUT, human.id, storage.id,
                                  [], [], Counter())
                    eventSequence.append(eventTuple)
                    timeStep += 1
                    print "%d: NOISE -- Human %d pulls hand out from storage " \
                          "%d. No item displaced." % \
                          (timeStep, human.id, storage.id)
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
            eventSequence.append((STORAGEEXIT, s.id))
            print "%d: Storage %d has exited with content %s." \
                  % (timeStep, s.id, self.counterToString(s.content)) 
        """
        print "\nSimulation has finished, final distribution is:" 
        self.printStatus()

        return eventSequence

    def eventSequenceToCSV(self, eventSequence, nStorage,
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
        # [Count, time, event, entity_type, entity_id_x, entity_id_y(optional),
        # Content(optional)]
        delimiter = ','

        storageCsvWriters = []
        storageCsvFiles = []
        for i in range(1, nStorage + 1):
            csvfile = open('Data/storage_%d.csv' % i, 'wb')
            wrtr = csv.writer(csvfile, delimiter=delimiter)
            storageCsvFiles.append(csvfile)
            storageCsvWriters.append(wrtr)

        csvfile = open('Data/eseq.csv', 'wb')
        wrtr = csv.writer(csvfile, delimiter=delimiter)
        contentDeltaCsvFile = open('Data/contentDelta.csv', 'wb')
        contentDeltaCsvWriter = csv.writer(contentDeltaCsvFile, delimiter=delimiter)
        timeStep = 1
        for eventTuple in eventSequence:
            event = eventTuple[0]
            toEntity = -1
            fromEntity = eventTuple[1]
            contentString = ''
            counterSnapshot = None
            # if np.random.random() < seqNoiseProb:
            #     addSeqNoise = True
            # else:
            #     addSeqNoise = False

            # Write to the master csv file
            if event == HUMANENTER:
                initialContent = eventTuple[3]
                wrtr.writerow((5, timeStep, 0, 0, fromEntity))
                contentDeltaCsvWriter.writerow(())
            elif event == STORAGEENTER:
                initialContent = eventTuple[3]
                wrtr.writerow((5, timeStep, 1, 1, fromEntity))
                contentDeltaCsvWriter.writerow(())
            elif event == HUMANEXIT:
                wrtr.writerow((5, timeStep, 2, 0, fromEntity))
                contentDeltaCsvWriter.writerow(())
            elif event == STORAGEEXIT:
                wrtr.writerow((5, timeStep, 3, 1, fromEntity))
                contentDeltaCsvWriter.writerow(())
            elif event == HANDSIN:
                toEntity = eventTuple[2]
                counterSnapshot = eventTuple[3]
		wrtr.writerow((5, timeStep, 6, 1, toEntity))
                wrtr.writerow((6, timeStep, 4, 2, fromEntity, toEntity))
                contentDeltaCsvWriter.writerow(())
                # if addSeqNoise:
                #     wrtr.writerow((6, timeStep, 4, 2, fromEntity, toEntity))
            elif event == HANDSOUT:
                toEntity = eventTuple[2]
                contentToStorage = eventTuple[3]
                contentFromStorage = eventTuple[4]
                counterSnapshot = eventTuple[5]
                c = Counter(contentToStorage)
                c.subtract(contentFromStorage)
		wrtr.writerow((5, timeStep, 6, 1, toEntity))
                wrtr.writerow((6, timeStep, 5, 2, fromEntity, toEntity))
                # timeStep += 1
                # wrtr.writerow((5, timeStep, 6, 1, toEntity))

                # if addSeqNoise:
                #     timeStep += 1
                #     wrtr.writerow((6, timeStep, 5, 2, fromEntity, toEntity))
                contentDeltaCsvWriter.writerow((
                    timeStep, fromEntity, toEntity,
                    self.counterToString(c)))
            elif event == NOISEHANDSOUT:
                toEntity = eventTuple[2]
                wrtr.writerow((6, timeStep, 5, 2, fromEntity, toEntity))
                contentDeltaCsvWriter.writerow((
                    timeStep, fromEntity, toEntity,
                    'NA')) 
            else:
                raise "Event %s not recognized." % event
            # Write to the storage-specific csv files
            for i in range(nStorage):
                storageId = i + 1
                if event == HANDSIN and toEntity == storageId:
                    # Count noise is added here
                    contentString = [self.counterToString(
                        self.copyCounterWithNoise(
                            counterSnapshot, countNoiseProb)
                    ) for j in range(countNoiseMaxNumNoisy)]
                    contentString += [self.counterToString(
                        counterSnapshot)] * (countNoiseMaxNum -
                                             countNoiseMaxNumNoisy)
                    shuffle(contentString)
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
                        shuffle(contentString)
                        storageCsvWriters[i].writerow(contentString)

                        # if addSeqNoise:
                        #     storageCsvWriters[i].writerow(contentString)
                    else:
                        storageCsvWriters[i].writerow(())
                    # Extra blank row for storage update event
                    # storageCsvWriters[i].writerow(())
                else:
                    storageCsvWriters[i].writerow(())

            timeStep += 1

        # Close all csv files
        csvfile.close()
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
            noise = np.random.randint(1,2)
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
        for i, c in counter.items():
            l[i] = c
        return '[' + ' '.join(str(x) for x in l) + ']'


def main(mode):
    if mode == 0:
        # Run a predetermined sequence
        eseq = [(HUMANENTER, 0, -1, ['Apple', 'Orange']),
                (STORAGEENTER, 0, -1, []),
                (HANDSIN, 0, 0), (HANDSOUT, 0, 0, ['Apple', 'Orange'], []),
                (HANDSIN, 0, 0), (HANDSOUT, 0, 0, [], ['Apple']),
                (HUMANEXIT, 0), (STORAGEEXIT, 0), ]
        sim = Simulator()
        sim.runEventSequence(eseq)
        sim.printStatus()
        sim.eventSequenceToCSV(eseq, 1)
    elif mode == 1:
        sim = Simulator()
        nHuman, nStorage, nObject = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        # objects = ['Apple', 'Orange', 'Grape', 'Pear', 'Banana', 'Avocado',
        #            'Pineapple', 'Watermelon', 'Blueberry', 'Coconut']
        objects = Counter({0: int(int(sys.argv[4])/10), 1: int(int(sys.argv[4])/10), 2: int(int(sys.argv[4])/10), 3: int(int(sys.argv[4])/10), 4: int(int(sys.argv[4])/10), 5: int(int(sys.argv[4])/10), 6: int(int(sys.argv[4])/10), 7: int(int(sys.argv[4])/10), 8: int(int(sys.argv[4])/10), 9: int(int(sys.argv[4])/10)})
        eventList = [HUMANENTER, HUMANEXIT, HANDSIN, HANDSOUT, NOISE]
        eventPDF = np.array([float(sys.argv[9]), float(sys.argv[10]), float(sys.argv[11])+float(sys.argv[15]), float(sys.argv[11])+float(sys.argv[15]), float(sys.argv[6])])
        eventPDF /= np.sum(eventPDF)
	maxStorageperHuman = int(nStorage/nHuman)
	maxObjectsperHuman = min(int(nObject/nHuman), 10)
        maxHumans = int(sys.argv[5])/(maxStorageperHuman+1)-2
        maxIter = 1000000
        countNoiseProb=float(sys.argv[7])
        frames=10
        contentNoiseProb=float(sys.argv[8])
        nStorage = nHuman*maxStorageperHuman
        mininteract = maxObjectsperHuman*2
        """
        generateRandomEventSequence(self, nHuman, nStorage, 
                                    eventList, eventPDF, maxIter, maxHumans,
                                    maxStorageperHuman, maxObjectsperHuman,mininteract)
        """
        eventSequence = sim.generateRandomEventSequence(
            nHuman, eventList, eventPDF, maxIter, maxHumans,
            maxStorageperHuman, maxObjectsperHuman,mininteract)

        print "\nEvent tuples (internal to simulator) are:"
        for t, e in enumerate(eventSequence):
            print t, e
        sim.eventSequenceToCSV(eventSequence, nStorage, countNoiseProb, int(contentNoiseProb*frames), frames)
    else:
        raise "Mode %d is not implemented." % mode


if __name__ == '__main__':
    main(1)
