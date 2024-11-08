import sys
import torch
from scene.gaussian_model import GaussianModel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
from scene import Scene
from gaussian_renderer import render, GaussianModel
from utils.general_utils import safe_state
from argparse import ArgumentParser
from arguments import ModelParams, PipelineParams, get_combined_args

class RealTimeGaussianViewer(QWidget):
    def __init__(self, model_params, pipeline_params, iteration):
        super().__init__()
        
        # Model and rendering setup
        self.gaussians = GaussianModel(model_params.sh_degree)
        self.scene = Scene(model_params, self.gaussians, load_iteration=iteration, shuffle=False)
        
        bg_color = [1, 1, 1] if model_params.white_background else [0, 0, 0]
        self.background = torch.tensor(bg_color, dtype=torch.float32, device="cuda")
        self.pipeline = pipeline_params
        self.views = self.scene.getTrainCameras()
        self.current_index = 0

        # PyQt Setup
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        
        # Control Buttons
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

        # Timer for auto-play
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_view)

        # Button Signals
        self.prev_button.clicked.connect(self.prev_view)
        self.next_button.clicked.connect(self.next_view)
        self.auto_button.clicked.connect(self.toggle_auto_play)

        # Initial Window Size
        self.resize(800, 600)
    
    def render_image(self, view):
        """Render the current view and convert it to QImage for display in PyQt."""
        with torch.no_grad():
            rendering = render(view, self.gaussians, self.pipeline, self.background)["render"]

            # Convert rendering from torch tensor to numpy
            rendering = rendering.permute(1, 2, 0).cpu().numpy()
            rendering = (rendering * 255).astype('uint8')  # Scale to 0-255 and convert to uint8

            h, w, _ = rendering.shape
            # Convert numpy array to bytes and create QImage with the correct format
            q_image = QImage(rendering.tobytes(), w, h, 3 * w, QImage.Format_RGB888)
            
            # Return the QPixmap scaled to fit the label
            return QPixmap.fromImage(q_image).scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def load_image(self):
        view = self.views[self.current_index]
        pixmap = self.render_image(view)
        self.label.setPixmap(pixmap)
        self.setWindowTitle(f"Real-Time Gaussian Splatting Viewer - View {self.current_index + 1}")

    def prev_view(self):
        self.current_index = (self.current_index - 1) % len(self.views)
        self.load_image()

    def next_view(self):
        self.current_index = (self.current_index + 1) % len(self.views)
        self.load_image()

    def toggle_auto_play(self):
        if self.timer.isActive():
            self.timer.stop()
            self.auto_button.setText("Start Auto Play")
        else:
            self.timer.start(150)  # Interval for smoother playback
            self.auto_button.setText("Stop Auto Play")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set up command line argument parser
    parser = ArgumentParser(description="Real-Time Gaussian Splatting Viewer")
    model_params = ModelParams(parser, sentinel=True)
    pipeline_params = PipelineParams(parser)
    parser.add_argument("--iteration", default=-1, type=int)
    parser.add_argument("--quiet", action="store_true")
    args = get_combined_args(parser)

    # Initialize system state (RNG)
    safe_state(args.quiet)

    # Initialize the viewer
    viewer = RealTimeGaussianViewer(model_params.extract(args), pipeline_params.extract(args), args.iteration)
    viewer.show()
    sys.exit(app.exec_())
