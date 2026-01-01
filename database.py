import sqlite3
from datetime import datetime
import json
import os

class DatabaseManager:
    def __init__(self, db_path='chatbot.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS intents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                examples TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent_id INTEGER,
                response_text TEXT NOT NULL,
                response_type TEXT DEFAULT 'text',
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (intent_id) REFERENCES intents (id)
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE,
                name TEXT,
                email TEXT,
                department TEXT,
                year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT,
                query TEXT NOT NULL,
                response TEXT,
                intent_detected TEXT,
                confidence REAL,
                entities TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                user_id INTEGER,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                comments TEXT,
                resolved BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_intent ON conversations(intent_detected)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating)')
            
            conn.commit()
            print("Database tables initialized successfully!")
    
    def add_intent(self, name, description=None, examples=None):
        """Add a new intent to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            examples_json = json.dumps(examples) if examples else None
            
            try:
                cursor.execute('''
                    INSERT INTO intents (name, description, examples)
                    VALUES (?, ?, ?)
                ''', (name, description, examples_json))
                conn.commit()
                print(f"Added intent: {name}")
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Intent already exists
                print(f"Intent '{name}' already exists")
                # Get existing intent ID
                cursor.execute('SELECT id FROM intents WHERE name = ?', (name,))
                result = cursor.fetchone()
                return result[0] if result else None
    
    def add_response(self, intent_name, response_text, response_type='text', metadata=None):
        """Add a response for an intent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get intent_id
            cursor.execute('SELECT id FROM intents WHERE name = ?', (intent_name,))
            result = cursor.fetchone()
            
            if not result:
                intent_id = self.add_intent(intent_name)
            else:
                intent_id = result[0]
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute('''
                INSERT INTO responses (intent_id, response_text, response_type, metadata)
                VALUES (?, ?, ?, ?)
            ''', (intent_id, response_text, response_type, metadata_json))
            
            conn.commit()
            print(f"Added response for intent '{intent_name}': {response_text[:50]}...")
            return cursor.lastrowid
    
    def log_conversation(self, user_id, session_id, query, response, 
                         intent_detected, confidence, entities=None):
        """Log a conversation to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            entities_json = json.dumps(entities) if entities else None
            
            cursor.execute('''
                INSERT INTO conversations 
                (user_id, session_id, query, response, intent_detected, confidence, entities)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, session_id, query, response, intent_detected, confidence, entities_json))
            
            conn.commit()
            return cursor.lastrowid
    
    def add_feedback(self, conversation_id, user_id, rating, comments=None):
        """Add feedback for a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feedback (conversation_id, user_id, rating, comments)
                VALUES (?, ?, ?, ?)
            ''', (conversation_id, user_id, rating, comments))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_conversation_history(self, user_id=None, limit=50, offset=0):
        """Get conversation history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT c.*, u.name, u.student_id
                    FROM conversations c
                    LEFT JOIN users u ON c.user_id = u.id
                    WHERE c.user_id = ?
                    ORDER BY c.timestamp DESC
                    LIMIT ? OFFSET ?
                ''', (user_id, limit, offset))
            else:
                cursor.execute('''
                    SELECT c.*, u.name, u.student_id
                    FROM conversations c
                    LEFT JOIN users u ON c.user_id = u.id
                    ORDER BY c.timestamp DESC
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
            
            columns = [column[0] for column in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                # Parse JSON fields
                if result.get('entities'):
                    try:
                        result['entities'] = json.loads(result['entities'])
                    except:
                        result['entities'] = []
                results.append(result)
            
            return results
    
    def get_statistics(self):
        """Get system statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total conversations
            cursor.execute('SELECT COUNT(*) FROM conversations')
            stats['total_conversations'] = cursor.fetchone()[0]
            
            # Unique users
            cursor.execute('SELECT COUNT(DISTINCT user_id) FROM conversations WHERE user_id IS NOT NULL')
            stats['unique_users'] = cursor.fetchone()[0]
            
            # Intents used
            cursor.execute('SELECT COUNT(DISTINCT intent_detected) FROM conversations')
            stats['unique_intents'] = cursor.fetchone()[0]
            
            # Average confidence
            cursor.execute('SELECT AVG(confidence) FROM conversations WHERE confidence IS NOT NULL')
            avg_conf = cursor.fetchone()[0]
            stats['avg_confidence'] = round(float(avg_conf or 0), 2)
            
            # Feedback statistics
            cursor.execute('SELECT COUNT(*), AVG(rating) FROM feedback')
            feedback_result = cursor.fetchone()
            stats['total_feedback'] = feedback_result[0]
            avg_rating = feedback_result[1] or 0
            stats['avg_rating'] = round(float(avg_rating), 1)
            
            # Recent activity (last 24 hours)
            cursor.execute('''
                SELECT COUNT(*) FROM conversations 
                WHERE timestamp >= datetime('now', '-1 day')
            ''')
            stats['recent_conversations'] = cursor.fetchone()[0]
            
            # Most common intents
            cursor.execute('''
                SELECT intent_detected, COUNT(*) as count 
                FROM conversations 
                WHERE intent_detected IS NOT NULL 
                GROUP BY intent_detected 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            stats['top_intents'] = cursor.fetchall()
            
            return stats
    
    def get_intent_responses(self, intent_name):
        """Get all responses for an intent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT r.response_text, r.response_type, r.metadata
                FROM responses r
                JOIN intents i ON r.intent_id = i.id
                WHERE i.name = ?
            ''', (intent_name,))
            
            responses = []
            for row in cursor.fetchall():
                response = {
                    'text': row[0],
                    'type': row[1],
                    'metadata': json.loads(row[2]) if row[2] else None
                }
                responses.append(response)
            
            return responses
    
    def add_user(self, student_id, name=None, email=None, department=None, year=None):
        """Add a new user to the system"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO users (student_id, name, email, department, year)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, name, email, department, year))
            
            conn.commit()
            
            # Get the user_id
            cursor.execute('SELECT id FROM users WHERE student_id = ?', (student_id,))
            result = cursor.fetchone()
            
            return result[0] if result else None
    
    def clear_all_data(self):
        """Clear all data from database (for testing/reset)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM feedback')
            cursor.execute('DELETE FROM conversations')
            cursor.execute('DELETE FROM responses')
            cursor.execute('DELETE FROM intents')
            cursor.execute('DELETE FROM users')
            
            # Reset autoincrement counters
            cursor.execute('DELETE FROM sqlite_sequence')
            
            conn.commit()
            print("All data cleared from database!")
    
    def export_data(self, format='json'):
        """Export database data"""
        data = {
            'intents': [],
            'responses': [],
            'conversations': [],
            'feedback': []
        }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Export intents
            cursor.execute('SELECT * FROM intents')
            for row in cursor.fetchall():
                intent = dict(row)
                if intent.get('examples'):
                    intent['examples'] = json.loads(intent['examples'])
                data['intents'].append(intent)
            
            # Export responses
            cursor.execute('''
                SELECT r.*, i.name as intent_name 
                FROM responses r
                JOIN intents i ON r.intent_id = i.id
            ''')
            for row in cursor.fetchall():
                response = dict(row)
                if response.get('metadata'):
                    response['metadata'] = json.loads(response['metadata'])
                data['responses'].append(response)
            
            # Export conversations (limit to 1000)
            cursor.execute('SELECT * FROM conversations ORDER BY timestamp DESC LIMIT 1000')
            for row in cursor.fetchall():
                conv = dict(row)
                if conv.get('entities'):
                    conv['entities'] = json.loads(conv['entities'])
                data['conversations'].append(conv)
            
            # Export feedback
            cursor.execute('SELECT * FROM feedback')
            for row in cursor.fetchall():
                data['feedback'].append(dict(row))
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        return data

# Initialize database and add sample data
if __name__ == '__main__':
    print("=" * 60)
    print("DATABASE SETUP FOR STUDENT CHATBOT")
    print("=" * 60)
    
    db = DatabaseManager()
    
    # Ask if user wants to clear existing data
    response = input("Clear existing database data? (y/n): ").lower()
    if response == 'y':
        db.clear_all_data()
        print("Database cleared!")
    
    # Add sample intents
    print("\nAdding sample intents...")
    sample_intents = [
        ('greeting', 'Greeting messages', ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']),
        ('attendance', 'Attendance related queries', ['attendance', 'present percentage', 'attendance record', 'how many days present', 'attendance policy']),
        ('exam_schedule', 'Exam schedule queries', ['exam dates', 'when are exams', 'exam schedule', 'final exam timetable', 'mid term exams', 'exam timetable']),
        ('fees', 'Fee related queries', ['fee payment', 'tuition fees', 'semester fees', 'payment deadline', 'how to pay fees', 'fee structure']),
        ('courses', 'Course related queries', ['available courses', 'course registration', 'elective subjects', 'course syllabus', 'register for courses', 'subjects']),
        ('library', 'Library related queries', ['library timings', 'library hours', 'borrow books', 'library card', 'library rules', 'book return']),
        ('hostel', 'Hostel related queries', ['hostel admission', 'hostel fees', 'hostel facilities', 'room allotment', 'hostel rules', 'hostel food']),
        ('transport', 'Transport related queries', ['bus schedule', 'college bus', 'transport fees', 'bus routes', 'transport facility']),
        ('results', 'Results and grades', ['exam results', 'marks', 'grades', 'result declaration', 'grade card']),
        ('faculty', 'Faculty information', ['faculty details', 'professor contact', 'teacher information', 'department faculty'])
    ]
    
    for intent in sample_intents:
        db.add_intent(intent[0], intent[1], intent[2])
    
    # Add sample responses
    print("\nAdding sample responses...")
    sample_responses = [
        ('greeting', 'Hello! Welcome to Student Query Assistant. How can I help you today?'),
        ('greeting', 'Hi there! I\'m here to assist with your academic queries. What would you like to know?'),
        ('greeting', 'Welcome! I can help you with exam schedules, attendance, fees, courses, and more. How can I assist you?'),
        
        ('attendance', 'Attendance records can be viewed on the student portal under "My Attendance" section.'),
        ('attendance', 'You need minimum 75% attendance to appear for exams. Check your current percentage on the portal.'),
        ('attendance', 'Attendance is updated every Friday by your class coordinator. Contact them if there are discrepancies.'),
        
        ('exam_schedule', 'The exam schedule for this semester will be published on December 1st on the university website.'),
        ('exam_schedule', 'Mid-term exams start next week. Check your department notice board for the detailed schedule.'),
        ('exam_schedule', 'Final exams are usually held in May and December. The exact dates will be announced one month prior.'),
        
        ('fees', 'The last date for fee payment is 15th of every month. Late fees apply after the deadline.'),
        ('fees', 'You can pay fees online through the university payment gateway using credit/debit cards or net banking.'),
        ('fees', 'Fee structure is available in the academic handbook. Contact accounts office for detailed breakdown.'),
        
        ('courses', 'Course registration for next semester opens on January 10th and closes on January 20th.'),
        ('courses', 'The complete course list and syllabus are available in the academic handbook on the department website.'),
        ('courses', 'You can choose elective subjects during the registration period. Consult your academic advisor for guidance.'),
        
        ('library', 'Library timings: Monday to Friday - 8 AM to 8 PM, Saturday - 9 AM to 5 PM, Sunday - Closed'),
        ('library', 'You can borrow up to 5 books for 15 days with your student ID card.'),
        ('library', 'Online library resources are available 24/7 through the library portal with your student login.'),
        
        ('hostel', 'Hostel admission for new students starts from July 1st. Forms are available at the hostel office.'),
        ('hostel', 'Hostel fees: Single room - ₹50,000/semester, Double sharing - ₹35,000/semester.'),
        ('hostel', 'Hostel facilities include Wi-Fi, laundry, gym, and 24/7 security. Visit hostel office for details.'),
        
        ('transport', 'College bus schedule: Morning - 7:30 AM to 9:30 AM, Evening - 4:30 PM to 6:30 PM.'),
        ('transport', 'Transport fees: ₹8,000 per semester. Bus routes cover all major areas of the city.'),
        ('transport', 'Bus passes can be obtained from the transport office with valid student ID and fee receipt.'),
        
        ('results', 'Semester results are declared within 45 days of the last exam. Check the university website.'),
        ('results', 'Marksheets can be collected from the examination office 15 days after result declaration.'),
        ('results', 'For revaluation, apply within 10 days of result declaration with ₹500 fee per paper.'),
        
        ('faculty', 'Faculty contact details are available on the department website under "Faculty" section.'),
        ('faculty', 'You can meet faculty during their office hours: Monday to Friday, 2 PM to 4 PM.'),
        ('faculty', 'For academic queries, contact your class coordinator or department head.')
    ]
    
    for response in sample_responses:
        db.add_response(response[0], response[1])
    
    # Add a sample user
    print("\nAdding sample user...")
    user_id = db.add_user(
        student_id='2023001',
        name='John Doe',
        email='john.doe@university.edu',
        department='Computer Science',
        year=3
    )
    
    # Log some sample conversations
    print("\nLogging sample conversations...")
    sample_conversations = [
        (user_id, 'session_001', 'hello', 'Hello! Welcome to Student Query Assistant.', 'greeting', 0.95),
        (user_id, 'session_001', 'when is exam?', 'Exam schedules are published one month before exams.', 'exam_schedule', 0.88),
        (user_id, 'session_001', 'attendance percentage', 'Attendance records can be viewed on the student portal.', 'attendance', 0.92),
        (user_id, 'session_001', 'how to pay fees?', 'You can pay fees online through the university payment gateway.', 'fees', 0.90),
        (user_id, 'session_001', 'library timings', 'Library timings: Monday to Friday - 8 AM to 8 PM.', 'library', 0.94)
    ]
    
    for conv in sample_conversations:
        db.log_conversation(*conv)
    
    # Add sample feedback
    print("\nAdding sample feedback...")
    db.add_feedback(1, user_id, 5, 'Very helpful!')
    db.add_feedback(2, user_id, 4, 'Good response')
    db.add_feedback(3, user_id, 5, 'Accurate information')
    
    # Display statistics
    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    
    stats = db.get_statistics()
    print(f"Total conversations: {stats['total_conversations']}")
    print(f"Unique users: {stats['unique_users']}")
    print(f"Unique intents: {stats['unique_intents']}")
    print(f"Average confidence: {stats['avg_confidence']}")
    print(f"Total feedback: {stats['total_feedback']}")
    print(f"Average rating: {stats['avg_rating']}/5")
    print(f"Recent conversations (24h): {stats['recent_conversations']}")
    
    print("\nTop 5 intents:")
    for intent, count in stats['top_intents']:
        print(f"  {intent}: {count}")
    
    print("\n" + "=" * 60)
    print("Database setup completed successfully!")
    print("=" * 60)
    print("\nYou can now run: python app.py")