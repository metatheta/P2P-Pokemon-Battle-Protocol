# broadcast and show list of active joiners
from Connections import HostConnection

host = HostConnection(9281)
host.discovery_broadcast()

print(f"Broadcast done, list of peers: {host.connected_peers}")