from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch
import sys
sys.path.append('..')
from utils.database import DatabaseConnection


class DashboardPage(QWidget):
    def __init__(self, username, user_id=1):
        super().__init__()
        self.username = username
        self.user_id = user_id
        self.db = DatabaseConnection()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 0, 35, 20)
        layout.setSpacing(20)

        # Dashboard title
        dashboard_title = QLabel("Dashboard")
        dashboard_title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        dashboard_title.setContentsMargins(0, 20, 0, 10)
        layout.addWidget(dashboard_title, alignment=Qt.AlignLeft)

        # Welcome Card
        welcome_card = self.create_welcome_card()
        layout.addWidget(welcome_card)

        # Bar Chart
        chart_frame = self.create_chart()
        layout.addWidget(chart_frame, alignment=Qt.AlignLeft)

    def create_welcome_card(self):
        welcome_card = QFrame()
        welcome_card.setStyleSheet("""
            QFrame {
                background-color: #E6EFFA;
                border-radius: 12px;
                padding: 40px;
            }
        """)
        welcome_card.setMinimumHeight(400)
        welcome_card.setMaximumHeight(500)
        welcome_card.setMinimumWidth(850)

        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(10, 10, 10, 10)
        welcome_layout.setSpacing(10)
        welcome_layout.setAlignment(Qt.AlignCenter)

        welcome_title = QLabel(f"Welcome back, {self.username}!")
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_title.setStyleSheet("font-size: 60px; font-weight: bold; color: #333;")
        
        welcome_sub = QLabel("Your students are waiting to learn")
        welcome_sub.setAlignment(Qt.AlignCenter)
        welcome_sub.setStyleSheet("font-size: 28px; color: #555;")

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_sub)

        return welcome_card

    def create_chart(self):
        chart_frame = QFrame()
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(0)
        chart_frame.setMinimumHeight(250)
        chart_frame.setMinimumWidth(660)

        figure = Figure(figsize=(8, 4))
        figure.patch.set_alpha(0)  # transparent background
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)
        ax.set_facecolor("none")

        # load ang real data from database
        stats = self.db.get_section_statistics(self.user_id)
        
        # kunin lahat ng sections from My Classes (sorted alphabetically)
        labels = []
        values = []
        
        if stats:
            # I-sort ang sections alphabetically
            sorted_sections = sorted(stats.items())
            for section_name, count in sorted_sections:
                labels.append(section_name)
                values.append(count)
        else:
            # Kung walang sections, ipakita ang empty graph
            labels = ["No Sections Yet"]
            values = [0]
        
        # set ang colors - repeating pattern
        colors = ["#2F1802", "#141C04", "#481409", "#060F45"] * ((len(labels) // 4) + 1)
        colors = colors[:len(labels)]

        bars = ax.bar(labels, values, color=colors)
        for bar in bars:
            x, y = bar.get_xy()
            width, height = bar.get_width(), bar.get_height()
            ax.add_patch(FancyBboxPatch((x, 0), width, height,
                                        boxstyle="round,pad=0.02",
                                        linewidth=0,
                                        facecolor=bar.get_facecolor()))
            bar.set_visible(False)

        # I-set ang y-axis limit based sa max value
        max_value = max(values) if values else 0
        ax.set_ylim(0, max(max_value + 5, 10))  # At least 10 para maganda tingnan
        ax.set_ylabel("Students", fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(axis='x', length=0, labelsize=12, colors="#333")
        ax.tick_params(axis='y', labelsize=11, colors="#555")

        for i, val in enumerate(values):
            ax.text(i, val + 0.5, str(val), ha='center', va='bottom', 
                   fontsize=11, fontweight='600', color="#222")

        figure.tight_layout(pad=2)
        chart_layout.addWidget(canvas, alignment=Qt.AlignRight)
        
        # I-save ang canvas para ma-refresh later
        self.chart_canvas = canvas
        self.chart_figure = figure

        return chart_frame
    
    def refresh_chart(self):
        """I-refresh ang chart with updated data from database"""
        # I-clear ang current figure
        self.chart_figure.clear()
        ax = self.chart_figure.add_subplot(111)
        ax.set_facecolor("none")
        
        # I-load ang updated data
        stats = self.db.get_section_statistics(self.user_id)
        
        # I-kunin lahat ng sections from My Classes (sorted alphabetically)
        labels = []
        values = []
        
        if stats:
            # I-sort ang sections alphabetically
            sorted_sections = sorted(stats.items())
            for section_name, count in sorted_sections:
                labels.append(section_name)
                values.append(count)
        else:
            # Kung walang sections, ipakita ang empty graph
            labels = ["No Sections Yet"]
            values = [0]
        
        # I-set ang colors - repeating pattern
        colors = ["#836FFF", "#C8B6FF", "#9A7FF0", "#000000"] * ((len(labels) // 4) + 1)
        colors = colors[:len(labels)]
        
        bars = ax.bar(labels, values, color=colors)
        for bar in bars:
            x, y = bar.get_xy()
            width, height = bar.get_width(), bar.get_height()
            ax.add_patch(FancyBboxPatch((x, 0), width, height,
                                        boxstyle="round,pad=0.02",
                                        linewidth=0,
                                        facecolor=bar.get_facecolor()))
            bar.set_visible(False)
        
        max_value = max(values) if values else 0
        ax.set_ylim(0, max(max_value + 5, 10))
        ax.set_ylabel("Students", fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(axis='x', length=0, labelsize=12, colors="#333")
        ax.tick_params(axis='y', labelsize=11, colors="#555")
        
        for i, val in enumerate(values):
            ax.text(i, val + 0.5, str(val), ha='center', va='bottom', 
                   fontsize=11, fontweight='600', color="#222")
        
        self.chart_figure.tight_layout(pad=2)
        self.chart_canvas.draw()
