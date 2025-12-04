from Connections import HostConnection

host = HostConnection(8168)
print('made host')

host.discovery_broadcast()
print('host finish broadcasting')

tempDict = host.receive()
print('host received something')

print(f'host received {tempDict['messageType']}')
print(f'host received from {tempDict['from']}')
print(f'with sequence number {tempDict['sequence_number']}')