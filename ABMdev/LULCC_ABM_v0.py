"""
Agent Based Model of Land Use and Land Cover Change 

@author: lejoflores & kendrakaiser
"""
#---------------------------------------
#  Load Packages
#---------------------------------------
import geopandas as gp
import numpy as np
from geofxns import minDistCity #slow
from geofxns import saveLC #do we need to import each function, or can we just load all of them?
import CropFuncs.CropDecider as cd
import InitializeAgentsDomain as init
import PostProcessing.FigureFuncs as ppf

userPath='/Users/kek25/Documents/GitRepos/'
DataPath= userPath+'IM3-BoiseState/'

#---------------------------------------
# 0. Declare Variables
#---------------------------------------
#set agent switching parameters
a_ra = 4.5
b_ra = 1.0

fmin = 1.0
fmax = 1.5
f0 = 1.2
n = 100

#---------------------------------------
# 1. Preprocessing
#---------------------------------------
#load extent
extent=gp.read_file(DataPath + 'ABMdev/Data/extent_3km_AdaCanyon.shp')
#load inital landcover
lc=np.load(DataPath + 'ABMdev/Data/gcam_3km_2010_AdaCanyon.npy')
#initalize minimum distance to city
dist2city=minDistCity(lc)

Ny, Nx = lc[0].shape
Nt = 50

#---------------------------------------
#  Initialize Crops
#---------------------------------------
Nc = 4 #there are actually 17 when the 1km is run, need random profit profiles for each of these 
CropIDs =np.array([1,2,3,10]) # need to make this automatic depending on which crops show up 
CropIDs= CropIDs.reshape((Nc,1))
#CropIDs=np.arange(Nc).reshape((Nc,1)) + 1
CropID_all = np.zeros((Nt,Ny,Nx))
CropID_all[0,:,:] = lc

#---------------------------------------
#  Initialize Profits
#---------------------------------------
Profit_ant = np.zeros((Nt,Ny,Nx))
Profit_act = np.zeros((Nt,Ny,Nx))

Profit_ant[0,:,:] = 30000.0 + np.random.normal(loc=0.0,scale=1000.0,size=(1,Ny,Nx))
Profit_act[0,:,:] = Profit_ant[0,:,:]

Profits = [] # A list of numpy arrays that will be Nt x Nc 
Profits = cd.GeneratePrices(Nt)
Profits = Profits[:, 0:Nc]

#---------------------------------------
#  Initialize Agents
#---------------------------------------
#Update so each of these inital values are randomly selected from NASS distributions
AgentData = {
        "AgeInit" : int(45.0),
        "nFields" : 1,
        "AreaFields" : np.array([10]),
        "LandStatus" : 0,
        "density" : 2,
        }

dFASM = init.InitializeDomain(Ny, Nx)
AgentArray = init.PlaceAgents(Ny, Nx, lc, dist2city)
dFASM = init.InitializeAgents(AgentArray, AgentData, dFASM, dist2city, Ny, Nx)

#---------------------------------------
# 2. loop through decision process 
#---------------------------------------

for i in np.arange(1,Nt):
    
    for j in np.arange(Ny):
        for k in np.arange(Nx):
            #Assess Profit
            Profit_ant_temp, Profit_p = cd.AssessProfit(CropID_all, Profits, i, j, k, Nc, CropIDs)
            #Decide on Crop
            CropChoice, ProfitChoice = cd.DecideN(a_ra, b_ra, fmin, fmax, n, Profit_ant_temp, CropIDs, \
                                                      Profit_p, rule=True)
            CropID_all, Profit_ant, Profit_act = cd.MakeChoice(CropID_all, Profit_ant_temp, Profit_ant, \
                                                               CropChoice, ProfitChoice, Profit_act, i,j,k)
 

ppf.CreateAnimation(CropID_all, Nt)
#is there a way to not have to define i,j,k in the function input variables?
#CropID_all, Profit_ant, Profit_act = cd.MakeDecision(Nt, Ny, Nx, Nc, CropID_all, Profits, Profit_ant, Profit_act, a_ra, b_ra, fmin, fmax, n, CropIDs)
"one unit test would be to confirm that non-ag stayed the same and that all of the ag did not stay the same"        
#need to pull out the parts that dont rely on the loop and put the decision inside of it, that way relevant info can be updated between timesteps; 

#---------------------------------------
# 3. update variables 
#---------------------------------------

#update distance to city from output of decision process - IF we were incorperating the urban agent then this would happen in each time step
#dist2city=minDistCity(lc_new)
     
  #Update AgentArray 
#where in the model does the code denote that the agent goes from farmer to urban or visa versa
     #dFASM[i][j].SwapAgent('aFarmer','aUrban',fromIndex,AgentArray)
     
for i in np.arange(Ny):
 	for j in np.arange(Nx):
         if(AgentArray[i][j]=='aFarmer'):            
             dFASM[i][j].FarmAgents[0].UpdateAge()
             dFASM[i][j].FarmAgents[0].UpdateDist2city(dist2city[i][j])
      
#---------------------------------------
# 4. Save Output
#---------------------------------------
      
#write landcover to array - sub w Jons work
#saveLC(temp_lc, 2010, it, DataPath)
           

