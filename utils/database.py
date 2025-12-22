import pymysql
from pymysql import Error

class DatabaseConnection:
    def __init__(self):
        self.host = "localhost"
        self.database = "classtrack_db"
        self.user = "root" 
        self.password = "Marshey_1213"
        self.connection = None
    
    def connect(self):
        """database connection"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """close the database connection"""
        if self.connection:
            self.connection.close()
    
    def validate_user(self, username, password):
        """
        I-validate ang user credentials
       
        """
        if not username or not password:
            return False, "Please enter both username and password", None
        
        if not self.connect():
            return False, "Database connection failed", None
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            
            if user:
                # I-update ang last login
                update_query = "UPDATE users SET last_login = NOW() WHERE user_id = %s"
                cursor.execute(update_query, (user['user_id'],))
                self.connection.commit()
                cursor.close()
                self.disconnect()
                return True, "Login successful!", user
            else:
                cursor.close()
                self.disconnect()
                return False, "Invalid username or password", None
                
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}", None
    
    def validate_user_by_email(self, email, password):
        """
        I-validate ang user credentials gamit ang email

        """
        if not email or not password:
            return False, "Please enter both email and password", None
        
        if not self.connect():
            return False, "Database connection failed", None
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            query = "SELECT * FROM users WHERE email = %s AND password = %s"
            cursor.execute(query, (email, password))
            user = cursor.fetchone()
            
            if user:
                cursor.close()
                self.disconnect()
                return True, "Verification successful!", user
            else:
                cursor.close()
                self.disconnect()
                return False, "Invalid email or password", None
                
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}", None
    
    def add_user(self, username, password, email):
        """
        Mag-add ng new user sa database
        """
        if not username or not password or not email:
            return False, "All fields are required"
        
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            
            # I-check kung existing na ang username
            check_query = "SELECT username FROM users WHERE username = %s"
            cursor.execute(check_query, (username,))
            if cursor.fetchone():
                cursor.close()
                self.disconnect()
                return False, "Username already exists"
            
            # I-check kung existing na ang email
            check_email_query = "SELECT email FROM users WHERE email = %s"
            cursor.execute(check_email_query, (email,))
            if cursor.fetchone():
                cursor.close()
                self.disconnect()
                return False, "Email already registered"
            
            # I-insert ang new user
            insert_query = """
                INSERT INTO users (username, password, email) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (username, password, email))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Account created successfully!"
            
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    def reset_password(self, email, new_password):
        """
        reset user password using email
        """
        if not email or not new_password:
            return False, "Email and password are required"
        
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            
            # I-check kung existing ang email
            check_query = "SELECT user_id FROM users WHERE email = %s"
            cursor.execute(check_query, (email,))
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                self.disconnect()
                return False, "Email not found. Please check your email address."
            
            # I-update ang password
            update_query = "UPDATE users SET password = %s WHERE email = %s"
            cursor.execute(update_query, (new_password, email))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Password reset successfully!"
            
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    # ==================== SECTIONS MANAGEMENT ====================
    
    def get_sections(self, user_id, include_archived=False):
        """
        Kunin lahat ng sections para sa user
        """
        if not self.connect():
            return []
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            if include_archived:
                query = "SELECT * FROM sections WHERE user_id = %s ORDER BY created_at DESC"
            else:
                query = "SELECT * FROM sections WHERE user_id = %s AND is_archived = FALSE ORDER BY created_at DESC"
            cursor.execute(query, (user_id,))
            sections = cursor.fetchall()
            cursor.close()
            self.disconnect()
            return sections
        except Error as e:
            print(f"Error fetching sections: {e}")
            self.disconnect()
            return []
    
    def add_section(self, section_name, user_id, section=None, subject=None, room=None):
        """
        Mag-add ng new section

        """
        if not section_name:
            return False, "Section name is required", None
        
        if not self.connect():
            return False, "Database connection failed", None
        
        try:
            cursor = self.connection.cursor()
            
            # I-check kung existing na ang section para sa user na ito
            check_query = "SELECT section_id FROM sections WHERE section_name = %s AND user_id = %s AND is_archived = FALSE"
            cursor.execute(check_query, (section_name, user_id))
            if cursor.fetchone():
                cursor.close()
                self.disconnect()
                return False, "Section already exists", None
            
            # I-insert ang new section with all fields
            insert_query = "INSERT INTO sections (section_name, section, subject, room, user_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (section_name, section, subject, room, user_id))
            section_id = cursor.lastrowid
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Section created successfully", section_id
            
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}", None
    
    def update_section(self, section_id, section_name, section, subject, room):
        """
        Update section details
        Returns: (success: bool, message: str)
        """
        if not section_name:
            return False, "Class name is required"
        
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            
            # Check if another section with this name exists (excluding current section)
            check_query = "SELECT section_id FROM sections WHERE section_name = %s AND section_id != %s AND is_archived = FALSE"
            cursor.execute(check_query, (section_name, section_id))
            if cursor.fetchone():
                cursor.close()
                self.disconnect()
                return False, "A class with this name already exists"
            
            # Update the section
            update_query = """
                UPDATE sections 
                SET section_name = %s, section = %s, subject = %s, room = %s
                WHERE section_id = %s
            """
            cursor.execute(update_query, (section_name, section, subject, room, section_id))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Class updated successfully"
            
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    def archive_section(self, section_id):
        """
        I-archive ang section (soft delete)
        Returns: (success: bool, message: str)
        """
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            query = "UPDATE sections SET is_archived = TRUE, archived_at = NOW() WHERE section_id = %s"
            cursor.execute(query, (section_id,))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Section archived successfully"
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    def restore_section(self, section_id):
        """
        I-restore ang archived section
        Returns: (success: bool, message: str)
        """
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            query = "UPDATE sections SET is_archived = FALSE, archived_at = NULL WHERE section_id = %s"
            cursor.execute(query, (section_id,))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Section restored successfully"
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    def delete_section_permanently(self, section_id):
        """
        Permanenteng i-delete ang section at lahat ng students nito
        Returns: (success: bool, message: str)
        """
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM sections WHERE section_id = %s"
            cursor.execute(query, (section_id,))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Section deleted permanently"
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    # ==================== STUDENTS MANAGEMENT ====================
    
    def get_students(self, section_id, include_archived=False):
        """
        Kunin lahat ng students sa isang section
        Returns: list of student dictionaries
        """
        if not self.connect():
            return []
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            if include_archived:
                query = "SELECT * FROM students WHERE section_id = %s ORDER BY last_name, first_name"
            else:
                query = "SELECT * FROM students WHERE section_id = %s AND is_archived = FALSE ORDER BY last_name, first_name"
            cursor.execute(query, (section_id,))
            students = cursor.fetchall()
            cursor.close()
            self.disconnect()
            return students
        except Error as e:
            print(f"Error fetching students: {e}")
            self.disconnect()
            return []
    
    def add_student(self, student_data):
        """
        Mag-add ng new student
        """
        required_fields = ['student_id', 'section_id', 'first_name', 'last_name']
        for field in required_fields:
            if field not in student_data or not student_data[field]:
                return False, f"{field} is required"
        
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            
            # I-check kung existing na ang student ID sa SAME section lang
            check_query = "SELECT student_id FROM students WHERE student_id = %s AND section_id = %s"
            cursor.execute(check_query, (student_data['student_id'], student_data['section_id']))
            if cursor.fetchone():
                cursor.close()
                self.disconnect()
                return False, "Student ID already exists in this section"
            
            # I-insert ang new student
            insert_query = """
                INSERT INTO students (student_id, section_id, first_name, last_name, age, email, phone, birthday, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                student_data['student_id'],
                student_data['section_id'],
                student_data['first_name'],
                student_data['last_name'],
                student_data.get('age'),
                student_data.get('email'),
                student_data.get('phone'),
                student_data.get('birthday'),
                student_data.get('address')
            ))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Student added successfully"
            
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    def update_student(self, student_id, student_data):
        """
        I-update ang student information
        Returns: (success: bool, message: str)
        """
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            update_query = """
                UPDATE students SET
                    first_name = %s,
                    last_name = %s,
                    age = %s,
                    email = %s,
                    phone = %s,
                    birthday = %s,
                    address = %s
                WHERE student_id = %s
            """
            cursor.execute(update_query, (
                student_data['first_name'],
                student_data['last_name'],
                student_data.get('age'),
                student_data.get('email'),
                student_data.get('phone'),
                student_data.get('birthday'),
                student_data.get('address'),
                student_id
            ))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Student updated successfully"
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    def archive_student(self, student_id, section_id=None):
        """
        I-archive ang student (soft delete)
        If section_id is provided, only archive for that section
        Returns: (success: bool, message: str)
        """
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            if section_id:
                query = "UPDATE students SET is_archived = TRUE, archived_at = NOW() WHERE student_id = %s AND section_id = %s"
                cursor.execute(query, (student_id, section_id))
            else:
                query = "UPDATE students SET is_archived = TRUE, archived_at = NOW() WHERE student_id = %s"
                cursor.execute(query, (student_id,))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Student archived successfully"
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    def restore_student(self, student_id, section_id=None):
        """
        I-restore ang archived student
        If section_id is provided, only restore for that section
        Returns: (success: bool, message: str)
        """
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            if section_id:
                query = "UPDATE students SET is_archived = FALSE, archived_at = NULL WHERE student_id = %s AND section_id = %s"
                cursor.execute(query, (student_id, section_id))
            else:
                query = "UPDATE students SET is_archived = FALSE, archived_at = NULL WHERE student_id = %s"
                cursor.execute(query, (student_id,))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Student restored successfully"
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    def delete_student_permanently(self, student_id, section_id=None):
 
        # Permanent delete ang student
        # If section_id is provided, only delete for that section
  
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            if section_id:
                query = "DELETE FROM students WHERE student_id = %s AND section_id = %s"
                cursor.execute(query, (student_id, section_id))
            else:
                query = "DELETE FROM students WHERE student_id = %s"
                cursor.execute(query, (student_id,))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Student deleted permanently"
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    def get_student_count(self, section_id):
        # Kunin ang bilang ng students sa section (excluding archived)

        if not self.connect():
            return 0
        
        try:
            cursor = self.connection.cursor()
            query = "SELECT COUNT(*) as count FROM students WHERE section_id = %s AND is_archived = FALSE"
            cursor.execute(query, (section_id,))
            result = cursor.fetchone()
            count = result[0] if result else 0
            cursor.close()
            self.disconnect()
            return count
        except Error as e:
            print(f"Error counting students: {e}")
            self.disconnect()
            return 0
    
    def add_students_batch(self, students_list):
        """
        Mag-add ng multiple students nang sabay-sabay
        students_list: list of student dictionaries
        Returns: (success_count: int, failed_count: int, messages: list)
        """
        success_count = 0
        failed_count = 0
        messages = []
        
        for student in students_list:
            success, message = self.add_student(student)
            if success:
                success_count += 1
                messages.append(f"✓ {student.get('first_name')} {student.get('last_name')}: {message}")
            else:
                failed_count += 1
                messages.append(f"✗ {student.get('first_name')} {student.get('last_name')}: {message}")
        
        return success_count, failed_count, messages
    
    def get_section_statistics(self, user_id):
        """
        Kunin ang statistics ng lahat ng sections with student counts para sa dashboard
        Returns: dict with section_name as key and student_count as value
        """
        if not self.connect():
            return {}
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            query = """
                SELECT s.section_name, COUNT(st.student_id) as student_count
                FROM sections s
                LEFT JOIN students st ON s.section_id = st.section_id AND st.is_archived = FALSE
                WHERE s.user_id = %s AND s.is_archived = FALSE
                GROUP BY s.section_id, s.section_name
                ORDER BY s.section_name
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            cursor.close()
            self.disconnect()
            
            # I-convert to dictionary para madaling i-access
            stats = {row['section_name']: row['student_count'] for row in results}
            return stats
        except Error as e:
            print(f"Error fetching section statistics: {e}")
            self.disconnect()
            return {}
    
    def save_attendance(self, section_id, attendance_date, attendance_data):
        """Save attendance record for a section"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Insert or get attendance record for this date
            cursor.execute("""
                INSERT INTO attendance (section_id, attendance_date) 
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE attendance_id=LAST_INSERT_ID(attendance_id)
            """, (section_id, attendance_date))
            
            attendance_id = cursor.lastrowid
            if attendance_id == 0:
                cursor.execute("""
                    SELECT attendance_id FROM attendance 
                    WHERE section_id = %s AND attendance_date = %s
                """, (section_id, attendance_date))
                result = cursor.fetchone()
                attendance_id = result[0] if result else None
            
            if not attendance_id:
                return False
            
            # Delete existing records for this attendance
            cursor.execute("""
                DELETE FROM attendance_records WHERE attendance_id = %s
            """, (attendance_id,))
            
            # Insert new attendance records
            for student_id, data in attendance_data.items():
                status = data.get('status')
                if status:
                    cursor.execute("""
                        INSERT INTO attendance_records 
                        (attendance_id, student_id, section_id, status)
                        VALUES (%s, %s, %s, %s)
                    """, (attendance_id, student_id, section_id, status))
            
            self.connection.commit()
            return True
            
        except Error as e:
            print(f"Error saving attendance: {e}")
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            self.disconnect()
    
    def get_attendance_records(self, section_id):
        """Get all attendance records for a section"""
        if not self.connect():
            return []
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            # Get all attendance dates for this section
            cursor.execute("""
                SELECT 
                    a.attendance_id,
                    a.attendance_date,
                    DAYNAME(a.attendance_date) as day_name,
                    COUNT(ar.record_id) as total_marked,
                    SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) as present_count,
                    SUM(CASE WHEN ar.status = 'absent' THEN 1 ELSE 0 END) as absent_count
                FROM attendance a
                LEFT JOIN attendance_records ar ON a.attendance_id = ar.attendance_id
                WHERE a.section_id = %s
                GROUP BY a.attendance_id, a.attendance_date
                ORDER BY a.attendance_date DESC
            """, (section_id,))
            
            return cursor.fetchall()
            
        except Error as e:
            print(f"Error getting attendance records: {e}")
            return []
        finally:
            self.disconnect()
    
    def get_attendance_details(self, attendance_id):
        """Get detailed attendance records for a specific date"""
        if not self.connect():
            return {}
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            cursor.execute("""
                SELECT student_id, status
                FROM attendance_records
                WHERE attendance_id = %s
            """, (attendance_id,))
            
            records = cursor.fetchall()
            return {record['student_id']: {'status': record['status']} for record in records}
            
        except Error as e:
            print(f"Error getting attendance details: {e}")
            return {}
        finally:
            self.disconnect()
    
    def delete_attendance(self, attendance_id):
        """Delete an attendance record"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM attendance WHERE attendance_id = %s", (attendance_id,))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error deleting attendance: {e}")
            return False
        finally:
            self.disconnect()
    def save_attendance(self, section_id, attendance_date, attendance_data):
        """Save attendance record for a section"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Insert or get attendance record for this date
            cursor.execute("""
                INSERT INTO attendance (section_id, attendance_date) 
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE attendance_id=LAST_INSERT_ID(attendance_id)
            """, (section_id, attendance_date))
            
            attendance_id = cursor.lastrowid
            if attendance_id == 0:
                cursor.execute("""
                    SELECT attendance_id FROM attendance 
                    WHERE section_id = %s AND attendance_date = %s
                """, (section_id, attendance_date))
                result = cursor.fetchone()
                attendance_id = result[0] if result else None
            
            if not attendance_id:
                return False
            
            # Delete existing records for this attendance
            cursor.execute("""
                DELETE FROM attendance_records WHERE attendance_id = %s
            """, (attendance_id,))
            
            # Insert new attendance records
            for student_id, data in attendance_data.items():
                status = data.get('status')
                if status:
                    cursor.execute("""
                        INSERT INTO attendance_records 
                        (attendance_id, student_id, section_id, status)
                        VALUES (%s, %s, %s, %s)
                    """, (attendance_id, student_id, section_id, status))
            
            self.connection.commit()
            return True
            
        except Error as e:
            print(f"Error saving attendance: {e}")
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            self.disconnect()
    
    def get_attendance_records(self, section_id):
        """Get all attendance records for a section"""
        if not self.connect():
            return []
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            # Get all attendance dates for this section
            cursor.execute("""
                SELECT 
                    a.attendance_id,
                    a.attendance_date,
                    DAYNAME(a.attendance_date) as day_name,
                    COUNT(ar.record_id) as total_marked,
                    SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) as present_count,
                    SUM(CASE WHEN ar.status = 'absent' THEN 1 ELSE 0 END) as absent_count
                FROM attendance a
                LEFT JOIN attendance_records ar ON a.attendance_id = ar.attendance_id
                WHERE a.section_id = %s
                GROUP BY a.attendance_id, a.attendance_date
                ORDER BY a.attendance_date DESC
            """, (section_id,))
            
            return cursor.fetchall()
            
        except Error as e:
            print(f"Error getting attendance records: {e}")
            return []
        finally:
            self.disconnect()
    
    def get_attendance_details(self, attendance_id):
        """Get detailed attendance records for a specific date"""
        if not self.connect():
            return {}
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            cursor.execute("""
                SELECT student_id, status
                FROM attendance_records
                WHERE attendance_id = %s
            """, (attendance_id,))
            
            records = cursor.fetchall()
            return {record['student_id']: {'status': record['status']} for record in records}
            
        except Error as e:
            print(f"Error getting attendance details: {e}")
            return {}
        finally:
            self.disconnect()
    
    def delete_attendance(self, attendance_id):
        """Delete an attendance record"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM attendance WHERE attendance_id = %s", (attendance_id,))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error deleting attendance: {e}")
            return False
        finally:
            self.disconnect()

    # ==================== RESOURCES METHODS ====================
    
    def add_resource(self, user_id, file_name, subject, file_path, file_size):
        """Add a new resource to database"""
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO resources (user_id, file_name, subject, file_path, file_size)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, file_name, subject, file_path, file_size))
            resource_id = cursor.lastrowid
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, resource_id
        except Error as e:
            print(f"Error adding resource: {e}")
            self.disconnect()
            return False, str(e)
    
    def get_resources(self, user_id):
        """Get all resources for a user"""
        if not self.connect():
            return []
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            query = """
                SELECT resource_id, file_name, subject, file_path, file_size,
                       DATE_FORMAT(uploaded_at, '%%Y-%%m-%%d') as uploaded
                FROM resources
                WHERE user_id = %s
                ORDER BY uploaded_at DESC
            """
            cursor.execute(query, (user_id,))
            resources = cursor.fetchall()
            cursor.close()
            self.disconnect()
            return resources
        except Error as e:
            print(f"Error fetching resources: {e}")
            self.disconnect()
            return []
    
    def delete_resource(self, resource_id):
        """Delete a resource from database"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM resources WHERE resource_id = %s", (resource_id,))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True
        except Error as e:
            print(f"Error deleting resource: {e}")
            self.disconnect()
            return False
    
    def save_student_grades(self, student_id, section_id, midterm, final):
        """Save or update student grades"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Convert empty or zero values to None
            midterm = midterm if midterm and midterm > 0 else None
            final = final if final and final > 0 else None
            
            # Check if grades already exist
            check_query = """
                SELECT grade_id FROM grades 
                WHERE student_id = %s AND section_id = %s
            """
            cursor.execute(check_query, (student_id, section_id))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing grades
                update_query = """
                    UPDATE grades 
                    SET midterm = %s, final = %s, updated_at = NOW()
                    WHERE student_id = %s AND section_id = %s
                """
                cursor.execute(update_query, (midterm, final, student_id, section_id))
            else:
                # Only insert if at least one grade is provided
                if midterm is not None or final is not None:
                    insert_query = """
                        INSERT INTO grades (student_id, section_id, midterm, final)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (student_id, section_id, midterm, final))
            
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True
        except Error as e:
            print(f"Error saving grades: {e}")
            self.disconnect()
            return False
    
    def get_student_grades(self, student_id, section_id):
        """Get student grades for a specific section"""
        if not self.connect():
            return {}
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            query = """
                SELECT midterm, final 
                FROM grades 
                WHERE student_id = %s AND section_id = %s
            """
            cursor.execute(query, (student_id, section_id))
            grades = cursor.fetchone()
            cursor.close()
            self.disconnect()
            return grades if grades else {}
        except Error as e:
            print(f"Error fetching grades: {e}")
            self.disconnect()
            return {}
    
    def add_schedule(self, user_id, subject, section, day, time, room, color):
        """Add a new schedule"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO schedules (user_id, subject, section, day, time, room, color)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, subject, section, day, time, room, color))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True
        except Error as e:
            print(f"Error adding schedule: {e}")
            self.disconnect()
            return False
    
    def get_schedules(self, user_id):
        """Get all schedules for a user"""
        if not self.connect():
            return []
        
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT schedule_id, subject, section, day, time, room, color
                FROM schedules
                WHERE user_id = %s
                ORDER BY 
                    FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'),
                    time
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            schedules = []
            for row in rows:
                schedules.append({
                    'schedule_id': row[0],
                    'subject': row[1],
                    'section': row[2],
                    'day': row[3],
                    'time': row[4],
                    'room': row[5],
                    'color': row[6]
                })
            
            cursor.close()
            self.disconnect()
            return schedules
        except Error as e:
            print(f"Error fetching schedules: {e}")
            self.disconnect()
            return []
    
    def delete_schedule(self, schedule_id):
        """Delete a schedule"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM schedules WHERE schedule_id = %s"
            cursor.execute(query, (schedule_id,))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True
        except Error as e:
            print(f"Error deleting schedule: {e}")
            self.disconnect()
            return False

