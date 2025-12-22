from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from datetime import datetime
sys.path.append('..')
from utils.database import DatabaseConnection


class DashboardPage(QWidget):
    def __init__(self, username, user_id=1):
        super().__init__()
        self.username = username
        self.user_id = user_id
        self.db = DatabaseConnection()
        self.stat_value_labels = {}  # Store references to value labels for updates
        self.init_ui()
        
        # Set up timer for periodic refresh (every 5 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_outstanding_students)
        self.refresh_timer.start(5000)  # 5000ms = 5 seconds

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 0, 35, 20)
        layout.setSpacing(20)

        # Dashboard title
        dashboard_title = QLabel("Dashboard")
        dashboard_title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        dashboard_title.setContentsMargins(0, 10, 0, 5)
        layout.addWidget(dashboard_title, alignment=Qt.AlignLeft)

        # Welcome Card
        welcome_card = self.create_welcome_card()
        layout.addWidget(welcome_card)

        # Main content area - two columns
        main_content = QHBoxLayout()
        main_content.setSpacing(20)
        
        # Left side - Statistics Cards (in a grid)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(20)
        
        self.stats_grid = self.create_statistics_grid()
        left_layout.addWidget(self.stats_grid)
        
        # Right side - Outstanding Students
        self.outstanding_container = self.create_outstanding_students_section()
        
        # Add both sides to main content (60-40 split)
        main_content.addWidget(left_container, 60)
        main_content.addWidget(self.outstanding_container, 40)
        
        layout.addLayout(main_content, 1)

    def create_welcome_card(self):
        welcome_card = QFrame()
        welcome_card.setStyleSheet("""
            QFrame {
                background-color: #E6EFFA;
                border-radius: 12px;
                padding: 40px;
            }
        """)
        welcome_card.setMinimumHeight(300)
        welcome_card.setMaximumHeight(400)
        welcome_card.setMinimumWidth(850)

        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        welcome_layout.setSpacing(1)
        welcome_layout.setAlignment(Qt.AlignCenter)

        welcome_title = QLabel(f"Welcome back, {self.username.capitalize()}!")
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_title.setStyleSheet("font-size: 50px; font-weight: bold; color: #333;")
        
        welcome_sub = QLabel("You need to manage your students and classes.")
        welcome_sub.setAlignment(Qt.AlignCenter)
        welcome_sub.setStyleSheet("font-size: 28px; color: #555;")

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_sub)

        return welcome_card

    def create_statistics_grid(self):
        """Create a 2x2 grid of statistics cards"""
        container = QWidget()
        grid_layout = QGridLayout(container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(15)

        # Get data from database
        sections = list(self.db.get_sections(self.user_id, include_archived=False))
        total_classes = len(sections)
        
        # Calculate total students across all classes
        total_students = 0
        for section in sections:
            students = list(self.db.get_students(section['section_id'], include_archived=False))
            total_students += len(students)
        
        # Get today's classes from schedule
        todays_classes = self.get_todays_classes_count()
        
        # Total resources from database
        total_resources = len(list(self.db.get_resources(self.user_id)))

        # Create stat cards data
        stat_cards_data = [
            ('Total Classes', str(total_classes), 'Active', '📚', '#4A90E2'),
            ('Total Students', str(total_students), 'Enrolled', '👥', '#9B59B6'),
            ("Today's Classes", str(todays_classes), 'Scheduled', '📅', '#5DADE2'),
            ('Total Resources', str(total_resources), 'Uploaded', '📁', '#F39C12')
        ]

        # Add cards to grid (2x2)
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for (title, value, subtitle, icon, color), pos in zip(stat_cards_data, positions):
            card = self.create_stat_card(title, value, subtitle, icon, color)
            grid_layout.addWidget(card, pos[0], pos[1])

        return container

    def create_outstanding_students_section(self):
        """Create outstanding students section with top performers"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("⭐ Outstanding Students")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #222;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Info icon
        info_label = QLabel("ℹ️")
        info_label.setStyleSheet("font-size: 14px; color: #999;")
        info_label.setToolTip("Based on grades only")
        header_layout.addWidget(info_label)
        
        layout.addLayout(header_layout)

        # Description
        desc = QLabel("Top performers based on grades")
        desc.setStyleSheet("font-size: 12px; color: #777; margin-bottom: 10px;")
        layout.addWidget(desc)

        # Scroll area for students list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #F5F5F5;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                border-radius: 4px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.students_list_layout = QVBoxLayout(scroll_content)
        self.students_list_layout.setContentsMargins(0, 0, 0, 0)
        self.students_list_layout.setSpacing(10)
        self.students_list_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Load outstanding students
        self.refresh_outstanding_students()

        return container

    def refresh_outstanding_students(self):
        """Refresh the outstanding students list - can be called externally"""
        if not hasattr(self, 'students_list_layout'):
            return
            
        # Clear current list
        while self.students_list_layout.count():
            item = self.students_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get all students with their grades and attendance
        outstanding_students = self.get_top_students()

        if outstanding_students:
            for rank, student_data in enumerate(outstanding_students[:10], 1):  # Top 10
                student_card = self.create_student_card(rank, student_data)
                self.students_list_layout.addWidget(student_card)
        else:
            no_data = QLabel("No student data available yet.\nGrades and attendance will appear here.")
            no_data.setStyleSheet("font-size: 13px; color: #999; padding: 20px;")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setWordWrap(True)
            self.students_list_layout.addWidget(no_data)

    def get_top_students(self):
        """Get top students based on semestral grades from grades tab"""
        sections = list(self.db.get_sections(self.user_id, include_archived=False))
        all_students = []

        for section in sections:
            students = list(self.db.get_students(section['section_id'], include_archived=False))
            
            for student in students:
                student_id = student['student_id']
                
                # Get grades for this student (midterm and final)
                grades = self.db.get_student_grades(student_id, section['section_id']) if hasattr(self.db, 'get_student_grades') else {}
                
                if grades:
                    midterm_val = grades.get('midterm')
                    final_val = grades.get('final')
                    
                    # Only calculate if both grades exist and are greater than 0
                    if midterm_val is not None and final_val is not None:
                        midterm = float(midterm_val)
                        final = float(final_val)
                        
                        if midterm > 0 and final > 0:
                            # Calculate average score (0-100)
                            avg_score = (midterm + final) / 2
                            # Convert to 1.00-5.00 grading scale
                            semestral = self.convert_score_to_grade(avg_score)
                            
                            # Calculate attendance rate for display
                            attendance_rate = self.calculate_attendance_rate(student_id, section['section_id'])
                            
                            # Lower grade number is better (1.00 is best, 5.00 is worst)
                            # Sort by semestral grade (ascending - lower is better)
                            all_students.append({
                                'student_id': student_id,
                                'name': f"{student.get('first_name', '')} {student.get('last_name', '')}".strip(),
                                'section': section['section_name'],
                                'semestral': semestral,
                                'attendance': attendance_rate,
                                'score': semestral  # Use semestral grade directly
                            })

        # Sort by semestral grade (ascending - lower grade is better)
        all_students.sort(key=lambda x: x['score'])
        
        return all_students

    def convert_score_to_grade(self, score):
        """Convert 0-100 score to 1.00-5.00 grading scale based on the grading system"""
        if score >= 99:
            return 1.00
        elif score >= 96:
            return 1.25
        elif score >= 93:
            return 1.50
        elif score >= 90:
            return 1.75
        elif score >= 87:
            return 2.00
        elif score >= 84:
            return 2.25
        elif score >= 81:
            return 2.50
        elif score >= 78:
            return 2.75
        elif score >= 75:
            return 3.00
        elif score >= 70:
            return 4.00
        elif score >= 69:
            return 5.00
        else:
            return 5.00  # Failed

    def calculate_attendance_rate(self, student_id, section_id):
        """Calculate attendance rate for a student"""
        try:
            # Get all attendance records for the section
            attendance_records = self.db.get_attendance_records(section_id)
            
            if not attendance_records:
                return 0

            present_count = 0
            total_count = 0

            for record in attendance_records:
                attendance_data = record.get('attendance_data', {})
                if str(student_id) in attendance_data:
                    total_count += 1
                    if attendance_data[str(student_id)].get('status') == 'present':
                        present_count += 1

            if total_count == 0:
                return 0

            return (present_count / total_count) * 100
        except:
            return 0

    def create_student_card(self, rank, student_data):
        """Create a card for an outstanding student"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-radius: 8px;
                border: 1px solid #E9ECEF;
            }
            QFrame:hover {
                background-color: #E6EFFA;
                border: 1px solid #4A90E2;
            }
        """)
        card.setMinimumHeight(70)
        card.setMaximumHeight(80)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # Rank badge
        rank_label = QLabel(str(rank))
        rank_label.setFixedSize(35, 35)
        rank_label.setAlignment(Qt.AlignCenter)
        
        # Different colors for top 3
        if rank == 1:
            rank_style = "background-color: #FFD700; color: white; font-weight: 700;"
        elif rank == 2:
            rank_style = "background-color: #C0C0C0; color: white; font-weight: 700;"
        elif rank == 3:
            rank_style = "background-color: #CD7F32; color: white; font-weight: 700;"
        else:
            rank_style = "background-color: #E0E0E0; color: #666; font-weight: 600;"
        
        rank_label.setStyleSheet(f"{rank_style} border-radius: 17px; font-size: 14px;")
        layout.addWidget(rank_label)

        # Student info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)

        name_label = QLabel(student_data['name'])
        name_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #222;")
        info_layout.addWidget(name_label)

        section_label = QLabel(student_data['section'])
        section_label.setStyleSheet("font-size: 11px; color: #666;")
        info_layout.addWidget(section_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # Performance metrics
        metrics_layout = QVBoxLayout()
        metrics_layout.setSpacing(2)
        metrics_layout.setAlignment(Qt.AlignRight)

        # Semestral Grade (from grades tab)
        grade_text = f"{student_data['semestral']:.2f}"
        grade_label = QLabel(f"📊 {grade_text}")
        grade_label.setStyleSheet("font-size: 12px; color: #4A90E2; font-weight: 600;")
        metrics_layout.addWidget(grade_label, alignment=Qt.AlignRight)

        layout.addLayout(metrics_layout)

        return card

    def refresh_statistics(self):
        """Refresh statistics data in real-time"""
        # Get updated data from database
        sections = list(self.db.get_sections(self.user_id, include_archived=False))
        total_classes = len(sections)
        
        # Calculate total students across all classes
        total_students = 0
        for section in sections:
            students = list(self.db.get_students(section['section_id'], include_archived=False))
            total_students += len(students)
        
        # Get total resources
        total_resources = len(list(self.db.get_resources(self.user_id)))
        
        # Update the value labels
        if 'Total Classes' in self.stat_value_labels:
            self.stat_value_labels['Total Classes'].setText(str(total_classes))
        
        if 'Total Students' in self.stat_value_labels:
            self.stat_value_labels['Total Students'].setText(str(total_students))
        
        if 'Total Resources' in self.stat_value_labels:
            self.stat_value_labels['Total Resources'].setText(str(total_resources))
        
        # Refresh outstanding students list
        if hasattr(self, 'students_list_layout'):
            self.refresh_outstanding_students()

    def create_stat_card(self, title, value, subtitle, icon, icon_color):
        """Create a single statistics card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
            }
        """)
        card.setMinimumHeight(220)
        card.setMaximumHeight(280)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 20, 25, 20)
        card_layout.setSpacing(5)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 20px; color: #666; font-weight: 600;")
        card_layout.addWidget(title_label)

        # Value and icon row
        value_layout = QHBoxLayout()
        value_layout.setSpacing(10)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 48px; font-weight: 700; color: #222;")
        value_layout.addWidget(value_label)
        
        # Store reference to value label for updates
        self.stat_value_labels[title] = value_label

        value_layout.addStretch()

        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 38px; color: {icon_color};")
        value_layout.addWidget(icon_label, alignment=Qt.AlignTop)

        card_layout.addLayout(value_layout)
        card_layout.addSpacing(5)

        # Subtitle
        subtitle_label = QLabel(f"● {subtitle}")
        subtitle_label.setStyleSheet(f"font-size: 20px; color: {icon_color}; font-weight: 600;")
        card_layout.addWidget(subtitle_label)

        card_layout.addStretch()

        return card
    
    def get_todays_classes_count(self):
        """Get the count of classes scheduled for today."""
        schedules = self.db.get_schedules(self.user_id)
        
        # Get today's day name
        today = datetime.now()
        today_day_name = today.strftime("%A")
        
        # Count schedules for today
        todays_schedules = [
            sched for sched in schedules
            if sched['day'] == today_day_name
        ]
        
        return len(todays_schedules)
