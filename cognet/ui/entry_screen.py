import uuid
import datetime
import numpy as np
import matplotlib.colors as mcolors
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QLabel, QFrame
from PySide6.QtCore import Qt, Signal, QTimer, QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from models.note_model import split_into_sentences, generate_3d_vector

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []

        title_format = QTextCharFormat()
        title_format.setForeground(QColor("#facc15"))
        title_format.setFontWeight(QFont.Bold)
        title_format.setFontPointSize(16)
        self.rules.append((QRegularExpression(r'^#\s.*'), title_format))

        subtitle_format = QTextCharFormat()
        subtitle_format.setForeground(QColor("#38bdf8"))
        subtitle_format.setFontWeight(QFont.Bold)
        subtitle_format.setFontPointSize(14)
        self.rules.append((QRegularExpression(r'^##\s.*'), subtitle_format))

        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#94a3b8"))
        list_format.setFontWeight(QFont.Bold)
        self.rules.append((QRegularExpression(r'^\s*[\*\-\+]\s'), list_format))

        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#0ea5e9"))
        code_format.setFontFamilies(["Courier New", "Consolas", "monospace"])
        self.rules.append((QRegularExpression(r'`[^`]+`'), code_format))

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
        
        self.mini_sc = None
        self.node_texts = []
        self.node_colors_hex = []
        self.rendered_indices = []
        self.focused_idx = None
        
        self._panning = False
        self._press_pos = None
        self._press_button = None
        self._pan_start_lims = None
        
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

        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)

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
        self.editor.setPlaceholderText("Write your ideas here. All standard markdown syntaxes apply...")
        self.editor.textChanged.connect(self.trigger_autosave)
        self.highlighter = MarkdownHighlighter(self.editor.document())
        left_layout.addWidget(self.editor)

        split_layout.addWidget(left_widget, stretch=3)

        right_widget = QFrame()
        right_widget.setObjectName("MiniViewport")
        right_widget.setStyleSheet("QFrame#MiniViewport { background-color: #0f172a; border: 1px solid #1e293b; border-radius: 12px; }")
        right_layout = QVBoxLayout(right_widget)
        # Squeeze margins to let plot explode into container
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)

        vp_title = QLabel("REAL-TIME PATHWAY")
        vp_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #facc15; letter-spacing: 1px; background: transparent;")
        vp_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(vp_title)

        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        self.mini_fig = Figure(figsize=(3, 3), dpi=100)
        self.mini_fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.mini_canvas = FigureCanvas(self.mini_fig)
        self.mini_canvas.setStyleSheet("background-color: transparent;")
        right_layout.addWidget(self.mini_canvas, stretch=1)

        self.vp_desc = QLabel("Left-Drag: Pan | Right-Drag: Rotate | Click Node: Focus")
        self.vp_desc.setStyleSheet("font-size: 11px; color: #64748b; background: transparent;")
        self.vp_desc.setAlignment(Qt.AlignCenter)
        self.vp_desc.setWordWrap(True)
        self.vp_desc.setMinimumHeight(65)
        right_layout.addWidget(self.vp_desc)

        split_layout.addWidget(right_widget, stretch=2)
        layout.addLayout(split_layout)

        self.mini_canvas.mpl_connect('scroll_event', self.on_scroll)
        self.mini_canvas.mpl_connect('button_press_event', self.on_press)
        self.mini_canvas.mpl_connect('button_release_event', self.on_release)
        self.mini_canvas.mpl_connect('motion_notify_event', self.on_motion)

    def draw_gradient_line(self, ax, p1, p2, c1_hex, c2_hex, weight):
        c1 = np.array(mcolors.to_rgb(c1_hex))
        c2 = np.array(mcolors.to_rgb(c2_hex))
        n = 6
        xs = np.linspace(p1[0], p2[0], n+1)
        ys = np.linspace(p1[1], p2[1], n+1)
        zs = np.linspace(p1[2], p2[2], n+1)
        for i in range(n):
            c = (1 - (i+0.5)/n)*c1 + ((i+0.5)/n)*c2
            ax.plot(xs[i:i+2], ys[i:i+2], zs[i:i+2], color=c, lw=weight, alpha=0.8)

    def start_new_entry(self):
        self.current_id = str(uuid.uuid4())
        self.title_input.clear()
        self.category_input.clear()
        self.editor.clear()
        self.focused_idx = None
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
                self.focused_idx = None
                self.status_label.setText("Loaded from Library")
                self.update_mini_plot()
                break

    def trigger_autosave(self):
        self.status_label.setText("Saving Draft...")
        self.save_timer.start()

    def save_entry(self):
        if not self.current_id: return
        title, category = self.title_input.text().strip(), self.category_input.text().strip() or "General"
        content = self.editor.toPlainText().strip()
        if not title and not content:
            self.status_label.setText("Empty Draft")
            return

        sents_data = [{"text": s, "vector": generate_3d_vector(s, category)} for s in split_into_sentences(content)]
        data = [item for item in self.db_manager.load_data() if item["id"] != self.current_id]
        data.append({
            "id": self.current_id, "title": title or "Untitled Concept",
            "category": category, "content": content,
            "timestamp": datetime.datetime.now().isoformat(), "sentences": sents_data
        })
        self.db_manager.save_data(data)
        self.status_label.setText("Draft Auto-Saved")

    def update_mini_plot(self):
        category = self.category_input.text().strip() or "General"
        content = self.editor.toPlainText().strip()

        self.mini_fig.clear()
        ax = self.mini_fig.add_subplot(projection='3d')
        ax.set_position([0, 0, 1, 1])
        self.mini_fig.patch.set_facecolor('#0f172a')
        ax.set_facecolor('#0f172a')
        ax.set_axis_off()

        try: ax.mouse_init(rotate_btn=3, zoom_btn=0)
        except Exception: pass
        ax._rotate_btn = 3
        ax._zoom_btn = 0
        if hasattr(ax, '_pan_btn'): ax._pan_btn = 0

        self.mini_sc = None
        self.node_texts, self.node_colors_hex, self.rendered_indices = [], [], []

        if not content:
            ax.text(0, 0, 0, "Awaiting mental syntax...", color='#64748b', ha='center', va='center', style='italic')
            self.mini_canvas.draw()
            return

        raw_vectors = []
        for s in split_into_sentences(content):
            if vec := generate_3d_vector(s, category):
                raw_vectors.append(vec)
                self.node_texts.append(s)

        if not raw_vectors:
            self.mini_canvas.draw()
            return

        from ui.embedding_viewer import project_to_3d, force_directed_3d
        coords = project_to_3d(raw_vectors)

        node_palette = ["#facc15", "#38bdf8", "#f472b6", "#4ade80", "#a78bfa", "#fb923c", "#2dd4bf", "#f87171"]
        self.node_colors_hex = [node_palette[i % len(node_palette)] for i in range(len(coords))]

        np_vectors = np.array(raw_vectors)
        norms = np.linalg.norm(np_vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        sim_matrix = np.dot(np_vectors / norms, (np_vectors / norms).T)

        threshold = 0.50
        adj_matrix = np.zeros_like(sim_matrix)
        for i in range(len(sim_matrix)):
            for j in np.argsort(sim_matrix[i])[::-1]:
                if i != j and sim_matrix[i, j] > threshold:
                    adj_matrix[i, j] = adj_matrix[j, i] = sim_matrix[i, j]

        physics_coords = force_directed_3d(coords, adj_matrix)
        xs, ys, zs = physics_coords[:, 0], physics_coords[:, 1], physics_coords[:, 2]

        self.rendered_indices = list(range(len(xs)))

        if self.focused_idx is not None and self.focused_idx < len(xs):
            idx = self.focused_idx
            targets = [idx] + [j for j in range(len(xs)) if adj_matrix[idx, j] > 0]
            self.rendered_indices = targets
            
            for j in targets[1:]:
                sim = adj_matrix[idx, j]
                weight = (sim - threshold) * 8 + 1
                self.draw_gradient_line(ax, physics_coords[idx], physics_coords[j], self.node_colors_hex[idx], self.node_colors_hex[j], weight)

            self.mini_sc = ax.scatter(xs[targets], ys[targets], zs[targets], c=[self.node_colors_hex[t] for t in targets], s=60, edgecolors='#ffffff', linewidths=1.0)
            
            min_x, max_x = np.min(xs[targets]), np.max(xs[targets])
            min_y, max_y = np.min(ys[targets]), np.max(ys[targets])
            min_z, max_z = np.min(zs[targets]), np.max(zs[targets])
            rng = max(max_x - min_x, max_y - min_y, max_z - min_z) * 1.5
            if rng < 0.5: rng = 2.0
            
            mid_x, mid_y, mid_z = xs[idx], ys[idx], zs[idx]
            ax.set_xlim(mid_x - rng/2, mid_x + rng/2)
            ax.set_ylim(mid_y - rng/2, mid_y + rng/2)
            ax.set_zlim(mid_z - rng/2, mid_z + rng/2)
        else:
            for i in range(len(xs)):
                for j in range(i+1, len(xs)):
                    if adj_matrix[i, j] > 0:
                        sim = adj_matrix[i, j]
                        weight = (sim - threshold) * 5 + 0.8
                        self.draw_gradient_line(ax, physics_coords[i], physics_coords[j], self.node_colors_hex[i], self.node_colors_hex[j], weight)

            self.mini_sc = ax.scatter(xs, ys, zs, c=self.node_colors_hex, s=45, depthshade=True, edgecolors='#0f172a', linewidths=0.5)
            
            min_x, max_x = np.min(xs), np.max(xs)
            min_y, max_y = np.min(ys), np.max(ys)
            min_z, max_z = np.min(zs), np.max(zs)
            rng = max(max_x - min_x, max_y - min_y, max_z - min_z) * 1.2
            if rng < 0.5: rng = 2.0
            
            mid_x, mid_y, mid_z = (max_x+min_x)/2, (max_y+min_y)/2, (max_z+min_z)/2
            ax.set_xlim(mid_x - rng/2, mid_x + rng/2)
            ax.set_ylim(mid_y - rng/2, mid_y + rng/2)
            ax.set_zlim(mid_z - rng/2, mid_z + rng/2)
            
            for i, (x, y, z) in enumerate(zip(xs, ys, zs)):
                ax.text(x, y, z + (rng * 0.04), f"N{i+1}", color='#e2e8f0', fontsize=7, ha='center')

        try: ax.set_box_aspect([1, 1, 1], zoom=1.35)
        except TypeError: ax.set_box_aspect([1, 1, 1]); ax.dist = 7

        self.mini_canvas.draw()

    def on_scroll(self, event):
        if event.inaxes is None: return
        ax = event.inaxes
        scale_factor = 1.15 if event.button == 'down' else 1 / 1.15
        xlim, ylim, zlim = ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d()
        def scale_lim(lim):
            mid, rng = (lim[0] + lim[1]) / 2, (lim[1] - lim[0]) / 2
            return (mid - rng * scale_factor, mid + rng * scale_factor)
        ax.set_xlim3d(scale_lim(xlim)); ax.set_ylim3d(scale_lim(ylim)); ax.set_zlim3d(scale_lim(zlim))
        event.canvas.draw_idle()

    def on_press(self, event):
        if event.inaxes is None: return
        self._press_pos = (event.x, event.y)
        self._press_button = event.button
        
        if event.button == 1:
            self._panning = True
            self._pan_start_lims = (event.inaxes.get_xlim3d(), event.inaxes.get_ylim3d(), event.inaxes.get_zlim3d())

    def on_release(self, event):
        self._panning = False
        if event.inaxes is None or self._press_pos is None: return
        
        dist = np.hypot(event.x - self._press_pos[0], event.y - self._press_pos[1])
        if dist < 10 and self._press_button == 1:
            if self.mini_sc is not None:
                cont, ind = self.mini_sc.contains(event)
                if cont:
                    self.focused_idx = self.rendered_indices[ind["ind"][0]]
                else:
                    self.focused_idx = None
                self.update_mini_plot()
        self._press_pos = None
        self._press_button = None

    def on_motion(self, event):
        if getattr(self, '_panning', False) and event.inaxes is not None and self._press_pos is not None:
            ax = event.inaxes
            dx, dy = event.x - self._press_pos[0], event.y - self._press_pos[1]
            w, h = ax.figure.canvas.get_width_height()

            x_span = self._pan_start_lims[0][1] - self._pan_start_lims[0][0]
            y_span = self._pan_start_lims[1][1] - self._pan_start_lims[1][0]
            z_span = self._pan_start_lims[2][1] - self._pan_start_lims[2][0]

            azim, elev = np.deg2rad(ax.azim), np.deg2rad(ax.elev)
            
            dx_data = - (dx / w) * max(x_span, y_span) * 0.8
            dy_data = - (dy / h) * z_span * 0.8
            
            shift_x = dx_data * np.sin(azim) - dy_data * np.cos(azim) * np.sin(elev)
            shift_y = -dx_data * np.cos(azim) - dy_data * np.sin(azim) * np.sin(elev)
            shift_z = dy_data * np.cos(elev)

            ax.set_xlim3d(self._pan_start_lims[0][0] + shift_x, self._pan_start_lims[0][1] + shift_x)
            ax.set_ylim3d(self._pan_start_lims[1][0] + shift_y, self._pan_start_lims[1][1] + shift_y)
            ax.set_zlim3d(self._pan_start_lims[2][0] + shift_z, self._pan_start_lims[2][1] + shift_z)
            self.mini_canvas.draw_idle()
            return

        if event.button is not None: return

        if event.inaxes is None or not hasattr(self, 'mini_sc') or self.mini_sc is None: return
            
        cont, ind = self.mini_sc.contains(event)
        if cont:
            idx = self.rendered_indices[ind["ind"][0]]
            text = self.node_texts[idx]
            snippet = text[:40] + "..." if len(text) > 40 else text
            
            display = f"Node {idx+1}: \"{snippet}\""
            self.vp_desc.setText(display)
            self.vp_desc.setStyleSheet(f"font-size: 11px; color: {self.node_colors_hex[idx]}; background: transparent; font-weight: bold;")
        else:
            self.vp_desc.setText("Left-Drag: Pan | Right-Drag: Rotate | Click Node: Focus")
            self.vp_desc.setStyleSheet("font-size: 11px; color: #64748b; background: transparent;")