import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
from PIL import Image, ImageTk, ImageGrab
import paho.mqtt.client as mqtt
import pytweening as pt
from bs4 import BeautifulSoup
from loguru import logger
import pyperclip
import numpy as np
import os
import ctypes
import json
import requests
from io import BytesIO


ctypes.windll.shcore.SetProcessDpiAwareness(1)

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print(msg)
    print("message received " , msg)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print("Subscribing to topic","dnd")
    print(client.subscribe("dnd"))
    
def pull_image_from_clipboard():
    return im



class LogWindow(tk.Toplevel):
    def __init__(self):
        super().__init__(height = 500, width = 1500)
        self.title("Log Window")
        
        self.log = tk.Text(self)
        self.log.place(x = 0, y = 0, height = 500, width = 1500)
        



class InitiativeWindow(tk.Toplevel):
    def __init__(self):
        super().__init__(height = 600, width = 1800)
        self.resizable(0,0)
        self.title("Initiative Display")
        
        self.render_list = []
        
        def InitiativeSet():
            pass
        
        self.upper_frame = ttk.Frame(self)
        self.lower_frame = ttk.Frame(self)
        
        #tmp_canvas = tk.Canvas(upper_frame, bg = "#0000FF", width = 300, height = 300)
        #tmp_canvas.pack()
        
        self.initiative_list = tk.Listbox(self.upper_frame)
        #self.initiative_list.grid(row = 0, column = 0, sticky = "ns")
        self.initiative_list.place(x = 0, y = 0, height = 300, width = 400)
        
        
        def parse_dndb():
            logger.debug("Parsing dndb content")
            avatar_imgs = []
            render_list = []

            logger.debug("Looking for avatars...")
            # Find the combat cards
            html = pyperclip.paste()
            # print(html)
            soup = BeautifulSoup(html)
            # avatars_list = soup.find_all("div", class_ = "combatant-summary__avatar")
            avatars_list = soup.find_all("div", class_ = "combatant-card__mid-bit combatant-summary")
            
            
            logger.debug("done, found " + str(len(avatars_list)))
            for avatar in avatars_list:
                content = requests.get(avatar.img['src']).content
                image_data = BytesIO(content)
                img = ImageTk.PhotoImage(Image.open(image_data).resize((250,250)))
                avatar_imgs.append(img)
                
                avatar_name = avatar.find_all("div", class_ = "combatant-summary__name")[0].string
                render_list.append((img, avatar_name))
                logger.debug("Parsed 1.")
            self.render_list = render_list
            logger.debug("Set internal render list")
            self.initiative_list.delete(0, self.initiative_list.size()-1)
            for elem in self.render_list:
                self.initiative_list.insert(tk.END, elem[1])
            logger.debug("Set new initiative list contents.")
            
        pull_initiative_btn = ttk.Button(self.upper_frame, text = "Pull Order", command = parse_dndb)
        pull_initiative_btn.place(x = 410, y = 0)
        
        ship_btn = ttk.Button(self.upper_frame, text = "Ship")
        ship_btn.place(x = 410, y = 40)

        drop_btn = ttk.Button(self.upper_frame, text = "Drop")
        drop_btn.place(x = 410, y = 170)
        

        
        move_up_btn = ttk.Button(self.upper_frame, text = "Move Up")
        move_up_btn.place(x = 410, y = 210)
        
        move_down_btn = ttk.Button(self.upper_frame, text = "Move Down")
        move_down_btn.place(x = 410, y = 250)
        
        self.prep_name = ttk.Entry(self.upper_frame, text = "Name")
        self.prep_name.place(x = 1500, y = 0, width = 250)
        
        def pull_pic_fcn():
            im = ImageGrab.grabclipboard()
            logger.debug("Pulled from clipboard")
            if im:
                self.prep_img_be = ImageTk.PhotoImage(im.resize((250,250)))
                self.prep_img_cv = self.prep_canvas.create_image(0,0, image = self.prep_img_be, anchor = "nw")

        
        self.pull_pic_btn = ttk.Button(self.upper_frame, text = "Pull Pic", command = pull_pic_fcn)
        self.pull_pic_btn.place(x = 1500, y = 30, anchor = "ne", width = 100)
        
        
        self.add_above_btn = ttk.Button(self.upper_frame, text = "Add Above")
        self.add_above_btn.place(x = 1500, y = 70, anchor = "ne", width = 100)
        self.add_below_btn = ttk.Button(self.upper_frame, text = "Add Below")
        self.add_below_btn.place(x = 1500, y = 110, anchor = "ne", width = 100)
        self.prep_canvas = tk.Canvas(self.upper_frame, bg = "#000000", width = 300, height = 300)
        self.prep_canvas.place(x = 1500, y = 30, width = 250, height = 250)
        
        
        
        
        self.display_canvas = tk.Canvas(self.lower_frame, bg = "#00FF00", width = 1800, height = 300)
        #self.display_canvas.pack(expand = 1, fill = tk.BOTH)
        self.display_canvas.grid(row = 4, column = 0, columnspan = 5)
        
        #upper_frame.pack()
        self.upper_frame.place(x = 0, y = 0, height = 300, width = 1800)
        #lower_frame.pack()
        self.lower_frame.place(x = 0, y = 300, height = 300, width = 1800)



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

logWindow = LogWindow()

def write_log(msg):
    global logWindow
    logWindow.log.insert(tk.END, msg)
    
logger.add(write_log)






initiative_window = InitiativeWindow()








print("Starting mqtt client")
client.loop_start() 
print("Starting main loop")
root.mainloop()
