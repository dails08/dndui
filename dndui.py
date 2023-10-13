import tkinter as tk
from tkinter import filedialog
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
import pathlib
import multiprocessing as mp
from threading import Timer
from flask import Flask, request
import atexit
import sys

import vlc


def startFlaskServer(q):
    if getattr(sys, 'frozen', False):
        template_folder = os.path.join(sys._MEIPASS, 'templates')
        static_folder = os.path.join(sys._MEIPASS, 'static')
        app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    
    else:
        app = Flask(__name__)
    
    @app.route("/msg/<msg>")
    def rxMessage(msg):
        q.put(msg)
        return "ok"
        
    app.run(debug = False, port = 5000)

if __name__ == "__main__":
    mp.freeze_support()
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

    def onMessage(msg):
        print(msg)
        print("message received: " , msg)
        if msg.split("/")[0] == "CitationWindow":
            art_window.parse_msg(msg.split("/")[1:])



    class LogWindow(tk.Toplevel):
        def __init__(self):
            super().__init__(height = 500, width = 1500)
            self.title("Log Window")
            
            self.log = tk.Text(self)
            self.log.place(x = 0, y = 0, height = 500, width = 1500)
            
           
           


    class InitiativeTab(ttk.Frame):
        def __init__(self, controller):
            super().__init__(controller)
            
            self.initiative_window = tk.Toplevel(width = 1800, height = 300)
            self.initiative_window.resizable(0,0)
            self.initiative_window.title("Initiative Dispay")
            
            self.render_list = []
            self.initiative_group_list = []
            
            self.display_canvas = tk.Canvas(self.initiative_window, bg = "#00FF00", width = 1800, height = 300)
            self.display_canvas.place(x = 0, y = 0, width = 1800, height = 300)
            
            self.avatar_size = (200,200)
            self.cameo_size = (250,275)
            self.upper_buffer = 15
            self.left_buffer = 10

            
            self.initiative_list = tk.Listbox(self)
            self.initiative_list.place(x = 0, y = 0, height = 400, width = 200)
            
            self.pull_initiative_btn = ttk.Button(self, text = "Pull Order", command = self.parseDNDB)
            self.pull_initiative_btn.place(x = 210, y = 0)

            self.ship_btn = ttk.Button(self, text = "Ship", command = self.shipFcn)
            self.ship_btn.place(x = 210, y = 40)

            self.drop_btn = ttk.Button(self, text = "Drop", command = self.dropFcn)
            self.drop_btn.place(x = 210, y = 170)
        

        
            self.move_up_btn = ttk.Button(self, text = "Move Up", command = self.moveUpFcn)
            self.move_up_btn.place(x = 210, y = 210)
            
            self.move_down_btn = ttk.Button(self, text = "Move Down", command = self.moveDownFcn)
            self.move_down_btn.place(x = 210, y = 250)
            
            self.clear_initiative_btn = ttk.Button(self, text = "Clear", command = self.clearList)
            self.clear_initiative_btn.place(x = 210, y = 350)
            
            self.cycle_fwd_btn = ttk.Button(self, text = "Cycle Forward", command = self.cycleForward)
            self.cycle_fwd_btn.place(x = 5, y = 405, width = 150, height = 150)
            self.cycle_bwd_btn = ttk.Button(self, text = "Cycle Backward", command = self.cycleBackward)
            self.cycle_bwd_btn.place(x = 155, y = 405, width = 150, height = 150)
            
            
            self.prep_name_str_var = tk.StringVar(value = "Name")
            self.prep_name = ttk.Entry(self, textvariable = self.prep_name_str_var)
            
            self.prep_name.place(x = 600, y = 0, width = 200)
            
            self.pull_pic_btn = ttk.Button(self, text = "Pull Pic", command = self.pullPicFcn)
            self.pull_pic_btn.place(x = 600, y = 30, anchor = "ne", width = 100)
            
            self.add_above_btn = ttk.Button(self, text = "Add Above", command = self.addAboveFcn)
            self.add_above_btn.place(x = 600, y = 70, anchor = "ne", width = 100)
            self.add_below_btn = ttk.Button(self, text = "Add Below", command = self.addBelowFcn)
            self.add_below_btn.place(x = 600, y = 110, anchor = "ne", width = 100)
            self.prep_canvas = tk.Canvas(self, bg = "#000000", width = self.avatar_size[0], height = self.avatar_size[1])
            self.prep_canvas.place(x = 600, y = 30, width = self.avatar_size[0], height = self.avatar_size[1])
            
            self.copy_encounter_script_btn = ttk.Button(self, text = "Copy Encounter Script", command = self.copyEncounterScript)
            self.copy_encounter_script_btn.place(x = 495, y = 495, width = 300, height = 50)
            
        def copyEncounterScript(self):
            pyperclip.copy("navigator.clipboard.writeText(document.body.innerHTML);")
            
        def clearList(self):
            while self.initiative_list.size() > 0:
                self.initiative_list.delete(0)
                self.initiative_group_list.pop(0).destroy()
                


            

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
                
                self.font = tkFont.Font(family='Matura MT Script Capitals', size=12, weight='bold')
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
            
        def addBelowFcn(self):
            logger.debug("Adding below")
            selection = self.initiative_list.curselection()[0]
            
            to_name = self.prep_name_str_var.get()
            to_avatar = self.prep_img
            new_init_group = self.InitiativeGroup(name = to_name, avatar = to_avatar, canvas = self.display_canvas, location = [2000,0], avatar_size = self.avatar_size, cameo_size = self.cameo_size, upper_buffer = self.upper_buffer, left_buffer = self.left_buffer)    
            self.initiative_list.insert(selection + 1, to_name)
            # add to initiative group list
            self.initiative_group_list.insert(selection + 1, new_init_group)
            # update location and redraw
            self.setInitGroupsSpacing()
            
        def moveUpFcn(self):
            logger.debug("Moving up")
            selection = self.initiative_list.curselection()[0]
            logger.debug("Selection is " + str(selection))
            if selection > 0:
                to_name = self.initiative_list.get(selection)
                
                logger.debug("Copying " + to_name + " down")
                self.initiative_list.insert(selection - 1, to_name)
                
                logger.debug("Deleting " + self.initiative_list.get(selection + 1))
                self.initiative_list.delete(selection +1)
                
                
                logger.debug("Swapping " + self.initiative_group_list[selection - 1].name + " and " + self.initiative_group_list[selection].name)
                self.initiative_group_list[selection - 1], self.initiative_group_list[selection] = self.initiative_group_list[selection], self.initiative_group_list[selection - 1]
                
                logger.debug("Setting selection to " + self.initiative_list.get(selection - 1))
                self.initiative_list.selection_set(selection - 1)
                
                self.setInitGroupsSpacing()
                
        def moveDownFcn(self):
            logger.debug("Moving down")
            selection = self.initiative_list.curselection()[0]
            logger.debug("Selection is " + str(selection))
            if selection < self.initiative_list.size()-1:
                # easiest way to do this is just to moveUp the selection below.
                to_name = self.initiative_list.get(selection + 1)
                
                logger.debug("Copying " + to_name + " up")
                self.initiative_list.insert(selection, to_name)
                
                logger.debug("Deleting " + self.initiative_list.get(selection + 2))
                self.initiative_list.delete(selection + 2)
                
                logger.debug("Swapping " + self.initiative_group_list[selection + 1].name + " and " + self.initiative_group_list[selection].name)
                
                self.initiative_group_list[selection + 1], self.initiative_group_list[selection] = self.initiative_group_list[selection], self.initiative_group_list[selection + 1]

                logger.debug("Setting selection to " + self.initiative_list.get(selection + 1))
                self.initiative_list.selection_set(selection + 1)

                self.setInitGroupsSpacing()



            
        
    class BackgroundWindow(tk.Toplevel):
        def __init__(self, vlc_instance):
            super().__init__(width = 1920, height = 1080)
            self.resizable(0,0)
            self.title("Background Display")
            
            style = ttk.Style()
            style.configure("playerframe.TFrame", background = "black")
            
            self.display_frame = ttk.Frame(self)#, style = "playerframe.TFrame")
            self.display_frame.place(x = 0, y = 0, width = 1920, height = 1080)
            self.display_frame.config()
            
            self.h = self.display_frame.winfo_id()
            
            #self.canvas = tk.Canvas(self.display_frame)
            #self.canvas.place(x = 0, y = 0, width = 1920, height = 1080)
            
            
           # def descendTree(dir):
           #     for dirName, subdirList, fileList in os.walk(
                
            
            
            self.vlc_instance = vlc_instance
            
            MRL = r"C:\Users\Christopher\Dropbox\CoS\OBS Rework\bg\AT2.jpg"
            self.player = self.vlc_instance.media_player_new()
            self.player.set_hwnd(self.h)
            self.player.audio_set_mute(True)

            self.list_player = self.vlc_instance.media_list_player_new()
            self.list_player.set_media_player(self.player)
            self.list_player.set_playback_mode(vlc.PlaybackMode.repeat)

            self.media_list = self.vlc_instance.media_list_new([MRL])
            self.list_player.set_media_list(self.media_list)
            self.list_player.play_item_at_index(0)
        
        def playMedia(self, MRL):
            logger.debug("Received " + MRL + " at bg window")
            self.media_list = self.vlc_instance.media_list_new([MRL])
            self.list_player.set_media_list(self.media_list)
            self.list_player.play_item_at_index(0)
            





    class BackgroundTab(ttk.Frame):
        def __init__(self, vlc_instance, background_window,citations_window, controller):
            super().__init__(controller)
            self.vlc_instance = vlc_instance
            self.background_window = background_window
            
            self.citations_window = citations_window
            
            self.tree_frame = ttk.Frame(self)
            self.tree_frame.place(x = 0, y = 0, width = 410, height = 500)
            self.file_tree = ttk.Treeview(self.tree_frame)
            self.file_tree.place(x = 0, y = 0, width = 400, height = 500)
            
            scrollbar = ttk.Scrollbar(self.tree_frame, orient = "vertical", command = self.file_tree.yview)
            self.file_tree.configure(yscrollcommand = scrollbar.set)
            
            scrollbar.place(x = 395, y = 0, height = 500, width = 15)
            self.media_root_dir = r"C:\Users\Christopher\Dropbox\CoS\COS2\working assets\visual assets\bg"
            
            preview_scale = .6
            self.preview_frame = ttk.Frame(self)
            self.preview_frame.place(x = 410, y = 10, width = int(640*preview_scale), height = int(360*preview_scale))
            
            MRL = r"C:\Users\Christopher\Dropbox\CoS\OBS Rework\bg\AT2.jpg"
            
            self.citation_str_var = tk.StringVar(value = "")
            self.citation_entry = ttk.Entry(self, textvariable = self.citation_str_var)
            self.citation_entry.place(x = 410, y = int(360*preview_scale) + 15, width = int(640*preview_scale))
            
            self.save_citation_btn = ttk.Button(self, text = "Save Citation", command = self.saveCitation)
            self.save_citation_btn.place(x = 410, y = int(360*preview_scale) + 15 + 30 + 5)


            
            parent_dir = ""
            
           # def descendTree(dir):
           #     for dirName, subdirList, fileList in os.walk(
                
            for dirName, subdirList, fileList in os.walk(self.media_root_dir):
                #print("Dir: " + dirName)
                #print("Adding Dir " + dirName + " under " + parent_dir) 
                if not self.file_tree.exists(dirName):
                    self.file_tree.insert("", "end", dirName, text = dirName.split("\\")[-1])
                for subdir in subdirList:
                    fq_subdir = dirName + "\\" + subdir
                    #print("Adding subdir " + fq_subdir + " under " + dirName)
                    self.file_tree.insert(dirName, "end", iid = fq_subdir, text = subdir)
                for filename in fileList:
                    if filename.split(".")[-1] in ["webp"]:
                        continue
                    fq_filename = dirName + "\\" + filename
                    #print("Adding file " + fq_filename + " under " + dirName)
                    self.file_tree.insert(dirName, "end", iid = fq_filename, text = filename)
            
            self.file_tree.bind("<Double-1>", self.fileTreeDoubleClick)
            self.file_tree.bind("<Return>", self.fileTreeDoubleClick)
            self.file_tree.bind("<<TreeviewSelect>>", self.fileTreeSingleClick)
            
            self.media_list = self.vlc_instance.media_list_new([MRL])

            self.preview_player = self.vlc_instance.media_player_new()
            self.preview_player.set_hwnd(self.preview_frame.winfo_id())
            self.preview_player.audio_set_mute(True)
            
            self.preview_list_player = self.vlc_instance.media_list_player_new()
            self.preview_list_player.set_media_player(self.preview_player)
            self.preview_list_player.set_playback_mode(vlc.PlaybackMode.repeat)
            
            self.preview_media_list = self.vlc_instance.media_list_new([MRL])
            self.preview_list_player.set_media_list(self.media_list)
            self.preview_list_player.play_item_at_index(0)
            
        def saveCitation(self):
            citation = self.citation_str_var.get()
            selection_iid = self.file_tree.selection()[0]
            item = self.file_tree.item(selection_iid)
            if len(self.file_tree.get_children(selection_iid)) > 0:
                # Don't cite whole folders of media
                return
            filename = item['text']
            self.citations_window.citations_dict[filename] = citation
            with open("citations_dict.json", "w") as citations_file:
                json.dump(self.citations_window.citations_dict, citations_file)

        def playMedia(self, MRL):
            logger.debug("Sending " + MRL + " to bg window")
            self.background_window.playMedia(MRL)
            
        def previewMedia(self, MRL):
            self.preview_media_list = self.vlc_instance.media_list_new([MRL])
            self.preview_list_player.set_media_list(self.preview_media_list)
            self.preview_list_player.play_item_at_index(0)        

        def fileTreeDoubleClick(self, event):
            selection_iid = self.file_tree.selection()[0]
            print("Selection iid:")
            print(selection_iid)
            item = self.file_tree.item(selection_iid)
            if len(self.file_tree.get_children(selection_iid)) > 0:
                # Don't play whole folders of media
                return
            print("Item:")
            print(item)
            selection_parent = self.file_tree.parent(selection_iid)
            print("Selection parent:")
            print(selection_parent)
            filename = item['text']
            while filename.startswith("_ex_"):
                filename = filename[4:]
            print(filename)
            self.playMedia(selection_iid)
            self.citations_window.citeArt(filename)
            
            
        def fileTreeSingleClick(self, event):
            selection_iid = self.file_tree.selection()[0]
            print("Selection iid:")
            print(selection_iid)
            item = self.file_tree.item(selection_iid)
            if len(self.file_tree.get_children(selection_iid)) > 0:
                # Don't play whole folders of media
                return
            print("Item:")
            print(item)
            selection_parent = self.file_tree.parent(selection_iid)
            print("Selection parent:")
            print(selection_parent)
            filename = item['text']
            while filename.startswith("_ex_"):
                filename = filename[4:]
            print(filename)
            self.citation_entry.delete(0, tk.END)
            if filename in self.citations_window.citations_dict.keys():
                creator_name = self.citations_window.citations_dict[filename]
                self.citation_entry.insert(0, creator_name)
            self.previewMedia(selection_iid)

    vlc_instance = vlc.Instance()
    vlc_instance.log_unset()

    q = mp.Queue()
    
    logger.debug("Starting Flask process")
    flask_server_p = mp.Process(target = startFlaskServer, args = [q])
    flask_server_p.start()
    logger.debug("Testing Flask process")
    resp = requests.get("http://localhost:5000/msg/test_message")
    logger.debug("Flask test result: " + str(resp.status_code))
    
    t = None
    def checkFlaskQueue(q):
        global t
        if not q.empty():
            logger.debug("Pulling from Flask queue")
            onMessage(q.get())
        t = Timer(0.1, checkFlaskQueue, args = [q])
        t.start()

    logger.debug("Starting Flask monitor thread")
    checkFlaskQueue(q)
    
    def exitHandler():
        logger.debug("Starting terminate procedure")
        if flask_server_p.is_alive():
            logger.debug("Found running Flask server")
            flask_server_p.terminate()
            flask_server_p.join()
            logger.debug("Flask server terminated")
        else:
            logger.debug("Did not find a running Flask server")
        global t
        t.cancel()
        global root
        root.destroy()
    #atexit.register(exitHandler)



    root = tk.Tk()
    root.title("The Digital DM")
    root.geometry("800x600")
    root.option_add("*tearOff", False)
    
    menubar = tk.Menu(root)
    root["menu"] = menubar
    
    menu_file = tk.Menu(menubar)
    
    menubar.add_cascade(menu = menu_file, label = "File")
    
    def setMediaLocation(background_tab):
        media_root_dir = filedialog.askdirectory(initialdir = "~")
        
        for child in background_tab.file_tree.get_children():
            background_tab.file_tree.delete(child)
        
        for dirName, subdirList, fileList in os.walk(media_root_dir):
            #print("Dir: " + dirName)
            #print("Adding Dir " + dirName + " under " + parent_dir) 
            if not background_tab.file_tree.exists(dirName):
                background_tab.file_tree.insert("", "end", dirName, text = dirName.split("/")[-1])
            for subdir in subdirList:
                fq_subdir = dirName + "\\" + subdir
                #print("Adding subdir " + fq_subdir + " under " + dirName)
                background_tab.file_tree.insert(dirName, "end", iid = fq_subdir, text = subdir)
            for filename in fileList:
                if filename.split(".")[-1] in ["webp"]:
                    continue
                fq_filename = dirName + "\\" + filename
                #print("Adding file " + fq_filename + " under " + dirName)
                background_tab.file_tree.insert(dirName, "end", iid = fq_filename, text = filename)
           

    class ArtCitationWindow(tk.Toplevel):
        def __init__(self):
            super().__init__(height = 500, width = 1500)
            self.title("Citations Window")
            if "citations_dict.json" in os.listdir():
                with open("citations_dict.json", "r") as citation_file:
                    self.citations_dict = json.load(citation_file)
            else:
                self.citations_dict = dict()
        

            self.session_citations= set()
            
            self.citations = tk.Text(self)
            self.citations.place(x = 0, y = 0, height = 500, width = 1500)
                   
        def parse_msg(self, msg):
            logger.debug(msg)
            if msg[0] == "Audio":
                citeArt(msg[1])
           
        def citeArt(self, filename):
            #print("To cite:")
            #print(filename)
            if filename in self.citations_dict.keys() and filename not in self.session_citations:
                creator_name = self.citations_dict[filename]
                citation = filename.split(".")[0] + ": " + creator_name + "\n"

                self.session_citations.add(filename)
                self.citations.insert(tk.END, citation)

    menu_file.add_command(label = "Set Media Location", command = lambda: setMediaLocation(background_tab))
   



    # logWindow = LogWindow()

    # def write_log(msg):
        # global logWindow
        # logWindow.log.insert(tk.END, msg)
        
    # write_logger_id = logger.add(write_log)


    citation_window = ArtCitationWindow()
        








    tab_control = ttk.Notebook(root)

    background_window = BackgroundWindow(vlc_instance)
    background_tab = BackgroundTab(vlc_instance, background_window, citation_window, tab_control)
    tab_control.add(background_tab, text = "Background")

    initiative_tab = InitiativeTab(tab_control)
    tab_control.add(initiative_tab, text = "Initiative")

    tab_control.pack(expand = 1, fill = "both")

    print("Starting main loop")
    #root.protocol("WM_DELETE_WINDOW", exitHandler)
    root.mainloop()
    
    ############################
    ## End of program cleanup ##
    ############################
    # logger.remove(write_logger_id)
    logger.debug("Starting terminate procedure")
    if flask_server_p.is_alive():
        logger.debug("Found running Flask server")
        flask_server_p.terminate()
        flask_server_p.join()
        logger.debug("Flask server terminated")
    else:
        logger.debug("Did not find a running Flask server")
    t.cancel()