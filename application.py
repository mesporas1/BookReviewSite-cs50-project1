import os, requests

from flask import Flask, session, render_template, request, jsonify
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

# Keep track of user


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
    
    

@app.route("/search", methods=["POST"])
def search():
    # Get username and password
    username = request.form.get("username")
    password = request.form.get("password")

    # Make sure username and password exist
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password",{"username": username, "password": password}).rowcount == 0:
        return render_template("error.html", message = "No such username and password exists")
    else:
        session["user"] = username
        return render_template("search.html", user = username)

@app.route("/search/results", methods=["POST"])
def books():
    """Lists books from the search"""
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    author = request.form.get("author")
    username = session["user"]

    if isbn != "":
        isbn = "%" + request.form.get("isbn") + "%"
    if title != "":
        title = "%" + request.form.get("title") + "%"
    if author != "":
        author = "%" + request.form.get("author") + "%"

    #Make sure book exists
    books = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author", {"isbn": isbn, "title":title, "author":author}).fetchall()
    if books is None:
        return render_template("error.html", message = "No books")
    return render_template("books.html", books = books, isbn = isbn, title = title, author = author, username = username)

@app.route("/book/<int:book_id>", methods=["POST"])
def book(book_id):
    """List review of single book"""
    book_id = request.form.get("book_id")
    print(request.form.get("book_id"))
    book = db.execute("SELECT * FROM books where id = :book_id", {"book_id":book_id}).fetchone()
    print(book)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("gr-key"), "isbns" : book.isbn})
    print(res)
    #Stores results of requests into data file. Format is one list that contains a dictionary of the review counts
    data = res.json()
    #Returns the average rating from data of the received book_id
    avg_rate= data["books"][0]["average_rating"]
    

    return render_template("book.html", book_id = book_id, book=book, data=data, avg_rate=avg_rate)
    #return render_template("book.html", book_id = book_id, book=book, data=data)

@app.route("/api/<string:isbn>")
def isbn_api(isbn):
    """Return details about a single book."""

    # Make sure book exists.
    book = db.execute("SELECT * FROM books where isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid isbn"}), 404

    # Get all books isbn information
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("gr-key"), "isbns" : book.isbn})
    data = res.json()
    avg_rate= data["books"][0]["average_rating"]

    return jsonify({
            "title": book.isbn,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "average_score": avg_rate
            })