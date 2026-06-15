import numpy as np
import matplotlib.colors as mcolors
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

def force_directed_3d(coords, adj_matrix, iterations=60):
    pos = coords.copy()
    pos += np.random.randn(*pos.shape) * 0.05
    N = len(pos)
    k = 1.5 / (N**(1/3)) if N > 0 else 1.5
    
    for _ in range(iterations):
        diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
        dist = np.linalg.norm(diff, axis=-1)
        np.fill_diagonal(dist, 1.0)
        
        repulse = (k**2 / dist**2)[..., np.newaxis] * diff
        for i in range(3): np.fill_diagonal(repulse[..., i], 0)
        disp = np.sum(repulse, axis=1)
        
        attract = (dist**2 / k)[..., np.newaxis] * diff * adj_matrix[..., np.newaxis]
        disp -= np.sum(attract, axis=1)
        
        disp -= pos * 0.05
        
        disp_norm = np.linalg.norm(disp, axis=-1)
        disp_norm[disp_norm == 0] = 1.0
        step = (disp / disp_norm[:, np.newaxis]) * np.minimum(disp_norm, k)[:, np.newaxis]
        pos += step
    return pos


class EmbeddingViewer(QWidget):
    back_clicked = Signal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        
        self.view_mode = "vector"
        self.focused_idx = None
        
        self.sc = None
        self.texts = []
        self.categories = []
        self.vector_metadata = []
        self.rendered_indices = []
        
        self._panning = False
        self._press_pos = None
        self._press_button = None
        self._pan_start_lims = None
        
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

        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(10)
        
        self.btn_vector_tab = QPushButton("Origin Vectors")
        self.btn_vector_tab.clicked.connect(lambda: self.switch_mode("vector"))
        tab_layout.addWidget(self.btn_vector_tab)
        
        self.btn_pathway_tab = QPushButton("Total Pathway")
        self.btn_pathway_tab.clicked.connect(lambda: self.switch_mode("pathway"))
        tab_layout.addWidget(self.btn_pathway_tab)

        header_layout.addLayout(tab_layout)
        layout.addLayout(header_layout)

        # Full Bleed Canvas Integration
        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.canvas, stretch=4)

        self.hud_card = QFrame()
        self.hud_card.setObjectName("hudCard")
        self.hud_card.setStyleSheet("QFrame#hudCard { background-color: #16161a; border: 1px solid #2a2a32; border-radius: 12px; padding: 15px; }")
        hud_layout = QVBoxLayout(self.hud_card)
        
        self.hud_category = QLabel("SYSTEM STATUS: ACTIVE")
        self.hud_category.setStyleSheet("color: #8f8f9d; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        hud_layout.addWidget(self.hud_category)

        self.hud_text = QLabel("Left-Drag: Pan  |  Right-Drag: Rotate  |  Left-Click Node: Focus  |  Right-Click Node: Delete")
        self.hud_text.setStyleSheet("color: #e2e2e6; font-size: 14px; font-style: italic;")
        self.hud_text.setWordWrap(True)
        hud_layout.addWidget(self.hud_text)

        layout.addWidget(self.hud_card, stretch=1)

        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
        self.update_tab_styles()

    def switch_mode(self, mode):
        self.view_mode = mode
        self.focused_idx = None
        self.update_tab_styles()
        self.load_and_render()

    def update_tab_styles(self):
        active_style = "background-color: #38bdf8; color: #07090e; font-weight: bold; border-radius: 8px;"
        inactive_style = "background-color: #0f172a; color: #64748b; border: 1px solid #1e293b; border-radius: 8px;"
        self.btn_vector_tab.setStyleSheet(active_style if self.view_mode == "vector" else inactive_style)
        self.btn_pathway_tab.setStyleSheet(active_style if self.view_mode == "pathway" else inactive_style)

    def draw_gradient_line(self, ax, p1, p2, c1_hex, c2_hex, weight):
        c1 = np.array(mcolors.to_rgb(c1_hex))
        c2 = np.array(mcolors.to_rgb(c2_hex))
        n = 8
        xs = np.linspace(p1[0], p2[0], n+1)
        ys = np.linspace(p1[1], p2[1], n+1)
        zs = np.linspace(p1[2], p2[2], n+1)
        for i in range(n):
            c = (1 - (i+0.5)/n)*c1 + ((i+0.5)/n)*c2
            ax.plot(xs[i:i+2], ys[i:i+2], zs[i:i+2], color=c, lw=weight, alpha=0.8)

    def load_and_render(self):
        self.fig.clear()
        self.texts, self.categories, self.vector_metadata = [], [], []

        data = self.db_manager.load_data()
        raw_vectors, colors = [], []
        category_palette = ["#38bdf8", "#facc15", "#60a5fa", "#fbbf24", "#0ea5e9", "#eab308", "#93c5fd", "#f472b6", "#4ade80"]

        def get_color(cat): return category_palette[abs(hash(cat.lower())) % len(category_palette)]

        for entry in data:
            entry_id, cat = entry.get("id"), entry.get("category", "General")
            color = get_color(cat)
            for idx, s_obj in enumerate(entry.get("sentences", [])):
                if vec := s_obj.get("vector"):
                    raw_vectors.append(vec)
                    self.texts.append(s_obj.get("text", ""))
                    self.categories.append(cat)
                    colors.append(color)
                    self.vector_metadata.append({"entry_id": entry_id, "sentence_idx": idx, "text": s_obj.get("text", "")})

        # --- Hardcode Maximize Plot Container Space ---
        ax = self.fig.add_subplot(projection='3d')
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        ax.set_position([0, 0, 1, 1])
        
        self.fig.patch.set_facecolor('#07090e')
        ax.set_facecolor('#07090e')
        ax.set_axis_off()

        # --- Hijack Matplotlib Native Mouse Bindings ---
        try: ax.mouse_init(rotate_btn=3, zoom_btn=0)
        except Exception: pass
        ax._rotate_btn = 3  # Force Right-Click for Rotation
        ax._zoom_btn = 0    # Disable Click-Drag Zooming completely
        if hasattr(ax, '_pan_btn'): ax._pan_btn = 0

        if raw_vectors:
            target_dim = max(len(v) for v in raw_vectors)
            valid_indices = [i for i, v in enumerate(raw_vectors) if len(v) == target_dim]
            raw_vectors = [raw_vectors[i] for i in valid_indices]
            self.texts = [self.texts[i] for i in valid_indices]
            self.categories = [self.categories[i] for i in valid_indices]
            colors = [colors[i] for i in valid_indices]
            self.vector_metadata = [self.vector_metadata[i] for i in valid_indices]
            
        if not raw_vectors:
            ax.text(0, 0, 0, "No vectors found.\nCreate entries to begin mapping.", color='#8f8f9d', ha='center', va='center')
            self.canvas.draw()
            return

        coords = project_to_3d(raw_vectors)
        self.rendered_indices = list(range(len(coords)))
        
        if self.view_mode == "vector":
            xs, ys, zs = coords[:, 0], coords[:, 1], coords[:, 2]
            max_val = np.max(np.abs(coords)) if coords.size > 0 else 1.0
            limit = max(max_val * 1.2, 1.0)
            
            ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit); ax.set_zlim(-limit, limit)
            
            ax.plot([-limit, limit], [0,0], [0,0], color='#1e293b', lw=1, alpha=0.5)
            ax.plot([0,0], [-limit, limit], [0,0], color='#1e293b', lw=1, alpha=0.5)
            ax.plot([0,0], [0,0], [-limit, limit], color='#1e293b', lw=1, alpha=0.5)

            for x, y, z, col in zip(xs, ys, zs, colors):
                ax.plot([0, x], [0, y], [0, z], color=col, alpha=0.25, linewidth=1.2)
                ax.quiver(0, 0, 0, x, y, z, color=col, alpha=0.3, arrow_length_ratio=0.08, linewidths=0.5)

            self.sc = ax.scatter(xs, ys, zs, c=colors, s=60, depthshade=True, edgecolors='#07090e', linewidths=0.5)

        elif self.view_mode == "pathway":
            np_vectors = np.array(raw_vectors)
            norms = np.linalg.norm(np_vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1
            sim_matrix = np.dot(np_vectors / norms, (np_vectors / norms).T)
            
            threshold = 0.50
            adj_matrix = np.zeros_like(sim_matrix)
            for i in range(len(sim_matrix)):
                top_matches = np.argsort(sim_matrix[i])[::-1]
                matches_found = 0
                for j in top_matches:
                    if i != j and sim_matrix[i, j] > threshold:
                        adj_matrix[i, j] = sim_matrix[i, j]
                        adj_matrix[j, i] = sim_matrix[i, j]
                        matches_found += 1
                        if matches_found >= 3: break

            physics_coords = force_directed_3d(coords, adj_matrix)
            xs, ys, zs = physics_coords[:, 0], physics_coords[:, 1], physics_coords[:, 2]

            if self.focused_idx is not None:
                idx = self.focused_idx
                targets = [idx] + [j for j in range(len(xs)) if adj_matrix[idx, j] > 0]
                self.rendered_indices = targets  
                
                for j in targets[1:]:
                    sim = adj_matrix[idx, j]
                    weight = (sim - threshold) * 8 + 1
                    self.draw_gradient_line(ax, physics_coords[idx], physics_coords[j], colors[idx], colors[j], weight)
                    mid_x, mid_y, mid_z = (xs[idx]+xs[j])/2, (ys[idx]+ys[j])/2, (zs[idx]+zs[j])/2
                    ax.text(mid_x, mid_y, mid_z + 0.05, f"{sim*100:.0f}%", color='#e2e8f0', fontsize=8, ha='center', weight='bold')

                self.sc = ax.scatter(xs[targets], ys[targets], zs[targets], c=[colors[t] for t in targets], s=90, edgecolors='#ffffff', linewidths=1.0)
                
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
                            self.draw_gradient_line(ax, physics_coords[i], physics_coords[j], colors[i], colors[j], weight)
                
                self.sc = ax.scatter(xs, ys, zs, c=colors, s=60, depthshade=True, edgecolors='#07090e', linewidths=0.5)
                
                min_x, max_x = np.min(xs), np.max(xs)
                min_y, max_y = np.min(ys), np.max(ys)
                min_z, max_z = np.min(zs), np.max(zs)
                rng = max(max_x - min_x, max_y - min_y, max_z - min_z) * 1.2
                if rng < 0.5: rng = 2.0
                
                mid_x, mid_y, mid_z = (max_x+min_x)/2, (max_y+min_y)/2, (max_z+min_z)/2
                ax.set_xlim(mid_x - rng/2, mid_x + rng/2)
                ax.set_ylim(mid_y - rng/2, mid_y + rng/2)
                ax.set_zlim(mid_z - rng/2, mid_z + rng/2)

        # Force expand bounding box to completely kill invisible borders
        try: ax.set_box_aspect([1, 1, 1], zoom=1.35)
        except TypeError: ax.set_box_aspect([1, 1, 1]); ax.dist = 7
        
        self.canvas.draw()

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
            # 1. Left Click: Enable our Custom Pan math
            self._panning = True
            self._pan_start_lims = (event.inaxes.get_xlim3d(), event.inaxes.get_ylim3d(), event.inaxes.get_zlim3d())

    def on_release(self, event):
        self._panning = False
        if event.inaxes is None or self._press_pos is None: return
        
        dist = np.hypot(event.x - self._press_pos[0], event.y - self._press_pos[1])
        if dist < 10: 
            if self._press_button == 1:
                if self.sc is not None:
                    cont, ind = self.sc.contains(event)
                    if cont and self.view_mode == "pathway":
                        self.focused_idx = self.rendered_indices[ind["ind"][0]]
                    else:
                        self.focused_idx = None
                    self.load_and_render()
            elif self._press_button == 3:
                if self.sc is not None:
                    cont, ind = self.sc.contains(event)
                    if cont:
                        global_idx = self.rendered_indices[ind["ind"][0]]
                        if global_idx < len(self.vector_metadata):
                            self.confirm_and_delete_vector(self.vector_metadata[global_idx])
                            
        self._press_pos = None
        self._press_button = None

    def on_motion(self, event):
        if getattr(self, '_panning', False) and event.inaxes is not None and self._press_pos is not None:
            # Execute True Plane Panning
            ax = event.inaxes
            dx, dy = event.x - self._press_pos[0], event.y - self._press_pos[1]
            w, h = ax.figure.canvas.get_width_height()

            x_span = self._pan_start_lims[0][1] - self._pan_start_lims[0][0]
            y_span = self._pan_start_lims[1][1] - self._pan_start_lims[1][0]
            z_span = self._pan_start_lims[2][1] - self._pan_start_lims[2][0]

            azim, elev = np.deg2rad(ax.azim), np.deg2rad(ax.elev)
            
            # Map pixels to 3D movement distances 
            dx_data = - (dx / w) * max(x_span, y_span) * 0.8
            dy_data = - (dy / h) * z_span * 0.8
            
            shift_x = dx_data * np.sin(azim) - dy_data * np.cos(azim) * np.sin(elev)
            shift_y = -dx_data * np.cos(azim) - dy_data * np.sin(azim) * np.sin(elev)
            shift_z = dy_data * np.cos(elev)

            ax.set_xlim3d(self._pan_start_lims[0][0] + shift_x, self._pan_start_lims[0][1] + shift_x)
            ax.set_ylim3d(self._pan_start_lims[1][0] + shift_y, self._pan_start_lims[1][1] + shift_y)
            ax.set_zlim3d(self._pan_start_lims[2][0] + shift_z, self._pan_start_lims[2][1] + shift_z)
            self.canvas.draw_idle()
            return

        if event.button is not None: return

        if event.inaxes is None or self.sc is None: return
        cont, ind = self.sc.contains(event)
        if cont:
            global_idx = self.rendered_indices[ind["ind"][0]]
            if global_idx < len(self.texts):
                txt, cat = self.texts[global_idx], self.categories[global_idx]
                self.hud_category.setText(f"CATEGORY: {cat}")
                self.hud_text.setText(f'"{txt}"')
                self.hud_text.setStyleSheet("color: #38bdf8; font-size: 14px; font-weight: 500;")
        else:
            self.hud_category.setText("SYSTEM STATUS: ACTIVE")
            self.hud_text.setText("Left-Drag: Pan  |  Right-Drag: Rotate  |  Left-Click Node: Focus")
            self.hud_text.setStyleSheet("color: #8f8f9d; font-size: 14px; font-style: italic;")

    def confirm_and_delete_vector(self, meta):
        reply = QMessageBox.question(self, "Delete Node", f"Delete this vector?\n\n\"{meta['text']}\"", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            data = self.db_manager.load_data()
            for entry in data:
                if entry.get("id") == meta["entry_id"]:
                    sents = entry.get("sentences", [])
                    if 0 <= meta["sentence_idx"] < len(sents):
                        sents.pop(meta["sentence_idx"])
                        entry["content"] = " ".join([s["text"] for s in sents])
                        break
            self.db_manager.save_data(data)
            self.focused_idx = None
            self.load_and_render()