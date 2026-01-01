from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import random
import sqlite3
import os
from typing import Dict, List
import uuid

app = Flask(__name__)
app.secret_key = 'ai_student_chatbot_secret_2024'
CORS(app, supports_credentials=True)

# Enhanced knowledge base
KNOWLEDGE_BASE = {
    "academics": {
        "exams": {
            "patterns": ["exam", "schedule", "date", "timetable", "mid term", "final", "semester"],
            "responses": [
                "📅 **Exam Schedule 2024-25:**\n• Mid-term Exams: **Oct 15-30, 2024**\n• Final Exams: **Dec 10-25, 2024**\n• Practical Exams: **Nov 5-15, 2024**\n• Supplementary Exams: **Jan 5-10, 2025**\n\n📱 Check your personalized schedule on the student portal!",
                "🎯 **Important Exam Dates:**\n✅ Semester 3 & 5: **Nov 10-25, 2024**\n✅ Semester 7: **Dec 1-15, 2024**\n✅ Project Viva: **Dec 20-30, 2024**\n✅ Result Declaration: Within **45 days**\n\n⚠️ **Hall tickets** available 7 days before exams",
                "📋 **Exam Guidelines:**\n• Duration: **3 hours**\n• Passing: **40% minimum**\n• ID Card: **Mandatory**\n• Calculator: **Non-programmable only**\n• Dress Code: **Formal (No casuals)**\n\n💡 **Pro Tip:** Start revision at least 2 weeks in advance!"
            ]
        },
        "attendance": {
            "patterns": ["attendance", "present", "absent", "percentage", "shortage", "leave"],
            "responses": [
                "📊 **Attendance Policy:**\n✅ **Minimum Required:** **75%**\n✅ **Current Average:** **82%** (Good! 🎉)\n✅ **Next Update:** **Every Friday**\n✅ **Deficiency Notice:** Below **60%**\n\n👀 View detailed report: **Student Portal → My Attendance**",
                "⚠️ **Attendance Alerts:**\nIf below 75%:\n1. Submit **medical certificate** within 3 days\n2. Meet **HOD** for condonation\n3. Attend **extra classes** if arranged\n4. Submit **leave application** online\n\n📅 Check daily to avoid shortage!",
                "🎯 **Your Attendance Status:**\n• Last Updated: **Today**\n• Current Percentage: **84%** ✅\n• Required Percentage: **75%**\n• Status: **GOOD** (Keep it up! 🚀)\n\n📱 Get notifications on the college app"
            ]
        },
        "courses": {
            "patterns": ["course", "subject", "syllabus", "elective", "credit", "registration", "curriculum"],
            "responses": [
                "📚 **Course Registration 2025:**\n🔄 **Registration Period:** **Jan 10-20, 2025**\n📋 **Maximum Credits:** **24 per semester**\n🎯 **Elective Choices:** **2 subjects**\n💰 **Late Fee:** **₹500/day** after deadline\n\n💡 **Pro Tip:** Consult your academic advisor before selection!",
                "🔍 **Available Courses (CS Department):**\n• **AI & Machine Learning** (4 credits)\n• **Cloud Computing** (3 credits)\n• **Cybersecurity** (3 credits)\n• **Data Science** (4 credits)\n• **IoT & Embedded Systems** (3 credits)\n• **Blockchain Technology** (3 credits)\n\n📖 Complete syllabus on department website",
                "✅ **Registration Steps:**\n1. Login to **student portal**\n2. Go to **Course Registration**\n3. Select **preferred courses**\n4. Verify **prerequisites**\n5. **Submit** by deadline\n6. Pay **fees** if applicable\n7. Download **acknowledgment**"
            ]
        },
        "results": {
            "patterns": ["result", "mark", "grade", "cgpa", "score", "backlog", "supplementary"],
            "responses": [
                "🏆 **Result Updates:**\n• Semester 4: **Declared ✅** (Download marksheet)\n• Semester 6: **Processing ⏳**\n• Revaluation: **Open for 10 days**\n• Supplementary: **Registration open**\n\n📥 Download from: **universityresults.edu.in**",
                "📈 **Grading System:**\n• **O (Outstanding):** 90-100 (10 points)\n• **A+ (Excellent):** 80-89 (9 points)\n• **A (Very Good):** 70-79 (8 points)\n• **B+ (Good):** 60-69 (7 points)\n• **B (Above Average):** 50-59 (6 points)\n• **C (Average):** 40-49 (5 points)\n• **F (Fail):** Below 40 (0 points)",
                "🔄 **Backlog Process:**\n1. Register for **backlog exam** online\n2. Pay **₹500/subject**\n3. Attend **special classes** (optional)\n4. Appear for **exam** in next cycle\n5. Clear within **4 semesters** max\n\n📞 Contact: **Examination Office, Block C**"
            ]
        }
    },
    "administration": {
        "fees": {
            "patterns": ["fee", "payment", "tuition", "scholarship", "installment", "refund"],
            "responses": [
                "💰 **Fee Structure 2024-25:**\n• **Tuition Fee:** ₹75,000/semester\n• **Library Fee:** ₹2,000\n• **Lab Fee:** ₹5,000\n• **Hostel Fee:** ₹35,000\n• **Exam Fee:** ₹3,000\n• **Total:** ₹1,20,000\n\n💳 **Payment Options:**\n✅ Online Portal (24/7)\n✅ UPI (GPay/PhonePe)\n✅ Credit/Debit Card\n✅ Net Banking\n✅ Cash (Only at counter)",
                "⏰ **Payment Deadlines:**\n• **Semester 1:** Aug 15, 2024\n• **Semester 3:** Jan 15, 2025\n• **Late Fee:** ₹500/day\n• **Final Date:** 30 days grace\n\n🎓 **Scholarships Available:**\n• **Merit-based:** 25-100% waiver\n• **Need-based:** Apply by Aug 30\n• **Sports quota:** Submit certificates\n• **SC/ST:** Full waiver available",
                "📱 **Quick Pay Guide:**\n1. Login to **student portal**\n2. Go to **Finance Section**\n3. Select **payment method**\n4. Enter **amount**\n5. **Confirm** payment\n6. Download **receipt**\n7. **Print** for records\n\n🆘 Help: **accounts@university.edu**"
            ]
        },
        "documents": {
            "patterns": ["document", "certificate", "transcript", "id card", "bonafide", "migration", "character"],
            "responses": [
                "📄 **Document Services:**\n• **Transcript:** ₹200, 3 working days\n• **Bonafide Certificate:** Free, 1 day\n• **ID Card (Duplicate):** ₹100, 7 days\n• **Migration Certificate:** ₹500, 10 days\n• **Character Certificate:** ₹150, 2 days\n\n📍 Apply at: **Admin Office, Block A**",
                "🖨️ **Document Request Process:**\n1. Login to **student portal**\n2. Fill **document request form**\n3. Pay **fees online**\n4. Collect from **office**\n5. Or get **soft copy** via email\n\n⏰ Office Hours: **10 AM - 4 PM (Mon-Fri)**",
                "🔒 **Lost Documents?**\n1. File **police complaint** (if ID card)\n2. Submit **application form**\n3. Pay **duplicate fee**\n4. Wait **7-10 working days**\n5. Collect with **ID proof**\n\n⚠️ Keep digital copies as backup!"
            ]
        }
    },
    "campus": {
        "library": {
            "patterns": ["library", "book", "journal", "database", "research", "study"],
            "responses": [
                "📚 **Library Facilities:**\n⏰ **Timings:** 8 AM - 10 PM (Mon-Sat), 9 AM - 5 PM (Sun)\n📖 **Collection:** 50,000+ books, 100+ journals\n💻 **E-Resources:** IEEE, Springer, Elsevier (24/7)\n🎧 **Study Rooms:** 15 rooms (book in advance)\n☕ **Cafe:** Inside library (8 AM - 8 PM)\n\n🔍 **Virtual Tour:** Scan QR code at entrance!",
                "🔍 **How to Search & Issue:**\n1. Visit **library portal**\n2. Enter **ISBN/title/author**\n3. Check **availability**\n4. Note **shelf number**\n5. Issue at **counter**\n6. Max: **5 books for 15 days**\n\n💰 **Fine:** ₹5/day after due date",
                "🌟 **Special Collections:**\n• **Rare Manuscripts Section**\n• **Research Paper Archive**\n• **International Journals**\n• **Thesis Collection**\n• **Digital Archives**\n\n👨‍💼 **Librarian:** Dr. Sharma (Ext. 456)"
            ]
        },
        "hostel": {
            "patterns": ["hostel", "room", "mess", "accommodation", "laundry", "gym"],
            "responses": [
                "🏠 **Hostel Facilities:**\n• **Rooms:** AC/Non-AC options\n• **Wi-Fi:** High-speed (100 Mbps)\n• **Gym:** 6 AM - 10 PM\n• **Laundry:** Free (Mon-Sat)\n• **Medical:** 24/7 nurse available\n• **Security:** CCTV + guards\n\n📞 **Warden:** Mr. Gupta (9876543210)",
                "🍽️ **Mess Details:**\n• **Veg/Non-veg** separate kitchens\n• **Breakfast:** 7-9 AM\n• **Lunch:** 12-2 PM\n• **Dinner:** 7-9 PM\n• **Special diet** on request\n• **Monthly Charges:** ₹4,500\n\n📱 **Complaints:** Use college app",
                "📝 **Hostel Admission Process:**\n1. Apply **online** (priority basis)\n2. Submit **documents**\n3. Pay **advance** (₹10,000)\n4. **Room allotment**\n5. **Move-in** within 7 days\n\n🎯 **Priority:** Distance > Merit > First-come"
            ]
        },
        "transport": {
            "patterns": ["bus", "transport", "vehicle", "shuttle", "commute", "parking"],
            "responses": [
                "🚌 **Bus Schedule 2024:**\n🔼 **Morning Pickups:** 6:30, 7:15, 8:00, 8:45 AM\n🔽 **Evening Returns:** 4:00, 4:45, 5:30, 6:15 PM\n📍 **Routes:** Covers all major areas\n💵 **Fee:** ₹8,000/semester\n\n📱 **Live Tracking:** Download 'College Bus Tracker' app",
                "🎫 **Bus Pass Procedure:**\n1. Apply at **transport office**\n2. Submit **ID proof + photo**\n3. Pay **fees**\n4. Get **pass** in 2 days\n5. **Renew** each semester\n\n⚠️ **Lost Pass?** Report immediately! ₹200 fine",
                "🛵 **Other Transport Options:**\n• **Campus Shuttle:** Free (8 AM - 6 PM)\n• **Cycle Rent:** ₹500/month\n• **Car Parking:** ₹2,000/semester\n• **EV Charging:** Free for students\n\n🌱 **Carpool encouraged!** Save environment"
            ]
        }
    },
    "support": {
        "greeting": {
            "patterns": ["hello", "hi", "hey", "good morning", "good afternoon", "greetings"],
            "responses": [
                "🌟 **Hello there!** 🤖\nI'm your **AI Student Assistant**, here to help you 24/7!\n\n💡 **Try asking about:**\n• **Exam schedules** 📅\n• **Fee payments** 💰\n• **Library resources** 📚\n• **Hostel facilities** 🏠\n• **Campus events** 🎉\n• **Document services** 📄\n\n🎯 **Quick Tip:** Use the buttons or type naturally!",
                "👋 **Welcome back!** 🚀\nHow can I assist you today?\n\n📱 **Available Features:**\n✅ **Quick Actions** (sidebar)\n✅ **Voice Input** (coming soon)\n✅ **File Upload** (coming soon)\n✅ **Chat History**\n✅ **Smart Suggestions**\n\n💬 Just ask anything!",
                "🤖 **Hi! I'm ready to help!** 💫\n\n🎓 **I can assist with:**\n1. **Academic Queries** (exams, courses, results)\n2. **Administration** (fees, documents)\n3. **Campus Life** (library, hostel, transport)\n4. **Support & Guidance**\n\n🔍 Use keywords for faster results!"
            ]
        },
        "help": {
            "patterns": ["help", "support", "guide", "tutorial", "how to", "assistance"],
            "responses": [
                "🆘 **Help Center:**\n1. **Academic Support:** Exams, courses, attendance\n2. **Administration:** Fees, documents, certificates\n3. **Campus Services:** Library, hostel, transport\n4. **Technical Support:** Portal issues, login problems\n5. **Emergency:** Contact numbers, first aid\n\n📞 **Human Support:** 1800-123-456 (24/7)",
                "📖 **Getting Started Guide:**\n• Use **quick buttons** for common questions\n• **Type naturally** - I understand context\n• **Check analytics** for statistics\n• **Rate responses** to help me improve\n• **Save conversations** for reference\n• **Export chat** if needed\n\n🔧 Need specific help? Just ask!",
                "🔗 **Useful Contacts:**\n• **Academic Office:** Ext. 101\n• **Accounts Department:** Ext. 102\n• **Library:** Ext. 103\n• **Hostel Office:** Ext. 104\n• **Transport:** Ext. 105\n• **IT Helpdesk:** Ext. 106\n• **Emergency:** Ext. 107\n\n📧 **Email:** support@university.edu"
            ]
        }
    }
}

class ChatbotAI:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect('chatbot_ai.db')
        c = conn.cursor()
        
        # Conversations table
        c.execute('''CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    category TEXT,
                    subcategory TEXT,
                    confidence REAL,
                    sentiment TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
        
        # Analytics table
        c.execute('''CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    metric_value REAL,
                    recorded_date DATE DEFAULT CURRENT_DATE
                )''')
        
        # Create indexes
        c.execute('CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_category ON conversations(category)')
        
        conn.commit()
        conn.close()
        
        # Initialize sample data if empty
        self.initialize_sample_data()
    
    def initialize_sample_data(self):
        """Initialize with sample conversations"""
        conn = sqlite3.connect('chatbot_ai.db')
        c = conn.cursor()
        
        # Check if we have data
        c.execute('SELECT COUNT(*) FROM conversations')
        count = c.fetchone()[0]
        
        if count == 0:
            sample_data = [
                ('session_sample_1', 'hello', 'Hello! How can I help?', 'support', 'greeting', 0.95, 'positive'),
                ('session_sample_1', 'exam schedule', 'Exams start in December', 'academics', 'exams', 0.92, 'neutral'),
                ('session_sample_1', 'fee payment', 'Pay online through portal', 'administration', 'fees', 0.88, 'neutral'),
                ('session_sample_2', 'library timings', 'Library open 8 AM to 8 PM', 'campus', 'library', 0.94, 'positive'),
                ('session_sample_2', 'hostel admission', 'Apply online for hostel', 'campus', 'hostel', 0.91, 'positive'),
                ('session_sample_3', 'attendance percentage', 'Check on student portal', 'academics', 'attendance', 0.89, 'neutral'),
                ('session_sample_3', 'course registration', 'Registration opens Jan 10', 'academics', 'courses', 0.93, 'positive'),
                ('session_sample_4', 'bus schedule', 'Buses from 6:30 AM', 'campus', 'transport', 0.90, 'neutral'),
                ('session_sample_4', 'results', 'Results declared on portal', 'academics', 'results', 0.87, 'neutral'),
                ('session_sample_5', 'documents', 'Get certificates from admin office', 'administration', 'documents', 0.91, 'positive')
            ]
            
            for data in sample_data:
                c.execute('''INSERT INTO conversations 
                            (session_id, query, response, category, subcategory, confidence, sentiment)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
            
            print("✅ Sample data initialized in database")
        
        conn.commit()
        conn.close()
    
    def analyze_query(self, query: str) -> Dict:
        """Analyze user query to determine intent"""
        query_lower = query.lower().strip()
        
        # Default values
        result = {
            "category": "support",
            "subcategory": "help",
            "confidence": 0.5,
            "sentiment": "neutral",
            "matched_patterns": []
        }
        
        # Check each category and subcategory
        for category, subcats in KNOWLEDGE_BASE.items():
            for subcategory, data in subcats.items():
                for pattern in data['patterns']:
                    if pattern in query_lower:
                        result["matched_patterns"].append(pattern)
                        result["category"] = category
                        result["subcategory"] = subcategory
                        result["confidence"] = min(0.95, result["confidence"] + 0.2)
        
        # Adjust confidence based on number of matches
        if len(result["matched_patterns"]) > 0:
            result["confidence"] = min(0.95, 0.7 + (len(result["matched_patterns"]) * 0.1))
        
        # Simple sentiment analysis
        positive_words = ['thanks', 'thank', 'good', 'great', 'excellent', 'helpful', 'awesome']
        negative_words = ['bad', 'wrong', 'error', 'not working', 'problem', 'poor', 'terrible']
        
        for word in positive_words:
            if word in query_lower:
                result["sentiment"] = "positive"
                break
        
        for word in negative_words:
            if word in query_lower:
                result["sentiment"] = "negative"
                break
        
        return result
    
    def generate_response(self, analysis: Dict) -> str:
        """Generate response based on analysis"""
        category = analysis["category"]
        subcategory = analysis["subcategory"]
        
        if category in KNOWLEDGE_BASE and subcategory in KNOWLEDGE_BASE[category]:
            responses = KNOWLEDGE_BASE[category][subcategory]['responses']
            response = random.choice(responses)
            
            # Add sentiment-based closing
            if analysis["sentiment"] == "positive":
                response += "\n\n😊 **Glad I could help!** Anything else you'd like to know?"
            elif analysis["sentiment"] == "negative":
                response += "\n\n😔 **Sorry if this wasn't helpful.** Would you like to speak with a human assistant?"
            else:
                response += "\n\n💡 **Need more details?** Just ask!"
            
            # Add confidence note
            if analysis["confidence"] < 0.7:
                response += "\n\n⚠️ *Note: I'm not completely sure about this. Please verify with official sources.*"
            
            return response
        else:
            return "🤔 **I'm not sure about that.** Could you rephrase or ask something else?\n\n💡 **Try these:**\n• 'Exam schedule for next semester'\n• 'How to pay fees online'\n• 'Library opening hours'\n• 'Hostel admission process'"
    
    def process_query(self, query: str, session_id: str) -> Dict:
        """Process a user query and return response"""
        # Analyze query
        analysis = self.analyze_query(query)
        
        # Generate response
        response = self.generate_response(analysis)
        
        # Store in database
        self.store_conversation(session_id, query, response, analysis)
        
        return {
            "response": response,
            "category": analysis["category"],
            "subcategory": analysis["subcategory"],
            "confidence": analysis["confidence"],
            "sentiment": analysis["sentiment"],
            "matched_patterns": analysis["matched_patterns"],
            "timestamp": datetime.now().isoformat()
        }
    
    def store_conversation(self, session_id: str, query: str, response: str, analysis: Dict):
        """Store conversation in database"""
        try:
            conn = sqlite3.connect('chatbot_ai.db')
            c = conn.cursor()
            
            c.execute('''INSERT INTO conversations 
                        (session_id, query, response, category, subcategory, confidence, sentiment)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (session_id, query, response, analysis["category"], 
                      analysis["subcategory"], analysis["confidence"], analysis["sentiment"]))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error storing conversation: {e}")
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        try:
            conn = sqlite3.connect('chatbot_ai.db')
            c = conn.cursor()
            
            # Total conversations
            c.execute('SELECT COUNT(*) FROM conversations')
            total_queries = c.fetchone()[0] or 0
            
            # Unique sessions (last 30 days)
            c.execute('''SELECT COUNT(DISTINCT session_id) FROM conversations 
                        WHERE timestamp >= datetime('now', '-30 days')''')
            unique_users = c.fetchone()[0] or 1
            
            # Average confidence
            c.execute('SELECT AVG(confidence) FROM conversations WHERE confidence IS NOT NULL')
            avg_conf = c.fetchone()[0]
            avg_confidence = round(float(avg_conf or 0.85), 3)
            
            # Recent activity (last 24 hours)
            c.execute('''SELECT COUNT(*) FROM conversations 
                        WHERE timestamp >= datetime('now', '-1 day')''')
            recent_activity = c.fetchone()[0] or 0
            
            # Today's activity
            c.execute('''SELECT COUNT(*) FROM conversations 
                        WHERE DATE(timestamp) = DATE('now')''')
            today_activity = c.fetchone()[0] or 0
            
            # Category distribution
            c.execute('''SELECT category, COUNT(*) as count 
                        FROM conversations 
                        WHERE category IS NOT NULL 
                        GROUP BY category 
                        ORDER BY count DESC''')
            category_data = c.fetchall()
            
            # Most common queries
            c.execute('''SELECT query, COUNT(*) as frequency 
                        FROM conversations 
                        GROUP BY query 
                        ORDER BY frequency DESC 
                        LIMIT 5''')
            common_queries = c.fetchall()
            
            # Success rate (based on confidence > 0.7)
            c.execute('''SELECT COUNT(*) FROM conversations WHERE confidence >= 0.7''')
            successful = c.fetchone()[0] or 0
            success_rate = round((successful / total_queries * 100) if total_queries > 0 else 95, 1)
            
            conn.close()
            
            return {
                "success": True,
                "total_queries": total_queries,
                "unique_users": unique_users,
                "avg_confidence": avg_confidence,
                "success_rate": success_rate,
                "recent_activity": recent_activity,
                "today_activity": today_activity,
                "categories": [
                    {"name": cat[0], "count": cat[1], "percentage": round((cat[1] / total_queries * 100) if total_queries > 0 else 0, 1)}
                    for cat in category_data
                ],
                "common_queries": [
                    {"query": q[0], "frequency": q[1]}
                    for q in common_queries
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            # Return fallback statistics
            return {
                "success": False,
                "total_queries": 156,
                "unique_users": 24,
                "avg_confidence": 0.87,
                "success_rate": 92.5,
                "recent_activity": 12,
                "today_activity": 8,
                "categories": [
                    {"name": "academics", "count": 85, "percentage": 54.5},
                    {"name": "administration", "count": 42, "percentage": 26.9},
                    {"name": "campus", "count": 29, "percentage": 18.6}
                ],
                "common_queries": [
                    {"query": "exam schedule", "frequency": 23},
                    {"query": "fee payment", "frequency": 18},
                    {"query": "library timings", "frequency": 15},
                    {"query": "attendance", "frequency": 12},
                    {"query": "hostel facilities", "frequency": 10}
                ],
                "timestamp": datetime.now().isoformat(),
                "note": "Using sample data - database may not be initialized"
            }

# Initialize chatbot
chatbot = ChatbotAI()

@app.route('/')
def home():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.json
        query = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not query:
            return jsonify({
                "response": "⚠️ Please enter a message.",
                "category": "error",
                "confidence": 0.0,
                "session_id": session_id
            }), 400
        
        # Process query
        result = chatbot.process_query(query, session_id)
        result["session_id"] = session_id
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            "response": "⚠️ Sorry, I encountered an error processing your request. Please try again.",
            "category": "error",
            "confidence": 0.0,
            "session_id": data.get('session_id', str(uuid.uuid4()))
        }), 500

@app.route('/api/statistics', methods=['GET'])
def statistics():
    """Get chatbot statistics"""
    stats = chatbot.get_statistics()
    return jsonify(stats)

@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    """Get smart suggestions"""
    category = request.args.get('category', 'academics')
    
    suggestions_list = []
    if category in KNOWLEDGE_BASE:
        for subcat in KNOWLEDGE_BASE[category]:
            suggestions_list.extend(KNOWLEDGE_BASE[category][subcat]['patterns'][:2])
    
    # Add some general suggestions
    general_suggestions = [
        "upcoming events on campus",
        "academic calendar 2024-25",
        "contact department heads",
        "campus map and directions",
        "student clubs and societies",
        "career counseling services",
        "internship opportunities",
        "research facilities"
    ]
    
    suggestions_list.extend(general_suggestions[:4])
    
    return jsonify({
        "suggestions": suggestions_list[:10],
        "category": category,
        "count": len(suggestions_list[:10])
    })

@app.route('/api/quick_actions', methods=['GET'])
def quick_actions():
    """Get quick action buttons"""
    return jsonify({
        "actions": [
            {"icon": "📅", "text": "Exam Schedule", "category": "academics", "color": "#3B82F6"},
            {"icon": "💰", "text": "Pay Fees", "category": "administration", "color": "#10B981"},
            {"icon": "📚", "text": "Library", "category": "campus", "color": "#8B5CF6"},
            {"icon": "🏠", "text": "Hostel", "category": "campus", "color": "#F59E0B"},
            {"icon": "🚌", "text": "Transport", "category": "campus", "color": "#EF4444"},
            {"icon": "📄", "text": "Documents", "category": "administration", "color": "#6366F1"},
            {"icon": "🎓", "text": "Courses", "category": "academics", "color": "#EC4899"},
            {"icon": "📊", "text": "Results", "category": "academics", "color": "#14B8A6"}
        ]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Student Chatbot",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if os.path.exists('chatbot_ai.db') else "not_found"
    })

@app.route('/api/export', methods=['POST'])
def export_conversations():
    """Export conversation history (placeholder)"""
    return jsonify({
        "success": True,
        "message": "Export feature coming soon!",
        "features": [
            "Export as PDF",
            "Export as CSV",
            "Export as JSON",
            "Schedule automatic exports"
        ]
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 AI STUDENT CHATBOT v2.0")
    print("="*60)
    print("📡 Starting server...")
    print("🌐 Access at: http://localhost:5000")
    print("📊 Analytics dashboard available")
    print("💡 Features: AI-powered responses, Statistics, Smart suggestions")
    print("="*60)
    
    # Check database
    if not os.path.exists('chatbot_ai.db'):
        print("⚠️  Database not found. Initializing...")
        chatbot.init_database()
        print("✅ Database initialized successfully!")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)