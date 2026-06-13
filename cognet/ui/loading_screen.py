from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, Signal

class LoadingScreen(QWidget):
    create_entry_clicked = Signal()
    view_embeddings_clicked = Signal()
    quit_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)

        layout.addSpacerItem(QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Core Branding Block
        title_label = QLabel("CogNet")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        sub_label = QLabel("Cognitive Vector Mapping & Semantic Syntax Engine")
        sub_label.setObjectName("subtitleLabel")
        sub_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub_label)

        layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Central Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(15)

        self.btn_new = QPushButton("Create New Entry")
        self.btn_new.setObjectName("accentButton")
        self.btn_new.clicked.connect(self.create_entry_clicked.emit)
        btn_layout.addWidget(self.btn_new)

        self.btn_view = QPushButton("Explore 3D Vector Space")
        self.btn_view.clicked.connect(self.view_embeddings_clicked.emit)
        btn_layout.addWidget(self.btn_view)

        self.btn_quit = QPushButton("Quit Application")
        self.btn_quit.clicked.connect(self.quit_clicked.emit)
        btn_layout.addWidget(self.btn_quit)

        # Centering container
        btn_container = QWidget()
        btn_container.setLayout(btn_layout)
        btn_container.setMaximumWidth(380)
        
        centering_layout = QHBoxLayout()
        centering_layout.addStretch()
        centering_layout.addWidget(btn_container)
        centering_layout.addStretch()
        
        layout.addLayout(centering_layout)
        layout.addSpacerItem(QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))