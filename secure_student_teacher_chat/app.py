from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app and configuration
app = Flask(__name__)
app.secret_key = 'secret123'  # Used for session encryption (should be kept secret in production)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the Message model to store chat messages
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))             # Sender name
    role = db.Column(db.String(20))              # Role of sender ('student' or 'teacher')
    message = db.Column(db.Text)                 # Message content
    subject = db.Column(db.String(100))          # Subject of the query
    department = db.Column(db.String(100))       # Department (e.g., Computer, Civil)
    query_type = db.Column(db.String(100))       # Type of query (e.g., academic, exam)
    time = db.Column(db.String(50))              # Timestamp of message
    reply = db.Column(db.Text)                   # Reply from teacher
    replied_by = db.Column(db.String(100))       # Name of teacher who replied

# Redirect root URL to login page
@app.route('/')
def index():
    return redirect(url_for('login'))

# Login route for both students and teachers
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hardcoded teacher credentials
        if username in ['Sagar Mhatre', 'Shivraj Patil', 'Aniket'] and password == 'mes@hoc':
            session['username'] = username
            session['role'] = 'teacher'
            return redirect(url_for('chat'))

        # Hardcoded student password
        if password == 'mes':
            session['username'] = username
            session['role'] = 'student'
            return redirect(url_for('chat'))

        # Invalid login
        return render_template('index.html', error="Invalid credentials.")

    return render_template('login.html')

# Logout route to clear session
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Chat route where users can view messages
@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    role = session['role']

    # If teacher, show only messages from their department
    if role == 'teacher':
        if username == 'Sagar Mhatre':
            messages = Message.query.filter_by(department='Computer').all()
        elif username == 'Shivraj Patil':
            messages = Message.query.filter_by(department='Civil').all()
        elif username == 'Aniket':
            messages = Message.query.filter_by(department='Mechanical').all()
        else:
            messages = []  # Default empty list for unknown teacher
    else:
        # Students can only see their own messages
        messages = Message.query.filter_by(name=username).all()

    return render_template('chat.html', messages=messages, username=username, role=role)

# Route to handle message sending by students
@app.route('/send', methods=['POST'])
def send_message():
    if 'username' not in session:
        return redirect(url_for('login'))

    data = request.form
    # Create a new message object
    msg = Message(
        name=session['username'],
        role=session['role'],
        message=data['message'],
        subject=data['subject'],
        department=data['department'],
        query_type=data['query_type'],
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    # Add and commit to database
    db.session.add(msg)
    db.session.commit()
    return redirect(url_for('chat'))

# Route to allow teachers to reply to a message
@app.route('/reply/<int:msg_id>', methods=['POST'])
def reply_message(msg_id):
    if 'username' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    msg = Message.query.get(msg_id)
    if msg:
        # Save teacher's reply and who replied
        msg.reply = request.form['reply']
        msg.replied_by = session['username']
        db.session.commit()
    return redirect(url_for('chat'))

# Run the Flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure all tables are created before first request
    app.run(debug=True)
