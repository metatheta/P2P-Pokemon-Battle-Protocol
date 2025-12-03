import base64
import tkinter
import uuid
from math import ceil
from Connections import HostConnection, PeerConnection
from Messages import StickerFragment

sender = HostConnection(8921)
sender.discovery_broadcast()
root = tkinter.Tk()
root.title("Image")

def chunk_and_send(chunk_size: int, data: str):
    chunk_index = 0
    total_chunks = ceil(len(data) / chunk_size)
    for i in range(0, len(data), chunk_size):
        fragment = StickerFragment(0, uuid.uuid4(), "Allen", chunk_index, total_chunks, data[i:i+chunk_size])
        for peer in sender.connected_peers.keys():
            sender.send(fragment.to_message_format(), peer)
        chunk_index += 1

with open("stickers/death_mark.png", "rb") as img:
    encoded = base64.b64encode(img.read()).decode('ascii')
    chunk_and_send(1024, encoded)