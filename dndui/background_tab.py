import json
import os

import vlc
from loguru import logger
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from dndui.vlc_embed import embed_vlc_widget

TAGS_FILE = "tags_dict.json"
CITATION_FILE = "citation_dict.json"
INITIAL_MRL = r"C:\Users\Christopher\Dropbox\CoS\OBS Rework\bg\AT2.jpg"
EXCLUDED_EXTENSIONS = ["webp"]


class BackgroundTab(QWidget):
    def __init__(self, vlc_instance, background_window, citations_window, media_root_dir):
        super().__init__()
        self.vlc_instance = vlc_instance
        self.background_window = background_window
        self.citations_window = citations_window
        self.media_root_dir = media_root_dir

        if os.path.exists(TAGS_FILE):
            with open(TAGS_FILE, "r") as tags_file:
                self.tags_dict = json.load(tags_file)
        else:
            self.tags_dict = dict()

        self.path_items = {}

        self.tag_filter_entry = QLineEdit()
        self.tag_filter_entry.setPlaceholderText("Filter by name or tag...")
        self.tag_filter_entry.textChanged.connect(self.refreshFileTree)

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.itemActivated.connect(self.onItemActivated)
        self.file_tree.itemSelectionChanged.connect(self.onSelectionChanged)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.tag_filter_entry)
        left_layout.addWidget(self.file_tree)

        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("bgPreviewFrame")
        self.preview_frame.setFixedSize(384, 216)

        self.citation_entry = QLineEdit()
        self.citation_entry.setPlaceholderText("Citation")
        self.save_citation_btn = QPushButton("Save Citation")
        self.save_citation_btn.clicked.connect(self.saveCitation)

        self.tags_entry = QLineEdit()
        self.tags_entry.setPlaceholderText("Tags (comma-separated)")
        self.save_tags_btn = QPushButton("Save Tags")
        self.save_tags_btn.clicked.connect(self.saveTags)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.preview_frame)
        right_layout.addSpacing(8)
        right_layout.addWidget(self.citation_entry)
        right_layout.addWidget(self.save_citation_btn)
        right_layout.addSpacing(8)
        right_layout.addWidget(self.tags_entry)
        right_layout.addWidget(self.save_tags_btn)
        right_layout.addStretch(1)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

        self.refreshFileTree()

        self.preview_player = embed_vlc_widget(self.preview_frame, self.vlc_instance)
        self.preview_player.audio_set_mute(True)

        self.preview_list_player = self.vlc_instance.media_list_player_new()
        self.preview_list_player.set_media_player(self.preview_player)
        self.preview_list_player.set_playback_mode(vlc.PlaybackMode.repeat)

        self.preview_media_list = self.vlc_instance.media_list_new([INITIAL_MRL])
        self.preview_list_player.set_media_list(self.preview_media_list)
        self.preview_list_player.play_item_at_index(0)

    def populateFileTree(self, media_root_dir, tag_filter=""):
        tag_filter = tag_filter.strip().lower()

        dirs = {}
        for dirName, subdirList, fileList in os.walk(media_root_dir):
            fileList = [f for f in fileList if f.split(".")[-1] not in EXCLUDED_EXTENSIONS]
            dirs[dirName] = (subdirList, fileList)

        def fileMatches(filename):
            if not tag_filter:
                return True
            if tag_filter in filename.lower():
                return True
            tags = self.tags_dict.get(filename, [])
            return any(tag_filter in tag.lower() for tag in tags)

        match_cache = {}

        def dirHasMatch(dirName):
            if dirName in match_cache:
                return match_cache[dirName]
            subdirList, fileList = dirs[dirName]
            has_match = any(fileMatches(f) for f in fileList) or any(
                dirHasMatch(dirName + "\\" + subdir) for subdir in subdirList
            )
            match_cache[dirName] = has_match
            return has_match

        for dirName, (subdirList, fileList) in dirs.items():
            if tag_filter and not dirHasMatch(dirName):
                continue
            if dirName not in self.path_items:
                item = QTreeWidgetItem([os.path.basename(dirName)])
                item.setData(0, Qt.UserRole, dirName)
                self.file_tree.addTopLevelItem(item)
                self.path_items[dirName] = item
            parent_item = self.path_items[dirName]
            for subdir in subdirList:
                fq_subdir = dirName + "\\" + subdir
                if tag_filter and not dirHasMatch(fq_subdir):
                    continue
                item = QTreeWidgetItem([subdir])
                item.setData(0, Qt.UserRole, fq_subdir)
                parent_item.addChild(item)
                self.path_items[fq_subdir] = item
            for filename in fileList:
                if not fileMatches(filename):
                    continue
                fq_filename = dirName + "\\" + filename
                item = QTreeWidgetItem([filename])
                item.setData(0, Qt.UserRole, fq_filename)
                parent_item.addChild(item)
                self.path_items[fq_filename] = item

    def refreshFileTree(self):
        self.file_tree.clear()
        self.path_items = {}
        self.populateFileTree(self.media_root_dir, self.tag_filter_entry.text())

    def playMedia(self, mrl):
        logger.debug("Sending " + mrl + " to bg window")
        self.background_window.playMedia(mrl)

    def previewMedia(self, mrl):
        self.preview_media_list = self.vlc_instance.media_list_new([mrl])
        self.preview_list_player.set_media_list(self.preview_media_list)
        self.preview_list_player.play_item_at_index(0)

    def onItemActivated(self, item, column):
        if item.childCount() > 0:
            # Don't play whole folders of media
            return
        fq_path = item.data(0, Qt.UserRole)
        filename = item.text(0)
        while filename.startswith("_ex_"):
            filename = filename[4:]
        self.playMedia(fq_path)
        self.citations_window.citeArt(filename)

    def onSelectionChanged(self):
        selected = self.file_tree.selectedItems()
        if not selected:
            return
        item = selected[0]
        if item.childCount() > 0:
            # Don't preview whole folders of media
            return
        fq_path = item.data(0, Qt.UserRole)
        filename = item.text(0)
        while filename.startswith("_ex_"):
            filename = filename[4:]

        self.citation_entry.clear()
        if filename in self.citations_window.citations_dict.keys():
            self.citation_entry.setText(self.citations_window.citations_dict[filename])

        self.tags_entry.clear()
        if filename in self.tags_dict.keys():
            self.tags_entry.setText(", ".join(self.tags_dict[filename]))

        self.previewMedia(fq_path)

    def saveCitation(self):
        selected = self.file_tree.selectedItems()
        if not selected:
            return
        item = selected[0]
        if item.childCount() > 0:
            # Don't cite whole folders of media
            return
        filename = item.text(0)
        self.citations_window.citations_dict[filename] = self.citation_entry.text()
        with open(CITATION_FILE, "w") as citations_file:
            json.dump(self.citations_window.citations_dict, citations_file)

    def saveTags(self):
        selected = self.file_tree.selectedItems()
        if not selected:
            return
        item = selected[0]
        if item.childCount() > 0:
            # Don't tag whole folders of media
            return
        tags = [tag.strip() for tag in self.tags_entry.text().split(",") if tag.strip()]
        filename = item.text(0)
        self.tags_dict[filename] = tags
        with open(TAGS_FILE, "w") as tags_file:
            json.dump(self.tags_dict, tags_file)
