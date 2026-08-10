import json
import os

from PySide6.QtCore import QMimeData, QPoint, Qt
from PySide6.QtGui import QDrag, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from dndui import images

LIBRARY_DIR = "initiative_library_images"
LIBRARY_FILE = "initiative_library.json"
LIBRARY_MIME_TYPE = "application/x-dndui-library-name"


class Library:
    def __init__(self):
        os.makedirs(LIBRARY_DIR, exist_ok=True)
        if os.path.exists(LIBRARY_FILE):
            with open(LIBRARY_FILE, "r") as library_file:
                self.entries = json.load(library_file)
        else:
            self.entries = dict()

    def __contains__(self, name):
        return name in self.entries

    def names(self):
        return sorted(self.entries.keys())

    def load_image(self, name):
        filename = self.entries.get(name)
        if filename is None:
            return None
        path = os.path.join(LIBRARY_DIR, filename)
        if not os.path.exists(path):
            return None
        return images.qimage_from_file(path)

    def save(self, name, avatar_image):
        if not name or avatar_image is None or name in self.entries:
            return
        safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip() or "unnamed"
        filename = safe_name + ".png"
        counter = 1
        while os.path.exists(os.path.join(LIBRARY_DIR, filename)):
            filename = safe_name + "_" + str(counter) + ".png"
            counter += 1
        images.save_png(avatar_image, os.path.join(LIBRARY_DIR, filename))
        self.entries[name] = filename
        self._persist()

    def remove(self, name):
        filename = self.entries.pop(name, None)
        if filename is not None:
            path = os.path.join(LIBRARY_DIR, filename)
            if os.path.exists(path):
                os.remove(path)
        self._persist()

    def _persist(self):
        with open(LIBRARY_FILE, "w") as library_file:
            json.dump(self.entries, library_file)


class LibraryListWidget(QListWidget):
    def __init__(self, library, parent=None):
        super().__init__(parent)
        self.library = library
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragOnly)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item is None:
            return
        name = item.text()

        mime_data = QMimeData()
        mime_data.setData(LIBRARY_MIME_TYPE, name.encode("utf-8"))

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        avatar_image = self.library.load_image(name)
        if avatar_image is not None:
            thumb = images.scaled_pixmap(avatar_image, 60, 60)
            drag.setPixmap(thumb)
            drag.setHotSpot(QPoint(30, 30))

        drag.exec(Qt.CopyAction)


class LibraryPanel(QWidget):
    def __init__(self, library, parent=None):
        super().__init__(parent)
        self.library = library

        heading = QLabel("Library")
        heading.setProperty("role", "heading")

        self.filter_entry = QLineEdit()
        self.filter_entry.setPlaceholderText("Filter by name...")
        self.filter_entry.textChanged.connect(self.refresh)

        self.list_widget = LibraryListWidget(self.library)
        self.list_widget.itemSelectionChanged.connect(self.updatePreview)

        delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self.list_widget)
        delete_shortcut.setContext(Qt.WidgetShortcut)
        delete_shortcut.activated.connect(self.removeSelected)

        self.preview_label = QLabel()
        self.preview_label.setFixedSize(100, 100)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: black; border-radius: 6px;")

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.removeSelected)

        layout = QVBoxLayout(self)
        layout.addWidget(heading)
        layout.addWidget(self.filter_entry)
        layout.addWidget(self.list_widget, 1)
        layout.addWidget(self.preview_label, 0, Qt.AlignHCenter)
        layout.addWidget(self.remove_btn)

        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        filter_text = self.filter_entry.text().strip().lower()
        for name in self.library.names():
            if filter_text and filter_text not in name.lower():
                continue
            self.list_widget.addItem(name)

    def updatePreview(self):
        selected = self.list_widget.selectedItems()
        if not selected:
            return
        avatar_image = self.library.load_image(selected[0].text())
        if avatar_image is None:
            return
        self.preview_label.setPixmap(images.scaled_pixmap(avatar_image, 100, 100))

    def removeSelected(self):
        selected = self.list_widget.selectedItems()
        if not selected:
            return
        self.library.remove(selected[0].text())
        self.preview_label.clear()
        self.refresh()

    def saveEntity(self, name, avatar_image):
        self.library.save(name, avatar_image)
        self.refresh()
