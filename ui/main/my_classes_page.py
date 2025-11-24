from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
sys.path.append('..')
from utils.database import DatabaseConnection


class MyClassesPage(QWidget):
    def __init__(self, user_id=1, dashboard_page=None):
        super().__init__()
        self.user_id = user_id
        self.dashboard_page = dashboard_page
        self.db = DatabaseConnection()
        self.init_ui()
        self.load_sections()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(35, 20, 35, 20)
        main_layout.setSpacing(25)

        # Header with title
        title = QLabel("My Classes")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        main_layout.addWidget(title)

        # Sections container with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll_content = QWidget()
        self.sections_layout = QGridLayout(scroll_content)
        self.sections_layout.setSpacing(20)
        self.sections_layout.setContentsMargins(0, 0, 0, 0)
        self.sections_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Action buttons container (bottom right)
        buttons_container = QFrame()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        # ADD SECTION button
        add_section_btn = QPushButton("ADD SECTION")
        add_section_btn.setCursor(Qt.PointingHandCursor)
        add_section_btn.setFixedSize(200, 50)
        add_section_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #222;
                border: 2px solid #DDD;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
                border-color: #BBB;
            }
        """)
        add_section_btn.clicked.connect(self.add_section_dialog)

        # ARCHIVE button
        archive_btn = QPushButton("ARCHIVE")
        archive_btn.setCursor(Qt.PointingHandCursor)
        archive_btn.setFixedSize(200, 50)
        archive_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #222;
                border: 2px solid #DDD;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
                border-color: #BBB;
            }
        """)
        archive_btn.clicked.connect(self.show_archive_dialog)

        buttons_layout.addWidget(add_section_btn)
        buttons_layout.addWidget(archive_btn)
        buttons_layout.addStretch()

        # Position buttons at bottom right
        main_layout.addWidget(buttons_container, alignment=Qt.AlignRight | Qt.AlignBottom)

    def load_sections(self):
        # load ang sections from database
        self.clear_sections_layout()
        sections = self.db.get_sections(self.user_id, include_archived=False)
        
        # I-convert to list at i-reverse para ipakita ang oldest first (queue - FIFO)
        sections = list(sections)
        sections.reverse()
        
        # I-set ang column stretches para sa equal distribution
        for i in range(3):
            self.sections_layout.setColumnStretch(i, 1)
        
        row = 0
        col = 0
        
        for section in sections:
            card = self.create_section_card(section)
            self.sections_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 3:  # 3 cards per row
                col = 0
                row += 1
        
        # I-refresh ang dashboard chart kung available
        if self.dashboard_page:
            self.dashboard_page.refresh_chart()

    def clear_sections_layout(self):
        while self.sections_layout.count():
            item = self.sections_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def create_section_card(self, section):
        """Gumawa ng section card na katulad ng design sa image"""
        card = QFrame()
        card.setMinimumHeight(220)
        card.setMinimumWidth(300)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
            }
        """)
        card.setCursor(Qt.PointingHandCursor)
        
        # I-set ang size policy para mag-expand proportionally (3 cards per row)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignCenter)

        # Section title
        section_title = QLabel(section['section_name'])
        section_title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222; outline: none;")
        section_title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(section_title)
        
        card_layout.addStretch()
        
        # Delete button at bottom right
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("image/bin.png"))
        delete_btn.setIconSize(QSize(20, 20))
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedSize(35, 35)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 17px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #FFE6E6;
            }
        """)
        delete_btn.clicked.connect(lambda: self.archive_section(section))
        
        delete_container = QWidget()
        delete_container.setStyleSheet("background-color: transparent;")
        delete_layout = QHBoxLayout(delete_container)
        delete_layout.setContentsMargins(0, 0, 0, 0)
        delete_layout.addStretch()
        delete_layout.addWidget(delete_btn)
        
        card_layout.addWidget(delete_container)
        
        # Make card clickable to view students, pero i-filter ang clicks sa delete button
        def card_click_handler(event):
            # I-check kung nag-click sa delete button area
            if not delete_btn.geometry().contains(delete_container.mapFrom(card, event.pos())):
                self.view_section_details(section)
        
        card.mousePressEvent = card_click_handler
        
        return card

    def view_section_details(self, section):
        """Buksan ang dialog na nagpapakita ng section details at students"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{section['section_name']} - Details")
        dialog.resize(1200, 700)
        dialog.setStyleSheet("background-color: #E7E7DF;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel(section['section_name'])
        title.setStyleSheet("font-size: 26px; font-weight: 700; color: #222;")
        header_layout.addWidget(title)
        
        # I-save ang student_count label para ma-update
        student_count_label = QLabel()
        student_count_label.setStyleSheet("font-size: 18px; color: #777; margin-left: 10px;")
        header_layout.addWidget(student_count_label)
        
        header_layout.addStretch()
        
        # Add Student button
        add_student_btn = QPushButton("+ Add Student")
        add_student_btn.setCursor(Qt.PointingHandCursor)
        add_student_btn.setFixedHeight(40)
        add_student_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #222;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #757575;
                color: white;
            }
        """)
        header_layout.addWidget(add_student_btn)
        
        # View Archive button
        view_archive_btn = QPushButton(" View Archive")
        view_archive_btn.setIcon(QIcon("image/archive.png"))
        view_archive_btn.setIconSize(QSize(20, 20))
        view_archive_btn.setCursor(Qt.PointingHandCursor)
        view_archive_btn.setFixedHeight(40)
        view_archive_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #222;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #757575;
                color: white;
            }
        """)
        view_archive_btn.clicked.connect(lambda: self.show_student_archive_dialog(section, refresh_table))
        header_layout.addWidget(view_archive_btn)
        
        layout.addLayout(header_layout)
        
        # Container para sa table (para madaling i-replace)
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(table_container)
        
        # Function para i-refresh ang table
        def refresh_table():
            # I-clear ang current table
            while table_layout.count():
                item = table_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # I-load ang updated students
            students = self.db.get_students(section['section_id'], include_archived=False)
            student_count_label.setText(f"{len(students)} students")
            
            if students:
                table = self.create_students_table_with_refresh(section, students, refresh_table)
                table_layout.addWidget(table)
            else:
                no_students = QLabel("No students in this section yet")
                no_students.setStyleSheet("font-size: 16px; color: #999; padding: 40px;")
                no_students.setAlignment(Qt.AlignCenter)
                table_layout.addWidget(no_students)
        
        # I-connect ang add student button sa refresh function
        add_student_btn.clicked.connect(lambda: self.add_student_dialog_with_refresh(section, refresh_table))
        
        # Initial load ng table
        refresh_table()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedHeight(40)
        close_btn.setFixedWidth(120)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: ;
                color: #333;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
        dialog.exec_()

    def create_students_table(self, section, students):
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
                padding: 10px;
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
                padding: 10px;
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
        
        # Set column widths - i-adjust para sakto lang makita lahat
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Student ID
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # First Name
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Last Name
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Age
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # Email
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Phone
        table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Birthday
        table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Grade
        table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)  # Actions
        table.setColumnWidth(8, 100)
        
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
            actions_widget = self.create_action_buttons(section, student)
            table.setCellWidget(row, 8, actions_widget)
            table.setRowHeight(row, 50)
        
        return table

    def create_students_table_with_refresh(self, section, students, refresh_callback):
        """Gumawa ng students table with refresh capability"""
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
                padding: 10px;
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
                padding: 10px;
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
        
        # Set column widths - i-adjust para sakto lang makita lahat
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Student ID
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # First Name
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Last Name
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Age
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # Email
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Phone
        table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Birthday
        table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Grade
        table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)  # Actions
        table.setColumnWidth(8, 100)
        
        for row, student in enumerate(students):
            table.setItem(row, 0, QTableWidgetItem(student.get('student_id', '')))
            table.setItem(row, 1, QTableWidgetItem(student.get('first_name', '')))
            table.setItem(row, 2, QTableWidgetItem(student.get('last_name', '')))
            table.setItem(row, 3, QTableWidgetItem(str(student.get('age', ''))))
            table.setItem(row, 4, QTableWidgetItem(student.get('email', '')))
            table.setItem(row, 5, QTableWidgetItem(student.get('phone', '')))
            table.setItem(row, 6, QTableWidgetItem(student.get('birthday', '')))
            table.setItem(row, 7, QTableWidgetItem(str(student.get('grade', ''))))
            
            # Action buttons widget with refresh callback
            actions_widget = self.create_action_buttons_with_refresh(section, student, refresh_callback)
            table.setCellWidget(row, 8, actions_widget)
            table.setRowHeight(row, 50)
        
        return table

    def create_action_buttons_with_refresh(self, section, student, refresh_callback):
        """Gumawa ng action buttons with refresh callback"""
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 0, 5, 0)
        actions_layout.setSpacing(5)
        
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon("image/edit.png"))
        edit_btn.setIconSize(QSize(18, 18))
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setFixedSize(35, 35)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #E6EFFA;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #C8B6FF;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_student_dialog_with_refresh(section, student, refresh_callback))
        
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("image/bin.png"))
        delete_btn.setIconSize(QSize(18, 18))
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedSize(35, 35)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFE6E6;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #FFCCCC;
            }
        """)
        delete_btn.clicked.connect(lambda: self.archive_student_with_refresh(student, refresh_callback))
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        actions_layout.addStretch()
        
        return actions_widget

    def create_action_buttons(self, section, student):
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 0, 5, 0)
        actions_layout.setSpacing(5)
        
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon("image/edit.png"))
        edit_btn.setIconSize(QSize(18, 18))
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setFixedSize(35, 35)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #E6EFFA;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #C8B6FF;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_student_dialog(section, student))
        
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("image/bin.png"))
        delete_btn.setIconSize(QSize(18, 18))
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedSize(35, 35)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFE6E6;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #FFCCCC;
            }
        """)
        delete_btn.clicked.connect(lambda: self.archive_student(student))
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        actions_layout.addStretch()
        
        return actions_widget

    def add_section_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Section")
        dialog.setFixedSize(450, 220)
        dialog.setStyleSheet("background-color: #E7E7DF;")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Create New Section")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #222;")
        layout.addWidget(title)
        
        section_input = QLineEdit()
        section_input.setPlaceholderText("Enter section name (e.g., BSCS-1A)")
        section_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border-radius: 8px;
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
        cancel_btn.setFixedHeight(45)
        cancel_btn.setFixedWidth(120)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border-radius: 8px;
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
        create_btn.setFixedHeight(45)
        create_btn.setFixedWidth(120)
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #836FFF;
                color: white;
                border-radius: 8px;
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
                success, message, _ = self.db.add_section(section_name, self.user_id)
                if success:
                    self.load_sections()
                    dialog.accept()
                    QMessageBox.information(dialog, "Success", message)
                else:
                    QMessageBox.warning(dialog, "Error", message)
            else:
                QMessageBox.warning(dialog, "Invalid Input", "Please enter a section name!")
        
        create_btn.clicked.connect(create_section)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(create_btn)
        layout.addLayout(buttons_layout)
        
        dialog.exec_()

    def archive_section(self, section):
        """I-archive ang section instead na i-delete"""
        reply = QMessageBox.question(
            self, 'Archive Section',
            f"Are you sure you want to archive section '{section['section_name']}'?\nYou can restore it later from the Archive.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.db.archive_section(section['section_id'])
            if success:
                self.load_sections()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)

    def add_student_dialog(self, section):
        self.show_student_dialog(section, None, "Add Student")
    
    def add_student_quick(self, section):
        """Quick add student from section card"""
        self.show_student_dialog(section, None, "Add Student")

    def edit_student_dialog(self, section, student):
        self.show_student_dialog(section, student, "Edit Student")
    
    def add_student_dialog_with_refresh(self, section, refresh_callback):
        """Add student dialog with refresh callback"""
        self.show_student_dialog_with_refresh(section, None, "Add Student", refresh_callback)
    
    def edit_student_dialog_with_refresh(self, section, student, refresh_callback):
        """Edit student dialog with refresh callback"""
        self.show_student_dialog_with_refresh(section, student, "Edit Student", refresh_callback)

    def show_student_dialog(self, section, student, title):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(550, 700)
        dialog.setStyleSheet("background-color: #E7E7DF;")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 22px; font-weight: 700; color: #222;")
        layout.addWidget(title_label)
        
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
            if student:
                field.setText(str(student.get(field_key, '')))
            field.setStyleSheet("""
                QLineEdit {
                    padding: 12px;
                    border-radius: 8px;
                    border: 2px solid #C8B6FF;
                    font-size: 14px;
                    background-color: white;
                }
            """)
            layout.addWidget(field)
            fields[field_key] = field
            
            # Disable student_id field when editing
            if student and field_key == "student_id":
                field.setEnabled(False)
        
        scroll.setWidget(scroll_content)
        
        main_layout = QVBoxLayout(dialog)
        main_layout.addWidget(scroll)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(45)
        cancel_btn.setFixedWidth(120)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border-radius: 8px;
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
        save_btn.setFixedHeight(45)
        save_btn.setFixedWidth(120)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #836FFF;
                color: white;
                border-radius: 8px;
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
                if not value and key in ['student_id', 'first_name', 'last_name']:
                    QMessageBox.warning(dialog, "Missing Information", 
                                      f"Please fill in {key.replace('_', ' ').title()}!")
                    return
                new_student[key] = value
            
            new_student['section_id'] = section['section_id']
            
            # Save or update
            if student:
                # Update existing student
                success, message = self.db.update_student(student['student_id'], new_student)
            else:
                # Add new student
                success, message = self.db.add_student(new_student)
            
            if success:
                QMessageBox.information(dialog, "Success", message)
                dialog.accept()
                # Refresh the section details view if it's open
                self.load_sections()
            else:
                QMessageBox.warning(dialog, "Error", message)
        
        save_btn.clicked.connect(save_student)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        main_layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def show_student_dialog_with_refresh(self, section, student, title, refresh_callback):
        """Student dialog with refresh callback para real-time update"""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(550, 700)
        dialog.setStyleSheet("background-color: #E7E7DF;")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 22px; font-weight: 700; color: #222;")
        layout.addWidget(title_label)
        
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
            if student:
                field.setText(str(student.get(field_key, '')))
            field.setStyleSheet("""
                QLineEdit {
                    padding: 12px;
                    border-radius: 8px;
                    border: 2px solid #C8B6FF;
                    font-size: 14px;
                    background-color: white;
                }
            """)
            layout.addWidget(field)
            fields[field_key] = field
            
            # Disable student_id field when editing
            if student and field_key == "student_id":
                field.setEnabled(False)
        
        scroll.setWidget(scroll_content)
        
        main_layout = QVBoxLayout(dialog)
        main_layout.addWidget(scroll)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(45)
        cancel_btn.setFixedWidth(120)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border-radius: 8px;
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
        save_btn.setFixedHeight(45)
        save_btn.setFixedWidth(120)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #836FFF;
                color: white;
                border-radius: 8px;
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
                if not value and key in ['student_id', 'first_name', 'last_name']:
                    QMessageBox.warning(dialog, "Missing Information", 
                                      f"Please fill in {key.replace('_', ' ').title()}!")
                    return
                new_student[key] = value
            
            new_student['section_id'] = section['section_id']
            
            # Save or update
            if student:
                # Update existing student
                success, message = self.db.update_student(student['student_id'], new_student)
            else:
                # Add new student
                success, message = self.db.add_student(new_student)
            
            if success:
                QMessageBox.information(dialog, "Success", message)
                dialog.accept()
                # I-refresh ang table immediately
                refresh_callback()
                # I-refresh din ang sections para ma-update ang dashboard
                self.load_sections()
            else:
                QMessageBox.warning(dialog, "Error", message)
        
        save_btn.clicked.connect(save_student)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        main_layout.addLayout(buttons_layout)
        
        dialog.exec_()

    def archive_student_with_refresh(self, student, refresh_callback):
        """I-archive ang student with refresh callback"""
        student_name = f"{student['first_name']} {student['last_name']}"
        
        reply = QMessageBox.question(
            self, 'Archive Student',
            f"Are you sure you want to archive '{student_name}'?\nYou can restore them later from the Archive.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.db.archive_student(student['student_id'])
            if success:
                # I-refresh ang table immediately
                refresh_callback()
                # I-refresh din ang sections para ma-update ang dashboard
                self.load_sections()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)

    def archive_student(self, student):
        """I-archive ang student instead na i-delete"""
        student_name = f"{student['first_name']} {student['last_name']}"
        
        reply = QMessageBox.question(
            self, 'Archive Student',
            f"Are you sure you want to archive '{student_name}'?\nYou can restore them later from the Archive.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.db.archive_student(student['student_id'])
            if success:
                self.load_sections()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)

    def show_archive_dialog(self):
        """Ipakita lahat ng archived sections"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Archived Sections")
        dialog.setMinimumSize(900, 600)
        dialog.setStyleSheet("background-color: #E7E7DF;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("📦 Archived Sections")
        header.setStyleSheet("font-size: 26px; font-weight: 700; color: #222;")
        layout.addWidget(header)
        
        # Get archived sections
        archived_sections = self.db.get_sections(self.user_id, include_archived=True)
        archived_sections = [s for s in archived_sections if s['is_archived']]
        
        if archived_sections:
            # Create table
            table = QTableWidget()
            table.setRowCount(len(archived_sections))
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Section Name", "Archived Date", "Actions", "Delete"])
            table.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #F5F5F5;
                    color: #333;
                    font-weight: 600;
                    padding: 10px;
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
                    padding: 10px;
                    color: #333;
                }
            """)
            table.verticalHeader().setVisible(False)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            table.setColumnWidth(2, 120)
            table.setColumnWidth(3, 120)
            
            for row, section in enumerate(archived_sections):
                table.setItem(row, 0, QTableWidgetItem(section['section_name']))
                archived_date = section.get('archived_at', 'Unknown')
                if archived_date and archived_date != 'Unknown':
                    archived_date = str(archived_date).split('.')[0]  # Remove microseconds
                table.setItem(row, 1, QTableWidgetItem(archived_date))
                
                # Restore button
                restore_btn = QPushButton(" Restore")
                restore_btn.setIcon(QIcon("image/restore.png"))
                restore_btn.setIconSize(QSize(20, 20))
                restore_btn.setCursor(Qt.PointingHandCursor)
                restore_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E6EFFA;
                        color: #000000;
                        border-radius: 6px;
                        padding: 8px 15px;
                        font-size: 13px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #C8B6FF;
                    }
                """)
                restore_btn.clicked.connect(lambda checked, s=section: self.restore_section(s, dialog))
                table.setCellWidget(row, 2, restore_btn)
                
                # Permanent delete button
                delete_btn = QPushButton(" Delete")
                delete_btn.setIcon(QIcon("image/bin.png"))
                delete_btn.setIconSize(QSize(20, 20))
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFE6E6;
                        color: #000000;
                        border-radius: 6px;
                        padding: 8px 15px;
                        font-size: 13px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #FFCCCC;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, s=section: self.delete_section_permanently(s, dialog))
                table.setCellWidget(row, 3, delete_btn)
                
                table.setRowHeight(row, 50)
            
            layout.addWidget(table)
        else:
            no_archive = QLabel("No archived sections")
            no_archive.setStyleSheet("font-size: 16px; color: #999; padding: 40px;")
            no_archive.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_archive)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedHeight(40)
        close_btn.setFixedWidth(120)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
        dialog.exec_()

    def show_student_archive_dialog(self, section, refresh_callback=None):
        """Ipakita ang archived students para sa specific section"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Archived Students - {section['section_name']}")
        dialog.resize(1200, 700)
        dialog.setStyleSheet("background-color: #E7E7DF;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel(f"📦 Archived Students - {section['section_name']}")
        header.setStyleSheet("font-size: 24px; font-weight: 700; color: #222;")
        layout.addWidget(header)
        
        # Get archived students
        all_students = self.db.get_students(section['section_id'], include_archived=True)
        archived_students = [s for s in all_students if s['is_archived']]
        
        if archived_students:
            # Create table
            table = QTableWidget()
            table.setRowCount(len(archived_students))
            table.setColumnCount(10)
            table.setHorizontalHeaderLabels([
                "Student ID", "First Name", "Last Name", "Age", 
                "Email", "Phone", "Birthday", "Grade", "Restore", "Delete"
            ])
            table.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #F5F5F5;
                    color: #333;
                    font-weight: 600;
                    padding: 10px;
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
                    padding: 10px;
                    color: #333;
                }
            """)
            table.verticalHeader().setVisible(False)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            # Set column widths for better fit
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Student ID
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # First Name
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Last Name
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Age
            table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # Email
            table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Phone
            table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Birthday
            table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Grade
            table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)  # Restore
            table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Fixed)  # Delete
            table.setColumnWidth(8, 80)
            table.setColumnWidth(9, 80)
            
            for row, student in enumerate(archived_students):
                table.setItem(row, 0, QTableWidgetItem(student.get('student_id', '')))
                table.setItem(row, 1, QTableWidgetItem(student.get('first_name', '')))
                table.setItem(row, 2, QTableWidgetItem(student.get('last_name', '')))
                table.setItem(row, 3, QTableWidgetItem(str(student.get('age', ''))))
                table.setItem(row, 4, QTableWidgetItem(student.get('email', '')))
                table.setItem(row, 5, QTableWidgetItem(student.get('phone', '')))
                table.setItem(row, 6, QTableWidgetItem(student.get('birthday', '')))
                table.setItem(row, 7, QTableWidgetItem(str(student.get('grade', ''))))
                
                # Restore button
                restore_btn = QPushButton()
                restore_btn.setIcon(QIcon("image/restore.png"))
                restore_btn.setIconSize(QSize(20, 20))
                restore_btn.setCursor(Qt.PointingHandCursor)
                restore_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E6EFFA;
                        color: #000000;
                        border-radius: 6px;
                        padding: 5px;
                        font-size: 16px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #C8B6FF;
                    }
                """)
                restore_btn.clicked.connect(lambda checked, s=student: self.restore_student(s, dialog, refresh_callback))
                table.setCellWidget(row, 8, restore_btn)
                
                # Permanent delete button
                delete_btn = QPushButton()
                delete_btn.setIcon(QIcon("image/bin.png"))
                delete_btn.setIconSize(QSize(20, 20))
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFE6E6;
                        color: #000000;
                        border-radius: 6px;
                        padding: 5px;
                        font-size: 16px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #FFCCCC;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, s=student: self.delete_student_permanently(s, dialog))
                table.setCellWidget(row, 9, delete_btn)
                
                table.setRowHeight(row, 50)
            
            layout.addWidget(table)
        else:
            no_archive = QLabel("No archived students in this section")
            no_archive.setStyleSheet("font-size: 16px; color: #999; padding: 40px;")
            no_archive.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_archive)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedHeight(40)
        close_btn.setFixedWidth(120)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
        dialog.exec_()

    def restore_section(self, section, parent_dialog):
        """I-restore ang archived section"""
        reply = QMessageBox.question(
            parent_dialog, 'Restore Section',
            f"Restore section '{section['section_name']}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.db.restore_section(section['section_id'])
            if success:
                self.load_sections()
                parent_dialog.accept()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)

    def delete_section_permanently(self, section, parent_dialog):
        """Permanenteng i-delete ang section"""
        reply = QMessageBox.question(
            parent_dialog, 'Permanently Delete',
            f"PERMANENTLY delete section '{section['section_name']}'?\nThis action CANNOT be undone!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.db.delete_section_permanently(section['section_id'])
            if success:
                self.load_sections()
                parent_dialog.accept()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)

    def restore_student(self, student, parent_dialog, refresh_callback=None):
        """I-restore ang archived student"""
        student_name = f"{student['first_name']} {student['last_name']}"
        reply = QMessageBox.question(
            parent_dialog, 'Restore Student',
            f"Restore student '{student_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.db.restore_student(student['student_id'])
            if success:
                self.load_sections()
                # Refresh the section details dialog if callback is provided
                if refresh_callback:
                    refresh_callback()
                parent_dialog.accept()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)

    def delete_student_permanently(self, student, parent_dialog):
        """Permanenteng i-delete ang student"""
        student_name = f"{student['first_name']} {student['last_name']}"
        reply = QMessageBox.question(
            parent_dialog, 'Permanently Delete',
            f"PERMANENTLY delete student '{student_name}'?\nThis action CANNOT be undone!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.db.delete_student_permanently(student['student_id'])
            if success:
                self.load_sections()
                parent_dialog.accept()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)
