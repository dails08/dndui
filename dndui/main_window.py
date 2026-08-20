from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QTabWidget

from dndui import config as config_module
from dndui.background_tab import BackgroundTab
from dndui.background_window import BackgroundWindow
from dndui.citation_window import ArtCitationWindow
from dndui.initiative_tab import InitiativeTab
from dndui.npc_tab import NPCTab


class MainWindow(QMainWindow):
    def __init__(self, vlc_instance, config):
        super().__init__()
        self.setWindowTitle("The Digital DM")
        self.resize(1050, 650)

        self.vlc_instance = vlc_instance
        self.config = config

        self.citation_window = ArtCitationWindow()

        self.background_window = BackgroundWindow(vlc_instance)

        media_root_dir = config.get("media_root_dir", config_module.DEFAULT_MEDIA_ROOT_DIR)
        self.background_tab = BackgroundTab(
            vlc_instance, self.background_window, self.citation_window, media_root_dir
        )

        self.initiative_tab = InitiativeTab()

        npc_root_dir = config.get("npc_root_dir", config_module.DEFAULT_NPC_ROOT_DIR)
        self.npc_tab = NPCTab(self.citation_window, npc_root_dir)

        tabs = QTabWidget()
        tabs.addTab(self.background_tab, "Background")
        tabs.addTab(self.initiative_tab, "Initiative")
        tabs.addTab(self.npc_tab, "NPCs")
        self.setCentralWidget(tabs)

        self._buildMenu()

    def _buildMenu(self):
        menu_file = self.menuBar().addMenu("File")
        set_media_location_action = QAction("Set Media Location", self)
        set_media_location_action.triggered.connect(self.setMediaLocation)
        menu_file.addAction(set_media_location_action)

        set_npc_location_action = QAction("Set NPC Location", self)
        set_npc_location_action.triggered.connect(self.setNPCLocation)
        menu_file.addAction(set_npc_location_action)

    def setMediaLocation(self):
        media_root_dir = QFileDialog.getExistingDirectory(self, "Set Media Location", str(Path.home()))
        if not media_root_dir:
            return

        self.background_tab.media_root_dir = media_root_dir
        self.background_tab.refreshFileTree()

        self.config["media_root_dir"] = media_root_dir
        config_module.save_config(self.config)

    def setNPCLocation(self):
        npc_root_dir = QFileDialog.getExistingDirectory(self, "Set NPC Location", str(Path.home()))
        if not npc_root_dir:
            return

        self.npc_tab.npc_root_dir = npc_root_dir
        self.npc_tab.refreshList()

        self.config["npc_root_dir"] = npc_root_dir
        config_module.save_config(self.config)

    def closeEvent(self, event):
        self.background_window.close()
        self.citation_window.close()
        self.initiative_tab.display_window.close()
        super().closeEvent(event)
        QApplication.instance().quit()
