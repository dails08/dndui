import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
from PIL import Image, ImageTk
import paho.mqtt.client as mqtt
import pytweening as pt
import numpy as np
import os
import ctypes
import json

ctypes.windll.shcore.SetProcessDpiAwareness(1)

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print(msg)
    print("message received " , msg)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print("Subscribing to topic","dnd")
    print(client.subscribe("dnd"))


def parse_dndb():
    avatar_imgs = []
    render_list = []

    print("Looking for avatars...", end = "")
    # Find the combat cards
    html = pyperclip.paste()
    # print(html)
    soup = BeautifulSoup(html)
    # avatars_list = soup.find_all("div", class_ = "combatant-summary__avatar")
    avatars_list = soup.find_all("div", class_ = "combatant-card__mid-bit combatant-summary")
    
    
    print("done, found " + str(len(avatars_list)))
    for avatar in avatars_list:
        _src = avatar.img['src']
        print(_src)
        if _src not in img_library.keys():
            content = requests.get(avatar.img['src']).content
            img_library[_src] = content
        else:
            content = img_library[_src]
        image_data = BytesIO(content)
        _img = pygame.transform.smoothscale(pygame.image.load(image_data), (100,100))
        avatar_imgs.append(_img)
        
        avatar_name = avatar.find_all("div", class_ = "combatant-summary__name")[0].string
        render_list.append((_img, avatar_name))



class InitiativeWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.resizable(0,0)
        self.title("Initiative Display")
        
        upper_frame = ttk.Frame(self)
        lower_frame = ttk.Frame(self)
        
        #tmp_canvas = tk.Canvas(upper_frame, bg = "#0000FF", width = 300, height = 300)
        #tmp_canvas.pack()
        
        self.initiative_list = tk.Listbox(upper_frame)
        self.initiative_list.grid(row = 0, column = 0)
        
        button_frame_left = tk.Frame(upper_frame)
        button_frame_left.grid(row = 0, column = 1)
        
        drop_btn = ttk.Button(button_frame_left, text = "Drop")
        drop_btn.grid(column = 0, row = 0)
        
        buffer_frame = tk.Frame(button_frame_left)
        buffer_frame.grid(column = 0, row = 1, rowspan = 2, pady = 80)
        
        move_up_btn = ttk.Button(button_frame_left, text = "Move Up")
        move_up_btn.grid(column = 0, row = 3)
        move_down_btn = ttk.Button(button_frame_left, text = "Move Down")
        move_down_btn.grid(column = 0, row = 4)
        
        
        
        self.display_canvas = tk.Canvas(lower_frame, bg = "#00FF00", width = 1800, height = 300)
        #self.display_canvas.pack(expand = 1, fill = tk.BOTH)
        self.display_canvas.grid(row = 4, column = 0, columnspan = 5)
        
        #upper_frame.pack()
        upper_frame.grid(row = 0, column = 0, sticky = "w")
        #lower_frame.pack()
        lower_frame.grid(row = 1, column = 0)



broker_address="127.0.0.1"

print("creating new instance")
client = mqtt.Client() #create new instance
client.on_message=on_message #attach function to callback
client.on_connect = on_connect

print("connecting to broker")
client.connect(broker_address, port = 1883) #connect to broker


root = tk.Tk()
root.title("Tab Widget")
root.geometry("800x600")

tabControl = ttk.Notebook(root)

tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

tabControl.add(tab1, text = "Tab 1")
tabControl.add(tab2, text = "Tab 2")

tabControl.pack(expand = 1, fill = "both")

ttk.Label(tab1, text = "Tab1").grid(column = 0, row = 0, padx = 30, pady = 30)
ttk.Label(tab2, text = "Tab2").grid(column = 0, row = 0, padx = 30, pady = 30)








initiative_window = InitiativeWindow()








print("Starting mqtt client")
client.loop_start() 
print("Starting main loop")
root.mainloop()
