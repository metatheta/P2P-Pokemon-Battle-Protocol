import socket

# made a class to handle the networking stuff
class Transport:
    sequenceNumber = 0
    bytesToRead = 4096
    broadcastIP = "255.255.255.255"
    broadcastPort = 8618
    localBindIP = "0.0.0.0"

    # it takes port numbers as parameters 
    # it should make the socket and bind to the 
    # socket on creation
    def __init__(self, yourPortNumber):
        self.yourPortNumber = yourPortNumber
        self.yourSocket = self.makeSocket()
        self.bind()
        self.senderInfo = None

    def make_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def bind(self):
        self.yourSocket.bind((Transport.localBindIP, self.yourPortNumber))

    # this is a method that should be called when making
    # the message, it updates the sequence number and
    # returns the sequence number to use
    def update_and_get_sequence_number(self):
        Transport.sequenceNumber += 1
        return Transport.sequenceNumber
    
    # this is a method the should be called when comparing
    # the received message's sequence number to our record of sequence number
    # returns sequence number
    def get_sequence_number(self):
        return Transport.sequenceNumber
    
    # it has a method to send messages, having the
    # string representation of the message as parameter
    def send_to_peer(self, message: str):
        self.yourSocket.sendto(message.encode(), self.senderInfo)

    # it can also receive messages and pass the contents
    # of the message as a string
    def receive(self):
        bytesReceived, self.senderInfo = self.yourSocket.recvfrom(Transport.bytesToRead)
        content = bytesReceived.decode()
        return content

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
        temp.sendto("message_type: BROADCAST".encode(), (Transport.broadcastIP, Transport.broadcastPort))
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
