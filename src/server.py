import os
import docker


def get_server_lst():
    servers = []
    try:
        client = docker.from_env()
        for container in client.containers.list():
            container_attrs = container.attrs
            container_name = container_attrs['Name'].lstrip('/')  # Remove leading '/' from container name
            ip_address = container_attrs['NetworkSettings']['IPAddress']
            mac_address = container_attrs['NetworkSettings']['MacAddress']
            port_mapping = container_attrs['HostConfig']['PortBindings'] if 'PortBindings' in container_attrs[
                'HostConfig'] else {}
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
    os.environ["SERVER_LST"] = '/home/conehead/server_lst.txt'
    print(get_server_lst())
