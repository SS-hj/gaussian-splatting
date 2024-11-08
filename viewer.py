import sys
import os
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

class ImageViewer(QWidget):
    def __init__(self, root_directory, dataset_name):
        super().__init__()

        # Construct the image folder path from root_directory and dataset_name
        self.image_folder = os.path.join(root_directory, dataset_name)
        
        if not os.path.isdir(self.image_folder):
            raise ValueError(f"The directory '{self.image_folder}' does not exist.")
        
        # List of image files in the specified folder
        self.image_files = sorted([f for f in os.listdir(self.image_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))])
        if not self.image_files:
            raise ValueError(f"No image files found in the directory '{self.image_folder}'.")

        self.current_index = 0

        # UI Elements
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.prev_button = QPushButton("Previous", self)
        self.next_button = QPushButton("Next", self)
        self.auto_button = QPushButton("Start Auto Play", self)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.prev_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.auto_button)
        self.setLayout(layout)

        # Timer for auto play with smoother playback (150ms interval)
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_image)

        # Signals
        self.prev_button.clicked.connect(self.prev_image)
        self.next_button.clicked.connect(self.next_image)
        self.auto_button.clicked.connect(self.toggle_auto_play)

        self.resize(800, 600)  # Initial window size that can be resized

        # Placeholder for pre-loaded images (only used for auto play)
        self.preloaded_images = []

    def showEvent(self, event):
        super().showEvent(event)
        # After the window is shown, load the initial image
        self.load_image()

    def load_and_resize_image(self, image_file):
        # Load and resize images to the window size to reduce real-time scaling time
        pixmap = QPixmap(os.path.join(self.image_folder, image_file))
        return pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def load_image(self):
        if self.timer.isActive():
            # During auto play, use pre-loaded images
            pixmap = self.preloaded_images[self.current_index]
        else:
            # For prev/next buttons, load image based on the current label size
            pixmap = self.load_and_resize_image(self.image_files[self.current_index])

        self.label.setPixmap(pixmap)
        self.setWindowTitle(f"Image Viewer - {self.image_files[self.current_index]}")

    def prev_image(self):
        self.current_index = (self.current_index - 1) % len(self.image_files)
        self.load_image()

    def next_image(self):
        self.current_index = (self.current_index + 1) % len(self.image_files)
        self.load_image()

    def toggle_auto_play(self):
        if self.timer.isActive():
            self.timer.stop()
            self.auto_button.setText("Start Auto Play")
        else:
            # Show loading message while images are being pre-loaded
            self.label.setText("Loading images... Please wait.")
            QApplication.processEvents()  # Force GUI update to show loading text
            
            # Pre-load all images based on current window size before starting auto play
            self.preloaded_images = []
            for img in self.image_files:
                pixmap = self.load_and_resize_image(img)
                self.preloaded_images.append(pixmap)
                
            # Once preloading is done, update the UI and start the auto play
            self.label.clear()  # Clear the loading text
            self.timer.start(150)  # 150ms interval for smoother, slower transition
            self.auto_button.setText("Stop Auto Play")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set the root directory directly in the code
    root_directory = "./rendered_images"  # Update this to your root path

    # Ensure that the dataset name is passed as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python image_viewer.py <dataset_name>")
        sys.exit(1)

    dataset_name = sys.argv[1]  # Dataset name passed as a command-line argument

    viewer = ImageViewer(root_directory, dataset_name)
    viewer.show()
    sys.exit(app.exec_())
