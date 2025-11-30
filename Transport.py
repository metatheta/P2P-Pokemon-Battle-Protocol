import socket

from Messages import Message, Acknowledgement


# made a class to handle the networking stuff
class Transport:
    bytesToRead = 4096
    broadcastIP = "255.255.255.255"
    broadcastPort = 8618
    localBindIP = "0.0.0.0"
    MAX_RETRANSMITS = 3

    # it takes port numbers as parameters
    # it should make the socket and bind to the
    # socket on creation
    def __init__(self, yourPortNumber):
        self.yourPortNumber = yourPortNumber
        self.yourSocket = self.make_socket()
        self.bind()
        self.senderInfo = None
        self.retransmission_counter = 0
        self.sequenceNumber = 0

    def make_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def bind(self):
        self.yourSocket.bind((Transport.localBindIP, self.yourPortNumber))

    # it has a method to send messages, having the
    # string representation of the message as parameter
    # also returns the success value of the sending
    # NOTE: receive gotta be called or senderInfo set separately
    # before this message can be used
    def send_to_peer(self, message: str) -> bool:
        self.yourSocket.settimeout(0.5)  # Wait 500 ms for the ACK
        while True:
            try:
                print(f"Attempt to send to {self.senderInfo}")
                self.yourSocket.sendto(message.encode(), self.senderInfo)
                data, addr = self.yourSocket.recvfrom(Transport.bytesToRead)
                response_str = data.decode()
                response_fields = Message.from_message_format(response_str)

                if (
                    response_fields.get("message_type") == "ACKNOWLEDGEMENT"
                    and int(response_fields.get("ack_number")) == self.sequenceNumber
                ):
                    # ACK matches the sent message num = the message was successfully sent
                    self.sequenceNumber += 1
                    self.yourSocket.settimeout(None)
                    self.retransmission_counter = 0
                    print("Message successfully sent")
                    return True
            except socket.timeout:
                if self.retransmission_counter < self.MAX_RETRANSMITS:
                    print("Timed out, resending")
                    self.retransmission_counter += 1
                else:
                    return False
            except Exception as e:
                print(f"Exception: {e}")
                return False

    # it can also receive messages and return the message fields dict
    def receive(self) -> dict | None:
        while True:
            try:
                data, addr = self.yourSocket.recvfrom(Transport.bytesToRead)
                self.senderInfo = addr
                received_str = data.decode()
                received = Message.from_message_format(received_str)

                if received.get("message_type") == "ACKNOWLEDGEMENT":
                    continue  # Skip ACKs

                if int(received.get("sequence_number")) == self.sequenceNumber:
                    self.send_ack()
                    self.sequenceNumber += 1
                    print("Matching ACK received")
                    return received

            except Exception as e:
                print(f"Exception: {e}")
                

    # a method for sending ACKs
    def send_ack(self):
        ack = Acknowledgement(ack_number=self.sequenceNumber)
        self.yourSocket.sendto(ack.to_message_format().encode(), self.senderInfo)

    # we also have a method to call .close() at the end
    # of the program
    def close(self):
        self.yourSocket.close()


class HostTransport(Transport):
    def __init__(self, yourPortNumber):
        super().__init__(yourPortNumber)

    # method that allows the Host to initiate a game
    # by broadcasting
    def broadcast(self):
        temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        temp.sendto(
            "message_type: BROADCAST".encode(),
            (Transport.broadcastIP, Transport.broadcastPort),
        )
        temp.close()


class JoinerTransport(Transport):
    def __init__(self, yourPortNumber):
        super().__init__(yourPortNumber)

    # a function that makes a temporary socket that we bind
    # to the broadcastIP and agreed upon broadcast port
    # returns true if we receive a broadcast
    def wait_for_broadcast(self) -> bool:
        broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcastSocket.bind((Transport.localBindIP, Transport.broadcastPort))

        while True:
            bits, self.senderInfo = broadcastSocket.recvfrom(Transport.bytesToRead)
            content = bits.decode()

            if "BROADCAST" in content:
                broadcastSocket.close()
                return True


class SpectatorTransport(Transport):
    spectatorIP = Transport.localBindIP
    spectatorPort = Transport.broadcastPort

    def __init__(self, yourPortNumber):
        super().__init__(yourPortNumber)

    # Much like the JoinerTransport but it keeps on listening
    # to the broadcast socket
    # Note: I haven't figured out how to close the socket yet
    def spectate(self) -> bool:
        spectatorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        spectatorSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        spectatorSocket.bind((self.spectatorIP, self.spectatorPort))

        while True:
            bits, self.senderInfo = spectatorSocket.recvfrom(Transport.bytesToRead)
            content = bits.decode()

            if "BROADCAST" in content:
                return True
