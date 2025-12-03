import base64
import tkinter
import uuid

from Messages import StickerFragment

root = tkinter.Tk()
root.title("Image")

def split_base64(chunk_size: int, data: bytes):
    result = []
    chunk_index = 0
    for i in range (0, len(data), chunk_size):
        fragment = StickerFragment(0, uuid.uuid4(), "Allen", chunk_index, len(data), data[i:i+chunk_size])
        chunk_index += 1
        result.append(fragment)
    return result

if __name__ == '__main__':
    with open("stickers/death_mark.png", "rb") as img:
        encoded = base64.encodebytes(img.read())

    chunks: list[StickerFragment] = split_base64(1024, encoded)

    frags = [x.fragment_data for x in chunks]
    final = b"".join(frags)

    with open("output1.txt", "w") as f:
        print(final, file=f)

    img = tkinter.PhotoImage(data=final)
    img_label = tkinter.Label(root, image=img)
    img_label.pack()

    root.mainloop()
