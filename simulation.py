import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt

# Define the population
population_size = 1000
population = pd.DataFrame({'state': ['susceptible'] * population_size})

# Define the parameters
infection_probability = 0.05
recovery_probability_infected = 0.05  # Recovery probability for infected individuals
recovery_probability_severe = 0.05  # Recovery probability for severely infected individuals
recovery_probability_hospitalized = 0.2  # Recovery probability for hospitalized individuals
severe_probability = 0.2  # Probability of transitioning from infected to severely infected
hospital_capacity = 120  # Maximum capacity of hospitalized individuals
lethality_probability_severe = 0.1  # Probability of dying for severely infected individuals
lethality_probability_hospitalized = 0.02  # Probability of dying for hospitalized individuals
num_time_steps = 100

# Track statistics
susceptible_count = []
infected_count = []
severely_infected_count = []
hospitalized_count = []
dead_count = []
recovered_count = []

# Simulation loop
for _ in range(num_time_steps):
    # Count the number of individuals in each state
    state_counts = population['state'].value_counts()
    print(state_counts)

    # Track the counts of each state
    susceptible_count.append(state_counts.get('susceptible', 0))
    infected_count.append(state_counts.get('infected', 0))
    severely_infected_count.append(state_counts.get('severely infected', 0))
    hospitalized_count.append(state_counts.get('hospitalized', 0))
    dead_count.append(state_counts.get('dead', 0))
    recovered_count.append(state_counts.get('recovered', 0))

    # Generate random numbers for state transitions
    random_numbers = np.random.random(population_size)

    # Check if susceptible individuals get infected
    susceptible_mask = (population['state'] == 'susceptible')
    infected_mask = (random_numbers < infection_probability)
    population.loc[susceptible_mask & infected_mask, 'state'] = 'infected'
    random_numbers = np.random.random(population_size)
    
    # Check if infected individuals transition to severely infected
    infected_mask = (population['state'] == 'infected')
    severe_infected_mask = (random_numbers < severe_probability)
    population.loc[infected_mask & severe_infected_mask, 'state'] = 'severely infected'
    random_numbers = np.random.random(population_size)

    # Check if severely infected individuals transition to hospitalized or dead
    severe_infected_mask = (population['state'] == 'severely infected')
    hospitalized_mask = (random_numbers < (1 - (population['state'] == 'hospitalized').sum() / hospital_capacity))
    random_numbers = np.random.random(population_size)
    dead_mask = (random_numbers < lethality_probability_severe)
    # print(np.logical_or(hospitalized_mask, dead_mask))
    state_counts_2 = population['state'].value_counts()
    print("severe", state_counts_2)
    population.loc[np.logical_and(severe_infected_mask, hospitalized_mask), 'state'] = 'hospitalized'
    state_counts_2 = population['state'].value_counts()
    print("hospitalize", state_counts_2)
    severe_infected_mask = (population['state'] == 'severely infected')
    population.loc[np.logical_and(severe_infected_mask, dead_mask), 'state'] = 'dead'
    state_counts_2 = population['state'].value_counts()
    print("dead", state_counts_2)
    random_numbers = np.random.random(population_size)

    # Check if hospitalized individuals recover or die
    hospitalized_mask = (population['state'] == 'hospitalized')
    recovery_mask = (random_numbers < recovery_probability_hospitalized)
    random_numbers = np.random.random(population_size)
    dead_mask = (random_numbers < lethality_probability_hospitalized)
    population.loc[np.logical_and(hospitalized_mask, recovery_mask), 'state'] = 'recovered'
    population.loc[hospitalized_mask & dead_mask, 'state'] = 'dead'
    random_numbers = np.random.random(population_size)

    # Check if infected individuals recover
    infected_mask = (population['state'] == 'infected')
    recovery_mask = (random_numbers < recovery_probability_infected)
    population.loc[infected_mask & recovery_mask, 'state'] = 'recovered'

# Plot the epidemic progression
time_steps = range(num_time_steps)
plt.plot(time_steps, susceptible_count, label='Susceptible')
plt.plot(time_steps, infected_count, label='Infected')
plt.plot(time_steps, severely_infected_count, label='Severely Infected')
plt.plot(time_steps, hospitalized_count, label='Hospitalized')
plt.plot(time_steps, dead_count, label='Dead')
plt.plot(time_steps, recovered_count, label='Recovered')
plt.xlabel('Time Steps')
plt.ylabel('Population Count')
plt.legend()
plt.show()
