from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import datetime
import random
import sys
sys.path.append('..')
from utils.database import DatabaseConnection


class CreateScheduleDialog(QDialog):
    """Dialog window for adding a new class schedule."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Schedule")
        self.setWindowIcon(QIcon("image/system.png"))
        self.setFixedSize(500, 620)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(15)

        # Dialog Title
        title = QLabel("Add Schedule")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #1A1A1A; background-color: transparent;")
        layout.addWidget(title)
        
        layout.addSpacing(10)

        # Subject
        subject_label = QLabel("Subject (required)")
        subject_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1A1A1A; background-color: transparent;")
        layout.addWidget(subject_label)
        
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter subject name")
        self.subject_input.setFixedHeight(45)
        self.subject_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                font-size: 14px;
                color: #1A1A1A;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #9CA3AF;
            }
        """)
        layout.addWidget(self.subject_input)

        # Section
        section_label = QLabel("Section")
        section_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1A1A1A; background-color: transparent;")
        layout.addWidget(section_label)
        
        self.section_input = QLineEdit()
        self.section_input.setPlaceholderText("Enter section")
        self.section_input.setFixedHeight(45)
        self.section_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                font-size: 14px;
                color: #1A1A1A;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #9CA3AF;
            }
        """)
        layout.addWidget(self.section_input)

        # Day
        day_label = QLabel("Day")
        day_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1A1A1A; background-color: transparent;")
        layout.addWidget(day_label)
        
        self.day_input = QComboBox()
        self.day_input.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        self.day_input.setFixedHeight(45)
        self.day_input.setStyleSheet("""
            QComboBox {
                padding: 10px 14px;
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                font-size: 14px;
                color: #1A1A1A;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #3B82F6;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6B7280;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background-color: white;
                selection-background-color: #3B82F6;
                selection-color: white;
                padding: 4px;
            }
        """)
        layout.addWidget(self.day_input)

        # Time
        time_label = QLabel("Time")
        time_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1A1A1A; background-color: transparent;")
        layout.addWidget(time_label)
        
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("e.g. 7:00 - 10:00")
        self.time_input.setFixedHeight(45)
        self.time_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                font-size: 14px;
                color: #1A1A1A;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #9CA3AF;
            }
        """)
        layout.addWidget(self.time_input)

        # Room
        room_label = QLabel("Room")
        room_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1A1A1A; background-color: transparent;")
        layout.addWidget(room_label)
        
        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("e.g. 101")
        self.room_input.setFixedHeight(45)
        self.room_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                font-size: 14px;
                color: #1A1A1A;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #9CA3AF;
            }
        """)
        layout.addWidget(self.room_input)

        layout.addSpacing(15)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedSize(100, 42)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #3B82F6;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F3F4F6;
            }
            QPushButton:pressed {
                background-color: #E5E7EB;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        add_btn = QPushButton("Create")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedSize(100, 42)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        add_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        """Returns the data entered by the user."""
        return {
            "subject": self.subject_input.text().strip(),
            "section": self.section_input.text().strip(),
            "day": self.day_input.currentText(),
            "time": self.time_input.text().strip(),
            "room": self.room_input.text().strip()
        }


class DeleteScheduleDialog(QDialog):
    """Dialog window for deleting a schedule."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Schedule")
        self.setWindowIcon(QIcon("image/system.png"))
        self.setFixedSize(500, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(15)

        # Dialog Title
        title = QLabel("Delete Schedule")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #1A1A1A; background-color: transparent;")
        layout.addWidget(title)
        
        # Warning message
        warning = QLabel("Enter the subject, section, and day to delete the schedule.")
        warning.setStyleSheet("font-size: 13px; color: #666; background-color: transparent;")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        
        layout.addSpacing(10)

        # Subject
        subject_label = QLabel("Subject (required)")
        subject_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1A1A1A; background-color: transparent;")
        layout.addWidget(subject_label)
        
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter subject name")
        self.subject_input.setFixedHeight(45)
        self.subject_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                font-size: 14px;
                color: #1A1A1A;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #EF4444;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #9CA3AF;
            }
        """)
        layout.addWidget(self.subject_input)

        # Section
        section_label = QLabel("Section (required)")
        section_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1A1A1A; background-color: transparent;")
        layout.addWidget(section_label)
        
        self.section_input = QLineEdit()
        self.section_input.setPlaceholderText("Enter section")
        self.section_input.setFixedHeight(45)
        self.section_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                font-size: 14px;
                color: #1A1A1A;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #EF4444;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #9CA3AF;
            }
        """)
        layout.addWidget(self.section_input)

        # Day
        day_label = QLabel("Day (required)")
        day_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1A1A1A; background-color: transparent;")
        layout.addWidget(day_label)
        
        self.day_input = QComboBox()
        self.day_input.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        self.day_input.setFixedHeight(45)
        self.day_input.setStyleSheet("""
            QComboBox {
                padding: 10px 14px;
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                font-size: 14px;
                color: #1A1A1A;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #EF4444;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6B7280;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background-color: white;
                selection-background-color: #EF4444;
                selection-color: white;
                padding: 4px;
            }
        """)
        layout.addWidget(self.day_input)

        layout.addSpacing(15)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedSize(100, 42)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #666;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F3F4F6;
            }
            QPushButton:pressed {
                background-color: #E5E7EB;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedSize(100, 42)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
        """)
        delete_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        """Returns the data entered by the user."""
        return {
            "subject": self.subject_input.text().strip(),
            "section": self.section_input.text().strip(),
            "day": self.day_input.currentText()
        }



class SchedulePage(QWidget):
    def __init__(self, user_id=1):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseConnection()
        self.schedules = []
        self.load_schedules()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(35, 20, 35, 20)
        main_layout.setSpacing(20)
        
        # Left side - Schedule Grid
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Schedule")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        delete_btn = QPushButton("  Delete Schedule")
        delete_btn.setIcon(QIcon("image/bin.png"))
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedHeight(45)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #4C9AFF;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3A7FD5;
            }
        """)
        delete_btn.clicked.connect(self.delete_schedule)
        header_layout.addWidget(delete_btn)
        
        create_btn = QPushButton("+ Create Schedule")
        create_btn.setCursor(Qt.PointingHandCursor)
        create_btn.setFixedHeight(45)
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #4C9AFF;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3A7FD5;
            }
        """)
        create_btn.clicked.connect(self.create_schedule)
        header_layout.addWidget(create_btn)
        
        left_layout.addLayout(header_layout)
        
        # Schedule Grid Container
        self.schedule_card = QWidget()
        self.schedule_card.setStyleSheet("""
            QWidget {
                background-color: #797979;
                border-radius: 20px;
            }
        """)
        
        self.refresh_schedule_grid()
        left_layout.addWidget(self.schedule_card)
        
        # Right side - Today's Schedule Panel
        right_widget = QWidget()
        right_widget.setFixedWidth(350)
        right_widget.setStyleSheet("""
            QWidget {
                background-color: #F8F8F8;
                border-radius: 20px;
            }
        """)
        
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(25, 25, 25, 25)
        right_layout.setSpacing(15)
        
        # Panel Header
        panel_title = QLabel("Today Schedule")
        panel_title.setStyleSheet("font-size: 22px; font-weight: 700; color: #222;")
        right_layout.addWidget(panel_title)
        
        # Date
        self.date_label = QLabel(self.get_today_date_text())
        self.date_label.setStyleSheet("font-size: 14px; color: #666; font-weight: 600;")
        right_layout.addWidget(self.date_label)
        
        # Scroll area for schedule blocks
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #E0E0E0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #B0B0B0;
                border-radius: 4px;
            }
        """)
        
        self.schedule_blocks_widget = QWidget()
        self.schedule_blocks_layout = QVBoxLayout(self.schedule_blocks_widget)
        self.schedule_blocks_layout.setContentsMargins(0, 10, 0, 0)
        self.schedule_blocks_layout.setSpacing(15)
        self.schedule_blocks_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.schedule_blocks_widget)
        right_layout.addWidget(scroll)
        
        self.refresh_today_panel()
        
        # Add both sides to main layout
        main_layout.addWidget(left_widget, 3)
        main_layout.addWidget(right_widget, 1)

    def times_overlap(self, time1, time2):
        """Check if two time ranges overlap"""
        try:
            # Parse time ranges like "7:00 - 7:30" or "7:00-7:30"
            def parse_time_range(time_str):
                # Remove spaces and split by dash
                time_str = time_str.replace(' ', '')
                parts = time_str.split('-')
                if len(parts) != 2:
                    return None, None
                
                # Parse start and end times
                start_parts = parts[0].split(':')
                end_parts = parts[1].split(':')
                
                if len(start_parts) != 2 or len(end_parts) != 2:
                    return None, None
                
                start_hour = int(start_parts[0])
                start_min = int(start_parts[1])
                end_hour = int(end_parts[0])
                end_min = int(end_parts[1])
                
                # Convert to minutes since midnight
                start_total = start_hour * 60 + start_min
                end_total = end_hour * 60 + end_min
                
                return start_total, end_total
            
            start1, end1 = parse_time_range(time1)
            start2, end2 = parse_time_range(time2)
            
            if start1 is None or start2 is None:
                return False
            
            # Check for overlap: times overlap if one starts before the other ends
            return (start1 < end2 and end1 > start2)
        except:
            return False

    def load_schedules(self):
        """Load schedules from database."""
        schedules_data = self.db.get_schedules(self.user_id)
        self.schedules = []
        for sched in schedules_data:
            self.schedules.append({
                'schedule_id': sched['schedule_id'],
                'subject': sched['subject'],
                'section': sched['section'] or '',
                'day': sched['day'],
                'time': sched['time'],
                'room': sched['room'] or '',
                'color': sched['color'] or '#F0C7CF'
            })
    
    def get_today_date_text(self):
        """Returns today's date and day."""
        today = datetime.datetime.now()
        date_str = today.strftime("%B %d")
        day_str = today.strftime("%A")
        return f"{date_str}\n{day_str}"

    def get_today_schedules(self):
        """Filters schedules to return only those matching today."""
        today = datetime.datetime.now()
        today_day_name = today.strftime("%A")
        
        today_list = [
            sched for sched in self.schedules
            if sched['day'] == today_day_name
        ]
        
        # Sort schedules by time
        try:
            today_list.sort(key=lambda x: datetime.datetime.strptime(x['time'].split(' - ')[0].strip(), '%H:%M'))
        except ValueError:
            today_list.sort(key=lambda x: x['time'])
        
        return today_list

    def create_schedule(self):
        """Open dialog to create a new schedule."""
        dialog = CreateScheduleDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not all(data.values()):
                QMessageBox.warning(self, "Input Error", "All fields must be filled out.")
                return
            
            # Check for duplicate schedule
            duplicate_found = False
            for sched in self.schedules:
                if (sched['subject'].lower() == data['subject'].lower() and
                    sched['section'].lower() == data['section'].lower() and
                    sched['day'].lower() == data['day'].lower() and
                    sched['time'].lower() == data['time'].lower() and
                    sched['room'].lower() == data['room'].lower()):
                    duplicate_found = True
                    break
            
            if duplicate_found:
                QMessageBox.warning(
                    self, 
                    "Duplicate Schedule", 
                    f"This schedule already exists:\n\n{data['subject']} ({data['section']})\n{data['day']} {data['time']}\nRoom {data['room']}\n\nPlease modify the schedule details."
                )
                return
            
            # Check for time overlap on the same day
            for sched in self.schedules:
                if sched['day'].lower() == data['day'].lower():
                    # Check if times overlap
                    if self.times_overlap(sched['time'], data['time']):
                        QMessageBox.warning(
                            self,
                            "Schedule Conflict",
                            f"Time conflict detected!\n\nExisting schedule:\n{sched['subject']} ({sched['section']})\n{sched['day']} {sched['time']}\nRoom {sched['room']}\n\nNew schedule:\n{data['subject']} ({data['section']})\n{data['day']} {data['time']}\nRoom {data['room']}\n\nPlease choose a different time slot."
                        )
                        return
            
            # Assign random color
            colors = ["#F0C7CF", "#A3C7D6", "#C9919E", "#D5D0D5", "#F7D08A", "#B5EAD7", "#FFDAC1"]
            data["color"] = random.choice(colors)
            
            # Save to database
            success = self.db.add_schedule(
                self.user_id,
                data['subject'],
                data['section'],
                data['day'],
                data['time'],
                data['room'],
                data['color']
            )
            
            if success:
                # Reload schedules from database
                self.load_schedules()
                
                # Refresh both views
                self.refresh_schedule_grid()
                self.refresh_today_panel()
                
                QMessageBox.information(self, "Success", f"Schedule added: {data['subject']} ({data['section']}) on {data['day']}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save schedule to database.")

    def delete_schedule(self):
        """Open dialog to delete a schedule."""
        dialog = DeleteScheduleDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not data['subject'] or not data['section'] or not data['day']:
                QMessageBox.warning(self, "Input Error", "Subject, section, and day must be filled out.")
                return
            
            # Find matching schedule(s) in the database
            matching_schedules = [
                sched for sched in self.schedules
                if sched['subject'].lower() == data['subject'].lower() and 
                   sched['section'].lower() == data['section'].lower() and
                   sched['day'].lower() == data['day'].lower()
            ]
            
            if not matching_schedules:
                QMessageBox.warning(
                    self, 
                    "Not Found", 
                    f"No schedule found with:\nSubject: {data['subject']}\nSection: {data['section']}\nDay: {data['day']}"
                )
                return
            
            # Confirm deletion
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Found {len(matching_schedules)} schedule(s) matching:\nSubject: {data['subject']}\nSection: {data['section']}\nDay: {data['day']}\n\nDelete all matching schedules?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                deleted_count = 0
                for sched in matching_schedules:
                    success = self.db.delete_schedule(sched['schedule_id'])
                    if success:
                        deleted_count += 1
                
                if deleted_count > 0:
                    # Reload schedules from database
                    self.load_schedules()
                    
                    # Refresh both views
                    self.refresh_schedule_grid()
                    self.refresh_today_panel()
                    
                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Deleted {deleted_count} schedule(s)"
                    )
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete schedules from database.")

    def refresh_schedule_grid(self):
        """Refresh the schedule grid."""
        # Clear old layout
        if self.schedule_card.layout():
            QWidget().setLayout(self.schedule_card.layout())
        
        card_layout = QVBoxLayout(self.schedule_card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(15)
        
        # Create grid
        grid = QGridLayout()
        grid.setSpacing(1)
        
        days = ["PERIOD", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
        periods = [
            "7:00 - 7:30", "7:30 - 8:00", "8:00 - 8:30", "8:30 - 9:00", "9:00 - 9:30", "9:30 - 10:00",
            "10:00 - 10:30", "10:30 - 11:00", "11:00 - 11:30", "11:30 - 12:00", "12:00 - 12:30",
            "12:30 - 1:00", "1:00 - 1:30", "1:30 - 2:00", "2:00 - 2:30", "2:30 - 3:00",
            "3:00 - 3:30", "3:30 - 4:00", "4:00 - 4:30", "4:30 - 5:00"
        ]
        
        # Header row
        for col, day in enumerate(days):
            header = QLabel(day)
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet("""
                background-color: #6A6A6A;
                color: white;
                font-weight: 700;
                font-size: 12px;
                padding: 10px;
                border: none;
            """)
            grid.addWidget(header, 0, col)
        
        # Create a dictionary to store cells by position
        cells = {}
        
        # Period rows with empty cells
        for row, period in enumerate(periods):
            period_label = QLabel(period)
            period_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            period_label.setStyleSheet("""
                background-color: #6A6A6A;
                color: white;
                font-size: 14px;
                padding: 8px;
                border: none;
            """)
            grid.addWidget(period_label, row + 1, 0)
            
            # Empty cells
            for col in range(1, len(days)):
                cell = QLabel()
                cell.setMinimumHeight(35)
                cell.setStyleSheet("background-color: #888888; border: none;")
                grid.addWidget(cell, row + 1, col)
                cells[(row, col)] = cell
        
        # Day name to column mapping
        day_map = {
            "MONDAY": 1, "TUESDAY": 2, "WEDNESDAY": 3, 
            "THURSDAY": 4, "FRIDAY": 5, "SATURDAY": 6
        }
        
        # Place schedules in the grid
        for sched in self.schedules:
            day_upper = sched['day'].upper()
            if day_upper not in day_map:
                continue
            
            col = day_map[day_upper]
            time_range = sched['time']
            
            # Parse time range (e.g., "7:00 - 8:30" or "7:00-8:30")
            try:
                # Handle both "7:00 - 10:00" and "7:00-10:00" formats
                if ' - ' in time_range:
                    start_time, end_time = time_range.split(' - ')
                elif '-' in time_range:
                    start_time, end_time = time_range.split('-')
                else:
                    continue
                    
                start_time = start_time.strip()
                end_time = end_time.strip()
                
                # Find matching period indices
                start_row = None
                end_row = None
                
                for idx, period in enumerate(periods):
                    period_start, period_end = period.split(' - ')
                    period_start = period_start.strip()
                    period_end = period_end.strip()
                    
                    # Match start time with period start
                    if period_start == start_time or period_start.startswith(start_time):
                        start_row = idx
                    # Match end time with period end
                    if period_end == end_time or period_end.startswith(end_time):
                        end_row = idx
                
                # If exact match not found, try to find the closest match
                if start_row is None or end_row is None:
                    # Convert times to minutes for comparison
                    try:
                        start_hour, start_min = map(int, start_time.split(':'))
                        end_hour, end_min = map(int, end_time.split(':'))
                        start_minutes = start_hour * 60 + start_min
                        end_minutes = end_hour * 60 + end_min
                        
                        for idx, period in enumerate(periods):
                            period_start, period_end = period.split(' - ')
                            p_start_hour, p_start_min = map(int, period_start.strip().split(':'))
                            p_end_hour, p_end_min = map(int, period_end.strip().split(':'))
                            p_start_minutes = p_start_hour * 60 + p_start_min
                            p_end_minutes = p_end_hour * 60 + p_end_min
                            
                            if start_row is None and p_start_minutes == start_minutes:
                                start_row = idx
                            if end_row is None and p_end_minutes == end_minutes:
                                end_row = idx
                    except (ValueError, AttributeError):
                        pass
                
                if start_row is not None and end_row is not None and end_row >= start_row:
                    # Calculate row span
                    row_span = end_row - start_row + 1
                    
                    # Remove the cells that will be covered
                    for r in range(start_row, end_row + 1):
                        if (r, col) in cells:
                            grid.removeWidget(cells[(r, col)])
                            cells[(r, col)].deleteLater()
                            del cells[(r, col)]
                    
                    # Create schedule block
                    block = QWidget()
                    block.setStyleSheet(f"""
                        QWidget {{
                            background-color: {sched['color']};
                            border-radius: 12px;
                            padding: 12px;
                        }}
                    """)
                    
                    block_layout = QVBoxLayout(block)
                    block_layout.setContentsMargins(12, 12, 12, 12)
                    block_layout.setSpacing(6)
                    
                    subject_label = QLabel(sched['subject'])
                    subject_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #333; background-color: transparent;")
                    subject_label.setWordWrap(True)
                    subject_label.setAlignment(Qt.AlignCenter)
                    block_layout.addWidget(subject_label)
                    
                    section_label = QLabel(sched['section'])
                    section_label.setStyleSheet("font-size: 13px; color: #444; background-color: transparent;")
                    section_label.setAlignment(Qt.AlignCenter)
                    block_layout.addWidget(section_label)
                    
                    room_label = QLabel(f"Room: {sched['room']}")
                    room_label.setStyleSheet("font-size: 12px; color: #555; background-color: transparent;")
                    room_label.setAlignment(Qt.AlignCenter)
                    block_layout.addWidget(room_label)
                    
                    block_layout.addStretch()
                    
                    # Add to grid with row span
                    grid.addWidget(block, start_row + 1, col, row_span, 1)
                    
            except (ValueError, AttributeError):
                # If time parsing fails, skip this schedule
                continue
        
        card_layout.addLayout(grid)
        # Remove the stretch to fill the entire space
        # card_layout.addStretch()

    def refresh_today_panel(self):
        """Refresh the today schedule panel."""
        # Clear existing blocks
        while self.schedule_blocks_layout.count():
            item = self.schedule_blocks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get today's schedules
        today_schedules = self.get_today_schedules()
        
        if not today_schedules:
            no_schedule = QLabel("🎉 No classes scheduled for today! 🎉")
            no_schedule.setAlignment(Qt.AlignCenter)
            no_schedule.setWordWrap(True)
            no_schedule.setStyleSheet("""
                font-size: 14px;
                color: #797979;
                font-style: italic;
                padding: 40px 20px;
            """)
            self.schedule_blocks_layout.addWidget(no_schedule)
        else:
            for sched in today_schedules:
                block = self.create_schedule_block(
                    f"{sched['subject']}\n{sched['section']}\n{sched['time']}",
                    f"Room: {sched['room']}",
                    sched['color']
                )
                self.schedule_blocks_layout.addWidget(block)
        
        self.schedule_blocks_layout.addStretch()

    def create_schedule_block(self, title, subtitle, color):
        """Create a schedule block widget."""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 15px;
                padding: 15px;
            }}
        """)
        widget.setMinimumHeight(100)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #333;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 12px; color: #555;")
        layout.addWidget(subtitle_label)
        
        layout.addStretch()
        
        return widget
