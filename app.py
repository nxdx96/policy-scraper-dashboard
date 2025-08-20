from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import os
import random
import threading
from dotenv import load_dotenv
from scraper_engine import ScrapingEngine

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key-for-development')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/scraper_dashboard')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def generate_short_id():
    """Generate a 5-digit unique ID"""
    while True:
        new_id = str(random.randint(10000, 99999))
        # Check if this ID already exists
        if not Job.query.filter_by(id=new_id).first():
            return new_id

class Job(db.Model):
    id = db.Column(db.String(5), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.Text, nullable=False)
    selenium_instructions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'selenium_instructions': self.selenium_instructions,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class JobRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(5), db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.String(20), default='running')  # running, completed, failed
    results = db.Column(db.Text)  # JSON string of results
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    job = db.relationship('Job', backref=db.backref('runs', lazy=True))

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    if search_query:
        jobs = Job.query.filter(
            db.or_(
                Job.name.contains(search_query),
                Job.url.contains(search_query),
                Job.id.contains(search_query)
            )
        ).order_by(Job.created_at.desc()).all()
    else:
        jobs = Job.query.order_by(Job.created_at.desc()).all()
    
    return render_template('index.html', jobs=jobs, search_query=search_query)

@app.route('/create_job', methods=['POST'])
def create_job():
    try:
        name = request.form.get('name')
        url = request.form.get('url')
        selenium_instructions = request.form.get('selenium_instructions', '')
        
        if not name or not url:
            flash('Name and URL are required fields', 'error')
            return redirect(url_for('index'))
        
        new_job = Job(
            id=generate_short_id(),
            name=name,
            url=url,
            selenium_instructions=selenium_instructions
        )
        
        db.session.add(new_job)
        db.session.commit()
        
        flash('Job created successfully!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Error creating job: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/update_job/<job_id>', methods=['POST'])
def update_job(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        
        job.name = request.form.get('name', job.name)
        job.url = request.form.get('url', job.url)
        job.selenium_instructions = request.form.get('selenium_instructions', job.selenium_instructions)
        
        db.session.commit()
        flash('Job updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating job: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete_job/<job_id>', methods=['POST'])
def delete_job(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        flash('Job deleted successfully!', 'success')
        
    except Exception as e:
        flash(f'Error deleting job: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/run_job/<job_id>', methods=['POST'])
def run_job(job_id):
    """Execute a scraping job"""
    try:
        job = Job.query.get_or_404(job_id)
        
        # Create a new job run record
        job_run = JobRun(job_id=job_id, status='running')
        db.session.add(job_run)
        db.session.commit()
        
        # Execute scraping in a separate thread
        def execute_scraping():
            engine = ScrapingEngine(headless=True)
            job_data = job.to_dict()
            result = engine.run_scraping_job(job_data)
            
            # Update job run with results
            job_run.status = 'completed' if result['status'] == 'success' else 'failed'
            job_run.results = str(result)
            job_run.completed_at = datetime.utcnow()
            db.session.commit()
        
        # Start scraping in background
        threading.Thread(target=execute_scraping, daemon=True).start()
        
        flash(f'Scraping job {job_id} started successfully!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Error starting job: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/job_status/<job_id>')
def job_status(job_id):
    """Get the status of recent job runs"""
    try:
        job = Job.query.get_or_404(job_id)
        recent_runs = JobRun.query.filter_by(job_id=job_id).order_by(JobRun.started_at.desc()).limit(5).all()
        
        runs_data = []
        for run in recent_runs:
            runs_data.append({
                'id': run.id,
                'status': run.status,
                'started_at': run.started_at.strftime('%Y-%m-%d %H:%M:%S'),
                'completed_at': run.completed_at.strftime('%Y-%m-%d %H:%M:%S') if run.completed_at else None,
                'results': run.results
            })
        
        return jsonify({
            'job_id': job_id,
            'job_name': job.name,
            'runs': runs_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/macro_docs')
def macro_docs():
    """Get documentation for available macros"""
    engine = ScrapingEngine()
    docs = engine.get_macro_documentation()
    return jsonify(docs)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)