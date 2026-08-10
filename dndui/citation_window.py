import json
import os

from loguru import logger
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

CITATION_FILE = "citation_dict.json"


class ArtCitationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Citations Window")
        self.resize(1500, 500)

        if os.path.exists(CITATION_FILE):
            with open(CITATION_FILE, "r") as citation_file:
                self.citations_dict = json.load(citation_file)
        else:
            self.citations_dict = dict()

        self.session_citations = set()

        self.citations = QTextEdit()
        self.citations.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.citations)

        self.show()

    def parse_msg(self, msg):
        logger.debug(msg)
        if msg[0] == "Audio":
            self.citeArt(msg[1])

    def citeArt(self, filename):
        if filename in self.citations_dict.keys() and filename not in self.session_citations:
            creator_name = self.citations_dict[filename]
            citation = filename.split(".")[0] + ": " + creator_name + "\n"

            self.session_citations.add(filename)
            self.citations.insertPlainText(citation)
