from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from .main.dashboard_page import DashboardPage
from .main.my_classes_page import MyClassesPage
from .main.class_detail_page import ClassDetailPage
from .main.attendance_page import AttendancePage
from .main.schedule_page import SchedulePage
from .main.resources_page import ResourcesPage
from .main.archive_page import ArchivePage


class MainWindow(QMainWindow):
    def __init__(self, username, user_id=1):
        super().__init__()
        self.username = username
        self.user_id = user_id
        self.setWindowTitle("ClassTrack - Main Window")
        self.setWindowIcon(QIcon("image/system.png"))
        self.setGeometry(100, 100, 1250, 750)
        self.setStyleSheet("background-color: #E7E7DF;")

        # === Main container ===
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(main_widget)

        # SIDEBAR
        sidebar = self.create_sidebar()

        # MAIN CONTENT AREA
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # TOP BAR
        top_bar_container = self.create_top_bar()
        content_layout.addWidget(top_bar_container, alignment=Qt.AlignTop)

        # MAIN BODY - Using QStackedWidget for different pages
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        # Create pages
        self.dashboard_page = DashboardPage(username, self.user_id)
        self.my_classes_page = MyClassesPage(self.user_id, self.dashboard_page)
        self.my_classes_page.main_window = self  # Set reference to main window
        self.attendance_page = AttendancePage()
        self.schedule_page = SchedulePage(self.user_id)
        self.resources_page = ResourcesPage(self.user_id)
        self.resources_page.main_window = self  # Set reference to main window
        self.archive_page = ArchivePage(self.user_id, self.my_classes_page)
        
        # Dictionary to store class detail pages
        self.class_pages = {}

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.my_classes_page)
        self.stacked_widget.addWidget(self.attendance_page)
        self.stacked_widget.addWidget(self.schedule_page)
        self.stacked_widget.addWidget(self.resources_page)
        self.stacked_widget.addWidget(self.archive_page)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_frame)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #555; color: white;")
        sidebar.setFixedWidth(280)
        
        # Scroll area for sidebar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        sidebar_content = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_content)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # User profile section at top
        profile_widget = QWidget()
        profile_widget.setStyleSheet("background-color: #2D3E50; padding: 0px;")
        profile_layout = QVBoxLayout(profile_widget)
        profile_layout.setContentsMargins(20, 30, 20, 30)
        profile_layout.setSpacing(15)
        
        # Profile picture (circular)
        profile_pic_container = QWidget()
        profile_pic_container.setStyleSheet("background-color: transparent;")
        profile_pic_layout = QHBoxLayout(profile_pic_container)
        profile_pic_layout.setContentsMargins(0, 0, 0, 0)
        profile_pic_layout.setAlignment(Qt.AlignCenter)
        
        profile_icon_frame = QFrame()
        profile_icon_frame.setFixedSize(100, 80)
        profile_icon_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 40px;
                border: none;
            }
        """)
        
        profile_icon_layout = QHBoxLayout(profile_icon_frame)
        profile_icon_layout.setContentsMargins(0, 0, 0, 0)
        profile_icon_layout.setAlignment(Qt.AlignCenter)
        
        profile_icon = QLabel()
        profile_icon.setPixmap(QIcon("image/user.png").pixmap(80, 80))
        profile_icon.setAlignment(Qt.AlignCenter)
        profile_icon_layout.addWidget(profile_icon)
        
        profile_pic_layout.addWidget(profile_icon_frame)
        profile_layout.addWidget(profile_pic_container)
        
        # Username
        username_label = QLabel(self.username.upper())
        username_label.setStyleSheet("""
            font-size: 18px;
            color: white;
            font-weight: bold;
            background-color: transparent;
        """)
        username_label.setAlignment(Qt.AlignCenter)
        profile_layout.addWidget(username_label)
        
        # ClassTrack label
        classtrack_label = QLabel("ClassTrack")
        classtrack_label.setStyleSheet("""
            font-size: 25px;
            color: white;
            font-weight: 600;
            background-color: transparent;
        """)
        classtrack_label.setAlignment(Qt.AlignCenter)
        profile_layout.addWidget(classtrack_label)
        
        sidebar_layout.addWidget(profile_widget)
        
        # Navigation buttons container
        nav_container = QWidget()
        nav_container.setStyleSheet("background-color: transparent;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(20, 20, 20, 30)
        nav_layout.setSpacing(10)

        self.buttons = {}
        
        # Dashboard button
        dashboard_btn = QPushButton("  Dashboard")
        dashboard_btn.setIcon(QIcon("image/dashboard.png"))
        dashboard_btn.setIconSize(QSize(20, 20))
        dashboard_btn.setCursor(Qt.PointingHandCursor)
        dashboard_btn.setStyleSheet(self.get_main_button_style())
        dashboard_btn.setCheckable(True)
        dashboard_btn.clicked.connect(lambda: self.switch_page("Dashboard"))
        self.buttons["Dashboard"] = dashboard_btn
        nav_layout.addWidget(dashboard_btn)
        
        # My Classes button with submenu
        my_classes_btn = QPushButton("  My Classes")
        my_classes_btn.setIcon(QIcon("image/classes.png"))
        my_classes_btn.setIconSize(QSize(20, 20))
        my_classes_btn.setCursor(Qt.PointingHandCursor)
        my_classes_btn.setStyleSheet(self.get_main_button_style())
        my_classes_btn.setCheckable(True)
        my_classes_btn.clicked.connect(lambda: self.toggle_my_classes_submenu())
        self.buttons["My Classes"] = my_classes_btn
        nav_layout.addWidget(my_classes_btn)
        
        # My Classes submenu container
        self.my_classes_submenu = QWidget()
        self.my_classes_submenu.setStyleSheet("background-color: transparent;")
        self.submenu_layout = QVBoxLayout(self.my_classes_submenu)
        self.submenu_layout.setContentsMargins(20, 5, 0, 5)
        self.submenu_layout.setSpacing(5)
        
        self.submenu_buttons = {}
        self.load_class_submenus()
        
        self.my_classes_submenu.setVisible(False)
        nav_layout.addWidget(self.my_classes_submenu)
        
        # Schedule button
        schedule_btn = QPushButton("  Schedule")
        schedule_btn.setIcon(QIcon("image/schedule.png"))
        schedule_btn.setIconSize(QSize(20, 20))
        schedule_btn.setCursor(Qt.PointingHandCursor)
        schedule_btn.setStyleSheet(self.get_main_button_style())
        schedule_btn.setCheckable(True)
        schedule_btn.clicked.connect(lambda: self.switch_page("Schedule"))
        self.buttons["Schedule"] = schedule_btn
        nav_layout.addWidget(schedule_btn)
        
        # Resources button
        resources_btn = QPushButton("  Resources")
        resources_btn.setIcon(QIcon("image/resources.png"))
        resources_btn.setIconSize(QSize(20, 20))
        resources_btn.setCursor(Qt.PointingHandCursor)
        resources_btn.setStyleSheet(self.get_main_button_style())
        resources_btn.setCheckable(True)
        resources_btn.clicked.connect(lambda: self.switch_page("Resources"))
        self.buttons["Resources"] = resources_btn
        nav_layout.addWidget(resources_btn)
        
        # Archive button
        archive_btn = QPushButton("  Archive")
        archive_btn.setIcon(QIcon("image/archive.png"))
        archive_btn.setIconSize(QSize(20, 20))
        archive_btn.setCursor(Qt.PointingHandCursor)
        archive_btn.setStyleSheet(self.get_main_button_style())
        archive_btn.setCheckable(True)
        archive_btn.clicked.connect(lambda: self.switch_page("Archive"))
        self.buttons["Archive"] = archive_btn
        nav_layout.addWidget(archive_btn)

        # Set Dashboard as default
        self.buttons["Dashboard"].setChecked(True)

        nav_layout.addStretch()
        
        # Logout button at bottom
        logout_btn = QPushButton("  LOGOUT")
        logout_btn.setIcon(QIcon("image/logout.png"))
        logout_btn.setIconSize(QSize(20, 20))
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: darkgray;
                color: black;
                font-size: 16px;
                text-align: center;
                padding: 12px;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: gray;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        nav_layout.addWidget(logout_btn)
        
        sidebar_layout.addWidget(nav_container)
        scroll.setWidget(sidebar_content)
        
        sidebar_main_layout = QVBoxLayout(sidebar)
        sidebar_main_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_main_layout.addWidget(scroll)
        
        return sidebar
    
    def get_main_button_style(self):
        return """
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
        """
    
    def load_class_submenus(self):
        """Load all classes as submenu items under My Classes"""
        # Clear existing submenu buttons
        for btn in self.submenu_buttons.values():
            btn.deleteLater()
        self.submenu_buttons.clear()
        
        # Get all sections from database
        from utils.database import DatabaseConnection
        import random
        db = DatabaseConnection()
        sections = db.get_sections(self.user_id, include_archived=False)
        sections = list(sections)
        sections.reverse()
        
        for index, section in enumerate(sections):
            # Generate same color as the card
            random.seed(index * 123456)
            r = random.randint(180, 255)
            g = random.randint(180, 255)
            b = random.randint(180, 255)
            card_color = f'#{r:02x}{g:02x}{b:02x}'
            
            submenu_btn = QPushButton(section['section_name'])
            submenu_btn.setCursor(Qt.PointingHandCursor)
            submenu_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #CCC;
                    font-size: 14px;
                    text-align: left;
                    padding: 8px 12px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #666;
                    color: white;
                }
                QPushButton:checked {
                    background-color: #777;
                    color: white;
                    font-weight: bold;
                }
            """)
            submenu_btn.setCheckable(True)
            submenu_btn.clicked.connect(lambda checked, s=section, c=card_color: self.open_class_page(s, c))
            self.submenu_buttons[section['section_id']] = submenu_btn
            self.submenu_layout.addWidget(submenu_btn)
    
    def toggle_my_classes_submenu(self):
        """Toggle the My Classes submenu visibility"""
        is_visible = self.my_classes_submenu.isVisible()
        self.my_classes_submenu.setVisible(not is_visible)
        
        if not is_visible:
            # Reload submenus to show latest classes
            self.load_class_submenus()
            
            # Uncheck all main buttons except My Classes
            for name, btn in self.buttons.items():
                if name != "My Classes":
                    btn.setChecked(False)
            self.buttons["My Classes"].setChecked(True)
            
            # Switch to My Classes overview page
            self.stacked_widget.setCurrentWidget(self.my_classes_page)
    
    def create_top_bar(self):
        top_bar_container = QFrame()
        top_bar_container.setStyleSheet("background-color: #E7E7DF;")
        top_bar_layout = QHBoxLayout(top_bar_container)
        top_bar_layout.setContentsMargins(30, 15, 30, 5)
        top_bar_layout.setSpacing(20)

        top_bar_layout.addStretch()

        return top_bar_container
    
    def show_profile_menu(self, event, profile_card):
        """Show profile dropdown menu"""
        dropdown_menu = QMenu(self)
        dropdown_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #DDD;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 10px 30px;
                font-size: 14px;
                color: #333;
            }
            QMenu::item:selected {
                background-color: #E6EFFA;
                border-radius: 6px;
            }
        """)
        
        view_profile_action = QAction("View Profile", self)
        change_password_action = QAction("Change Password", self)
        logout_action = QAction("Logout", self)
        
        view_profile_action.triggered.connect(self.view_profile)
        change_password_action.triggered.connect(self.change_password)
        logout_action.triggered.connect(self.logout)
        
        dropdown_menu.addAction(view_profile_action)
        dropdown_menu.addAction(change_password_action)
        dropdown_menu.addSeparator()
        dropdown_menu.addAction(logout_action)
        
        dropdown_menu.exec_(profile_card.mapToGlobal(profile_card.rect().bottomLeft()))
    
    def view_profile(self):
        QMessageBox.information(self, "Profile", f"Viewing profile for {self.username}")
    
    def change_password(self):
        """Change user password"""
        QMessageBox.information(self, "Change Password", "Change password functionality")
    
    def logout(self):
        #Logout user
        reply = QMessageBox.question(self, 'Logout', 
                                    'Are you sure you want to logout?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            # You can add code here to show login window again

    def switch_page(self, page_name):
        # Uncheck all main buttons
        for btn in self.buttons.values():
            btn.setChecked(False)
        
        # Check the selected one if it exists in buttons
        if page_name in self.buttons:
            self.buttons[page_name].setChecked(True)
        
        # Map page names to indices
        page_map = {
            "Dashboard": 0,
            "My Classes": 1,
            "Schedule": 3,
            "Resources": 4,
            "Archive": 5
        }
        
        if page_name in page_map:
            self.stacked_widget.setCurrentIndex(page_map[page_name])
            
            # Refresh pages when switching to them
            if page_name == "Archive":
                self.archive_page.load_archived_sections()
            elif page_name == "My Classes":
                self.my_classes_page.load_sections()
            elif page_name == "Resources":
                self.resources_page.refresh_subject_filter()

    def open_class_page(self, section, card_color=None):
        """Open or create a class detail page for the given section"""
        section_id = section['section_id']
        
        # Check if page already exists
        if section_id in self.class_pages:
            class_page = self.class_pages[section_id]
            # Update section data in case it changed
            class_page.section = section
            # Update border color if provided
            if card_color:
                class_page.update_title_border(card_color)
        else:
            # Create new class detail page
            class_page = ClassDetailPage(section, self.user_id, card_color)
            class_page.main_window = self
            self.class_pages[section_id] = class_page
            
            # Connect grade update signal to dashboard refresh
            class_page.grades_updated.connect(self.dashboard_page.refresh_outstanding_students)
            self.stacked_widget.addWidget(class_page)
        
        # Switch to the class page
        self.stacked_widget.setCurrentWidget(class_page)
        
        # Update button states
        for btn in self.buttons.values():
            btn.setChecked(False)
        self.buttons["My Classes"].setChecked(True)
        
        # Update submenu button states
        for sid, btn in self.submenu_buttons.items():
            btn.setChecked(sid == section_id)
    
    def logout(self):
        """Logout and return to login window"""
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from .auth.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.showMaximized()
            self.close()
