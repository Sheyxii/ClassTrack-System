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
        """Establish database connection"""
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
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def validate_user(self, username, password):
        """
        Validate user credentials
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
                # Update last login
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
        Validate user credentials by email
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
        Add new user to database
        Returns: (success: bool, message: str)
        """
        if not username or not password or not email:
            return False, "All fields are required"
        
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            
            # Check if username already exists
            check_query = "SELECT username FROM users WHERE username = %s"
            cursor.execute(check_query, (username,))
            if cursor.fetchone():
                cursor.close()
                self.disconnect()
                return False, "Username already exists"
            
            # Check if email already exists
            check_email_query = "SELECT email FROM users WHERE email = %s"
            cursor.execute(check_email_query, (email,))
            if cursor.fetchone():
                cursor.close()
                self.disconnect()
                return False, "Email already registered"
            
            # Insert new user
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
        Reset user password by email
        Returns: (success: bool, message: str)
        """
        if not email or not new_password:
            return False, "Email and password are required"
        
        if not self.connect():
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            
            # Check if email exists
            check_query = "SELECT user_id FROM users WHERE email = %s"
            cursor.execute(check_query, (email,))
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                self.disconnect()
                return False, "Email not found. Please check your email address."
            
            # Update password
            update_query = "UPDATE users SET password = %s WHERE email = %s"
            cursor.execute(update_query, (new_password, email))
            self.connection.commit()
            cursor.close()
            self.disconnect()
            return True, "Password reset successfully!"
            
        except Error as e:
            self.disconnect()
            return False, f"Database error: {e}"
