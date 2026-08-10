from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QImage, QPixmap


def qimage_from_file(path):
    return QImage(path)


def qimage_from_bytes(data):
    return QImage.fromData(data)


def qimage_from_clipboard():
    image = QGuiApplication.clipboard().image()
    if image.isNull():
        return None
    return image


def to_pixmap(image):
    if isinstance(image, QPixmap):
        return image
    return QPixmap.fromImage(image)


def scaled_pixmap(image, width, height):
    return to_pixmap(image).scaled(width, height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)


def save_png(image, path):
    if isinstance(image, QPixmap):
        image = image.toImage()
    image.convertToFormat(QImage.Format_RGBA8888).save(path, "PNG")
