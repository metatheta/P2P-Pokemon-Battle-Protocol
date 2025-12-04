from Connections import PeerConnection

joiner  = PeerConnection(9279)
print('made joiner')

joiner.wait_for_broadcast()
print('joiner finished receiving broadcast')

message = f"""messageType: test
              from: {joiner.port_number}
              sequence_number: 1"""
joiner.send(message)
print('joiner sent message')

