import sys
sys.path.append('.')
from utils.database import DatabaseConnection

def cleanup_duplicate_schedules():
    """Remove duplicate schedules from the database."""
    db = DatabaseConnection()
    
    if not db.connect():
        print("❌ Failed to connect to database")
        return
    
    try:
        cursor = db.connection.cursor()
        
        # Get all schedules
        cursor.execute("SELECT * FROM schedules ORDER BY schedule_id")
        all_schedules = cursor.fetchall()
        
        print(f"Total schedules in database: {len(all_schedules)}\n")
        
        # Track seen schedules and duplicates
        seen = {}
        duplicates = []
        
        for schedule in all_schedules:
            schedule_id = schedule[0]
            user_id = schedule[1]
            subject = schedule[2]
            section = schedule[3]
            day = schedule[4]
            time = schedule[5]
            room = schedule[6]
            
            # Create a unique key for this schedule
            key = (user_id, subject, section, day, time, room)
            
            if key in seen:
                # This is a duplicate
                duplicates.append(schedule_id)
                print(f"❌ DUPLICATE: ID={schedule_id} - {subject} ({section}) on {day} {time} Room {room}")
            else:
                seen[key] = schedule_id
                print(f"✓ KEEP: ID={schedule_id} - {subject} ({section}) on {day} {time} Room {room}")
        
        if duplicates:
            print(f"\n{'='*60}")
            print(f"Found {len(duplicates)} duplicate schedule(s)")
            print(f"{'='*60}")
            
            response = input("\nDelete duplicates? (yes/no): ").lower()
            
            if response == 'yes':
                deleted_count = 0
                for schedule_id in duplicates:
                    cursor.execute("DELETE FROM schedules WHERE schedule_id = %s", (schedule_id,))
                    deleted_count += 1
                
                db.connection.commit()
                print(f"\n✓ Deleted {deleted_count} duplicate schedule(s)")
            else:
                print("\nCancelled - no changes made")
        else:
            print("\n✓ No duplicates found!")
        
        cursor.close()
        db.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.disconnect()

if __name__ == "__main__":
    cleanup_duplicate_schedules()
