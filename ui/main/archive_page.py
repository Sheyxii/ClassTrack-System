from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
sys.path.append('..')
from utils.database import DatabaseConnection


class ArchivePage(QWidget):
    def __init__(self, user_id=1, my_classes_page=None):
        super().__init__()
        self.user_id = user_id
        self.my_classes_page = my_classes_page
        self.db = DatabaseConnection()
        self.checkboxes = []
        self.sections_data = []
        self.init_ui()

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

        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📦 Archive")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Delete Selected button
        delete_selected_btn = QPushButton("🗑️ DELETE SELECTED")
        delete_selected_btn.setCursor(Qt.PointingHandCursor)
        delete_selected_btn.setFixedHeight(40)
        delete_selected_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        delete_selected_btn.clicked.connect(self.delete_selected)
        header_layout.addWidget(delete_selected_btn)
        
        # Delete All button
        delete_all_btn = QPushButton("🗑️ DELETE ALL")
        delete_all_btn.setCursor(Qt.PointingHandCursor)
        delete_all_btn.setFixedHeight(40)
        delete_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)
        delete_all_btn.clicked.connect(self.delete_all)
        header_layout.addWidget(delete_all_btn)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setFixedHeight(40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #222;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
        """)
        refresh_btn.clicked.connect(self.load_archived_sections)
        header_layout.addWidget(refresh_btn)
        
        content_layout.addLayout(header_layout)

        # Archived sections container
        self.sections_container = QWidget()
        self.sections_container.setStyleSheet("""
            QWidget {
                background-color: #9E9E9E;
                border-radius: 15px;
            }
        """)
        sections_container_layout = QVBoxLayout(self.sections_container)
        sections_container_layout.setContentsMargins(15, 15, 15, 15)
        sections_container_layout.setSpacing(10)

        # Scroll area for archived sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.archive_layout = QVBoxLayout(scroll_content)
        self.archive_layout.setContentsMargins(0, 0, 0, 0)
        self.archive_layout.setSpacing(15)
        self.archive_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(scroll_content)

        sections_container_layout.addWidget(scroll)
        content_layout.addWidget(self.sections_container)

        main_layout.addWidget(content_widget)
        
        # Load archived sections
        self.load_archived_sections()

    def load_archived_sections(self):
        """Load all archived sections"""
        # Clear existing content
        while self.archive_layout.count():
            item = self.archive_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Reset checkboxes and sections data
        self.checkboxes = []
        self.sections_data = []

        # Get archived sections
        archived_sections = self.db.get_sections(self.user_id, include_archived=True)
        archived_sections = [s for s in archived_sections if s['is_archived']]
        self.sections_data = archived_sections

        if archived_sections:
            # Create table
            table = QTableWidget()
            table.setRowCount(len(archived_sections))
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Select", "Section Name", "Archived Date", "Restore", "Delete"])
            
            # Create custom header with "Select All" checkbox
            header = table.horizontalHeader()
            header.setStyleSheet("""
                QHeaderView::section {
                    background-color: #F5F5F5;
                    color: #333;
                    font-weight: 600;
                    padding: 10px;
                    border: none;
                    font-size: 13px;
                }
            """)
            
            # Add "Select All" checkbox in header
            select_all_widget = QWidget()
            select_all_layout = QHBoxLayout(select_all_widget)
            select_all_layout.setContentsMargins(0, 0, 0, 0)
            select_all_layout.setAlignment(Qt.AlignCenter)
            
            self.select_all_checkbox = QCheckBox()
            self.select_all_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
            self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
            select_all_layout.addWidget(self.select_all_checkbox)
            
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
            table.setColumnWidth(0, 80)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            table.setColumnWidth(3, 120)
            table.setColumnWidth(4, 120)

            for row, section in enumerate(archived_sections):
                # Checkbox
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                
                checkbox = QCheckBox()
                checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
                self.checkboxes.append(checkbox)
                checkbox_layout.addWidget(checkbox)
                table.setCellWidget(row, 0, checkbox_widget)
                
                table.setItem(row, 1, QTableWidgetItem(section['section_name']))
                archived_date = section.get('archived_at', 'Unknown')
                if archived_date and archived_date != 'Unknown':
                    archived_date = str(archived_date).split('.')[0]
                table.setItem(row, 2, QTableWidgetItem(archived_date))

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
                restore_btn.clicked.connect(lambda checked, s=section: self.restore_section(s))
                table.setCellWidget(row, 3, restore_btn)

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
                delete_btn.clicked.connect(lambda checked, s=section: self.delete_section_permanently(s))
                table.setCellWidget(row, 4, delete_btn)

                table.setRowHeight(row, 50)

            self.archive_layout.addWidget(table)
        else:
            no_archive = QLabel("No archived sections")
            no_archive.setStyleSheet("font-size: 18px; color: #555; padding: 40px; background-color: white; border-radius: 8px;")
            no_archive.setAlignment(Qt.AlignCenter)
            self.archive_layout.addWidget(no_archive)

    def restore_section(self, section):
        """Restore an archived section"""
        reply = QMessageBox.question(
            self, 'Restore Section',
            f"Restore section '{section['section_name']}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success, message = self.db.restore_section(section['section_id'])
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_archived_sections()
                # Refresh my classes page if available
                if self.my_classes_page:
                    self.my_classes_page.load_sections()
            else:
                QMessageBox.warning(self, "Error", message)

    def delete_section_permanently(self, section):
        """Permanently delete a section"""
        reply = QMessageBox.question(
            self, 'Permanently Delete',
            f"PERMANENTLY delete section '{section['section_name']}'?\nThis action CANNOT be undone!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success, message = self.db.delete_section_permanently(section['section_id'])
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_archived_sections()
            else:
                QMessageBox.warning(self, "Error", message)

    def toggle_select_all(self, state):
        """Toggle all checkboxes when Select All is clicked"""
        for checkbox in self.checkboxes:
            checkbox.setChecked(state == Qt.Checked)

    def delete_selected(self):
        """Delete all selected sections"""
        selected_sections = []
        for i, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked() and i < len(self.sections_data):
                selected_sections.append(self.sections_data[i])
        
        if not selected_sections:
            QMessageBox.warning(self, "No Selection", "Please select at least one section to delete.")
            return
        
        section_names = "\n".join([f"• {s['section_name']}" for s in selected_sections])
        reply = QMessageBox.question(
            self, 'Delete Selected Sections',
            f"PERMANENTLY delete {len(selected_sections)} selected section(s)?\n\n{section_names}\n\nThis action CANNOT be undone!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success_count = 0
            failed_count = 0
            
            for section in selected_sections:
                success, message = self.db.delete_section_permanently(section['section_id'])
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            
            if success_count > 0:
                QMessageBox.information(
                    self, "Success", 
                    f"Successfully deleted {success_count} section(s)." + 
                    (f"\nFailed: {failed_count}" if failed_count > 0 else "")
                )
                self.load_archived_sections()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete selected sections.")

    def delete_all(self):
        """Delete all archived sections"""
        if not self.sections_data:
            QMessageBox.warning(self, "No Sections", "There are no archived sections to delete.")
            return
        
        section_names = "\n".join([f"• {s['section_name']}" for s in self.sections_data])
        reply = QMessageBox.question(
            self, 'Delete All Sections',
            f"PERMANENTLY delete ALL {len(self.sections_data)} archived section(s)?\n\n{section_names}\n\nThis action CANNOT be undone!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success_count = 0
            failed_count = 0
            
            for section in self.sections_data:
                success, message = self.db.delete_section_permanently(section['section_id'])
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            
            if success_count > 0:
                QMessageBox.information(
                    self, "Success", 
                    f"Successfully deleted {success_count} section(s)." + 
                    (f"\nFailed: {failed_count}" if failed_count > 0 else "")
                )
                self.load_archived_sections()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete sections.")
