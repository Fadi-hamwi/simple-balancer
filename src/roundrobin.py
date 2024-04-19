from server import get_server_lst


class RoundRobinLoadBalancer:
    def __init__(self):
        self.servers = get_server_lst()
        self.current_index = 0

    def get_next_server(self):
        if not self.servers:
            return None

        next_server = self.servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.servers)
        return next_server
