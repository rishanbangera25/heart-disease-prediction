from flask import Flask, render_template, request, redirect, session, url_for, flash
import numpy as np
import pickle
import pandas as pd
from flask_sqlalchemy import SQLAlchemy

model = pickle.load(open("model (1).pkl","rb"))

app = Flask(__name__)

# session key
app.secret_key = "secret123"

# database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


# user table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))


# Home page
@app.route('/')
def home():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/methodology')
def methodology():
    return render_template("methodology.html")


@app.route('/login', methods=["GET","POST"])
def login():

    if request.method == "POST":

        print("Login button clicked")   # DEBUG

        email = request.form["email"]
        password = request.form["password"]

        print(email, password)   # DEBUG

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session["user"] = user.username
            return redirect("/")
        else:
            return "Invalid login details"

    return render_template("login.html")


# REGISTER
@app.route('/register', methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        new_user = User(username=username, email=email, password=password)

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# Prediction route
@app.route('/predict', methods=['GET','POST'])
def predict():

    # Check login
    if 'user' not in session:
        flash("Please login to access the prediction page.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':

        age = int(request.form['age'])
        sex = request.form['sex']
        cp = request.form['cp']
        bp = int(request.form['bp'])
        chol = int(request.form['cholesterol'])
        fbs = int(request.form['fbs'])
        ecg = request.form['ecg']
        hr = int(request.form['hr'])
        angina = request.form['angina']
        oldpeak = float(request.form['oldpeak'])
        slope = request.form['slope']

        data = {
            "Age": age,
            "Sex": sex,
            "ChestPainType": cp,
            "RestingBP": bp,
            "Cholesterol": chol,
            "FastingBS": fbs,
            "RestingECG": ecg,
            "MaxHR": hr,
            "ExerciseAngina": angina,
            "Oldpeak": oldpeak,
            "ST_Slope": slope
        }

        df = pd.DataFrame([data])
        df = pd.get_dummies(df)
        df = df.reindex(columns=model.feature_names_in_, fill_value=0)

        prediction = model.predict(df)
        result = "High Risk of Heart Disease" if prediction[0] == 1 else "Low Risk of Heart Disease"

        return render_template("predict.html", prediction_text=result)

    # GET request: just show the empty form
    return render_template("predict.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)