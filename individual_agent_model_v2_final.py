# -*- coding: utf-8 -*-
"""Group Project 1 Individual Agent Model_v2_FINAL.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bmiuN7_PyuBedEoeCAl08XuhDDfMdNWp

### For questions regarding the code, contact David Wei @ davidwei@g.harvard.edu ###
"""

import numpy as np
import matplotlib.pyplot as plt
import random
from collections import defaultdict
import pandas as pd

import matplotlib as mpl

# Edit the font, font size, and axes width
mpl.rcParams['font.family'] = 'Avenir'
plt.rcParams['font.size'] = 15
plt.rcParams['axes.linewidth'] = 2

"""### Helpful Resources

Available data indicate that persons with mild to moderate COVID-19 remain infectious no longer than 10 days after symptom onset. Persons with more severe to critical illness or severe immunocompromise likely remain infectious no longer than 20 days after symptom onset

https://www.cdc.gov/coronavirus/2019-ncov/hcp/duration-isolation.html#:~:text=Available%20data%20indicate%20that%20persons,days%20after%20symptom%20onset

- inspired the `min_infect` and `max_infect` variables

### Global Variables Summary

- 's': susceptible population, capable of contracting infection if in contact with an exposed, infected, or undetected individual

- 'e': exposed population; these are people who have contracted the virus and are contagious, but are not yet symptomatic (incubation period)

- 'i': infected population; these are the symptomatic individuals (can either recover or die)

- 'u': undetected population; these are the people who are asymptomatic but can spread the virus (can only recover)

- 'r': recovered population; these are people who have recovered from an infection

- 'f': population who have died; this is the fatality count

Potential outcomes for individuals:

s

s -> e -> i -> r

s -> e -> i -> f

s -> e -> u -> r

### Notes

`nc1_lam` and `nc2_lam` may be affected by social distancing policies. We expect `nc2_lam` < `nc1_lam` since unwell individuals are less likely to move around and come in contact with other individuals.

`incubate_time` is just a constant, but we can vary this (uniform distribution perhaps). It was set to the shorter end of the expected incubation period of covid because this individual could turn out to be undetected, at which they would be contagious for a total of 2+5=7 to 2+10=15 days.

`min_infect` and `max_infect` are the minimum and maximum number of days an infected or undetected (`i` or `u`) individual is contagious, excluding the incubation period, at which their status is `e`

`p_e`, `p_i`, `p_u`, and `p_f` are the probabilities of becoming exposed after contact (`s` -> `e`), symptomatic (`e` -> `i`), asymptomatic (`e` -> `u`), and dying (`i` -> `f`), respectively. We assume that only symptomatic individuals may die.

### To Do

- Changing fatality rate (`p_f`) depending on age of the individual

- Different probability of being infected based on age of the individual

- `nc1_lam` and `nc2_lam` probably vary across age groups as well

- Maybe `p_e` would change too, depending on age?


Perhaps we can create an array that contains the age information of each individual agent in `pop` (indices of the `pop` array correspond directly to the indices in this new array). We can then pass this array on to the census1D array, much like what was done with the dictionaries `t_e`, `t_i`, and `t_u`.

Maybe we can also have function simulate1D return this array of age information so that we can plot the SEIURF for each age groups.
"""

# GLOBAL VARIABLES
n = 10000 # population

nc1_lam = 1.665 # rate of contacts per day of exposed and undetected people (modelled by Poisson)
nc2_lam = 1 # rate of contacts per day of symptomatic infected people (modelled by Poisson)

incubate_time = 2 # days that incubation lasts (before an 'e' individual becomes 'i', symptomatic, or 'u', asymptomatic)

# generate uniform distribution (nearest integer)
min_infect = 5 # minimum number of days infected or undetected person (i.e. symptomatic or asymptomatic) is contagious
max_infect = 15 # maximum number of days infected or undetected person (i.e. symptomatic or asymptomatic) is contagious

# probabilities
p_e = 0.201    # prob of being exposed after contact 
p_i = 0.484   # prob of becoming symptomatic / infected
p_u = 1 - p_i # prob of becoming asymptomatic (undetected)
p_f = 2.6605/100    # prob of a fatality (assuming only symptomatic individuals may die)

p_e=0
tt, results = simulate1D()

plt.figure()

labels = ['S', 'E', 'I', 'U', 'R', 'F']

for y_arr, label in zip(np.transpose(results), labels):
    plt.plot(tt, y_arr, label=label)
    
plt.title('Evolution of Populations over Time (IAM)')
plt.xlabel('Time (days)')
plt.ylabel('Population')
plt.legend()

# plot_realizations(10)

p_e = 0.201
plot_average_over_realizations(100);

nc1_lam = 1.665
plot_average_over_realizations(100, parameter = '')

nc1_lam = 7

plot_average_over_realizations(100, parameter = '')

def plot_average_over_realizations(n_realizations, parameter = 'p_e'):
    '''
    Input: number of realizations to average over
    '''
     # Create dictionaries to store the times and results of each realization
    tts = {}
    results = {}

    # Simulate n_realizations given the p, nc, pt values passed to the function
    for i in range(n_realizations):
        tts[i], results[i] = simulate1D()
        
    timesteps_per_realization = []
    for n in range(n_realizations):
        timesteps_per_realization.append(len(list(results.values())[n]))
    
    max_num_timesteps = max(timesteps_per_realization)
    max_idx = np.argmax(timesteps_per_realization)
        
    for n in range(n_realizations):
        if len(results[n]) < max_num_timesteps:
            new_val = results[n] + [results[n][-1]]*(max_num_timesteps - len(results[n]))
            results[n] = new_val
    
    avg_over_realizations = np.average(np.array(list(results.values())), axis = 0)

    plt.figure()
    plt.plot(tts[max_idx], avg_over_realizations)
    
    ########## CHANGE THE TITLE HERE ##########
#     plt.title(f'Baseline: $\lambda_1$={nc1_lam}, p_e = {p_e}, p_i = {p_i}, p_f = 2.66%')

    plt.title(f'Social Distancing: $\lambda_1$={nc1_lam}')
#     plt.title('Evolution of Populations over Time: Uniform Parameters')
    if parameter == 'p_e':
        plt.title(f'Varying $p_e$: $p_e = {p_e:.3f}$')
    if parameter == 'p_i':
        plt.title(f'Varying $p_i$: $p_i = {p_i:.3f}$')
    if parameter == 'p_f':
        plt.title(f'Varying $p_f$: $p_f = {p_f*100:.1f}\%$')
    
        
    if parameter == 'lambda':
        plt.title(f'Varying $\lambda_1$: $\lambda_1 = {nc1_lam}%$')
#    plt.title(f'Social Distancing: $\lambda_1$=1.545')
#    plt.title(f'Evolution of Populations over Time: \n Averaged Over {n_realizations} realizations')
    plt.xlabel('Time (days)')
    plt.ylabel('Population')
    plt.legend(['S', 'E', 'I', 'U', 'R', 'F' ], bbox_to_anchor=(1.05, 1), loc='upper left')
#     plt.xlim([0,120])
    plt.show()
    
    max_time = []
    max_pop = []
    
    min_time = []
    min_pop = []

    # Separate results array to SEIURF arrays
    S, E, I, U, R, F = np.transpose(avg_over_realizations)
    max_pop.append(max(S))
    max_pop.append(max(E))
    max_pop.append(max(I))
    max_pop.append(max(U))
    max_pop.append(max(R))
    max_pop.append(max(F))

    max_time.append(np.argmax(S))
    max_time.append(np.argmax(E))
    max_time.append(np.argmax(I))
    max_time.append(np.argmax(U))
    max_time.append(np.argmax(R))
    max_time.append(np.argmax(F))

    min_pop.append(min(S))
    min_pop.append(min(E))
    min_pop.append(min(I))
    min_pop.append(min(U))
    min_pop.append(min(R))
    min_pop.append(min(F))

    min_time.append(np.argmin(S))
    min_time.append(np.argmin(E))
    min_time.append(np.argmin(I))
    min_time.append(np.argmin(U))
    min_time.append(np.argmin(R))
    min_time.append(np.argmin(F))
    
    
    df = pd.DataFrame({'max_time':max_time,'min_time':min_time,
                         'max_pop': max_pop,'min_pop':min_pop}, index=['S', 'E', 'I', 'U', 'R', 'F' ])

    
    return df.round(2)

# plt.plot(tt[:-1], dydx)

"""# Functions"""

def simulate1D():
    """
    this function packages the simulation steps of intializing the population
    vector and iterating the epidemic and census functions unit I=0
    the censuses are accumulated in a matrix, results
    """
    t=0 # counts number of days, starting from the 0th day
    pop=initial1D(n,0,0,0,0,0) # initial susceptible, exposed, infected, recovered, and undetected
    
    # dictionaries to keep track how many days are left before an individual's 'e', 'i', or 'u' state will change
    t_e = {} # days left of the exposed/incubation period
    t_i = {} # days left for the infected period
    t_u = {} # days left for the undetected period
    
    pop[int(n/2)-1]='i' # 1 infection to start with
    t_i[int(n/2)-1]=int(np.random.uniform(min_infect,max_infect)) # add number of days left the individual has of being infected

    s,e,i,u,r,f=census1D(pop) # get the number of individuals in each state
    results=[[s,e,i,u,r,f]] # add starting populations into an array
    tt=[t] # keep track of the timesteps
    
    # as long as there is an exposed, infected, or undetected individual, the infection will continue to spread
    while e>0 or i>0 or u>0:
        # pass population as well as dictionaries (days each e, i, u individual have left in their current state)
        pop, t_e, t_i, t_u=epidemic1D(pop, t_e, t_i, t_u) 
        
        s,e,i,u,r,f=census1D(pop) # get the number of individuals in each state
        results.append([s,e,i,u,r,f]) # add current population into an array
        
        # update time
        t=t+1
        tt.append(t)
        
    # return time and results
    return tt,results

def initial1D(s0,e0,i0,u0,r0,f0):
    '''
    sets an initial population vector for the epidemic simulation
    each state subpopulation is appended to the growing vector, pop
    NOTE: if position in the array is important,eg. if you are modeling
    local neighborhood contacts, each individual must be placed 
    randomly in the array
    '''
    
    pop=[] # array of individual agent states
    
    # add the states of the individual agents into the array
    for i in range(s0):
        pop.append('s')
    for i in range(e0):
        pop.append('e')
    for i in range(i0):
        pop.append('i')
    for i in range(u0):
        pop.append('u')
    for i in range(r0):
        pop.append('r')
    for i in range(f0):
        pop.append('f')
        
    # randomizes individuals in array
    return pop

def census1D(pop):
    # counts the number of s, e, i, r, u, and f cells in pop
    s=0 # susceptible
    e=0 # exposed
    i=0 # infected
    u=0 # undetected
    r=0 # recovered
    f=0 # fatalities
    n=np.array(pop).shape[0]

    for j in range(n):
        if pop[j]=='s':
            s+=1
        elif pop[j]=='e':
            e+=1
        elif pop[j]=='i':
            i+=1
        elif pop[j]=='u':
            u+=1
        elif pop[j]=='r':
            r+=1
        elif pop[j]=='f':
            f+=1
    return s,e,i,u,r,f

def epidemic1D(pop1, t_e, t_i, t_u):
    '''
    this stochastic epidemic simulation calculates a new pop2
    vector of 's', 'e', i', 'u', 'r', and 'f' from the current pop1
    
    The number of contacts of the contagious ('e', 'i', 'u') is generated by a poisson distribution. We assume
    that 'e' and 'u' individuals have the same rate of contacts nc1_lam. However, 'i' individuals have a lower
    rate of contacts nc2_lam.
    
    `t_e`, `t_i`, and `t_u` dictionaries explained:
    The moment an individual becomes exposed, we add them to dictionary 't_e' with the number of days left that
    they will remain in that state. After this number becomes 0, we remove them from 't_e' and see whether they
    become 'i' or 'u', that is symptomatic or asymptomatic, respectively. For 'i' and 'u', we generate the number
    of days in their respective states from a uniform distribution ranging from `min_infect` to `max_infect`. At
    the end of the countdown for a symptomatic individual, 'i', they will either recover (with probability p_i)
    or die (probability p_f = 1-p_i). At the end of the countdown for an asymptomatic individual, 'u', they
    will recover.
    '''
    # initial times in state left
    t_e2 = t_e.copy()
    t_i2 = t_i.copy()
    t_u2 = t_u.copy()
    
    pop2=pop1.copy() # population after contacts
    n=np.array(pop1).shape[0]
    
    
    # iterate through each individual
    for j in range(n):
        # if person is exposed or undetected (assumption: they do NOT change behavior, so number of contacts is same)
        if pop1[j]=='e' or pop1[j]=='u':
            # number of contacts
            nc1 = np.random.poisson(nc1_lam)
            
            # generate contacts and with probability p_e, an 's' individual will become 'e'
            for c in range(nc1):
                k=j
                while k==j and pop1[k]!='f': # make sure we only count contacts with a different and alive individual
                    k=np.random.randint(n)
                
                # see if susceptible person is exposed
                if pop1[k]=='s' and np.random.rand()<p_e:
                    pop2[k]='e'
                    t_e2[k] = incubate_time
        
        # if person is infected (assumption: they change behavior, so number of contacts is fewer)
        if pop1[j]=='i':
            # number of contacts
            nc2 = np.random.poisson(nc2_lam)
            
            # generate contacts and with probability p_e, an 's' individual will become 'e'
            for c in range(nc2):
                k=j
                while k==j and pop1[k]!='f': # make sure we only count contacts with a different and alive individual
                    k=np.random.randint(n)
                
                # see if susceptible person is exposed
                if pop1[k]=='s' and np.random.rand()<p_e:
                    pop2[k]='e'
                    t_e2[k] = incubate_time
        
    # update time left in 'e', 'i', and 'u' states
    
    for key in t_e:
        time = t_e2.pop(key) - 1
        if time > 0:
            t_e2[key] = time
        else:
            if np.random.rand() < p_i: # symptomatic
                pop2[key] = 'i'
                t_i2[key] = int(np.random.uniform(min_infect,max_infect))
            else: # undetected/asymptomatic
                pop2[key] = 'u'
                t_u2[key] = int(np.random.uniform(min_infect,max_infect))
            
    for key in t_i:
        time = t_i2.pop(key) - 1
        if time > 0:
            t_i2[key] = time
        else:
            if np.random.rand() < p_f: # fatality
                pop2[key] = 'f'
            else: # recovered
                pop2[key] = 'r'
                
    for key in t_u:
        time = t_u2.pop(key) - 1
        if time > 0:
            t_u2[key] = time
        else: # recovery
            pop2[key] = 'r'
        
    return pop2, t_e2, t_i2, t_u2

def plot_realizations(n_realizations):
    '''
    Produces a plot with many realizations of S, I, R populations vs time
    Inputs: n_realizations: number of realizations to plot
    '''
    # Create dictionaries to store the times and results of each realization
    tts = {}
    results = {}

    # Simulate n_realizations given the p, nc, pt values passed to the function
    for i in range(n_realizations):
        tts[i], results[i] = simulate1D()
    
    # Create the figure
    plt.figure(figsize=(12,9))

    # Iterate through each realization and plot
    for key in tts:
        # Separate results array to S, I, R arrays
        S, E, I, U, R, F = np.transpose(results[key])
        plt.plot(tts[key], S, color = 'blue', linewidth=1)
        plt.plot(tts[key], E, color = 'orange', linewidth=1)
        plt.plot(tts[key], I, color = 'green', linewidth=1)
        plt.plot(tts[key], U, color = 'red', linewidth=1)
        plt.plot(tts[key], R, color = 'purple', linewidth=1)
        plt.plot(tts[key], F, color = 'brown', linewidth=1)

    # Formatting
    plt.title(f'Evolution of Populations over Time for {n_realizations} realizations')
    plt.xlabel('Time (days)')
    plt.ylabel('Population')
    plt.legend(['S', 'E', 'I', 'U', 'R', 'F' ])

"""# Sensitivity Testing"""

# GLOBAL VARIABLES
n = 10000 # population

nc1_lam = 1.665 # rate of contacts per day of exposed and undetected people (modelled by Poisson)
nc2_lam = 1 # rate of contacts per day of symptomatic infected people (modelled by Poisson)

incubate_time = 2 # days that incubation lasts (before an 'e' individual becomes 'i', symptomatic, or 'u', asymptomatic)

# generate uniform distribution (nearest integer)
min_infect = 5 # minimum number of days infected or undetected person (i.e. symptomatic or asymptomatic) is contagious
max_infect = 15 # maximum number of days infected or undetected person (i.e. symptomatic or asymptomatic) is contagious

# probabilities
p_e = 0.201    # prob of being exposed after contact 
p_i = 0.484   # prob of becoming symptomatic / infected
p_u = 1 - p_i # prob of becoming asymptomatic (undetected)
p_f = 2.6605/100    # prob of a fatality (assuming only symptomatic individuals may die)

pd.set_option("display.max_rows", None, "display.max_columns", None)

# change title before running function
for prob in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
    p_e = prob
    print(p_e)
    display(plot_average_over_realizations(100, parameter = 'p_e'))

# GLOBAL VARIABLES
n = 10000 # population

nc1_lam = 1.665 # rate of contacts per day of exposed and undetected people (modelled by Poisson)
nc2_lam = 1 # rate of contacts per day of symptomatic infected people (modelled by Poisson)

incubate_time = 2 # days that incubation lasts (before an 'e' individual becomes 'i', symptomatic, or 'u', asymptomatic)

# generate uniform distribution (nearest integer)
min_infect = 5 # minimum number of days infected or undetected person (i.e. symptomatic or asymptomatic) is contagious
max_infect = 15 # maximum number of days infected or undetected person (i.e. symptomatic or asymptomatic) is contagious

# probabilities
p_e = 0.201    # prob of being exposed after contact 
p_i = 0.484   # prob of becoming symptomatic / infected
p_u = 1 - p_i # prob of becoming asymptomatic (undetected)
p_f = 2.6605/100    # prob of a fatality (assuming only symptomatic individuals may die)

pd.set_option("display.max_rows", None, "display.max_columns", None)

# change title before running function
for prob in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
    p_i = prob
    print(p_i)
    display(plot_average_over_realizations(100, parameter = 'p_i'))

# GLOBAL VARIABLES
n = 10000 # population

nc1_lam = 1.665 # rate of contacts per day of exposed and undetected people (modelled by Poisson)
nc2_lam = 1 # rate of contacts per day of symptomatic infected people (modelled by Poisson)

incubate_time = 2 # days that incubation lasts (before an 'e' individual becomes 'i', symptomatic, or 'u', asymptomatic)

# generate uniform distribution (nearest integer)
min_infect = 5 # minimum number of days infected or undetected person (i.e. symptomatic or asymptomatic) is contagious
max_infect = 15 # maximum number of days infected or undetected person (i.e. symptomatic or asymptomatic) is contagious

# probabilities
p_e = 0.201    # prob of being exposed after contact 
p_i = 0.484   # prob of becoming symptomatic / infected
p_u = 1 - p_i # prob of becoming asymptomatic (undetected)
p_f = 2.6605/100    # prob of a fatality (assuming only symptomatic individuals may die)

pd.set_option("display.max_rows", None, "display.max_columns", None)

# change title before running function
for prob in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
    p_f = prob/5
    display(plot_average_over_realizations(100, parameter = 'p_f'))

# GLOBAL VARIABLES
n = 10000 # population

nc1_lam = 1.665 # rate of contacts per day of exposed and undetected people (modelled by Poisson)
nc2_lam = 1 # rate of contacts per day of symptomatic infected people (modelled by Poisson)

incubate_time = 2 # days that incubation lasts (before an 'e' individual becomes 'i', symptomatic, or 'u', asymptomatic)

# generate uniform distribution (nearest integer)
min_infect = 5 # minimum number of days infected or undetected person (i.e. symptomatic or asymptomatic) is contagious
max_infect = 15 # maximum number of days infected or undetected person (i.e. symptomatic or asymptomatic) is contagious

# probabilities
p_e = 0.201    # prob of being exposed after contact 
p_i = 0.484   # prob of becoming symptomatic / infected
p_u = 1 - p_i # prob of becoming asymptomatic (undetected)
p_f = 2.6605/100    # prob of a fatality (assuming only symptomatic individuals may die)

pd.set_option("display.max_rows", None, "display.max_columns", None)

# change title before running function
for lam in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    nc1_lam = lam
    display(plot_average_over_realizations(100, parameter = 'lambda'))