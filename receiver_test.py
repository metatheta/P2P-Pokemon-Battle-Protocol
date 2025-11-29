from Transport import Transport

port = 8492
transport = Transport(port)
print(f"Initialized on port {port} with IP {transport.yourSocket.getsockname()}")

msg = transport.receive()
print(msg)
