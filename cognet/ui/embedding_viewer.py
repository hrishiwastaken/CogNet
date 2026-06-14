import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QMessageBox
from PySide6.QtCore import Qt, Signal
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def project_to_3d(embeddings_list: list[list[float]]) -> np.ndarray:
    X = np.array(embeddings_list)
    N, D = X.shape
    if D <= 3:
        if D < 3:
            padded = np.zeros((N, 3))
            padded[:, :D] = X
            return padded
        return X
    if N < 3:
        rng = np.random.RandomState(42)
        proj_matrix = rng.randn(D, 3)
        proj_matrix /= np.linalg.norm(proj_matrix, axis=0)
        return np.dot(X, proj_matrix)
    mean = np.mean(X, axis=0)
    X_centered = X - mean
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    X_projected = np.dot(X_centered, Vt[:3].T)
    return X_projected


class EmbeddingViewer(QWidget):
    back_clicked = Signal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.sc = None
        self.texts = []
        self.categories = []
        self.vector_metadata = [] # Tracks specific indices back to their entries
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Back to Menu")
        self.btn_back.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(self.btn_back)

        header_layout.addStretch()

        title_label = QLabel("3D Vector Space representation")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00e5ff;")
        header_layout.addWidget(title_label)
        layout.addLayout(header_layout)

        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.canvas, stretch=4)

        self.hud_card = QFrame()
        self.hud_card.setObjectName("hudCard")
        self.hud_card.setStyleSheet("""
            QFrame#hudCard {
                background-color: #16161a;
                border: 1px solid #2a2a32;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        hud_layout = QVBoxLayout(self.hud_card)
        
        self.hud_category = QLabel("SYSTEM STATUS: ACTIVE")
        self.hud_category.setStyleSheet("color: #8f8f9d; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        hud_layout.addWidget(self.hud_category)

        self.hud_text = QLabel("Hover over any vector node to view mental syntax...")
        self.hud_text.setStyleSheet("color: #e2e2e6; font-size: 14px; font-style: italic;")
        self.hud_text.setWordWrap(True)
        hud_layout.addWidget(self.hud_text)

        layout.addWidget(self.hud_card, stretch=1)

    def load_and_render(self):
        self.fig.clear()
        self.texts = []
        self.categories = []
        self.vector_metadata = []

        data = self.db_manager.load_data()
        raw_vectors = []
        colors = []
        
        category_palette = ["#38bdf8", "#facc15", "#60a5fa", "#fbbf24", "#0ea5e9", "#eab308", "#93c5fd"]

        def get_color(cat):
            return category_palette[abs(hash(cat.lower())) % len(category_palette)]

        for entry in data:
            entry_id = entry.get("id")
            cat = entry.get("category", "General")
            color = get_color(cat)
            for idx, sentence_obj in enumerate(entry.get("sentences", [])):
                text = sentence_obj.get("text", "")
                vec = sentence_obj.get("vector", [])
                if vec:
                    raw_vectors.append(vec)
                    self.texts.append(text)
                    self.categories.append(cat)
                    colors.append(color)
                    self.vector_metadata.append({
                        "entry_id": entry_id,
                        "sentence_idx": idx,
                        "text": text
                    })

        ax = self.fig.add_subplot(projection='3d')
        self.fig.patch.set_facecolor('#07090e')
        ax.set_facecolor('#07090e')

        if not raw_vectors:
            ax.text(0, 0, 0, "No vectors generated yet.\nWrite your first entry!", 
                    color='#8f8f9d', ha='center', va='center', fontsize=12)
            ax.set_axis_off()
            self.canvas.draw()
            return

        coords = project_to_3d(raw_vectors)
        xs = coords[:, 0]
        ys = coords[:, 1]
        zs = coords[:, 2]

        # 1. Establish strict symmetric limits centered at the origin
        max_val = np.max(np.abs(coords)) if coords.size > 0 else 1.0
        limit = max(max_val * 1.2, 1.0)
        
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_zlim(-limit, limit)
        
        # 2. Fix the aspect ratio to a perfect cube
        ax.set_box_aspect([1, 1, 1])
        
        # 3. Use clean modern dark styling by turning default axes decorations off
        ax.set_axis_off()

        # 4. Draw our own stable, clean coordinate axes passing through the origin (0, 0, 0)
        axis_color = '#1e293b'
        axis_alpha = 0.5
        ax.plot([-limit, limit], [0, 0], [0, 0], color=axis_color, linestyle='-', linewidth=1, alpha=axis_alpha)
        ax.plot([0, 0], [-limit, limit], [0, 0], color=axis_color, linestyle='-', linewidth=1, alpha=axis_alpha)
        ax.plot([0, 0], [0, 0], [-limit, limit], color=axis_color, linestyle='-', linewidth=1, alpha=axis_alpha)

        # 5. Draw subtle grid on Z=0 (the ground/base plane)
        grid_color = '#0f172a'
        grid_ticks = 4
        for val in np.linspace(-limit, limit, grid_ticks * 2 + 1):
            if abs(val) < 1e-5:
                continue  # Skip primary axes
            # Line parallel to Y-axis
            ax.plot([val, val], [-limit, limit], [0, 0], color=grid_color, linestyle=':', linewidth=0.5, alpha=0.3)
            # Line parallel to X-axis
            ax.plot([-limit, limit], [val, val], [0, 0], color=grid_color, linestyle=':', linewidth=0.5, alpha=0.3)

        # 6. Add modern text labels at the endpoints
        label_color = '#8f8f9d'
        ax.text(limit * 1.05, 0, 0, "+X", color=label_color, fontsize=8, ha='center', va='center')
        ax.text(0, limit * 1.05, 0, "+Y", color=label_color, fontsize=8, ha='center', va='center')
        ax.text(0, 0, limit * 1.05, "+Z", color=label_color, fontsize=8, ha='center', va='center')

        # 7. Draw vector lines and arrows from (0,0,0) to target coordinate (x,y,z)
        for x, y, z, col in zip(xs, ys, zs, colors):
            ax.plot([0, x], [0, y], [0, z], color=col, alpha=0.25, linewidth=1.2)
            # Use small thin quivers to denote direction, starting from the origin (0, 0, 0)
            ax.quiver(0, 0, 0, x, y, z, color=col, alpha=0.3, arrow_length_ratio=0.08, linewidths=0.5)

        # 8. Render the scatter nodes
        self.sc = ax.scatter(xs, ys, zs, c=colors, s=60, depthshade=True, edgecolors='#07090e', linewidths=0.5)

        # Mouse Listeners
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.draw()

    def on_hover(self, event):
        if event.inaxes is None or self.sc is None:
            return
        cont, ind = self.sc.contains(event)
        if cont:
            idx = ind["ind"][0]
            if idx < len(self.texts):
                sentence = self.texts[idx]
                category = self.categories[idx]
                self.hud_category.setText(f"CATEGORY: {category} (Right-click to Delete Vector)")
                self.hud_text.setText(f'"{sentence}"')
                self.hud_text.setStyleSheet("color: #38bdf8; font-size: 14px; font-weight: 500;")
        else:
            self.hud_category.setText("SYSTEM STATUS: ACTIVE")
            self.hud_text.setText("Hover over any vector node to view mental syntax...")
            self.hud_text.setStyleSheet("color: #8f8f9d; font-size: 14px; font-style: italic;")

    def on_click(self, event):
        # Button 3 is Right-click
        if event.button == 3 and event.inaxes is not None and self.sc is not None:
            cont, ind = self.sc.contains(event)
            if cont:
                idx = ind["ind"][0]
                if idx < len(self.vector_metadata):
                    meta = self.vector_metadata[idx]
                    self.confirm_and_delete_vector(meta)

    def confirm_and_delete_vector(self, meta):
        reply = QMessageBox.question(
            self, 
            "Delete Vector Node",
            f"Are you sure you want to delete this sentence vector?\n\n\"{meta['text']}\"",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            data = self.db_manager.load_data()
            for entry in data:
                if entry.get("id") == meta["entry_id"]:
                    sentences = entry.get("sentences", [])
                    if 0 <= meta["sentence_idx"] < len(sentences):
                        sentences.pop(meta["sentence_idx"])
                        entry["sentences"] = sentences
                        # Synchronize core paragraph display string
                        entry["content"] = " ".join([s["text"] for s in sentences])
                        break
            self.db_manager.save_data(data)
            self.load_and_render()