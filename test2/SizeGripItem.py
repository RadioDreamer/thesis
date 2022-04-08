from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem

Top         = 1 << 0
Bottom      = 1 << 1
Left        = 1 << 2
Right       = 1 << 3
TopLeft     = Top | Left
BottomLeft  = Bottom | Left
TopRight    = Top | Right
BottomRight = Bottom | Right

class HandleItem(QGraphicsRectItem):
    def __init__(self, positionFlags, parent):
        super(HandleItem, self).__init__(-4, -4, 8, 8, parent)
        self.positionFlags = positionFlags
        self.parent = parent
        self.setBrush(QBrush(Qt.lightGray))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            return self.restrictPosition(value)
        elif change == QGraphicsItem.ItemPositionHasChanged:
            if self.positionFlags == TopLeft:
                self.parent.setTopLeft(value)
            elif self.positionFlags == Top:
                self.parent.setTop(value.y())
            elif self.positionFlags == TopRight:
                self.parent.setTopRight(value)
            elif self.positionFlags == Right:
                self.parent.setRight(value.x())
            elif self.positionFlags == BottomRight:
                self.parent.setBottomRight(value)
            elif self.positionFlags == Bottom:
                self.parent.setBottom(value.y())
            elif self.positionFlags == BottomLeft:
                self.parent.setBottomLeft(value)
            elif self.positionFlags == Left:
                self.parent.setLeft(value.x())
        return value

    def restrictPosition(self, newPos):
        retVal = newPos

        if self.positionFlags & Top or self.positionFlags & Bottom:
            retVal.setY(newPos.y())

        if self.positionFlags & Left or self.positionFlags & Right:
            retVal.setX(newPos.x())

        if self.positionFlags & Top and retVal.y() > self.parent.rect.bottom():
            retVal.setY(self.parent.rect.bottom())
        elif self.positionFlags & Bottom and retVal.y() < self.parent.rect.top():
            retVal.setY(self.parent.rect.top())

        if self.positionFlags & Left and retVal.x() > self.parent.rect.right():
            retVal.setX(self.parent.rect.right())
        elif self.positionFlags & Right and retVal.x() < self.parent.rect.left():
            retVal.setX(self.parent.rect.left())

        return retVal

class SizeGripItem(QGraphicsItem):
    def __init__(self, resizer, parent):
        super(SizeGripItem, self).__init__(parent)
        self.resizer = resizer
        self.parent = parent
        self.rect = self.parent.boundingRect()

        self.handleItems = [HandleItem(d, self) for d in [Top, Bottom, Left, TopLeft, BottomLeft, Right, TopRight, BottomRight]]
        self.updateHandleItemPositions()

    def paint(self, painter, option, widget):
        pass

    def setTopLeft(self, pos):
        self.rect.setTopLeft(pos)
        self.doResize()

    def setTop(self, y):
        self.rect.setTop(y)
        self.doResize()

    def setTopRight(self, pos):
        self.rect.setTopRight(pos)
        self.doResize()

    def setRight(self, x):
        self.rect.setRight(x)
        self.doResize()

    def setBottomRight(self, pos):
        self.rect.setBottomRight(pos)
        self.doResize()

    def setBottom(self, y):
        self.rect.setBottom(y)
        self.doResize()

    def setBottomLeft(self, pos):
        self.rect.setBottomLeft(pos)
        self.doResize()

    def setLeft(self, x):
        self.rect.setLeft(x)
        self.doResize()

    def doResize(self):
        if self.resizer:
            self.resizer.resize(self.rect)
            self.updateHandleItemPositions()

    def updateHandleItemPositions(self):
        for item in self.handleItems:
            item.setFlag(QGraphicsItem.ItemSendsGeometryChanges, False)

            flags = item.positionFlags
            if flags == TopLeft:
                item.setPos(self.rect.topLeft())
            elif flags == Top:
                item.setPos(self.rect.left() + self.rect.width() / 2 - 1,
                            self.rect.top())
            elif flags == TopRight:
                item.setPos(self.rect.topRight())
            elif flags == Right:
                item.setPos(self.rect.right(),
                            self.rect.top() + self.rect.height() / 2 - 1)
            elif flags == BottomRight:
                item.setPos(self.rect.bottomRight())
            elif flags == Bottom:
                item.setPos(self.rect.left() + self.rect.width() / 2 - 1,
                            self.rect.bottom())
            elif flags == BottomLeft:
                item.setPos(self.rect.bottomLeft())
            elif flags == Left:
                item.setPos(self.rect.left(),
                            self.rect.top() + self.rect.height() / 2 - 1)
            item.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
