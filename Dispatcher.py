import random
import math
import simulation_utils as su
from numpy.random import weibull


class Dispatcher:

    # random.seed(1234)

    q = 24/25
    y = 100
    t_0 = 1
    alpha = 0.5

    def __init__(self, number_of_tasks: int,
                 number_of_servers: int,
                 rho: float, d: int):
        self.number_of_tasks = number_of_tasks
        self.number_of_servers = number_of_servers
        self.servers = {i: 0 for i in range(number_of_servers)}
        self.rho = rho
        self.d = d
        self.tasks_timeline = []
        self.system_times = []
        self.delays = []
        self.beta = self.compute_beta(self.rho)
        self.interval_times = []
        self.process_times = []

    def get_tasks_timeline(self):
        return self.tasks_timeline

    def get_servers(self):
        return self.servers

    def get_system_times(self):
        return self.system_times

    def compute_beta(self, rho):
        exp_t = self.t_0 + (1 - self.q)*self.y
        beta = rho*self.number_of_servers*exp_t/2
        return beta

    def generate_tasks_timeline(self, number_of_tasks: int):
        prev = 0
        for _ in range(number_of_tasks):
            r1 = random.uniform(0, 1)
            if r1 <= self.q:
                self.interval_times.append(self.t_0)
                prev += self.t_0
            else:
                r2 = random.uniform(0, 1)
                task = self.t_0 - self.y * math.log(r2)
                self.interval_times.append(task)
                prev += task
            self.tasks_timeline.append(prev)

    def pick_random_servers(self):
        ids = random.sample(range(0, self.number_of_servers), self.d)
        return ids

    def pick_best_server(self):
        servers_ids = self.pick_random_servers()

        best_server = servers_ids[0]
        min_time = self.servers[servers_ids[0]]

        for id in servers_ids[1:]:
            current_time = self.servers[id]
            if current_time < min_time:
                min_time = current_time
                best_server = id

        return best_server

    def assign_task(self, time, server_id):
        r3 = random.uniform(0, 1)
        # sostituire con exp x
        task = max(1, min(100*self.beta*2,
                          int(self.beta*(-math.log(r3))**(1/self.alpha))))
        self.process_times.append(task)
        server_time = self.servers[server_id]

        if server_time > time:
            task_finish_time = server_time + task
        else:
            task_finish_time = time + task
        self.servers[server_id] = task_finish_time

        # self.system_times.append(task_finish_time - time)

        delay = server_time - task - time
        self.delays.append(delay)

    def execute_simulation(self):
        print()
        print("Starting simulation for rho = " + str(self.rho))
        print("Beta =", self.beta)
        print()

        self.generate_tasks_timeline(self.number_of_tasks)

        for time in self.tasks_timeline:
            server_id = self.pick_best_server()
            self.assign_task(time, server_id)

        # mean_system_time = sum(self.system_times)/self.number_of_tasks
        mean_system_delay = sum(self.delays)/self.number_of_tasks

        print("Completed!")
        process_time_exp = su.compute_process_time_exp(self.beta, self.alpha)
        interval_time_exp = su.compute_interval_time_exp(
            self.t_0, self.q, self.y)

        mean_process_time = sum(self.process_times)/len(self.process_times)
        mean_interval_time = sum(self.interval_times)/len(self.interval_times)

        print("E[X] =", process_time_exp)
        print("Mean process time =", mean_process_time)
        print("E[T] =", interval_time_exp)
        print("Mean interval time =", mean_interval_time)

        print("\nThe mean system delay is:", mean_system_delay)
        print()

        return mean_system_delay
