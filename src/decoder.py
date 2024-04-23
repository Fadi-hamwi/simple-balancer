from scapy.all import sniff, sendp, send
from scapy.layers.l2 import Ether
from scapy.layers.inet import TCP, IP
import roundrobin
import time
from server import *
import docker
from concurrent.futures import ThreadPoolExecutor
import threading
import dockerize


def decode_packet(packet):
    # Choose the next server based on round-robin algorithm
    current_server = load_balancer.get_next_server()
    # for ip in load_balancer.ips:
    #     if ip != packet[IP].dst:
    #         return

    if current_server is None:
        return  # No available server, skip processing or dest ip does not match

    # Modify the MAC addresses in the Ethernet header
    packet[Ether].dst = current_server['MAC']
    packet[IP].dst = current_server['IP']
    # Send the modified packet to the appropriate server
    sendp(packet)
    print(f"\033[93;1mModified packet sent to container {current_server['Name']} at IP {current_server['MAC']}\033[0m")


def monitor_docker_containers():
    while True:
        time.sleep(60)
        load_balancer.servers = update_server_lst()


def sniff_helper():
    sniff(prn=decode_packet, filter='ip', store=0)


def main():
    executor.submit(sniff_helper)
    # sniff_helper()


if __name__ == "__main__":
    docker_client = docker.from_env()
    dockerize.up_containers()
    network = dockerize.create_docker_network()  # you could pass a name for the network default is 'testing'
    dockerize.join(network)
    load_balancer = roundrobin.RoundRobinLoadBalancer()
    # Create a thread pool for decoding packets
    executor = ThreadPoolExecutor(max_workers=5)
    # Start the Docker monitoring thread
    # docker_monitor_thread = threading.Thread(target=monitor_docker_containers, daemon=True).start()
    # Start executing main
    main()
