import uuid
import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QLabel
from PySide6.QtCore import Qt, Signal, QTimer, QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from models.note_model import split_into_sentences, generate_3d_vector

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []

        # Titles (# Header) -> Cyan
        title_format = QTextCharFormat()
        title_format.setForeground(QColor("#00e5ff"))
        title_format.setFontWeight(QFont.Bold)
        title_format.setFontPointSize(16)
        self.rules.append((QRegularExpression(r'^#\s.*'), title_format))

        # Subtitles (## Header) -> Purple
        subtitle_format = QTextCharFormat()
        subtitle_format.setForeground(QColor("#b388ff"))
        subtitle_format.setFontWeight(QFont.Bold)
        subtitle_format.setFontPointSize(14)
        self.rules.append((QRegularExpression(r'^##\s.*'), subtitle_format))

        # Lists (* or -) -> Yellow
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#ffd54f"))
        list_format.setFontWeight(QFont.Bold)
        self.rules.append((QRegularExpression(r'^\s*[\*\-\+]\s'), list_format))

        # Code snippets (`code`) -> Bright Pink
        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#ff4081"))
        code_format.setFontFamilies(["Courier New", "Consolas", "monospace"])
        self.rules.append((QRegularExpression(r'`[^`]+`'), code_format))

        # Annotations ([annotation]) -> Mint Green
        anno_format = QTextCharFormat()
        anno_format.setForeground(QColor("#69f0ae"))
        anno_format.setFontItalic(True)
        self.rules.append((QRegularExpression(r'\[.*?\]'), anno_format))

    def highlightBlock(self, text):
        for pattern, format_ in self.rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format_)


class EntryScreen(QWidget):
    back_clicked = Signal()
    library_clicked = Signal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_id = None
        self.init_ui()

        self.save_timer = QTimer(self)
        self.save_timer.setInterval(1000)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_entry)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Back to Menu")
        self.btn_back.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(self.btn_back)

        # Added Library Screen Button
        self.btn_library = QPushButton("Library 📁")
        self.btn_library.clicked.connect(self.library_clicked.emit)
        header_layout.addWidget(self.btn_library)

        header_layout.addStretch()

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #8f8f9d; font-size: 12px;")
        header_layout.addWidget(self.status_label)
        layout.addLayout(header_layout)

        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(15)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title your entry...")
        self.title_input.textChanged.connect(self.trigger_autosave)
        fields_layout.addWidget(self.title_input, stretch=3)

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Category")
        self.category_input.textChanged.connect(self.trigger_autosave)
        fields_layout.addWidget(self.category_input, stretch=1)

        layout.addLayout(fields_layout)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "Write your ideas here. All standard markdown syntaxes apply:\n\n"
            "  # Primary Header Topic\n"
            "  ## Subtopic Division\n"
            "  * Important Bullet Point\n"
            "  `code snippets or math values`\n"
            "  [Add custom citations or annotations]"
        )
        self.editor.textChanged.connect(self.trigger_autosave)
        self.highlighter = MarkdownHighlighter(self.editor.document())
        layout.addWidget(self.editor)

    def start_new_entry(self):
        self.current_id = str(uuid.uuid4())
        self.title_input.clear()
        self.category_input.clear()
        self.editor.clear()
        self.status_label.setText("New Session Initialized")

    def load_existing_entry(self, entry_id):
        data = self.db_manager.load_data()
        for entry in data:
            if entry.get("id") == entry_id:
                self.current_id = entry_id
                self.title_input.setText(entry.get("title", ""))
                self.category_input.setText(entry.get("category", ""))
                self.editor.setText(entry.get("content", ""))
                self.status_label.setText("Loaded from Library")
                break

    def trigger_autosave(self):
        self.status_label.setText("Saving Draft...")
        self.save_timer.start()

    def save_entry(self):
        if not self.current_id:
            return

        title = self.title_input.text().strip()
        category = self.category_input.text().strip() or "General"
        content = self.editor.toPlainText().strip()

        if not title and not content:
            self.status_label.setText("Empty Draft")
            return

        sentences_raw = split_into_sentences(content)
        sentences_data = []
        for s in sentences_raw:
            vec = generate_3d_vector(s, category)
            sentences_data.append({
                "text": s,
                "vector": vec
            })

        data = self.db_manager.load_data()

        entry = {
            "id": self.current_id,
            "title": title or "Untitled Concept",
            "category": category,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat(),
            "sentences": sentences_data
        }

        data = [item for item in data if item["id"] != self.current_id]
        data.append(entry)

        self.db_manager.save_data(data)
        self.status_label.setText("Draft Auto-Saved")