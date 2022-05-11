from PySide6.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsTextItem,
    QGraphicsItem
)
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPen, QBrush, QColor, QFont
from RuleAndObjectEditDialog import RuleAndObjectEditDialog


class RegionView(QGraphicsRectItem):
    """
    A class that visually represents the region with it's object and rules
    """

    def __init__(self, id, rect, obj, rules, simulator=None, parent=None):
        """
        Initializing method for the visual region

        Parameters
        ----------
        id : int
            the unique identifier of the visual region
        rect : QRectF
            the rectangle that bounds the visual region
        obj : str
            the string representing the objects in the region
        rules : str
            the string representing the rules in the region
        simulator : MembraneSimulator, optional
            the simulator object which handles simulation (default is None)
        parent : QWidget
            the parent widget of the visual region
        """

        super().__init__(rect, parent)
        self.id = id
        self.simulator = simulator
        self.obj_text = QGraphicsTextItem(obj, self)
        self.rule_text = QGraphicsTextItem(rules, self)

        font = QFont("Source Code Pro Semibold")
        font.setPointSize(10)
        self.obj_text.setFont(font)
        self.rule_text.setFont(font)

        self.center_text()
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setPen(QPen(QBrush(QColor('grey')), 3))

    def paint(self, painter, option, widget):
        """
        Overridden method of base class's `paint()`

        This is done to make sure the border of the region is rounded

        Parameters
        ----------
        painter : QPainter
            the painter object responsible for drawing the region
        option :
        widget : QWidget

        Returns
        -------

        """
        painter.drawRoundedRect(self.rect(), 25, 25, Qt.RelativeSize)

    def adjust_text(self):
        """
        A function that adjusts the font size of the displayed objects
        """

        self.obj_text.adjustSize()


    #    def mousePressEvent(self, event):
    #        self.click_pos = event.pos()
    #        rect = self.rect()
    #        if abs(rect.left() - self.click_pos.x()) < 5:
    #            self.selected_edge = 'left'
    #        elif abs(rect.right() - self.click_pos.x()) < 5:
    #            self.selected_edge = 'right'
    #        elif abs(rect.top() - self.click_pos.y()) < 5:
    #            self.selected_edge = 'top'
    #        elif abs(rect.bottom() - self.click_pos.y()) < 5:
    #            self.selected_edge = 'bottom'
    #        else:
    #            self.selected_edge = None
    #        self.click_pos = event.pos()
    #        self.click_rect = rect
    #        super().mousePressEvent(event)

    #    def mouseMoveEvent(self, event):
    #        pos = event.pos()
    #        x_diff = pos.x() - self.click_pos.x()
    #        y_diff = pos.y() - self.click_pos.y()

    #        # Start with the rectangle as it was when clicked.
    #        rect = QRectF(self.click_rect)

    #        # Then adjust by the distance the mouse moved.
    #        if self.selected_edge is None:
    #            rect.translate(x_diff, y_diff)
    #        elif self.selected_edge == 'top':
    #            rect.adjust(0, y_diff, 0, 0)
    #        elif self.selected_edge == 'left':
    #            rect.adjust(x_diff, 0, 0, 0)
    #        elif self.selected_edge == 'bottom':
    #            rect.adjust(0, 0, 0, y_diff)
    #        elif self.selected_edge == 'right':
    #            rect.adjust(0, 0, x_diff, 0)

    #        # Figure out the limits of movement. I did it by updating the scene's
    #        # rect after the window resizes.
    #        scene_rect = self.scene().sceneRect()
    #        view_left = scene_rect.left()
    #        view_top = scene_rect.top()
    #        view_right = scene_rect.right()
    #        view_bottom = scene_rect.bottom()

    #        # Next, check if the rectangle has been dragged out of bounds.
    #        if rect.top() < view_top:
    #            if self.selected_edge is None:
    #                rect.translate(0, view_top - rect.top())
    #            else:
    #                rect.setTop(view_top)
    #        if rect.left() < view_left:
    #            if self.selected_edge is None:
    #                rect.translate(view_left - rect.left(), 0)
    #            else:
    #                rect.setLeft(view_left)
    #        if view_bottom < rect.bottom():
    #            if self.selected_edge is None:
    #                rect.translate(0, view_bottom - rect.bottom())
    #            else:
    #                rect.setBottom(view_bottom)
    #        if view_right < rect.right():
    #            if self.selected_edge is None:
    #                rect.translate(view_right - rect.right(), 0)
    #            else:
    #                rect.setRight(view_right)

    #        # Also check if the rectangle has been dragged inside out.
    #        if rect.width() < 5:
    #            if self.selected_edge == 'left':
    #                rect.setLeft(rect.right() - 5)
    #            else:
    #                rect.setRight(rect.left() + 5)
    #        if rect.height() < 5:
    #            if self.selected_edge == 'top':
    #                rect.setTop(rect.bottom() - 5)
    #            else:
    #                rect.setBottom(rect.top() + 5)

    #        # Finally, update the rect that is now guaranteed to stay in bounds.
    #        self.setRect(rect)
    #        self.center_text()
    #        super().mouseMoveEvent(event)

    ##################################

    def center_text(self):
        """
        A function that centers the displayed objects and rules and also
        positions the rules directly under the objects
        """

        text_rect = QRectF(self.obj_text.boundingRect())
        rule_rect = QRectF(self.rule_text.boundingRect())
        self.obj_text.setPos((self.rect().width() - text_rect.width()) / 2, 0)
        self.rule_text.setPos((self.rect().width() - rule_rect.width()) / 2,
                              text_rect.height())

    def mouseDoubleClickEvent(self, event):
        """
        The event handler for the action of a doubleclick on the region's area

        Parameters
        ----------
        event : QMouseDoubleClickEvent
            the object containing information about the event
        """

        objects = self.simulator.model.regions[self.id].objects
        rule_string = self.simulator.model.get_rule_string(self.id)

        valid_fn = self.simulator.model.__class__.is_valid_rule
        dialog = RuleAndObjectEditDialog(str(objects), rule_string,
                                         self.simulator.type,
                                         valid_fn=valid_fn
                                         )
        dialog.exec()

        rule_result = dialog.get_rules()
        if not rule_result == rule_string:
            self.simulator.update_region_rules(self.id, rule_result)

        obj_result = RegionView.sort_word(dialog.object_edit.text())
        if obj_result != RegionView.sort_word(self.obj_text.toPlainText()):
            self.simulator.update_region_objects(self.id, obj_result)
        self.center_text()

    @classmethod
    def sort_word(cls, string):
        """
        A class method for ordering the characters in a string

        This method is used to check that the original objects are same as
        the new input, since if only the order of characters changed,
        the content is the same nevertheless Parameters ---------- string

        Returns
        -------
        str
            the lexicographically ordered string containing the region's objects
        """

        return ''.join(sorted(string, key=str.lower))
