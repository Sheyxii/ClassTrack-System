from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch

# === DASHBOARD ===
class DashboardWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("ClassTrack - Dashboard")
        self.setGeometry(100, 100, 1250, 750)
        self.setStyleSheet("background-color: #E7E7DF;")

        # === Main container ===
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(main_widget)

        # SIDEBAR
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #555; color: white;")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(25, 45, 25, 45)
        sidebar_layout.setSpacing(25)

        logo = QLabel("ClassTrack")
        logo.setStyleSheet("font-size: 22px; font-weight: bold;")
        sidebar_layout.addWidget(logo)
        sidebar_layout.addSpacing(30)

        self.buttons = {}
        button_names = ["Dashboard", "My Classes", "Attendance", "Schedule", "Resources", "Settings"]
        for b in button_names:
            btn = QPushButton(b)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    font-size: 16px;
                    text-align: left;
                    padding: 12px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #666;
                }
                QPushButton:checked {
                    background-color: #777;
                    font-weight: bold;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, name=b: self.switch_page(name))
            self.buttons[b] = btn
            sidebar_layout.addWidget(btn)

        # Set Dashboard as default
        self.buttons["Dashboard"].setChecked(True)

        sidebar_layout.addStretch()

        # MAIN CONTENT AREA
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # TOP BAR
        top_bar_container = QFrame()
        top_bar_container.setStyleSheet("background-color: #E7E7DF;")
        top_bar_layout = QHBoxLayout(top_bar_container)
        top_bar_layout.setContentsMargins(30, 15, 30, 5)
        top_bar_layout.setSpacing(20)

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search anything...")
        search_bar.setFixedWidth(400)
        search_bar.setFixedHeight(40)
        search_bar.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border-radius: 20px;
                padding: 8px 20px;
                font-size: 16px;
            }
        """)
        top_bar_layout.addWidget(search_bar)
        top_bar_layout.addStretch()

        user_name = QLabel(username)  # dynamic username
        user_name.setStyleSheet("font-size: 17px; color: #333; font-weight: 600;")
        profile_icon = QLabel("👤")
        profile_icon.setStyleSheet("font-size: 20px;")
        notif_icon = QLabel("🔔")
        notif_icon.setStyleSheet("font-size: 20px;")
        mail_icon = QLabel("✉️")
        mail_icon.setStyleSheet("font-size: 26px;")

        top_bar_layout.addWidget(user_name)
        top_bar_layout.addSpacing(10)
        top_bar_layout.addWidget(profile_icon)
        top_bar_layout.addSpacing(12)
        top_bar_layout.addWidget(mail_icon)
        top_bar_layout.addSpacing(12)
        top_bar_layout.addWidget(notif_icon)

        content_layout.addWidget(top_bar_container, alignment=Qt.AlignTop)

        # MAIN BODY - Using QStackedWidget for different pages
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        # Create pages
        self.create_dashboard_page(username)
        self.create_my_classes_page()
        self.create_attendance_page()
        self.create_schedule_page()
        self.create_resources_page()
        self.create_settings_page()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_frame)

    def switch_page(self, page_name):
        # Uncheck all buttons
        for btn in self.buttons.values():
            btn.setChecked(False)
        # Check the selected one
        self.buttons[page_name].setChecked(True)
        # Switch to the corresponding page
        index = list(self.buttons.keys()).index(page_name)
        self.stacked_widget.setCurrentIndex(index)

    def create_dashboard_page(self, username):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 0, 35, 20)
        layout.setSpacing(20)

        dashboard_title = QLabel("Dashboard")
        dashboard_title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        layout.addWidget(dashboard_title, alignment=Qt.AlignLeft)

        # Welcome Card
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
        welcome_layout.setContentsMargins(30, 30, 30, 30)
        welcome_layout.setSpacing(15)
        welcome_layout.setAlignment(Qt.AlignCenter)

        welcome_title = QLabel(f"Welcome back, {username}!")  # dynamic welcome
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_title.setStyleSheet("font-size: 60px; font-weight: bold; color: #333;")
        welcome_sub = QLabel("Your students are waiting to learn")
        welcome_sub.setAlignment(Qt.AlignCenter)
        welcome_sub.setStyleSheet("font-size: 28px; color: #555;")

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_sub)
        layout.addWidget(welcome_card)

        # Bar Chart
        chart_frame = QFrame()
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(0)
        chart_frame.setMinimumHeight(250)
        chart_frame.setFixedWidth(550)

        figure = Figure()
        figure.patch.set_alpha(0)  # transparent background
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)
        ax.set_facecolor("none")

        labels = ["BSIT-1A", "BSIT-2A", "BSCIS-2A", "BSCIS-2B"]
        values = [28, 25, 30, 27]
        colors = ["#000000", "#C8B6FF", "#9A7FF0", "#836FFF"]

        bars = ax.bar(labels, values, color=colors)
        for bar in bars:
            x, y = bar.get_xy()
            width, height = bar.get_width(), bar.get_height()
            ax.add_patch(FancyBboxPatch((x, 0), width, height,
                                        boxstyle="round,pad=0.02",
                                        linewidth=0,
                                        facecolor=bar.get_facecolor()))
            bar.set_visible(False)

        ax.set_ylim(0, 35)
        ax.set_ylabel("Students", fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(axis='x', length=0, labelsize=12, colors="#333")
        ax.tick_params(axis='y', labelsize=11, colors="#555")

        for i, val in enumerate(values):
            ax.text(i, val + 0.5, str(val), ha='center', va='bottom', fontsize=11, fontweight='600', color="#222")

        figure.tight_layout(pad=2)
        chart_layout.addWidget(canvas, alignment=Qt.AlignRight)
        layout.addWidget(chart_frame, alignment=Qt.AlignRight)

        self.stacked_widget.addWidget(page)

    def create_my_classes_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 20, 35, 20)
        title = QLabel("My Classes")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        layout.addWidget(title)
        # Placeholder content
        placeholder = QLabel("Content for My Classes page goes here.")
        placeholder.setStyleSheet("font-size: 18px; color: #555;")
        layout.addWidget(placeholder)
        layout.addStretch()
        self.stacked_widget.addWidget(page)

    def create_attendance_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 20, 35, 20)
        title = QLabel("Attendance")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        layout.addWidget(title)
        # Placeholder content
        placeholder = QLabel("Content for Attendance page goes here.")
        placeholder.setStyleSheet("font-size: 18px; color: #555;")
        layout.addWidget(placeholder)
        layout.addStretch()
        self.stacked_widget.addWidget(page)

    def create_schedule_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 20, 35, 20)
        title = QLabel("Schedule")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        layout.addWidget(title)
        # Placeholder content
        placeholder = QLabel("Content for Schedule page goes here.")
        placeholder.setStyleSheet("font-size: 18px; color: #555;")
        layout.addWidget(placeholder)
        layout.addStretch()
        self.stacked_widget.addWidget(page)

    def create_resources_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 20, 35, 20)
        title = QLabel("Resources")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        layout.addWidget(title)
        # Placeholder content
        placeholder = QLabel("Content for Resources page goes here.")
        placeholder.setStyleSheet("font-size: 18px; color: #555;")
        layout.addWidget(placeholder)
        layout.addStretch()
        self.stacked_widget.addWidget(page)

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 20, 35, 20)
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        layout.addWidget(title)
        # Placeholder content
        placeholder = QLabel("Content for Settings page goes here.")
        placeholder.setStyleSheet("font-size: 18px; color: #555;")
        layout.addWidget(placeholder)
        layout.addStretch()
        self.stacked_widget.addWidget(page)


