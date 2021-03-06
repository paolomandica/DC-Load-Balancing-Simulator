from Dispatcher import Dispatcher
import multiprocessing as mp
import matplotlib.pyplot as plt
import seaborn as sns
import math


def compute_process_time_exp(beta, alpha):
    return beta*math.factorial(1/alpha)


def compute_interval_time_exp(t_0, q, y):
    return t_0 + (1-q)*y


def plot(df, d, title, xlabel, ylabel, path, confidence_intervals=None):
    plt.figure(figsize=(16, 9))
    sns.set(style='darkgrid',)
    sns.lineplot(x='Rho', y=ylabel, data=df,
                 hue='Policy', style='Policy',
                 markers=True, dashes=False)

    if confidence_intervals != None:
        for (lower, upper) in confidence_intervals:
            rho = df['Rho'].unique()
            plt.fill_between(rho, lower, upper, alpha=0.3)

    plt.title(title, fontsize=24)
    plt.xlabel(xlabel, fontsize=18)
    plt.ylabel(ylabel, fontsize=18)
    if confidence_intervals != None:
        plt.legend(loc='upper left')
    plt.legend(fontsize='x-large')
    plt.savefig(path)
    plt.show()


class Simulator:

    def __init__(self, number_of_tasks, number_of_servers, d):
        self.number_of_servers = number_of_servers
        self.number_of_tasks = number_of_tasks
        self.d = d

    def simulate_partial(self, rho, i, output: list, overheads: list, jbt, custom, seed):
        dispatcher = Dispatcher(self.number_of_tasks,
                                self.number_of_servers,
                                rho, self.d, seed,
                                jbt=jbt, custom=custom)
        mean_sys_delay, overhead = dispatcher.execute_simulation()
        output.append((i, mean_sys_delay))
        overheads.append((i, overhead))

    def multiprocessing_simulation(self, rho_values, n_proc, jbt=False, custom=False, seed=1):
        processes = []
        # initialize the Manager for results and shared variables
        manager = mp.Manager()
        output = manager.list()
        overheads = manager.list()

        # initialize processes
        for i in range(len(rho_values)):
            p = mp.Process(target=self.simulate_partial,
                           args=[rho_values[i], i, output, overheads, jbt, custom, seed])
            processes.append(p)

        # start processes
        for p in processes:
            p.start()

        # wait for each process to terminate
        for p in processes:
            p.join()

        output.sort()
        overheads.sort()
        results = [r[1] for r in output]
        overheads = [r[1] for r in overheads]
        return results, overheads
