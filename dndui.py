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
import gc
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
        
        self.avatar_size = (200,200)
        self.cameo_size = (250,275)
        self.upper_buffer = 15
        self.left_buffer = 10
        
        self.pull_initiative_btn = ttk.Button(self.upper_frame, text = "Pull Order", command = self.parseDNDB)
        self.pull_initiative_btn.place(x = 410, y = 0)

        self.ship_btn = ttk.Button(self.upper_frame, text = "Ship", command = self.shipFcn)
        self.ship_btn.place(x = 410, y = 40)

        self.drop_btn = ttk.Button(self.upper_frame, text = "Drop", command = self.dropFcn)
        self.drop_btn.place(x = 410, y = 170)
    

    
        self.move_up_btn = ttk.Button(self.upper_frame, text = "Move Up")
        self.move_up_btn.place(x = 410, y = 210)
        
        self.move_down_btn = ttk.Button(self.upper_frame, text = "Move Down")
        self.move_down_btn.place(x = 410, y = 250)
        
        self.cycle_fwd_btn = ttk.Button(self.upper_frame, text = "Cycle Forward", command = self.cycleForward)
        self.cycle_fwd_btn.place(x = 800, y = 100, width = 200, height = 200)
        self.cycle_bwd_btn = ttk.Button(self.upper_frame, text = "Cycle Backward", command = self.cycleBackward)
        self.cycle_bwd_btn.place(x = 1020, y = 100, width = 200, height = 200)
        
        
        self.prep_name_str_var = tk.StringVar(value = "Name")
        self.prep_name = ttk.Entry(self.upper_frame, textvariable = self.prep_name_str_var)
        
        self.prep_name.place(x = 1500, y = 0, width = 250)
        
        self.pull_pic_btn = ttk.Button(self.upper_frame, text = "Pull Pic", command = self.pullPicFcn)
        self.pull_pic_btn.place(x = 1500, y = 30, anchor = "ne", width = 100)
        
        self.add_above_btn = ttk.Button(self.upper_frame, text = "Add Above", command = self.addAboveFcn)
        self.add_above_btn.place(x = 1500, y = 70, anchor = "ne", width = 100)
        self.add_below_btn = ttk.Button(self.upper_frame, text = "Add Below")
        self.add_below_btn.place(x = 1500, y = 110, anchor = "ne", width = 100)
        self.prep_canvas = tk.Canvas(self.upper_frame, bg = "#000000", width = self.avatar_size[0], height = self.avatar_size[1])
        self.prep_canvas.place(x = 1500, y = 30, width = self.avatar_size[0], height = self.avatar_size[1])
        
        
        
        
        self.display_canvas = tk.Canvas(self.lower_frame, bg = "#00FF00", width = 1800, height = 300)
        self.display_canvas.grid(row = 4, column = 0, columnspan = 5)
        
        self.upper_frame.place(x = 0, y = 0, height = 300, width = 1800)
        self.lower_frame.place(x = 0, y = 300, height = 300, width = 1800)

    def setInitGroupsSpacing(self):
        for i in range(len(self.initiative_group_list)):
            self.initiative_group_list[i].setDestinationAndMove(coords = (i * 250, 0))

    class InitiativeGroup():
        def __init__(self, name = "Nobody", avatar = None, canvas = None, location = [0,0], avatar_size = (250,250), upper_buffer = 10, left_buffer = 10, cameo_size = (250,275)):
            self.name = name
            self.avatar = avatar
            self.avatar_size = avatar_size
            self.cameo_size = cameo_size
            self.upper_buffer = upper_buffer
            self.left_buffer = left_buffer
            self.location = location
            self.destination = self.location
            self.canvas = canvas
            self.avatar_image_be = ImageTk.PhotoImage(self.avatar.resize(self.avatar_size))
            self.avatar_image_id = self.canvas.create_image(self.left_buffer + self.location[0], self.upper_buffer + self.location[1], image = self.avatar_image_be, anchor = "nw")
            
            self.font = tkFont.Font(family='Arial', size=12, weight='bold')
            self.cameo_be = ImageTk.PhotoImage(Image.open("./assets/init_cameo.png").resize(self.cameo_size))
            self.cameo_id = self.canvas.create_image(self.left_buffer + self.location[0] - 25, self.upper_buffer + self.location[1]-5, image = self.cameo_be, anchor = "nw")

            self.name_id = self.canvas.create_text(self.left_buffer + self.location[0] + self.avatar_size[0]/2,self.upper_buffer + self.location[1] + self.avatar_size[1] + 40, text = self.name, width = 200, font = self.font, justify = tk.CENTER, fill = "white")

            self.anim = 0
            
        

        
        def destroy(self):
            logger.debug("Destroying " + self.name)
            self.canvas.delete(self.avatar_image_id)
            self.canvas.delete(self.name_id)
            self.canvas.delete(self.cameo_id)
            
            
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
                self.left_buffer + self.location[0], 
                self.upper_buffer + self.location[1])
            self.canvas.coords(self.name_id, 
                self.left_buffer + self.location[0] + self.avatar_size[0]/2, 
                self.upper_buffer + self.location[1] + self.avatar_size[1] + 40)
            self.canvas.coords(self.cameo_id,
                self.left_buffer + self.location[0] - 25,
                self.upper_buffer + self.location[1] - 5)

            
        def snapToDestination(self):
            self.location = self.destination
            self.redraw()
            if self.anim != 0:
                root.after_cancel(self.anim)
                self.anim = 0

        def updateLocation(self, steps=200, duration = 200):
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

    def cycleForward(self):
        self.initiative_group_list[0].setDestination((2000,0))
        self.initiative_group_list[0].snapToDestination()
        self.initiative_group_list.append(self.initiative_group_list.pop(0))
        self.initiative_list.insert(tk.END, self.initiative_list.get(0))
        self.initiative_list.delete(0)
        self.setInitGroupsSpacing()
        
    def cycleBackward(self):
        self.initiative_group_list[-1].setDestination((-300, 0))
        self.initiative_group_list[-1].snapToDestination()
        self.initiative_group_list.insert(0, self.initiative_group_list.pop())
        self.initiative_list.insert(0, self.initiative_list.get(tk.END))
        self.initiative_list.delete(tk.END)
        self.setInitGroupsSpacing()

    def parseDNDB(self):
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
        
    
    def shipFcn(self):
        for elem in self.initiative_group_list:
            elem.destroy()
        self.initiative_group_list = []
        for elem in self.render_list:
            logger.debug(elem[1])
            self.initiative_group_list.append(self.InitiativeGroup(name = elem[1], avatar = elem[0], canvas = self.display_canvas, location = [0,0], avatar_size = self.avatar_size, cameo_size = self.cameo_size, upper_buffer = self.upper_buffer, left_buffer = self.left_buffer))
        self.setInitGroupsSpacing()
            
    

    def dropFcn(self):
        selection = self.initiative_list.curselection()[0]
        logger.debug("Removing " + str(selection) + ": " + self.initiative_group_list[selection].name)
        self.initiative_list.delete(selection)
        self.initiative_group_list.pop(selection).destroy()
        #to_del.setDestinationAndMove((to_del.getCurrentPosition()[0], 600))
        #root.after(500, to_del.destroy())
        #root.after(500, lambda: gc.collect())
        self.setInitGroupsSpacing()



    
    def pullPicFcn(self):
        self.prep_img = ImageGrab.grabclipboard()
        logger.debug("Pulled from clipboard")
        if self.prep_img:
            self.prep_img_be = ImageTk.PhotoImage(self.prep_img.resize(self.avatar_size))
            self.prep_img_cv = self.prep_canvas.create_image(0,0, image = self.prep_img_be, anchor = "nw")

    
    
    def addAboveFcn(self):
        logger.debug("Adding above")
        # pull selection ix from list box
        selection = self.initiative_list.curselection()[0]

        # create initiativegroup
            # pull name
        to_name = self.prep_name_str_var.get()
            # pull img
        to_avatar = self.prep_img
        new_init_group = self.InitiativeGroup(name = to_name, avatar = to_avatar, canvas = self.display_canvas, location = [2000,0], avatar_size = self.avatar_size, cameo_size = self.cameo_size, upper_buffer = self.upper_buffer, left_buffer = self.left_buffer)    
        # add to list box
        self.initiative_list.insert(selection, to_name)
        # add to initiative group list
        self.initiative_group_list.insert(selection, new_init_group)
        # update location and redraw
        self.setInitGroupsSpacing()

        
    



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
