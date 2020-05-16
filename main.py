import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import multiprocessing as mp
from time import time
from simulation_utils import Simulator, plot


number_of_tasks = (10**6)
number_of_servers = 20
d = 3
rho_values = np.arange(0.8, 1., 0.01)
multiple_sim = True
n_sim = 5
n_proc = mp.cpu_count()


def perform_multiple_simulations(simulator, jbt=False):
    mean_system_times_lists = []
    mean_system_times = []
    z = 1.96
    lowers = []
    uppers = []

    for _ in range(n_sim):
        mean_system_times_partial, overheads = simulator.multiprocessing_simulation(
            rho_values, n_proc, jbt)
        mean_system_times_lists.append(mean_system_times_partial)

    for l in zip(*mean_system_times_lists):
        mean, sigma = np.mean(l), np.std(l)
        mean_system_times.append(np.mean(l))
        lowers.append(mean - (z*sigma/np.sqrt(len(l))))
        uppers.append(mean + (z*sigma/np.sqrt(len(l))))
        confidence_intervals = (lowers, uppers)

    return mean_system_times, confidence_intervals, overheads


if __name__ == "__main__":

    mean_system_times = []
    mean_system_delays = []
    ci = None

    print("\nStarting simulation process...")
    start = time()

    if multiple_sim:
        # Pod-d simulation
        simulator = Simulator(number_of_tasks, number_of_servers, d)
        mean_system_times_pod, confidence_intervals_pod, overheads_pod = perform_multiple_simulations(
            simulator)

        # JSQ simulation
        simulator = Simulator(
            number_of_tasks, number_of_servers, number_of_servers)
        mean_system_times_jsq, confidence_intervals_jsq, overheads_jsq = perform_multiple_simulations(
            simulator)

        # JBT-d simulation
        simulator = Simulator(number_of_tasks, number_of_servers, d)
        mean_system_times_jbt, confidence_intervals_jbt, overheads_jbt = perform_multiple_simulations(
            simulator, True)

        filename = 'weibull_multiple_'
        ci = [confidence_intervals_pod,
              confidence_intervals_jsq,
              confidence_intervals_jbt]

    else:
        # Pod-d simulation
        simulator = Simulator(number_of_tasks, number_of_servers, d)
        mean_system_times_pod, overheads_pod = simulator.multiprocessing_simulation(
            rho_values, n_proc)

        # JSQ simulation
        simulator = Simulator(
            number_of_tasks, number_of_servers, number_of_servers)
        mean_system_times_jsq, overheads_jsq = simulator.multiprocessing_simulation(
            rho_values, n_proc)

        # JBT-d simulation
        simulator = Simulator(number_of_tasks, number_of_servers, d)
        mean_system_times_jbt, overheads_jbt = simulator.multiprocessing_simulation(
            rho_values, n_proc, jbt=True)

        filename = 'weibull_'

    end = time()
    print("Simulation completed in", int(end-start), "seconds!\n\n")

    data = {
        "Rho": rho_values,
        "Pod": mean_system_times_pod,
        "JSQ": mean_system_times_jsq,
        "JBT-d": mean_system_times_jbt
    }
    df = pd.DataFrame.from_dict(data)
    ylabel = "Mean System Time"
    df = df.melt('Rho', var_name='Policy',  value_name=ylabel)
    path = './plots/' + filename + str(number_of_tasks) + '.png'
    plot(df, d, "Mean System Time Variation",
         "Utilization Coefficient (Rho)", ylabel, path, ci)

    data = {
        "Rho": rho_values,
        "Pod": overheads_pod,
        "JSQ": overheads_jsq,
        "JBT-d": overheads_jbt
    }
    df = pd.DataFrame.from_dict(data)
    ylabel = "System Message Overhead"
    df = df.melt('Rho', var_name='Policy',  value_name=ylabel)
    path = './plots/weibull_overhead.png'
    plot(df, d, "Message Overhead Variation",
         "Utilization Coefficient (Rho)", ylabel, path)
