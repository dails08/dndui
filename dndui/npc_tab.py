import json
import os

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from dndui.background_tab import CITATION_FILE, TAGS_FILE
from dndui.images import qimage_from_file, to_pixmap

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "gif", "webp"}
ICON_SIZE = 96
PREVIEW_SIZE = 320


class NPCTab(QWidget):
    def __init__(self, citations_window, npc_root_dir):
        super().__init__()
        self.citations_window = citations_window
        self.npc_root_dir = npc_root_dir

        if os.path.exists(TAGS_FILE):
            with open(TAGS_FILE, "r") as tags_file:
                self.tags_dict = json.load(tags_file)
        else:
            self.tags_dict = dict()

        self.current_image = None
        self.current_filename = None

        self.filter_entry = QLineEdit()
        self.filter_entry.setPlaceholderText("Filter by name or tag...")
        self.filter_entry.textChanged.connect(self.applyFilter)

        self.npc_list = QListWidget()
        self.npc_list.setViewMode(QListWidget.IconMode)
        self.npc_list.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.npc_list.setResizeMode(QListWidget.Adjust)
        self.npc_list.setMovement(QListWidget.Static)
        self.npc_list.setWordWrap(True)
        self.npc_list.setSpacing(8)
        self.npc_list.itemSelectionChanged.connect(self.onSelectionChanged)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.filter_entry)
        left_layout.addWidget(self.npc_list)

        self.name_label = QLabel()
        self.name_label.setProperty("role", "heading")
        self.name_label.setAlignment(Qt.AlignCenter)

        self.preview_label = QLabel()
        self.preview_label.setFixedSize(PREVIEW_SIZE, PREVIEW_SIZE)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: black; border-radius: 6px;")

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self.copyFcn)

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
        right_layout.addWidget(self.name_label)
        right_layout.addWidget(self.preview_label, 0, Qt.AlignHCenter)
        right_layout.addWidget(self.copy_btn)
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

        self.refreshList()

    def collectImageFiles(self):
        files = []
        for dirName, _subdirList, fileList in os.walk(self.npc_root_dir):
            for filename in fileList:
                if filename.rsplit(".", 1)[-1].lower() in IMAGE_EXTENSIONS:
                    files.append(os.path.join(dirName, filename))
        return sorted(files, key=lambda p: os.path.basename(p).lower())

    def fileMatches(self, filename, name_filter):
        if name_filter in filename.lower():
            return True
        tags = self.tags_dict.get(filename, [])
        return any(name_filter in tag.lower() for tag in tags)

    def refreshList(self):
        # Rescans disk and rebuilds icons; only call when the directory contents
        # may have changed. Filtering alone should use applyFilter().
        self.npc_list.clear()
        if not self.npc_root_dir or not os.path.isdir(self.npc_root_dir):
            return

        for fq_path in self.collectImageFiles():
            filename = os.path.basename(fq_path)
            image = qimage_from_file(fq_path)
            item = QListWidgetItem(QIcon(to_pixmap(image)), filename)
            item.setData(Qt.UserRole, fq_path)
            self.npc_list.addItem(item)

        self.applyFilter()

    def applyFilter(self):
        name_filter = self.filter_entry.text().strip().lower()
        for i in range(self.npc_list.count()):
            item = self.npc_list.item(i)
            item.setHidden(bool(name_filter) and not self.fileMatches(item.text(), name_filter))

    def onSelectionChanged(self):
        selected = self.npc_list.selectedItems()
        if not selected:
            return
        item = selected[0]
        fq_path = item.data(Qt.UserRole)
        filename = item.text()

        self.current_filename = filename
        self.current_image = qimage_from_file(fq_path)

        self.name_label.setText(filename)
        pixmap = to_pixmap(self.current_image).scaled(
            PREVIEW_SIZE, PREVIEW_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(pixmap)

        self.citation_entry.clear()
        if filename in self.citations_window.citations_dict:
            self.citation_entry.setText(self.citations_window.citations_dict[filename])

        self.tags_entry.clear()
        if filename in self.tags_dict:
            self.tags_entry.setText(", ".join(self.tags_dict[filename]))

    def copyFcn(self):
        if self.current_image is None or not self.current_filename:
            return
        QGuiApplication.clipboard().setImage(self.current_image)
        self.citations_window.citeArt(self.current_filename)

    def saveCitation(self):
        if not self.current_filename:
            return
        self.citations_window.citations_dict[self.current_filename] = self.citation_entry.text()
        with open(CITATION_FILE, "w") as citations_file:
            json.dump(self.citations_window.citations_dict, citations_file)

    def saveTags(self):
        if not self.current_filename:
            return
        tags = [tag.strip() for tag in self.tags_entry.text().split(",") if tag.strip()]
        self.tags_dict[self.current_filename] = tags
        with open(TAGS_FILE, "w") as tags_file:
            json.dump(self.tags_dict, tags_file)
