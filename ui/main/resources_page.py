from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sys
import shutil
from datetime import datetime
sys.path.append('..')
from utils.database import DatabaseConnection


class ResourcesPage(QWidget):
    def __init__(self, user_id=1):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseConnection()
        self.resources_dir = "uploaded_resources"  # Directory to store files
        self.init_resources_directory()
        self.load_resources_from_db()
        self.init_ui()

    def init_resources_directory(self):
        """Create directory for storing uploaded files"""
        if not os.path.exists(self.resources_dir):
            os.makedirs(self.resources_dir)
    
    def load_resources_from_db(self):
        """Load resources from database"""
        db_resources = self.db.get_resources(self.user_id)
        self.resources = []
        for res in db_resources:
            self.resources.append({
                'resource_id': res['resource_id'],
                'name': res['file_name'],
                'subject': res['subject'],
                'size': res['file_size'],
                'uploaded': res['uploaded'],
                'file_path': res['file_path']
            })

    def get_user_subjects(self):
        """Get unique subjects from user's classes"""
        sections = list(self.db.get_sections(self.user_id))
        subjects = set()
        for section in sections:
            subject = section.get('subject', '')
            if subject:
                subjects.add(subject)
        return ['All'] + sorted(list(subjects))
    
    def refresh_subject_filter(self):
        """Refresh the subject filter dropdown with updated subjects"""
        current_selection = self.subject_filter.currentText()
        self.subject_filter.clear()
        
        user_subjects = self.get_user_subjects()
        if len(user_subjects) == 1:  # Only 'All'
            self.subject_filter.addItems(['All'])
        else:
            self.subject_filter.addItems(user_subjects)
        
        # Try to restore previous selection
        index = self.subject_filter.findText(current_selection)
        if index >= 0:
            self.subject_filter.setCurrentIndex(index)
        else:
            self.subject_filter.setCurrentIndex(0)  # Default to 'All'

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Header outside the frame
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        title = QLabel("Resources")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Manage and organize your class materials")
        subtitle.setStyleSheet("font-size: 16px; color: #555;")
        header_layout.addWidget(subtitle)
        
        main_layout.addLayout(header_layout)

        # Main content area with gray background
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #9E9E9E; border-radius: 12px;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Control panel (search, filter, upload)
        control_panel = QWidget()
        control_panel.setStyleSheet("""
            QWidget {
                background-color: #BDBDBD;
                border-radius: 12px;
            }
        """)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(20, 20, 20, 20)
        control_layout.setSpacing(15)
        
        # Search bar
        search_layout = QHBoxLayout()
        
        search_icon = QLabel()
        search_icon.setPixmap(QIcon("image/search.png").pixmap(30, 30))
        search_icon.setStyleSheet("background: transparent;")
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search resources...")
        self.search_input.setFixedHeight(45)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #999;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: white;
                color: #222;
            }
            QLineEdit:focus {
                border: 2px solid #666;
            }
        """)
        self.search_input.textChanged.connect(self.filter_resources)
        search_layout.addWidget(self.search_input)
        
        control_layout.addLayout(search_layout)
        
        # Filter and Upload row
        filter_upload_layout = QHBoxLayout()
        filter_upload_layout.setSpacing(15)
        
        filter_upload_layout.addStretch()
        
        # Subject filter dropdown
        self.subject_filter = QComboBox()
        user_subjects = self.get_user_subjects()
        if len(user_subjects) == 1:  # Only 'All'
            self.subject_filter.addItems(['All'])
        else:
            self.subject_filter.addItems(user_subjects)
        self.subject_filter.setFixedHeight(45)
        self.subject_filter.setFixedWidth(180)
        self.subject_filter.setStyleSheet("""
            QComboBox {
                border: 2px solid #666;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: white;
                color: #222;
            }
            QComboBox:hover {
                border: 2px solid #444;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #999;
                background-color: white;
                selection-background-color: #666;
                selection-color: white;
                padding: 5px;
            }
        """)
        self.subject_filter.currentTextChanged.connect(self.filter_resources)
        filter_upload_layout.addWidget(self.subject_filter)
        
        # Upload button
        upload_btn = QPushButton("  Upload File")
        upload_btn.setIcon(QIcon("image/upload.png"))
        upload_btn.setIconSize(QSize(20, 20))
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.setFixedHeight(45)
        upload_btn.setFixedWidth(150)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                color: #333;
                border: 2px solid #666;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #7393B3;
            }
        """)
        upload_btn.clicked.connect(self.show_upload_dialog)
        filter_upload_layout.addWidget(upload_btn)
        
        control_layout.addLayout(filter_upload_layout)
        
        content_layout.addWidget(control_panel)
        
        # Resources container with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.resources_layout = QVBoxLayout(scroll_content)
        self.resources_layout.setContentsMargins(0, 0, 0, 0)
        self.resources_layout.setSpacing(15)
        self.resources_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(scroll_content)
        content_layout.addWidget(scroll)
        
        main_layout.addWidget(content_widget)
        
        # Display resources
        self.display_resources()

    def display_resources(self, filtered_resources=None):
        """Display resource cards"""
        # Clear current resources
        while self.resources_layout.count():
            item = self.resources_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        resources_to_display = filtered_resources if filtered_resources is not None else self.resources
        
        if not resources_to_display:
            no_resources = QLabel("No resources found")
            no_resources.setStyleSheet("font-size: 16px; color: #999; padding: 40px;")
            no_resources.setAlignment(Qt.AlignCenter)
            self.resources_layout.addWidget(no_resources)
            return
        
        # Group by subject
        subjects = {}
        for resource in resources_to_display:
            subject = resource['subject']
            if subject not in subjects:
                subjects[subject] = []
            subjects[subject].append(resource)
        
        # Create cards for each subject
        for subject, subject_resources in subjects.items():
            # Subject header card
            subject_card = self.create_subject_card(subject, subject_resources)
            self.resources_layout.addWidget(subject_card)

    def create_subject_card(self, subject, resources):
        """Create a subject section with resource cards"""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(10)
        
        # Subject header
        for resource in resources:
            resource_card = self.create_resource_card(resource, subject)
            container_layout.addWidget(resource_card)
        
        return container

    def create_resource_card(self, resource, subject):
        """Create individual resource card"""
        card = QWidget()
        
        # Get pastel color based on subject
        card_color = self.get_pastel_color(subject)
        
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {card_color};
                border-radius: 10px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 15, 20, 15)
        card_layout.setSpacing(10)
        
        # Top section with icon and subject tag
        top_layout = QHBoxLayout()
        
        # File icon with background
        icon_container = QWidget()
        icon_container.setFixedSize(50, 50)
        icon_bg_color = self.get_darker_shade(card_color)
        icon_container.setStyleSheet(f"""
            QWidget {{
                background-color: {icon_bg_color};
                border-radius: 10px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel("📄")
        icon_label.setStyleSheet("font-size: 28px; background: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        top_layout.addWidget(icon_container)
        
        top_layout.addStretch()
        
        # Subject tag
        subject_tag = QLabel(subject)
        subject_tag.setFixedHeight(30)
        subject_tag.setAlignment(Qt.AlignCenter)
        subject_tag.setStyleSheet(f"""
            QLabel {{
                background-color: {icon_bg_color};
                color: #1a1a1a;
                padding: 5px 15px;
                border-radius: 15px;
                font-size: 14px;
                font-weight: 700;
            }}
        """)
        top_layout.addWidget(subject_tag)
        
        card_layout.addLayout(top_layout)
        
        # File info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        name_label = QLabel(resource['name'])
        name_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #1a1a1a; background: transparent;")
        info_layout.addWidget(name_label)
        
        details_label = QLabel(f"Size: {resource['size']}")
        details_label.setStyleSheet("font-size: 13px; color: #555; background: transparent;")
        info_layout.addWidget(details_label)
        
        upload_label = QLabel(f"Uploaded: {resource['uploaded']}")
        upload_label.setStyleSheet("font-size: 13px; color: #555; background: transparent;")
        info_layout.addWidget(upload_label)
        
        card_layout.addLayout(info_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # View button
        view_btn = QPushButton("  View")
        view_btn.setIcon(QIcon("image/view.png"))
        view_btn.setIconSize(QSize(18, 18))
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.setFixedHeight(40)
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        view_btn.clicked.connect(lambda: self.view_resource(resource))
        button_layout.addWidget(view_btn)
        
        button_layout.addStretch()
        
        # Download button
        download_btn = QPushButton()
        download_btn.setIcon(QIcon("image/download.png"))
        download_btn.setIconSize(QSize(18, 18))
        download_btn.setCursor(Qt.PointingHandCursor)
        download_btn.setFixedSize(40, 40)
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border: none;
                border-radius: 6px;
                font-size: 18px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        download_btn.clicked.connect(lambda: self.download_resource(resource))
        button_layout.addWidget(download_btn)
        
        # Delete button
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("image/bin.png"))
        delete_btn.setIconSize(QSize(18, 18))
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedSize(40, 40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFB3B3;
                color: #333;
                border: none;
                border-radius: 6px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #FF9999;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_resource(resource))
        button_layout.addWidget(delete_btn)
        
        card_layout.addLayout(button_layout)
        
        return card
    
    def get_pastel_color(self, subject):
        """Generate pastel color based on subject name"""
        # Hash the subject name to get consistent colors
        hash_val = sum(ord(c) for c in subject)
        
        # Generate pastel colors (high saturation, high lightness)
        hue = (hash_val * 137) % 360  # Use golden angle for better distribution
        
        # Convert HSL to RGB for pastel colors
        import colorsys
        r, g, b = colorsys.hls_to_rgb(hue/360, 0.85, 0.4)  # High lightness, medium saturation
        
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def get_darker_shade(self, hex_color):
        """Get a darker shade of the given color for icon background"""
        # Remove the # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken by 20%
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        
        return f'#{r:02x}{g:02x}{b:02x}'

    def filter_resources(self):
        """Filter resources based on search and subject"""
        search_text = self.search_input.text().lower()
        subject = self.subject_filter.currentText()
        
        filtered = [
            r for r in self.resources
            if (search_text in r['name'].lower() or search_text in r['subject'].lower())
            and (subject == 'All' or r['subject'] == subject)
        ]
        
        self.display_resources(filtered)

    def show_upload_dialog(self):
        """Show dialog to upload new resource"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Upload Resource")
        dialog.setWindowIcon(QIcon("image/system.png"))
        dialog.setFixedSize(500, 550)
        dialog.setStyleSheet("QDialog { background-color: white; }")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with border
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: white; border-bottom: 1px solid #E0E0E0;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(24, 20, 24, 20)
        
        title = QLabel("Upload Resource")
        title.setStyleSheet("font-size: 20px; font-weight: 600; color: #222;")
        header_layout.addWidget(title)
        
        layout.addWidget(header_widget)
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(20)
        
        # File name
        name_label = QLabel("File Name")
        name_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #333;")
        content_layout.addWidget(name_label)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter file name")
        name_input.setFixedHeight(48)
        name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #DDD;
                border-radius: 6px;
                padding: 0 14px;
                font-size: 14px;
                background-color: white;
                color: #333;
            }
            QLineEdit:focus {
                border: 1px solid #999;
            }
            QLineEdit::placeholder {
                color: #999;
            }
        """)
        content_layout.addWidget(name_input)
        
        # Subject
        subject_label = QLabel("Subject")
        subject_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #333; margin-top: 4px;")
        content_layout.addWidget(subject_label)
        
        subject_combo = QComboBox()
        user_subjects = self.get_user_subjects()
        if len(user_subjects) <= 1:
            subject_combo.addItems(['Select a subject'])
        else:
            subject_combo.addItems(['Select a subject'] + user_subjects[1:])  # Exclude 'All'
        subject_combo.setFixedHeight(48)
        subject_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #DDD;
                border-radius: 6px;
                padding: 0 14px;
                font-size: 14px;
                background-color: white;
                color: #333;
            }
            QComboBox:hover {
                border: 1px solid #999;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #666;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #DDD;
                background-color: white;
                selection-background-color: #F0F0F0;
                selection-color: #333;
                outline: none;
            }
        """)
        content_layout.addWidget(subject_combo)
        
        # File upload area
        upload_area = QWidget()
        upload_area.setFixedHeight(180)
        upload_area.setAcceptDrops(True)
        upload_area.setStyleSheet("""
            QWidget {
                border: 2px dashed #CCC;
                border-radius: 8px;
                background-color: #FAFAFA;
            }
        """)
        
        # Store reference to name_input for drag and drop
        upload_area.name_input = name_input
        
        # Enable drag and drop
        def dragEnterEvent(event):
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
                upload_area.setStyleSheet("""
                    QWidget {
                        border: 2px dashed #2563EB;
                        border-radius: 8px;
                        background-color: #EFF6FF;
                    }
                """)
        
        def dragLeaveEvent(event):
            upload_area.setStyleSheet("""
                QWidget {
                    border: 2px dashed #CCC;
                    border-radius: 8px;
                    background-color: #FAFAFA;
                }
            """)
        
        def dropEvent(event):
            upload_area.setStyleSheet("""
                QWidget {
                    border: 2px dashed #CCC;
                    border-radius: 8px;
                    background-color: #FAFAFA;
                }
            """)
            if event.mimeData().hasUrls():
                urls = event.mimeData().urls()
                if urls:
                    file_path = urls[0].toLocalFile()
                    # Check if file type is allowed
                    allowed_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
                    if any(file_path.lower().endswith(ext) for ext in allowed_extensions):
                        file_name = os.path.basename(file_path)
                        upload_area.name_input.setText(file_name)
                        upload_area.name_input.setProperty('file_path', file_path)
                        event.acceptProposedAction()
                    else:
                        QMessageBox.warning(dialog, "Invalid File Type", "Please upload PDF, DOC, DOCX, PPT, or PPTX files only.")
        
        upload_area.dragEnterEvent = dragEnterEvent
        upload_area.dragLeaveEvent = dragLeaveEvent
        upload_area.dropEvent = dropEvent
        
        upload_layout = QVBoxLayout(upload_area)
        upload_layout.setAlignment(Qt.AlignCenter)
        upload_layout.setSpacing(8)
        
        # Upload icon (using styled label)
        icon_label = QLabel("⬆")
        icon_label.setStyleSheet("font-size: 56px; color: #999; background: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(icon_label)
        
        upload_text = QLabel("Click to browse")
        upload_text.setStyleSheet("font-size: 14px; color: #666; background: transparent;")
        upload_text.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(upload_text)
        
        file_types = QLabel("PDF, DOC, DOCX, PPT, PPTX")
        file_types.setStyleSheet("font-size: 12px; color: #999; background: transparent;")
        file_types.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(file_types)
        
        # Make upload area clickable
        upload_area.mousePressEvent = lambda e: self.browse_file(name_input)
        
        content_layout.addWidget(upload_area)
        
        content_layout.addStretch()
        
        layout.addWidget(content_widget)
        
        # Footer with buttons
        footer_widget = QWidget()
        footer_widget.setStyleSheet("background-color: white; border-top: 1px solid #E0E0E0;")
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(24, 16, 24, 16)
        footer_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(44)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333;
                border: 1px solid #DDD;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
                border-color: #CCC;
            }
        """)
        cancel_btn.clicked.connect(dialog.close)
        footer_layout.addWidget(cancel_btn)
        
        footer_layout.addStretch()
        
        upload_btn = QPushButton("Upload")
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.setFixedHeight(44)
        upload_btn.setMinimumWidth(120)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        upload_btn.clicked.connect(lambda: self.upload_resource(name_input, subject_combo, dialog))
        footer_layout.addWidget(upload_btn)
        
        layout.addWidget(footer_widget)
        
        dialog.exec_()

    def browse_file(self, name_input):
        """Browse for file to upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "Documents (*.pdf *.doc *.docx *.ppt *.pptx);;All Files (*.*)"
        )
        if file_path:
            file_name = os.path.basename(file_path)
            name_input.setText(file_name)
            name_input.setProperty('file_path', file_path)

    def upload_resource(self, name_input, subject_combo, dialog):
        """Upload resource file"""
        name = name_input.text().strip()
        subject = subject_combo.currentText()
        file_path = name_input.property('file_path')
        
        if not name:
            QMessageBox.warning(self, "Missing Information", "Please enter a file name")
            return
        
        if subject == 'Select a subject':
            QMessageBox.warning(self, "Missing Information", "Please select a subject")
            return
        
        if not file_path:
            QMessageBox.warning(self, "Missing File", "Please select a file to upload")
            return
        
        # Get file size
        file_size = os.path.getsize(file_path)
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        # Copy file to resources directory
        dest_path = os.path.join(self.resources_dir, name)
        try:
            shutil.copy2(file_path, dest_path)
        except Exception as e:
            QMessageBox.critical(self, "Upload Error", f"Failed to upload file: {str(e)}")
            return
        
        # Save to database
        success, result = self.db.add_resource(self.user_id, name, subject, dest_path, size_str)
        
        if success:
            # Reload resources from database
            self.load_resources_from_db()
            self.display_resources()
            dialog.close()
            QMessageBox.information(self, "Success", "Resource uploaded successfully!")
            # Refresh dashboard statistics
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'dashboard_page'):
                self.main_window.dashboard_page.refresh_statistics()
        else:
            # Delete file if database save failed
            try:
                os.remove(dest_path)
            except:
                pass
            QMessageBox.critical(self, "Upload Error", f"Failed to save to database: {result}")

    def view_resource(self, resource):
        """View/open resource file"""
        if resource['file_path'] and os.path.exists(resource['file_path']):
            os.startfile(resource['file_path'])
        else:
            QMessageBox.information(self, "View Resource", f"Opening: {resource['name']}\n(File viewer functionality)")

    def download_resource(self, resource):
        """Download resource to user's chosen location"""
        if not resource['file_path'] or not os.path.exists(resource['file_path']):
            QMessageBox.warning(self, "Download Error", "File not found")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            resource['name'],
            "All Files (*.*)"
        )
        
        if save_path:
            try:
                shutil.copy2(resource['file_path'], save_path)
                QMessageBox.information(self, "Success", "File downloaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Download Error", f"Failed to download file: {str(e)}")

    def delete_resource(self, resource):
        """Delete resource"""
        reply = QMessageBox.question(
            self,
            "Delete Resource",
            f"Are you sure you want to delete '{resource['name']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete from database
            if self.db.delete_resource(resource['resource_id']):
                # Delete file if exists
                if resource['file_path'] and os.path.exists(resource['file_path']):
                    try:
                        os.remove(resource['file_path'])
                    except Exception as e:
                        QMessageBox.warning(self, "Warning", f"Could not delete file: {str(e)}")
                
                # Reload resources from database
                self.load_resources_from_db()
                self.display_resources()
                QMessageBox.information(self, "Success", "Resource deleted successfully!")
                # Refresh dashboard statistics
                if hasattr(self, 'main_window') and hasattr(self.main_window, 'dashboard_page'):
                    self.main_window.dashboard_page.refresh_statistics()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete resource from database")
