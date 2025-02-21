from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QPen, QTransform
import sys

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer with Zoom and Drag")
        
        # Central widget setup
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Image viewing area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.image_label = QLabel()
        self.scroll_area.setWidget(self.image_label)
        
        # Mode and state tracking
        self.is_draw_mode = False
        self.is_dragging = False
        self.last_mouse_pos = None
        self.boxes = []
        self.drawing = False
        self.start_pos = None
        
        # Zoom tracking
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Button layout
        self.button_layout = QVBoxLayout()
        self.load_button = QPushButton("Load Image")
        self.load_excel_button = QPushButton("Load Excel")
        self.mode_button = QPushButton("Toggle Draw Mode")
        self.remove_box_button = QPushButton("Remove Box")
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")
        self.reset_zoom_button = QPushButton("Reset Zoom")
        self.submit_button = QPushButton("Submit")
        
        # Connect buttons
        self.load_button.clicked.connect(self.load_image)
        self.load_excel_button.clicked.connect(self.load_excel)
        self.mode_button.clicked.connect(self.toggle_mode)
        self.remove_box_button.clicked.connect(self.remove_last_box)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.reset_zoom_button.clicked.connect(self.reset_zoom)
        self.submit_button.clicked.connect(self.to_transfer)
        
        # Add buttons to layout
        self.button_layout.addWidget(self.load_button)
        self.button_layout.addWidget(self.load_excel_button)
        self.button_layout.addWidget(self.mode_button)
        self.button_layout.addWidget(self.remove_box_button)
        self.button_layout.addWidget(self.zoom_in_button)
        self.button_layout.addWidget(self.zoom_out_button)
        self.button_layout.addWidget(self.reset_zoom_button)
        self.button_layout.addWidget(self.submit_button)
        self.button_layout.addStretch()
        
        # Main layout setup
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addLayout(self.button_layout)
        
        # Setup event handling
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.mouse_press
        self.image_label.mouseReleaseEvent = self.mouse_release
        self.image_label.mouseMoveEvent = self.mouse_move
        self.scroll_area.wheelEvent = self.wheel_event
        
        self.original_image = None
        self.scaled_image = None
        self.excel = None 
        self.update_mode_button() 

    def to_transfer(self):
        if not self.boxes:
            QtWidgets.QMessageBox.critical(self, "Error", "No Boxes are Drawn")
        elif not self.excel:
            QtWidgets.QMessageBox.critical(self, "Error", "Excel file is not selected")
        else:
            self.coordinates = []
            for start, end in self.boxes:
                width = abs(start.x() - end.x())
                height = abs(start.y() - end.y())
                self.coordinates.append({
                    "x1" : start.x(),
                    "y1" : start.y(),
                    "x2" : end.x(),
                    "y2" : end.y(),
                    "width" : width,
                    "height" : height 
                })    
            self.close()

    def load_excel(self):
        self.excel, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Excel", "", "Excel Files (*.xlsx)" 
        )
        if not self.excel:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to load Excel")


    def load_image(self):
        self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if self.filename:
            self.original_image = QPixmap(self.filename)
            if not self.original_image.isNull():
                self.boxes.clear()
                self.update_image()
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "Failed to load image")
                self.original_image = None

    def update_image(self):
        if self.original_image:
            # Scale the image
            scaled_size = self.original_image.size() * self.zoom_factor
            self.scaled_image = self.original_image.scaled(
                scaled_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.redraw_boxes()

    def get_scaled_point(self, point):
        """Convert point from scaled coordinates to original coordinates"""
        if not self.original_image or not self.scaled_image:
            return point
        
        scale_x = self.original_image.width() / self.scaled_image.width()
        scale_y = self.original_image.height() / self.scaled_image.height()
        
        return QPoint(int(point.x() * scale_x), int(point.y() * scale_y))

    def get_display_point(self, point):
        """Convert point from original coordinates to scaled coordinates"""
        if not self.original_image or not self.scaled_image:
            return point
        
        scale_x = self.scaled_image.width() / self.original_image.width()
        scale_y = self.scaled_image.height() / self.original_image.height()
        
        return QPoint(int(point.x() * scale_x), int(point.y() * scale_y))

    def toggle_mode(self):
        self.is_draw_mode = not self.is_draw_mode
        self.update_mode_button()

    def update_mode_button(self):
        self.mode_button.setText("Draw Mode" if self.is_draw_mode else "Drag Mode")
        self.mode_button.setStyleSheet(
            "background-color: #ffcccc;" if self.is_draw_mode else "background-color: #cccccc;"
        )

    def mouse_press(self, event):
        if not self.original_image:
            return
            
        if self.is_draw_mode:
            self.drawing = True
            self.start_pos = event.pos()
        else:
            self.is_dragging = True
            self.last_mouse_pos = event.pos()
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.image_label.setCursor(Qt.ClosedHandCursor)

    def mouse_move(self, event):
        if not self.original_image:
            return
            
        if self.is_draw_mode and self.drawing:
            # Draw preview of box
            pixmap = self.scaled_image.copy()
            painter = QPainter(pixmap)
            painter.setPen(QPen(Qt.red, 2))
            painter.drawRect(QRect(self.start_pos, event.pos()))
            painter.end()
            self.image_label.setPixmap(pixmap)
            
        elif not self.is_draw_mode and self.is_dragging:
            # Calculate drag distance
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            
            # Update scroll bars
            h_bar = self.scroll_area.horizontalScrollBar()
            v_bar = self.scroll_area.verticalScrollBar()
            
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())

    def mouse_release(self, event):
        if not self.original_image:
            return
            
        if self.is_draw_mode and self.drawing:
            self.drawing = False
            # Convert coordinates to original image space before storing
            start = self.get_scaled_point(self.start_pos)
            end = self.get_scaled_point(event.pos())
            self.boxes.append((start, end))
            self.redraw_boxes()
            
        elif not self.is_draw_mode:
            self.is_dragging = False
            self.image_label.setCursor(Qt.ArrowCursor)

    def remove_last_box(self):
        if self.boxes:
            self.boxes.pop()
            self.redraw_boxes()
        else:
            QtWidgets.QMessageBox.information(self, "Info", "No boxes to remove")

    def redraw_boxes(self):
        if self.original_image and self.scaled_image:
            pixmap = self.scaled_image.copy()
            painter = QPainter(pixmap)
            painter.setPen(QPen(Qt.red, 2))
            
            for start, end in self.boxes:
                # Convert coordinates from original to display space
                start_scaled = self.get_display_point(start)
                end_scaled = self.get_display_point(end)
                painter.drawRect(QRect(start_scaled, end_scaled))
            
            painter.end()
            self.image_label.setPixmap(pixmap)

    def zoom_in(self):
        self.zoom_factor = min(self.zoom_factor * 1.2, self.max_zoom)
        self.update_image()

    def zoom_out(self):
        self.zoom_factor = max(self.zoom_factor / 1.2, self.min_zoom)
        self.update_image()

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.update_image()

    def wheel_event(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

def main():
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.showMaximized()
    app.exec_()
    print("!")
    return getattr(viewer, "coordinates", None), getattr(viewer, "filename", None), getattr(viewer, "excel", None)