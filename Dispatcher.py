class Dispatcher:

    tasks_timeline = []
    system_times = []

    def __init__(self, number_of_tasks,
                 number_of_servers):
        self.number_of_tasks = number_of_tasks
        self.number_of_servers = number_of_servers
        self.servers = {i: 0 for i in range(number_of_servers)}

    def generate_tasks(self, number_of_tasks):
        pass

    def pick_random_servers(self, d):
        pass

    def pick_best_server(self, servers):
        pass

    def assign_task(self, server):
        pass
