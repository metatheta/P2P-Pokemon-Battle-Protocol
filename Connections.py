from Messages import DiscoveryBroadcast
import socket

from Messages import Message, Acknowledgement


# Pseudo-connection through UDP
# Wrapper around the raw UDP socket to provide high-level
# read and send methods that have built-in reliability features
# It no longer stores an address of its peers directly
# so that the functionality can be unique per subclass
class LogicalConnection:
    read_length = 4096
    BROADCAST_IP = "255.255.255.255"
    BROADCAST_PORT = 7777
    LOCAL_BIND_IP = "0.0.0.0"
    MAX_RETRANSMITS = 3

    def __init__(self, port_number, verbose_flag):
        self.port_number = port_number
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((LogicalConnection.LOCAL_BIND_IP, self.port_number))
        self.retransmission_counter = 0
        self.sequenceNumber = 0
        self.verbose_flag = verbose_flag

    def __send__(self, message: str, addr: tuple[str, int]) -> bool:
        self.socket.settimeout(0.5)  # Wait 500 ms for the ACK
        while True:
            try:
                self.log(f"Attempt to send to {addr}")
                self.socket.sendto(message.encode(), addr)
                data, addr = self.socket.recvfrom(LogicalConnection.read_length)
                response_str = data.decode()
                response_fields = Message.from_message_format(response_str)

                if (
                    response_fields.get("message_type") == "ACKNOWLEDGEMENT"
                    and int(response_fields.get("ack_number")) == self.sequenceNumber
                ):
                    # ACK matches the sent message num = the message was successfully sent
                    self.sequenceNumber += 1
                    self.socket.settimeout(None)
                    self.retransmission_counter = 0
                    self.log("Message successfully sent")
                    return True
            except socket.timeout:
                if self.retransmission_counter < self.MAX_RETRANSMITS:
                    print(f"Timed out, resending")
                    self.retransmission_counter += 1
                else:
                    print(f"Max retransmits reached, failed to receive ACK")
                    return False
            except Exception as e:
                print(f"Exception: {e}")
                return False

    def receive(self) -> dict | None:
        while True:
            try:
                data, addr = self.socket.recvfrom(LogicalConnection.read_length)
                received_str = data.decode()
                received = Message.from_message_format(received_str)

                if received.get("message_type") == "ACKNOWLEDGEMENT":
                    continue  # Skip ACKs

                if int(received.get("sequence_number")) == self.sequenceNumber:
                    self.send_ack(addr)
                    self.sequenceNumber += 1
                    self.log("Matching ACK received")
                    return received

            except Exception as e:
                print(f"Exception: {e}")

    def send_ack(self, addr: tuple[str, int]):
        ack = Acknowledgement(self.sequenceNumber)
        self.socket.sendto(ack.to_message_format().encode(), addr)

    def close(self):
        self.socket.close()

    def log(self, message: str):
        if self.verbose_flag:
            print(message)


class HostConnection(LogicalConnection):
    def __init__(self, port_number):
        super().__init__(port_number)
        self.connected_peers = []
        # The host will act as the central server, storing connections to all the peers in a list
        # Joiners/Spectators never interact directly with each other and use the host as a proxy

    def discovery_broadcast(self):
        temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # make temp broadcasting socket

        broadcast_addr = (
            LogicalConnection.BROADCAST_IP,
            LogicalConnection.BROADCAST_PORT,
        )
        message = DiscoveryBroadcast(self.port_number).to_message_format()
        temp.sendto(message.encode(), broadcast_addr)
        self.log(f"Broadcasted using temp socket {temp.getsockname()}")
        # broadcast main socket details

        self.socket.settimeout(5)  # Wait 5 seconds for all joiners to connect
        while True:
            try:
                data, addr = self.socket.recvfrom(LogicalConnection.read_length)
                # Receive connections from the main socket

                if addr not in self.connected_peers:
                    self.connected_peers.append(addr)
                    self.log(f"New peer from {addr} connected")
                # The actual content of the messages they send doesn't seem to be relevant
                # however we can add it later if the acknowledgement needs to be used in some way
            except socket.timeout:
                self.log("Timeout reached, no peers can connect now")
                # So the socket times out if recv doesn't complete in 5 seconds
                break

        temp.close()

# I have no idea what to name it cause "joiner" should refer specifically to
# the other battler and not also spectators, so imma call this a Peer connection
# It's basically any connection that's not the host, having the choice to become
# a spectator or joiner
class PeerConnection(LogicalConnection):
    def __init__(self, port_number):
        super().__init__(port_number)
        self.host_addr = None

    def wait_for_broadcast(self) -> bool:
        # make a temp socket that will be used for listening to the broadcast
        broadcast_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_receiver.bind(
            (LogicalConnection.LOCAL_BIND_IP, LogicalConnection.BROADCAST_PORT)
        )

        while True:
            print("Joiner waiting for host broadcast")
            data, host_temp_addr = broadcast_receiver.recvfrom(
                LogicalConnection.read_length
            )
            content = data.decode()
            tempDict = Message.from_message_format(content)
            self.host_addr = (host_temp_addr[0], int(tempDict.get("host_port")))

            if "BROADCAST" == tempDict.get("message_type"):
                self.send_ack()
                self.log(f"Sent ACK to {self.host_addr}")
                broadcast_receiver.close()
                return True

    def send(self, message: str):
        super().__send__(message, self.host_addr)

    def send_ack(self):
        super().send_ack(self.host_addr)

    # Now the joiner peer only sends to the host it has recognized