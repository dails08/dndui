import os
import ctypes
import json
# import multiprocessing as mp
from threading import Timer

import tkinter as tk

from tkinter import filedialog
from tkinter import ttk
import tkinter.font as tkFont
# from PIL import Image, ImageTk, ImageGrab
import pytweening as pt
from loguru import logger
import numpy as np
import requests
import gc
from io import BytesIO
import pathlib


import vlc



if __name__ == "__main__":
    # mp.freeze_support()
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

    class LogWindow(tk.Toplevel):
        def __init__(self):
            super().__init__(height = 500, width = 1500)
            self.title("Log Window")
            
            self.log = tk.Text(self)
            self.log.place(x = 0, y = 0, height = 500, width = 1500)
            
           
           




            
        
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
        def __init__(self, vlc_instance, background_window, controller):
            super().__init__(controller)
            self.vlc_instance = vlc_instance
            self.background_window = background_window
            
            # self.citations_window = citations_window
            
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
            
            # self.save_citation_btn = ttk.Button(self, text = "Save Citation", command = self.saveCitation)
            # self.save_citation_btn.place(x = 410, y = int(360*preview_scale) + 15 + 30 + 5)


            
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
            
        # def saveCitation(self):
        #     citation = self.citation_str_var.get()
        #     selection_iid = self.file_tree.selection()[0]
        #     item = self.file_tree.item(selection_iid)
        #     if len(self.file_tree.get_children(selection_iid)) > 0:
        #         # Don't cite whole folders of media
        #         return
        #     filename = item['text']
        #     self.citations_window.citations_dict[filename] = citation
        #     with open("citations_dict.json", "w") as citations_file:
        #         json.dump(self.citations_window.citations_dict, citations_file)

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
            # self.citations_window.citeArt(filename)
            
            
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
            # if filename in self.citations_window.citations_dict.keys():
            #     creator_name = self.citations_window.citations_dict[filename]
            #     self.citation_entry.insert(0, creator_name)
            self.previewMedia(selection_iid)

    vlc_instance = vlc.Instance()
    vlc_instance.log_unset()

    
    
    

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
           

    # class ArtCitationWindow(tk.Toplevel):
    #     def __init__(self):
    #         super().__init__(height = 500, width = 1500)
    #         self.title("Citations Window")
    #         if "citations_dict.json" in os.listdir():
    #             with open("citations_dict.json", "r") as citation_file:
    #                 self.citations_dict = json.load(citation_file)
    #         else:
    #             self.citations_dict = dict()
        

    #         self.session_citations= set()
            
    #         self.citations = tk.Text(self)
    #         self.citations.place(x = 0, y = 0, height = 500, width = 1500)
                   
        # def parse_msg(self, msg):
        #     logger.debug(msg)
        #     if msg[0] == "Audio":
        #         citeArt(msg[1])
           
        # def citeArt(self, filename):
        #     #print("To cite:")
        #     #print(filename)
        #     if filename in self.citations_dict.keys() and filename not in self.session_citations:
        #         creator_name = self.citations_dict[filename]
        #         citation = filename.split(".")[0] + ": " + creator_name + "\n"

        #         self.session_citations.add(filename)
        #         self.citations.insert(tk.END, citation)

    menu_file.add_command(label = "Set Media Location", command = lambda: setMediaLocation(background_tab))
   



    # logWindow = LogWindow()

    # def write_log(msg):
        # global logWindow
        # logWindow.log.insert(tk.END, msg)
        
    # write_logger_id = logger.add(write_log)


    # citation_window = ArtCitationWindow()
        








    tab_control = ttk.Notebook(root)

    background_window = BackgroundWindow(vlc_instance)
    background_tab = BackgroundTab(vlc_instance, background_window, tab_control)
    tab_control.add(background_tab, text = "Background")


    tab_control.pack(expand = 1, fill = "both")

    print("Starting main loop")
    #root.protocol("WM_DELETE_WINDOW", exitHandler)
    root.mainloop()
    
    ############################
    ## End of program cleanup ##
    ############################
    # logger.remove(write_logger_id)
    logger.debug("Starting terminate procedure")
