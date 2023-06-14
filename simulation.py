import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt


# Create separate populations
population_size = 10000
populations = {
    'chance': pd.DataFrame({'state': ['susceptible'] * population_size, 'infection_type': [''] * population_size, 'infection_willingness': 0}),
    'deliberate': pd.DataFrame({'state': ['susceptible'] * population_size, 'infection_type': [''] * population_size, 'infection_willingness': 0.005})
}

# Track statistics for each population
population_counts = {
    'chance': {
        'susceptible': [population_size],
        'infected': [0],
        'severely_infected': [0],
        'hospitalized': [0],
        'dead': [0],
        'recovered': [0]
    },
    'deliberate': {
        'susceptible': [population_size],
        'infected': [0],
        'severely_infected': [0],
        'hospitalized': [0],
        'dead': [0],
        'recovered': [0]
    }
}

# Define the parameters
# infection_probability = [np.random.normal(loc=np.sin(i/10)/50, scale=0.01) for i in range(100)]
recovery_probability_infected = 0.05  # Recovery probability for infected individuals
recovery_probability_severe = 0.05  # Recovery probability for severely infected individuals
recovery_probability_hospitalized = 0.2  # Recovery probability for hospitalized individuals
severe_probability = 0.2  # Probability of transitioning from infected to severely infected
hospital_capacity = 200  # Maximum capacity of hospitalized individuals
lethality_probability_severe = 0.05  # Probability of dying for severely infected individuals
lethality_probability_hospitalized = 0.01  # Probability of dying for hospitalized individuals
num_time_steps = 200  # Number of time steps to simulate


# Simulation loop
for i in range(num_time_steps):
    for population_type, population in populations.items():
        active_population = population_counts[population_type]['susceptible'][-1] + population_counts[population_type]['infected'][-1] + population_counts[population_type]['severely_infected'][-1] + population_counts[population_type]['recovered'][-1]
        infection_probability = np.random.normal(loc=np.sin(i/10)/50, scale=0.01) \
                                * (1 + (population_counts[population_type]["infected"][-1] + population_counts[population_type]["severely_infected"][-1]) / active_population) \
                                * (1-population_counts[population_type]["recovered"][-1] / active_population)

        # Generate random numbers for state transitions
        random_numbers = np.random.random(population_size)

        # Check if susceptible individuals get infected
        susceptible_mask = (population['state'] == 'susceptible')
        infected_mask = (random_numbers < infection_probability)
        population.loc[susceptible_mask & infected_mask, 'state'] = 'infected'
        population.loc[susceptible_mask & infected_mask, 'infection_type'] = 'chance'
        random_numbers = np.random.random(population_size)

        # Check if individuals decide to get deliberately infected
        low_hospital_utilization = ((population_counts[population_type]["hospitalized"][-1]) / hospital_capacity) < 0.5  # Define the threshold for low utilization
        susceptible_mask = (population['state'] == 'susceptible')
        deliberate_infection_mask = (random_numbers < population["infection_willingness"]) & low_hospital_utilization
        population.loc[susceptible_mask & deliberate_infection_mask, 'state'] = 'infected'
        population.loc[susceptible_mask & deliberate_infection_mask, 'infection_type'] = 'deliberate'

        
        # Check if infected individuals transition to severely infected
        infected_mask = (population['state'] == 'infected')
        severe_infected_mask = (random_numbers < severe_probability)
        population.loc[infected_mask & severe_infected_mask, 'state'] = 'severely_infected'
        random_numbers = np.random.random(population_size)

        # Check if severely infected individuals transition to hospitalized or dead
        severe_infected_mask = (population['state'] == 'severely_infected')
        hospitalized_mask = (random_numbers < (1 - (population['state'] == 'hospitalized').sum() / hospital_capacity))
        random_numbers = np.random.random(population_size)
        dead_mask = (random_numbers < lethality_probability_severe)
        # print(np.logical_or(hospitalized_mask, dead_mask))
        population.loc[np.logical_and(severe_infected_mask, hospitalized_mask), 'state'] = 'hospitalized'
        severe_infected_mask = (population['state'] == 'severely_infected')
        population.loc[np.logical_and(severe_infected_mask, dead_mask), 'state'] = 'dead'
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

        # Count the number of individuals in each state
        state_counts = population['state'].value_counts()


        for state, count in state_counts.items():
            population_counts[population_type][state].append(count)
        for counts in population_counts[population_type].values():
            if len(counts) < i + 2:
                counts.append(0)


print(populations["deliberate"]["infection_type"].value_counts())

# Plot the epidemic progression
time_steps = range(num_time_steps + 1)

# Create a figure with two subplots
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

# Plot for population type: chance
axes[0].semilogy(time_steps, population_counts['chance']['susceptible'], label='Susceptible')
axes[0].semilogy(time_steps, population_counts['chance']['infected'], label='Infected')
axes[0].semilogy(time_steps, population_counts['chance']['severely_infected'], label='Severely Infected')
axes[0].semilogy(time_steps, population_counts['chance']['hospitalized'], label='Hospitalized')
axes[0].semilogy(time_steps, population_counts['chance']['dead'], label='Dead')
axes[0].semilogy(time_steps, population_counts['chance']['recovered'], label='Recovered')
axes[0].set_xlabel('Time Steps')
axes[0].set_ylabel('Population Count (Log Scale)')
axes[0].set_title('Epidemic Progression (Population Type: Chance)')
axes[0].legend()
axes[0].set_yscale('log')

# Plot for population type: deliberate
axes[1].semilogy(time_steps, population_counts['deliberate']['susceptible'], label='Susceptible')
axes[1].semilogy(time_steps, population_counts['deliberate']['infected'], label='Infected')
axes[1].semilogy(time_steps, population_counts['deliberate']['severely_infected'], label='Severely Infected')
axes[1].semilogy(time_steps, population_counts['deliberate']['hospitalized'], label='Hospitalized')
axes[1].semilogy(time_steps, population_counts['deliberate']['dead'], label='Dead')
axes[1].semilogy(time_steps, population_counts['deliberate']['recovered'], label='Recovered')
axes[1].set_xlabel('Time Steps')
axes[1].set_ylabel('Population Count (Log Scale)')
axes[1].set_title('Epidemic Progression (Population Type: Deliberate)')
axes[1].legend()
axes[1].set_yscale('log')

plt.tight_layout()
plt.show()
