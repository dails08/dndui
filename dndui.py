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
        self.initiative_group_list = []
        
        self.upper_frame = ttk.Frame(self)
        self.lower_frame = ttk.Frame(self)
        
        
        self.initiative_list = tk.Listbox(self.upper_frame)
        self.initiative_list.place(x = 0, y = 0, height = 300, width = 400)
        
        avatar_size = (200,200)
        upper_buffer = 10
        left_buffer = 10
        
    
        
    class InitiativeGroup():
        def __init__(self, name = "Nobody", avatar = None, canvas = None, location = [0,0]):
            self.name = name
            self.avatar = avatar
            self.location = location
            self.destination = self.location
            self.canvas = canvas
            self.avatar_image_be = ImageTk.PhotoImage(self.avatar.resize(avatar_size))
            self.avatar_image_id = self.canvas.create_image(left_buffer + self.location[0], upper_buffer + self.location[1], image = self.avatar_image_be, anchor = "nw")
            
            self.font = tkFont.Font(family='Arial', size=12, weight='bold')
            self.name_id = self.canvas.create_text(left_buffer + self.location[0] + avatar_size[0]/2,upper_buffer + self.location[1] + avatar_size[1] + 10, text = self.name, width = 200, font = self.font, justify = tk.CENTER, fill = "white")

            self.anim = 0
            
        def setInitGroupsSpacing():
            for i in range(len(self.initiative_group_list)):
                self.initiative_group_list[i].setDestinationAndMove(coords = (i * 300, 0))

        
        def destroy(self):
            logger.debug("Destroying " + self.name)
            self.canvas.delete(self.avatar_image_id)
            self.canvas.delete(self.name_id)
            
            
        def setDestination(self, coords):
            self.destination = coords
        def setDestinationAndMove(self, coords):
            self.destination = coords
            self.updateLocation()
            
        def getCurrentPosition(self):
            return self.location
        def getDestination(self):
            return self.destination
            
        def redraw(self):
            self.canvas.coords(self.avatar_image_id, 
                left_buffer + self.location[0], 
                upper_buffer + self.location[1])
            self.canvas.coords(self.name_id, 
                left_buffer + self.location[0] + avatar_size[0]/2, 
                upper_buffer + self.location[1] + avatar_size[1] + 10)

            
        def snapToDestination(self):
            self.location = self.destination
            self.canvas.coords(self.avatar_image_id, left_buffer + self.location[0], upper_buffer + self.location[1])
            self.canvas.coords(self.name_id, 
                left_buffer + self.location[0] + avatar_size[0]/2, 
                upper_buffer + self.location[1] + avatar_size[1] + 10)
            if self.anim != 0:
                root.after_cancel(self.anim)
                self.anim = 0

        def updateLocation(self, steps=100, duration = 200):
            if self.anim != 0:
                root.after_cancel(self.anim)
                self.anim = 0
            if self.getCurrentPosition() != self.getDestination():
                #print("Position needs updating!")
                # calculate y path
                # hard-code animation pattern for now
                x_distance = self.getDestination()[0] - self.getCurrentPosition()[0]
                x_path = self.getCurrentPosition()[0] + x_distance * np.array([pt.easeOutQuint(x) for x in np.linspace(0,1, steps+1)])
                per_step = int(duration/steps)
                # call update_step fcn
                self.updateLocationStep(x_path, per_step)

        def updateLocationStep(self, x_path, per_step):
            #print("Taking a step!")
            if len(x_path) == 0:
                #print("Done moving!")
                self.snapToDestination()
            else:
                self.location = (x_path[0], self.location[1])
                self.redraw()
                #self.canvas.coords(self.avatar_image_id, self.getDestination()[0], x_path[0])
                #self.canvas.coords(self.text_block_id, self.destination_position[0]-300, y_path[0])
                #self.canvas.coords(self.text_words_id, self.destination_position[0]-150, y_path[0]+50)
                
                
                self.anim = root.after(per_step, lambda: self.updateLocationStep(x_path[1:], per_step))

    
    def parseDNDB():
        logger.debug("Parsing dndb content")
        avatar_imgs = []
        render_list = []

        logger.debug("Looking for avatars...")
        # Find the combat cards
        html = pyperclip.paste()
        soup = BeautifulSoup(html, features = "html.parser")
        avatars_list = soup.find_all("div", class_ = "combatant-card__mid-bit combatant-summary")
        
        
        logger.debug("done, found " + str(len(avatars_list)))
        for avatar in avatars_list:
            content = requests.get(avatar.img['src']).content
            image_data = BytesIO(content)
            img = Image.open(image_data)
            avatar_imgs.append(img)
            
            avatar_name = avatar.find_all("div", class_ = "combatant-summary__name")[0].string
            render_list.append((img, avatar_name))
            logger.debug("Parsed " + avatar_name)
        self.render_list = render_list
        logger.debug("Set internal render list")
        self.initiative_list.delete(0, self.initiative_list.size()-1)
        for elem in self.render_list:
            self.initiative_list.insert(tk.END, elem[1])
        logger.debug("Set new initiative list contents.")
        
    pull_initiative_btn = ttk.Button(self.upper_frame, text = "Pull Order", command = parseDNDB)
    pull_initiative_btn.place(x = 410, y = 0)
    
    def shipFcn():
        for elem in self.initiative_group_list:
            elem.destroy()
        self.initiative_group_list = []
        for elem in self.render_list:
            logger.debug(elem[1])
            self.initiative_group_list.append(InitiativeGroup(name = elem[1], avatar = elem[0], canvas = self.display_canvas, location = [0,0]))
        self.setInitGroupsSpacing()
            
    
    ship_btn = ttk.Button(self.upper_frame, text = "Ship", command = shipFcn)
    ship_btn.place(x = 410, y = 40)

    def dropFcn():
        selection = self.initiative_list.curselection()[0]
        logger.debug("Removing " + str(selection))
        self.initiative_list.delete(selection)
        self.render_list.pop(selection)
        self.initiative_group_list[selection].destroy()
        self.initiative_group_list.pop(selection)
        self.setInitGroupsSpacing()



    drop_btn = ttk.Button(self.upper_frame, text = "Drop", command = dropFcn)
    drop_btn.place(x = 410, y = 170)
    

    
    move_up_btn = ttk.Button(self.upper_frame, text = "Move Up")
    move_up_btn.place(x = 410, y = 210)
    
    move_down_btn = ttk.Button(self.upper_frame, text = "Move Down")
    move_down_btn.place(x = 410, y = 250)
    
    
    self.prep_name_str_var = tk.StringVar(value = "Name")
    self.prep_name = ttk.Entry(self.upper_frame, textvariable = self.prep_name_str_var)
    
    self.prep_name.place(x = 1500, y = 0, width = 250)
    
    def pullPicFcn():
        self.prep_img = ImageGrab.grabclipboard()
        logger.debug("Pulled from clipboard")
        if self.prep_img:
            self.prep_img_be = ImageTk.PhotoImage(self.prep_img.resize(avatar_size))
            self.prep_img_cv = self.prep_canvas.create_image(0,0, image = self.prep_img_be, anchor = "nw")

    
    self.pull_pic_btn = ttk.Button(self.upper_frame, text = "Pull Pic", command = pullPicFcn)
    self.pull_pic_btn.place(x = 1500, y = 30, anchor = "ne", width = 100)
    
    def addAboveFcn():
        logger.debug("Adding above")
        # pull selection ix from list box
        selection = self.initiative_list.curselection()[0]

        # create initiativegroup
            # pull name
        to_name = self.prep_name_str_var.get()
            # pull img
        to_avatar = self.prep_img
        new_init_group = InitiativeGroup(name = to_name, avatar = to_avatar, canvas = self.display_canvas, location = [2000,0])    
        # add to list box
        self.initiative_list.insert(selection, to_name)
        # add to initiative group list
        self.initiative_group_list.insert(selection, new_init_group)
        # update location and redraw
        self.setInitGroupsSpacing()

        
    
    self.add_above_btn = ttk.Button(self.upper_frame, text = "Add Above", command = addAboveFcn)
    self.add_above_btn.place(x = 1500, y = 70, anchor = "ne", width = 100)
    self.add_below_btn = ttk.Button(self.upper_frame, text = "Add Below")
    self.add_below_btn.place(x = 1500, y = 110, anchor = "ne", width = 100)
    self.prep_canvas = tk.Canvas(self.upper_frame, bg = "#000000", width = avatar_size[0], height = avatar_size[1])
    self.prep_canvas.place(x = 1500, y = 30, width = avatar_size[0], height = avatar_size[1])
    
    
    
    
    self.display_canvas = tk.Canvas(self.lower_frame, bg = "#00FF00", width = 1800, height = 300)
    self.display_canvas.grid(row = 4, column = 0, columnspan = 5)
    
    self.upper_frame.place(x = 0, y = 0, height = 300, width = 1800)
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
