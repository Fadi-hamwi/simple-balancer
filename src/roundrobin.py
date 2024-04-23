import docker

from server import update_server_lst


class RoundRobinLoadBalancer:
    def __init__(self):
        self.servers = update_server_lst()
        self.current_index = 0
        self.ips = [server['IP'] for server in self.servers]

    def get_next_server(self):
        if not self.servers:
            return None

        next_server = self.servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.servers)
        return next_server


if __name__ == '__main__':
    load_balancer = RoundRobinLoadBalancer()
    # dockerize.join()
    client = docker.from_env()
    print(load_balancer.ips)
