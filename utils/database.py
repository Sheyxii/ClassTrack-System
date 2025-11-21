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
        """I-establish ang database connection"""
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
        """I-close ang database connection"""
        if self.connection:
            self.connection.close()
    
    def validate_user(self, username, password):
        """
        I-validate ang user credentials
        Returns: (success: bool, message: str, user_data: dict or None)
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
        Returns: (success: bool, message: str, user_data: dict or None)
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
        Returns: (success: bool, message: str)
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
        I-reset ang user password gamit ang email
        Returns: (success: bool, message: str)
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
        Returns: list of section dictionaries
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
    
    def add_section(self, section_name, user_id):
        """
        Mag-add ng new section
        Returns: (success: bool, message: str, section_id: int or None)
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
            
            # I-insert ang new section
            insert_query = "INSERT INTO sections (section_name, user_id) VALUES (%s, %s)"
            cursor.execute(insert_query, (section_name, user_id))
            section_id = cursor.lastrowid
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Section created successfully", section_id
            
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}", None
    
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
        student_data: dict with keys: student_id, section_id, first_name, last_name, age, email, phone, birthday, address, grade
        Returns: (success: bool, message: str)
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
                INSERT INTO students (student_id, section_id, first_name, last_name, age, email, phone, birthday, address, grade)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                student_data.get('address'),
                student_data.get('grade')
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
                    address = %s,
                    grade = %s
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
                student_data.get('grade'),
                student_id
            ))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Student updated successfully"
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    def archive_student(self, student_id):
        """
        I-archive ang student (soft delete)
        Returns: (success: bool, message: str)
        """
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            query = "UPDATE students SET is_archived = TRUE, archived_at = NOW() WHERE student_id = %s"
            cursor.execute(query, (student_id,))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Student archived successfully"
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    def restore_student(self, student_id):
        """
        I-restore ang archived student
        Returns: (success: bool, message: str)
        """
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            query = "UPDATE students SET is_archived = FALSE, archived_at = NULL WHERE student_id = %s"
            cursor.execute(query, (student_id,))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Student restored successfully"
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
    
    def delete_student_permanently(self, student_id):
 
        # Permanent delete ang student
  
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
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

