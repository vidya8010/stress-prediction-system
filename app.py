from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
import pickle
from datetime import datetime,timedelta
from sqlalchemy import func
import os

#Start 
app = Flask(__name__)

app.secret_key = "a_very_secret_key_12345"  # <--- add this line
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'project.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {"check_same_thread": False}
}

db = SQLAlchemy(app)

#Tables
class RegisterUser(db.Model):
    __tablename__ = 'register_users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    last_login = db.Column(db.DateTime,nullable=True)

class FormData(db.Model):
    __tablename__ = 'form_data'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    platform=db.Column(db.String(60))
    time_spent = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    mood = db.Column(db.String(50))
    stress = db.Column(db.Float)
    last_login = db.Column(db.DateTime,default=datetime.now)

class RegisterAdmin(db.Model):
    __tablename__ = 'register_admin'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    


#ml files imported
model = pickle.load(open("model_train.pkl", "rb"))
le_gender = pickle.load(open("gender_encoder.pkl", "rb"))
le_mood = pickle.load(open("mood_encoder.pkl", "rb"))
le_platform=pickle.load(open("platform_encoder.pkl","rb"))

#Home Function
@app.route("/")
def home():
    return render_template('home.html')

#About function
@app.route('/about')
def about():
    return render_template('about.html')

#Contact page function 
@app.route('/contact')
def contact():
    return render_template('contact.html')

#Login selection 
@app.route('/login_selection',)
def login_selection():
    return render_template('login_selection.html')

#Register user
@app.route('/register_user',methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        #get data from frontend through form 
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # check if user already exists
        existing_user = RegisterUser.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists! login")
            return redirect(url_for("user_login"))

        # hash password (important for security)
        hashed_password = generate_password_hash(password)

        # create new user object
        new_user = RegisterUser(
            name=name,
            email=email,
            password=hashed_password,
        )

        # save to database
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!")
        return redirect(url_for("user_login"))
    return render_template('register_user.html')

#User Login
@app.route('/user_login', methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = RegisterUser.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            user.last_login = datetime.now()
            db.session.commit()
            session["user_id"] = user.id
            session["username"] = user.name

            return redirect('getstarted')

        else:
            flash("Invalid Credentials")

    return render_template('user_login.html')

#Forget passward
@app.route('/forget_pass', methods=['GET', 'POST'])
def forget_pass():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check if email exists
        user = RegisterUser.query.filter_by(email=email).first()

        if not user:
            flash("Email not registered!", "danger")
            return redirect(url_for('forget_pass'))

        # Check password match
        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('forget_pass'))

        # Hash new password
        hashed_password = generate_password_hash(new_password)

        # Update password in database
        user.password = hashed_password
        db.session.commit()

        flash("Password updated successfully! Please login.", "success")
        return redirect(url_for('user_login'))

    return render_template('forget_pass.html')


#Starting after login 
@app.route('/getstarted')
def getstarted():
    return render_template('getstarted.html')

#Predectionfrom
@app.route('/form',methods=['GET','POST'])
def form():
    if request.method == 'POST':
        #it collect the data from user and send this data to ml model
        age = int(request.form['age'])
        encoded_gender = int(request.form['gender'])
        encoded_platform=int(request.form['platform'])
        frequency = int(request.form['frequency'])
        time_spent = int(request.form['time_spent'])
        encoded_mood = int(request.form['mood'])

        # now srerady your input fields for predictng stress 
        features = [[age, encoded_gender,encoded_platform, frequency, time_spent, encoded_mood]]#this are the list of fields on which i calculate stress level
        predicted_stress = model.predict(features)[0]# here we store our stress level in predicted_stress var and .predict metjod used to predict your stress

        stress_percent = predicted_stress * 10
        stress_percent = max(0, min(100, stress_percent))
        stress_percent = round(stress_percent, 2)


        #this method are used to reconvert your data to text format becouse in html we use number values for gender and mood
        original_gender = le_gender.inverse_transform([encoded_gender])[0]
        original_mood = le_mood.inverse_transform([encoded_mood])[0]
        original_platform=le_platform.inverse_transform([encoded_platform])[0]
        # Save to DB
        entry = FormData(
            name=request.form['name'],
            age=age,
            gender=original_gender,
            platform=original_platform,
            time_spent=time_spent,
            frequency=frequency,
            mood=original_mood,
            stress=round(stress_percent,2)
        )
        db.session.add(entry)
        db.session.commit()

        # it shows Prediction Page 
        return render_template(
            'prediction.html',
            stress_percent=round(stress_percent,2)
            )
    return render_template('form.html')

#Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('user_login'))

#Admin registration 
@app.route('/admin_register',methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        #get data from frontend through form 
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # check if user already exists
        existing_user = RegisterAdmin.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists! login")
            return redirect(url_for("admin_login"))

        # hash password (important for security)
        hashed_password = generate_password_hash(password)

        # create new user object
        new_user = RegisterAdmin(
            name=name,
            email=email,
            password=hashed_password
        )

        # save to database
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!")
        return redirect(url_for("admin_login"))
    return render_template('admin_register.html')


#Admin login
@app.route('/admin_login',methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Step 1: find user in SAME table
        user = RegisterAdmin.query.filter_by(email=email).first()

        # Step 2: check password
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.name
            return redirect('admin_home')
        else:
            flash("Invalid Credentials")
    return render_template('admin_login.html')

#Admin home
@app.route('/admin_home')
def admin_home():

    total_users = RegisterUser.query.count()

    # active users (last 7 days)
    limit = datetime.now() - timedelta(days=7)

    all_users = RegisterUser.query.all()

    active_users = RegisterUser.query.filter(
        RegisterUser.last_login != None,
        RegisterUser.last_login >= limit
    ).count()
    reports = (
        FormData.query.count() 
    )
    #Most used platform 
    most_used_platform = (
        db.session.query(
            FormData.platform,
            func.count(FormData.platform).label('total')
        )
        .group_by(FormData.platform)
        .order_by(func.count(FormData.platform).desc())
        .first()
    )
    platform_name = most_used_platform[0] if most_used_platform else "No Data"
    platform_count = most_used_platform[1] if most_used_platform else 0

    #Average time
    avg_time = db.session.query(
        func.avg(FormData.time_spent)
        ).scalar()

    avg_time = round(avg_time, 1) if avg_time else 0

    #Chart implementation
    platform_data = (
    db.session.query(
        FormData.platform,
        func.count(FormData.id)
    )
    .group_by(FormData.platform)
    .all()
    )

    labels = [row[0] for row in platform_data]
    counts = [row[1] for row in platform_data]

    return render_template(
        'admin_home.html',
        total_users=total_users,
        active_users=active_users,
        reports=reports,
        users=all_users,
        platform_name=platform_name,
        platform_count=platform_count,
        avg_time=avg_time,
        labels=labels,
        counts=counts
    )


#Admin content 
@app.route('/reports')
def reports():
    total_users = RegisterUser.query.count()
    total_predictions = (
        FormData.query.count()
    )
    users=FormData.query.all()
    high_stress_count = FormData.query.filter(FormData.stress >= 60).count()
    low_stress_count=FormData.query.filter(FormData.stress <=40).count()
    return render_template(
        'reports.html',
        total_users=total_users,
        total_predictions=total_predictions,
        high_stress=high_stress_count,
        low_stress=low_stress_count,
        users=users
    )

#Admin users table 
@app.route('/users')
def users():
    all_users = RegisterUser.query.all()
    return render_template(
        'users.html',
        users=all_users
    )
#Admin logout
@app.route('/admin_logout')
def admin_logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('admin_login'))
#MAin function 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)