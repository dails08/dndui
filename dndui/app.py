import multiprocessing as mp
import sys

import requests
import vlc
from loguru import logger
from PySide6.QtWidgets import QApplication

from dndui import config as config_module
from dndui import style
from dndui.ipc import FlaskQueuePoller, start_flask_server
from dndui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(style.load_stylesheet())

    vlc_instance = vlc.Instance()
    vlc_instance.log_unset()

    queue = mp.Queue()

    logger.debug("Starting Flask process")
    flask_server_process = mp.Process(target=start_flask_server, args=[queue])
    flask_server_process.start()
    logger.debug("Testing Flask process")
    resp = requests.get("http://localhost:5000/msg/test_message")
    logger.debug("Flask test result: " + str(resp.status_code))

    config = config_module.load_config()

    window = MainWindow(vlc_instance, config)
    window.show()

    def onMessage(msg):
        print(msg)
        print("message received: ", msg)
        if msg.split("/")[0] == "CitationWindow":
            window.citation_window.parse_msg(msg.split("/")[1:])

    poller = FlaskQueuePoller(queue)
    poller.messageReceived.connect(onMessage)
    poller.start()

    exit_code = app.exec()

    logger.debug("Starting terminate procedure")
    poller.stop()
    if flask_server_process.is_alive():
        logger.debug("Found running Flask server")
        flask_server_process.terminate()
        flask_server_process.join()
        logger.debug("Flask server terminated")
    else:
        logger.debug("Did not find a running Flask server")

    return exit_code
