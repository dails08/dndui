import vlc
from loguru import logger
from PySide6.QtWidgets import QWidget

from dndui.vlc_embed import embed_vlc_widget

INITIAL_MRL = r"C:\Users\Christopher\Dropbox\CoS\OBS Rework\bg\AT2.jpg"


class BackgroundWindow(QWidget):
    def __init__(self, vlc_instance):
        super().__init__()
        self.setWindowTitle("Background Display")
        self.setFixedSize(1920, 1080)

        self.display_frame = QWidget(self)
        self.display_frame.setObjectName("bgDisplayFrame")
        self.display_frame.setGeometry(0, 0, 1920, 1080)

        self.vlc_instance = vlc_instance

        self.show()

        self.player = embed_vlc_widget(self.display_frame, self.vlc_instance)
        self.player.audio_set_mute(True)

        self.list_player = self.vlc_instance.media_list_player_new()
        self.list_player.set_media_player(self.player)
        self.list_player.set_playback_mode(vlc.PlaybackMode.repeat)

        self.media_list = self.vlc_instance.media_list_new([INITIAL_MRL])
        self.list_player.set_media_list(self.media_list)
        self.list_player.play_item_at_index(0)

    def playMedia(self, mrl):
        logger.debug("Received " + mrl + " at bg window")
        self.media_list = self.vlc_instance.media_list_new([mrl])
        self.list_player.set_media_list(self.media_list)
        self.list_player.play_item_at_index(0)
