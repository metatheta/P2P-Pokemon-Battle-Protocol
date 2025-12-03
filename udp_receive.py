import tkinter

from Connections import PeerConnection

root = tkinter.Tk()
root.title("Image")
receiver = PeerConnection(8392)

if receiver.wait_for_broadcast():
    chunks = {}
    while True:
        fields = receiver.receive()
        index = int(fields["chunk_index"])
        data = fields["fragment_data"]
        total = int(fields["total_chunks"])
        chunks[index] = data
        if len(chunks) == total:
            break
    final_string = "".join(chunks[i] for i in range(total))
    img = tkinter.PhotoImage(data=final_string)
    img_label = tkinter.Label(root, image=img)
    img_label.pack()
    root.mainloop()