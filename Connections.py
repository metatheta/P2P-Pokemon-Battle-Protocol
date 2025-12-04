from Messages import DiscoveryBroadcast
import socket
from Messages import Message, Acknowledgement


class LogicalConnection:
    read_length = 4096
    BROADCAST_IP = "255.255.255.255"
    BROADCAST_PORT = 7777
    LOCAL_BIND_IP = "0.0.0.0"
    MAX_RETRANSMITS = 3

    def __init__(self, port_number, verbose_flag=False):
        self.port_number = port_number
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((LogicalConnection.LOCAL_BIND_IP, self.port_number))
        self.retransmission_counter = 0
        self.send_sequence_number = 0
        self.receive_sequence_number = 0
        self.verbose_flag = verbose_flag

    def __send__(self, message: str, addr: tuple[str, int]) -> bool:
        # Try to extract sequence number from message to know what ACK to expect
        try:
            msg_fields = Message.from_message_format(message)
            expected_ack = int(msg_fields.get("sequence_number"))
        except (ValueError, TypeError):
            # Fallback for messages without sequence number (if any)
            expected_ack = self.send_sequence_number

        self.socket.settimeout(0.5)
        while True:
            try:
                self.log(f"Attempt to send to {addr}")
                self.socket.sendto(message.encode(), addr)

                # Wait for ACK
                while True:
                    try:
                        data, response_addr = self.socket.recvfrom(
                            LogicalConnection.read_length
                        )
                        response_str = data.decode()
                        response_fields = Message.from_message_format(response_str)

                        if (
                            response_fields.get("message_type") == "ACKNOWLEDGEMENT"
                            and int(response_fields.get("ack_number")) == expected_ack
                        ):
                            # Only increment internal counter if we were using it
                            if expected_ack == self.send_sequence_number:
                                self.send_sequence_number += 1
                            self.socket.settimeout(None)
                            self.retransmission_counter = 0
                            self.log("Message successfully sent")
                            self.delimited_message(response_str)
                            return True
                    except socket.timeout:
                        raise # Re-raise to trigger retransmission logic
                    except Exception:
                        # Ignore malformed packets or other errors while waiting for ACK
                        continue

            except socket.timeout:
                if self.retransmission_counter < self.MAX_RETRANSMITS:
                    self.log("Timed out, resending")
                    self.retransmission_counter += 1
                else:
                    self.socket.settimeout(None)
                    self.retransmission_counter = 0
                    self.log(f"Max retransmits reached, failed to receive ACK")
                    return False
            except Exception:
                self.socket.settimeout(None)
                return False

    def receive(self) -> dict | None:
        while True:
            try:
                data, addr = self.socket.recvfrom(LogicalConnection.read_length)
                received_str = data.decode()
                received = Message.from_message_format(received_str)

                if received.get("message_type") == "ACKNOWLEDGEMENT":
                    continue

                if int(received.get("sequence_number")) == self.receive_sequence_number:
                    self.send_ack(addr, self.receive_sequence_number)
                    self.receive_sequence_number += 1
                    self.log("Matching ACK received")
                    return received
                elif (
                    int(received.get("sequence_number")) < self.receive_sequence_number
                ):
                    # Duplicate packet, resend ACK
                    self.log(
                        f"Duplicate packet {received.get('sequence_number')} received, resending ACK"
                    )
                    self.send_ack(addr, int(received.get("sequence_number")))
                    continue

            except Exception:
                pass

    def send_ack(self, addr, ack_num):
        ack = Acknowledgement(ack_num)
        self.socket.sendto(ack.to_message_format().encode(), addr)

    def send_fragment(self, message: str):
        """Send a sticker fragment - fire and forget with proper sequence number."""
        # Parse message and update sequence number
        msg_fields = Message.from_message_format(message)
        msg_fields["sequence_number"] = str(self.send_sequence_number)

        # Rebuild message
        rebuilt_msg = ""
        for k, v in msg_fields.items():
            rebuilt_msg += f"{k}: {v}\n"

        # Send without waiting for ACK (fragments use their own reassembly)
        self.socket.sendto(rebuilt_msg.encode(), self.host_addr)
        self.send_sequence_number += 1

    def close(self):
        self.socket.close()

    ## Logs any error handling or reliability messages
    def log(self, message: str):
        if self.verbose_flag:
            print(message)

    def delimited_message(self, message: str):
        if self.verbose_flag:
            print("Message sent: ")
            lines = message.strip().splitlines()
            result = "{\n"

            for i, line in enumerate(lines):
                result += "\t" + line
                if i != len(lines) - 1:
                    result += ','
                result += '\n'
            result += "}"

            print(result)



class HostConnection(LogicalConnection):
    def __init__(self, port_number):
        super().__init__(port_number)
        self.connected_peers: dict[tuple[str, int], int] = {}
        self.message_buffer: list[tuple[dict, tuple[str, int]]] = []
        self.send_sequence_numbers: dict[
            tuple[str, int], int
        ] = {}  # Track send seq nums per peer

    def send(self, message: str, addr: tuple[str, int]) -> bool:
        """Send a message to a specific peer with proper sequence number tracking."""
        # Initialize sequence number for this peer if not exists
        if addr not in self.send_sequence_numbers:
            self.send_sequence_numbers[addr] = 0

        # Parse message and inject/update sequence number
        msg_fields = Message.from_message_format(message)
        msg_fields["sequence_number"] = str(self.send_sequence_numbers[addr])

        # Rebuild message
        rebuilt_msg = ""
        for k, v in msg_fields.items():
            rebuilt_msg += f"{k}: {v}\n"

        # Send using parent's __send__ which handles retransmission
        success = super().__send__(rebuilt_msg, addr)

        if success:
            self.send_sequence_numbers[addr] += 1

        return success

    def discovery_broadcast(self):
        temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        broadcast_addr = (
            LogicalConnection.BROADCAST_IP,
            LogicalConnection.BROADCAST_PORT,
        )
        message = DiscoveryBroadcast(self.port_number).to_message_format()
        temp.sendto(message.encode(), broadcast_addr)
        self.log(f"Broadcasted using temp socket {temp.getsockname()}")
        # broadcast main socket details

        self.socket.settimeout(3)
        while True:
            try:
                data, addr = self.socket.recvfrom(LogicalConnection.read_length)
                received_str = data.decode()
                received = Message.from_message_format(received_str)

                if received.get("message_type") == "ACKNOWLEDGEMENT":
                    self.connected_peers.setdefault(addr, 0)
                    self.log(f"New peer from {addr} connected")
                else:
                    # Non-ACK message arrived during discovery
                    # Send ACK immediately so sender doesn't timeout
                    if addr in self.connected_peers:
                        expected_seq = self.connected_peers[addr]
                        incoming_seq = int(received.get("sequence_number"))
                        if incoming_seq == expected_seq:
                            self.send_ack(addr, ack_num=incoming_seq)
                            self.log(
                                f"ACKed and buffering message during discovery: {received.get('message_type')}"
                            )
                            self.message_buffer.append((received, addr))
                            # Don't increment sequence number yet - that happens in receive()
                        elif incoming_seq < expected_seq:
                            # Duplicate, just ACK it
                            self.send_ack(addr, ack_num=incoming_seq)
                            self.log(
                                f"ACKed duplicate during discovery: seq {incoming_seq}"
                            )
                    else:
                        # Message from unknown peer, buffer it anyway
                        self.log(
                            f"Buffering message from unknown peer during discovery: {received.get('message_type')}"
                        )
                        self.message_buffer.append((received, addr))
            except socket.timeout:
                self.log("Timeout reached, no peers can connect now")
                break

        self.socket.settimeout(None)
        temp.close()

    def send_fragment_broadcast(self, message: str):
        """Broadcast a sticker fragment to all connected peers - fire and forget."""
        for peer_addr in list(self.connected_peers.keys()):
            # Initialize sequence number for this peer if not exists
            if peer_addr not in self.send_sequence_numbers:
                self.send_sequence_numbers[peer_addr] = 0

            # Parse message and inject sequence number for this specific peer
            msg_fields = Message.from_message_format(message)
            msg_fields["sequence_number"] = str(self.send_sequence_numbers[peer_addr])

            # Rebuild message
            rebuilt_msg = ""
            for k, v in msg_fields.items():
                rebuilt_msg += f"{k}: {v}\n"

            # Send without waiting for ACK (fragments use their own reassembly)
            self.socket.sendto(rebuilt_msg.encode(), peer_addr)
            self.send_sequence_numbers[peer_addr] += 1

    def receive(self) -> dict | None:
        # First, check if there are buffered messages from discovery
        if self.message_buffer:
            buffered_msg, buffered_addr = self.message_buffer.pop(0)
            print(f"Returning buffered message from {buffered_addr}")

            # Process the buffered message same as a fresh one
            if buffered_addr not in self.connected_peers:
                # Skip messages from unknown peers
                return self.receive()  # Recursively check next buffered or socket

            expected = self.connected_peers[buffered_addr]
            incoming = int(buffered_msg.get("sequence_number"))

            if incoming == expected:
                # Already ACKed during discovery, just increment and return
                self.connected_peers[buffered_addr] += 1
                return buffered_msg
            elif incoming < expected:
                # Duplicate packet (already processed)
                print(
                    f"Skipping duplicate buffered packet {incoming} from {buffered_addr}"
                )
                return self.receive()  # Recursively check next

        while True:
            try:
                data, addr = self.socket.recvfrom(LogicalConnection.read_length)
                received_str = data.decode()
                received = Message.from_message_format(received_str)

                if received.get("message_type") == "ACKNOWLEDGEMENT":
                    continue

                if addr not in self.connected_peers:
                    continue

                expected = self.connected_peers[addr]
                incoming = int(received.get("sequence_number"))

                if incoming == expected:
                    self.send_ack(addr, ack_num=incoming)
                    self.connected_peers[addr] += 1
                    return received
                elif incoming < expected:
                    # Duplicate packet, resend ACK
                    print(
                        f"Duplicate packet {incoming} received from {addr}, resending ACK"
                    )
                    self.send_ack(addr, ack_num=incoming)
                    continue

            except Exception:
                pass


class PeerConnection(LogicalConnection):
    def __init__(self, port_number):
        super().__init__(port_number)
        self.host_addr = None

    def wait_for_broadcast(self) -> bool:
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
                self.send_ack(0)
                self.log(f"Sent ACK to {self.host_addr}")
                broadcast_receiver.close()
                return True

    def send(self, message: str):
        return super().__send__(message, self.host_addr)

    def send_ack(self, addr_or_ack_num, ack_num=None):
        if ack_num is None:
            ack_num = addr_or_ack_num
        super().send_ack(self.host_addr, ack_num)


# TODO add verbose mode flag to make most of this logging optional
