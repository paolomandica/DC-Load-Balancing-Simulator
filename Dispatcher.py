import random
import math
import simulation_utils as su
from numpy.random import weibull
import matplotlib.pyplot as plt


class Dispatcher:

    random.seed(1234)

    q = 3/5
    y = 10
    t_0 = 1
    alpha = 0.5
    t = 1000*t_0

    def __init__(self, number_of_tasks: int,
                 number_of_servers: int,
                 rho: float, d: int,
                 jbt=False, custom=False):
        self.number_of_tasks = number_of_tasks
        self.number_of_servers = number_of_servers
        self.servers = {i: [0] for i in range(number_of_servers)}
        self.rho = rho
        self.d = d
        self.tasks_timeline = []
        self.system_times = []
        self.beta = self.compute_beta(self.rho)
        self.interval_times = []
        self.process_times = []
        self.overhead = 0
        self.jbt = jbt
        self.custom = custom
        self.rs = []

    def get_tasks_timeline(self):
        return self.tasks_timeline

    def get_servers(self):
        return self.servers

    def get_system_times(self):
        return self.system_times

    def compute_beta(self, rho):
        exp_t = self.t_0 + (1 - self.q)*self.y
        den = math.factorial(1/self.alpha)
        beta = rho*self.number_of_servers*exp_t/den
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
            self.tasks_timeline.append(round(prev))

    def pick_random_servers(self, server_ids, n_servers):
        ids = random.sample(server_ids, n_servers)
        return ids

    def get_queue_len(self, server_id, time):
        count = 0
        tasks = self.servers[server_id]
        for task in tasks:
            if task > time:
                count += 1
            else:
                self.servers[server_id].remove(task)
            if len(tasks) == 0:
                self.servers[server_id].append(0)
        return count

    def pick_best_server(self, server_ids, n_servers, time):
        servers_ids = self.pick_random_servers(server_ids, n_servers)

        best_server = servers_ids[0]

        min_n_tasks = self.get_queue_len(servers_ids[0], time)

        for id in servers_ids[1:]:
            current_n_tasks = self.get_queue_len(id, time)
            if current_n_tasks < min_n_tasks:
                min_n_tasks = current_n_tasks
                best_server = id

        return best_server

    def pick_best_server_custom(self, server_ids, n_servers, time):
        servers_ids = self.pick_random_servers(server_ids, n_servers)

        best_server = servers_ids[0]
        min_finish_time = self.servers[best_server][-1]

        for id in server_ids[1:]:
            cur_finish_time = self.servers[id][-1]
            if cur_finish_time < min_finish_time:
                min_finish_time = cur_finish_time
                best_server = id

        return best_server

    def generate_task(self):
        r3 = random.uniform(0, 1)
        task = max(1, min(100*self.beta*2,
                          round(self.beta*(-math.log(r3))**(1/self.alpha))))
        return task

    def assign_task(self, time, server_id, task=None):
        if task == None:
            task = self.generate_task()

        self.process_times.append(task)
        try:
            server_time = self.servers[server_id][-1]
        except:
            server_time = 0

        if server_time > time:
            task_finish_time = server_time + task
        else:
            task_finish_time = time + task
        self.servers[server_id].append(task_finish_time)

        system_time = task_finish_time - time
        self.system_times.append(system_time)

    def process_tasks_jbt(self):
        t_units = 0
        threshold = float("+inf")
        servers_below_threshold = []

        for time in self.tasks_timeline:
            # if t units of time passed, update the threshold,
            # update the list of servers below threshold
            # and use the server with lower threshold to assign the task
            if time > t_units:
                server_id = self.pick_best_server(
                    self.servers.keys(), self.d, time)
                self.overhead += 2*self.d
                threshold = max(
                    1, self.get_queue_len(server_id, time))
                self.overhead += self.number_of_servers
                sbt_temp = []
                # search for all the servers below threshold
                for id in self.servers:
                    queue_len = self.get_queue_len(id, time)
                    if queue_len < threshold:
                        sbt_temp.append(id)
                diff = len(set(sbt_temp).difference(
                    set(servers_below_threshold)))
                self.overhead += diff
                t_units += self.t
                self.rs.append(threshold)

            # else, choose a random server from the ones below threshold
            # or eventually from all the servers and assign the task
            else:
                if len(servers_below_threshold) > 0:
                    server_id = random.sample(servers_below_threshold, 1)[0]
                    servers_below_threshold.remove(server_id)
                else:
                    server_id = random.sample(list(self.servers.keys()), 1)[0]

            self.assign_task(time, server_id)

            for id in self.servers:
                if id not in servers_below_threshold:
                    n_tasks = self.get_queue_len(id, time)
                    if n_tasks < threshold:
                        servers_below_threshold.append(id)
                        self.overhead += 1

        self.overhead /= self.number_of_tasks

    def process_custom(self):
        servers = list(self.servers.keys())

        sl = (-math.exp(0.2)*(self.beta**self.alpha))**(1/self.alpha)
        sm1 = (-math.exp(0.4)*(self.beta**self.alpha))**(1/self.alpha)
        sm2 = (-math.exp(0.5)*(self.beta**self.alpha))**(1/self.alpha)
        su = (-math.exp(0.7)*(self.beta**self.alpha))**(1/self.alpha)

        for time in self.tasks_timeline:
            task = self.generate_task()
            if task < sl:
                n_servers = len(servers)//4
                server = self.pick_best_server_custom(servers, n_servers, time)
            elif task >= sl and task < sm1:
                n_servers = len(servers)//2
                server = self.pick_best_server_custom(servers, n_servers, time)
            elif task >= sm1 and task < sm2:
                n_servers = int(len(servers)/1.3)
                server = self.pick_best_server_custom(servers, n_servers, time)
            else:
                n_servers = len(servers)
                server = self.pick_best_server_custom(
                    servers, len(servers), time)

            self.overhead += n_servers*2
            self.assign_task(time, server, task)

        self.overhead /= self.number_of_tasks

    def compute_overhead(self):
        self.overhead = 2*self.d

    def print_results(self, process_time_exp, mean_process_time,
                      interval_time_exp, mean_interval_time,
                      empirical_rho, mean_system_time):
        message = "\nCompleted! rho = " + str(round(self.rho, 2)) + "\n" + \
            "Beta = " + str(self.beta) + "\n" + \
            "E[X] = " + str(round(process_time_exp, 2)) + " --> " + \
            "Mean process time = " + str(round(mean_process_time, 4)) + "\n" + \
            "E[T] = " + str(round(interval_time_exp, 2)) + " --> " + \
            "Mean interval time = " + str(round(mean_interval_time, 4)) + "\n" + \
            "Rho = " + str(round(self.rho, 2)) + " --> " + \
            "Empirical Rho = " + str(round(empirical_rho, 4)) + "\n" + \
            "Mean system time = " + str(round(mean_system_time)) + "\n"

        print(message)

    def execute_simulation(self):
        print()
        print("Starting simulation for rho = " + str(self.rho))
        print()

        self.generate_tasks_timeline(self.number_of_tasks)

        if self.jbt:
            self.process_tasks_jbt()

        elif self.custom:
            self.process_custom()

        else:
            for time in self.tasks_timeline:
                server_id = self.pick_best_server(
                    list(self.servers.keys()), self.d, time)
                self.assign_task(time, server_id)
            self.compute_overhead()

        to_remove = int(self.number_of_tasks*0.1)
        mean_system_time = sum(
            self.system_times[to_remove:])/(self.number_of_tasks-to_remove)

        process_time_exp = su.compute_process_time_exp(self.beta, self.alpha)
        interval_time_exp = su.compute_interval_time_exp(
            self.t_0, self.q, self.y)

        mean_process_time = sum(self.process_times)/len(self.process_times)
        mean_interval_time = sum(self.interval_times)/len(self.interval_times)
        empirical_rho = mean_process_time / \
            (self.number_of_servers*mean_interval_time)

        self.print_results(process_time_exp, mean_process_time,
                           interval_time_exp, mean_interval_time,
                           empirical_rho, mean_system_time)

        # if self.jbt and (self.rho > 0.989):
        #     plt.plot(range(len(self.rs)), self.rs)
        #     plt.show()
        print("PROCESS TIMES = ", self.process_times)

        return mean_system_time, self.overhead
