import os
import sys

from flask import Flask
from PySide6.QtCore import QObject, QTimer, Signal


def start_flask_server(queue):
    if getattr(sys, "frozen", False):
        template_folder = os.path.join(sys._MEIPASS, "templates")
        static_folder = os.path.join(sys._MEIPASS, "static")
        app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    else:
        app = Flask(__name__)

    @app.route("/msg/<msg>")
    def rxMessage(msg):
        queue.put(msg)
        return "ok"

    app.run(debug=False, port=5000)


class FlaskQueuePoller(QObject):
    messageReceived = Signal(str)

    def __init__(self, queue, interval_ms=100, parent=None):
        super().__init__(parent)
        self.queue = queue
        self.timer = QTimer(self)
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self._poll)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def _poll(self):
        while not self.queue.empty():
            self.messageReceived.emit(self.queue.get())
