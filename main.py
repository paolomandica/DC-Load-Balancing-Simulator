import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import multiprocessing as mp
from time import time
from simulation_utils import Simulator, plot


number_of_tasks = (10**5)
number_of_servers = 20
d = 3
rho_values = np.arange(0.8, 1., 0.01)
multiple_sim = False
n_sim = 5
n_proc = mp.cpu_count()


if __name__ == "__main__":

    mean_system_times = []
    mean_system_delays = []
    mean_system_delays_lists = []

    print("\nStarting simulation process...")
    start = time()

    simulator = Simulator(number_of_tasks, number_of_servers, d)
    mean_system_delays_jsq, overheads_jsq = simulator.multiprocessing_simulation(
        rho_values, n_proc)

    # if multiple_sim:
    #     for i in range(n_sim):
    #         mean_system_delays_part = simulator.multiprocessing_simulation(
    #             rho_values, n_proc)
    #         mean_system_delays_lists.append(mean_system_delays_part)
    #     mean_system_delays = [
    #         sum(x)/n_sim for x in zip(*mean_system_delays_lists)]

    # Pod-d simulation
    simulator = Simulator(number_of_tasks, number_of_servers, d)
    mean_system_delays_pod, overheads_pod = simulator.multiprocessing_simulation(
        rho_values, n_proc)

    # JSQ simulation
    simulator = Simulator(
        number_of_tasks, number_of_servers, number_of_servers)
    mean_system_delays_jsq, overheads_jsq = simulator.multiprocessing_simulation(
        rho_values, n_proc)

    # JBT-d simulation
    simulator = Simulator(number_of_tasks, number_of_servers, d)
    mean_system_delays_jbt, overheads_jbt = simulator.multiprocessing_simulation(
        rho_values, n_proc, jbt=True)

    end = time()
    print("Simulation completed in", int(end-start), "seconds!\n\n")

    data = {
        "Rho": rho_values,
        "Pod": mean_system_delays_pod,
        "JSQ": mean_system_delays_jsq,
        "JBT-d": mean_system_delays_jbt
    }
    df = pd.DataFrame.from_dict(data)
    ylabel = "Mean System Delay"
    df = df.melt('Rho', var_name='Policy',  value_name=ylabel)
    path = './plots/weibull_' + str(number_of_tasks) + '.png'
    plot(df, d, "Mean System Time Variation",
         "Utilization Coefficient (Rho)", ylabel, path)

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
