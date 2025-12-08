import json
import sys
sys.path.append('.')
from utils.database import DatabaseConnection

def setup_default_sections_and_students():
    """Setup default sections and students"""
    db = DatabaseConnection()
    
    # Load default students from JSON
    with open('utils/default_students.json', 'r') as f:
        students = json.load(f)
    
    # Assuming user_id = 1 (you can change this if needed)
    user_id = 1
    
    # Create ITEC 104 section
    print("Creating ITEC 104 section...")
    success1, message1, section_id1 = db.add_section(
        section_name="ITEC 104",
        user_id=user_id,
        section="BSCS 2B",
        subject="ITEC 104",
        room="Room 301"
    )
    
    if success1:
        print(f"✓ {message1} (ID: {section_id1})")
    else:
        print(f"✗ {message1}")
        if "already exists" not in message1.lower():
            return
    
    # Create CMSC 203 section
    print("\nCreating CMSC 203 section...")
    success2, message2, section_id2 = db.add_section(
        section_name="CMSC 203",
        user_id=user_id,
        section="BSCS 2B",
        subject="CMSC 203",
        room="Room 302"
    )
    
    if success2:
        print(f"✓ {message2} (ID: {section_id2})")
    else:
        print(f"✗ {message2}")
        if "already exists" not in message2.lower():
            return
    
    # If sections already exist, get their IDs
    if not success1 or not success2:
        if not db.connect():
            print("Database connection failed")
            return
        cursor = db.connection.cursor()
        
        if not success1:
            cursor.execute("SELECT section_id FROM sections WHERE section_name = %s AND user_id = %s AND is_archived = FALSE", ("ITEC 104", user_id))
            result = cursor.fetchone()
            if result:
                section_id1 = result[0]
        
        if not success2:
            cursor.execute("SELECT section_id FROM sections WHERE section_name = %s AND user_id = %s AND is_archived = FALSE", ("CMSC 203", user_id))
            result = cursor.fetchone()
            if result:
                section_id2 = result[0]
        
        cursor.close()
        db.disconnect()
    
    # Add students to ITEC 104
    print(f"\nAdding {len(students)} students to ITEC 104...")
    added_count1 = 0
    for student in students:
        student_data = {
            'student_id': student['student_id'],
            'section_id': section_id1,
            'first_name': student['first_name'],
            'last_name': student['last_name'],
            'age': student['age'],
            'email': student['email'],
            'phone': student['phone'],
            'birthday': student['birthday'],
            'address': student['address'],
            'grade': student['grade']
        }
        success, message = db.add_student(student_data)
        if success:
            added_count1 += 1
            print(f"  ✓ Added {student['first_name']} {student['last_name']}")
        else:
            print(f"  ✗ {student['first_name']} {student['last_name']}: {message}")
    
    print(f"\nTotal students added to ITEC 104: {added_count1}/{len(students)}")
    
    # Add students to CMSC 203
    print(f"\nAdding {len(students)} students to CMSC 203...")
    added_count2 = 0
    for student in students:
        student_data = {
            'student_id': student['student_id'],
            'section_id': section_id2,
            'first_name': student['first_name'],
            'last_name': student['last_name'],
            'age': student['age'],
            'email': student['email'],
            'phone': student['phone'],
            'birthday': student['birthday'],
            'address': student['address'],
            'grade': student['grade']
        }
        success, message = db.add_student(student_data)
        if success:
            added_count2 += 1
            print(f"  ✓ Added {student['first_name']} {student['last_name']}")
        else:
            print(f"  ✗ {student['first_name']} {student['last_name']}: {message}")
    
    print(f"\nTotal students added to CMSC 203: {added_count2}/{len(students)}")
    print("\n" + "="*60)
    print("Setup complete!")
    print(f"ITEC 104 - BSCS 2B: {added_count1} students")
    print(f"CMSC 203 - BSCS 2B: {added_count2} students")
    print("="*60)

if __name__ == "__main__":
    setup_default_sections_and_students()
