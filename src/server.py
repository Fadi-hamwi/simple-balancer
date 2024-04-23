import dockerize
import docker

client = docker.from_env()


def update_server_lst():
    servers = []
    network = client.networks.get(dockerize.NETWORK_NAME)
    try:
        """ we only lookup the containers connected to the network 
        because not all containers are web servers and we know for a fact 
        that all the containers connected the network are web servers.
        """
        for container in network.containers:
            container_attrs = container.attrs
            container_name = container_attrs['Name'].lstrip('/')  # Remove leading '/' from container name
            ip_address = container_attrs['NetworkSettings']['Networks'][dockerize.NETWORK_NAME]['IPAddress']
            mac_address = container_attrs['NetworkSettings']['Networks'][dockerize.NETWORK_NAME]['MacAddress']
            port_mapping = container_attrs['NetworkSettings']['Ports']
            # Construct server dictionary
            server_info = {
                'Name': container_name,
                'IP': ip_address,
                'MAC': mac_address,
                'PortMappings': port_mapping
            }
            servers.append(server_info)
        print("\033[92;1mReceived the latest update of the server list\033[0m")
    except Exception as e:
        print(f"\033[91;1mERROR: Failed to retrieve server list: {e}\033[0m")
    return servers


if __name__ == "__main__":
    client = docker.from_env()
    print(update_server_lst())
