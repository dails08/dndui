from loguru import logger
from PySide6.QtCore import QEasingCurve, QPointF, QPropertyAnimation, Qt
from PySide6.QtGui import QFont, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsObject,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QWidget,
)

from dndui.images import scaled_pixmap

AVATAR_SIZE = (200, 200)
CAMEO_SIZE = (250, 275)
UPPER_BUFFER = 15
LEFT_BUFFER = 10
GROUP_SPACING = 250
OFFSCREEN_X = 2000
OFFSCREEN_LEFT_X = -300
ANIMATION_DURATION_MS = 200
CAMEO_ASSET_PATH = "./assets/init_cameo.png"


class InitiativeGroupItem(QGraphicsObject):
    def __init__(
        self,
        name,
        avatar_image,
        cameo_pixmap,
        avatar_size=AVATAR_SIZE,
        cameo_size=CAMEO_SIZE,
        upper_buffer=UPPER_BUFFER,
        left_buffer=LEFT_BUFFER,
        location=(0, 0),
        parent=None,
    ):
        super().__init__(parent)
        self.name = name
        self._anim = None

        avatar_pixmap = scaled_pixmap(avatar_image, avatar_size[0], avatar_size[1])

        self.cameo_item = QGraphicsPixmapItem(cameo_pixmap, self)
        self.cameo_item.setPos(left_buffer - 25, upper_buffer - 5)
        self.cameo_item.setZValue(1)

        self.avatar_item = QGraphicsPixmapItem(avatar_pixmap, self)
        self.avatar_item.setPos(left_buffer, upper_buffer)
        self.avatar_item.setZValue(0)

        self.name_item = QGraphicsTextItem(name, self)
        font = QFont("Matura MT Script Capitals", 12, QFont.Bold)
        self.name_item.setFont(font)
        self.name_item.setDefaultTextColor(Qt.white)
        self.name_item.setTextWidth(200)
        text_option = self.name_item.document().defaultTextOption()
        text_option.setAlignment(Qt.AlignCenter)
        self.name_item.document().setDefaultTextOption(text_option)
        self.name_item.setZValue(2)
        name_x = left_buffer + avatar_size[0] / 2 - 100
        name_y = upper_buffer + avatar_size[1] + 40 - self.name_item.boundingRect().height() / 2
        self.name_item.setPos(name_x, name_y)

        self.setPos(location[0], location[1])

    def boundingRect(self):
        return self.childrenBoundingRect()

    def paint(self, painter, option, widget=None):
        pass

    def moveTo(self, dest, animate=True):
        if self._anim is not None:
            self._anim.stop()
            self._anim = None
        if not animate:
            self.setPos(dest[0], dest[1])
            return
        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(ANIMATION_DURATION_MS)
        anim.setEasingCurve(QEasingCurve.OutQuint)
        anim.setEndValue(QPointF(dest[0], dest[1]))
        anim.start()
        self._anim = anim

    def destroy(self):
        logger.debug("Destroying " + self.name)
        if self._anim is not None:
            self._anim.stop()
            self._anim = None
        scene = self.scene()
        if scene is not None:
            scene.removeItem(self)


class InitiativeDisplayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Initiative Display")
        self.setFixedSize(1800, 300)

        self.scene = QGraphicsScene(0, 0, 1800, 300, self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setObjectName("initiativeView")
        self.view.setGeometry(0, 0, 1800, 300)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setFrameShape(QFrame.NoFrame)
        self.view.setInteractive(False)
        self.view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)

        self.cameo_pixmap = QPixmap(CAMEO_ASSET_PATH).scaled(
            CAMEO_SIZE[0], CAMEO_SIZE[1], Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )

        self.show()

    def addGroup(self, name, avatar_image, location=(0, 0)):
        item = InitiativeGroupItem(
            name=name,
            avatar_image=avatar_image,
            cameo_pixmap=self.cameo_pixmap,
            avatar_size=AVATAR_SIZE,
            cameo_size=CAMEO_SIZE,
            upper_buffer=UPPER_BUFFER,
            left_buffer=LEFT_BUFFER,
            location=location,
        )
        self.scene.addItem(item)
        return item
