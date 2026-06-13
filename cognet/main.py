import os
# Suppress Hugging Face download notifications and symbolic link warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QSplashScreen, QFrame, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from ui.styles import STYLE_SHEET
from ui.loading_screen import LoadingScreen
from ui.entry_screen import EntryScreen
from ui.embedding_viewer import EmbeddingViewer
from ui.library_screen import LibraryScreen
from data.database_manager import DatabaseManager
from models.note_model import get_transformer_model


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
                background-color: #0d0e12;
                border: 2px solid #00e5ff;
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
        title_lbl.setStyleSheet("font-size: 32px; font-weight: bold; color: #00e5ff;")
        title_lbl.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title_lbl)
        
        desc_lbl = QLabel("Initializing Semantic Engines...")
        desc_lbl.setStyleSheet("font-size: 13px; color: #b388ff; margin-top: 5px;")
        desc_lbl.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(desc_lbl)
        
        desc_sub = QLabel("Scanning offline cache parameters")
        desc_sub.setStyleSheet("font-size: 11px; color: #8f8f9d;")
        desc_sub.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(desc_sub)
        
        layout.addWidget(self.frame)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CogNet")
        self.resize(950, 720)

        self.db_manager = DatabaseManager()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.loading_screen = LoadingScreen()
        self.entry_screen = EntryScreen(self.db_manager)
        self.embedding_viewer = EmbeddingViewer(self.db_manager)
        self.library_screen = LibraryScreen(self.db_manager)

        self.stacked_widget.addWidget(self.loading_screen)
        self.stacked_widget.addWidget(self.entry_screen)
        self.stacked_widget.addWidget(self.embedding_viewer)
        self.stacked_widget.addWidget(self.library_screen)

        # Core Navigation Rules
        self.loading_screen.create_entry_clicked.connect(self.go_to_entry_screen)
        self.loading_screen.view_embeddings_clicked.connect(self.go_to_embedding_viewer)
        self.loading_screen.quit_clicked.connect(self.close)

        self.entry_screen.back_clicked.connect(self.go_to_menu)
        self.entry_screen.library_clicked.connect(self.go_to_library)
        
        self.embedding_viewer.back_clicked.connect(self.go_to_menu)
        
        self.library_screen.back_clicked.connect(self.go_to_entry_screen_existing)
        self.library_screen.edit_requested.connect(self.load_entry_into_editor)

        self.stacked_widget.setCurrentWidget(self.loading_screen)

    def go_to_entry_screen(self):
        self.entry_screen.start_new_entry()
        self.stacked_widget.setCurrentWidget(self.entry_screen)

    def go_to_entry_screen_existing(self):
        self.stacked_widget.setCurrentWidget(self.entry_screen)

    def go_to_embedding_viewer(self):
        self.embedding_viewer.load_and_render()
        self.stacked_widget.setCurrentWidget(self.embedding_viewer)

    def go_to_library(self):
        self.library_screen.refresh_list()
        self.stacked_widget.setCurrentWidget(self.library_screen)

    def load_entry_into_editor(self, entry_id):
        self.entry_screen.load_existing_entry(entry_id)
        self.stacked_widget.setCurrentWidget(self.entry_screen)

    def go_to_menu(self):
        self.stacked_widget.setCurrentWidget(self.loading_screen)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    
    # 1. Initialize and show the clean loader splash frame
    splash = CogNetSplash()
    splash.show()
    app.processEvents()
    
    # 2. Sequential background preload (Downloads model once, then starts instantly afterward)
    get_transformer_model()
    
    # 3. Terminate splash and open core window
    splash.close()
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()