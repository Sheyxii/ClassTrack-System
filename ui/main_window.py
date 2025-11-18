from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch

# === DASHBOARD ===
class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("ClassTrack - Main Window")
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
        dashboard_title.setContentsMargins(0, 20, 0, 10)
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
        welcome_layout.setContentsMargins(10, 10, 10, 10)
        welcome_layout.setSpacing(10)
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
        values = [0, 0, 0, 0]
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
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(35, 20, 35, 20)
        main_layout.setSpacing(20)

        # Header with title and add section button
        header_layout = QHBoxLayout()
        title = QLabel("My Classes")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        add_section_btn = QPushButton("+ Add Section")
        add_section_btn.setCursor(Qt.PointingHandCursor)
        add_section_btn.setFixedHeight(40)
        add_section_btn.setStyleSheet("""
            QPushButton {
                background-color: #836FFF;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #9A7FF0;
            }
        """)
        add_section_btn.clicked.connect(self.add_section_dialog)
        header_layout.addWidget(add_section_btn)
        main_layout.addLayout(header_layout)

        # Sections container with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll_content = QWidget()
        self.sections_layout = QVBoxLayout(scroll_content)
        self.sections_layout.setSpacing(20)
        self.sections_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Store sections data (per user)
        self.sections_data = {}  # {section_name: [list of students]}
        
        # Show empty state if no sections
        self.show_empty_state()

        self.stacked_widget.addWidget(page)

    def show_empty_state(self):
        if not self.sections_data:
            empty_card = QFrame()
            empty_card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 12px;
                    border: 2px dashed #C8B6FF;
                }
            """)
            empty_layout = QVBoxLayout(empty_card)
            empty_layout.setContentsMargins(40, 60, 40, 60)
            
            icon = QLabel("📚")
            icon.setAlignment(Qt.AlignCenter)
            icon.setStyleSheet("font-size: 64px;")
            
            message = QLabel("No classes yet")
            message.setAlignment(Qt.AlignCenter)
            message.setStyleSheet("font-size: 24px; font-weight: 600; color: #333;")
            
            submessage = QLabel("Click 'Add Section' to create your first class")
            submessage.setAlignment(Qt.AlignCenter)
            submessage.setStyleSheet("font-size: 16px; color: #777;")
            
            empty_layout.addWidget(icon)
            empty_layout.addWidget(message)
            empty_layout.addWidget(submessage)
            
            self.sections_layout.addWidget(empty_card)

    def clear_sections_layout(self):
        while self.sections_layout.count():
            item = self.sections_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def refresh_sections_display(self):
        self.clear_sections_layout()
        
        if not self.sections_data:
            self.show_empty_state()
            return
        
        for section_name, students in self.sections_data.items():
            self.create_section_card(section_name, students)

    def create_section_card(self, section_name, students):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)

        # Section header
        header_layout = QHBoxLayout()
        
        section_title = QLabel(section_name)
        section_title.setStyleSheet("font-size: 22px; font-weight: 700; color: #222;")
        header_layout.addWidget(section_title)
        
        student_count = QLabel(f"{len(students)} students")
        student_count.setStyleSheet("font-size: 16px; color: #777; margin-left: 10px;")
        header_layout.addWidget(student_count)
        
        header_layout.addStretch()
        
        # Action buttons
        add_student_btn = QPushButton("+ Add Student")
        add_student_btn.setCursor(Qt.PointingHandCursor)
        add_student_btn.setFixedHeight(35)
        add_student_btn.setStyleSheet("""
            QPushButton {
                background-color: #E6EFFA;
                color: #222;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #C8B6FF;
            }
        """)
        add_student_btn.clicked.connect(lambda: self.add_student_dialog(section_name))
        header_layout.addWidget(add_student_btn)
        
        delete_section_btn = QPushButton("🗑")
        delete_section_btn.setCursor(Qt.PointingHandCursor)
        delete_section_btn.setFixedSize(35, 35)
        delete_section_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFE6E6;
                color: #D32F2F;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #FFCCCC;
            }
        """)
        delete_section_btn.clicked.connect(lambda: self.delete_section(section_name))
        header_layout.addWidget(delete_section_btn)
        
        card_layout.addLayout(header_layout)
        
        # Students table
        if students:
            table = QTableWidget()
            table.setRowCount(len(students))
            table.setColumnCount(9)
            table.setHorizontalHeaderLabels([
                "Student ID", "First Name", "Last Name", "Age", 
                "Email", "Phone", "Birthday", "Grade", "Actions"
            ])
            table.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #F5F5F5;
                    color: #333;
                    font-weight: 600;
                    padding: 8px;
                    border: none;
                    font-size: 13px;
                }
            """)
            table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #E0E0E0;
                    border-radius: 6px;
                    background-color: white;
                    gridline-color: #F0F0F0;
                }
                QTableWidget::item {
                    padding: 8px;
                    color: #333;
                }
                QTableWidget::item:selected {
                    background-color: #E6EFFA;
                    color: #222;
                }
            """)
            table.verticalHeader().setVisible(False)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.horizontalHeader().setStretchLastSection(False)
            
            # Set column widths
            for i in range(8):
                table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
            table.setColumnWidth(8, 120)
            
            for row, student in enumerate(students):
                table.setItem(row, 0, QTableWidgetItem(student.get('student_id', '')))
                table.setItem(row, 1, QTableWidgetItem(student.get('first_name', '')))
                table.setItem(row, 2, QTableWidgetItem(student.get('last_name', '')))
                table.setItem(row, 3, QTableWidgetItem(str(student.get('age', ''))))
                table.setItem(row, 4, QTableWidgetItem(student.get('email', '')))
                table.setItem(row, 5, QTableWidgetItem(student.get('phone', '')))
                table.setItem(row, 6, QTableWidgetItem(student.get('birthday', '')))
                table.setItem(row, 7, QTableWidgetItem(str(student.get('grade', ''))))
                
                # Action buttons widget
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 0, 5, 0)
                actions_layout.setSpacing(5)
                
                edit_btn = QPushButton("✏️")
                edit_btn.setCursor(Qt.PointingHandCursor)
                edit_btn.setFixedSize(30, 30)
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E6EFFA;
                        border-radius: 4px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #C8B6FF;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, s=section_name, idx=row: self.edit_student_dialog(s, idx))
                
                delete_btn = QPushButton("🗑")
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setFixedSize(30, 30)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFE6E6;
                        color: #D32F2F;
                        border-radius: 4px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #FFCCCC;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, s=section_name, idx=row: self.delete_student(s, idx))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                table.setCellWidget(row, 8, actions_widget)
                table.setRowHeight(row, 45)
            
            card_layout.addWidget(table)
        else:
            no_students = QLabel("No students in this section yet")
            no_students.setStyleSheet("font-size: 15px; color: #999; padding: 20px;")
            no_students.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(no_students)
        
        self.sections_layout.addWidget(card)

    def add_section_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Section")
        dialog.setFixedSize(400, 200)
        dialog.setStyleSheet("background-color: #E7E7DF;")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        title = QLabel("Create New Section")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #222;")
        layout.addWidget(title)
        
        section_input = QLineEdit()
        section_input.setPlaceholderText("Enter section name (e.g., BSIT-1A)")
        section_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 6px;
                border: 2px solid #C8B6FF;
                font-size: 15px;
                background-color: white;
            }
        """)
        layout.addWidget(section_input)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        create_btn = QPushButton("Create")
        create_btn.setCursor(Qt.PointingHandCursor)
        create_btn.setFixedHeight(40)
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #836FFF;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #9A7FF0;
            }
        """)
        
        def create_section():
            section_name = section_input.text().strip()
            if section_name:
                if section_name in self.sections_data:
                    QMessageBox.warning(dialog, "Duplicate Section", "This section already exists!")
                    return
                self.sections_data[section_name] = []
                self.refresh_sections_display()
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Invalid Input", "Please enter a section name!")
        
        create_btn.clicked.connect(create_section)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(create_btn)
        layout.addLayout(buttons_layout)
        
        dialog.exec_()

    def delete_section(self, section_name):
        reply = QMessageBox.question(
            self, 'Delete Section',
            f"Are you sure you want to delete section '{section_name}'?\nThis will also delete all students in this section.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.sections_data[section_name]
            self.refresh_sections_display()

    def add_student_dialog(self, section_name):
        self.show_student_dialog(section_name, None, "Add Student")

    def edit_student_dialog(self, section_name, student_index):
        self.show_student_dialog(section_name, student_index, "Edit Student")

    def show_student_dialog(self, section_name, student_index, title):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(500, 650)
        dialog.setStyleSheet("background-color: #E7E7DF;")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(12)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #222;")
        layout.addWidget(title_label)
        
        # Get existing student data if editing
        student_data = {}
        if student_index is not None:
            student_data = self.sections_data[section_name][student_index]
        
        # Input fields
        fields = {}
        field_configs = [
            ("student_id", "Student ID", "e.g., 2024001"),
            ("first_name", "First Name", "Enter first name"),
            ("last_name", "Last Name", "Enter last name"),
            ("age", "Age", "e.g., 20"),
            ("email", "Email", "student@example.com"),
            ("phone", "Phone Number", "e.g., 09123456789"),
            ("birthday", "Birthday", "MM/DD/YYYY"),
            ("address", "Address", "Enter complete address"),
            ("grade", "Grade", "e.g., 1.5"),
        ]
        
        for field_key, label_text, placeholder in field_configs:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333;")
            layout.addWidget(label)
            
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            field.setText(str(student_data.get(field_key, '')))
            field.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    border-radius: 6px;
                    border: 2px solid #C8B6FF;
                    font-size: 14px;
                    background-color: white;
                }
            """)
            layout.addWidget(field)
            fields[field_key] = field
        
        scroll.setWidget(scroll_content)
        
        main_layout = QVBoxLayout(dialog)
        main_layout.addWidget(scroll)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #836FFF;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #9A7FF0;
            }
        """)
        
        def save_student():
            # Collect data
            new_student = {}
            for key, field in fields.items():
                value = field.text().strip()
                if not value and key != 'grade':  # grade can be empty
                    QMessageBox.warning(dialog, "Missing Information", f"Please fill in {key.replace('_', ' ').title()}!")
                    return
                new_student[key] = value
            
            # Check for duplicate names in the section
            full_name = f"{new_student['first_name']} {new_student['last_name']}"
            for idx, student in enumerate(self.sections_data[section_name]):
                if student_index is not None and idx == student_index:
                    continue  # Skip the current student when editing
                existing_name = f"{student['first_name']} {student['last_name']}"
                if full_name.lower() == existing_name.lower():
                    QMessageBox.warning(dialog, "Duplicate Student", 
                                      f"A student with the name '{full_name}' already exists in this section!")
                    return
            
            # Save or update
            if student_index is not None:
                self.sections_data[section_name][student_index] = new_student
            else:
                self.sections_data[section_name].append(new_student)
            
            self.refresh_sections_display()
            dialog.accept()
        
        save_btn.clicked.connect(save_student)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        main_layout.addLayout(buttons_layout)
        
        dialog.exec_()

    def delete_student(self, section_name, student_index):
        student = self.sections_data[section_name][student_index]
        student_name = f"{student['first_name']} {student['last_name']}"
        
        reply = QMessageBox.question(
            self, 'Delete Student',
            f"Are you sure you want to delete '{student_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.sections_data[section_name].pop(student_index)
            self.refresh_sections_display()

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


