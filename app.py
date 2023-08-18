from flask import Flask, render_template, request, url_for, redirect, session,flash
from datetime import timedelta,datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.secret_key = "flaskappsecret"
app.permanent_session_lifetime = timedelta(minutes=10)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(20), nullable=False, unique=True)
    lname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<Users %r>' % self.fname

class PassengerDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    travel_date = db.Column(db.Date, nullable=False)
    passenger_count = db.Column(db.Integer, nullable=False)
    passenger_name_1 = db.Column(db.String(100), nullable=False)
    passenger_name_2 = db.Column(db.String(100))
    passenger_name_3 = db.Column(db.String(100))
    passenger_name_4 = db.Column(db.String(100))
    email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    user = db.relationship('Users', backref=db.backref('passenger_details', lazy=True))
    time_booked = db.Column(db.DateTime, default=datetime.now)
    def __repr__(self):
        return '<PassengerDetails %r>' % self.id


with app.app_context():
    db.create_all()
    
@app.route('/')
def index():
    return render_template('base.html')
@app.route('/home')
def home():
    if "email" in session:
        email=session["email"]
        user = Users.query.filter_by(email=email).first()
        fname = user.fname if user else None
        return render_template("home.html", fname=fname)
    else:
        return render_template("home.html")
@app.route('/booking')
def booking():
    if "email" in session:
        email=session["email"]
        user = Users.query.filter_by(email=email).first()
        fname = user.fname if user else None
        #fname = session["email"]
        return render_template("booking.html", fname=fname)
    else:
        return render_template("features.html")

@app.route('/login', methods=["POST", "GET"])
def login():
    if "email" not in session:
        if request.method == "POST":
            session.permanent = True
            email = request.form["email"]
            password = request.form["password"]
            
            user = Users.query.filter_by(email=email).first()         
            if user and check_password_hash(user.password, password):
                session["email"] = email
                return redirect(url_for("profile"))
            else:
                flash("Invalid email or password.", "error")
                return redirect(url_for("login"))
        else:
            return render_template("login.html")
    else:
        return redirect(url_for("profile"))

@app.route("/profile")
def profile():
    if "email" in session:
        email=session["email"]
        user = Users.query.filter_by(email=email).first()
        fname = user.fname if user else None
        #fname = session["email"]
        return render_template("user.html", fname=fname)
    else:
        return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "email" not in session:
        if request.method == "POST":
            fname = request.form["fname"]
            lname = request.form["lname"]
            email = request.form["email"]
            password = request.form["password"]
            existing_user = Users.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already registered. Please login to continue.")
                return redirect(url_for("login"))
            password_hash = generate_password_hash(password)
            new_user = Users(fname=fname, lname=lname, email=email, password=password_hash)
            db.session.add(new_user)
            db.session.commit()
            flash("Sign-up Done. Please login!")
            return redirect(url_for("login"))
        else:
            return render_template("signup.html")
    else:
        return render_template("home.html")
@app.route("/logout")
def logout():
    session.pop("email", None)
    session.pop("password",None)  
    return redirect(url_for("login"))

@app.route('/passengerdetails', methods=["GET","POST"])
def passengerdetails():
    if request.method=="GET":
        from_location = request.args.get('from')
        to_location = request.args.get('to')
        travel_date = request.args.get('date')
        passenger_count = request.args.get('passengers')
        berth_class = request.args.get('berth_class')
        return render_template('passengerdetails.html', from_location=from_location, to_location=to_location,
                            travel_date=travel_date, passenger_count=passenger_count, berth_class=berth_class)        

@app.route("/success", methods=["GET", "POST"])
def success():
        if "email" in session:
            from_location = request.form.get('from_location')
            to_location= request.form.get('to_location')
            travel_date_str = request.form.get('travel_date')
            email=session["email"]
            travel_date = datetime.strptime(travel_date_str, '%Y-%m-%d').date() if travel_date_str else None
            passenger_count=request.form.get('passenger_count')
            berth_class=request.form.get('berth_class')
            passenger_name_1=request.form.get('passenger_name-1')
            passenger_name_2=request.form.get('passenger_name-2')
            passenger_name_3=request.form.get('passenger_name-3')
            passenger_name_4=request.form.get('passenger_name-4')
            passenger_details = PassengerDetails(
                from_location=from_location,
                to_location=to_location,
                travel_date=travel_date,
                email=email,
                passenger_count=passenger_count,
                passenger_name_1=passenger_name_1,
                passenger_name_2=passenger_name_2,
                passenger_name_3=passenger_name_3,
                passenger_name_4=passenger_name_4
            )
            db.session.add(passenger_details)
            db.session.commit()
                    
            return render_template("success.html",from_location=from_location, to_location=to_location,
                                travel_date=travel_date,email=email, passenger_count=passenger_count, berth_class=berth_class,
                                passenger_name_1=passenger_name_1,passenger_name_2=passenger_name_2,passenger_name_3=passenger_name_3,passenger_name_4=passenger_name_4)
        else:
            return redirect(url_for("login"))
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
        app.run(debug=True)


