import json
import sys
import random
from datetime import datetime, timedelta
sys.path.append('.')
from utils.database import DatabaseConnection

def setup_default_sections_and_students():
    """Setup default sections and students"""
    db = DatabaseConnection()
    
    # Load students from JSON
    with open('utils/default_students.json', 'r') as f:
        students = json.load(f)
    
    # User ID
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
    
    # Get existing section IDs if already created
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
            'address': student['address']
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
            'address': student['address']
        }
        success, message = db.add_student(student_data)
        if success:
            added_count2 += 1
            print(f"  ✓ Added {student['first_name']} {student['last_name']}")
        else:
            print(f"  ✗ {student['first_name']} {student['last_name']}: {message}")
    
    print(f"\nTotal students added to CMSC 203: {added_count2}/{len(students)}")
    
    # Add grades for ITEC 104 students
    print(f"\n{'='*60}")
    print("Adding grades for ITEC 104 students...")
    print(f"{'='*60}")
    grades_count1 = 0
    for student in students:
        # Random grades (1.00 to 3.00)
        midterm = round(random.uniform(1.00, 3.00), 2)
        final = round(random.uniform(1.00, 3.00), 2)
        
        success = db.save_student_grades(
            student['student_id'],
            section_id1,
            midterm,
            final
        )
        if success:
            grades_count1 += 1
            semestral = (midterm + final) / 2
            print(f"  ✓ {student['first_name']} {student['last_name']}: Midterm={midterm}, Final={final}, Semestral={semestral:.2f}")
    
    print(f"\nTotal grades added for ITEC 104: {grades_count1}/{len(students)}")
    
    # Add grades for CMSC 203 students
    print(f"\n{'='*60}")
    print("Adding grades for CMSC 203 students...")
    print(f"{'='*60}")
    grades_count2 = 0
    for student in students:
        # Random grades (1.00 to 3.00)
        midterm = round(random.uniform(1.00, 3.00), 2)
        final = round(random.uniform(1.00, 3.00), 2)
        
        success = db.save_student_grades(
            student['student_id'],
            section_id2,
            midterm,
            final
        )
        if success:
            grades_count2 += 1
            semestral = (midterm + final) / 2
            print(f"  ✓ {student['first_name']} {student['last_name']}: Midterm={midterm}, Final={final}, Semestral={semestral:.2f}")
    
    print(f"\nTotal grades added for CMSC 203: {grades_count2}/{len(students)}")
    
    # Add attendance records (Nov 27 to present)
    print(f"\n{'='*60}")
    print("Adding attendance records (Nov 27 - Present)...")
    print(f"{'='*60}")
    
    start_date = datetime(2025, 11, 27)
    end_date = datetime.now()
    current_date = start_date
    attendance_count = 0
    
    while current_date <= end_date:
        # Weekdays only (Monday-Friday)
        if current_date.weekday() < 5:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # ITEC 104 attendance
            attendance_data1 = {}
            for student in students:
                # 85% chance of being present
                status = 'present' if random.random() < 0.85 else 'absent'
                attendance_data1[student['student_id']] = {'status': status}
            
            success1 = db.save_attendance(section_id1, date_str, attendance_data1)
            if success1:
                attendance_count += 1
                present_count = sum(1 for data in attendance_data1.values() if data['status'] == 'present')
                print(f"  ✓ ITEC 104 - {date_str}: {present_count}/{len(students)} present")
            
            # CMSC 203 attendance
            attendance_data2 = {}
            for student in students:
                # 85% present chance
                status = 'present' if random.random() < 0.85 else 'absent'
                attendance_data2[student['student_id']] = {'status': status}
            
            success2 = db.save_attendance(section_id2, date_str, attendance_data2)
            if success2:
                attendance_count += 1
                present_count = sum(1 for data in attendance_data2.values() if data['status'] == 'present')
                print(f"  ✓ CMSC 203 - {date_str}: {present_count}/{len(students)} present")
        
        current_date += timedelta(days=1)
    
    print(f"\nTotal attendance records added: {attendance_count}")
    
    # Create archived sections
    print(f"\n{'='*60}")
    print("Creating archived sections...")
    print(f"{'='*60}")
    
    archived_sections = [
        ("CMSC 202", "BSCS 2A", "CMSC 202", "Room 201"),
        ("ITEC 102", "BSCS 2A", "ITEC 102", "Room 202"),
        ("ITEC 106", "BSCS 2A", "ITEC 106", "Room 203")
    ]
    
    archived_count = 0
    for section_name, section, subject, room in archived_sections:
        # Create archived section
        success, message, section_id = db.add_section(
            section_name=section_name,
            user_id=user_id,
            section=section,
            subject=subject,
            room=room
        )
        
        if success or "already exists" in message.lower():
            if not success:
                # Get section ID if exists
                if not db.connect():
                    continue
                cursor = db.connection.cursor()
                cursor.execute("SELECT section_id FROM sections WHERE section_name = %s AND user_id = %s", (section_name, user_id))
                result = cursor.fetchone()
                if result:
                    section_id = result[0]
                cursor.close()
                db.disconnect()
            
            # Add 10 students to archived section
            for student in students[:10]:
                student_data = {
                    'student_id': student['student_id'],
                    'section_id': section_id,
                    'first_name': student['first_name'],
                    'last_name': student['last_name'],
                    'age': student['age'],
                    'email': student['email'],
                    'phone': student['phone'],
                    'birthday': student['birthday'],
                    'address': student['address']
                }
                db.add_student(student_data)
            
            # Archive section
            archive_success, archive_msg = db.archive_section(section_id)
            if archive_success:
                archived_count += 1
                print(f"  ✓ {section_name} archived with 10 students")
    
    print(f"\nTotal archived sections: {archived_count}")
    
    # Add default schedules
    print(f"\n{'='*60}")
    print("Adding default schedules...")
    print(f"{'='*60}")
    
    schedules = [
        # Tuesday
        ("CMSC 203", "BSCS 2B", "Tuesday", "7:00-9:00", "107", "#B5EAD7"),
        ("CMSC 203", "BSCS 2B", "Tuesday", "10:00-1:00", "206", "#F7D08A"),
        
        # Wednesday
        ("CMSC 203", "BSCS 2A", "Wednesday", "7:00-9:00", "102", "#F0C7CF"),
        ("CMSC 203", "BSCS 2A", "Wednesday", "10:00-1:00", "102", "#F0C7CF"),
        ("ITST 301", "BSIT 3D", "Wednesday", "1:00-3:00", "103", "#F0C7CF"),
        
        # Thursday
        ("ITEC 104", "BSCS 2B", "Thursday", "7:00-9:00", "107", "#F0C7CF"),
        ("ITEC 104", "BSCS 2B", "Thursday", "10:00-1:00", "205", "#A3C7D6"),
        ("ITST 301", "BSIT 3D", "Thursday", "2:00-5:00", "105", "#B5EAD7"),
        
        # Friday
        ("ITEC 104", "BSCS 2A", "Friday", "7:00-9:00", "109", "#D5D0D5"),
        ("ITEC 104", "BSCS 2A", "Friday", "10:00-1:00", "201", "#A3C7D6"),
        ("CMSC 308", "BSCS 3B", "Friday", "2:00-5:00", "109", "#A3C7D6"),
        
        # Saturday
        ("CMSC 308", "BSCS 3B", "Saturday", "7:00-12:00", "110", "#D5D0D5"),
        ("CMSC 308", "BSCS 3A", "Saturday", "1:00-5:00", "102", "#F7D08A"),
        
        # Monday
        ("CMSC 308", "BSCS 3A", "Monday", "1:00-5:00", "101", "#F0C7CF"),
    ]
    
    schedule_count = 0
    for subject, section, day, time, room, color in schedules:
        success = db.add_schedule(
            user_id,
            subject,
            section,
            day,
            time,
            room,
            color
        )
        if success:
            schedule_count += 1
            print(f"  ✓ {subject} ({section}) - {day} {time} in Room {room}")
    
    print(f"\nTotal schedules added: {schedule_count}/{len(schedules)}")
    
    print("\n" + "="*60)
    print("Setup complete!")
    print(f"ITEC 104 - BSCS 2B: {added_count1} students, {grades_count1} grades")
    print(f"CMSC 203 - BSCS 2B: {added_count2} students, {grades_count2} grades")
    print(f"Attendance records: {attendance_count} (Nov 27 - Present)")
    print(f"Archived sections: {archived_count}")
    print(f"Schedules: {schedule_count}")
    print("="*60)

if __name__ == "__main__":
    setup_default_sections_and_students()
