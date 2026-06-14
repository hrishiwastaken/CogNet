import uuid
import datetime
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QLabel, QFrame
from PySide6.QtCore import Qt, Signal, QTimer, QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from models.note_model import split_into_sentences, generate_3d_vector


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []

        # Titles (# Header) -> Yellow Accent
        title_format = QTextCharFormat()
        title_format.setForeground(QColor("#facc15"))
        title_format.setFontWeight(QFont.Bold)
        title_format.setFontPointSize(16)
        self.rules.append((QRegularExpression(r'^#\s.*'), title_format))

        # Subtitles (## Header) -> Light Blue
        subtitle_format = QTextCharFormat()
        subtitle_format.setForeground(QColor("#38bdf8"))
        subtitle_format.setFontWeight(QFont.Bold)
        subtitle_format.setFontPointSize(14)
        self.rules.append((QRegularExpression(r'^##\s.*'), subtitle_format))

        # Lists (* or -) -> Subtle Slate Blue
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#94a3b8"))
        list_format.setFontWeight(QFont.Bold)
        self.rules.append((QRegularExpression(r'^\s*[\*\-\+]\s'), list_format))

        # Code snippets (`code`) -> Light Cyan/Blue
        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#0ea5e9"))
        code_format.setFontFamilies(["Courier New", "Consolas", "monospace"])
        self.rules.append((QRegularExpression(r'`[^`]+`'), code_format))

        # Annotations ([annotation]) -> Mint Green
        anno_format = QTextCharFormat()
        anno_format.setForeground(QColor("#34d399"))
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

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_id = None
        self.init_ui()

        self.save_timer = QTimer(self)
        self.save_timer.setInterval(1000)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_entry)
        self.save_timer.timeout.connect(self.update_mini_plot)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Back to Menu")
        self.btn_back.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(self.btn_back)

        header_layout.addStretch()

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #64748b; font-size: 12px;")
        header_layout.addWidget(self.status_label)
        layout.addLayout(header_layout)

        # Main horizontal split layout
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)

        # Left Column: Inputs & Editor
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

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

        left_layout.addLayout(fields_layout)

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
        left_layout.addWidget(self.editor)

        split_layout.addWidget(left_widget, stretch=3)

        # Right Column: Mini 3D Plot Viewport
        right_widget = QFrame()
        right_widget.setObjectName("MiniViewport")
        right_widget.setStyleSheet("""
            QFrame#MiniViewport {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 12px;
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 15, 10, 15)
        right_layout.setSpacing(10)

        vp_title = QLabel("REAL-TIME COGNITIVE PATHWAY")
        vp_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #facc15; letter-spacing: 1px; background: transparent;")
        vp_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(vp_title)

        # Matplotlib elements
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        self.mini_fig = Figure(figsize=(3, 3), dpi=100)
        self.mini_canvas = FigureCanvas(self.mini_fig)
        self.mini_canvas.setStyleSheet("background-color: transparent;")
        right_layout.addWidget(self.mini_canvas, stretch=1)

        vp_desc = QLabel("Thought flow vector projection")
        vp_desc.setStyleSheet("font-size: 11px; color: #64748b; background: transparent;")
        vp_desc.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(vp_desc)

        split_layout.addWidget(right_widget, stretch=2)
        
        layout.addLayout(split_layout)

    def start_new_entry(self):
        self.current_id = str(uuid.uuid4())
        self.title_input.clear()
        self.category_input.clear()
        self.editor.clear()
        self.status_label.setText("New Session Initialized")
        self.update_mini_plot()

    def load_existing_entry(self, entry_id):
        data = self.db_manager.load_data()
        for entry in data:
            if entry.get("id") == entry_id:
                self.current_id = entry_id
                self.title_input.setText(entry.get("title", ""))
                self.category_input.setText(entry.get("category", ""))
                self.editor.setText(entry.get("content", ""))
                self.status_label.setText("Loaded from Library")
                self.update_mini_plot()
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

    def update_mini_plot(self):
        category = self.category_input.text().strip() or "General"
        content = self.editor.toPlainText().strip()

        self.mini_fig.clear()
        ax = self.mini_fig.add_subplot(projection='3d')
        self.mini_fig.patch.set_facecolor('#0f172a')
        ax.set_facecolor('#0f172a')
        ax.set_axis_off()

        if not content:
            ax.text(0, 0, 0, "Awaiting mental syntax...", 
                    color='#64748b', ha='center', va='center', fontsize=9, style='italic')
            self.mini_canvas.draw()
            return

        sentences_raw = split_into_sentences(content)
        if not sentences_raw:
            ax.text(0, 0, 0, "Awaiting mental syntax...", 
                    color='#64748b', ha='center', va='center', fontsize=9, style='italic')
            self.mini_canvas.draw()
            return

        raw_vectors = []
        for s in sentences_raw:
            vec = generate_3d_vector(s, category)
            if vec:
                raw_vectors.append(vec)

        if not raw_vectors:
            self.mini_canvas.draw()
            return

        from ui.embedding_viewer import project_to_3d
        coords = project_to_3d(raw_vectors)
        xs = coords[:, 0]
        ys = coords[:, 1]
        zs = coords[:, 2]

        max_val = np.max(np.abs(coords)) if coords.size > 0 else 1.0
        limit = max(max_val * 1.2, 1.0)
        
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_zlim(-limit, limit)
        ax.set_box_aspect([1, 1, 1])

        # Draw mini stable axes
        axis_color = '#1e293b'
        ax.plot([-limit, limit], [0, 0], [0, 0], color=axis_color, linestyle='-', linewidth=0.8, alpha=0.4)
        ax.plot([0, 0], [-limit, limit], [0, 0], color=axis_color, linestyle='-', linewidth=0.8, alpha=0.4)
        ax.plot([0, 0], [0, 0], [-limit, limit], color=axis_color, linestyle='-', linewidth=0.8, alpha=0.4)

        # Plot sequential pathway line
        if len(xs) > 1:
            ax.plot(xs, ys, zs, color='#38bdf8', linestyle='--', linewidth=1.2, alpha=0.7)

        # Plot the nodes
        ax.scatter(xs, ys, zs, c='#facc15', s=35, depthshade=True, edgecolors='#0f172a', linewidths=0.5)
        
        self.mini_canvas.draw()