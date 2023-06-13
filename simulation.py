import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt

# Define the population
population_size = 10000
population = pd.DataFrame({'state': ['susceptible'] * population_size,
                           'infection_type': [''] * population_size})

# Define the parameters
infection_probability = [np.random.normal(loc=np.sin(i/10)/50, scale=0.01) for i in range(100)]
infection_willingness = 0.005  # Probability of deliberately infecting oneself
recovery_probability_infected = 0.05  # Recovery probability for infected individuals
recovery_probability_severe = 0.05  # Recovery probability for severely infected individuals
recovery_probability_hospitalized = 0.2  # Recovery probability for hospitalized individuals
severe_probability = 0.2  # Probability of transitioning from infected to severely infected
hospital_capacity = 200  # Maximum capacity of hospitalized individuals
lethality_probability_severe = 0.05  # Probability of dying for severely infected individuals
lethality_probability_hospitalized = 0.01  # Probability of dying for hospitalized individuals
num_time_steps = len(infection_probability)  # Number of time steps to simulate

# Track statistics
susceptible_count = []
infected_count_chance = []
infected_count_deliberate = []
severely_infected_count_chance = []
severely_infected_count_deliberate = []
hospitalized_count_chance = []
hospitalized_count_deliberate = []
dead_count_chance = []
dead_count_deliberate = []
recovered_count_chance = []
recovered_count_deliberate = []


# Simulation loop
for i in range(num_time_steps):
    # Count the number of individuals in each state
    state_counts = population['state'].value_counts()

    # Track the counts of each state
    susceptible_count.append(state_counts.get('susceptible', 0))
    infected_count_chance.append(np.sum((population['state'] == 'infected') & (population['infection_type'] == 'chance')))
    infected_count_deliberate.append(np.sum((population['state'] == 'infected') & (population['infection_type'] == 'deliberate')))
    severely_infected_count_chance.append(np.sum((population['state'] == 'severely infected') & (population['infection_type'] == 'chance')))
    severely_infected_count_deliberate.append(np.sum((population['state'] == 'severely infected') & (population['infection_type'] == 'deliberate')))
    hospitalized_count_chance.append(np.sum((population['state'] == 'hospitalized') & (population['infection_type'] == 'chance')))
    hospitalized_count_deliberate.append(np.sum((population['state'] == 'hospitalized') & (population['infection_type'] == 'deliberate')))
    dead_count_chance.append(np.sum((population['state'] == 'dead') & (population['infection_type'] == 'chance')))
    dead_count_deliberate.append(np.sum((population['state'] == 'dead') & (population['infection_type'] == 'deliberate')))
    recovered_count_chance.append(np.sum((population['state'] == 'recovered') & (population['infection_type'] == 'chance')))
    recovered_count_deliberate.append(np.sum((population['state'] == 'recovered') & (population['infection_type'] == 'deliberate')))

    # Generate random numbers for state transitions
    random_numbers = np.random.random(population_size)

    # Check if susceptible individuals get infected
    susceptible_mask = (population['state'] == 'susceptible')
    infected_mask = (random_numbers < infection_probability[i])
    population.loc[susceptible_mask & infected_mask, 'state'] = 'infected'
    population.loc[susceptible_mask & infected_mask, 'infection_type'] = 'chance'
    random_numbers = np.random.random(population_size)

    # Check if individuals decide to get deliberately infected
    low_hospital_utilization = ((hospitalized_count_chance[-1] + hospitalized_count_deliberate[-1]) / hospital_capacity) < 0.5  # Define the threshold for low utilization
    susceptible_mask = (population['state'] == 'susceptible')
    random_numbers = np.random.random(population_size)
    deliberate_infection_mask = (random_numbers < infection_willingness) & low_hospital_utilization
    population.loc[susceptible_mask & deliberate_infection_mask, 'state'] = 'infected'
    population.loc[susceptible_mask & deliberate_infection_mask, 'infection_type'] = 'deliberate'

    
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
    population.loc[np.logical_and(severe_infected_mask, hospitalized_mask), 'state'] = 'hospitalized'
    severe_infected_mask = (population['state'] == 'severely infected')
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



# Plot the epidemic progression
time_steps = range(num_time_steps)

# Define line styles and markers for each infection type
line_styles = {'chance': '-', 'deliberate': '--'}
markers = {'chance': 'o', 'deliberate': 's'}

# Create a figure with two subplots
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

# Plot for infection type: chance
axes[0].semilogy(time_steps, susceptible_count, label='Susceptible', linestyle=line_styles['chance'], marker=markers['chance'])
axes[0].semilogy(time_steps, infected_count_chance, label='Infected (Chance)', linestyle=line_styles['chance'], marker=markers['chance'])
axes[0].semilogy(time_steps, severely_infected_count_chance, label='Severely Infected (Chance)', linestyle=line_styles['chance'], marker=markers['chance'])
axes[0].semilogy(time_steps, hospitalized_count_chance, label='Hospitalized (Chance)', linestyle=line_styles['chance'], marker=markers['chance'])
axes[0].semilogy(time_steps, dead_count_chance, label='Dead (Chance)', linestyle=line_styles['chance'], marker=markers['chance'])
axes[0].semilogy(time_steps, recovered_count_chance, label='Recovered (Chance)', linestyle=line_styles['chance'], marker=markers['chance'])
axes[0].set_xlabel('Time Steps')
axes[0].set_ylabel('Population Count (Log Scale)')
axes[0].set_title('Epidemic Progression (Infection Type: Chance)')
axes[0].legend()
axes[0].set_yscale('log')

# Add infection type annotations for chance
state_counts_chance = population[population['infection_type'] == 'chance']['state'].value_counts()
for state, count in state_counts_chance.items():
    if state != 'susceptible':
        axes[0].annotate(f"{state} ({count})", xy=(num_time_steps - 1, count), xytext=(5, 0), textcoords='offset points')

# Plot for infection type: deliberate
axes[1].semilogy(time_steps, susceptible_count, label='Susceptible', linestyle=line_styles['deliberate'], marker=markers['deliberate'])
axes[1].semilogy(time_steps, infected_count_deliberate, label='Infected (Deliberate)', linestyle=line_styles['deliberate'], marker=markers['deliberate'])
axes[1].semilogy(time_steps, severely_infected_count_deliberate, label='Severely Infected (Deliberate)', linestyle=line_styles['deliberate'], marker=markers['deliberate'])
axes[1].semilogy(time_steps, hospitalized_count_deliberate, label='Hospitalized (Deliberate)', linestyle=line_styles['deliberate'], marker=markers['deliberate'])
axes[1].semilogy(time_steps, dead_count_deliberate, label='Dead (Deliberate)', linestyle=line_styles['deliberate'], marker=markers['deliberate'])
axes[1].semilogy(time_steps, recovered_count_deliberate, label='Recovered (Deliberate)', linestyle=line_styles['deliberate'], marker=markers['deliberate'])
axes[1].set_xlabel('Time Steps')
axes[1].set_ylabel('Population Count (Log Scale)')
axes[1].set_title('Epidemic Progression (Infection Type: Deliberate)')
axes[1].legend()
axes[1].set_yscale('log')

# Add infection type annotations for deliberate
state_counts_deliberate = population[population['infection_type'] == 'deliberate']['state'].value_counts()
for state, count in state_counts_deliberate.items():
    if state != 'susceptible':
        axes[1].annotate(f"{state} ({count})", xy=(num_time_steps - 1, count), xytext=(5, 0), textcoords='offset points')

plt.tight_layout()
plt.show()
