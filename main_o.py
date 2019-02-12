
from sim import Sim
import os
import cProfile
import pylab
import math
import matplotlib.pyplot as plt
import random
import csv
import numpy as np
import pandas as pd
import itertools
from itertools import izip_longest
from collections import OrderedDict
import time
import datetime
import multiprocessing

def meta_params():
    
    m = OrderedDict() # For meta-parameters file
    
    m['numRepeats'] = 1
    m['initialPop'] = 750
    m['startYear'] = 1860
    m['endYear'] = 2050
    m['thePresent'] = 2012
    m['statsCollectFrom'] = 1960
    m['policyStartYear'] = 2020
    m['minStartAge'] = 20
    m['maxStartAge'] = 40
    m['verboseDebugging'] = False
    m['singleRunGraphs'] = False
    m['favouriteSeed'] = int(time.time())
    m['loadFromFile'] = False
    m['numberClasses'] = 5
    m['numCareLevels'] = 5
    m['timeDiscountingRate'] = 0.035
        ## Description of the map, towns, and houses
    m['mapGridXDimension'] = 8
    m['mapGridYDimension'] = 12    
    m['townGridDimension'] = 25
    m['numHouseClasses'] = 3
    m['houseClasses'] = ['small','medium','large']
    m['cdfHouseClasses'] = [ 0.6, 0.9, 5.0 ]

    m['ukMap'] = [0.0, 0.1, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0,
                  0.1, 0.1, 0.2, 0.2, 0.3, 0.0, 0.0, 0.0,
                  0.0, 0.2, 0.2, 0.3, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.2, 1.0, 0.5, 0.0, 0.0, 0.0, 0.0,
                  0.4, 0.0, 0.2, 0.2, 0.4, 0.0, 0.0, 0.0,
                  0.6, 0.0, 0.0, 0.3, 0.8, 0.2, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.6, 0.8, 0.4, 0.0, 0.0,
                  0.0, 0.0, 0.2, 1.0, 0.8, 0.6, 0.1, 0.0,
                  0.0, 0.0, 0.1, 0.2, 1.0, 0.6, 0.3, 0.4,
                  0.0, 0.0, 0.5, 0.7, 0.5, 1.0, 1.0, 0.0,
                  0.0, 0.0, 0.2, 0.4, 0.6, 1.0, 1.0, 0.0,
                  0.0, 0.2, 0.3, 0.0, 0.0, 0.0, 0.0, 0.0]

    m['ukClassBias'] = [0.0, -0.05, -0.05, -0.05, 0.0, 0.0, 0.0, 0.0,
                        -0.05, -0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, -0.05, -0.05, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, -0.05, -0.05, 0.05, 0.0, 0.0, 0.0, 0.0,
                        -0.05, 0.0, -0.05, -0.05, 0.0, 0.0, 0.0, 0.0,
                        -0.05, 0.0, 0.0, -0.05, -0.05, -0.05, 0.0, 0.0,
                        0.0, 0.0, 0.0, -0.05, -0.05, -0.05, 0.0, 0.0,
                        0.0, 0.0, -0.05, -0.05, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, -0.05, 0.0, -0.05, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, -0.05, 0.0, 0.2, 0.15, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.1, 0.2, 0.15, 0.0,
                        0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0]
    
    m['mapDensityModifier'] = 0.6
    ## Graphical interface details
    m['interactiveGraphics'] = False
    m['delayTime'] = 0.0
    m['screenWidth'] = 1300
    m['screenHeight'] = 700
    m['bgColour'] = 'black'
    m['mainFont'] = 'Helvetica 18'
    m['fontColour'] = 'white'
    m['dateX'] = 70
    m['dateY'] = 20
    m['popX'] = 70
    m['popY'] = 50
    m['pixelsInPopPyramid'] = 2000
    m['careLevelColour'] = ['blue','green','yellow','orange','red']
    m['houseSizeColour'] = ['brown','purple','yellow']
    m['pixelsPerTown'] = 56
    m['maxTextUpdateList'] = 22
    
    # multiprocessing params
    m['multiprocessing'] = False
    m['numberProcessors'] = 3
    
    fileName = 'metaParameters.csv'
    c = m.copy()
    for key, value in c.iteritems():
        if not isinstance(value, list):
            c[key] = [value]
    with open(fileName, "wb") as f:
        csv.writer(f).writerow(c.keys())
        csv.writer(f).writerows(itertools.izip_longest(*c.values()))
        
    return m
    
def init_params():
    """Set up the simulation parameters."""

    p = OrderedDict()
    
    # Public Care Provision Parameters
    p['publicCareNeedLevel'] = 5
    p['publicCareAgeLimit'] = 1000
    p['wealthLimitFullStateContribution'] = 14250
    p['wealthLimitPartialStateContribution'] = 23250
    p['partialContributionRate'] = 0.5
    p['minimumIncomeGuarantee'] = 163
    
    # Public Finances Parameters
    p['taxBrakets'] = [663, 228, 0]
    p['taxationRates'] = [0.4, 0.2, 0.0]
    p['statePension'] = 164.35
    p['employeePensionContribution'] = 0.04
    p['employerPensionContribution'] = 0.03
    p['statePensionContribution'] = 0.01
    
    #### SES-version parameters   ######
    
    p['mortalityBias'] = 0.9   ### SES death bias
    p['careNeedBias'] = 0.9   ### Care Need Level death bias
    p['unmetCareNeedBias'] = 0.5  ### Unmet Care Need death bias
    
    p['fertilityBias'] = 0.9  ### Fertility bias
    
    ####  Income-related parameters
    p['workingAge'] = [16, 18, 20, 22, 24]
    p['pensionWage'] = [5.0, 7.0, 10.0, 13.0, 18.0] # [0.64, 0.89, 1.27, 1.66, 2.29] #  
    p['incomeInitialLevels'] = [5.0, 7.0, 9.0, 11.0, 14.0] #[0.64, 0.89, 1.15, 1.40, 1.78] #  
    p['incomeFinalLevels'] = [10.0, 15.0, 22.0, 33.0, 50.0] #[1.27, 1.91, 2.80, 4.21, 6.37] #  
    p['incomeGrowthRate'] = [0.4, 0.35, 0.35, 0.3, 0.25]
    p['wageVar'] = 0.1
    p['workDiscountingTime'] = 0.75
    p['weeklyHours'] = [40.0, 30.0, 20.0, 0.0, 0.0]
    
    # Care transition params
    p['unmetNeedExponent'] = 1.0
    p['careBias'] = 0.9
    p['careTransitionRate'] = 0.7
    
    
    # Social Transition params
    p['educationCosts'] = [0.0, 100.0, 150.0, 200.0] #[0.0, 12.74, 19.12, 25.49] # 
    p['eduWageSensitivity'] = 0.4 # 0.2
    p['eduRankSensitivity'] = 4.0 # 2.0
    p['costantIncomeParam'] = 5.0 # 20.0
    p['costantEduParam'] = 10.0 #  10.0
    p['careEducationParam'] = 0.005 
    
    
    # Marriages params
    p['incomeMarriageParam'] = 0.025
    p['betaGeoExp'] = 2.0
    p['betaSocExp'] = 2.0
    p['rankGenderBias'] = 0.5
    p['deltageProb'] =  [0.0, 0.1, 0.25, 0.4, 0.2, 0.05]
    p['numChildrenExp'] = 1.0
    p['maleMarriageMultiplier'] = 1.3

    # Unmer Need params
    p['unmetCareNeedDiscountParam'] = 0.5
    p['shareUnmetNeedDiscountParam'] = 0.5
    
    # Hospitalisation costs params
    p['hospitalizationParam'] = 0.5
    p['needLevelParam'] = 2.0
    p['unmetSocialCareParam'] = 2.0
    p['costHospitalizationPerDay'] = 400
    
    # Priced growth  #####
    p['wageGrowthRate'] = 1.0 # 1.01338 # 

    ## Mortality statistics
    p['baseDieProb'] = 0.0001
    p['babyDieProb'] = 0.005
    p['maleAgeScaling'] = 14.0
    p['maleAgeDieProb'] = 0.00021
    p['femaleAgeScaling'] = 15.5
    p['femaleAgeDieProb'] = 0.00019
    p['num5YearAgeClasses'] = 28

    ## Transitions to care statistics
    p['baseCareProb'] = 0.0002
    p['personCareProb'] = 0.0008
    ##p['maleAgeCareProb'] = 0.0008
    p['maleAgeCareScaling'] = 18.0
    ##p['femaleAgeCareProb'] = 0.0008
    p['femaleAgeCareScaling'] = 19.0
    p['cdfCareTransition'] = [ 0.7, 0.9, 0.95, 1.0 ]
    p['careLevelNames'] = ['none','low','moderate','substantial','critical']
    p['careDemandInHours'] = [ 0.0, 8.0, 16.0, 30.0, 80.0 ]
    
    ## Availability of care statistics
    p['childHours'] = 5.0
    p['homeAdultHours'] = 30.0
    p['workingAdultHours'] = 25.0
    p['retiredHours'] = 60.0
    p['lowCareHandicap'] = 0.5
    p['hourlyCostOfCare'] = 20.0

    ## Fertility statistics
    p['growingPopBirthProb'] = 0.215
    p['steadyPopBirthProb'] = 0.13
    p['transitionYear'] = 1965
    p['minPregnancyAge'] = 17
    p['maxPregnancyAge'] = 42

    ## Class and employment statistics
    p['numOccupationClasses'] = 3
    p['occupationClasses'] = ['lower','intermediate','higher']
    p['cdfOccupationClasses'] = [ 0.6, 0.9, 1.0 ]

    ## Age transition statistics
    p['ageOfAdulthood'] = 16
    p['ageOfRetirement'] = 65
    
    ## Marriage and divorce statistics (partnerships really)
    p['basicFemaleMarriageProb'] = 0.25
    p['femaleMarriageModifierByDecade'] = [ 0.0, 0.5, 1.0, 1.0, 1.0, 0.6, 0.5, 0.4, 0.1, 0.01, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0 ]
    p['basicMaleMarriageProb'] =  0.3 
    p['maleMarriageModifierByDecade'] = [ 0.0, 0.16, 0.5, 1.0, 0.8, 0.7, 0.66, 0.5, 0.4, 0.2, 0.1, 0.05, 0.01, 0.0, 0.0, 0.0 ]
    p['basicDivorceRate'] = 0.06
    p['variableDivorce'] = 0.06
    p['divorceModifierByDecade'] = [ 0.0, 1.0, 0.9, 0.5, 0.4, 0.2, 0.1, 0.03, 0.01, 0.001, 0.001, 0.001, 0.0, 0.0, 0.0, 0.0 ]
    p['divorceBias'] = 0.85
    p['probChildrenWithFather'] = 0.1
    
    ## Leaving home and moving around statistics
    p['probApartWillMoveTogether'] = 1.0 # 0.3
    p['coupleMovesToExistingHousehold'] = 0.0 # 0.3
    p['basicProbAdultMoveOut'] = 0.22
    p['probAdultMoveOutModifierByDecade'] = [ 0.0, 0.2, 1.0, 0.6, 0.3, 0.15, 0.03, 0.03, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ]
    p['basicProbSingleMove'] = 0.05
    p['probSingleMoveModifierByDecade'] = [ 0.0, 1.0, 1.0, 0.8, 0.4, 0.06, 0.04, 0.02, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ]
    p['basicProbFamilyMove'] = 0.03
    p['probFamilyMoveModifierByDecade'] = [ 0.0, 0.5, 0.8, 0.5, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1 ]
    p['agingParentsMoveInWithKids'] = 0.1
    p['variableMoveBack'] = 0.1

    # Save default parameters in separated folder
    folder = 'defaultSimFolder'
    if not os.path.exists(folder):
        os.makedirs(folder)
    filePath = folder + '/defaultParameters.csv'
    c = p.copy()
    for key, value in c.iteritems():
        if not isinstance(value, list):
            c[key] = [value]
    with open(filePath, "wb") as f:
        csv.writer(f).writerow(c.keys())
        csv.writer(f).writerows(itertools.izip_longest(*c.values()))

    return p


def loadScenarios():
    defaultParams = pd.read_csv('defaultParameters.csv', sep=',', header=0)
    sensitivityParams = pd.read_csv('sensitivityParameters.csv', sep=',', header=0)
    names = sensitivityParams.columns
    numberRows = sensitivityParams.shape[0]
    defaultScenario = defaultParams.copy()
    defaultScenario['scenarioIndex'] = np.nan

    scenarios = []
    if sensitivityParams['combinationKey'][0] == 0: # Single scenario: default parameters
        defaultScenario['scenarioIndex'][0] = 0
        scenarios.append(defaultScenario)
        
    elif sensitivityParams['combinationKey'][0] == 1: # One scenario for each row of the sensitivityParams file (missing values are set to default)
        index = 0
        for n in range(numberRows):
            newScenario = defaultScenario.copy()
            for i in names[1:]:
                if not pd.isnull(sensitivityParams[i][n]):
                    newScenario[i][0] = sensitivityParams[i][n]
            newScenario['scenarioIndex'][0] = index
            index += 1
            scenarios.append(newScenario)
            
    elif sensitivityParams['combinationKey'][0] == 2: # One scenario for each value in the sensitivityParams file
        index = 0
        for n in range(numberRows):
            for i in names[1:]:
                newScenario = defaultScenario.copy()
                if pd.isnull(sensitivityParams[i][n]):
                    continue
                else:
                    newScenario[i][0] = sensitivityParams[i][n]
                newScenario['scenarioIndex'][0] = index
                index += 1
                scenarios.append(newScenario)
                
    else:  # All the different combinations of values in the sensitivityParams file
        scenariosParametersList = []
        parNames = []
        for i in names[1:]:
            if pd.isnull(sensitivityParams[i][0]):
                continue
            parNames.append(i)
            scenariosParametersList.append([x for x in sensitivityParams[i] if pd.isnull(x) == False])
        combinations = list(itertools.product(*scenariosParametersList))
        index = 0
        for c in combinations:
            newScenario = defaultScenario.copy()
            for v in c:
                newScenario[parNames[c.index(v)]][0] = v
            newScenario['scenarioIndex'][0] = index
            index += 1
            scenarios.append(newScenario)

    return scenarios

def loadPolicies(scenarios):
    policiesParams = pd.read_csv('policyParameters.csv', sep=',', header=0)
    names = policiesParams.columns
    numberRows = policiesParams.shape[0]
  
    policies = [[] for x in xrange(len(scenarios))]
    
    for i in range(len(scenarios)):
        index = 0
        policyParams = pd.DataFrame()
        policyParams['policyIndex'] = np.nan
        for j in names[1:]:
            policyParams[j] = scenarios[i][j]
        policyParams['policyIndex'][0] = index
        policies[i].append(policyParams)
        index += 1
        
        if policiesParams['combinationKey'][0] != 0:
            if policiesParams['combinationKey'][0] == 1: # One policy for each row of the policyParams file (missing values are set to default)
                for n in range(numberRows):
                    policyParams = policies[i][0].copy()
                    for j in names[1:]:
                        if not pd.isnull(policiesParams[j][n]):
                            policyParams[j][0] = policiesParams[j][n]
                    policyParams['policyIndex'][0] = index
                    index += 1
                    policies[i].append(policyParams)

            elif policiesParams['combinationKey'][0] == 2: # One scenario for each value in the policyParams file
                for n in range(numberRows):
                    for i in names[1:]:
                        policyParams = policies[i][0].copy()
                        if not pd.isnull(policiesParams[j][n]):
                            policyParams[j][0] = policiesParams[j][n]
                        else:
                            continue
                        policyParams['policyIndex'][0] = index
                        index += 1
                        policies[i].append(policyParams)
        
            else: # All the different combinations of values in the policyParams file
                policyList = []
                parNames = []
                for i in names[1:]:
                    if pd.isnull(policiesParams[i][0]):
                        continue
                    parNames.append(i)
                    policyList.append([x for x in policiesParams[i] if pd.isnull(x) == False])
                combinations = list(itertools.product(*policyList))
                for c in combinations:
                    policyParams = policies[i][0].copy()
                    for v in c:
                        policyParams[parNames[c.index(v)]][0] = v
                    policyParams['policyIndex'][0] = index
                    index += 1
                    policies[i].append(policyParams)
    
    
    
    # From dataframe to dictionary
    policiesParams = []
    for i in range(len(policies)):
        scenarioPoliciesParams = []
        for j in range(len(policies[i])):
            numberRows = policies[i][j].shape[0]
            keys = list(policies[i][j].columns.values)
            values = []
            for column in policies[i][j]:
                colValues = []
                for r in range(numberRows):
                    if pd.isnull(policies[i][j].loc[r, column]):
                        break
                    colValues.append(policies[i][j][column][r])
                values.append(colValues)
            p = OrderedDict(zip(keys, values))
            for key, value in p.iteritems():
                if len(value) < 2:
                    p[key] = value[0]
            scenarioPoliciesParams.append(p)
        policiesParams.append(scenarioPoliciesParams)
    
    return policiesParams

# multiprocessing functions
def multiprocessParams(scenariosParams, policiesParams, numRepeats, fSeed, folder, n):
    params = []
    for j in range(int(numRepeats)):
        randSeed = int(time.time())
        for i in range(len(scenariosParams)):
            scenPar = OrderedDict(scenariosParams[i])
            scenPar['scenarioIndex'] = i
            scenPar['repeatIndex'] = j
            scenPar['rootFolder'] = folder
            scenPar['randomSeed'] = -1
            if j == 0:
                scenPar['randomSeed'] = fSeed
            else:
                scenPar['randomSeed'] = randSeed
            if n == 0:
                z = OrderedDict(policiesParams[i][0])
                z['policyIndex'] = 0
                z['scenarioIndex'] = i
                z['repeatIndex'] = j
                z['randomSeed'] = scenPar['randomSeed']
                z['rootFolder'] = folder
                params.append([scenPar, z])
            else:
                for k in range(len(policiesParams[i][1:])):
                    z = OrderedDict(policiesParams[i][1:][k])
                    z['policyIndex'] = k+1
                    z['scenarioIndex'] = i
                    z['repeatIndex'] = j
                    z['randomSeed'] = scenPar['randomSeed']
                    z['rootFolder'] = folder
                    params.append([scenPar, z])

    return params

def multiprocessingSim(params):
    # Create Sim instance
    folderRun = params[0]['rootFolder'] + '/Rep_' + str(params[0]['repeatIndex'])
    
    s = Sim(params[0]['scenarioIndex'], params[0], folderRun)
    
    print''
    print params[1]['policyIndex']
    print''
    
    s.run(params[1]['policyIndex'], params[1], params[1]['randomSeed'])
        

if __name__ == "__main__":
    
    # Create a folder for the simulation
    timeStamp = datetime.datetime.today().strftime('%Y_%m_%d-%H_%M_%S')
    folder = os.path.join('Simulations_Folder', timeStamp)
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Create or update file for graphs
    if not os.path.isfile('./graphsParams.csv'):
        with open("graphsParams.csv", "w") as file:
            writer = csv.writer(file, delimiter = ",", lineterminator='\r')
            writer.writerow((['simFolder', 'doGraphs', 'numRepeats', 'numScenarios', 'numPolicies']))
    else:
        graphsDummy = pd.read_csv('graphsParams.csv', sep=',', header=0)
        numberRows = graphsDummy.shape[0]
        for i in range(numberRows):
            graphsDummy['doGraphs'][i] = 0
        graphsDummy.to_csv("graphsParams.csv", index=False)
        
    
    parametersFromFiles = False
    
    scenariosParams = []
    policiesParams = [[[]]]
    
    numberScenarios = -1
    numberPolicies = -1
    
    if parametersFromFiles == False:
        
        numberScenarios = 1
        numberPolicies = 1
        
        metaParams = meta_params()
        initParams = init_params()
        
        z = metaParams.copy()   # start with x's keys and values
        z.update(initParams) 
        scenariosParams.append(z)
        
    else:
        # Import initial, sensitivity and policy parameters from csv files
        # Create list of scenarios to feed into Sim
        # Create list of policies to feed into Sim.run
        
        # Load meta-parameters
        mP = pd.read_csv('metaParameters.csv', sep=',', header=0)
        numberRows = mP.shape[0]
        keys = list(mP.columns.values)
        values = []
        for column in mP:
            colValues = []
            for i in range(numberRows):
                if pd.isnull(mP.loc[i, column]):
                    break
                colValues.append(mP[column][i])
            values.append(colValues)
        metaParams = OrderedDict(zip(keys, values))
        for key, value in metaParams.iteritems():
            if len(value) < 2:
                metaParams[key] = value[0]
        
        scenarios = loadScenarios()
        
        numberScenarios = len(scenarios)
        
        # From dataframe to dictionary
        scenariosParams = []
        for scenario in scenarios:
            numberRows = scenario.shape[0]
            keys = list(scenario.columns.values)
            values = []
            for column in scenario:
                colValues = []
                for i in range(numberRows):
                    if pd.isnull(scenario.loc[i, column]):
                        break
                    colValues.append(scenario[column][i])
                values.append(colValues)
            p = OrderedDict(zip(keys, values))
            for key, value in p.iteritems():
                if len(value) < 2:
                    p[key] = value[0]
            
            z = metaParams.copy()   # start with x's keys and values
            z.update(p) 
            scenariosParams.append(z)
        
        policiesParams = loadPolicies(scenarios)
        
        numberPolicies = len(policiesParams[0])
    
    # Add graph parameters to graphsParam.csvs file
    with open("graphsParams.csv", "a") as file:
        writer = csv.writer(file, delimiter = ",", lineterminator='\r')
        writer.writerow([timeStamp, 1, int(metaParams['numRepeats']), numberScenarios, numberPolicies])
    
    numRepeats = int(metaParams['numRepeats'])
    fSeed = int(metaParams['favouriteSeed'])
    
    if metaParams['multiprocessing'] == False or parametersFromFiles == False:
    
        for r in range(numRepeats):
            # Create Run folders
            folderRun = folder + '/Rep_' + str(r)
            if not os.path.exists(folderRun):
                os.makedirs(folderRun)
            # Set seed
            seed = fSeed
            if r > 0:
                seed = int(time.time())
            for i in range(len(scenariosParams)):
                n = OrderedDict(scenariosParams[i])
                s = Sim(i, n, folderRun)
                for j in range(len(policiesParams[i])):
                    p = OrderedDict(policiesParams[i][j])
                    s.run(j, p, seed) # Add policy paramters later
                    
    else:
        processors = int(metaParams['numberProcessors'])
        if processors > multiprocessing.cpu_count():
            processors = multiprocessing.cpu_count()
            
        pool = multiprocessing.Pool(processors)
        # Create a list of dictionaries (number repetitions times number of scenarios), adding repeat index for folders' creation
        params = multiprocessParams(scenariosParams, policiesParams, metaParams['numRepeats'], fSeed, folder, 0)
        pool.map(multiprocessingSim, params)
        pool.close()
        pool.join()
        
        if numberPolicies > 1:
            # multiporcessing for the policies
            pool = multiprocessing.Pool(processors)
            # Create a list of policy parameters (numer of policies times number of scenarios times number of repeats)
            params = multiprocessParams(scenariosParams, policiesParams, metaParams['numRepeats'], fSeed, folder, 1)
            pool.map(multiprocessingSim, params)
            pool.close()
            pool.join()
        

























