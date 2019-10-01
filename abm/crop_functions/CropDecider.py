"""
Created on Tue Jul  9 12:12:43 2019

@author: lejoflores
"""

import numpy as np
import scipy.special as sp


def DefineSeed(seed):
    global seed_val
    seed_val=seed
    return


def SwitchingProbCurve(alpha,beta,fmin,fmax,n,profit):
    
    x  = np.linspace(0,1.0,num=n)
    
    fx = sp.betainc(alpha,beta,x)
    
    x2 = np.linspace(fmin*profit,fmax*profit,num=n)
    
    return x2, fx


def Decide(alpha, beta, fmin, fmax, n, profit, profit_p):
    """Choose from among two different alternatives

    :param alpha:
    :param beta:
    :param fmin:
    :param fmax:
    :param n:
    :param profit:
    :param profit_p:

    :return:

    """

    if profit_p > profit:
        
        x, fx = SwitchingProbCurve(alpha, beta, fmin, fmax, n, profit)
        
        prob_switch = np.interp(profit_p, x, fx)
        
        if np.random.rand(1) < prob_switch: #need to send it seed in the unit test
            return 1 # Switch
        else:
            return 0 # Do not switch
        
    else:
        return 0 # Do not switch if not profitable


def DecideN(alpha, beta, fmin, fmax, n, profit, vec_crops, vec_profit_p, rule=True):
    """Choose from among N different crops, all with associated anticipated profit values.

    :param alpha:
    :param beta:
    :param fmin:
    :param fmax:
    :param n:
    :param profit:
    :param vec_crops:
    :param vec_profit_p:
    :param rule:

    :return:

    """

    # Key assumptions: the vector of crop IDs and anticipated profits associated
    # with each crop must both be N x 1 column vectors. Error trap this below:
    assert (vec_crops.shape == vec_profit_p.shape), 'Supplied vector of crop IDs and potential profits must be identical'
    assert (vec_crops.shape[1] == 1), 'Supplied vector of crop IDs and potential profits must be N x 1'
    
    # Create a boolean vector to store a 0 or 1 if the farmer will select the
    # crop (==1) or not (==1)
    AccRej = np.zeros(vec_crops.shape, dtype='int')
    
    for i in np.arange(AccRej.size):

        # Use the `Decide` function above to choose whether or not the crop is viable
        AccRej[i] = Decide(alpha, beta, fmin, fmax, n, profit, vec_profit_p[i]) # is fmin/fmax setting bounds on range of additional profit?

    # Find the Crop IDs and associated profits that were returned as "viable" 
    # based on the "Decide" function (that is, Decide came back as "yes" == 1)
    ViableCrops = vec_crops[AccRej == 1]
    ViableProfits = vec_profit_p[AccRej == 1]

    if ViableCrops.size==0:
        return -1, -1
    
    # Find the maximum anticipated profit and the crop IDs associated with that 
    # maximum
    MaxProfit = ViableProfits.max()
    MaxProfitCrop = ViableCrops[ViableProfits == MaxProfit]
    
    # This next part should be rare. There happen to be more than one viable  
    # crops that carry the same anticipated profit that also coincides with 
    # the maximum anticipated profit. The choice here is to choose randomly
    # from among those crops that have the same (maximum) profit
    if MaxProfitCrop.size > 1:
        ViableCrops = MaxProfitCrop
        ViableProfits = ViableProfits[ViableProfits == MaxProfit]
        rule = False # Switch rule to trick the algorithm into using the random option
    
    
    # TODO: Right now, only rules choose crops based on profitability and/or
    # randomness. In future, add rules to choose based on network behavior, etc.
    if rule: # Return crop with largest profit

        CropChoice = MaxProfitCrop
        ProfitChoice = MaxProfit
        
    else: # Choose randomly from among all viable crops

        indChoice = np.random.choice(np.arange(ViableCrops.size), size=1)
        CropChoice = ViableCrops[indChoice]
        ProfitChoice = ViableProfits[indChoice]
        
    # Return the crop choice and associated profit
    return CropChoice, ProfitChoice


def GeneratePrices(Nt):
    """Generates 6 synthetic crop profits with different behaviors. This function
    is largely for debugging purposes to test new model test cases, etc.

    :param Nt:

    :return:

    """
    # Crop 1 = Steadily increasing
    P1_i = 20000.0
    P1_f = 31000.0
    P1_s = 1000.0

    P1 = (np.linspace(P1_i, P1_f, num=Nt).reshape((Nt, 1)) + np.random.normal(loc=0.0, scale=P1_s, size=(Nt, 1)))
    
    # Crop 2
    P2_i = 30000.0
    P2_f = 15000.0
    P2_s = 1000.0
    
    P2 = (np.linspace(P2_i, P2_f, num=Nt).reshape((Nt, 1)) + np.random.normal(loc=0.0, scale=P2_s, size=(Nt, 1)))
    
    # Crop 3 = Sinusoidal fluctuation
    P3_l = 28000.0
    P3_a = 5000.0
    P3_n = 2.0
    P3_s = 1000.0
    
    x3 = np.linspace(0.0, P3_n * 2 * np.pi, num=Nt).reshape((Nt, 1))
    P3 = (P3_l + P3_a * np.sin(x3) + np.random.normal(loc=0.0, scale=P3_s, size=(Nt, 1)))
    
    # Crop 4 = Step decrease
    P4_i = 31000.0
    P4_f = 14000.0
    P4_s = 1000.0
    
    P4 = np.zeros((Nt, 1))
    P4[0:(int(P4.size / 2))] = P4_i
    P4[(int(P4.size / 2)):] = P4_f
    P4 += np.random.normal(loc=0.0, scale=P4_s, size=(Nt, 1))
    
    # Crop 5 = Step increase
    P5_i = 10000.0
    P5_f = 30000.0
    P5_s = 1000.0

    P5 = np.zeros((Nt, 1))
    P5[0:(int(P5.size / 2))] = P5_i
    P5[(int(P5.size / 2)):] = P5_f
    P5 += np.random.normal(loc=0.0, scale=P5_s, size=(Nt, 1))
    
    # Crop 6 = Constant with noise
    P6_l = 27000.0
    P6_s = 1000.0

    P6 = (P6_l * np.ones((Nt, 1)) + np.random.normal(loc=0.0, scale=P6_s, size=(Nt, 1)))

    P_matrix = np.column_stack((P1, P2, P3, P4, P5, P6))
    
    return P_matrix


def AssessProfit(Crop, Profits_cur, Profits_alt,  Nc, CropIDs):
    """AssessProfit and Make Choice: seperates the differenct components into functions

    :param Crop:
    :param Profits_cur:
    :param Profits_alt:
    :param Nc:
    :param CropIDs:

    :return:

    """
    # Existing Crop ID
    CurCropChoice_ind = Crop.astype('int') # - 1
    CropIx=np.where(CropIDs == CurCropChoice_ind)

    # assess current and future profit of that given crop
    if np.isin(CurCropChoice_ind, CropIDs): # change this to be a vector of possible cropIDs
        Profit_last = Profits_cur[CropIx[0][0]] # last years profit
        Profit_p = Profits_alt[:] # this years expected profit
        Profit_p = Profit_p.reshape(Nc, 1)

    else:
        Profit_last = 0
        Profit_p = np.zeros((Nc, 1))
        
    return Profit_last, Profit_p


def MakeChoice(CropID_last, Profit_last, Profit_ant, CropChoice, ProfitChoice, seed=False):
    """Need description.

    :param CropID_last:
    :param Profit_last:
    :param Profit_ant:
    :param CropChoice:
    :param ProfitChoice:
    :param seed:

    :return:

    """
    
    if seed:
        
        try:
            seed_val
        except NameError:
            print("Random seed needs to be initialized using the CropDecider.DefineSeed() Function")
        
        np.random.seed(seed_val)
    
    # Check if return  values indicate the farmer shouldn't switch
    if (CropChoice==-1) and (ProfitChoice==-1):
        CropID_next = CropID_last
        Profit_ant = Profit_last
        Profit_act = Profit_ant + np.random.normal(loc=0.0, scale=1000.0, size=(1, 1, 1)) #this years actual profit

    else: #switch to the new crop
        CropID_next = CropChoice
        Profit_ant = ProfitChoice
        Profit_act= Profit_ant + np.random.normal(loc=0.0, scale=1000.0, size=(1, 1, 1))

    return CropID_next, Profit_ant, Profit_act
