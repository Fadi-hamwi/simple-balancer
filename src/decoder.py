import socket
import struct
import sys

import roundrobin
import time
from server import *
import docker
from concurrent.futures import ThreadPoolExecutor
import threading


def calculate_fcs(data):
    fcs = 0xffff  # Initial FCS value
    for byte in data:
        fcs ^= byte
        for _ in range(8):
            if fcs & 0x0001:
                fcs = (fcs >> 1) ^ 0x8408
            else:
                fcs >>= 1
    # Convert FCS to bytes in little-endian order
    fcs_bytes = fcs.to_bytes(2, byteorder='little')
    return fcs_bytes


def decode_packet(packet):
    eth_header = packet[:14]  # Ethernet header is 14 bytes
    eth_fields = struct.unpack("!6s6sH", eth_header)
    source_mac = eth_fields[0].hex()
    dest_mac = eth_fields[1].hex()

    # Determine packet type
    if eth_fields[2] == 0x0800:  # IP
        # print(f"Received an IP packet from {source_mac} to {dest_mac}")
        # Choose the next server based on round-robin algorithm
        current_server = load_balancer.get_next_server()
        if current_server is None:
            return  # No available server, skip processing

        # # Modify the MAC addresses in the Ethernet header
        # dest_mac_modified = current_server['MAC'].replace(':', '').encode()
        # source_mac_str = source_mac.replace(':', '').decode()  # Convert bytes to string
        # dest_mac_modified_str = dest_mac_modified.decode()  # Convert bytes to string
        #
        # try:
        #     eth_header_modified = struct.pack("!6s6sH", bytes.fromhex(source_mac_str),
        #                                       bytes.fromhex(dest_mac_modified_str),
        #                                       eth_fields[2])
        # except Exception as e:
        #     print(f"\033[91;1mException occurred during struct.pack: {e}\033[0m")

        # Craft the modified packet by replacing the Ethernet header
        # modified_packet = eth_header_modified + packet[14:]
        modified_packet = packet
        # Send the modified packet to the appropriate server
        try:
            # Get the IP address of the target container using its name
            target_container = docker_client.containers.get(current_server['Name'])
            target_ip = target_container.attrs['NetworkSettings']['IPAddress']
            # Forward the packet using UDP socket
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.sendto(modified_packet,
                              (target_ip, int(target_container.attrs['HostConfig']['PortBindings']['8080'
                                                                                                   '/tcp'][0][
                                                  'HostPort'])))
            udp_socket.close()
            print(f"\033[93;1mModified packet sent to container {current_server['Name']} at IP {target_ip}\033[0m")
        except Exception as e:
            print(f"\033[91;1mFailed to send packet to container {current_server['Name']}: {e}\033[0m")


def monitor_docker_containers():
    while True:
        time.sleep(60)
        load_balancer.servers = get_server_lst()


# Main function to handle packet decoding and Docker monitoring
def main():
    while True:
        packet, _ = raw_socket.recvfrom(BUFFER_SIZE)  # Adjust buffer size as needed
        executor.submit(decode_packet, packet)


if __name__ == "__main__":
    load_balancer = roundrobin.RoundRobinLoadBalancer()
    BUFFER_SIZE = 2 ** 16
    ETH_P_ALL = 3
    HOME = os.getenv("HOME")
    os.environ["SERVER_LST"] = f"{HOME}/server_lst.txt"
    docker_client = docker.from_env()
    # Create a thread pool for decoding packets
    executor = ThreadPoolExecutor(max_workers=10)
    # Start the Docker monitoring thread
    docker_monitor_thread = threading.Thread(target=monitor_docker_containers).start()

    # Create a raw socket for capturing packets
    raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
    main()
