from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
sys.path.append('..')
from utils.database import DatabaseConnection


class GradeLineEdit(QLineEdit): #Custom QLineEdit that shows error message for invalid input
    
    def __init__(self, parent_widget, field_name):
        super().__init__()
        self.parent_widget = parent_widget
        self.field_name = field_name
    
    def keyPressEvent(self, event):
        # Check if the key is valid (digit, decimal point, backspace, delete, arrow keys, etc.)
        key = event.text()
        allowed_keys = [Qt.Key_Backspace, Qt.Key_Delete, Qt.Key_Left, Qt.Key_Right, 
                       Qt.Key_Tab, Qt.Key_Home, Qt.Key_End, Qt.Key_Return, Qt.Key_Enter]
        
        if key and key not in '0123456789.' and event.key() not in allowed_keys:
            QMessageBox.warning(
                self.parent_widget,
                "Invalid Input",
                f"Please enter only numbers and decimal point (.) for {self.field_name}.\n\nLetters and symbols are not allowed."
            )
            return  # Ignore the key press
        super().keyPressEvent(event)


class ClassDetailPage(QWidget):
    grades_updated = pyqtSignal()  # Signal for when grades are updated
    
    def __init__(self, section, user_id=1, card_color=None):
        super().__init__()
        self.section = section
        self.user_id = user_id
        self.card_color = card_color if card_color else '#9E9E9E'
        self.db = DatabaseConnection()
        self.current_tab = 'attendance'
        self.class_title = None  # Will store reference to title label
        self.load_attendance_from_database()  # Load attendance records from database
        self.init_ui()

    def load_attendance_from_database(self):
        """Load attendance records from database"""
        self.attendance_records = []
        
        db_records = self.db.get_attendance_records(self.section['section_id'])
        
        for record in db_records:
            # Get detailed attendance data
            attendance_data = self.db.get_attendance_details(record['attendance_id'])
            
            # Format date
            date_obj = record['attendance_date']
            formatted_date = date_obj.strftime('%B %d, %Y')
            day_name = record['day_name']
            
            self.attendance_records.append({
                'attendance_id': record['attendance_id'],
                'date': formatted_date,
                'day': day_name,
                'total': int(record['total_marked'] or 0),
                'present': int(record['present_count'] or 0),
                'absent': int(record['absent_count'] or 0),
                'attendance_data': attendance_data
            })

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #E7E7DF;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(20)

        # Class header
        header_layout = QHBoxLayout()
        
        # Back button and class name
        back_btn = QPushButton("← Back to My Classes")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: none;
                font-size: 16px;
                font-weight: bold;
                text-align: left;
                padding: 5px;
            }
            QPushButton:hover {
                color: #222;
                text-decoration: underline;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(back_btn)
        
        self.class_title = QLabel(self.section['section_name'])
        self.class_title.setStyleSheet(f"""
            font-size: 28px; 
            font-weight: 700; 
            color: #222;
            border-left: 5px solid {self.card_color};
            padding-left: 15px;
        """)
        title_layout.addWidget(self.class_title)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        content_layout.addLayout(header_layout)

        # Tabs header (outside container, on beige background)
        tabs_header = QWidget()
        tabs_header.setStyleSheet("background-color: transparent;")
        tabs_layout = QHBoxLayout(tabs_header)
        tabs_layout.setContentsMargins(0, 10, 0, 10)
        tabs_layout.setSpacing(10)
        
        # Create tab buttons
        self.student_tab = QPushButton("Student")
        self.attendance_tab = QPushButton("Attendance")
        self.grades_tab = QPushButton("Grades")
        
        self.tabs = [self.student_tab, self.attendance_tab, self.grades_tab]
        
        for tab in self.tabs:
            tab.setCursor(Qt.PointingHandCursor)
            tab.setFixedHeight(40)
            tab.setMinimumWidth(120)
            tab.setStyleSheet(self.get_inactive_tab_style())
            tabs_layout.addWidget(tab)
        
        # Set first tab as active
        self.student_tab.setStyleSheet(self.get_active_tab_style())
        
        # Connect tab clicks
        self.student_tab.clicked.connect(lambda: self.switch_tab('student'))
        self.attendance_tab.clicked.connect(lambda: self.switch_tab('attendance'))
        self.grades_tab.clicked.connect(lambda: self.switch_tab('grades'))
        
        tabs_layout.addStretch()
        content_layout.addWidget(tabs_header)

        # Content container (gray rounded box)
        content_container = QWidget()
        content_container.setStyleSheet("""
            QWidget {
                background-color: #9E9E9E;
                border-radius: 15px;
            }
        """)
        content_container_layout = QVBoxLayout(content_container)
        content_container_layout.setContentsMargins(20, 20, 20, 20)
        content_container_layout.setSpacing(0)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(scroll_content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(15)
        self.content_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(scroll_content)

        content_container_layout.addWidget(scroll)
        content_layout.addWidget(content_container)

        main_layout.addWidget(content_widget)
        
        # Load initial content
        self.load_student_view()

    def get_inactive_tab_style(self):
        return """
            QPushButton {
                background-color: #D3D3D3;
                color: #333;
                border: none;
                border-radius: 8px 8px 0px 0px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #C0C0C0;
            }
        """
    
    def get_active_tab_style(self):
        return """
            QPushButton {
                background-color: #808080;
                color: white;
                border: none;
                border-radius: 8px 8px 0px 0px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
        """

    def switch_tab(self, tab_key):
        """Switch between tabs"""
        self.current_tab = tab_key
        
        # Reset all tabs to inactive
        for tab in self.tabs:
            tab.setStyleSheet(self.get_inactive_tab_style())
        
        # Set active tab style and load content
        if tab_key == 'student':
            self.student_tab.setStyleSheet(self.get_active_tab_style())
            self.load_student_view()
        elif tab_key == 'attendance':
            self.attendance_tab.setStyleSheet(self.get_active_tab_style())
            self.load_attendance_view()
        elif tab_key == 'grades':
            self.grades_tab.setStyleSheet(self.get_active_tab_style())
            self.load_grades_view()

    def load_student_view(self):
        """Load student list view with full details"""
        self.clear_content_layout()
        QApplication.processEvents()  # Ensure widgets are cleared
        
        # Header with buttons
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Student count label
        students = list(self.db.get_students(self.section['section_id'], include_archived=False))
        self.student_count_label = QLabel(f"{len(students)} students")
        self.student_count_label.setStyleSheet("""
            font-size: 18px; 
            color: #777; 
            font-weight: 600;
            padding: 5px 10px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        """)
        self.student_count_label.setMinimumWidth(150)
        header_layout.addWidget(self.student_count_label)
        
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
        add_student_btn.clicked.connect(self.add_student)
        header_layout.addWidget(add_student_btn)
        
        # View Archive button
        view_archive_btn = QPushButton("📦 View Archive")
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
        view_archive_btn.clicked.connect(self.view_student_archive)
        header_layout.addWidget(view_archive_btn)
        
        self.content_layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 10, 0, 10)
        
        search_icon = QLabel()
        search_icon.setPixmap(QIcon("image/search.png").pixmap(20, 20))
        search_icon.setStyleSheet("background: transparent;")
        search_layout.addWidget(search_icon)
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-size: 14px; color: #555; font-weight: 600;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Student ID, Name, Email, or Phone...")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #DDD;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #808080;
            }
        """)
        self.search_input.textChanged.connect(self.filter_students)
        search_layout.addWidget(self.search_input)
        
        # Clear search button
        clear_btn = QPushButton("✕ Clear")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setFixedHeight(40)
        clear_btn.setFixedWidth(100)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        clear_btn.clicked.connect(lambda: self.search_input.clear())
        search_layout.addWidget(clear_btn)
        
        self.content_layout.addLayout(search_layout)
        
        # Container for table (for easy refresh)
        self.table_container = QWidget()
        table_layout = QVBoxLayout(self.table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create table with full student details
        self.refresh_student_table()
        
        self.content_layout.addWidget(self.table_container)
    
    def refresh_student_table(self, search_query=""):
        """Refresh the student table with optional search filter"""
        # Clear current table
        while self.table_container.layout().count():
            item = self.table_container.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get updated students
        all_students = list(self.db.get_students(self.section['section_id'], include_archived=False))
        
        # Filter students based on search query
        if search_query:
            search_lower = search_query.lower()
            students = [
                student for student in all_students
                if (search_lower in str(student.get('student_id', '')).lower() or
                    search_lower in student.get('first_name', '').lower() or
                    search_lower in student.get('last_name', '').lower() or
                    search_lower in f"{student.get('first_name', '')} {student.get('last_name', '')}".lower() or
                    search_lower in student.get('email', '').lower() or
                    search_lower in str(student.get('phone', '')).lower())
            ]
        else:
            students = all_students
        
        # Update count label
        if hasattr(self, 'student_count_label'):
            if search_query:
                self.student_count_label.setText(f"{len(students)} of {len(all_students)} students")
            else:
                self.student_count_label.setText(f"{len(students)} students")
        
        if students:
            table = self.create_students_table(students)
            self.table_container.layout().addWidget(table)
        else:
            if search_query:
                no_students = QLabel(f"No students found matching '{search_query}'")
            else:
                no_students = QLabel("No students yet. Click 'Add Student' to get started!")
            no_students.setStyleSheet("font-size: 16px; color: #999; padding: 40px;")
            no_students.setAlignment(Qt.AlignCenter)
            self.table_container.layout().addWidget(no_students)
    
    def filter_students(self):
        """Filter students based on search input"""
        search_query = self.search_input.text().strip() if hasattr(self, 'search_input') else ""
        self.refresh_student_table(search_query)
    
    def create_students_table(self, students):
        """Create detailed students table"""
        table = QTableWidget()
        table.setRowCount(len(students))
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Student ID", "Full Name", "Age", "Email", "Phone", "Actions"
        ])
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #808080;
                color: white;
                padding: 12px;
                border: none;
                font-weight: 600;
                font-size: 13px;
            }
        """)
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 10px;
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
        
        # Set column widths
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Student ID
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Full Name
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Age
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Email
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Phone
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)  # Actions
        table.setColumnWidth(5, 100)
        
        for row, student in enumerate(students):
            table.setItem(row, 0, QTableWidgetItem(student.get('student_id', '')))
            
            # Combine first_name and last_name for Full Name column
            full_name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
            table.setItem(row, 1, QTableWidgetItem(full_name))
            
            table.setItem(row, 2, QTableWidgetItem(str(student.get('age', ''))))
            table.setItem(row, 3, QTableWidgetItem(student.get('email', '')))
            table.setItem(row, 4, QTableWidgetItem(student.get('phone', '')))
            
            # Action buttons widget
            actions_widget = self.create_action_buttons(student)
            table.setCellWidget(row, 5, actions_widget)
            table.setRowHeight(row, 50)
        
        return table
    
    def create_action_buttons(self, student):
        """Create edit and delete action buttons"""
        actions_widget = QWidget()
        actions_widget.setStyleSheet("background-color: white;")
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(10, 5, 10, 5)
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
                border: 1px solid #E6EFFA;
            }
            QPushButton:hover {
                background-color: #C8B6FF;
                border-color: #C8B6FF;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_student(student))
        
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("image/bin.png"))
        delete_btn.setIconSize(QSize(18, 18))
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedSize(35, 35)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFE6E6;
                border-radius: 6px;
                border: 1px solid #FFE6E6;
            }
            QPushButton:hover {
                background-color: #FFCCCC;
                border-color: #FFCCCC;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_student(student))
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        actions_layout.addStretch()
        
        return actions_widget
    
    def load_attendance_view(self):
        """Load attendance view with table"""
        from datetime import datetime, timedelta
        
        self.clear_content_layout()
        QApplication.processEvents()  # Ensure widgets are cleared
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 10)
        
        search_icon = QLabel()
        search_icon.setPixmap(QIcon("image/search.png").pixmap(20, 20))
        search_icon.setStyleSheet("background: transparent;")
        search_layout.addWidget(search_icon)
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-size: 14px; color: #555; font-weight: 600;")
        search_layout.addWidget(search_label)
        
        self.attendance_search_input = QLineEdit()
        self.attendance_search_input.setPlaceholderText("Search by date or day...")
        self.attendance_search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #DDD;
                border-radius: 8px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #666;
            }
        """)
        self.attendance_search_input.textChanged.connect(self.filter_attendance_table)
        search_layout.addWidget(self.attendance_search_input, 1)
        
        clear_btn = QPushButton("✕ Clear")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setFixedHeight(40)
        clear_btn.setFixedWidth(90)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #555;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        clear_btn.clicked.connect(lambda: self.attendance_search_input.clear())
        search_layout.addWidget(clear_btn)
        
        self.content_layout.addLayout(search_layout)
        
        # Container for table (for easy refresh)
        self.attendance_table_container = QWidget()
        table_layout = QVBoxLayout(self.attendance_table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create attendance table with sample data
        self.create_attendance_table()
        
        self.content_layout.addWidget(self.attendance_table_container)
        
        # Create Attendance button at bottom right
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Archived Attendance button
        archived_btn = QPushButton("Archived Attendance")
        archived_btn.setCursor(Qt.PointingHandCursor)
        archived_btn.setFixedSize(180, 45)
        archived_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        archived_btn.clicked.connect(self.show_archived_attendance)
        button_layout.addWidget(archived_btn)
        
        create_attendance_btn = QPushButton("Create Attendance")
        create_attendance_btn.setCursor(Qt.PointingHandCursor)
        create_attendance_btn.setFixedSize(180, 45)
        create_attendance_btn.setStyleSheet("""
            QPushButton {
                background-color: #222;
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        create_attendance_btn.clicked.connect(self.create_attendance)
        button_layout.addWidget(create_attendance_btn)
        
        self.content_layout.addLayout(button_layout)
    
    def create_attendance_table(self, search_query=""):
        """Create the attendance table with dates"""
        from datetime import datetime, timedelta
        
        # Clear current table
        while self.attendance_table_container.layout().count():
            item = self.attendance_table_container.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Use stored attendance records (exclude archived)
        attendance_data = [record for record in self.attendance_records if not record.get('archived', False)]
        
        # Filter data based on search query
        if search_query and attendance_data:
            search_lower = search_query.lower()
            attendance_data = [
                record for record in attendance_data
                if (search_lower in record['date'].lower() or
                    search_lower in record['day'].lower())
            ]
        
        # Create table
        table = QTableWidget()
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 10px;
                gridline-color: #DDD;
            }
            QHeaderView::section {
                background-color: #5A5A5A;
                color: white;
                padding: 12px;
                border: none;
                font-weight: 600;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px;
                color: #333;
                font-size: 13px;
                border-bottom: 1px solid #DDD;
            }
        """)
        
        # Set columns
        columns = ["Date", "Day", "Total", "Present", "Absent", "Actions"]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setRowCount(len(attendance_data))
        
        # Populate table (currently empty)
        for row, record in enumerate(attendance_data):
            # Date
            date_item = QTableWidgetItem(record['date'])
            date_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 0, date_item)
            
            # Day
            day_item = QTableWidgetItem(record['day'])
            day_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 1, day_item)
            
            # Total
            total_item = QTableWidgetItem(f"Total: {record['total']}")
            total_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 2, total_item)
            
            # Present
            present_item = QTableWidgetItem(f"Present: {record['present']}")
            present_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 3, present_item)
            
            # Absent
            absent_item = QTableWidgetItem(f"Absent: {record['absent']}")
            absent_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 4, absent_item)
            
            # Action buttons (Edit, Delete, View)
            action_widget = QWidget()
            action_widget.setStyleSheet("background-color: white;")
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(10, 5, 10, 5)
            action_layout.setSpacing(5)
            action_layout.setAlignment(Qt.AlignCenter)
            
            # Edit button
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("image/edit.png"))
            edit_btn.setIconSize(QSize(16, 16))
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setFixedSize(35, 35)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E6EFFA;
                    border-radius: 6px;
                    border: 1px solid #E6EFFA;
                }
                QPushButton:hover {
                    background-color: #C8B6FF;
                    border-color: #C8B6FF;
                }
            """)
            edit_btn.clicked.connect(lambda checked, r=record: self.edit_attendance(r))
            action_layout.addWidget(edit_btn)
            
            # Delete button
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("image/bin.png"))
            delete_btn.setIconSize(QSize(16, 16))
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setFixedSize(35, 35)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFE6E6;
                    border-radius: 6px;
                    border: 1px solid #FFE6E6;
                }
                QPushButton:hover {
                    background-color: #FFCCCC;
                    border-color: #FFCCCC;
                }
            """)
            delete_btn.clicked.connect(lambda checked, r=record: self.delete_attendance(r))
            action_layout.addWidget(delete_btn)
            
            # View button
            view_btn = QPushButton("View")
            view_btn.setCursor(Qt.PointingHandCursor)
            view_btn.setFixedSize(60, 35)
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007BFF;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #0056B3;
                }
            """)
            view_btn.clicked.connect(lambda checked, r=record: self.view_attendance_details(r))
            action_layout.addWidget(view_btn)
            
            table.setCellWidget(row, 5, action_widget)
        
        # Adjust column widths - make all columns equal and stretch to fill frame
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set minimum row height for better spacing and button visibility
        for row in range(table.rowCount()):
            table.setRowHeight(row, 65)
        
        self.attendance_table_container.layout().addWidget(table)
    
    def filter_attendance_table(self):
        """Filter attendance table based on search input"""
        search_query = self.attendance_search_input.text().strip() if hasattr(self, 'attendance_search_input') else ""
        self.create_attendance_table(search_query)
    
    def view_attendance_details(self, record):
        """View detailed attendance for a specific date"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Attendance Details - {record['date']}")
        dialog.setWindowIcon(QIcon("image/system.png"))
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel(f"Attendance for {record['day']}, {record['date']}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #222;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Summary
        summary = QLabel(f"Total: {record['total']} | Present: {record['present']} | Absent: {record['absent']}")
        summary.setStyleSheet("font-size: 14px; color: #555; font-weight: 600;")
        header_layout.addWidget(summary)
        
        layout.addLayout(header_layout)
        
        # Get students data from record
        attendance_data = record.get('attendance_data', {})
        
        if not attendance_data:
            no_data = QLabel("No attendance data available")
            no_data.setStyleSheet("font-size: 16px; color: #999; padding: 40px;")
            no_data.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data)
            layout.addStretch()
        else:
            # Create table
            table = QTableWidget()
            table.setRowCount(len(attendance_data))
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Student ID", "Full Name", "Status"])
            
            table.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #5A5A5A;
                    color: white;
                    padding: 12px;
                    border: none;
                    font-weight: 600;
                    font-size: 13px;
                }
            """)
            
            table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #DDD;
                    border-radius: 8px;
                    background-color: white;
                    gridline-color: #DDD;
                }
                QTableWidget::item {
                    padding: 10px;
                    color: #333;
                    font-size: 13px;
                }
            """)
            
            table.verticalHeader().setVisible(False)
            table.setSelectionMode(QTableWidget.NoSelection)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            # Set column widths
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
            table.setColumnWidth(0, 150)
            table.setColumnWidth(2, 150)
            
            # Get all students for this section
            students = list(self.db.get_students(self.section['section_id'], include_archived=False))
            
            row = 0
            for student in students:
                student_id = student.get('student_id', '')
                
                if student_id not in attendance_data:
                    continue
                    
                # Student ID
                id_item = QTableWidgetItem(student_id)
                table.setItem(row, 0, id_item)
                
                # Full Name
                full_name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
                name_item = QTableWidgetItem(full_name)
                table.setItem(row, 1, name_item)
                
                # Status
                status = attendance_data[student_id].get('status', 'Not Marked')
                status_item = QTableWidgetItem(status.upper() if status else 'NOT MARKED')
                
                # Color code status with background color
                if status == 'present':
                    status_item.setBackground(QColor("#D4EDDA"))  # Light green
                    status_item.setForeground(QColor("#155724"))  # Dark green text
                elif status == 'absent':
                    status_item.setBackground(QColor("#F8D7DA"))  # Light red
                    status_item.setForeground(QColor("#721C24"))  # Dark red text
                else:
                    status_item.setForeground(QColor("#999"))
                    
                status_item.setFont(QFont("Arial", 12, QFont.Bold))
                table.setItem(row, 2, status_item)
                
                table.setRowHeight(row, 45)
                row += 1
            
            table.setRowCount(row)  # Adjust to actual rows
            layout.addWidget(table)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(120, 45)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def create_attendance(self):
        """Create new attendance record"""
        from datetime import datetime
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Attendance")
        dialog.setWindowIcon(QIcon("image/system.png"))
        dialog.setMinimumSize(900, 600)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header with date
        header_layout = QHBoxLayout()
        
        title = QLabel("Take Attendance")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #222;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Real-time date
        current_date = datetime.now()
        date_label = QLabel(current_date.strftime("%B %d, %Y - %A"))
        date_label.setStyleSheet("font-size: 18px; color: #555; font-weight: 600;")
        header_layout.addWidget(date_label)
        
        layout.addLayout(header_layout)
        
        # Get students for this section
        students = list(self.db.get_students(self.section['section_id'], include_archived=False))
        
        if not students:
            no_students = QLabel("No students in this section")
            no_students.setStyleSheet("font-size: 16px; color: #999; padding: 40px;")
            no_students.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_students)
        else:
            # Attendance table
            table = QTableWidget()
            table.setRowCount(len(students))
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Student Id", "Full Name", "Present", "Absent"])
            
            table.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #5A5A5A;
                    color: white;
                    padding: 12px;
                    border: none;
                    font-weight: 600;
                    font-size: 13px;
                }
            """)
            
            table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #DDD;
                    border-radius: 8px;
                    background-color: white;
                    gridline-color: #DDD;
                }
                QTableWidget::item {
                    padding: 10px;
                    color: #333;
                    background-color: white;
                    font-size: 13px;
                }
            """)
            
            table.verticalHeader().setVisible(False)
            table.setSelectionMode(QTableWidget.NoSelection)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            # Set column widths
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
            table.setColumnWidth(2, 140)
            table.setColumnWidth(3, 140)
            
            # Store attendance data
            self.attendance_data = {}
            
            for row, student in enumerate(students):
                student_id = student.get('student_id', '')
                
                # Student ID
                id_item = QTableWidgetItem(student_id)
                id_item.setForeground(QColor("white"))
                table.setItem(row, 0, id_item)
                
                # Full Name
                full_name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
                name_item = QTableWidgetItem(full_name)
                name_item.setForeground(QColor("white"))
                table.setItem(row, 1, name_item)
                
                # Present button
                present_widget = QWidget()
                present_layout = QHBoxLayout(present_widget)
                present_layout.setContentsMargins(0, 0, 0, 0)
                present_layout.setAlignment(Qt.AlignCenter)
                
                present_btn = QPushButton("Present")
                present_btn.setCursor(Qt.PointingHandCursor)
                present_btn.setFixedSize(100, 35)
                present_btn.setProperty("student_id", student_id)
                present_btn.setProperty("status", "present")
                present_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #6C757D;
                        color: white;
                        border: 2px solid #6C757D;
                        border-radius: 6px;
                        font-weight: 600;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #5A6268;
                    }
                    QPushButton[selected="true"] {
                        background-color: #28A745;
                        border-color: #28A745;
                    }
                """)
                present_btn.clicked.connect(lambda checked, sid=student_id, btn=present_btn: self.mark_attendance(sid, "present", btn))
                present_layout.addWidget(present_btn)
                table.setCellWidget(row, 2, present_widget)
                
                # Absent button
                absent_widget = QWidget()
                absent_layout = QHBoxLayout(absent_widget)
                absent_layout.setContentsMargins(0, 0, 0, 0)
                absent_layout.setAlignment(Qt.AlignCenter)
                
                absent_btn = QPushButton("Absent")
                absent_btn.setCursor(Qt.PointingHandCursor)
                absent_btn.setFixedSize(100, 35)
                absent_btn.setProperty("student_id", student_id)
                absent_btn.setProperty("status", "absent")
                absent_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #6C757D;
                        color: white;
                        border: 2px solid #6C757D;
                        border-radius: 6px;
                        font-weight: 600;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #5A6268;
                    }
                    QPushButton[selected="true"] {
                        background-color: #DC3545;
                        border-color: #DC3545;
                    }
                """)
                absent_btn.clicked.connect(lambda checked, sid=student_id, btn=absent_btn: self.mark_attendance(sid, "absent", btn))
                absent_layout.addWidget(absent_btn)
                table.setCellWidget(row, 3, absent_widget)
                
                table.setRowHeight(row, 65)
                
                # Store button references
                self.attendance_data[student_id] = {
                    'present_btn': present_btn,
                    'absent_btn': absent_btn,
                    'status': None
                }
            
            layout.addWidget(table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedSize(120, 45)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Attendance")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedSize(150, 45)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
        """)
        save_btn.clicked.connect(lambda: self.save_attendance(dialog, current_date))
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def mark_attendance(self, student_id, status, clicked_btn):
        """Mark student attendance and update button states"""
        if student_id in self.attendance_data:
            data = self.attendance_data[student_id]
            
            # Reset both buttons to default state
            data['present_btn'].setProperty("selected", "false")
            data['absent_btn'].setProperty("selected", "false")
            data['present_btn'].setStyle(data['present_btn'].style())
            data['absent_btn'].setStyle(data['absent_btn'].style())
            
            # Set clicked button as selected
            clicked_btn.setProperty("selected", "true")
            clicked_btn.setStyle(clicked_btn.style())
            
            # Update status
            data['status'] = status
    
    def save_attendance(self, dialog, date):
        """Save attendance record to database"""
        # Count marked students
        marked_count = sum(1 for data in self.attendance_data.values() if data['status'] is not None)
        
        if marked_count == 0:
            QMessageBox.warning(dialog, "No Attendance Marked", "Please mark attendance for at least one student!")
            return
        
        # Count present and absent
        present_count = sum(1 for data in self.attendance_data.values() if data['status'] == 'present')
        absent_count = sum(1 for data in self.attendance_data.values() if data['status'] == 'absent')
        
        # Save to database
        attendance_date = date.strftime('%Y-%m-%d')
        success = self.db.save_attendance(
            self.section['section_id'],
            attendance_date,
            self.attendance_data
        )
        
        if success:
            QMessageBox.information(
                dialog, 
                "Attendance Saved", 
                f"Attendance for {date.strftime('%B %d, %Y')} has been saved!\n"
                f"Present: {present_count} | Absent: {absent_count}"
            )
            dialog.accept()
            
            # Reload attendance records from database
            self.load_attendance_from_database()
            # Refresh the attendance table
            self.create_attendance_table()
        else:
            QMessageBox.critical(
                dialog,
                "Error",
                "Failed to save attendance to database!"
            )
    
    def edit_attendance(self, record):
        """Edit an existing attendance record"""
        from datetime import datetime
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Attendance - {record['date']}")
        dialog.setWindowIcon(QIcon("image/system.png"))
        dialog.setMinimumSize(900, 600)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header with date
        header_layout = QHBoxLayout()
        
        title = QLabel("Edit Attendance")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #222;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Show the date being edited
        date_label = QLabel(record['date'] + " - " + record['day'])
        date_label.setStyleSheet("font-size: 18px; color: #555; font-weight: 600;")
        header_layout.addWidget(date_label)
        
        layout.addLayout(header_layout)
        
        # Get students for this section
        students = list(self.db.get_students(self.section['section_id'], include_archived=False))
        
        if not students:
            no_students = QLabel("No students in this section")
            no_students.setStyleSheet("font-size: 16px; color: #999; padding: 40px;")
            no_students.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_students)
        else:
            # Attendance table
            table = QTableWidget()
            table.setRowCount(len(students))
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Student Id", "Full Name", "Present", "Absent"])
            
            table.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #5A5A5A;
                    color: white;
                    padding: 12px;
                    border: none;
                    font-weight: 600;
                    font-size: 13px;
                }
            """)
            
            table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #DDD;
                    border-radius: 8px;
                    background-color: white;
                    gridline-color: #DDD;
                }
                QTableWidget::item {
                    padding: 10px;
                    color: #333;
                    background-color: white;
                    font-size: 13px;
                }
            """)
            
            table.verticalHeader().setVisible(False)
            table.setSelectionMode(QTableWidget.NoSelection)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            # Set column widths
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
            table.setColumnWidth(2, 140)
            table.setColumnWidth(3, 140)
            
            # Store attendance data
            self.attendance_data = {}
            existing_data = record.get('attendance_data', {})
            
            for row, student in enumerate(students):
                student_id = student.get('student_id', '')
                
                # Student ID
                id_item = QTableWidgetItem(student_id)
                id_item.setForeground(QColor("white"))
                table.setItem(row, 0, id_item)
                
                # Full Name
                full_name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
                name_item = QTableWidgetItem(full_name)
                name_item.setForeground(QColor("white"))
                table.setItem(row, 1, name_item)
                
                # Present button
                present_widget = QWidget()
                present_layout = QHBoxLayout(present_widget)
                present_layout.setContentsMargins(0, 0, 0, 0)
                present_layout.setAlignment(Qt.AlignCenter)
                
                present_btn = QPushButton("Present")
                present_btn.setCursor(Qt.PointingHandCursor)
                present_btn.setFixedSize(100, 35)
                present_btn.setProperty("student_id", student_id)
                present_btn.setProperty("status", "present")
                
                # Check if already marked
                existing_status = existing_data.get(student_id, {}).get('status')
                if existing_status == 'present':
                    present_btn.setProperty("selected", "true")
                else:
                    present_btn.setProperty("selected", "false")
                
                present_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #6C757D;
                        color: white;
                        border: 2px solid #6C757D;
                        border-radius: 6px;
                        font-weight: 600;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #5A6268;
                    }
                    QPushButton[selected="true"] {
                        background-color: #28A745;
                        border-color: #28A745;
                    }
                """)
                present_btn.clicked.connect(lambda checked, sid=student_id, btn=present_btn: self.mark_attendance(sid, "present", btn))
                present_layout.addWidget(present_btn)
                table.setCellWidget(row, 2, present_widget)
                
                # Absent button
                absent_widget = QWidget()
                absent_layout = QHBoxLayout(absent_widget)
                absent_layout.setContentsMargins(0, 0, 0, 0)
                absent_layout.setAlignment(Qt.AlignCenter)
                
                absent_btn = QPushButton("Absent")
                absent_btn.setCursor(Qt.PointingHandCursor)
                absent_btn.setFixedSize(100, 35)
                absent_btn.setProperty("student_id", student_id)
                absent_btn.setProperty("status", "absent")
                
                # Check if already marked
                if existing_status == 'absent':
                    absent_btn.setProperty("selected", "true")
                else:
                    absent_btn.setProperty("selected", "false")
                
                absent_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #6C757D;
                        color: white;
                        border: 2px solid #6C757D;
                        border-radius: 6px;
                        font-weight: 600;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #5A6268;
                    }
                    QPushButton[selected="true"] {
                        background-color: #DC3545;
                        border-color: #DC3545;
                    }
                """)
                absent_btn.clicked.connect(lambda checked, sid=student_id, btn=absent_btn: self.mark_attendance(sid, "absent", btn))
                absent_layout.addWidget(absent_btn)
                table.setCellWidget(row, 3, absent_widget)
                
                table.setRowHeight(row, 60)
                
                # Store button references with existing status
                self.attendance_data[student_id] = {
                    'present_btn': present_btn,
                    'absent_btn': absent_btn,
                    'status': existing_status
                }
            
            layout.addWidget(table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedSize(120, 45)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Update Attendance")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedSize(180, 45)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
        """)
        save_btn.clicked.connect(lambda: self.update_attendance_record(dialog, record))
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def update_attendance_record(self, dialog, record):
        """Update existing attendance record"""
        # Count marked students
        marked_count = sum(1 for data in self.attendance_data.values() if data['status'] is not None)
        
        if marked_count == 0:
            QMessageBox.warning(dialog, "No Attendance Marked", "Please mark attendance for at least one student!")
            return
        
        # Count present and absent
        present_count = sum(1 for data in self.attendance_data.values() if data['status'] == 'present')
        absent_count = sum(1 for data in self.attendance_data.values() if data['status'] == 'absent')
        
        # Update the record in the list
        for i, rec in enumerate(self.attendance_records):
            if rec['date'] == record['date']:
                self.attendance_records[i] = {
                    'date': record['date'],
                    'day': record['day'],
                    'total': len(self.attendance_data),
                    'present': present_count,
                    'absent': absent_count,
                    'attendance_data': dict(self.attendance_data)
                }
                break
        
        QMessageBox.information(
            dialog,
            "Attendance Updated",
            f"Attendance for {record['date']} has been updated!\n"
            f"Present: {present_count} | Absent: {absent_count}"
        )
        dialog.accept()
        
        # Refresh the attendance table
        self.create_attendance_table()
    
    def delete_attendance(self, record):
        """Delete an attendance record with archive option"""
        # Create custom dialog with archive option
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Delete Attendance")
        msg_box.setText(f"What would you like to do with attendance for {record['date']}?")
        
        # Add custom buttons
        archive_btn = msg_box.addButton("Archive", QMessageBox.ActionRole)
        delete_btn = msg_box.addButton("Delete Permanently", QMessageBox.DestructiveRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.RejectRole)
        
        msg_box.exec_()
        
        clicked_btn = msg_box.clickedButton()
        
        if clicked_btn == archive_btn:
            # Archive the attendance
            record['archived'] = True
            QMessageBox.information(
                self,
                "Archived",
                f"Attendance for {record['date']} has been archived!"
            )
            # Refresh the attendance table
            self.create_attendance_table()
            
        elif clicked_btn == delete_btn:
            # Confirm permanent deletion
            confirm = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to permanently delete attendance for {record['date']}?\n\nThis action cannot be undone!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                # Remove from list
                self.attendance_records = [r for r in self.attendance_records if r['date'] != record['date']]
                
                QMessageBox.information(
                    self,
                    "Deleted",
                    f"Attendance for {record['date']} has been permanently deleted!"
                )
                # Refresh the attendance table
                self.create_attendance_table()
    
    def show_archived_attendance(self):
        """Show archived attendance records"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Archived Attendance - {self.section['section_name']}")
        dialog.resize(1200, 700)
        dialog.setStyleSheet("background-color: #E7E7DF;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        archived_records = [record for record in self.attendance_records if record.get('archived', False)]
        header = QLabel(f"📦 Archived Attendance - {self.section['section_name']}")
        header.setStyleSheet("font-size: 24px; font-weight: 700; color: #222;")
        layout.addWidget(header)
        
        if not archived_records:
            no_archive = QLabel("No archived attendance records in this section")
            no_archive.setStyleSheet("font-size: 16px; color: #999;")
            layout.addWidget(no_archive)
            layout.addStretch()
        else:
            # Create table
            table = QTableWidget()
            table.setRowCount(len(archived_records))
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels(["Date", "Day", "Total", "Present", "Absent", "View", "Restore"])
            
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
                    border-radius: 8px;
                    background-color: white;
                    gridline-color: #E0E0E0;
                }
                QTableWidget::item {
                    padding: 12px;
                    color: #333;
                    font-size: 13px;
                    border-bottom: 1px solid #E0E0E0;
                }
            """)
            
            table.verticalHeader().setVisible(False)
            table.setSelectionMode(QTableWidget.NoSelection)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            # Set column widths
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
            table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
            table.setColumnWidth(5, 80)
            table.setColumnWidth(6, 80)
            
            for row, record in enumerate(archived_records):
                # Date
                date_item = QTableWidgetItem(record['date'])
                date_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                table.setItem(row, 0, date_item)
                
                # Day
                day_item = QTableWidgetItem(record['day'])
                day_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                table.setItem(row, 1, day_item)
                
                # Total
                total_item = QTableWidgetItem(f"Total: {record['total']}")
                total_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                table.setItem(row, 2, total_item)
                
                # Present
                present_item = QTableWidgetItem(f"Present: {record['present']}")
                present_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                table.setItem(row, 3, present_item)
                
                # Absent
                absent_item = QTableWidgetItem(f"Absent: {record['absent']}")
                absent_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                table.setItem(row, 4, absent_item)
                
                # View button
                view_widget = QWidget()
                view_widget.setStyleSheet("background-color: white;")
                view_layout = QHBoxLayout(view_widget)
                view_layout.setContentsMargins(5, 5, 5, 5)
                view_layout.setAlignment(Qt.AlignCenter)
                
                view_btn = QPushButton("View")
                view_btn.setCursor(Qt.PointingHandCursor)
                view_btn.setFixedSize(70, 35)
                view_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #007BFF;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #0056B3;
                    }
                """)
                view_btn.clicked.connect(lambda checked, r=record: self.view_attendance_details(r))
                view_layout.addWidget(view_btn)
                table.setCellWidget(row, 5, view_widget)
                
                # Restore button
                restore_widget = QWidget()
                restore_widget.setStyleSheet("background-color: white;")
                restore_layout = QHBoxLayout(restore_widget)
                restore_layout.setContentsMargins(5, 5, 5, 5)
                restore_layout.setAlignment(Qt.AlignCenter)
                
                restore_btn = QPushButton("Restore")
                restore_btn.setCursor(Qt.PointingHandCursor)
                restore_btn.setFixedSize(70, 35)
                restore_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #28A745;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                    }
                """)
                restore_btn.clicked.connect(lambda checked, r=record, d=dialog: self.restore_attendance(r, d))
                restore_layout.addWidget(restore_btn)
                table.setCellWidget(row, 6, restore_widget)
                
                table.setRowHeight(row, 55)
            
            layout.addWidget(table)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(120, 45)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def restore_attendance(self, record, dialog):
        """Restore archived attendance record"""
        reply = QMessageBox.question(
            dialog,
            "Restore Attendance",
            f"Are you sure you want to restore attendance for {record['date']}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Unarchive the record
            record['archived'] = False
            
            QMessageBox.information(
                dialog,
                "Restored",
                f"Attendance for {record['date']} has been restored!"
            )
            
            # Close and refresh
            dialog.close()
            self.create_attendance_table()
            # Reopen archived dialog to show updated list
            self.show_archived_attendance()

    def load_grades_view(self):
        """Load grades view"""
        self.clear_content_layout()
        QApplication.processEvents()  # Ensure widgets are cleared
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 10)
        
        search_icon = QLabel()
        search_icon.setPixmap(QIcon("image/search.png").pixmap(20, 20))
        search_icon.setStyleSheet("background: transparent;")
        search_layout.addWidget(search_icon)
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-size: 14px; color: #555; font-weight: 600;")
        search_layout.addWidget(search_label)
        
        self.grades_search_input = QLineEdit()
        self.grades_search_input.setPlaceholderText("Search by Student ID or Name...")
        self.grades_search_input.setFixedHeight(40)
        self.grades_search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #DDD;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #808080;
            }
        """)
        self.grades_search_input.textChanged.connect(self.filter_grades)
        search_layout.addWidget(self.grades_search_input)
        
        # Clear search button
        clear_btn = QPushButton("✕ Clear")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setFixedHeight(40)
        clear_btn.setFixedWidth(100)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        clear_btn.clicked.connect(lambda: self.grades_search_input.clear())
        search_layout.addWidget(clear_btn)
        
        self.content_layout.addLayout(search_layout)
        
        # Container for table
        self.grades_table_container = QWidget()
        table_layout = QVBoxLayout(self.grades_table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create grades table
        self.create_grades_table()
        
        self.content_layout.addWidget(self.grades_table_container)
    
    def create_grades_table(self, search_query=""):
        """Create the grades table with editable cells"""
        # Clear current table
        while self.grades_table_container.layout().count():
            item = self.grades_table_container.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get students for this section
        all_students = list(self.db.get_students(self.section['section_id'], include_archived=False))
        
        # Filter students based on search query
        if search_query:
            search_lower = search_query.lower()
            students = [
                s for s in all_students
                if search_lower in s.get('student_id', '').lower()
                or search_lower in f"{s.get('first_name', '')} {s.get('last_name', '')}".lower()
            ]
        else:
            students = all_students
        
        if not students:
            no_students = QLabel("No students in this section")
            no_students.setStyleSheet("font-size: 16px; color: #999; padding: 40px;")
            no_students.setAlignment(Qt.AlignCenter)
            self.grades_table_container.layout().addWidget(no_students)
            return
        
        # Create table
        table = QTableWidget()
        table.setRowCount(len(students))
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["Student ID", "Student Name", "Midterm Grade", "Final Grade", "Semestral Grade", "Remarks", "Action"])
        
        # Header styling to match student table
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #808080;
                color: white;
                padding: 12px;
                border: none;
                font-weight: 600;
                font-size: 13px;
            }
        """)
        
        # Table styling to match student table
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                background-color: white;
                gridline-color: #F0F0F0;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #E6EFFA;
            }
        """)
        
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Set column widths
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Student ID
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Student Name
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)  # Midterm
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)  # Final
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)  # Semestral
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)  # Remarks
        table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)  # Action
        table.setColumnWidth(2, 150)
        table.setColumnWidth(3, 150)
        table.setColumnWidth(4, 150)
        table.setColumnWidth(6, 100)
        
        # Store grade inputs for calculation
        self.grade_inputs = {}
        
        for row, student in enumerate(students):
            student_id = student.get('student_id', '')
            
            # Get grades for this student
            grades = self.db.get_student_grades(student_id, self.section['section_id']) if hasattr(self.db, 'get_student_grades') else {}
            
            midterm = grades.get('midterm', 0.0) if grades else 0.0
            final = grades.get('final', 0.0) if grades else 0.0
            
            # Student ID
            id_item = QTableWidgetItem(student_id)
            id_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 0, id_item)
            
            # Student Name
            full_name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
            name_item = QTableWidgetItem(full_name)
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 1, name_item)
            
            # Midterm Grade - Editable cell
            midterm_widget = QWidget()
            midterm_widget.setStyleSheet("background-color: white;")
            midterm_layout = QHBoxLayout(midterm_widget)
            midterm_layout.setContentsMargins(0, 0, 0, 0)
            midterm_layout.setAlignment(Qt.AlignCenter)
            
            midterm_input = GradeLineEdit(self, "Midterm Grade")
            midterm_input.setPlaceholderText("0.00")
            midterm_input.setText(f"{midterm:.2f}" if midterm else "")
            midterm_input.setAlignment(Qt.AlignCenter)
            midterm_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #DDD;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 16px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border: 2px solid #808080;
                }
            """)
            # Add validator for numeric input with max 2 decimal places
            from PyQt5.QtGui import QRegExpValidator
            from PyQt5.QtCore import QRegExp
            midterm_validator = QRegExpValidator(QRegExp(r"^\d*\.?\d{0,2}$"))
            midterm_input.setValidator(midterm_validator)
            midterm_input.textChanged.connect(lambda text, r=row, sid=student_id: self.calculate_semestral(r, sid))
            midterm_layout.addWidget(midterm_input)
            table.setCellWidget(row, 2, midterm_widget)
            
            # Final Grade - Editable cell
            final_widget = QWidget()
            final_widget.setStyleSheet("background-color: white;")
            final_layout = QHBoxLayout(final_widget)
            final_layout.setContentsMargins(0, 0, 0, 0)
            final_layout.setAlignment(Qt.AlignCenter)
            
            final_input = GradeLineEdit(self, "Final Grade")
            final_input.setPlaceholderText("0.00")
            final_input.setText(f"{final:.2f}" if final else "")
            final_input.setAlignment(Qt.AlignCenter)
            final_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #DDD;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 16px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border: 2px solid #808080;
                }
            """)
            # Add validator for numeric input with max 2 decimal places
            final_validator = QRegExpValidator(QRegExp(r"^\d*\.?\d{0,2}$"))
            final_input.setValidator(final_validator)
            final_input.textChanged.connect(lambda text, r=row, sid=student_id: self.calculate_semestral(r, sid))
            final_layout.addWidget(final_input)
            table.setCellWidget(row, 3, final_widget)
            
            # Calculate semestral grade
            semestral = round((midterm + final) / 2, 2) if midterm or final else 0.0
            
            # Semestral Grade - Display only (auto-calculated)
            semestral_item = QTableWidgetItem(f"{semestral:.2f}" if (midterm or final) else "")
            semestral_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            
            # Color code based on grade performance
            if semestral > 0:
                if semestral <= 1.75:
                    semestral_item.setForeground(QColor("#27AE60"))  # Green for Excellent/Very Satisfactory
                elif semestral <= 2.50:
                    semestral_item.setForeground(QColor("#3498DB"))  # Blue for Satisfactory
                elif semestral <= 3.00:
                    semestral_item.setForeground(QColor("#F39C12"))  # Orange for Fairly Satisfactory/Passed
                elif semestral <= 5.00:
                    semestral_item.setForeground(QColor("#E74C3C"))  # Red for Conditional Failure/Failed
                else:
                    semestral_item.setForeground(QColor("#95A5A6"))  # Gray for invalid
                
                # Add tooltip with interpretation
                semestral_item.setToolTip(self.get_grade_interpretation(semestral))
            else:
                semestral_item.setForeground(QColor("#95A5A6"))
            
            semestral_item.setFont(QFont("Arial", 11, QFont.Bold))
            semestral_item.setFlags(semestral_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row, 4, semestral_item)
            
            # Remarks - Display grade interpretation
            remarks_text = ""
            if semestral > 0:
                if semestral >= 1.00 and semestral <= 1.25:
                    remarks_text = "Excellent"
                elif semestral > 1.25 and semestral <= 1.75:
                    remarks_text = "Very Satisfactory"
                elif semestral > 1.75 and semestral <= 2.50:
                    remarks_text = "Satisfactory"
                elif semestral > 2.50 and semestral <= 3.00:
                    remarks_text = "Fairly Satisfactory"
                elif semestral >= 3.00 and semestral < 4.00:
                    remarks_text = "Passed"
                elif semestral >= 4.00 and semestral <= 5.00:
                    remarks_text = "Conditional Failure"
                elif semestral > 5.00:
                    remarks_text = "Failed"
                else:
                    remarks_text = "No Remarks"
            else:
                remarks_text = "No Remarks"
            
            remarks_item = QTableWidgetItem(remarks_text)
            remarks_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            remarks_item.setFont(QFont("Arial", 10, QFont.Bold))
            remarks_item.setFlags(remarks_item.flags() & ~Qt.ItemIsEditable)
            
            # Color code remarks
            if remarks_text in ["Excellent", "Very Satisfactory"]:
                remarks_item.setForeground(QColor("#27AE60"))
            elif remarks_text == "Satisfactory":
                remarks_item.setForeground(QColor("#3498DB"))
            elif remarks_text in ["Fairly Satisfactory", "Passed"]:
                remarks_item.setForeground(QColor("#F39C12"))
            elif remarks_text in ["Conditional Failure", "Failed"]:
                remarks_item.setForeground(QColor("#E74C3C"))
            else:
                remarks_item.setForeground(QColor("#95A5A6"))  # Gray for "No Remarks"
            
            table.setItem(row, 5, remarks_item)
            
            # Store inputs for later access
            self.grade_inputs[student_id] = {
                'row': row,
                'midterm_input': midterm_input,
                'final_input': final_input,
                'table': table
            }
            
            # Action button (Delete)
            action_widget = QWidget()
            action_widget.setStyleSheet("background-color: white;")
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(10, 5, 10, 5)
            action_layout.setAlignment(Qt.AlignCenter)
            
            # Delete button
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("image/bin.png"))
            delete_btn.setIconSize(QSize(18, 18))
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setFixedSize(35, 35)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFE6E6;
                    border-radius: 6px;
                    border: 1px solid #FFE6E6;
                }
                QPushButton:hover {
                    background-color: #FFCCCC;
                    border-color: #FFCCCC;
                }
            """)
            delete_btn.clicked.connect(lambda checked, s=student: self.delete_grade(s))
            action_layout.addWidget(delete_btn)
            
            table.setCellWidget(row, 6, action_widget)
            table.setRowHeight(row, 60)
        
        self.grades_table_container.layout().addWidget(table)
    
    def calculate_semestral(self, row, student_id):
        """Calculate and update semestral grade when midterm or final changes"""
        if student_id not in self.grade_inputs:
            return
        
        grade_data = self.grade_inputs[student_id]
        table = grade_data['table']
        
        try:
            # Get midterm and final values
            midterm_text = grade_data['midterm_input'].text().strip()
            final_text = grade_data['final_input'].text().strip()
            
            midterm = float(midterm_text) if midterm_text else 0.0
            final = float(final_text) if final_text else 0.0
            
            # Save grades to database in real-time
            if hasattr(self.db, 'save_student_grades'):
                self.db.save_student_grades(
                    student_id,
                    self.section['section_id'],
                    midterm,
                    final
                )
            
            # Emit signal to update dashboard
            self.grades_updated.emit()
            
            # Update semestral cell
            semestral_item = table.item(row, 4)
            remarks_item = table.item(row, 5)
            
            if semestral_item:
                # Only show semestral if at least one grade is entered
                if midterm_text or final_text:
                    semestral = round((midterm + final) / 2, 2)
                    semestral_item.setText(f"{semestral:.2f}")
                    
                    # Color code based on grade performance
                    if semestral <= 1.75:
                        semestral_item.setForeground(QColor("#27AE60"))  # Green for Excellent/Very Satisfactory
                    elif semestral <= 2.50:
                        semestral_item.setForeground(QColor("#3498DB"))  # Blue for Satisfactory
                    elif semestral <= 3.00:
                        semestral_item.setForeground(QColor("#F39C12"))  # Orange for Fairly Satisfactory/Passed
                    elif semestral <= 5.00:
                        semestral_item.setForeground(QColor("#E74C3C"))  # Red for Conditional Failure/Failed
                    else:
                        semestral_item.setForeground(QColor("#95A5A6"))  # Gray for invalid
                    
                    # Add grade interpretation as tooltip
                    interpretation = self.get_grade_interpretation(semestral)
                    semestral_item.setToolTip(interpretation)
                    
                    # Update remarks column
                    if remarks_item:
                        remarks_text = ""
                        if semestral >= 1.00 and semestral <= 1.25:
                            remarks_text = "Excellent"
                        elif semestral > 1.25 and semestral <= 1.75:
                            remarks_text = "Very Satisfactory"
                        elif semestral > 1.75 and semestral <= 2.50:
                            remarks_text = "Satisfactory"
                        elif semestral > 2.50 and semestral <= 3.00:
                            remarks_text = "Fairly Satisfactory"
                        elif semestral >= 3.00 and semestral < 4.00:
                            remarks_text = "Passed"
                        elif semestral >= 4.00 and semestral <= 5.00:
                            remarks_text = "Conditional Failure"
                        elif semestral > 5.00:
                            remarks_text = "Failed"
                        
                        remarks_item.setText(remarks_text)
                        
                        # Color code remarks
                        if remarks_text in ["Excellent", "Very Satisfactory"]:
                            remarks_item.setForeground(QColor("#27AE60"))
                        elif remarks_text == "Satisfactory":
                            remarks_item.setForeground(QColor("#3498DB"))
                        elif remarks_text in ["Fairly Satisfactory", "Passed"]:
                            remarks_item.setForeground(QColor("#F39C12"))
                        elif remarks_text in ["Conditional Failure", "Failed"]:
                            remarks_item.setForeground(QColor("#E74C3C"))
                else:
                    semestral_item.setText("")
                    semestral_item.setToolTip("")
                    semestral_item.setForeground(QColor("#95A5A6"))
                    
                    # Show "No Remarks" when grades are cleared
                    if remarks_item:
                        remarks_item.setText("No Remarks")
                        remarks_item.setForeground(QColor("#95A5A6"))
        except ValueError:
            # Invalid input, keep current value
            pass
    
    def get_grade_interpretation(self, grade):
        """Get grade interpretation based on the grading system"""
        if grade >= 1.00 and grade <= 1.25:
            return "Excellent (1.00-1.25)"
        elif grade > 1.25 and grade <= 1.50:
            return "Excellent (1.25-1.50)"
        elif grade > 1.50 and grade <= 1.75:
            return "Very Satisfactory (1.50-1.75)"
        elif grade > 1.75 and grade <= 2.00:
            return "Very Satisfactory (1.75-2.00)"
        elif grade > 2.00 and grade <= 2.25:
            return "Satisfactory (2.00-2.25)"
        elif grade > 2.25 and grade <= 2.50:
            return "Satisfactory (2.25-2.50)"
        elif grade > 2.50 and grade <= 2.75:
            return "Fairly Satisfactory (2.50-2.75)"
        elif grade > 2.75 and grade <= 3.00:
            return "Fairly Satisfactory (2.75-3.00)"
        elif grade >= 3.00 and grade <= 4.00:
            return "Passed (3.00-4.00)"
        elif grade > 4.00 and grade <= 5.00:
            return "Conditional Failure (4.0-5.0)"
        elif grade > 5.00:
            return "Failed (5.0 and below)"
        elif grade == 0:
            return "Inc - Incomplete / Drp - Officially Dropped"
        else:
            return "Invalid Grade"
    
    def delete_grade(self, student):
        """Delete/reset student grades"""
        student_name = f"{student.get('first_name', '')} {student.get('last_name', '')}"
        reply = QMessageBox.question(
            self,
            "Reset Grades",
            f"Are you sure you want to reset all grades for '{student_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            student_id = student.get('student_id')
            
            # Reset the input fields
            if student_id in self.grade_inputs:
                self.grade_inputs[student_id]['midterm_input'].clear()
                self.grade_inputs[student_id]['final_input'].clear()
            
            # Delete grades from database if method exists
            if hasattr(self.db, 'delete_student_grades'):
                success = self.db.delete_student_grades(student_id, self.section['section_id'])
                if success:
                    QMessageBox.information(self, "Success", f"Grades reset for {student_name}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to reset grades")
            else:
                QMessageBox.information(self, "Success", f"Grades reset for {student_name}")
    
    def filter_grades(self):
        """Filter grades table based on search input"""
        search_query = self.grades_search_input.text().strip() if hasattr(self, 'grades_search_input') else ""
        self.create_grades_table(search_query)

    def load_customize_view(self):
        """Load customize view with editable class fields"""
        self.clear_content_layout()
        
        # Header
        header = QLabel("Class Settings")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #222; margin-bottom: 10px;")
        self.content_layout.addWidget(header)
        
        # Create form
        form_widget = QWidget()
        form_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
        """)
        form_widget.setMaximumWidth(600)
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)
        
        # Class name field
        class_name_label = QLabel("Class name (required)")
        class_name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #222;")
        form_layout.addWidget(class_name_label)
        
        self.class_name_input = QLineEdit()
        self.class_name_input.setText(self.section.get('section_name', ''))
        self.class_name_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #DDD;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #666;
            }
        """)
        form_layout.addWidget(self.class_name_input)
        
        # Section field
        section_label = QLabel("Section")
        section_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #222;")
        form_layout.addWidget(section_label)
        
        self.section_input = QLineEdit()
        self.section_input.setText(self.section.get('section', '') or '')
        self.section_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #DDD;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #666;
            }
        """)
        form_layout.addWidget(self.section_input)
        
        # Subject field
        subject_label = QLabel("Subject")
        subject_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #222;")
        form_layout.addWidget(subject_label)
        
        self.subject_input = QLineEdit()
        self.subject_input.setText(self.section.get('subject', '') or '')
        self.subject_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #DDD;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #666;
            }
        """)
        form_layout.addWidget(self.subject_input)
        
        # Room field
        room_label = QLabel("Room")
        room_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #222;")
        form_layout.addWidget(room_label)
        
        self.room_input = QLineEdit()
        self.room_input.setText(self.section.get('room', '') or '')
        self.room_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #DDD;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #666;
            }
        """)
        form_layout.addWidget(self.room_input)
        
        # Save button
        save_btn = QPushButton("Save Changes")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedHeight(45)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_class_settings)
        form_layout.addWidget(save_btn)
        
        self.content_layout.addWidget(form_widget)
        self.content_layout.addStretch()
    
    def save_class_settings(self):
        """Save updated class settings"""
        class_name = self.class_name_input.text().strip()
        section = self.section_input.text().strip()
        subject = self.subject_input.text().strip()
        room = self.room_input.text().strip()
        
        # Validate
        if not class_name:
            QMessageBox.warning(self, "Validation Error", "Class name is required!")
            return
        
        # Update database
        success, message = self.db.update_section(
            self.section['section_id'],
            class_name,
            section,
            subject,
            room
        )
        
        if success:
            # Update local section data
            self.section['section_name'] = class_name
            self.section['section'] = section
            self.section['subject'] = subject
            self.section['room'] = room
            
            # Update the title label
            if self.class_title:
                self.class_title.setText(class_name)
            
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)

    def clear_content_layout(self):
        """Clear all widgets from content layout"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
    
    def clear_layout(self, layout):
        """Recursively clear a layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def add_student(self):
        """Add new student to the section"""
        self.show_student_dialog(None, "Add Student")
    
    def edit_student(self, student):
        """Edit student information"""
        self.show_student_dialog(student, "Edit Student")
    
    def delete_student(self, student):
        """Archive student from the section"""
        student_name = f"{student.get('first_name', '')} {student.get('last_name', '')}"
        reply = QMessageBox.question(self, "Archive Student", 
                                    f"Are you sure you want to archive '{student_name}'?\nYou can restore them later from the Archive.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success, message = self.db.archive_student(student['student_id'], self.section['section_id'])
            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_student_table()
                # Refresh My Classes page to update student count on cards
                if hasattr(self, 'main_window') and hasattr(self.main_window, 'my_classes_page'):
                    self.main_window.my_classes_page.load_sections()
                # Refresh dashboard statistics
                if hasattr(self, 'main_window') and hasattr(self.main_window, 'dashboard_page'):
                    self.main_window.dashboard_page.refresh_statistics()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def view_student_archive(self):
        """View archived students for this section"""
        self.show_student_archive_dialog()
    
    def show_student_dialog(self, student, title):
        """Show add/edit student dialog"""
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
            ("student_id", "Student ID (Required)", "e.g., 0124-1579"),
            ("full_name", "Full Name (Required)", "Enter full name"),
            ("age", "Age (Required)", "e.g., 20"),
            ("email", "Email (Required)", "student@example.com"),
            ("phone", "Phone Number (11 digits)", "e.g., 09123456789"),
            ("address", "Address", "Enter complete address"),
        ]
        
        for field_key, label_text, placeholder in field_configs:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333;")
            layout.addWidget(label)
            
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            if student:
                if field_key == 'full_name':
                    # Combine first_name and last_name for editing
                    full_name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
                    field.setText(full_name)
                else:
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
            # Collect and validate data
            student_id = fields['student_id'].text().strip()
            full_name = fields['full_name'].text().strip()
            age = fields['age'].text().strip()
            email = fields['email'].text().strip()
            phone = fields['phone'].text().strip()
            address = fields['address'].text().strip()
            
            # Validation
            if not student_id:
                QMessageBox.warning(dialog, "Validation Error", "Student ID is required!")
                return
            if not full_name:
                QMessageBox.warning(dialog, "Validation Error", "Full Name is required!")
                return
            if not age:
                QMessageBox.warning(dialog, "Validation Error", "Age is required!")
                return
            if not age.isdigit():
                QMessageBox.warning(dialog, "Validation Error", "Age must be a number!")
                return
            if not email:
                QMessageBox.warning(dialog, "Validation Error", "Email is required!")
                return
            if '@' not in email or '.' not in email:
                QMessageBox.warning(dialog, "Validation Error", "Please enter a valid email address!")
                return
            if phone and (not phone.isdigit() or len(phone) != 11):
                QMessageBox.warning(dialog, "Validation Error", "Phone number must be exactly 11 digits!")
                return
            
            # Split full name into first and last name
            name_parts = full_name.split(maxsplit=1)
            first_name = name_parts[0] if len(name_parts) > 0 else full_name
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            new_student = {
                'student_id': student_id,
                'section_id': self.section['section_id'],
                'first_name': first_name,
                'last_name': last_name,
                'age': int(age),
                'email': email,
                'phone': phone if phone else None,
                'address': address if address else None
            }
            
            # Save or update
            if student:
                success, message = self.db.update_student(student['student_id'], new_student)
            else:
                success, message = self.db.add_student(new_student)
            
            if success:
                QMessageBox.information(dialog, "Success", message)
                dialog.accept()
                self.refresh_student_table()
                # Refresh My Classes page to update student count on cards
                if hasattr(self, 'main_window') and hasattr(self.main_window, 'my_classes_page'):
                    self.main_window.my_classes_page.load_sections()
                # Refresh dashboard statistics
                if hasattr(self, 'main_window') and hasattr(self.main_window, 'dashboard_page'):
                    self.main_window.dashboard_page.refresh_statistics()
            else:
                QMessageBox.warning(dialog, "Error", message)
        
        save_btn.clicked.connect(save_student)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        main_layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def show_student_archive_dialog(self):
        """Show archived students for this section"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Archived Students - {self.section['section_name']}")
        dialog.resize(1200, 700)
        dialog.setStyleSheet("background-color: #E7E7DF;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel(f"📦 Archived Students - {self.section['section_name']}")
        header.setStyleSheet("font-size: 24px; font-weight: 700; color: #222;")
        layout.addWidget(header)
        
        # Get archived students
        all_students = self.db.get_students(self.section['section_id'], include_archived=True)
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
            
            # Set column widths
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
            table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Fixed)
            table.setColumnWidth(8, 110)
            table.setColumnWidth(9, 110)
            
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
                restore_btn = QPushButton("Restore")
                restore_btn.setCursor(Qt.PointingHandCursor)
                restore_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border-radius: 6px;
                        padding: 5px 10px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                restore_btn.clicked.connect(lambda checked, s=student, d=dialog: self.restore_student(s, d))
                table.setCellWidget(row, 8, restore_btn)
                
                # Delete permanently button
                delete_btn = QPushButton("Delete")
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        border-radius: 6px;
                        padding: 5px 10px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #da190b;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, s=student, d=dialog: self.delete_student_permanently(s, d))
                table.setCellWidget(row, 9, delete_btn)
                
                table.setRowHeight(row, 50)
            
            layout.addWidget(table)
        else:
            no_archive = QLabel("No archived students in this section")
            no_archive.setStyleSheet("font-size: 16px; color: #999;")
            layout.addWidget(no_archive)
            layout.addStretch()
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
    
    def restore_student(self, student, parent_dialog):
        """Restore archived student"""
        student_name = f"{student['first_name']} {student['last_name']}"
        reply = QMessageBox.question(
            parent_dialog, 'Restore Student',
            f"Restore student '{student_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.db.restore_student(student['student_id'], self.section['section_id'])
            if success:
                QMessageBox.information(parent_dialog, "Success", message)
                parent_dialog.accept()
                self.refresh_student_table()
                # Refresh My Classes page to update student count on cards
                if hasattr(self, 'main_window') and hasattr(self.main_window, 'my_classes_page'):
                    self.main_window.my_classes_page.load_sections()
                # Refresh dashboard statistics
                if hasattr(self, 'main_window') and hasattr(self.main_window, 'dashboard_page'):
                    self.main_window.dashboard_page.refresh_statistics()
            else:
                QMessageBox.warning(parent_dialog, "Error", message)
    
    def delete_student_permanently(self, student, parent_dialog):
        """Permanently delete student"""
        student_name = f"{student['first_name']} {student['last_name']}"
        reply = QMessageBox.question(
            parent_dialog, 'Permanently Delete',
            f"PERMANENTLY delete student '{student_name}'?\nThis action CANNOT be undone!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.db.delete_student_permanently(student['student_id'], self.section['section_id'])
            if success:
                QMessageBox.information(parent_dialog, "Success", message)
                parent_dialog.accept()
                # Refresh My Classes page to update student count on cards
                if hasattr(self, 'main_window') and hasattr(self.main_window, 'my_classes_page'):
                    self.main_window.my_classes_page.load_sections()
                # Refresh dashboard statistics
                if hasattr(self, 'main_window') and hasattr(self.main_window, 'dashboard_page'):
                    self.main_window.dashboard_page.refresh_statistics()
            else:
                QMessageBox.warning(parent_dialog, "Error", message)

    def go_back(self):
        """Go back to My Classes page"""
        if hasattr(self, 'main_window'):
            self.main_window.switch_page("My Classes")
    
    def update_title_border(self, card_color):
        """Update the border color of the class title"""
        self.card_color = card_color
        if self.class_title:
            self.class_title.setStyleSheet(f"""
                font-size: 28px; 
                font-weight: 700; 
                color: #222;
                border-left: 5px solid {self.card_color};
                padding-left: 15px;
            """)
