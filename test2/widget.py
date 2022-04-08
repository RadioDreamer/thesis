import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem
from PySide6.QtCore import Qt, QRectF
from SizeGripItem import SizeGripItem


class SimpleResizer():
    def __init__(self, item):
        self.item = item

    def resize(self, rect):
        self.item.setRect(rect)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Membránrendszer szimuláció")

        scene = QGraphicsScene()
        rectItem = QGraphicsRectItem(QRectF(0, 0, 320, 240))
        rectItem.setBrush(Qt.GlobalColor.red)
        # rectItem.setPen(Qt.NoPen)
        rectItem.setFlag(QGraphicsItem.ItemIsMovable)
        scene.addItem(rectItem)
        ellipseItem = QGraphicsEllipseItem(QRectF(0, 0, 200, 200))
        ellipseItem.setBrush(Qt.blue)
        # ellipseItem.setPen(Qt.NoPen)
        ellipseItem.setFlag(QGraphicsItem.ItemIsMovable)
        scene.addItem(ellipseItem)
        rectSizeGripItem = SizeGripItem(SimpleResizer(rectItem), rectItem)
        ellipseSizeGripItem = SizeGripItem(SimpleResizer(ellipseItem), ellipseItem)
        graphicsView = QGraphicsView(self)
        graphicsView.setScene(scene)
        self.setCentralWidget(graphicsView)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
