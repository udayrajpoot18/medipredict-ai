"""
MediPredict AI - Production Flask Application
Features: Auth, ML Prediction, Health History, PDF Reports, Email, Admin Panel
"""

import os, pickle, logging, io
from datetime import datetime
from functools import wraps

import numpy as np
from flask import (Flask, render_template, request, jsonify,
                   redirect, url_for, flash, send_file, abort)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, UserMixin,
                         login_user, logout_user, login_required, current_user)
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash

# ReportLab for PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from config import config

# ─────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('logs/mediai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'production')
app.config.from_object(config.get(env, config['production']))

db    = SQLAlchemy(app)
mail  = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to use the diagnosis tools.'
login_manager.login_message_category = 'info'

# ─────────────────────────────────────────
# Models
# ─────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80),  unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password_hash= db.Column(db.String(256), nullable=False)
    is_admin     = db.Column(db.Boolean, default=False)
    is_active_acc= db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    last_login   = db.Column(db.DateTime)
    predictions  = db.relationship('Prediction', backref='user', lazy='dynamic',
                                   cascade='all, delete-orphan')

    def set_password(self, pw):   self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

    @property
    def prediction_count(self):
        return self.predictions.count()


class Prediction(db.Model):
    __tablename__ = 'predictions'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    disease     = db.Column(db.String(50),  nullable=False)
    disease_name= db.Column(db.String(100), nullable=False)
    risk_level  = db.Column(db.String(20),  nullable=False)   # High / Low
    result_text = db.Column(db.String(300), nullable=False)
    input_data  = db.Column(db.Text,        nullable=False)    # JSON string
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def formatted_date(self):
        return self.created_at.strftime('%d %b %Y, %I:%M %p')

    @property
    def risk_badge(self):
        return 'high' if self.risk_level == 'High' else 'low'


@login_manager.user_loader
def load_user(uid): return User.query.get(int(uid))

# ─────────────────────────────────────────
# ML Models
# ─────────────────────────────────────────
MODEL_CONFIG = {
    'diabetes':   {'path':'model/diabetes_model.sav',   'name':'Diabetes',            'fields':['Glucose (mg/dL)','Blood Pressure (mmHg)','BMI','Age']},
    'heart':      {'path':'model/heart_model.sav',      'name':'Heart Disease',        'fields':['Age','Cholesterol (mg/dL)','Blood Pressure (mmHg)','Max Heart Rate (bpm)']},
    'lung':       {'path':'model/lung_model.sav',       'name':'Lung Cancer',          'fields':['Smoking Status','Age','Cough Symptoms','Fatigue Level']},
    'parkinsons': {'path':'model/parkinsons_model.sav', 'name':"Parkinson's Disease",  'fields':['Voice Tremor','Pitch (Hz)','Jitter','Shimmer']},
    'thyroid':    {'path':'model/thyroid_model.sav',    'name':'Thyroid Disorder',     'fields':['TSH (mIU/L)','T3 (ng/dL)','T4 (µg/dL)','Age']},
}
ml_models = {}

def load_models():
    for key, cfg in MODEL_CONFIG.items():
        if os.path.exists(cfg['path']):
            ml_models[key] = pickle.load(open(cfg['path'], 'rb'))
            logger.info(f"Loaded model: {cfg['name']}")
        else:
            logger.warning(f"Model not found: {cfg['path']}")

load_models()

# ─────────────────────────────────────────
# Decorators
# ─────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────
# Email Helpers
# ─────────────────────────────────────────
def send_prediction_email(user, prediction):
    """Send prediction result email to user."""
    if not app.config.get('MAIL_USERNAME'):
        return  # Email not configured, skip silently
    try:
        risk_emoji = '⚠️' if prediction.risk_level == 'High' else '✅'
        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#0f172a;color:#cbd5e1;padding:30px;border-radius:12px">
          <h2 style="color:#00e676;margin-bottom:4px">Medipredict AI</h2>
          <p style="color:#64748b;font-size:12px;margin-bottom:24px">Intelligent Health Analytics</p>
          <h3 style="color:#ffffff">Hi {user.username}, your analysis is ready!</h3>
          <div style="background:#1e293b;border-radius:10px;padding:20px;margin:20px 0;border-left:4px solid {'#ef4444' if prediction.risk_level=='High' else '#00e676'}">
            <p style="font-size:18px;font-weight:700;color:#ffffff">{risk_emoji} {prediction.disease_name}</p>
            <p style="color:#94a3b8">Risk Level: <strong style="color:{'#ef4444' if prediction.risk_level=='High' else '#00e676'}">{prediction.risk_level}</strong></p>
            <p style="color:#94a3b8;font-size:12px">Date: {prediction.formatted_date}</p>
          </div>
          <p style="color:#94a3b8;font-size:13px">⚠️ This is an AI-generated result. Always consult a qualified healthcare professional.</p>
          <a href="#" style="display:inline-block;background:#00e676;color:#000;padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:700;margin-top:16px">View Full Report</a>
        </div>
        """
        msg = Message(
            subject=f'Your {prediction.disease_name} Analysis Result — Medipredict AI',
            recipients=[user.email],
            html=html_body
        )
        mail.send(msg)
        logger.info(f"Email sent to {user.email}")
    except Exception as e:
        logger.error(f"Email failed: {e}")


def send_welcome_email(user):
    """Send welcome email after signup."""
    if not app.config.get('MAIL_USERNAME'):
        return
    try:
        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#0f172a;color:#cbd5e1;padding:30px;border-radius:12px">
          <h2 style="color:#00e676">Welcome to Medipredict AI! 🎉</h2>
          <p>Hi <strong>{user.username}</strong>,</p>
          <p style="color:#94a3b8">Your account has been created. You can now access AI-powered health risk assessments for:</p>
          <ul style="color:#94a3b8">
            <li>🩺 Diabetes</li><li>❤️ Heart Disease</li><li>🫁 Lung Cancer</li><li>🧠 Parkinson's Disease</li><li>🦋 Thyroid Disorder</li>
          </ul>
          <p style="color:#64748b;font-size:12px;margin-top:24px">⚠️ Always consult a healthcare professional. This tool is for informational purposes only.</p>
        </div>
        """
        msg = Message(subject='Welcome to Medipredict AI!', recipients=[user.email], html=html_body)
        mail.send(msg)
    except Exception as e:
        logger.error(f"Welcome email failed: {e}")

# ─────────────────────────────────────────
# PDF Generator
# ─────────────────────────────────────────
def generate_pdf_report(user, prediction, input_fields):
    """Generate a styled A4 PDF report for a prediction."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()
    GREEN  = colors.HexColor('#00e676')
    DARK   = colors.HexColor('#0f172a')
    CARD   = colors.HexColor('#1e293b')
    MUTED  = colors.HexColor('#64748b')
    WHITE  = colors.white
    RED    = colors.HexColor('#ef4444')

    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontName='Helvetica-Bold', fontSize=22,
                                  textColor=WHITE, spaceAfter=4, alignment=TA_CENTER)
    sub_style   = ParagraphStyle('Sub', parent=styles['Normal'],
                                  fontName='Helvetica', fontSize=11,
                                  textColor=MUTED, spaceAfter=20, alignment=TA_CENTER)
    head_style  = ParagraphStyle('Head', parent=styles['Heading2'],
                                  fontName='Helvetica-Bold', fontSize=13,
                                  textColor=GREEN, spaceBefore=14, spaceAfter=8)
    body_style  = ParagraphStyle('Body', parent=styles['Normal'],
                                  fontName='Helvetica', fontSize=10,
                                  textColor=colors.HexColor('#94a3b8'), leading=16)
    warn_style  = ParagraphStyle('Warn', parent=styles['Normal'],
                                  fontName='Helvetica-Oblique', fontSize=9,
                                  textColor=colors.HexColor('#fbbf24'), leading=14)

    risk_color = RED if prediction.risk_level == 'High' else GREEN

    story = []

    # Header
    story.append(Paragraph("Medipredict AI", title_style))
    story.append(Paragraph("Intelligent Health Analytics Report", sub_style))
    story.append(HRFlowable(width='100%', thickness=1, color=GREEN, spaceAfter=16))

    # Patient + Report Info table
    info_data = [
        ['Patient Name', user.username,       'Report Date', prediction.formatted_date],
        ['Email',        user.email,           'Disease',     prediction.disease_name],
        ['User ID',      f'#{user.id}',        'Risk Level',  prediction.risk_level],
    ]
    info_table = Table(info_data, colWidths=[1.3*inch, 2.2*inch, 1.3*inch, 2.2*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD),
        ('TEXTCOLOR',  (0,0), (0,-1), GREEN),
        ('TEXTCOLOR',  (2,0), (2,-1), GREEN),
        ('TEXTCOLOR',  (1,0), (1,-1), WHITE),
        ('TEXTCOLOR',  (3,0), (3,-1), WHITE),
        ('FONTNAME',   (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME',   (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',   (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [CARD, colors.HexColor('#243044')]),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#334155')),
        ('ROUNDEDCORNERS', [6]),
        ('PADDING',    (0,0), (-1,-1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # Result banner
    result_data = [[f"{'⚠️  HIGH RISK' if prediction.risk_level=='High' else '✅  LOW RISK'}  —  {prediction.disease_name}"]]
    result_table = Table(result_data, colWidths=[7*inch])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), risk_color),
        ('TEXTCOLOR',  (0,0), (-1,-1), DARK if prediction.risk_level=='Low' else WHITE),
        ('FONTNAME',   (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 14),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('PADDING',    (0,0), (-1,-1), 14),
        ('ROUNDEDCORNERS', [8]),
    ]))
    story.append(result_table)
    story.append(Spacer(1, 16))

    # Input Parameters
    story.append(Paragraph("Input Parameters", head_style))
    import json
    try:
        vals = json.loads(prediction.input_data)
    except Exception:
        vals = []
    fields = MODEL_CONFIG.get(prediction.disease, {}).get('fields', [])
    param_data = [['Parameter', 'Value Entered']]
    for i, v in enumerate(vals):
        label = fields[i] if i < len(fields) else f'Parameter {i+1}'
        param_data.append([label, str(v)])
    param_table = Table(param_data, colWidths=[4*inch, 3*inch])
    param_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  GREEN),
        ('TEXTCOLOR',     (0,0), (-1,0),  DARK),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('BACKGROUND',    (0,1), (-1,-1), CARD),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [CARD, colors.HexColor('#243044')]),
        ('TEXTCOLOR',     (0,1), (-1,-1), WHITE),
        ('FONTNAME',      (0,1), (0,-1),  'Helvetica-Bold'),
        ('TEXTCOLOR',     (0,1), (0,-1),  colors.HexColor('#94a3b8')),
        ('FONTSIZE',      (0,0), (-1,-1), 9),
        ('GRID',          (0,0), (-1,-1), 0.5, colors.HexColor('#334155')),
        ('PADDING',       (0,0), (-1,-1), 9),
    ]))
    story.append(param_table)
    story.append(Spacer(1, 16))

    # Disclaimer
    story.append(HRFlowable(width='100%', thickness=0.5, color=MUTED, spaceAfter=10))
    story.append(Paragraph(
        "⚠️  MEDICAL DISCLAIMER: This report is generated by an AI system for informational purposes only. "
        "It is NOT a substitute for professional medical advice, diagnosis, or treatment. "
        "Always consult a qualified healthcare professional before making any medical decisions.",
        warn_style
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Generated by Medipredict AI  |  {datetime.utcnow().strftime('%d %b %Y %H:%M UTC')}  |  medipredict.ai",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=MUTED, alignment=TA_CENTER)
    ))

    doc.build(story)
    buf.seek(0)
    return buf

# ─────────────────────────────────────────
# Routes — Public
# ─────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/signup', methods=['GET','POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        email    = request.form.get('email','').strip().lower()
        pw       = request.form.get('password','')
        pw2      = request.form.get('confirm_password','')
        if not all([username, email, pw]):
            flash('All fields are required.', 'danger'); return redirect(url_for('signup'))
        if len(pw) < 6:
            flash('Password must be at least 6 characters.', 'danger'); return redirect(url_for('signup'))
        if pw != pw2:
            flash('Passwords do not match.', 'danger'); return redirect(url_for('signup'))
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger'); return redirect(url_for('signup'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger'); return redirect(url_for('signup'))
        user = User(username=username, email=email)
        user.set_password(pw)
        db.session.add(user); db.session.commit()
        send_welcome_email(user)
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        pw       = request.form.get('password','')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(pw):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=True)
            flash(f'Welcome back, {username}!', 'success')
            return redirect(request.args.get('next') or url_for('home'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

# ─────────────────────────────────────────
# Routes — Prediction
# ─────────────────────────────────────────
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    import json
    disease = request.form.get('disease','').lower()
    if disease not in MODEL_CONFIG:
        return render_template('index.html', prediction_text='❌ Invalid disease type.'), 400
    if disease not in ml_models:
        return render_template('index.html', prediction_text='❌ Model unavailable.'), 500

    values = []
    for key in sorted(request.form.keys()):
        if key.startswith('f'):
            try:
                values.append(float(request.form[key]))
            except ValueError:
                return render_template('index.html', prediction_text='❌ Please enter numbers only.'), 400
    if not values:
        return render_template('index.html', prediction_text='❌ No input provided.'), 400

    pred = ml_models[disease].predict(np.array([values]))
    disease_name = MODEL_CONFIG[disease]['name']

    if pred[0] == 1:
        risk, result = 'High', f'⚠️ <strong>High Risk Detected</strong> for {disease_name}'
    else:
        risk, result = 'Low',  f'✅ <strong>Low Risk Assessment</strong> for {disease_name}'

    # Save to DB
    p = Prediction(
        user_id=current_user.id,
        disease=disease,
        disease_name=disease_name,
        risk_level=risk,
        result_text=result,
        input_data=json.dumps(values)
    )
    db.session.add(p); db.session.commit()

    # Send email (non-blocking)
    send_prediction_email(current_user, p)

    logger.info(f"Prediction: user={current_user.username} disease={disease_name} risk={risk}")
    return render_template('index.html', prediction_text=result, risk=risk, latest_pred_id=p.id)

# ─────────────────────────────────────────
# Routes — Health History Dashboard
# ─────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    disease_filter = request.args.get('disease', '')
    risk_filter    = request.args.get('risk', '')

    q = Prediction.query.filter_by(user_id=current_user.id)
    if disease_filter: q = q.filter_by(disease=disease_filter)
    if risk_filter:    q = q.filter_by(risk_level=risk_filter)
    predictions = q.order_by(Prediction.created_at.desc()).paginate(page=page, per_page=10, error_out=False)

    # Stats
    all_preds   = Prediction.query.filter_by(user_id=current_user.id)
    total       = all_preds.count()
    high_risk   = all_preds.filter_by(risk_level='High').count()
    low_risk    = all_preds.filter_by(risk_level='Low').count()
    last_pred   = all_preds.order_by(Prediction.created_at.desc()).first()

    # Disease breakdown for chart
    from sqlalchemy import func
    disease_stats = db.session.query(
        Prediction.disease_name, func.count(Prediction.id)
    ).filter_by(user_id=current_user.id).group_by(Prediction.disease_name).all()

    return render_template('dashboard.html',
        predictions=predictions,
        total=total, high_risk=high_risk, low_risk=low_risk,
        last_pred=last_pred,
        disease_stats=disease_stats,
        disease_filter=disease_filter, risk_filter=risk_filter,
        disease_names={k: v['name'] for k,v in MODEL_CONFIG.items()}
    )


@app.route('/prediction/<int:pred_id>/delete', methods=['POST'])
@login_required
def delete_prediction(pred_id):
    p = Prediction.query.filter_by(id=pred_id, user_id=current_user.id).first_or_404()
    db.session.delete(p); db.session.commit()
    flash('Record deleted.', 'info')
    return redirect(url_for('dashboard'))

# ─────────────────────────────────────────
# Routes — PDF Download
# ─────────────────────────────────────────
@app.route('/report/<int:pred_id>/pdf')
@login_required
def download_pdf(pred_id):
    pred = Prediction.query.filter_by(id=pred_id, user_id=current_user.id).first_or_404()
    import json
    try:
        input_fields = json.loads(pred.input_data)
    except Exception:
        input_fields = []
    buf = generate_pdf_report(current_user, pred, input_fields)
    filename = f"medipredict_{pred.disease}_{pred.created_at.strftime('%Y%m%d')}.pdf"
    return send_file(buf, mimetype='application/pdf',
                     as_attachment=True, download_name=filename)

# ─────────────────────────────────────────
# Routes — Admin Panel
# ─────────────────────────────────────────
@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    from sqlalchemy import func
    total_users       = User.query.count()
    total_predictions = Prediction.query.count()
    high_risk_total   = Prediction.query.filter_by(risk_level='High').count()
    new_users_today   = User.query.filter(
        func.date(User.created_at) == datetime.utcnow().date()
    ).count()
    recent_users  = User.query.order_by(User.created_at.desc()).limit(20).all()
    recent_preds  = Prediction.query.order_by(Prediction.created_at.desc()).limit(30).all()
    disease_stats = db.session.query(
        Prediction.disease_name, func.count(Prediction.id)
    ).group_by(Prediction.disease_name).all()
    return render_template('admin.html',
        total_users=total_users, total_predictions=total_predictions,
        high_risk_total=high_risk_total, new_users_today=new_users_today,
        recent_users=recent_users, recent_preds=recent_preds,
        disease_stats=disease_stats
    )


@app.route('/admin/user/<int:uid>/toggle', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user(uid):
    u = User.query.get_or_404(uid)
    if u.id == current_user.id:
        flash("You can't deactivate yourself.", 'danger')
        return redirect(url_for('admin_panel'))
    u.is_active_acc = not u.is_active_acc
    db.session.commit()
    flash(f"User {u.username} {'activated' if u.is_active_acc else 'deactivated'}.", 'info')
    return redirect(url_for('admin_panel'))


@app.route('/admin/user/<int:uid>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(uid):
    u = User.query.get_or_404(uid)
    if u.id == current_user.id:
        flash("You can't delete yourself.", 'danger')
        return redirect(url_for('admin_panel'))
    db.session.delete(u); db.session.commit()
    flash(f"User {u.username} deleted.", 'success')
    return redirect(url_for('admin_panel'))

# ─────────────────────────────────────────
# Routes — API + Errors
# ─────────────────────────────────────────
@app.route('/api/health')
def health_check():
    return jsonify({
        'status':        'healthy' if len(ml_models) == len(MODEL_CONFIG) else 'degraded',
        'models_loaded': len(ml_models),
        'total_models':  len(MODEL_CONFIG),
        'timestamp':     datetime.utcnow().isoformat()
    })


@app.errorhandler(403)
def forbidden(e):
    flash('Access denied.', 'danger')
    return redirect(url_for('home'))


@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f'500: {e}')
    return render_template('index.html', prediction_text='❌ Server error. Please try again.'), 500

# ─────────────────────────────────────────
# Startup
# ─────────────────────────────────────────
def create_admin():
    """Create default admin if not exists."""
    admin_email = app.config.get('ADMIN_EMAIL', 'admin@medipredict.ai')
    admin_pw    = app.config.get('ADMIN_PASSWORD', 'Admin@123Secure')
    if not User.query.filter_by(email=admin_email).first():
        admin = User(username='admin', email=admin_email, is_admin=True)
        admin.set_password(admin_pw)
        db.session.add(admin); db.session.commit()
        logger.info(f"Admin created: {admin_email}")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(env == 'development'))
