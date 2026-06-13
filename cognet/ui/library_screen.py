import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal

class LibraryScreen(QWidget):
    back_clicked = Signal()
    edit_requested = Signal(str) # Emits Entry ID to load in the editor

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Header Navigation Block
        header_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Editor Menu")
        self.btn_back.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(self.btn_back)

        header_layout.addStretch()

        title_label = QLabel("Knowledge Library")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #b388ff;")
        header_layout.addWidget(title_label)
        layout.addLayout(header_layout)

        # Filtering / Sorting Controls Grid
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)

        # Sort Dropdown
        sort_label = QLabel("Sort By:")
        sort_label.setStyleSheet("color: #8f8f9d;")
        self.combo_sort = QComboBox()
        self.combo_sort.addItems(["Default", "By Entry Time (Newest First)", "By Entry Time (Oldest First)", "A-Z Title"])
        self.combo_sort.currentIndexChanged.connect(self.refresh_list)
        filter_layout.addWidget(sort_label)
        filter_layout.addWidget(self.combo_sort, stretch=1)

        # Category Filter Dropdown
        cat_label = QLabel("Category:")
        cat_label.setStyleSheet("color: #8f8f9d;")
        self.combo_category = QComboBox()
        self.combo_category.currentIndexChanged.connect(self.refresh_list)
        filter_layout.addWidget(cat_label)
        filter_layout.addWidget(self.combo_category, stretch=1)

        layout.addLayout(filter_layout)

        # Scroll Area for listing Card Buttons
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

    def populate_categories_dropdown(self, data):
        """
        Dynamically extracts and updates all unique categories present in the database.
        """
        self.combo_category.blockSignals(True)
        current_selection = self.combo_category.currentText()
        
        self.combo_category.clear()
        self.combo_category.addItem("All Categories")
        
        categories = sorted(list(set(entry.get("category", "General").strip() for entry in data if entry.get("category"))))
        for cat in categories:
            self.combo_category.addItem(cat)
            
        # Keep index selected if it still exists
        idx = self.combo_category.findText(current_selection)
        if idx >= 0:
            self.combo_category.setCurrentIndex(idx)
        else:
            self.combo_category.setCurrentIndex(0)
            
        self.combo_category.blockSignals(False)

    def refresh_list(self):
        # Clear existing card widgets
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        data = self.db_manager.load_data()
        self.populate_categories_dropdown(data)

        # Filter by Category choice
        selected_cat = self.combo_category.currentText()
        if selected_cat != "All Categories":
            data = [e for e in data if e.get("category", "General") == selected_cat]

        # Apply Sort rules
        sort_mode = self.combo_sort.currentText()
        if sort_mode == "By Entry Time (Newest First)":
            data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        elif sort_mode == "By Entry Time (Oldest First)":
            data.sort(key=lambda x: x.get("timestamp", ""))
        elif sort_mode == "A-Z Title":
            data.sort(key=lambda x: x.get("title", "").lower())

        # Build clean card layout for each entry
        for entry in data:
            card = self.create_entry_card(entry)
            self.scroll_layout.addWidget(card)

    def create_entry_card(self, entry) -> QFrame:
        card_frame = QFrame()
        card_frame.setObjectName("LibraryCard")
        card_frame.setStyleSheet("""
            QFrame#LibraryCard {
                background-color: #16161a;
                border: 1px solid #2a2a32;
                border-radius: 10px;
            }
            QFrame#LibraryCard:hover {
                border-color: #b388ff;
            }
            QLabel {
                background: transparent;
            }
        """)
        
        card_layout = QHBoxLayout(card_frame)
        card_layout.setContentsMargins(15, 12, 15, 12)
        
        # Left Side Info Panel
        info_widget = QWidget()
        info_widget.setStyleSheet("background: transparent;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        title_row = QHBoxLayout()
        title_lbl = QLabel(entry.get("title", "Untitled Concept"))
        title_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #00e5ff;")
        title_row.addWidget(title_lbl)
        
        cat_badge = QLabel(f"[{entry.get('category', 'General')}]")
        cat_badge.setStyleSheet("color: #b388ff; font-size: 11px; font-weight: bold;")
        title_row.addWidget(cat_badge)
        title_row.addStretch()
        info_layout.addLayout(title_row)
        
        # Display Snippet text (Cleanly truncate longer entries)
        snippet = entry.get("content", "")
        if len(snippet) > 130:
            snippet = snippet[:127] + "..."
        snippet_lbl = QLabel(snippet if snippet else "No written content.")
        snippet_lbl.setStyleSheet("color: #8f8f9d; font-size: 12px;")
        snippet_lbl.setWordWrap(True)
        info_layout.addWidget(snippet_lbl)
        
        card_layout.addWidget(info_widget, stretch=4)
        
        # Right Side Actions Layout (Buttons)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        btn_edit = QPushButton("Edit")
        btn_edit.setStyleSheet("QPushButton { font-size: 12px; padding: 6px 12px; border-color: #2a2a32; }")
        btn_edit.clicked.connect(lambda _, eid=entry.get("id"): self.edit_requested.emit(eid))
        action_layout.addWidget(btn_edit)
        
        btn_del = QPushButton("Delete")
        btn_del.setStyleSheet("""
            QPushButton { 
                background-color: #2a1115; 
                color: #ff4050; 
                border-color: #4c1a20; 
                font-size: 12px; 
                padding: 6px 12px; 
            }
            QPushButton:hover {
                background-color: #ff4050;
                color: #16161a;
            }
        """)
        btn_del.clicked.connect(lambda _, eid=entry.get("id"): self.delete_entry(eid))
        action_layout.addWidget(btn_del)
        
        card_layout.addLayout(action_layout, stretch=1)
        return card_frame

    def delete_entry(self, entry_id):
        # Delete Entire Entry Confirmation Dialog
        data = self.db_manager.load_data()
        target_title = "Selected Entry"
        for entry in data:
            if entry.get("id") == entry_id:
                target_title = entry.get("title", "Untitled Concept")
                break
                
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 
            "Delete Entry",
            f"Are you sure you want to permanently delete \"{target_title}\" from Library?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            filtered_data = [item for item in data if item["id"] != entry_id]
            self.db_manager.save_data(filtered_data)
            self.refresh_list()