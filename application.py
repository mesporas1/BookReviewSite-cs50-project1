import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def signup():
    #Sign up for a username and password
    # Get username and password
    return render_template("signup.html")

@app.route("/success", methods=["POST"])
def success():
    #Display a successful username and password

    # Get username and password
    username = request.form.get("username")
    password = request.form.get("password")
   
    # Make sure username and password exist.
    if db.execute("SELECT * FROM users WHERE username = :username",{"username": username}).rowcount > 0:
        return render_template("error.html", message = "Username exists")
    else:
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",{"username":username, "password":password})
        db.commit()
        return render_template("success.html")
    
    

@app.route("/login", methods=["POST"])
def login():
    # Get username and password
    username = request.form.get("username")
    password = request.form.get("password")
    
    # Make sure username and password exist
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password",{"username": username, "password": password}).rowcount == 0:
        return render_template("error.html", message = "No such username and password exists")
    else:
        return render_template("books.html", user = username)


#@app.route("/books")
#def books():
#    """Lists all flights."""
#    books = db.execute("SELECT * FROM books").fetchall()
#    return render_template("flights.html", flights=flights)