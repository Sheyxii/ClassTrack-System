"""
Script to populate BSCS 2B section with default students from JSON file
Run this once to add the 26 default students to your database
"""

import json
import os
from .database import DatabaseConnection

def populate_bscs2b(silent=False):
    """Load default students from JSON and add them to BSCS 2B section"""
    
    db = DatabaseConnection()
    
    # User ID (default admin user = 1, change if needed)
    user_id = 1
    section_name = "BSCS 2B"
    
    if not silent:
        print(f"Starting population of {section_name}...")
        print("=" * 60)
    
    # Step 1: Create or get BSCS 2B section
    if not silent:
        print(f"\n1. Checking if section '{section_name}' exists...")
    sections = db.get_sections(user_id, include_archived=False)
    section_id = None
    
    for section in sections:
        if section['section_name'] == section_name:
            section_id = section['section_id']
            if not silent:
                print(f"   ✓ Section found (ID: {section_id})")
            break
    
    if not section_id:
        if not silent:
            print(f"   Creating new section '{section_name}'...")
        success, message, section_id = db.add_section(section_name, user_id)
        if success:
            if not silent:
                print(f"   ✓ Section created successfully (ID: {section_id})")
        else:
            if not silent:
                print(f"   ✗ Error creating section: {message}")
            return
    
    # Step 2: Check if section already has students
    existing_students = db.get_students(section_id, include_archived=False)
    if len(existing_students) >= 26:
        if not silent:
            print(f"   ℹ Section already has {len(existing_students)} students. Skipping population.")
        return
    
    # Step 3: Load students from JSON file
    if not silent:
        print(f"\n2. Loading students from default_students.json...")
    try:
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'default_students.json')
        
        with open(json_path, 'r', encoding='utf-8') as file:
            students_data = json.load(file)
        if not silent:
            print(f"   ✓ Loaded {len(students_data)} students from JSON")
    except FileNotFoundError:
        if not silent:
            print("   ✗ Error: default_students.json not found in utils/ folder")
        return
    except json.JSONDecodeError as e:
        if not silent:
            print(f"   ✗ Error parsing JSON file: {e}")
        return
    
    # Step 4: Add section_id to each student
    for student in students_data:
        student['section_id'] = section_id
    
    # Step 5: Insert students into database
    if not silent:
        print(f"\n3. Adding students to database...")
        print("-" * 60)
    
    success_count, failed_count, messages = db.add_students_batch(students_data)
    
    # Display results
    if not silent:
        for message in messages:
            print(f"   {message}")
    
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY:")
        print(f"   Total students processed: {len(students_data)}")
        print(f"   ✓ Successfully added: {success_count}")
        print(f"   ✗ Failed: {failed_count}")
        print("=" * 60)
        
        if success_count > 0:
            print(f"\n🎉 Successfully populated {section_name} with {success_count} students!")
        
        if failed_count > 0:
            print(f"\n⚠️  {failed_count} students failed to add (possibly duplicates)")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BSCS 2B POPULATION SCRIPT")
    print("=" * 60)
    
    try:
        populate_bscs2b()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    input("\nPress Enter to exit...")
