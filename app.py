# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 02:43:43 2026

@author: lesii
"""
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -----------------
# DATABASE MODELS
# -----------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    goal = db.Column(db.String(200))
    
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    message = db.Column(db.String(200))
    time = db.Column(db.String(10))
    
class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    workout = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
@login_manager.user_loader 
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------
# AUTH ROUTES
# -----------

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        user = User(name=request.form['name'], email=request.form['email'], password=hashed_pw, goal=request.form['goal'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
    
    return render_template("login.html")
    
@app.route('/logout')
@login_required 
def logout():
    logout_user()
    return redirect(url_for('login'))

# --------------
# DASHBOARD
# --------------

@app.route('/dashboard')
@login_required 
def dashboard():
    reminders = Reminder.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", reminders=reminders)

# -------------------
# REMINDER SCHEDULING
# --------------------

@app.route('/add_reminder', methods=['POST'])
@login_required 
def add_reminder():
    reminder = Reminder(user_id=current_user.id, message=request.form['message'], time=request.form['time'])
    db.session.add(reminder)
    db.session.commit()
    return redirect(url_for('dashboard'))

# ----------------------------
# PUSH NOTIFICATION SIMULATION 
# ----------------------------

def reminder_checker():
    with app.app_context():
        while True: 
            now = datetime.now().strftime("%H:%M") 
            reminders = Reminder.query.filter_by(time=now).all() 
            for r in reminders: 
                print(f"!!Reminder for User {r.user_id}: {r.message}")
        time.sleep(60)
        

# ----------------
# WORKOUT LOG
# ----------------

@app.route('/log_workout', methods=['POST'])
@login_required 
def log_workout():
    log = WorkoutLog(user_id=current_user.id, workout=request.form['workout'])
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
   # thread = threading.Thread(target=reminder_checker)
   # thread.daemon = True
   # thread.start()
    
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=True) 