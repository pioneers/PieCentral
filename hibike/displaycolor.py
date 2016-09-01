import hibike
import time
import os, sys
import Tkinter
import Image, ImageTk

h = hibike.Hibike(timeout=1)
time.sleep(2)
x = [(uid, 100) for uid in h.getUIDs()]
uid_params = {uid: h.getParams(uid)[1:] for uid in h.getUIDs()}
h.subToDevices(x)
last = ''
counter = 0

def button_click_exit_mainloop (event):
    event.widget.quit() # this will cause mainloop to unblock.

device = h.getUIDs()[0]
h.writeValue(device, 'Toggle', 1)
root = Tkinter.Tk()
root.bind("<Button>", button_click_exit_mainloop)
imagedir = './images/colorsensor.jpg'
old_label_image = None


while 1:
    r,g,b,l = h.getData(device, 'dataUpdate')[0];
    print("RAW r: "+str(r))
    print("RAW g: "+str(g))
    print("RAW b: "+str(b))
    print("RAW l: "+str(l))

    if l == 0:
        time.sleep(0.1)
        continue

    l = float(l)
    r, g, b = r/l, g/l, b/l
    r, g, b = r*256, g*256, b*256
    hexval = '#'+hex(int(r) << 16 | int(g) << 8 | int(b))[2:]

    print(hexval)
    print('*************')

    img = Image.new('RGB', (512, 512), hexval)
    img.save('./images/colorsensor.jpg', 'jpeg')

    try:
        im = Image.open(imagedir)
        tkpi = ImageTk.PhotoImage(im)
        label_image = Tkinter.Label(root, image=tkpi)
        label_image.place(x=0,y=0)
        if old_label_image is not None:
            old_label_image.destroy()
        old_label_image = label_image
        root.mainloop() # wait until user clicks the window
    except e:
        pass

    # time.sleep(0.1)