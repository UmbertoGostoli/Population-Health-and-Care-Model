
from person import Person
from person import Population
from house import House
from house import Town
from house import Map
import random
import math
import pylab
import Tkinter
import struct
import time
import sys
import pprint
import pickle
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import csv
import os
from collections import OrderedDict
import operator
import itertools
from itertools import izip_longest
# from PIL import ImageTk         
# from PIL import Image



class Sim:
    """Instantiates a single run of the simulation."""    
    def __init__ (self, scenario, params, folder):
        
        self.p = OrderedDict(params)
        
        self.Outputs = ['year', 'currentPop', 'households', 'averageHouseholdSize', 'marriageTally', 'marriagePropNow', 'divorceTally', 
                   'shareSingleParents', 'shareFemaleSingleParent', 'totalCareDemandHours', 'totalCareSupply', 'totalUnmetNeed', 'shareUnmetCareNeeds', 
                   'taxPayers', 'taxBurden', 'familyCareRatio', 'employmentRate', 'publicCare', 'totalTaxRevenue', 'totalPensionRevenue', 
                   'pensionExpenditure', 'totalHospitalizationCost']
        self.outputData = pd.DataFrame()
        # Save initial parametrs into Scenario folder
        self.folder = folder + '/Scenario_' + str(scenario)
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        filePath = self.folder + '/scenarioParameters.csv'
        c = params.copy()
        for key, value in c.iteritems():
            if not isinstance(value, list):
                c[key] = [value]
        with open(filePath, "wb") as f:
            csv.writer(f).writerow(c.keys())
            csv.writer(f).writerows(itertools.izip_longest(*c.values()))
        
        
        ####  SES variables   #####
        self.socialClassShares = []
        self.careNeedShares = []
        self.householdIncomes = []
        self.individualIncomes = []
        self.incomeFrequencies = []
        self.sesPops = []
        self.sesPopsShares = []
        ## Statistical tallies
        self.times = []
        self.pops = []
        self.avgHouseholdSize = []
        self.marriageTally = 0
        self.numMarriages = []
        self.divorceTally = 0
        self.numDivorces = []
        self.totalCareDemand = []
        self.totalCareSupply = []
        self.totalHospitalizationCost = 0
        self.hospitalizationCost = []
        self.numTaxpayers = []
        self.totalUnmetNeed = []
        self.shareUnmetNeed = []
        self.totalFamilyCare = []
        self.totalTaxBurden = []
        self.marriageProp = []
        self.shareLoneParents = []
        self.shareFemaleLoneParents = []
        self.employmentRate = []
        self.publicCareProvision = []
        self.publicCare = 0
        self.stateTaxRevenue = []
        self.totalTaxRevenue = 0
        self.statePensionRevenue = []
        self.totalPensionRevenue = 0
        self.statePensionExpenditure = []
        self.pensionExpenditure = 0
        ## Counters and storage
        self.year = self.p['startYear']
        self.pyramid = PopPyramid(self.p['num5YearAgeClasses'],
                                  self.p['numCareLevels'])
        self.textUpdateList = []

        if self.p['interactiveGraphics']:
            self.window = Tkinter.Tk()
            self.canvas = Tkinter.Canvas(self.window,
                                    width=self.p['screenWidth'],
                                    height=self.p['screenHeight'],
                                    background=self.p['bgColour'])


    def run(self, policy, policyParams, seed):
        """Run the simulation from year start to year end."""

        #pprint.pprint(self.p)
        #raw_input("Happy with these parameters?  Press enter to run.")
        self.randSeed = seed
        random.seed(self.randSeed)
        np.random.seed(self.randSeed)

        self.initializePop()
        
        if self.p['interactiveGraphics']:
            self.initializeCanvas()     
            
        # Save policy parameters in Policy folder
        policyFolder = self.folder + '/Policy_' + str(policy)
        if not os.path.exists(policyFolder):
            os.makedirs(policyFolder)
        filePath = policyFolder + '/policyParameters.csv'
        c = policyParams.copy()
        for key, value in c.iteritems():
            if not isinstance(value, list):
                c[key] = [value]
        with open(filePath, "wb") as f:
            csv.writer(f).writerow(c.keys())
            csv.writer(f).writerows(itertools.izip_longest(*c.values()))
        
        if policy == 0:
            startYear = int(self.p['startYear'])
        else:
            startYear = int(self.p['policyStartYear'])
        
        for self.year in range (startYear, int(self.p['endYear']+1)):
            
            print self.year
            
            if policyParams and self.year == self.p['policyStartYear']:
                keys = policyParams.keys()
                for k in keys[1:]:
                    self.p[k] = policyParams[k]
                
                # From list of agents to list of indexes
                if policy == 0:
                    
                    self.from_Agents_to_IDs()
                    
                    # Save outputs
                    self.outputData = pd.read_csv(policyFolder + '/Outputs.csv')
                    self.outputData.to_csv(policyFolder + '/tempOutputs.csv', index=False)
                    # Save simulation
                    pickle.dump(self.pop, open(policyFolder + '/save.p', 'wb'))
                    pickle.dump(self.map, open(policyFolder + '/save.m', 'wb'))
                
                # Upload simulation
                self.pop = pickle.load(open(self.folder + '/Policy_0/save.p', 'rb'))
                self.map = pickle.load(open(self.folder + '/Policy_0/save.m', 'rb'))
                
                self.from_IDs_to_Agents()
                
                # Upload outputs
                if policy != 0:
                    self.outputData = pd.read_csv(self.folder + '/Policy_0/tempOutputs.csv')
                    self.outputData.to_csv(policyFolder + '/Outputs.csv', index=False)
                    
            
            # self.doOneYear(policyFolder)
            
            self.doOneYear_SES(policyFolder)
            
#            if self.year == self.p['thePresent']:
#                random.seed()
                
            print ''
        
        if self.p['singleRunGraphs']:
            self.doGraphs()
    
        if self.p['interactiveGraphics']:
            print "Entering main loop to hold graphics up there."
            self.window.mainloop()

        return self.totalTaxBurden[-1]


    def initializePop(self):
        """
        Set up the initial population and the map.
        We may want to do this from scratch, and we may want to do it
        by loading things from a pre-generated file.
        """
        ## First the map, towns, and houses

        if self.p['loadFromFile'] == False:
            self.map = Map(self.p['mapGridXDimension'],
                           self.p['mapGridYDimension'],
                           self.p['townGridDimension'],
                           self.p['cdfHouseClasses'],
                           self.p['ukMap'],
                           self.p['ukClassBias'],
                           self.p['mapDensityModifier'] )
        else:
            self.map = pickle.load(open("initMap.txt","rb"))


        ## Now the people who will live on it

        if self.p['loadFromFile'] == False:
            self.pop = Population(self.p['initialPop'],
                                  self.p['startYear'],
                                  self.p['minStartAge'],
                                  self.p['maxStartAge'],
                                  self.p['workingAge'],
                                  self.p['incomeInitialLevels'],
                                  self.p['incomeFinalLevels'],
                                  self.p['incomeGrowthRate'],
                                  self.p['workDiscountingTime'],
                                  self.p['wageVar'],
                                  self.p['weeklyHours'][0])
            ## Now put the people into some houses
            ## They've already been partnered up so put the men in first, then women to follow
            men = [x for x in self.pop.allPeople if x.sex == 'male']

            remainingHouses = []
            remainingHouses.extend(self.map.allHouses)
        
            for man in men:
                man.house = random.choice(remainingHouses)
                man.sec = man.house.size  ## This may not always work, assumes house classes = SEC classes!
                self.map.occupiedHouses.append(man.house)            
                remainingHouses.remove(man.house)
                woman = man.partner
                woman.house = man.house
                woman.sec = man.sec
                man.yearMarried.append(int(self.p['startYear']))
                woman.yearMarried.append(int(self.p['startYear']))
                man.house.occupants.append(man)
                man.house.occupants.append(woman)

        else:
            self.pop = pickle.load(open("initPop.txt","rb"))

        ## Choose one house to be the display house
        self.displayHouse = self.pop.allPeople[0].house
        self.nextDisplayHouse = None

        #reading JH's fertility projections from a CSV into a numpy array
        self.fert_data = np.genfromtxt('babyrate.txt.csv', skip_header=0, delimiter=',')

        #reading JH's fertility projections from two CSVs into two numpy arrays
        self.death_female = np.genfromtxt('deathrate.fem.csv', skip_header=0, delimiter=',')
        self.death_male = np.genfromtxt('deathrate.male.csv', skip_header=0, delimiter=',')
        
        self.incomeDistribution = np.genfromtxt('incomeDistribution.csv', skip_header=0, delimiter=',')
        
        self.incomesPercentiles = np.genfromtxt('incomesPercentiles.csv', skip_header=0, delimiter=',')
        
        self.wealthPercentiles = np.genfromtxt('wealthDistribution.csv', skip_header=0, delimiter=',')
        
        # Assign wealth
        self.updateWealth()
        
    def from_Agents_to_IDs(self):
        for person in self.pop.allPeople:
            if person.mother != None:
                person.motherID = person.mother.id
            else:
                person.motherID = -1
            if person.father != None:
                person.fatherID = person.father.id
            else:
                person.fatherID = -1
            person.childrenID = [x.id for x in person.children]
            person.houseID = person.house.id
            person.mother = None
            person.father = None
            person.children = []
            person.house = None
        
        for house in self.map.allHouses:
            house.occupantsID = [x.id for x in house.occupants]
            house.occupants = []
        
    def from_IDs_to_Agents(self):
        for person in self.pop.allPeople:
            if person.motherID != -1:
                person.mother = [x for x in self.pop.allPeople if x.id == person.motherID][0]
            else:
                person.mother = None
            if person.fatherID != -1:
                person.father = [x for x in self.pop.allPeople if x.id == person.fatherID][0]
            else:
                person.father = None
                
            person.children = [x for x in self.pop.allPeople if x.id in person.childrenID]
            
        for person in self.pop.allPeople:
            person.house = [x for x in self.map.allHouses if x.id == person.houseID][0]
            if person in self.pop.livingPeople:
                person.house.occupants.append(person)
    
    def doOneYear(self, policyFolder):
        """Run one year of simulated time."""

        ##print "Sim Year: ", self.year, "OH count:", len(self.map.occupiedHouses), "H count:", len(self.map.allHouses)
        
        # self.checkHouseholds(0)
        
        # print 'Did computeClassShares'
        
        self.doDeaths()
        
        # self.checkHouseholds(1)
        
        # print 'Did doDeaths_SES'
        
        self.doCareTransitions()
        
        # self.checkHouseholds(2)
        
        self.allocateCare()
        
        # print 'Did doCareTransitions'
        
        self.doAgeTransitions()
        
       
        self.checkHouseholds(1)
        # print 'Did doAgeTransitions'
        
        self.doSocialTransition_Red()
        

        self.updateIncome()
        
        
        self.updateWealth()
        
        # print 'Did updateIncome'
        
        self.doBirths()
        
        
        
        # print 'Did doBirths_SES'
        
        self.doDivorces()
        
       
       # self.checkHouseholds(2)
        # print 'Did doDivorces'
        
        
        # self.doMarriages()
        
        self.doMarriages_Bis()
        
        
        # print 'Did doMarriages'
        
        self.doMovingAround()
        
        
       # self.checkHouseholds(3)
        # print 'Did doMovingAround'

        self.pyramid.update(self.year, self.p['num5YearAgeClasses'], self.p['numCareLevels'],
                            self.p['pixelsInPopPyramid'], self.pop.livingPeople)
        
        self.healthServiceCost()
        
        self.doStats(policyFolder)
        
        if (self.p['interactiveGraphics']):
            self.updateCanvas()
            
        # print 'Did doStats'
        
    def doOneYear_SES(self, policyFolder):
        """Run one year of simulated time."""

        ##print "Sim Year: ", self.year, "OH count:", len(self.map.occupiedHouses), "H count:", len(self.map.allHouses)
        
        # self.checkHouseholds(0)
        
        
        self.computeClassShares()
        
        # print 'Did computeClassShares'
        
        ###################   Do Deaths   #############################
        
        # self.doDeaths()
        
        self.doDeaths_SES()
        
        ################################################################
        
        # print 'Did doDeaths_SES'
        
        ###################   Do Care Transitions   ##########################
        
        self.doCareTransitions()
        
        # self.doCareTransitions_UCN()
        
        self.allocateCare()
        
        ####################################################################
        
        # print 'Did doCareTransitions'
        
        self.doAgeTransitions()
        
        self.checkHouseholds(0)
        
        # print 'Did doAgeTransitions'
        
        ###################   Do Social Transitions   ##########################
        
        # self.doSocialTransition_Red()
        
        self.doSocialTransition()
        
        #########################################################################
        
        
        self.updateIncome()
        
        self.updateWealth()
        
        
        
        
        # print 'Did updateIncome'
        
        ###################   Do Births   ######################################
        
        # self.doBirths()
        
        self.doBirths_SES()
        
        ######################################################################
        
        
        #self.doCareAllocation()
        
        # print 'Did doBirths_SES'
        
        # self.doDivorces()
        
        self.doDivorces_SES()
        
        # self.checkHouseholds(3)
        
        # print 'Did doDivorces'
        
        ###################   Do Marriages   ##########################
        
        # self.doMarriages()
        
        # self.doMarriages_SES()
        
        self.doMarriages_Bis()
        #################################################################
        
        # print 'Did doMarriages'
        
        self.doMovingAround()
        
        
        # self.checkHouseholds(4)
        # print 'Did doMovingAround'

        self.pyramid.update(self.year, self.p['num5YearAgeClasses'], self.p['numCareLevels'],
                            self.p['pixelsInPopPyramid'], self.pop.livingPeople)
        
        self.healthServiceCost()
        
        self.doStats(policyFolder)
        
        if (self.p['interactiveGraphics']):
            self.updateCanvas()
            
        
            
        # print 'Did doStats'

    def doDeaths(self):
        """Consider the possibility of death for each person in the sim."""
        number_deaths = 0
        for person in self.pop.livingPeople:
            age = self.year - person.birthdate
            ##use the empirical rates from 1951 onwards
            if self.year > 1950:
                age = self.year - person.birthdate
                if age > 109:
                    age = 109
                if person.sex == 'male':
                    dieProb = self.death_male[age, self.year-1950]
                if person.sex == 'female':
                    dieProb = self.death_female[age, self.year-1950]
                if random.random() < dieProb:
                    person.dead = True
                    person.deadYear = self.year
                    self.pop.livingPeople.remove(person)
                    person.house.occupants.remove(person)
                    if len(person.house.occupants) == 0:
                        self.map.occupiedHouses.remove(person.house)
                        if (self.p['interactiveGraphics']):
                            self.canvas.itemconfig(person.house.icon, state='hidden')
                    if person.partner != None:
                        person.partner.partner = None
                    if person.house == self.displayHouse:
                        messageString = str(self.year) + ": #" + str(person.id) + " died aged " + str(age) + "." 
                        self.textUpdateList.append(messageString)
        ##use made-up rates prior to 1951
            else:
                babyDieProb = 0.0
                if age < 1:
                    babyDieProb = self.p['babyDieProb']
                if person.sex == 'male':
                    ageDieProb = ( ( math.exp( age /
                                               self.p['maleAgeScaling'] ) )
                                   * self.p['maleAgeDieProb'] )
                else:
                    ageDieProb = ( ( math.exp( age /
                                               self.p['femaleAgeScaling'] ) )
                                   * self.p['femaleAgeDieProb'] )
                dieProb = self.p['baseDieProb'] + babyDieProb + ageDieProb
                if random.random() < dieProb:
                    person.dead = True
                    person.deadYear = self.year
                    self.pop.livingPeople.remove(person)
                    person.house.occupants.remove(person)
                    if len(person.house.occupants) == 0:
                        self.map.occupiedHouses.remove(person.house)
                        if (self.p['interactiveGraphics']):
                            self.canvas.itemconfig(person.house.icon, state='hidden')
                    if person.partner != None:
                        person.partner.partner = None
                    if person.house == self.displayHouse:
                        messageString = str(self.year) + ": #" + str(person.id) + " died aged " + str(age) + "." 
                        self.textUpdateList.append(messageString)
                
        ## Can't remove from list while iterating so we need this
        self.pop.livingPeople[:] = [x for x in self.pop.livingPeople if x.dead == False]    



    def checkHouseholds(self, n):
        
        for member in self.pop.livingPeople:
            if member.partner != None and member.house != member.partner.house:
                print 'Step: ' + str(n)
                print 'Couple not living together'
                print member.id
                print member.dead
                print member.independentStatus
                print member.yearMarried
                print member.partner.id
                print member.partner.partner.id
                print member.partner.dead
                print member.partner.independentStatus
                print member.partner.yearMarried
                sys.exit()
    
        for house in self.map.occupiedHouses:
            
            household = house.occupants
            
            if len(household) != len(set(household)):
                print 'Step: ' + str(n)
                print 'Error: person counted twice'
                sys.exit()
                
            if len(household) == 0:
                print 'Step: ' + str(n)
                print 'Error: occupied house is empty!'
                sys.exit()
                
            married = [x for x in household if x.partner != None]
            
            if len(married) > 2:
                print 'Step: ' + str(n)
                print 'Error: more than a couple in a house'
                for member in married:
                    print member.id
                    print member.age
                    print member.status
                    print member.independentStatus
                    print member.classRank
                    print member.sex
                    print member.income
                    print member.careNeedLevel
                    print 'Person partner id: ' + str(member.partner.id)
                sys.exit()
                
            if len(married) == 1:
                print 'Step: ' + str(n)
                print 'Error: married person not living with partner'
                sys.exit()
           
            independentPeople = [x for x in household if x.independentStatus == True]
            
            if len(independentPeople) == 0:
                print 'Error: no independent people in the house'
                print 'Step: ' + str(n)
                for member in household:
                    print member.id
                    print member.age
                    print member.status
                    print member.classRank
                    print member.sex
                    print member.income
                    print member.careNeedLevel
                    print 'Father: ' + str(member.father.id)
                    print member.father.dead
                    print member.father.deadYear
                    print member.father.yearMarried
                    print member.father.yearDivorced
                    print 'Mother: ' + str(member.mother.id)
                    print member.mother.dead
                    print member.mother.deadYear
                    print member.mother.yearMarried
                    print member.mother.yearDivorced
                    
                    if member.partner != None:
                        print 'Person partner id: ' + str(member.partner.id)
                    if member.mother.partner != None:
                        print 'Person mother partner id: ' + str(member.mother.partner.id)
                        print 'Person mother partner children: ' + str([x.id for x in member.mother.partner.children])
                        if member.mother.partner.partner != None:
                            print 'Person father partner id: ' + str(member.mother.partner.partner.id)
                    if member.father.partner != None:
                        print 'Person father partner id: ' + str(member.father.partner.id)
                        print 'Person father partner children: ' + str([x.id for x in member.father.partner.children])
                        if member.father.partner.partner != None:
                            print 'Person father partner partner id: ' + str(member.father.partner.partner.id)
                sys.exit()
                
            
            


####################   doDeath - SES version    ################################################
    def computeClassShares(self):
    
        self.socialClassShares[:] = []
        self.careNeedShares[:] = []
        numPop = float(len(self.pop.livingPeople))
        for c in range(int(self.p['numberClasses'])):
            classPop = [x for x in self.pop.livingPeople if x.classRank == c]
            numclassPop = float(len(classPop))
            self.socialClassShares.append(numclassPop/numPop)
            
            needShares = []
            for b in range(int(self.p['numCareLevels'])):
                needPop = [x for x in classPop if x.careNeedLevel == b]
                numNeedPop = float(len(needPop))
                needShares.append(numNeedPop/numclassPop)
            self.careNeedShares.append(needShares)    
        
    
    def deathProb(self, baseRate, sex, classRank, needLevel):  ##, shareUnmetNeed, classPop):
        
        if sex == 'male':
            mortalityBias = self.p['maleMortalityBias']
        else:
            mortalityBias = self.p['femaleMortalityBias']
        
        a = 0
        for i in range(int(self.p['numberClasses'])):
            a += self.socialClassShares[i]*math.pow(mortalityBias, i)
        lowClassRate = baseRate/a
        
        classRate = lowClassRate*math.pow(mortalityBias, classRank)
       
        a = 0
        for i in range(int(self.p['numCareLevels'])):
            a += self.careNeedShares[classRank][i]*math.pow(self.p['careNeedBias'], (self.p['numCareLevels']-1) - i)
        higherNeedRate = classRate/a
       
        deathProb = higherNeedRate*math.pow(self.p['careNeedBias'], (self.p['numCareLevels']-1) - needLevel) # deathProb
      
        # Add the effect of unmet care need on mortality rate for each care need level
        
        ##### Temporarily by-passing the effect of Unmet Care Need   #############
        
#        a = 0
#        for x in classPop:
#            a += math.pow(self.p['unmetCareNeedBias'], 1-x.averageShareUnmetNeed)
#        higherUnmetNeed = (classRate*len(classPop))/a
#        deathProb = higherUnmetNeed*math.pow(self.p['unmetCareNeedBias'], 1-shareUnmetNeed)
        
        return deathProb
    
    def deathProb_UCN(self, baseRate, sex, classRank, needLevel, shareUnmetNeed, classPop):
        
        if sex == 'male':
            mortalityBias = self.p['maleMortalityBias']
        else:
            mortalityBias = self.p['femaleMortalityBias']
        
        a = 0
        for i in range(self.p['numberClasses']):
            a += self.socialClassShares[i]*math.pow(mortalityBias, i)
        lowClassRate = baseRate/a
        
        classRate = lowClassRate*math.pow(mortalityBias, classRank)
       
        a = 0
        for i in range(self.p['numCareLevels']):
            a += self.careNeedShares[classRank][i]*math.pow(self.p['careNeedBias'], (self.p['numCareLevels']-1) - i)
        higherNeedRate = classRate/a
       
        classRate = higherNeedRate*math.pow(self.p['careNeedBias'], (self.p['numCareLevels']-1) - needLevel) # deathProb
      
        # Add the effect of unmet care need on mortality rate for each care need level
        
        ##### Temporarily by-passing the effect of Unmet Care Need   #############
        
        a = 0
        for x in classPop:
            a += math.pow(self.p['unmetCareNeedBias'], 1-x.averageShareUnmetNeed)
        higherUnmetNeed = (classRate*len(classPop))/a
        deathProb = higherUnmetNeed*math.pow(self.p['unmetCareNeedBias'], 1-shareUnmetNeed)
        
        return deathProb
    
    def doDeaths_SES(self):
        
        preDeath = len(self.pop.livingPeople)
        
        deaths = [0, 0, 0, 0, 0]
        """Consider the possibility of death for each person in the sim."""
        for person in self.pop.livingPeople:
            age = person.age
            
            ####     Death process with histroical data  after 1950   ##################
            if self.year > 1950:
                if age > 109:
                    age = 109
                if person.sex == 'male':
                    rawRate = self.death_male[age, self.year-1950]
                if person.sex == 'female':
                    rawRate = self.death_female[age, self.year-1950]
                    
                classPop = [x for x in self.pop.livingPeople if x.careNeedLevel == person.careNeedLevel]
                
                dieProb = self.deathProb(rawRate, person.sex, person.parentsClassRank, person.careNeedLevel)

                # dieProb = self.deathProb_UCN(rawRate, person.sex, person.parentsClassRank, person.careNeedLevel, person.averageShareUnmetNeed, classPop)

            #############################################################################
            
                if random.random() < dieProb:
                    person.dead = True
                    person.deadYear = self.year
                    person.house.occupants.remove(person)
                    if len(person.house.occupants) == 0:
                        self.map.occupiedHouses.remove(person.house)
                        if (self.p['interactiveGraphics']):
                            self.canvas.itemconfig(person.house.icon, state='hidden')
                    if person.partner != None:
                        person.partner.partner = None
                    if person.house == self.displayHouse:
                        messageString = str(self.year) + ": #" + str(person.id) + " died aged " + str(age) + "." 
                        self.textUpdateList.append(messageString)
                
            else: 
                #######   Death process with made-up rates  ######################
                babyDieProb = 0.0
                if age < 1:
                    babyDieProb = self.p['babyDieProb']
                if person.sex == 'male':
                    ageDieProb = (math.exp(age/self.p['maleAgeScaling']))*self.p['maleAgeDieProb'] 
                else:
                    ageDieProb = (math.exp(age/self.p['femaleAgeScaling']))* self.p['femaleAgeDieProb']
                rawRate = self.p['baseDieProb'] + babyDieProb + ageDieProb
                
                classPop = [x for x in self.pop.livingPeople if x.careNeedLevel == person.careNeedLevel]
                
                dieProb = self.deathProb(rawRate, person.sex, person.parentsClassRank, person.careNeedLevel)
                #### Temporarily by-passing the effect of unmet care need   ######
                # dieProb = self.deathProb_UCN(rawRate, person.sex, person.parentsClassRank, person.careNeedLevel, person.averageShareUnmetNeed, classPop)
                
                if random.random() < dieProb:
                    person.dead = True
                    person.deadYear = self.year
                    deaths[person.classRank] += 1
                    person.house.occupants.remove(person)
                    if len(person.house.occupants) == 0:
                        self.map.occupiedHouses.remove(person.house)
                        if (self.p['interactiveGraphics']):
                            self.canvas.itemconfig(person.house.icon, state='hidden')
                    if person.partner != None:
                        person.partner.partner = None
                    if person.house == self.displayHouse:
                        messageString = str(self.year) + ": #" + str(person.id) + " died aged " + str(age) + "." 
                        self.textUpdateList.append(messageString)
                        
                  
        self.pop.livingPeople[:] = [x for x in self.pop.livingPeople if x.dead == False]
        
        postDeath = len(self.pop.livingPeople)
        
        print('the number of deaths is: ' + str(preDeath - postDeath))            

    def doCareTransitions(self):
        """Consider the possibility of each person coming to require care."""
        peopleNotInCriticalCare = [x for x in self.pop.livingPeople if x.careNeedLevel < self.p['numCareLevels']-1]
        for person in peopleNotInCriticalCare:
            age = self.year - person.birthdate
            if person.sex == 'male':
                ageCareProb = ( ( math.exp( age /
                                            self.p['maleAgeCareScaling'] ) )
                               * self.p['personCareProb'] )
            else:
                ageCareProb = ( ( math.exp( age /
                                           self.p['femaleAgeCareScaling'] ) )
                               * self.p['personCareProb'] )
            careProb = self.p['baseCareProb'] + ageCareProb
            
            if random.random() < careProb:
                multiStepTransition = random.random()
                if multiStepTransition < self.p['cdfCareTransition'][0]:
                    person.careNeedLevel += 1
                elif multiStepTransition < self.p['cdfCareTransition'][1]:
                    person.careNeedLevel += 2
                elif multiStepTransition < self.p['cdfCareTransition'][2]:
                    person.careNeedLevel += 3
                else:
                    person.careNeedLevel += 4
                    
                if person.careNeedLevel >= self.p['numCareLevels']:
                    person.careNeedLevel = self.p['numCareLevels'] - 1
                            
                if person.house == self.displayHouse:
                    messageString = str(self.year) + ": #" + str(person.id) + " now has "
                    messageString += self.p['careLevelNames'][int(person.careNeedLevel)] + " care needs." 
                    self.textUpdateList.append(messageString)
    

           
    def doCareTransitions_UCN(self):
        """Consider the possibility of each person coming to require care."""
        peopleNotInCriticalCare = [x for x in self.pop.livingPeople if x.careNeedLevel < self.p['numCareLevels']-1]
        for person in peopleNotInCriticalCare:
            age = self.year - person.birthdate
            if person.sex == 'male':
                ageCareProb = ( ( math.exp( age /
                                            self.p['maleAgeCareScaling'] ) )
                               * self.p['personCareProb'] )
            else:
                ageCareProb = ( ( math.exp( age /
                                           self.p['femaleAgeCareScaling'] ) )
                               * self.p['personCareProb'] )
            baseProb = self.p['baseCareProb'] + ageCareProb
            
            unmetNeedFactor = 1/math.exp(self.p['unmetNeedExponent']*person.averageShareUnmetNeed)
            
            careProb = baseProb*math.pow(self.p['careBias'], person.classRank)/unmetNeedFactor 
            
            
            #### Alternative prob which depends on care level and unmet care need   #####################################
            careProb = baseProb # baseProb*math.pow(self.p['careBias'], person.classRank)/unmetNeedFactor
            
            
            if random.random() < careProb:
                baseTransition = self.baseRate(self.p['careBias'], 1-self.p['careTransitionRate'])
                if person.careNeedLevel > 0:
                    unmetNeedFactor = 1/math.exp(self.p['unmetNeedExponent']*person.averageShareUnmetNeed)
                else:
                    unmetNeedFactor = 1.0
                transitionRate = (1.0 - baseTransition*math.pow(self.p['careBias'], person.classRank))*unmetNeedFactor

                stepCare = 1
                bound = transitionRate
                while random.random() > bound and stepCare < self.p['numCareLevels'] - 1:
                    stepCare += 1
                    bound += (1-bound)*transitionRate
                person.careNeedLevel += stepCare
                    
                if person.careNeedLevel >= self.p['numCareLevels']:
                    person.careNeedLevel = int(self.p['numCareLevels'] - 1)
                            
                if person.house == self.displayHouse:
                    messageString = str(self.year) + ": #" + str(person.id) + " now has "
                    messageString += self.p['careLevelNames'][person.careNeedLevel] + " care needs." 
                    self.textUpdateList.append(messageString)
    
    def baseRate(self, bias, cp):
        a = 0
        for i in range(self.p['numberClasses']):
            a += self.socialClassShares[i]*math.pow(bias, i)
        baseRate = cp/a
        return (baseRate)
    
    def allocateCare(self):
        
        self.reserCareVariables()
        
        self.updateCareNeeds()
        
        self.updateCareSupply()
        
        self.transferCare()
        
        self.updateUnmetCareNeed()
        
    def reserCareVariables(self):
        
        for person in self.pop.livingPeople:
            person.socialWork = 0
    
    def updateCareNeeds(self):
        
        self.publicCare = 0
        for person in self.pop.livingPeople:
            need = self.p['careDemandInHours'][int(person.careNeedLevel)]
            person.careDemand = need
            person.unmetCareNeed = person.careDemand
            
            if person.careNeedLevel >= self.p['publicCareNeedLevel'] and person.age >= self.p['publicCareAgeLimit']:
                self.publicCare += person.unmetCareNeed
                person.unmetCareNeed = 0
                
        self.publicCareProvision.append(self.publicCare)
            
    def updateCareSupply(self):
        for person in self.pop.livingPeople:
            if person.status == 'child':
                supply = self.p['childHours']
            elif person.status == 'student':
                supply = self.p['homeAdultHours']
            elif person.status == 'worker':
                supply = self.p['workingAdultHours']
            elif person.status == 'retired':
                supply = self.p['retiredHours']
            else:
                print person.status
                print "Shouldn't happen."
                sys.exit()

            if person.careNeedLevel > 1:
                supply = 0.0
            elif person.careNeedLevel == 1:
                supply *= self.p['lowCareHandicap']

            person.careAvailable = supply
            person.residualSupply = person.careAvailable
            
    def transferCare(self):
        for person in self.pop.livingPeople:
            ## Can you get the care you need from your housemates?
            if person.unmetCareNeed > 0.0:
                for donor in person.house.occupants:
                    if person != donor and donor.residualSupply > 0.0:
                        if donor.residualSupply > person.unmetCareNeed:
                            swap = person.unmetCareNeed
                            person.unmetCareNeed = 0.0
                            donor.residualSupply -= swap
                            donor.socialWork += swap
                            break
                        else:
                            swap = donor.residualSupply
                            donor.socialWork += swap
                            donor.residualSupply = 0.0
                            person.unmetCareNeed -= swap
                            
            ## Can you get the care you need from your children if they live in the same town?
            if person.unmetCareNeed > 0.0:
                for donor in person.children:
                    if person.house.town == donor.house.town and donor.residualSupply > 0.0 and donor.dead == False:
                        if donor.residualSupply > person.unmetCareNeed:
                            swap = person.unmetCareNeed
                            person.unmetCareNeed = 0.0
                            donor.residualSupply -= swap
                            donor.socialWork += swap
                            break
                        else:
                            swap = donor.residualSupply
                            donor.residualSupply = 0.0
                            person.unmetCareNeed -= swap
                            donor.socialWork += swap

        ## Now tally up the care situation, how much need is unmet, because that's the state's burden
        
    def updateUnmetCareNeed(self):
        
        for person in self.pop.livingPeople:
            if person.careNeedLevel > 0:
                person.cumulativeUnmetNeed *= self.p['unmetCareNeedDiscountParam']
                person.cumulativeUnmetNeed += person.unmetCareNeed
                person.totalDiscountedShareUnmetNeed *= self.p['shareUnmetNeedDiscountParam']
                person.totalDiscountedTime *= self.p['shareUnmetNeedDiscountParam']
                person.totalDiscountedShareUnmetNeed += person.unmetCareNeed/person.careDemand
                person.totalDiscountedTime += 1
                person.averageShareUnmetNeed = person.totalDiscountedShareUnmetNeed/person.totalDiscountedTime
    
    def doAgeTransitions(self):
        
        for person in self.pop.livingPeople:
            person.age += 1
            person.yearInTown += 1
        """Check whether people have moved on to a new status in life."""
        peopleNotYetRetired = [x for x in self.pop.livingPeople if x.status != 'retired']
        for person in peopleNotYetRetired:
            age = self.year - person.birthdate
            ## Do transitions to adulthood and retirement
            if age == self.p['ageOfAdulthood']:
                person.status = 'student'
                person.classRank = 0 # max(person.father.classRank, person.mother.classRank)
                if person.house == self.displayHouse:
                    self.textUpdateList.append(str(self.year) + ": #" + str(person.id) + " is now an adult.")
            elif age == self.p['ageOfRetirement']:
                person.status = 'retired'
                if person.house == self.displayHouse:
                    self.textUpdateList.append(str(self.year) + ": #" + str(person.id) + " has now retired.")

            ## If somebody is still at home but their parents have died, promote them to independent adult
            if person.mother != None:
                if person.status == 'worker' and person.mother not in person.house.occupants and person.father not in person.house.occupants:
                    person.independentStatus = True
            if person.status == 'student' and len([x for x in person.house.occupants if x.independentStatus == True]) == 0:
                if person.mother.dead:
                    if person.father.dead:
                        person.independentStatus = True
                        self.startWorking(person)
                        if person.house == self.displayHouse:
                            self.textUpdateList.append(str(self.year) + ": #" + str(person.id) + "'s parents are both dead.")
                    else:
                        self.movePeopleIntoChosenHouse(person.father.house, person.house,[person], 0)
                else:
                    self.movePeopleIntoChosenHouse(person.mother.house, person.house,[person], 0)
                    
            ## If somebody is a *child* at home and their parents have died, they need to be adopted
            if person.status == 'retired' and len([x for x in person.house.occupants if x.independentStatus == True]) == 0:
                person.independentStatus = True
            
            if person.status == 'child' and len([x for x in person.house.occupants if x.independentStatus == True]) == 0:
                if person.mother.dead:
                    if person.father.dead:
                        if person.house == self.displayHouse:
                            self.textUpdateList.append(str(self.year) + ": #" + str(person.id) + "will now be adopted.")
        
                        while True:
                            adoptiveMother = random.choice(self.pop.livingPeople)
                            if ( adoptiveMother.status != 'child'
                                 and adoptiveMother.sex == 'female'
                                 and adoptiveMother.partner != None ):
                                break
        
                        person.mother = adoptiveMother
                        adoptiveMother.children.append(person)
                        person.father = adoptiveMother.partner
                        adoptiveMother.partner.children.append(person)                
        
                        if adoptiveMother.house == self.displayHouse:
                            self.textUpdateList.append(str(self.year) + ": #" + str(person.id) +
                                                       " has been newly adopted by " + str(adoptiveMother.id)
                                                       + "." )
                        self.movePeopleIntoChosenHouse(adoptiveMother.house,person.house,[person], 0)   
                    else:
                        self.movePeopleIntoChosenHouse(person.father.house, person.house,[person], 0)
                else:
                    self.movePeopleIntoChosenHouse(person.mother.house, person.house,[person], 0)
                    
    def startWorking(self, person):
        
        person.status = 'worker'
        
        dKi = np.random.normal(0, self.p['wageVar'])
        person.initialIncome = self.p['incomeInitialLevels'][person.classRank]*math.exp(dKi)
        dKf = np.random.normal(dKi, self.p['wageVar'])
        person.finalIncome = self.p['incomeFinalLevels'][person.classRank]*math.exp(dKf)
        
        person.wage = person.initialIncome
        person.income = person.wage*self.p['weeklyHours'][int(person.careNeedLevel)]
    
    def doSocialTransition_Red(self):
        
        for person in self.pop.livingPeople:
            if person.age == self.p['ageOfAdulthood']:
                person.status = 'student'
                householdRanks = [person.father.classRank, person.mother.classRank]
                person.classRank = random.choice(householdRanks)
            if person.age == self.p['workingAge'][person.classRank] and person.status == 'student':
                self.startWorking(person)
                
    
    def doSocialTransition(self):
        
        for person in self.pop.livingPeople:
            if person.age == self.p['workingAge'][person.classRank] and person.status == 'student':
            # With a certain probability p the person enters the workforce, 
            # with a probability 1-p goes to the next educational level
                if person.classRank == 4:
                    probStudy = 0.0
                else:
                    probStudy = self.transitionProb(person) # Probability of keeping studying
                
                if random.random() > probStudy:
                    self.startWorking(person)
                    if person.house == self.displayHouse:
                        self.textUpdateList.append(str(self.year) + ": #" + str(person.id) + " is now looking for a job.")
                else:
                    person.classRank += 1
                    if person.house == self.displayHouse:
                        self.textUpdateList.append(str(self.year) + ": #" + str(person.id) + " is now a student.")
            
    def transitionProb (self, person):
        household = [x for x in person.house.occupants]
        if person.father.dead + person.mother.dead != 2:
            disposableIncome = sum([x.income for x in household])
            perCapitaDisposableIncome = disposableIncome/len(household)
            # print('Per Capita Disposable Income: ' + str(perCapitaDisposableIncome))
            
            if perCapitaDisposableIncome > 0.0:
                
                forgoneSalary = self.p['incomeInitialLevels'][person.classRank]*self.p['weeklyHours'][person.careNeedLevel]
                educationCosts = self.p['educationCosts'][person.classRank]
                relCost = (forgoneSalary+educationCosts)/perCapitaDisposableIncome
                
                # Check variable
#                if self.year == self.p['getCheckVariablesAtYear']:
#                    self.relativeEducationCost.append(relCost) # 0.2 - 5
                
                incomeEffect = (self.p['costantIncomeParam']+1)/(math.exp(self.p['eduWageSensitivity']*relCost) + self.p['costantIncomeParam']) # Min-Max: 0 - 10
                
                targetEL = max(person.father.classRank, person.mother.classRank)
                
                # targetEL = np.random.choice([person.father.classRank, person.mother.classRank])
                
                dE = float(targetEL - person.classRank)
                expEdu = math.exp(self.p['eduRankSensitivity']*dE)
                educationEffect = expEdu/(expEdu+self.p['costantEduParam'])
                
                careEffect = 1/math.exp(self.p['careEducationParam']*person.socialWork)
                
                
                ### Fixing probability to keep studying   ######################
                
                pStudy = incomeEffect*educationEffect # incomeEffect*educationEffect*careEffect
                
                #####################################################################
                
                # pStudy = math.pow(incomeEffect, self.p['incEduExp'])*math.pow(educationEffect, 1-self.p['incEduExp'])
                if pStudy < 0:
                    pStudy = 0
                # Check
#                if self.year == self.p['getCheckVariablesAtYear']:
#                    self.probKeepStudying.append(pStudy)
#                    self.person.classRankStudent.append(person.classRank)
                
            else:
                # print('perCapitaDisposableIncome: ' + str(perCapitaDisposableIncome))
                pStudy = 0
        else:
            pStudy = 0
        # pWork = math.exp(-1*self.p['eduEduSensitivity']*dE1)
        # return (pStudy/(pStudy+pWork))
        #pStudy = 0.8
        return pStudy
    
    
    def updateIncome(self):
        
        for person in self.pop.livingPeople:
            if person.income > 0 and person.age < self.p['ageOfRetirement']:
                person.workExperience *= self.p['workDiscountingTime']
                person.workExperience += 1
                person.wage = self.computeWage(person)
                person.income = person.wage*self.p['weeklyHours'][int(person.careNeedLevel)]
            elif person.age == self.p['ageOfRetirement']:
                person.wage = 0
                dK = np.random.normal(0, self.p['wageVar'])
                person.income = person.income*0.7*math.exp(dK) #self.p['pensionWage'][person.classRank]*self.p['weeklyHours'][0]
#                if person.income < self.p['statePension']:
#                    person.income = self.p['statePension']
     
        # Compute tax revenue and income after tax
        earningPeople = [x for x in self.pop.livingPeople if x.income > 0]
        self.totalTaxRevenue = 0
        self.totalPensionRevenue = 0
        for person in earningPeople:
            # Pension Contributions
            employeePensionContribution = person.income*self.p['employeePensionContribution']
            person.income -= employeePensionContribution
            self.totalPensionRevenue += employeePensionContribution
            self.totalPensionRevenue += person.income*self.p['employerPensionContribution']
            
            # Tax Revenues
            tax = 0
            residualIncome = person.income
            for i in range(len(self.p['taxBrakets'])):
                if residualIncome > self.p['taxBrakets'][i]:
                    taxable = residualIncome - self.p['taxBrakets'][i]
                    tax += taxable*self.p['taxationRates'][i]
                    residualIncome -= taxable
            person.income -= tax
            self.totalTaxRevenue += tax
        self.statePensionRevenue.append(self.totalPensionRevenue)
        self.stateTaxRevenue.append(self.totalTaxRevenue)
        
        # Pensions Expenditure
        pensioners = [x for x in self.pop.livingPeople if x.status == 'retired']
        totalIncome = sum([x.income for x in earningPeople if x.status == 'worker'])
        self.pensionExpenditure = self.p['statePension']*len(pensioners) + totalIncome*self.p['statePensionContribution']
        self.statePensionExpenditure.append(self.pensionExpenditure)
        
        households = [x for x in self.map.occupiedHouses]
        for house in households:
            house.householdIncome = sum([x.income for x in house.occupants])
            house.perCapitaIncome = house.householdIncome/float(len(house.occupants))
        
        # Assign incomes according to empirical income distribution
        #####   Temporarily disactivating the top-down income attribution   ############################
        
#        earningPeople = [x for x in self.pop.livingPeople if x.income > 0] #x.status == 'worker']
#        earningPeople.sort(key=operator.attrgetter("income"))
#        
#        workersToAssign = list(earningPeople)
#        incomePercentiles = []
#        for i in range(99, 0, -1):
#            groupNum = int(float(len(workersToAssign))/float(i))
#            workersGroup = workersToAssign[0:groupNum]
#            incomePercentiles.append(workersGroup)
#            workersToAssign = workersToAssign[groupNum:]
#        
#        for i in range(99):
#            wage = float(self.incomesPercentiles[i])/(52*40)
#            for person in incomePercentiles[i]:
#                dK = np.random.normal(0, self.p['wageVar'])
#                person.wage = wage*math.exp(dK)
#                person.income = person.wage*self.p['weeklyHours'][int(person.careNeedLevel)]
            
    def updateWealth(self):
        households = [x for x in self.map.occupiedHouses]
        for h in households:
            h.householdIncome = sum([x.income for x in h.occupants])
        households.sort(key=operator.attrgetter("householdIncome"))
        
        householdsToAssign = list(households)
        wealthPercentiles = []
        for i in range(100, 0, -1):
            groupNum = int(float(len(householdsToAssign))/float(i))
            householdGroup = householdsToAssign[0:groupNum]
            wealthPercentiles.append(householdGroup)
            householdsToAssign = householdsToAssign[groupNum:]
            
        for i in range(100):
            wealth = float(self.wealthPercentiles[i])
            for household in wealthPercentiles[i]:
                dK = np.random.normal(0, self.p['wageVar'])
                household.wealth = wealth*math.exp(dK)
        
        # Assign household wealth to single members
        for h in households:
            if h.householdIncome > 0:
                earningMembers = [x for x in h.occupants if x.income > 0]
                for m in earningMembers:
                    m.wealth = (m.income/h.householdIncome)*h.wealth
            else:
                independentMembers = [x for x in h.occupants if x.independentStatus == True]
                if len(independentMembers) > 0:
                    for m in independentMembers:
                        m.wealth = h.wealth/float(len(independentMembers))
            
        
        
    def computeWage(self, person):
        
        # newK = self.p['incomeFinalLevels'][classRank]*math.exp(dK)    
        # c = np.math.log(self.p['incomeInitialLevels'][classRank]/newK)
        # wage = newK*np.math.exp(c*np.math.exp(-1*self.p['incomeGrowthRate'][classRank]*workExperience))
        c = np.math.log(person.initialIncome/person.finalIncome)
        wage = person.finalIncome*np.math.exp(c*np.math.exp(-1*self.p['incomeGrowthRate'][person.classRank]*person.workExperience))
        dK = np.random.normal(0, self.p['wageVar'])
        wage *= math.exp(dK)
        return wage
    
    
    def doBirths(self):
        """For each fertile woman check whether she gives birth."""

        marriedLadies = 0
        adultLadies = 0

        womenOfReproductiveAge = [x for x in self.pop.livingPeople
                                  if x.sex == 'female'
                                  and (self.year - x.birthdate) > self.p['minPregnancyAge']
                                  and (self.year - x.birthdate) < self.p['maxPregnancyAge']
                                  and x.partner != None ]
        #counting up marriage stats
        for person in self.pop.livingPeople:
            age = self.year - person.birthdate
            if person.sex == 'female' and age >=17:
                adultLadies += 1
                if person.partner != None:
                    marriedLadies += 1

        #printing out stats for troubleshooting and sanity check
        marriedPercentage = float(marriedLadies)/float(adultLadies)
##        print "Simulation year: ", self.year
##        print "Total pop: ", len(self.pop.livingPeople)
##        print "Married ladies: ", marriedLadies
##        print "Adult ladies: ", adultLadies
##        print "Married Percentage: ", marriedPercentage
        
        for woman in womenOfReproductiveAge:
                previousChildren = woman.children
                if self.year < 1951:
                    birthProb = self.p['growingPopBirthProb']
                else:
                    birthProb = (self.fert_data[(self.year - woman.birthdate)-16,self.year-1950])/marriedPercentage
                    ##print "Birth probability is: ", birthProb
                if random.random() < birthProb:
                    baby = Person(woman, woman.partner, self.year, 0, 'random', woman.house, woman.sec, -1, 0, 0, 0, 0, 0, 0, 'child', False)
                    self.pop.allPeople.append(baby)
                    self.pop.livingPeople.append(baby)
                    woman.house.occupants.append(baby)
                    woman.children.append(baby)
                    woman.partner.children.append(baby)
                    if woman.house == self.displayHouse:
                        messageString = str(self.year) + ": #" + str(woman.id) + " had a baby, #" + str(baby.id) + "." 
                        self.textUpdateList.append(messageString) 
    
    
    def computeBirthProb(self, fertilityBias, rawRate, womanRank):
        womenOfReproductiveAge = [x for x in self.pop.livingPeople
                                  if x.sex == 'female' and x.age >= self.p['minPregnancyAge']]
        womanClassShares = []
        womanClassShares.append(len([x for x in womenOfReproductiveAge if x.classRank == 0])/float(len(womenOfReproductiveAge)))
        womanClassShares.append(len([x for x in womenOfReproductiveAge if x.classRank == 1])/float(len(womenOfReproductiveAge)))
        womanClassShares.append(len([x for x in womenOfReproductiveAge if x.classRank == 2])/float(len(womenOfReproductiveAge)))
        womanClassShares.append(len([x for x in womenOfReproductiveAge if x.classRank == 3])/float(len(womenOfReproductiveAge)))
        womanClassShares.append(len([x for x in womenOfReproductiveAge if x.classRank == 4])/float(len(womenOfReproductiveAge)))
        a = 0
        for i in range(int(self.p['numberClasses'])):
            a += womanClassShares[i]*math.pow(self.p['fertilityBias'], i)
        baseRate = rawRate/a
        birthProb = baseRate*math.pow(self.p['fertilityBias'], womanRank)
        return birthProb
    
    def doBirths_SES(self):
        
        preBirth = len(self.pop.livingPeople)
        
        marriedLadies = 0
        adultLadies = 0
        births = [0, 0, 0, 0, 0]
        marriedPercentage = []
        
        adultWomen = [x for x in self.pop.livingPeople
                                       if x.sex == 'female' and x.age >= self.p['minPregnancyAge']]
        
        womenOfReproductiveAge = [x for x in self.pop.livingPeople
                                  if x.sex == 'female'
                                  and x.age >= self.p['minPregnancyAge']
                                  and x.age <= self.p['maxPregnancyAge']
                                  and x.partner != None]
        
        adultLadies_1 = [x for x in adultWomen if x.classRank == 0]   
        marriedLadies_1 = len([x for x in adultLadies_1 if x.partner != None])
        if len(adultLadies_1) > 0:
            marriedPercentage.append(marriedLadies_1/float(len(adultLadies_1)))
        else:
            marriedPercentage.append(0)
        adultLadies_2 = [x for x in adultWomen if x.classRank == 1]    
        marriedLadies_2 = len([x for x in adultLadies_2 if x.partner != None])
        if len(adultLadies_2) > 0:
            marriedPercentage.append(marriedLadies_2/float(len(adultLadies_2)))
        else:
            marriedPercentage.append(0)
        adultLadies_3 = [x for x in adultWomen if x.classRank == 2]   
        marriedLadies_3 = len([x for x in adultLadies_3 if x.partner != None]) 
        if len(adultLadies_3) > 0:
            marriedPercentage.append(marriedLadies_3/float(len(adultLadies_3)))
        else:
            marriedPercentage.append(0)
        adultLadies_4 = [x for x in adultWomen if x.classRank == 3]  
        marriedLadies_4 = len([x for x in adultLadies_4 if x.partner != None])   
        if len(adultLadies_4) > 0:
            marriedPercentage.append(marriedLadies_4/float(len(adultLadies_4)))
        else:
            marriedPercentage.append(0)
        adultLadies_5 = [x for x in adultWomen if x.classRank == 4]   
        marriedLadies_5 = len([x for x in adultLadies_5 if x.partner != None]) 
        if len(adultLadies_5) > 0:
            marriedPercentage.append(marriedLadies_5/float(len(adultLadies_5)))
        else:
            marriedPercentage.append(0)
        
        # print(marriedPercentage)
        
#        for person in self.pop.livingPeople:
#           
#            if person.sex == 'female' and person.age >= self.p['minPregnancyAge']:
#                adultLadies += 1
#                if person.partner != None:
#                    marriedLadies += 1
#        marriedPercentage = float(marriedLadies)/float(adultLadies)
        
        for woman in womenOfReproductiveAge:
            
            householdRank = max([woman.classRank, woman.partner.classRank])
            
            if self.year < 1951:
                rawRate = self.p['growingPopBirthProb']
                birthProb = self.computeBirthProb(self.p['fertilityBias'], rawRate, householdRank)
            else:
                rawRate = self.fert_data[(self.year - woman.birthdate)-16, self.year-1950]
                birthProb = self.computeBirthProb(self.p['fertilityBias'], rawRate, householdRank)/marriedPercentage[householdRank]
                
            # birthProb = self.computeBirthProb(self.p['fertilityBias'], rawRate, woman.classRank)
            
            #baseRate = self.baseRate(self.socialClassShares, self.p['fertilityBias'], rawRate)
            #fertilityCorrector = (self.socialClassShares[woman.classRank] - self.p['initialClassShares'][woman.classRank])/self.p['initialClassShares'][woman.classRank]
            #baseRate *= 1/math.exp(self.p['fertilityCorrector']*fertilityCorrector)
            #birthProb = baseRate*math.pow(self.p['fertilityBias'], woman.classRank)
            
            if random.random() < birthProb:
                # (self, mother, father, age, birthYear, sex, status, house,
                # classRank, sec, edu, wage, income, finalIncome):
                parentsClassRank = max([woman.classRank, woman.partner.classRank])
                baby = Person(woman, woman.partner, self.year, 0, 'random', woman.house, woman.sec, -1, parentsClassRank, 0, 0, 0, 0, 0, 0, 'child', False)
                self.pop.allPeople.append(baby)
                self.pop.livingPeople.append(baby)
                woman.house.occupants.append(baby)
                woman.children.append(baby)
                woman.partner.children.append(baby)
                if woman.house == self.displayHouse:
                    messageString = str(self.year) + ": #" + str(woman.id) + " had a baby, #" + str(baby.id) + "." 
                    self.textUpdateList.append(messageString)
                    
        postBirth = len(self.pop.livingPeople)
        
        print('the number of births is: ' + str(postBirth - preBirth))
    
    # def doCareAllocation(self):
        
        
    def doDivorces(self):
        menInRelationships = [x for x in self.pop.livingPeople if x.sex == 'male' and x.partner != None ]
        for man in menInRelationships:
            
            age = self.year - man.birthdate 

            ## This is here to manage the sweeping through of this parameter
            ## but only for the years after 2012
            if self.year < self.p['thePresent']:
                splitProb = self.p['basicDivorceRate']*self.p['divorceModifierByDecade'][int(age)/10]
            else:
                splitProb = self.p['variableDivorce']*self.p['divorceModifierByDecade'][int(age)/10]
                
            if random.random() < splitProb:
                # man.children = []
                wife = man.partner
                man.partner = None
                wife.partner = None
                man.yearDivorced.append(self.year)
                wife.yearDivorced.append(self.year)
                if wife.status == 'student':
                    wife.independentStatus = True
                    self.startWorking(wife)
                self.divorceTally += 1
                distance = random.choice(['near','far'])
                if man.house == self.displayHouse:
                    messageString = str(self.year) + ": #" + str(man.id) + " splits with #" + str(wife.id) + "."
                    self.textUpdateList.append(messageString)
                manChildren = [x for x in man.children if x.dead == False and x.house == man.house and x.father == man and x.mother != wife]
                children = [x for x in man.children if x.dead == False and x.house == man.house]
                if np.random.random() < self.p['probChildrenWithFather']:
                    manChildren.extend(children)
                peopleToMove = [man]
                peopleToMove += manChildren
                self.findNewHouse(peopleToMove,distance)
            
    def computeSplitProb(self, rawRate, classRank):
        a = 0
        for i in range(int(self.p['numberClasses'])):
            a += self.socialClassShares[i]*math.pow(self.p['divorceBias'], i)
        baseRate = rawRate/a
        splitProb = baseRate*math.pow(self.p['divorceBias'], classRank)
        return splitProb
            
    def doDivorces_SES(self):
        menInRelationships = [x for x in self.pop.livingPeople if x.sex == 'male' and x.partner != None ]
        for man in menInRelationships:
            
            age = self.year - man.birthdate 

            ## This is here to manage the sweeping through of this parameter
            ## but only for the years after 2012
            if self.year < self.p['thePresent']:
                rawRate = self.p['basicDivorceRate'] * self.p['divorceModifierByDecade'][int(age)/10]
            else:
                rawRate = self.p['variableDivorce'] * self.p['divorceModifierByDecade'][int(age)/10]
                
            splitProb = self.computeSplitProb(rawRate, man.classRank)
                
            if random.random() < splitProb:
                # man.children = []
                wife = man.partner
                man.partner = None
                wife.partner = None
                man.yearDivorced.append(self.year)
                wife.yearDivorced.append(self.year)
                if wife.status == 'student':
                    wife.independentStatus = True
                    self.startWorking(wife)
                self.divorceTally += 1
                distance = random.choice(['near','far'])
                if man.house == self.displayHouse:
                    messageString = str(self.year) + ": #" + str(man.id) + " splits with #" + str(wife.id) + "."
                    self.textUpdateList.append(messageString)
                manChildren = [x for x in man.children if x.dead == False and x.house == man.house and x.father == man and x.mother != wife]
                
                for x in manChildren:
                    if x not in man.house.occupants:
                        print 'Error in doDivorce: man children not in house'
                        sys.exit()
                        
                peopleToMove = [man]
                peopleToMove += manChildren
                self.findNewHouse(peopleToMove,distance)
                
    def doMarriages_Bis(self):
        
        eligibleMen = [x for x in self.pop.livingPeople if x.sex == 'male' and x.partner == None and x.status != 'child' and x.status != 'student']
        eligibleWomen = [x for x in self.pop.livingPeople if x.sex == 'female' and x.partner == None and x.status != 'child']
        
        
        if len(eligibleMen) > 0 and len (eligibleWomen) > 0:
            random.shuffle(eligibleMen)
            random.shuffle(eligibleWomen)
            
            interestedWomen = []
            for w in eligibleWomen:
                womanMarriageProb = self.p['basicFemaleMarriageProb']*self.p['femaleMarriageModifierByDecade'][w.age/10]
                if random.random() < womanMarriageProb:
                    interestedWomen.append(w)
        
            for man in eligibleMen:
                manMarriageProb = self.p['basicMaleMarriageProb']*self.p['maleMarriageModifierByDecade'][man.age/10]
                
                # Adjusting for number of children
                numChildrenWithMan = len([x for x in man.children if x.house == man.house])
                childrenFactor = 1/math.exp(self.p['numChildrenExp']*numChildrenWithMan)
                manMarriageProb *= childrenFactor
                
                # Adjusting to increase rate
                manMarriageProb *= self.p['maleMarriageMultiplier']
                
                
                if random.random() < manMarriageProb:
                    potentialBrides = []
                    for woman in interestedWomen:
                        if woman.house != man.house:
                            if man.mother != None and woman.mother != None:
                                if man.mother != woman.mother and man not in woman.children and woman not in man.children:
                                    potentialBrides.append(woman)
                            else:
                                if man not in woman.children and woman not in man.children:
                                    potentialBrides.append(woman)
                    
                    if len(potentialBrides) > 0:
                        manTown = man.house.town
                        bridesWeights = []
                        for woman in potentialBrides:
                            
                            womanTown = woman.house.town
                            geoDistance = self.manhattanDistance(manTown, womanTown)/float(self.p['mapGridXDimension'] + self.p['mapGridYDimension'])
                            geoFactor = 1/math.exp(self.p['betaGeoExp']*geoDistance)
                            
                            womanRank = woman.classRank
                            if woman.status == 'student':
                                womanRank = max(woman.father.classRank, woman.mother.classRank)
                            statusDistance = float(abs(man.classRank-womanRank))/float((self.p['numberClasses']-1))
                            if man.classRank < woman.classRank:
                                betaExponent = self.p['betaSocExp']
                            else:
                                betaExponent = self.p['betaSocExp']*self.p['rankGenderBias']
                            socFactor = 1/math.exp(betaExponent*statusDistance)
                            
                            ageFactor = self.p['deltageProb'][self.deltaAge(man.age-woman.age)]
                            
                            numChildrenWithWoman = len([x for x in woman.children if x.house == woman.house])
                            
                            childrenFactor = 1/math.exp(self.p['numChildrenExp']*numChildrenWithWoman)
                            
                            marriageProb = geoFactor*socFactor*ageFactor*childrenFactor
                            
                            bridesWeights.append(marriageProb)
                            
                        if sum(bridesWeights) > 0:
                            bridesProb = [i/sum(bridesWeights) for i in bridesWeights]
                            woman = np.random.choice(potentialBrides, p = bridesProb)
                        else:
                            woman = np.random.choice(potentialBrides)
                        man.partner = woman
                        woman.partner = man
                        man.yearMarried.append(self.year)
                        woman.yearMarried.append(self.year)
                        interestedWomen.remove(woman)
                        
                        self.marriageTally += 1
    
                        if man.house == self.displayHouse or woman.house == self.displayHouse:
                            messageString = str(self.year) + ": #" + str(man.id) + " (age " + str(man.age) + ")"
                            messageString += " and #" + str(woman.id) + " (age " + str(woman.age)
                            messageString += ") marry."
                            self.textUpdateList.append(messageString)
        
    def doMarriages(self):
        """
        Marriages were originally intended to be done locally, i.e.,
        there would be an annual matchmaking process within each town.
        But the population per town can be so low that this made
        marriages really hard to arrange. An Allee effect for humans,
        basically.  So marriages are sorted out with the entire
        population as a mating pool.
        """
        
        
#        eligibleMen = [x for x in self.pop.livingPeople if x.sex == 'male' and x.partner == None and x.status == 'worker']
#        eligibleWomen = [x for x in self.pop.livingPeople if x.sex == 'female' and x.partner == None and x.status != 'child']
        
        eligibleMen = []
        eligibleWomen = []
        
        for i in self.pop.livingPeople:
            if i.status != 'child' and i.partner == None:
                if i.sex == 'male':
                    eligibleMen.append(i)
                else:
                    eligibleWomen.append(i)

        # print len(eligibleMen)
        
        if len(eligibleMen) > 0 and len (eligibleWomen) > 0:
            random.shuffle(eligibleMen)
            random.shuffle(eligibleWomen)

            interestedWomen = []
            for w in eligibleWomen:
                womanAge = self.year - w.birthdate
                womanMarriageProb = ( self.p['basicFemaleMarriageProb']
                                      * self.p['femaleMarriageModifierByDecade'][int(womanAge)/10] )
                if random.random() < womanMarriageProb:
                    interestedWomen.append(w)
                
            for m in eligibleMen:
                manAge = self.year - m.birthdate
                manMarriageProb = self.p['basicMaleMarriageProb']*self.p['maleMarriageModifierByDecade'][int(manAge)/10]
                if random.random() < manMarriageProb:
                    for w in interestedWomen:
                        womanAge = self.year - w.birthdate
                        diff = manAge - womanAge
                        if diff < 20 and diff > -5 and m.mother != w.mother and m.house != w.house:
                            m.partner = w
                            w.partner = m
                            m.yearMarried.append(self.year)
                            w.yearMarried.append(self.year)
                            interestedWomen.remove(w)
                            self.marriageTally += 1
                            if m.house == self.displayHouse or w.house == self.displayHouse:
                                messageString = str(self.year) + ": #" + str(m.id) + " (age " + str(manAge) + ")"
                                messageString += " and #" + str(w.id) + " (age " + str(womanAge)
                                messageString += ") marry."
                                self.textUpdateList.append(messageString)
                            break
                        
        print float(self.marriageTally)/float(len(self.pop.livingPeople))
                            
    def doMarriages_SES(self):
        
        eligibleMen = []
        eligibleWomen = []

        for i in self.pop.livingPeople:
            if i.partner == None:
                # Men need to be employed to marry
                if i.sex == 'male' and i.status == 'worker':
                    eligibleMen.append(i)
                    
        ######     Otional: select a subset of eligible men based on age    ##########################################
        potentialGrooms = []
        for m in eligibleMen:
            incomeFactor = (math.exp(self.p['incomeMarriageParam']*m.income)-1)/math.exp(self.p['incomeMarriageParam']*m.income)
            
            manMarriageProb = self.p['basicMaleMarriageProb']*self.p['maleMarriageModifierByDecade'][m.age/10]*incomeFactor
            if random.random() < manMarriageProb:
                potentialGrooms.append(m)
        
        # print float(len(potentialGrooms))/float(len(eligibleMen))
        ###########################################################################################################
        
        for man in potentialGrooms: # for man in eligibleMen: # 
            # maxEncounters = self.datingActivity(man)
            eligibleWomen = [x for x in self.pop.livingPeople if x.sex == 'female' and x.age >= self.p['minPregnancyAge'] and x.house != man.house and x.partner == None]
            
            potentialBrides = []
            for woman in eligibleWomen:
                if man.mother != None and woman.mother != None:
                    if man.mother != woman.mother and man not in woman.children and woman not in man.children:
                        potentialBrides.append(woman)
                else:
                    if man not in woman.children and woman not in man.children:
                        potentialBrides.append(woman)

            if len(potentialBrides) > 0:
                manTown = man.house.town
                bridesWeights = []
                for woman in potentialBrides:
                    studentFactor = 1.0
                    if woman.status == 'student':
                        studentFactor = self.p['studentFactorParam']
                    womanTown = woman.house.town
                    geoDistance = self.manhattanDistance(manTown, womanTown)/float(self.p['mapGridXDimension'] + self.p['mapGridYDimension'])
                    geoFactor = 1/math.exp(self.p['betaGeoExp']*geoDistance)
                    
                    statusDistance = float(abs(man.classRank-woman.classRank))/float((self.p['numberClasses']-1))
                    if man.classRank < woman.classRank:
                        betaExponent = self.p['betaSocExp']
                    else:
                        betaExponent = self.p['betaSocExp']*self.p['rankGenderBias']
                    socFactor = 1/math.exp(betaExponent*statusDistance)
                    
                    ageFactor = self.p['deltageProb'][self.deltaAge(man.age-woman.age)]
                    
                    marriageProb = geoFactor*socFactor*ageFactor*studentFactor
                    
                    bridesWeights.append(marriageProb)
                if sum(bridesWeights) > 0:
                    bridesProb = [i/sum(bridesWeights) for i in bridesWeights]
                    woman = np.random.choice(potentialBrides, p = bridesProb)
                else:
                    woman = np.random.choice(potentialBrides)
                man.partner = woman
                woman.partner = man
                man.yearMarried.append(self.year)
                woman.yearMarried.append(self.year)
                
                self.marriageTally += 1
    
                if man.house == self.displayHouse or woman.house == self.displayHouse:
                    messageString = str(self.year) + ": #" + str(man.id) + " (age " + str(man.age) + ")"
                    messageString += " and #" + str(woman.id) + " (age " + str(woman.age)
                    messageString += ") marry."
                    self.textUpdateList.append(messageString)
                    
        print float(self.marriageTally)/float(len(self.pop.livingPeople))
    
    def deltaAge(self, dA):
        if dA <= -10 :
            cat = 0
        elif dA >= -9 and dA <= -3:
            cat = 1
        elif dA >= -2 and dA <= 0:
            cat = 2
        elif dA >= 1 and dA <= 4:
            cat = 3
        elif dA >= 5 and dA <= 9:
            cat = 4
        else:
            cat = 5
        return cat

     
    def doMovingAround(self):
        """
        Various reasons why a person or family group might want to
        move around. People who are in partnerships but not living
        together are highly likely to find a place together. Adults
        still living at home might be ready to move out this year.
        Single people might want to move in order to find partners. A
        family might move at random for work reasons. Older people
        might move back in with their kids.
        """
        for i in self.pop.livingPeople:
            i.movedThisYear = False
            
        ## Need to keep track of this to avoid multiple moves
        separetedSpouses = [x for x in self.pop.livingPeople if x.partner != None and x.house != x.partner.house]
        couples = []
        for i in separetedSpouses:
            couples.append([i, i.partner])
            
        
            
        for person in separetedSpouses:
            
            
            if person.house != person.partner.house:
            
                if len(person.yearMarried) > 0 and  person.yearMarried[-1] == self.year and person.house == person.partner.house:
                    print 'Error: couple already in same house!'
                    sys.exit()
                
                # if person.partner != None and person.house != person.partner.house:
                    ## so we have someone who lives apart from their partner...
                    ## very likely they will change that
                if random.random() < self.p['probApartWillMoveTogether']:
                    peopleToMove = [person,person.partner]
                    personChildren = self.bringTheKids(person)
                    peopleToMove += personChildren
                    partnerChildren = self.bringTheKids(person.partner)
                    peopleToMove += [x for x in partnerChildren if x not in personChildren]
                    
                    if random.random() < self.p['coupleMovesToExistingHousehold']:
                        myHousePop = len(person.house.occupants)
                        yourHousePop = len(person.partner.house.occupants)
                        if yourHousePop < myHousePop:
                            targetHouse = person.partner.house
                        else:
                            targetHouse = person.house
                        if person.house == self.displayHouse:
                            messageString = str(self.year) + ": #" + str(person.id) + " and #" + str(person.partner.id)
                            messageString += " move to existing household."
                            self.textUpdateList.append(messageString)
                        self.movePeopleIntoChosenHouse(targetHouse,person.house,peopleToMove, 0)                        
                    else:
                        distance = random.choice(['here','near'])
                        if person.house == self.displayHouse:
                            messageString = str(self.year) + ": #" + str(person.id) + " moves out to live with #" + str(person.partner.id)
                            if len(peopleToMove) > 2:
                                messageString += ", bringing the kids"
                            messageString += "."
                            self.textUpdateList.append(messageString)
                        self.findNewHouse(peopleToMove,distance)                        
    
                    if person.independentStatus == False:
                        person.independentStatus = True
                    if person.partner.independentStatus == False:
                        person.partner.independentStatus = True

        for person in self.pop.livingPeople:
            age = self.year - person.birthdate
            ageClass = age / 10
            
            if person.movedThisYear:
                continue
            
            elif person.status == 'worker' and person.independentStatus == False and person.partner == None:
                ## a single person who hasn't left home yet
                if random.random() < ( self.p['basicProbAdultMoveOut']
                                       * self.p['probAdultMoveOutModifierByDecade'][ageClass] ):
                    peopleToMove = [person]
                    peopleToMove += self.bringTheKids(person)
                    distance = random.choice(['here','near'])
                    if person.house == self.displayHouse:
                        messageString = str(self.year) + ": #" + str(person.id) + " moves out, aged " + str(self.year-person.birthdate) + "."
                        self.textUpdateList.append(messageString)
                    self.findNewHouse(peopleToMove,distance)
                    person.independentStatus = True
                    

            elif person.independentStatus == True and person.partner == None:
                ## a young-ish person who has left home but is still (or newly) single
                if random.random() < ( self.p['basicProbSingleMove']
                                       * self.p['probSingleMoveModifierByDecade'][int(ageClass)] ):
                    peopleToMove = [person]
                    peopleToMove += self.bringTheKids(person)
                    distance = random.choice(['here','near'])
                    if person.house == self.displayHouse:
                        messageString = str(self.year) + ": #" + str(person.id) + " moves to meet new people."
                        self.textUpdateList.append(messageString)
                    self.findNewHouse(peopleToMove,distance)

            elif person.status == 'retired' and len(person.house.occupants) == 1:
                ## a retired person who lives alone
                for c in person.children:
                    if ( c.dead == False ):
                        distance = self.manhattanDistance(person.house.town,c.house.town)
                        distance += 1.0
                        if self.year < self.p['thePresent']:
                            mbRate = self.p['agingParentsMoveInWithKids']/distance
                        else:
                            mbRate = self.p['variableMoveBack']/distance
                        if random.random() < mbRate:
                            peopleToMove = [person]
                            if person.house == self.displayHouse:
                                messageString = str(self.year) + ": #" + str(person.id) + " is going to live with one of their children."
                                self.textUpdateList.append(messageString)
                            self.movePeopleIntoChosenHouse(c.house,person.house,peopleToMove, 0)
                            break
                        
        
            
            elif person.partner != None and person.yearMarried[-1] != self.year:
                ## any other kind of married person, e.g., a normal family with kids
                house = person.house
                household = [x for x in house.occupants]
                
                relocationCost = sum([math.pow(x.yearInTown, self.p['relocationCostParam']) for x in household])
                relocationCostFactor = math.exp(self.p['relocationCostBeta']*relocationCost)
                perCapitaIncome = float(sum([x.income for x in household]))/float(len(household))
                incomeFactor = math.exp(self.p['incomeRelocationBeta']*perCapitaIncome)
                relativeRelocationCostFactor = relocationCostFactor/incomeFactor
                probRelocation = self.p['baserelocationRate']/relativeRelocationCostFactor
                
                if random.random() < probRelocation: #self.p['basicProbFamilyMove']* self.p['probFamilyMoveModifierByDecade'][int(ageClass)]:
                    peopleToMove = [x for x in person.house.occupants]
#                    personChildren = self.bringTheKids(person)
#                    peopleToMove += personChildren
#                    partnerChildren = self.bringTheKids(person.partner)
#                    peopleToMove += [x for x in partnerChildren if x not in personChildren]
#                    stepChildrenPartner = [x for x in personChildren if x not in partnerChildren]
#                    stepChildrenPerson = [x for x in partnerChildren if x not in personChildren]
#                    person.children.extend(stepChildrenPerson)
#                    person.partner.children.extend(stepChildrenPartner)
                    distance = random.choice(['here,''near','far'])
                    if person.house == self.displayHouse:
                        messageString = str(self.year) + ": #" + str(person.id) + " and #" + str(person.partner.id) + " move house"
                        if len(peopleToMove) > 2:
                            messageString += " with kids"
                        messageString += "."
                        self.textUpdateList.append(messageString)
                    self.findNewHouse(peopleToMove,distance)
                


    def manhattanDistance(self,t1,t2):
        """Calculates the distance between two towns"""
        xDist = abs(t1.x - t2.x)
        yDist = abs(t1.y - t2.y)
        return xDist + yDist


    def bringTheKids(self,person):
        """Given a person, return a list of their dependent kids who live in the same house as them."""
        returnList = []
        for i in person.children:
            if ( i.house == person.house
                 and i.independentStatus == False
                 and i.dead == False ):
                returnList.append(i)
        return returnList


    def findNewHouse(self,personList,preference):
        """Find an appropriate empty house for the named person and put them in it."""

        newHouse = None
        person = personList[0]
        departureHouse = person.house
        t = person.house.town

        if ( preference == 'here' ):
            ## Anything empty in this town of the right size?
            localPossibilities = [x for x in t.houses
                                  if len(x.occupants) < 1
                                  and person.sec == x.size ]
            if localPossibilities:
                newHouse = random.choice(localPossibilities)

        if ( preference == 'near' or newHouse == None ):
            ## Neighbouring towns?
            if newHouse == None:
                nearbyTowns = [ k for k in self.map.towns
                                if abs(k.x - t.x) <= 1
                                and abs(k.y - t.y) <= 1 ]
                nearbyPossibilities = []
                for z in nearbyTowns:
                    for w in z.houses:
                        if len(w.occupants) < 1 and person.sec == w.size:
                            nearbyPossibilities.append(w)
                if nearbyPossibilities:
                    newHouse = random.choice(nearbyPossibilities)

        if ( preference == 'far' or newHouse == None ):
            ## Anywhere at all?
            if newHouse == None:
                allPossibilities = []
                for z in self.map.allHouses:
                    if len(z.occupants) < 1 and person.sec == z.size:
                        allPossibilities.append(z)
                if allPossibilities:
                    newHouse = random.choice(allPossibilities)

        ## Quit with an error message if we've run out of houses
        if newHouse in self.map.occupiedHouses:
            print 'Error in house selection: already occupied!'
            print newHouse.id
            
        if newHouse == None:
            print "No houses left for person of SEC " + str(person.sec)
            sys.exit()

        ## Actually make the chosen move
        self.movePeopleIntoChosenHouse(newHouse,departureHouse,personList, 1)


    def movePeopleIntoChosenHouse(self,newHouse,departureHouse,personList, case):

        ## Put the new house onto the list of occupied houses if it was empty
        household = list(personList)
        
        if len(household) != len(set(household)):
            print 'Error in movePeopleIntoChosenHouse: double counting people'
            for member in household:
                print member.id
            sys.exit()
        
        
        ## Move everyone on the list over from their former house to the new one
        for i in household:
            
            if i.house == newHouse:
                print 'Error: new house is the old house!'
                sys.exit()
                
            if newHouse.town != departureHouse.town:
                i.yearInTown = 0
                
            oldHouse = i.house
            
            if i not in oldHouse.occupants:
                print 'Error: person not in house.'
                print i.house.id
                print oldHouse.id
                sys.exit()
                
            oldHouse.occupants.remove(i)
            
            if len(oldHouse.occupants) == 0:
                self.map.occupiedHouses.remove(oldHouse)
                ##print "This house is now empty: ", oldHouse
                if (self.p['interactiveGraphics']):
                    self.canvas.itemconfig(oldHouse.icon, state='hidden')
            
            newHouse.occupants.append(i)
            
            i.house = newHouse
            i.movedThisYear = True

        ## This next is sloppy and will lead to loads of duplicates in the
        ## occupiedHouses list, but we don't want to miss any -- that's
        ## much worse -- and the problem will be solved by a conversion
        ## to set and back to list int he stats method in a moment
        if case == 1:
            self.map.occupiedHouses.append(newHouse)
        
        if len(self.map.occupiedHouses) != len(set(self.map.occupiedHouses)):
            print 'Error: house appears twice in occupied houses!'
            houses = []
            for x in self.map.occupiedHouses:
                if x in houses:
                    print x.id
                else:
                    houses.append(x)
            sys.exit()
        
        emptyOccupiedHouses = [x for x in self.map.occupiedHouses if len(x.occupants) == 0]
        
        if len(emptyOccupiedHouses) > 0:
            print 'Error: empty houses among occupied ones!'
            for m in emptyOccupiedHouses:
                print m.id
            sys.exit()
        
        if (self.p['interactiveGraphics']):
            self.canvas.itemconfig(newHouse.icon, state='normal')

            
            
        ## Check whether we've moved into the display house
        if newHouse == self.displayHouse:
            self.textUpdateList.append(str(self.year) + ": New people are moving into " + newHouse.name)
            messageString = ""
            for k in personList:
                messageString += "#" + str(k.id) + " "
            self.textUpdateList.append(messageString)
            
                
        ## or out of it...
        if departureHouse == self.displayHouse:
            self.nextDisplayHouse = newHouse
                

    def doStats(self, policyFolder):
        """Calculate annual stats and store them appropriately."""

        self.times.append(self.year)

        currentPop = len(self.pop.livingPeople)
        self.pops.append(currentPop)
        
        potentialWorkers = [x for x in self.pop.livingPeople if x.age >= self.p['ageOfAdulthood'] and x.age < self.p['ageOfRetirement']]
        employed = [x for x in potentialWorkers if x.status == 'worker' and x.careNeedLevel < 3]
        
        shareEmployed = float(len(employed))/float(len(potentialWorkers))
        self.employmentRate.append(shareEmployed)

        ## Check for double-included houses by converting to a set and back again
        self.map.occupiedHouses = list(set(self.map.occupiedHouses))

        parents = []
        for person in self.pop.livingPeople:
            for child in person.children:
                if person.house == child.house and person.partner != None and (child.age <= 15 or (child.age <= 18 and child.status == 'student')): # self.p['maxWtWChildAge']:
                    parents.append(person)
                    break
        numberCouples = float(len(parents))/2
        loneParents = []
        loneFemaleParents = []
        for person in self.pop.livingPeople:
            for child in person.children:
                if person.house == child.house and person.partner == None and (child.age <= 15 or (child.age <= 18 and child.status == 'student')): # self.p['maxWtWChildAge']:
                    loneParents.append(person)
                    if person.sex == 'female':
                        loneFemaleParents.append(person)
                    break
        numberLoneParents = float(len(loneParents))
        shareSingleParents = numberLoneParents/(numberCouples+numberLoneParents)
        shareFemaleSingleParent = 0
        if numberLoneParents > 0:
            shareFemaleSingleParent = float(len(loneFemaleParents))/numberLoneParents
        self.shareLoneParents.append(shareSingleParents)
        self.shareFemaleLoneParents.append(shareFemaleSingleParent)
        
        
        if self.year == 2017:
            self.sesPops = []
            for i in range(int(self.p['numberClasses'])):
                self.sesPops.append(len([x for x in self.pop.livingPeople if x.age > 23 and x.classRank == i]))
            self.sesPopsShares = [float(x)/float(sum(self.sesPops)) for x in self.sesPops]
            lenFrequency = len(self.incomeDistribution)
            self.incomeFrequencies = [0]*lenFrequency
            households = [y.occupants for y in self.map.occupiedHouses]
            
            self.individualIncomes = [x.income*52 for x in self.pop.livingPeople if x.income > 0]
            
        
            self.householdIncomes = [sum([x.income*52 for x in y]) for y in households]
            
            for i in self.householdIncomes:
                ind = int(i/1000)
                if ind > -1 and ind < lenFrequency:
                    self.incomeFrequencies[ind] += 1

        ## Check for overlooked empty houses
        emptyHouses = [x for x in self.map.occupiedHouses if len(x.occupants) == 0]
        for h in emptyHouses:
            self.map.occupiedHouses.remove(h)
            if (self.p['interactiveGraphics']):
                self.canvas.itemconfig(h.icon, state='hidden')

        ## Avg household size (easily calculated by pop / occupied houses)
        households = len(self.map.occupiedHouses)
        averageHouseholdSize = float(currentPop)/float(households)
        self.avgHouseholdSize.append(averageHouseholdSize)

        self.numMarriages.append(self.marriageTally)
        self.numDivorces.append(self.divorceTally)            
        
        
        totalCareDemandHours = sum([x.careDemand for x in self.pop.livingPeople])
        self.totalCareDemand.append(totalCareDemandHours)
        totalUnmetNeed = sum([x.unmetCareNeed for x in self.pop.livingPeople])
        self.totalUnmetNeed.append(totalUnmetNeed)
        shareUnmetCareNeeds = 0
        if totalCareDemandHours > 0:
            shareUnmetCareNeeds = totalUnmetNeed/totalCareDemandHours
        self.shareUnmetNeed.append(shareUnmetCareNeeds)
        
        totalCareSupply = sum([x.careAvailable for x in self.pop.livingPeople])
        self.totalCareSupply.append(totalCareSupply)
        taxPayers = len([x for x in self.pop.livingPeople if x.status == 'student' or x.status == 'worker'])
        self.numTaxpayers.append(taxPayers)
        
        if totalCareDemandHours == 0:
            familyCareRatio = 0.0
        else:
            familyCareRatio = (totalCareDemandHours - totalUnmetNeed)/totalCareDemandHours

        ##familyCareRatio = ( totalCareDemandHours - unmetNeed ) / (1.0 * (totalCareDemandHours+0.01))
        self.totalFamilyCare.append(familyCareRatio)

        taxBurden = ( totalUnmetNeed * self.p['hourlyCostOfCare'] * 52.18 ) / ( taxPayers * 1.0 )
        self.totalTaxBurden.append(taxBurden)
        
        ## Count the proportion of adult women who are married
        totalAdultWomen = 0
        totalMarriedAdultWomen = 0

        for person in self.pop.livingPeople:
            age = self.year - person.birthdate
            if person.sex == 'female' and age >= 18:
                totalAdultWomen += 1
                if person.partner != None:
                    totalMarriedAdultWomen += 1
        marriagePropNow = float(totalMarriedAdultWomen) / float(totalAdultWomen)
        self.marriageProp.append(marriagePropNow)

        
        outputs = [self.year, currentPop, households, averageHouseholdSize, self.marriageTally, marriagePropNow, self.divorceTally, 
                   shareSingleParents, shareFemaleSingleParent, totalCareDemandHours, totalCareSupply, totalUnmetNeed, shareUnmetCareNeeds, 
                   taxPayers, taxBurden, familyCareRatio, shareEmployed, self.publicCare, self.totalTaxRevenue, self.totalPensionRevenue, 
                   self.pensionExpenditure, self.totalHospitalizationCost]
        
        if self.year == self.p['startYear']:
            if not os.path.exists(policyFolder):
                os.makedirs(policyFolder)
            with open(os.path.join(policyFolder, "Outputs.csv"), "w") as file:
                writer = csv.writer(file, delimiter = ",", lineterminator='\r')
                writer.writerow((self.Outputs))
                writer.writerow(outputs)
        else:
            with open(os.path.join(policyFolder, "Outputs.csv"), "a") as file:
                writer = csv.writer(file, delimiter = ",", lineterminator='\r')
                writer.writerow(outputs)
        
        self.marriageTally = 0
        self.divorceTally = 0
        
        ## Some extra debugging stuff just to check that all
        ## the lists are behaving themselves
        if self.p['verboseDebugging']:
            peopleCount = 0
            for i in self.pop.allPeople:
                if i.dead == False:
                    peopleCount += 1
            print "True pop counting non-dead people in allPeople list = ", peopleCount

            peopleCount = 0
            for h in self.map.occupiedHouses:
                peopleCount += len(h.occupants)
            print "True pop counting occupants of all occupied houses = ", peopleCount

            peopleCount = 0
            for h in self.map.allHouses:
                peopleCount += len(h.occupants)
            print "True pop counting occupants of ALL houses = ", peopleCount

            tally = [ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            for h in self.map.occupiedHouses:
                tally[len(h.occupants)] += 1
            for i in range(len(tally)):
                if tally[i] > 0:
                    print i, tally[i]
            print

            
    def healthServiceCost(self):

        peopleWithUnmetNeed = [x for x in self.pop.livingPeople if x.careNeedLevel > 0]
        self.totalHospitalizationCost = 0
        for person in peopleWithUnmetNeed:
            needLevelFactor = math.pow(self.p['needLevelParam'], person.careNeedLevel)
            unmetSocialCareFactor = math.pow(self.p['unmetSocialCareParam'], person.averageShareUnmetNeed)
            averageHospitalization = self.p['hospitalizationParam']*needLevelFactor*unmetSocialCareFactor
            self.totalHospitalizationCost += averageHospitalization*self.p['costHospitalizationPerDay']
        self.hospitalizationCost.append(self.totalHospitalizationCost)
        
    def initializeCanvas(self):
        """Put up a TKInter canvas window to animate the simulation."""
        self.canvas.pack()

        ## Draw some numbers for the population pyramid that won't be redrawn each time
        for a in range(0,self.p['num5YearAgeClasses']):
            self.canvas.create_text(170, 385 - (10 * a),
                                    text=str(5*a) + '-' + str(5*a+4),
                                    font='Helvetica 6',
                                    fill='white')

        ## Draw the overall map, including towns and houses (occupied houses only)
        for t in self.map.towns:
            xBasic = 580 + (t.x * self.p['pixelsPerTown'])
            yBasic = 15 + (t.y * self.p['pixelsPerTown'])
            self.canvas.create_rectangle(xBasic, yBasic,
                                         xBasic+self.p['pixelsPerTown'],
                                         yBasic+self.p['pixelsPerTown'],
                                         outline='grey',
                                         state = 'hidden' )

        for h in self.map.allHouses:
            t = h.town
            xBasic = 580 + (t.x * self.p['pixelsPerTown'])
            yBasic = 15 + (t.y * self.p['pixelsPerTown'])
            xOffset = xBasic + 2 + (h.x * 2)
            yOffset = yBasic + 2 + (h.y * 2)

            outlineColour = fillColour = self.p['houseSizeColour'][h.size]
            width = 1

            h.icon = self.canvas.create_rectangle(xOffset,yOffset,
                                                  xOffset + width, yOffset + width,
                                                  outline=outlineColour,
                                                  fill=fillColour,
                                                  state = 'normal' )

        self.canvas.update()
        time.sleep(0.5)
        self.canvas.update()

        for h in self.map.allHouses:
            self.canvas.itemconfig(h.icon, state='hidden')

        for h in self.map.occupiedHouses:
            self.canvas.itemconfig(h.icon, state='normal')

        self.canvas.update()
        self.updateCanvas()

    def updateCanvas(self):
        """Update the appearance of the graphics canvas."""

        ## First we clean the canvas off; some items are redrawn every time and others are not
        self.canvas.delete('redraw')

        ## Now post the current year and the current population size
        self.canvas.create_text(self.p['dateX'],
                                self.p['dateY'],
                                text='Year: ' + str(self.year),
                                font = self.p['mainFont'],
                                fill = self.p['fontColour'],
                                tags = 'redraw')
        self.canvas.create_text(self.p['popX'],
                                self.p['popY'],
                                text='Pop: ' + str(len(self.pop.livingPeople)),
                                font = self.p['mainFont'],
                                fill = self.p['fontColour'],
                                tags = 'redraw')

        self.canvas.create_text(self.p['popX'],
                                self.p['popY'] + 30,
                                text='Ever: ' + str(len(self.pop.allPeople)),
                                font = self.p['mainFont'],
                                fill = self.p['fontColour'],
                                tags = 'redraw')

        ## Also some other stats, but not on the first display
        if self.year > self.p['startYear']:
            self.canvas.create_text(350,20,
                                    text='Avg household: ' + str ( round ( self.avgHouseholdSize[-1] , 2 ) ),
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,40,
                                    text='Marriages: ' + str(self.numMarriages[-1]),
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,60,
                                    text='Divorces: ' + str(self.numDivorces[-1]),
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,100,
                                    text='Total care demand: ' + str(round(self.totalCareDemand[-1], 0 ) ),
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,120,
                                    text='Num taxpayers: ' + str(round(self.numTaxpayers[-1], 0 ) ),
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,140,
                                    text='Family care ratio: ' + str(round(100.0 * self.totalFamilyCare[-1], 0 ) ) + "%",
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,160,
                                    text='Tax burden: ' + str(round(self.totalTaxBurden[-1], 0 ) ),
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,180,
                                    text='Marriage prop: ' + str(round(100.0 * self.marriageProp[-1], 0 ) ) + "%",
                                    font = 'Helvetica 11',
                                    fill = self.p['fontColour'],
                                    tags = 'redraw')

        

        ## Draw the population pyramid split by care categories
        for a in range(0,self.p['num5YearAgeClasses']):
            malePixel = 153
            femalePixel = 187
            for c in range(0,self.p['numCareLevels']):
                mWidth = self.pyramid.maleData[a,c]
                fWidth = self.pyramid.femaleData[a,c]

                if mWidth > 0:
                    self.canvas.create_rectangle(malePixel, 380 - (10*a),
                                                 malePixel - mWidth, 380 - (10*a) + 9,
                                                 outline=self.p['careLevelColour'][c],
                                                 fill=self.p['careLevelColour'][c],
                                                 tags = 'redraw')
                malePixel -= mWidth
                
                if fWidth > 0:
                    self.canvas.create_rectangle(femalePixel, 380 - (10*a),
                                                 femalePixel + fWidth, 380 - (10*a) + 9,
                                                 outline=self.p['careLevelColour'][c],
                                                 fill=self.p['careLevelColour'][c],
                                                 tags = 'redraw')
                femalePixel += fWidth

        ## Draw in the display house and the people who live in it
        if len(self.displayHouse.occupants) < 1:
            ## Nobody lives in the display house any more, choose another
            if self.nextDisplayHouse != None:
                self.displayHouse = self.nextDisplayHouse
                self.nextDisplayHouse = None
            else:
                self.displayHouse = random.choice(self.pop.livingPeople).house
                self.textUpdateList.append(str(self.year) + ": Display house empty, going to " + self.displayHouse.name + ".")
                messageString = "Residents: "
                for k in self.displayHouse.occupants:
                    messageString += "#" + str(k.id) + " "
                self.textUpdateList.append(messageString)
            

        outlineColour = self.p['houseSizeColour'][self.displayHouse.size]
        self.canvas.create_rectangle( 50, 450, 300, 650,
                                      outline = outlineColour,
                                      tags = 'redraw' )
        self.canvas.create_text ( 60, 660,
                                  text="Display house " + self.displayHouse.name,
                                  font='Helvetica 10',
                                  fill='white',
                                  anchor='nw',
                                  tags='redraw')
                                  

        ageBracketCounter = [ 0, 0, 0, 0, 0 ]

        for i in self.displayHouse.occupants:
            age = self.year - i.birthdate
            ageBracket = age / 20
            if ageBracket > 4:
                ageBracket = 4
            careClass = i.careNeedLevel
            sex = i.sex
            idNumber = i.id
            self.drawPerson(age,ageBracket,ageBracketCounter[ageBracket],careClass,sex,idNumber)
            ageBracketCounter[ageBracket] += 1


        ## Draw in some text status updates on the right side of the map
        ## These need to scroll up the screen as time passes

        if len(self.textUpdateList) > self.p['maxTextUpdateList']:
            excess = len(self.textUpdateList) - self.p['maxTextUpdateList']
            self.textUpdateList = self.textUpdateList[excess:excess+self.p['maxTextUpdateList']]

        baseX = 1035
        baseY = 30
        for i in self.textUpdateList:
            self.canvas.create_text(baseX,baseY,
                                    text=i,
                                    anchor='nw',
                                    font='Helvetica 9',
                                    fill = 'white',
                                    width = 265,
                                    tags = 'redraw')
            baseY += 30

        ## Finish by updating the canvas and sleeping briefly in order to allow people to see it
        self.canvas.update()
        if self.p['delayTime'] > 0.0:
            time.sleep(self.p['delayTime'])


    def drawPerson(self, age, ageBracket, counter, careClass, sex, idNumber):
        baseX = 70 + ( counter * 30 )
        baseY = 620 - ( ageBracket * 30 )

        fillColour = self.p['careLevelColour'][careClass]

        self.canvas.create_oval(baseX,baseY,baseX+6,baseY+6,
                                fill=fillColour,
                                outline=fillColour,tags='redraw')
        if sex == 'male':
            self.canvas.create_rectangle(baseX-2,baseY+6,baseX+8,baseY+12,
                                fill=fillColour,outline=fillColour,tags='redraw')
        else:
            self.canvas.create_polygon(baseX+2,baseY+6,baseX-2,baseY+12,baseX+8,baseY+12,baseX+4,baseY+6,
                                fill=fillColour,outline=fillColour,tags='redraw')
        self.canvas.create_rectangle(baseX+1,baseY+13,baseX+5,baseY+20,
                                     fill=fillColour,outline=fillColour,tags='redraw')
            
            
            
        self.canvas.create_text(baseX+11,baseY,
                                text=str(age),
                                font='Helvetica 6',
                                fill='white',
                                anchor='nw',
                                tags='redraw')
        self.canvas.create_text(baseX+11,baseY+8,
                                text=str(idNumber),
                                font='Helvetica 6',
                                fill='grey',
                                anchor='nw',
                                tags='redraw')


    def doGraphs(self):
        """Plot the graphs needed at the end of one run."""
        
        

        p1, = pylab.plot(self.times,self.pops,color="red")
        p2, = pylab.plot(self.times,self.numTaxpayers,color="blue")
        pylab.legend([p1, p2], ['Total population', 'Taxpayers'],loc='lower right')
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Number of people')
        pylab.xlabel('Year')
        pylab.savefig('popGrowth.pdf')
        pylab.show()
        pylab.close()

        pylab.plot(self.times,self.avgHouseholdSize,color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Average household size')
        pylab.xlabel('Year')
        pylab.savefig('avgHousehold.pdf')
        pylab.show()
        pylab.close()

        p1, = pylab.plot(self.times,self.totalCareDemand,color="red")
        p2, = pylab.plot(self.times,self.totalCareSupply,color="blue")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.legend([p1, p2], ['Care demand', 'Total theoretical supply'],loc='lower right')
        pylab.ylabel('Total hours per week')
        pylab.xlabel('Year')
        pylab.savefig('totalCareSituation.pdf')
        pylab.show()

        pylab.plot(self.times,self.totalFamilyCare,color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Proportion of informal social care')
        pylab.xlabel('Year')
        pylab.savefig('informalCare.pdf')
        pylab.show()

        pylab.plot(self.times,self.totalTaxBurden,color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Care costs in pounds per taxpayer per year')
        pylab.xlabel('Year')
        pylab.savefig('taxBurden.pdf')
        pylab.show()

        pylab.plot(self.times,self.marriageProp,color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Proportion of married adult women')
        pylab.xlabel('Year')
        pylab.savefig('marriageProp.pdf')
        pylab.savefig('marriageProp.png')
        pylab.show()
        
        pylab.plot(self.times,self.shareLoneParents,color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Share of Lone Parents')
        pylab.xlabel('Year')
        pylab.savefig('shareLoneParents.pdf')
        pylab.savefig('shareLoneParents.png')
        pylab.show()
        
        pylab.plot(self.times, self.shareUnmetNeed, color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Share of Unmet Care Need')
        pylab.xlabel('Year')
        pylab.savefig('shareUnmetCareNeed.pdf')
        pylab.savefig('shareUnmetCareNeed.png')
        pylab.show()
        
        pylab.plot(self.times, self.hospitalizationCost, color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Hospitalisation Cost')
        pylab.xlabel('Year')
        pylab.savefig('hospitalisationCost.pdf')
        pylab.savefig('hospitalisationCost.png')
        pylab.show()
        
        pylab.plot(self.times, self.employmentRate, color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Employment Rate')
        pylab.xlabel('Year')
        pylab.savefig('employmentRate.pdf')
        pylab.savefig('employmentRate.png')
        pylab.show()
        
        pylab.plot(self.times, self.publicCareProvision, color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Public Care Provision')
        pylab.xlabel('Year')
        pylab.savefig('publicCareProvision.pdf')
        pylab.savefig('publicCareProvision.png')
        pylab.show()
        
        y_pos = np.arange(len(self.sesPopsShares))
        plt.bar(y_pos, self.sesPopsShares)
        plt.ylabel('SES Populations')
        plt.show()
        
        lenFrequency = len(self.incomeDistribution)
        individualIncomeFrequencies = [0]*lenFrequency

        dK = np.random.normal(0, self.p['wageVar'])
        indDist = np.random.choice(self.incomesPercentiles, len(self.individualIncomes))*math.exp(dK)
        for i in indDist:
            ind = int(i/1000)
            if ind > -1 and ind < lenFrequency:
                individualIncomeFrequencies[ind] += 1
                
        y_pos = np.arange(lenFrequency)
        plt.bar(y_pos, individualIncomeFrequencies)
        plt.ylabel('individual frequency (empirical)')
        plt.show()
        
        lenFrequency = len(self.incomeDistribution)
        individualIncomeFrequencies = [0]*lenFrequency
        for i in self.individualIncomes:
            ind = int(i/1000)
            if ind > -1 and ind < lenFrequency:
                individualIncomeFrequencies[ind] += 1
                
        y_pos = np.arange(lenFrequency)
        plt.bar(y_pos, individualIncomeFrequencies)
        plt.ylabel('individual frequency (simulated)')
        plt.show()
        
        df = pd.DataFrame()
        df[0] = self.individualIncomes
        df[1] = indDist
        fig, ax = plt.subplots(1,1)
        for s in df.columns:
            df[s].plot(kind='density')
        fig.show()
    

class PopPyramid:
    """Builds a data object for storing population pyramid data in."""
    def __init__ (self, ageClasses, careLevels):
        self.maleData = pylab.zeros((int(ageClasses), int(careLevels)),dtype=int)
        self.femaleData = pylab.zeros((int(ageClasses), int(careLevels)),dtype=int)

    def update(self, year, ageClasses, careLevels, pixelFactor, people):
        ## zero the two arrays
        for a in range (int(ageClasses)):
            for c in range (int(careLevels)):
                self.maleData[a,c] = 0
                self.femaleData[a,c] = 0
        ## tally up who belongs in which category
        for i in people:
            ageClass = ( year - i.birthdate ) / 5
            if ageClass > ageClasses - 1:
                ageClass = ageClasses - 1
            careClass = i.careNeedLevel
            if i.sex == 'male':
                self.maleData[int(ageClass), int(careClass)] += 1
            else:
                self.femaleData[int(ageClass), int(careClass)] += 1

        ## normalize the totals into pixels
        total = len(people)        
        for a in range (int(ageClasses)):
            for c in range (int(careLevels)):
                self.maleData[a,c] = pixelFactor * self.maleData[a,c] / total
                self.femaleData[a,c] = pixelFactor * self.femaleData[a,c] / total
