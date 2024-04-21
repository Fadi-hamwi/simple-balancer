from scapy.all import sniff, sendp
from scapy.layers.l2 import Ether
import roundrobin
import time
from server import *
import docker
from concurrent.futures import ThreadPoolExecutor
import threading


def decode_packet(packet):
    # print(f"Received an IP packet from {source_mac} to {dest_mac}")
    # Choose the next server based on round-robin algorithm
    current_server = load_balancer.get_next_server()
    if current_server is None:
        return  # No available server, skip processing

    # Modify the MAC addresses in the Ethernet header
    packet[Ether].dst = current_server['MAC']
    target_ip = current_server['IP']
    # Send the modified packet to the appropriate server
    sendp(packet)
    print(f"\033[93;1mModified packet sent to container {current_server['Name']} at IP {target_ip}\033[0m")


def monitor_docker_containers():
    while True:
        time.sleep(60)
        load_balancer.servers = get_server_lst()


def sniff_helper():
    sniff(prn=decode_packet, filter='ip', store=0)


# Main function to handle packet decoding and Docker monitoring
def main():
    executor.submit(sniff_helper)


if __name__ == "__main__":
    load_balancer = roundrobin.RoundRobinLoadBalancer()
    docker_client = docker.from_env()
    # Create a thread pool for decoding packets
    executor = ThreadPoolExecutor(max_workers=10)
    # Start the Docker monitoring thread
    docker_monitor_thread = threading.Thread(target=monitor_docker_containers, daemon=True).start()
    # Start executing main
    main()
