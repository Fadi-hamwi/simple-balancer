import docker.types


NETWORK_NAME = 'testing'   # you can change it however you like default is 'testing'
client = docker.from_env()
ipam_pool = docker.types.IPAMPool(
    subnet='192.168.100.0/24',
    gateway='192.168.100.1'
)
ipam_config = docker.types.IPAMConfig(
    pool_configs=[ipam_pool]
)


def create_docker_network(network_name="testing", custom_ipam=ipam_config):
    """
    Create a docker network with the name `NETWORK_NAME`.
    First it checks if this network exists and if it doesn't
    it creates a new one.
    :return:
    A network object in both cases whether it's already exist or not.
    for more information about network objects refer to this link:
    https://docker-py.readthedocs.io/en/stable/networks.html#network-objects
    """
    if custom_ipam is None:
        custom_ipam = ipam_config
    try:
        if client.networks.get(network_name):
            print(f"\033[91;1mA Docker network with specified name:'{network_name}' is already exists.\033[0m")
    except Exception as e:
        print(f"\033[92;1mCreating the docker network with the name {network_name}\033[0m")
        client.networks.create(network_name, ipam=custom_ipam)
        NETWORK_NAME = network_name
    return client.networks.get(network_name)


def join(network):
    """
    Join the current running containers to the network specified in the param list.
    :param network: a network object if you're interested about them see this link:
    https://docker-py.readthedocs.io/en/stable/networks.html#network-objects

    :return: Number of newly connected containers to the network.
    """
    containers = client.containers
    network = client.networks.get(NETWORK_NAME)
    connected_containers = 0
    for container in containers.list():
        if container not in network.containers:
            connected_containers += 1
            network.connect(container)
    return connected_containers


def disconnect(network):
    """
    Disconnect all the containers connected to the specified network.
    we loop over the 'network.containers' not the client.containers.list()
    because it may raise an exception.
    :param network:
    :return: Number of the disconnected containers from the network
    """
    disconnected_containers = 0
    for container in network.containers:
        disconnected_containers += 1
        network.disconnect(container)
    return disconnected_containers


def del_network(network):
    network.remove()  # removes this network once empty
    print(f"\033[91;1mDocker Network '{NETWORK_NAME}' has been deleted successfully.\033[0m")


def up_containers():
    containers = client.containers.list({all: True})
    for container in containers:
        if container.attrs['Name'].startswith('/http-server'):
            if container.status != 'running':
                try:
                    container.start()
                except:
                    print("Failed to up container")


def down_containers():
    containers = client.containers.list()
    for container in containers:
        if container.attrs['Name'].startswith('/http-server'):
            container.kill()


if __name__ == '__main__':
    # down_containers()
    up_containers()
    networkTest = create_docker_network()
    # down_containers()
    print(join(networkTest))
    # del_network(networkTest)

