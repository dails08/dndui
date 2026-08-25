from PySide6.QtCore import QCoreApplication, Qt
import platform


def embed_vlc_widget(widget, vlc_instance):
    widget.setAttribute(Qt.WA_NativeWindow)
    if not widget.isVisible():
        widget.show()
    QCoreApplication.processEvents()

    local_os = platform.system()

    player = vlc_instance.media_player_new()
    print("Created new player:")
    print(player)
    if local_os == "Windows":
        player.set_hwnd(int(widget.winId()))
    elif local_os == "Linux":
        player.set_xwindow(int(widget.winId()))
    # print("With hwnd=" + str(int(widget.winId())))
    return player
