from Dispatcher import Dispatcher
import matplotlib.pyplot as plt
import numpy as np
import multiprocessing as mp
from time import time


number_of_tasks = 10**5
number_of_servers = 100
d = 3
rho_values = np.arange(0.8, 1., 0.01)


def simulate(rho):
    dispatcher = Dispatcher(number_of_tasks,
                            number_of_servers,
                            rho, d)
    mean_sys_delay = dispatcher.execute_simulation()
    return mean_sys_delay


def simulate_partial(rho, i, output: list):
    dispatcher = Dispatcher(number_of_tasks,
                            number_of_servers,
                            rho, d)
    mean_sys_delay = dispatcher.execute_simulation()

    output.append((i, mean_sys_delay))


def multiprocessing_simulation(rho_values, n_proc):
    processes = []
    # initialize the Manager for results and shared variables
    manager = mp.Manager()
    output = manager.list()

    # initialize processes
    for i in range(len(rho_values)):
        p = mp.Process(target=simulate_partial,
                       args=[rho_values[i], i, output])
        processes.append(p)

    # start processes
    for p in processes:
        p.start()

    # wait for each process to terminate
    for p in processes:
        p.join()

    output.sort()
    results = [r[1] for r in output]
    return results


if __name__ == "__main__":

    mean_system_times = []
    mean_system_delays = []

    print("\nStarting simulation process...")
    start = time()

    n_proc = mp.cpu_count()//2
    mean_system_delays = multiprocessing_simulation(rho_values, n_proc)

    # for rho in rho_values:
    #     mean_system_delays.append(simulate(rho))

    print(mean_system_delays)

    end = time()
    print("\nSimulation completed in", int(end-start), "seconds!\n")

    xi = list(range(len(rho_values)))
    plt.plot(rho_values, mean_system_delays)
    plt.scatter(rho_values, mean_system_delays, c='r')
    # ticks = [rho_values[i]
    #          for i in range(0, len(rho_values)-2, 2)] + [rho_values[-2]]
    plt.xticks(rho_values)
    plt.title("Mean System Delay Variation")
    plt.xlabel("Utilization Coefficient (Rho)")
    plt.ylabel("Mean System Delay")
    plt.show()
