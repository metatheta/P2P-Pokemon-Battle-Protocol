# This'll be the framework for the program entry point
from Connections import HostConnection

HOST_PORT = 9392

# open game UI on HOST_PORT and chat UI the next port
chat_host_connection = HostConnection(HOST_PORT+1)

# TODO open chat host subprocess using this connection



