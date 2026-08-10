from PySide6.QtCore import QCoreApplication, Qt


def embed_vlc_widget(widget, vlc_instance):
    widget.setAttribute(Qt.WA_NativeWindow)
    if not widget.isVisible():
        widget.show()
    QCoreApplication.processEvents()

    player = vlc_instance.media_player_new()
    player.set_hwnd(int(widget.winId()))
    return player
