from Messages import HandshakeRequest
from Transport import Transport
port = 8329
transport = Transport(port)
print(f"Initialized on port {port} with IP {transport.yourSocket.getsockname()}")

transport.senderInfo = ("127.0.0.1", 8492)
msg = HandshakeRequest(transport.sequenceNumber)
transport.send_to_peer(msg.to_message_format())