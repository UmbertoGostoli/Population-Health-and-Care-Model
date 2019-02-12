# -*- coding: utf-8 -*-
"""
Created on Wed Feb 06 15:45:43 2019

@author: ug4d
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_pdf import PdfPages
import os
from collections import OrderedDict
import pandas as pd


def doGraphs(graphsParams, metaParams):
    
    folder = graphsParams[0]
    numRepeats = graphsParams[2]
    numScenarios = graphsParams[3]
    numPolicies = graphsParams[4]
    
    simFolder = 'Simulations_Folder/' + folder
    
    multipleRepeatsDF = []
    for repeatID in range(numRepeats):
        repFolder = simFolder + '/Rep_' + str(repeatID)
        multipleScenariosDF = []
        for scenarioID in range(numScenarios):
            scenarioFolder = repFolder + '/Scenario_' + str(scenarioID)
            multiplePoliciesDF = []
            for policyID in range(numPolicies):
                policyFolder = scenarioFolder + '/Policy_' + str(policyID)
                outputsDF = pd.read_csv(policyFolder + '/Outputs.csv', sep=',', header=0)
                singlePolicyGraphs(outputsDF, policyFolder, metaParams)
                multiplePoliciesDF.append(outputsDF)
            if numPolicies > 1:
                multiplePoliciesGraphs(multiplePoliciesDF, scenarioFolder, metaParams, numPolicies)
            multipleScenariosDF.append(multiplePoliciesDF)
        if numScenarios > 1:
            multipleScenariosGraphs(multipleScenariosDF, repFolder, metaParams, numPolicies, numScenarios)
        multipleRepeatsDF.append(multipleScenariosDF)
    if numRepeats > 1:
        multipleRepeatsGraphs(multipleRepeatsDF, simFolder, metaParams, numPolicies, numScenarios, numRepeats)
    
    
def singlePolicyGraphs(output, policyFolder, p):
    
    folder = policyFolder + '/Graphs'
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    p1, = ax.plot(output['year'], output['currentPop'], color="red", label = 'Total population')
    p2, = ax.plot(output['year'], output['taxPayers'], color="blue", label = 'Taxpayers')
    ax.set_ylabel('Number of people')
    handels, labels = ax.get_legend_handles_labels()
    ax.legend(loc = 'lower right')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'popGrowth.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()
    
    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    p1, = ax.plot(output['year'], output['averageHouseholdSize'], color="red")
    ax.set_ylabel('Average Household Size')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'avgHouseholdSize.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()
    
    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    p1, = ax.plot(output['year'], output['totalCareDemandHours'], color="red", label = 'Aggregate Care Demand')
    p2, = ax.plot(output['year'], output['totalCareSupply'], color="blue", label = 'Aggregate Care Supply')
    ax.set_ylabel('Number of hours/week')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'careDemandAndSupply.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()
    
    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    p1, = ax.plot(output['year'], output['marriagePropNow'], color="red")
    ax.set_ylabel('Married adult women (share)')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'shareMarriedWomen.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()
    
    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    p1, = ax.plot(output['year'], output['shareSingleParents'], color="red")
    ax.set_ylabel('Single Parents (share)')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'shareSingleParents.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()
    
    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    p1, = ax.plot(output['year'], output['shareFemaleSingleParent'], color="red")
    ax.set_ylabel('Female Single Parents (share)')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'shareFemaleSingleParents.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()
    
    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    p1, = ax.plot(output['year'], output['shareUnmetCareNeeds'], color="red")
    ax.set_ylabel('Unmet Care Needs (share)')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'shareUnmetCareNeeds.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()
    
    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    p1, = ax.plot(output['year'], output['totalHospitalizationCost'], color="red")
    ax.set_ylabel('Hospitalization Cost')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'hospitalizationCost.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()
    
    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    p1, = ax.plot(output['year'], output['publicCare'], color="red")
    ax.set_ylabel('Public Care (hours per week)')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'publicCare.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()
    
    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    p1, = ax.plot(output['year'], output['employmentRate'], color="red")
    ax.set_ylabel('Employment Rate')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'employmentRate.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()

    
def multiplePoliciesGraphs(output, scenarioFolder, p, numPolicies):
    
    folder = scenarioFolder + '/Graphs'
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Add graphs across policies (within the same run/scenario)
    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    graph = []
    for i in range(numPolicies):
        graph.append(ax.plot(output[i]['year'], output[i]['currentPop'], label = 'Policy ' + str(i)))
    ax.set_title('Populations')
    ax.set_ylabel('Number of people')
    handels, labels = ax.get_legend_handles_labels()
    ax.legend(loc = 'lower right')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'popGrowth_axPol.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()

    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    graph = []
    for i in range(numPolicies):
        graph.append(ax.plot(output[i]['year'], output[i]['shareUnmetCareNeeds'], label = 'Policy ' + str(i)))
    ax.set_title('Share of Unmet Care Needs')
    ax.set_ylabel('Unmet Care Needs (share)')
    handels, labels = ax.get_legend_handles_labels()
    ax.legend(loc = 'lower right')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'shareUnmetCareNeeds_axPol.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()

    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    graph = []
    for i in range(numPolicies):
        graph.append(ax.plot(output[i]['year'], output[i]['totalHospitalizationCost'], label = 'Policy ' + str(i)))
    ax.set_title('Hospitalization Cost')
    ax.set_ylabel('Punds per year')
    handels, labels = ax.get_legend_handles_labels()
    ax.legend(loc = 'lower right')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'hospitalizationCost_axPol.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()

    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    graph = []
    for i in range(numPolicies):
        graph.append(ax.plot(output[i]['year'], output[i]['publicCare'], label = 'Policy ' + str(i)))
    ax.set_title('Amount of Public Care')
    ax.set_ylabel('Hours per week')
    handels, labels = ax.get_legend_handles_labels()
    ax.legend(loc = 'lower right')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'publicCare_axPol.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()
    
    fig, ax = plt.subplots() # Argument: figsize=(5, 3)
    graph = []
    for i in range(numPolicies):
        graph.append(ax.plot(output[i]['year'], output[i]['employmentRate'], label = 'Policy ' + str(i)))
    ax.set_title('Employment Rate')
    ax.set_ylabel('Employment Rate')
    handels, labels = ax.get_legend_handles_labels()
    ax.legend(loc = 'lower right')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
    ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
    fig.tight_layout()
    path = os.path.join(folder, 'employmentRate_axPol.pdf')
    pp = PdfPages(path)
    pp.savefig(fig)
    pp.close()
   
   
def multipleScenariosGraphs(output, repFolder, p, numPolicies, numScenarios):
    
    folder = repFolder + '/Graphs'
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    # Add graphs across scenarios (for the same policies)
    for j in range(numPolicies):
        fig, ax = plt.subplots() # Argument: figsize=(5, 3)
        graph = []
        for i in range(numScenarios):
            graph.append(ax.plot(output[i][j]['year'], output[i][j]['currentPop'], label = 'Scenario ' + str(i+1)))
        # p2, = ax.plot(output[1][0]['year'], output[1]['currentPop'], color="blue", label = 'Policy 1')
        ax.set_title('Populations - Policy ' + str(j))
        ax.set_ylabel('Number of people')
        handels, labels = ax.get_legend_handles_labels()
        ax.legend(loc = 'lower right')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
        ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
        fig.tight_layout()
        path = os.path.join(folder, 'popGrowth_axScen_P' + str(j) + '.pdf')
        pp = PdfPages(path)
        pp.savefig(fig)
        pp.close()
        
    
    for j in range(numPolicies):
        fig, ax = plt.subplots() # Argument: figsize=(5, 3)
        graph = []
        for i in range(numScenarios):
            graph.append(ax.plot(output[i][j]['year'], output[i][j]['shareUnmetCareNeeds'], label = 'Scenario ' + str(i+1)))
        # p2, = ax.plot(output[1][0]['year'], output[1]['currentPop'], color="blue", label = 'Policy 1')
        ax.set_title('Unmet Care Needs - Policy ' + str(j))
        ax.set_ylabel('Unmet Care Needs (share)')
        handels, labels = ax.get_legend_handles_labels()
        ax.legend(loc = 'lower right')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
        ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
        fig.tight_layout()
        path = os.path.join(folder, 'shareUnmetCareNeeds_axScen_P' + str(j) + '.pdf')
        pp = PdfPages(path)
        pp.savefig(fig)
        pp.close()
    
    for j in range(numPolicies):
        fig, ax = plt.subplots() # Argument: figsize=(5, 3)
        graph = []
        for i in range(numScenarios):
            graph.append(ax.plot(output[i][j]['year'], output[i][j]['totalHospitalizationCost'], label = 'Scenario ' + str(i+1)))
        # p2, = ax.plot(output[1][0]['year'], output[1]['currentPop'], color="blue", label = 'Policy 1')
        ax.set_title('Hospitalization Cost - Policy ' + str(j))
        ax.set_ylabel('Punds per year')
        handels, labels = ax.get_legend_handles_labels()
        ax.legend(loc = 'lower right')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
        ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
        fig.tight_layout()
        path = os.path.join(folder, 'hospitalizationCost_axScen_P' + str(j) + '.pdf')
        pp = PdfPages(path)
        pp.savefig(fig)
        pp.close()
    
    for j in range(numPolicies):
        fig, ax = plt.subplots() # Argument: figsize=(5, 3)
        graph = []
        for i in range(numScenarios):
            graph.append(ax.plot(output[i][j]['year'], output[i][j]['publicCare'], label = 'Scenario ' + str(i+1)))
        # p2, = ax.plot(output[1][0]['year'], output[1]['currentPop'], color="blue", label = 'Policy 1')
        ax.set_title('Amount of Public Care - Policy ' + str(j))
        ax.set_ylabel('Hours per week')
        handels, labels = ax.get_legend_handles_labels()
        ax.legend(loc = 'lower right')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
        ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
        fig.tight_layout()
        path = os.path.join(folder, 'publicCare_axScen_P' + str(j) + '.pdf')
        pp = PdfPages(path)
        pp.savefig(fig)
        pp.close()
    
    for j in range(numPolicies):
        fig, ax = plt.subplots() # Argument: figsize=(5, 3)
        graph = []
        for i in range(numScenarios):
            graph.append(ax.plot(output[i][j]['year'], output[i][j]['employmentRate'], label = 'Scenario ' + str(i+1)))
        # p2, = ax.plot(output[1][0]['year'], output[1]['currentPop'], color="blue", label = 'Policy 1')
        ax.set_title('Employment Rate - Policy ' + str(j))
        ax.set_ylabel('Employment Rate')
        handels, labels = ax.get_legend_handles_labels()
        ax.legend(loc = 'lower right')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
        ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
        fig.tight_layout()
        path = os.path.join(folder, 'employmentRate_axScen_P' + str(j) + '.pdf')
        pp = PdfPages(path)
        pp.savefig(fig)
        pp.close()
    

def multipleRepeatsGraphs(output, simFolder, p, numRepeats, numPolicies, numScenarios):
    
    folder = simFolder + '/Graphs'
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Add graphs across runs (for the same scenario/policy combinations)
    
    for j in range(numPolicies):
        for i in range(numScenarios):
            fig, ax = plt.subplots() # Argument: figsize=(5, 3)
            graph = []
            for z in range(numRepeats):
                graph.append(ax.plot(output[z][i][j]['year'], output[z][i][j]['currentPop'], label = 'Run ' + str(z+1)))
            ax.set_title('Populations - ' + 'Scenario ' + str(i+1) + '/Policy ' + str(j))
            ax.set_ylabel('Number of people')
            handels, labels = ax.get_legend_handles_labels()
            ax.legend(loc = 'lower right')
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
            ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
            fig.tight_layout()
            path = os.path.join(folder, 'popGrowth_axRep_S' + str(i+1) + '_P' + str(j) + '.pdf')
            pp = PdfPages(path)
            pp.savefig(fig)
            pp.close()
            
    for j in range(numPolicies):
        for i in range(numScenarios):
            fig, ax = plt.subplots() # Argument: figsize=(5, 3)
            graph = []
            for z in range(numRepeats):
                graph.append(ax.plot(output[z][i][j]['year'], output[z][i][j]['shareUnmetCareNeeds'], label = 'Run ' + str(z+1)))
            ax.set_title('Unmet Care Needs - ' + 'Scenario ' + str(i+1) + '/Policy ' + str(j))
            ax.set_ylabel('Unmet Care Needs (share)')
            handels, labels = ax.get_legend_handles_labels()
            ax.legend(loc = 'lower right')
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.set_xlim(left = int(p['statsCollectFrom']), right = int(p['endYear']))
            ax.set_xticks(range(int(p['statsCollectFrom']), int(p['endYear'])+1, 20))
            fig.tight_layout()
            path = os.path.join(folder, 'shareUnmetCareNeeds_axRep_S' + str(i+1) + '_P' + str(j) + '.pdf')
            pp = PdfPages(path)
            pp.savefig(fig)
            pp.close()

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
        
graphsParams = pd.read_csv('graphsParams.csv', sep=',', header=0)
dummy = list(graphsParams['doGraphs'])
for i in range(len(dummy)):
    if dummy[i] == 1:
        doGraphs(graphsParams.loc[i], metaParams)

        

