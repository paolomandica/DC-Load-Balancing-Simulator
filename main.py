from Dispatcher import Dispatcher
import matplotlib.pyplot as plt
import numpy as np


number_of_tasks = 100000
number_of_servers = 100
d = 3
rho_values = np.arange(0.8, 1., 0.01)


if __name__ == "__main__":

    mean_system_times = []

    for rho in rho_values:
        dispatcher = Dispatcher(number_of_tasks,
                                number_of_servers,
                                rho, d)
        mean_sys_time = dispatcher.execute_simulation()
        mean_system_times.append(mean_sys_time)

    print(mean_system_times)

    plt.plot(rho_values, mean_system_times)
    plt.scatter(rho_values, mean_system_times, c='r')
    plt.show()
