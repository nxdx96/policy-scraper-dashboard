from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key-for-development')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/scraper_dashboard')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Job(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)