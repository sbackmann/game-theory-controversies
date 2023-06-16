import numpy as np 


recovery_probability_infected = 0.05  
recovery_probability_severe = 0.005  
recovery_probability_hospitalized = 0.5
severe_probability = 0.2 
hospital_capacity = 200  
lethality_probability_severe = 0.3  
lethality_probability_hospitalized = 0.01  
num_time_steps = 200

cycles = 4
factor_rec = 15
num_recovered = 0

share_deliberate = 0.3

deliberate_willingsness = 10

deliberate_mask = np.zeros((10000, ))
deliberate_mask[:int(share_deliberate * 10000)] = 1
chance_mask = np.ones((10000, ))
chance_mask[:int(share_deliberate * 10000)] = 0

deliberate_mask = deliberate_mask.astype(bool)
chance_mask = chance_mask.astype(bool)


# 0 = susceptible, 1 = infected, 2 = severely infected, 3 = hospitalized, 4 = dead, 5 = recovered

population = np.zeros((10000, ))



for i in range(num_time_steps): 
    infection_rate = 0.01 * np.max((np.sin(i*np.pi*2/(num_time_steps/cycles))+1)/2 - factor_rec * (num_recovered/10000), 0)
    infection_rate = np.repeat(infection_rate, 10000)

    random_numbers = np.random.random(10000)

    infected_mask = (random_numbers < infection_rate)
    sucessceptible_mask = (population == 0)
    hospital_occupancy = np.sum(population == 3)/hospital_capacity
    
    # chance_infection: 
    population[chance_mask * infected_mask * sucessceptible_mask] = 1
    # deliberate_infection:
    if (hospital_occupancy < 0.5 ): 
        infected_mask = (random_numbers < infection_rate * deliberate_willingsness)
        population[deliberate_mask * infected_mask * sucessceptible_mask] = 1   
    else: 
        population[deliberate_mask * infected_mask * sucessceptible_mask] = 1
    
    random_numbers = np.random.random(10000)

    infected_mask = (population == 1)
    severe_mask = (random_numbers < severe_probability)
    population[infected_mask * severe_mask] = 2

    random_numbers = np.random.random(10000)

    severe_mask = (population == 2)
    if (hospital_occupancy > 0.95):
        hospitalized_mask = (random_numbers == 0)
    else:
        hospitalized_mask = (random_numbers < ((1-hospital_occupancy) * (hospital_capacity/np.sum(population == 2))))
    population[severe_mask * hospitalized_mask] = 3
    
    random_numbers = np.random.random(10000)
    severe_mask = (population == 2)
    population[severe_mask * (random_numbers < recovery_probability_severe)] = 5
    severe_mask = (population == 2); random_numbers = np.random.random(10000)
    population[severe_mask * (random_numbers < lethality_probability_severe)] = 4

    hospital_mask = (population == 3)
    population[hospital_mask * (random_numbers < recovery_probability_hospitalized)] = 5
    hospital_mask = (population == 3); random_numbers = np.random.random(10000)
    population[hospital_mask * (random_numbers < lethality_probability_hospitalized)] = 4

    infected_mask = (population == 1)
    population[infected_mask * (random_numbers < recovery_probability_infected)] = 5


    num_recovered = np.sum(population == 5)
   

print("dead: ", np.sum(population == 4)/10000)

print("dead deliberate ", np.sum(population[deliberate_mask] == 4)/(10000 * share_deliberate))
print("dead chance ", np.sum(population[chance_mask] == 4)/(10000 * (1-share_deliberate)))
    

