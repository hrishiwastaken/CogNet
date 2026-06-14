import os
import sys

# Suppress Hugging Face download notifications and symbolic link warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QFrame, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QThread, Signal, QEventLoop, QTimer
from ui.styles import STYLE_SHEET


class PreloadWorker(QThread):
    progress = Signal(str, str)
    
    def run(self):
        self.progress.emit("Initializing Semantic Engines...", "Caching database structures...")
        try:
            # Pre-load database structure
            from data.database_manager import DatabaseManager
            db = DatabaseManager()
            db.load_data()
        except Exception as e:
            print(f"[CogNet] Warning during DB preload: {e}")
            
        self.progress.emit("Loading Interface Libraries...", "Warming up Matplotlib 3D context...")
        try:
            import matplotlib
            matplotlib.use("QtAgg")
            import matplotlib.pyplot as plt
            # Cache the embedding viewer module
            from ui.embedding_viewer import EmbeddingViewer
        except Exception as e:
            print(f"[CogNet] Warning during Matplotlib preload: {e}")
            
        self.progress.emit("Initializing Semantic Engines...", "Warming up Sentence Transformers...")
        try:
            from sentence_transformers import SentenceTransformer
        except Exception as e:
            print(f"[CogNet] Warning during SentenceTransformer import: {e}")
            
        self.progress.emit("Loading Transformer Model...", "Loading all-MiniLM-L6-v2 (might take a moment)...")
        try:
            from models.note_model import get_transformer_model
            get_transformer_model()
        except Exception as e:
            print(f"[CogNet] Warning during model preload: {e}")
            
        self.progress.emit("Starting Interface...", "Launching CogNet...")


# Styled custom dark startup dialog
class CogNetSplash(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(380, 180)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.frame = QFrame(self)
        self.frame.setObjectName("SplashFrame")
        self.frame.setStyleSheet("""
            QFrame#SplashFrame {
                background-color: #07090e;
                border: 2px solid #38bdf8;
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setAlignment(Qt.AlignCenter)
        
        title_lbl = QLabel("CogNet")
        title_lbl.setStyleSheet("font-size: 32px; font-weight: bold; color: #38bdf8;")
        title_lbl.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title_lbl)
        
        self.desc_lbl = QLabel("Initializing Semantic Engines...")
        self.desc_lbl.setStyleSheet("font-size: 13px; color: #facc15; margin-top: 5px;")
        self.desc_lbl.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.desc_lbl)
        
        self.desc_sub = QLabel("Scanning offline cache parameters")
        self.desc_sub.setStyleSheet("font-size: 11px; color: #8f8f9d;")
        self.desc_sub.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.desc_sub)
        
        layout.addWidget(self.frame)

    def update_status(self, title, subtitle):
        self.desc_lbl.setText(title)
        self.desc_sub.setText(subtitle)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CogNet")
        self.resize(950, 720)

        # Lazy load modules (already cached by PreloadWorker, so instant)
        from data.database_manager import DatabaseManager
        from ui.entry_screen import EntryScreen
        from ui.embedding_viewer import EmbeddingViewer
        from ui.library_screen import DashboardScreen

        self.db_manager = DatabaseManager()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.dashboard_screen = DashboardScreen(self.db_manager)
        self.entry_screen = EntryScreen(self.db_manager)
        self.embedding_viewer = EmbeddingViewer(self.db_manager)

        self.stacked_widget.addWidget(self.dashboard_screen)
        self.stacked_widget.addWidget(self.entry_screen)
        self.stacked_widget.addWidget(self.embedding_viewer)

        # Core Navigation Rules
        self.dashboard_screen.create_entry_clicked.connect(self.go_to_entry_screen)
        self.dashboard_screen.view_embeddings_clicked.connect(self.go_to_embedding_viewer)
        self.dashboard_screen.quit_clicked.connect(self.close)
        self.dashboard_screen.edit_requested.connect(self.load_entry_into_editor)

        self.entry_screen.back_clicked.connect(self.go_to_menu)
        self.embedding_viewer.back_clicked.connect(self.go_to_menu)

        # Initialize list and show dashboard
        self.dashboard_screen.refresh_list()
        self.stacked_widget.setCurrentWidget(self.dashboard_screen)

    def go_to_entry_screen(self):
        self.entry_screen.start_new_entry()
        self.stacked_widget.setCurrentWidget(self.entry_screen)

    def go_to_entry_screen_existing(self):
        self.stacked_widget.setCurrentWidget(self.entry_screen)

    def go_to_embedding_viewer(self):
        self.embedding_viewer.load_and_render()
        self.stacked_widget.setCurrentWidget(self.embedding_viewer)

    def load_entry_into_editor(self, entry_id):
        self.entry_screen.load_existing_entry(entry_id)
        self.stacked_widget.setCurrentWidget(self.entry_screen)

    def go_to_menu(self):
        self.dashboard_screen.refresh_list()
        self.stacked_widget.setCurrentWidget(self.dashboard_screen)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    
    # 1. Initialize and show the clean loader splash frame instantly
    splash = CogNetSplash()
    splash.show()
    app.processEvents()
    
    # 2. Asynchronous background preload
    loop = QEventLoop()
    worker = PreloadWorker()
    worker.progress.connect(splash.update_status)
    worker.finished.connect(loop.quit)
    
    # Start the worker thread via a single-shot timer once the loop starts running
    QTimer.singleShot(0, worker.start)
    loop.exec()
    
    # 3. Terminate splash and open core window
    splash.close()
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()