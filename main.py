from Dispatcher import Dispatcher
import matplotlib.pyplot as plt
import numpy as np
import multiprocessing as mp
from time import time


number_of_tasks = (10**6)
number_of_servers = 20
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
    mean_system_delays_lists = []

    print("\nStarting simulation process...")
    start = time()

    n_proc = mp.cpu_count()//2
    # n_proc = 1
    # n_sim = 10
    # for i in range(n_sim):
    #     mean_system_delays_part = multiprocessing_simulation(
    #         rho_values, n_proc)
    #     mean_system_delays_lists.append(mean_system_delays_part)

    # mean_system_delays = [sum(x)/n_sim for x in zip(*mean_system_delays_lists)]

    mean_system_delays = multiprocessing_simulation(
        rho_values, n_proc)

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
    path = './plots/weibull_' + str(number_of_tasks) + '.png'
    plt.savefig(path)
    plt.show()
