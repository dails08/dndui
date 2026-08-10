import pyperclip
import requests
from bs4 import BeautifulSoup
from loguru import logger
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from dndui.images import qimage_from_bytes, qimage_from_clipboard, scaled_pixmap
from dndui.initiative_window import (
    AVATAR_SIZE,
    GROUP_SPACING,
    OFFSCREEN_LEFT_X,
    OFFSCREEN_X,
    InitiativeDisplayWindow,
)
from dndui.library import LIBRARY_MIME_TYPE, Library, LibraryPanel


class TurnOrderListWidget(QListWidget):
    entityDropped = Signal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setDefaultDropAction(Qt.CopyAction)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(LIBRARY_MIME_TYPE):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(LIBRARY_MIME_TYPE):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if not mime_data.hasFormat(LIBRARY_MIME_TYPE):
            event.ignore()
            return

        name = bytes(mime_data.data(LIBRARY_MIME_TYPE)).decode("utf-8")

        index = self.indexAt(event.position().toPoint()).row()
        if index == -1:
            index = self.count()
        elif self.dropIndicatorPosition() == QAbstractItemView.BelowItem:
            index += 1

        self.entityDropped.emit(name, index)
        event.acceptProposedAction()


class InitiativeTab(QWidget):
    def __init__(self):
        super().__init__()

        self.display_window = InitiativeDisplayWindow()

        self.render_list = []
        self.initiative_group_list = []
        self.prep_img = None

        self.library = Library()
        self.library_panel = LibraryPanel(self.library)

        self.turn_order_list = TurnOrderListWidget()
        self.turn_order_list.entityDropped.connect(self.addFromLibrary)

        self.pull_initiative_btn = QPushButton("Pull Order")
        self.pull_initiative_btn.clicked.connect(self.parseDNDB)

        self.ship_btn = QPushButton("Ship")
        self.ship_btn.setProperty("role", "primary")
        self.ship_btn.clicked.connect(self.shipFcn)

        self.drop_btn = QPushButton("Drop")
        self.drop_btn.clicked.connect(self.dropFcn)

        self.move_up_btn = QPushButton("Move Up")
        self.move_up_btn.clicked.connect(self.moveUpFcn)

        self.move_down_btn = QPushButton("Move Down")
        self.move_down_btn.clicked.connect(self.moveDownFcn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clearList)

        self.cycle_fwd_btn = QPushButton("Cycle Forward")
        self.cycle_fwd_btn.clicked.connect(self.cycleForward)

        self.cycle_bwd_btn = QPushButton("Cycle Backward")
        self.cycle_bwd_btn.clicked.connect(self.cycleBackward)

        turn_order_controls = QHBoxLayout()
        turn_order_controls.addWidget(self.pull_initiative_btn)
        turn_order_controls.addWidget(self.ship_btn)
        turn_order_controls.addWidget(self.drop_btn)
        turn_order_controls.addWidget(self.move_up_btn)
        turn_order_controls.addWidget(self.move_down_btn)
        turn_order_controls.addWidget(self.clear_btn)

        cycle_controls = QHBoxLayout()
        cycle_controls.addWidget(self.cycle_fwd_btn)
        cycle_controls.addWidget(self.cycle_bwd_btn)

        turn_order_column = QWidget()
        turn_order_layout = QVBoxLayout(turn_order_column)
        turn_order_layout.addWidget(self.turn_order_list, 1)
        turn_order_layout.addLayout(turn_order_controls)
        turn_order_layout.addLayout(cycle_controls)

        self.prep_name_entry = QLineEdit("Name")

        self.pull_pic_btn = QPushButton("Pull Pic")
        self.pull_pic_btn.clicked.connect(self.pullPicFcn)

        self.prep_preview_label = QLabel()
        self.prep_preview_label.setFixedSize(AVATAR_SIZE[0], AVATAR_SIZE[1])
        self.prep_preview_label.setAlignment(Qt.AlignCenter)
        self.prep_preview_label.setStyleSheet("background-color: black; border-radius: 6px;")

        self.add_above_btn = QPushButton("Add Above")
        self.add_above_btn.clicked.connect(self.addAboveFcn)

        self.add_below_btn = QPushButton("Add Below")
        self.add_below_btn.clicked.connect(self.addBelowFcn)

        self.copy_encounter_script_btn = QPushButton("Copy Encounter Script")
        self.copy_encounter_script_btn.clicked.connect(self.copyEncounterScript)

        prep_column = QWidget()
        prep_layout = QVBoxLayout(prep_column)
        prep_layout.addWidget(self.prep_name_entry)
        prep_layout.addWidget(self.pull_pic_btn)
        prep_layout.addWidget(self.prep_preview_label, 0, Qt.AlignHCenter)
        prep_layout.addWidget(self.add_above_btn)
        prep_layout.addWidget(self.add_below_btn)
        prep_layout.addStretch(1)
        prep_layout.addWidget(self.copy_encounter_script_btn)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(turn_order_column)
        splitter.addWidget(prep_column)
        splitter.addWidget(self.library_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)

        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

    def copyEncounterScript(self):
        pyperclip.copy("navigator.clipboard.writeText(document.body.innerHTML);")

    def clearList(self):
        while self.turn_order_list.count() > 0:
            self.turn_order_list.takeItem(0)
            self.initiative_group_list.pop(0).destroy()

    def setInitGroupsSpacing(self):
        for i in range(len(self.initiative_group_list)):
            self.initiative_group_list[i].moveTo((i * GROUP_SPACING, 0))

    def parseDNDB(self):
        logger.debug("Parsing dndb content")
        render_list = []

        logger.debug("Looking for avatars...")
        html = pyperclip.paste()
        soup = BeautifulSoup(html, features="html.parser")
        avatars_list = soup.find_all("div", class_="combatant-card__mid-bit combatant-summary")

        logger.debug("done, found " + str(len(avatars_list)))
        for avatar in avatars_list:
            content = requests.get(avatar.img["src"]).content
            avatar_image = qimage_from_bytes(content)

            avatar_name = avatar.find_all("div", class_="combatant-summary__name")[0].string
            render_list.append((avatar_image, avatar_name))
            logger.debug("Parsed " + avatar_name)
        self.render_list = render_list
        logger.debug("Set internal render list")
        self.turn_order_list.clear()
        for elem in self.render_list:
            self.turn_order_list.addItem(elem[1])
        logger.debug("Set new initiative list contents.")

    def shipFcn(self):
        for elem in self.initiative_group_list:
            elem.destroy()
        self.initiative_group_list = []
        for avatar_image, name in self.render_list:
            logger.debug(name)
            group = self.display_window.addGroup(name, avatar_image, location=(0, 0))
            self.initiative_group_list.append(group)
            self.library_panel.saveEntity(name, avatar_image)
        self.setInitGroupsSpacing()

    def dropFcn(self):
        selection = self.turn_order_list.currentRow()
        if selection < 0:
            return
        logger.debug("Removing " + str(selection) + ": " + self.initiative_group_list[selection].name)
        self.turn_order_list.takeItem(selection)
        self.initiative_group_list.pop(selection).destroy()
        self.setInitGroupsSpacing()

    def pullPicFcn(self):
        self.prep_img = qimage_from_clipboard()
        logger.debug("Pulled from clipboard")
        if self.prep_img is not None:
            self.prep_preview_label.setPixmap(scaled_pixmap(self.prep_img, AVATAR_SIZE[0], AVATAR_SIZE[1]))

    def addAboveFcn(self):
        logger.debug("Adding above")
        # defaults to the top when nothing is selected (e.g. empty list)
        row = self.turn_order_list.currentRow()
        selection = row if row >= 0 else 0

        to_name = self.prep_name_entry.text()
        to_avatar = self.prep_img
        group = self.display_window.addGroup(to_name, to_avatar, location=(OFFSCREEN_X, 0))
        self.turn_order_list.insertItem(selection, to_name)
        self.initiative_group_list.insert(selection, group)
        if to_avatar is not None:
            self.library_panel.saveEntity(to_name, to_avatar)
        self.setInitGroupsSpacing()

    def addBelowFcn(self):
        logger.debug("Adding below")
        # defaults to the top when nothing is selected (e.g. empty list)
        row = self.turn_order_list.currentRow()
        insert_index = row + 1 if row >= 0 else 0

        to_name = self.prep_name_entry.text()
        to_avatar = self.prep_img
        group = self.display_window.addGroup(to_name, to_avatar, location=(OFFSCREEN_X, 0))
        self.turn_order_list.insertItem(insert_index, to_name)
        self.initiative_group_list.insert(insert_index, group)
        if to_avatar is not None:
            self.library_panel.saveEntity(to_name, to_avatar)
        self.setInitGroupsSpacing()

    def moveUpFcn(self):
        logger.debug("Moving up")
        selection = self.turn_order_list.currentRow()
        logger.debug("Selection is " + str(selection))
        if selection > 0:
            to_name = self.turn_order_list.item(selection).text()

            logger.debug("Copying " + to_name + " down")
            self.turn_order_list.insertItem(selection - 1, to_name)
            self.turn_order_list.takeItem(selection + 1)

            self.initiative_group_list[selection - 1], self.initiative_group_list[selection] = (
                self.initiative_group_list[selection],
                self.initiative_group_list[selection - 1],
            )

            self.turn_order_list.setCurrentRow(selection - 1)
            self.setInitGroupsSpacing()

    def moveDownFcn(self):
        logger.debug("Moving down")
        selection = self.turn_order_list.currentRow()
        logger.debug("Selection is " + str(selection))
        if 0 <= selection < self.turn_order_list.count() - 1:
            to_name = self.turn_order_list.item(selection + 1).text()

            logger.debug("Copying " + to_name + " up")
            self.turn_order_list.insertItem(selection, to_name)
            self.turn_order_list.takeItem(selection + 2)

            self.initiative_group_list[selection + 1], self.initiative_group_list[selection] = (
                self.initiative_group_list[selection],
                self.initiative_group_list[selection + 1],
            )

            self.turn_order_list.setCurrentRow(selection + 1)
            self.setInitGroupsSpacing()

    def cycleForward(self):
        if not self.initiative_group_list:
            return
        self.initiative_group_list[0].moveTo((OFFSCREEN_X, 0), animate=False)
        self.initiative_group_list.append(self.initiative_group_list.pop(0))
        self.turn_order_list.addItem(self.turn_order_list.item(0).text())
        self.turn_order_list.takeItem(0)
        self.setInitGroupsSpacing()

    def cycleBackward(self):
        if not self.initiative_group_list:
            return
        self.initiative_group_list[-1].moveTo((OFFSCREEN_LEFT_X, 0), animate=False)
        self.initiative_group_list.insert(0, self.initiative_group_list.pop())
        last_index = self.turn_order_list.count() - 1
        self.turn_order_list.insertItem(0, self.turn_order_list.item(last_index).text())
        self.turn_order_list.takeItem(self.turn_order_list.count() - 1)
        self.setInitGroupsSpacing()

    def addFromLibrary(self, name, index):
        avatar_image = self.library.load_image(name)
        if avatar_image is None:
            return
        index = max(0, min(index, len(self.initiative_group_list)))
        group = self.display_window.addGroup(name, avatar_image, location=(OFFSCREEN_X, 0))
        self.turn_order_list.insertItem(index, name)
        self.initiative_group_list.insert(index, group)
        self.setInitGroupsSpacing()
