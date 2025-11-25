import socket

# made a class to handle the networking stuff
class Transport:
    sequenceNumber = 0
    ip = "127.0.0.1"
    bytesToRead = 4096

    # it takes port numbers as parameters 
    # it should make the socket and bind to the 
    # socket on creation
    def __init__(self, yourPort, theirPort):
        self.yourPort = yourPort
        self.theirPort = theirPort
        self.yourSocket = self.makeSocket()
        self.bind()
        
    def makeSocket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def bind(self):
        self.yourSocket.bind((Transport.ip, self.yourPort))

    # this is a method that should be called when making
    # the message, it updates the sequence number and
    # returns the sequence number to use
    def useNewSequenceNumber(self):
        Transport.sequenceNumber += 1
        return Transport.sequenceNumber
    
    # it has a method to send messages, having the
    # string representation of the message as parameter
    def send(self, message: str):
        self.yourSocket.sendto(message.encode(), (Transport.ip, self.theirPort))

    # it can also receive messages and pass the contents
    # of the message as a string
    def receive(self):
        bytesReceived, senderInfo = self.yourSocket.recvfrom(Transport.bytesToRead)
        content = bytesReceived.decode()
        return content

    # we also have a method to call .close() at the end
    # of the program
    def close(self):
        self.yourSocket.close()

        