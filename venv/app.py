import os, psycopg2, requests
from models import *
from flask import Flask, session, render_template, request, jsonify, redirect, flash, url_for
from flask_session import Session
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from goodreadsapi import get_good_reads_data

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

if not os.getenv("GOODREADS_APIKEY"):
    raise RuntimeError("GOODREADS_APIKEY is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "\\x03\\xd3d\\xe6\\x0f0f?\\xc0\\xd55\\x97"
Session(app)

# Set up database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Index Page
@app.route("/")
def index():
    """
    Redirect to login page.
    """
    return render_template("login.html")

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Get the login page or log into the app.
    """
    # Attempt to log in user if credentials are correct
    if request.method == "POST":
        username = request.form.get("inputUsername")
        password = request.form.get("inputPassword")
        if username == "" or password == "":
            flash(u"Please provide a username or password", category="error")
            return redirect(url_for("login"))
        user_exists =  User.query.filter(User.username == username).first()
        if user_exists is None or not check_password_hash(user_exists.password, password):
            flash(u"Invalid Username or Password!", category="error")
            return redirect(url_for("login"))
        else:
            session["user_name"] = user_exists.username
            return render_template("search.html")
    # Return login page if it is a GET request
    return render_template("login.html")

# Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Get the sign up page.
    """
    # Attempt to sign up user if credentials are valid
    if request.method == "POST":
        username = request.form.get("inputUsername")
        password = request.form.get("inputPassword")
        user_exists =  User.query.filter(User.username == username).first()
        if username == "" or password == "":
            flash(u"Username and/or password must have values!", category="error")
            return redirect(url_for("signup"))
        elif user_exists is not None:
            flash(u"Username already taken!", category="error")
            return redirect(url_for("signup"))
        else:
            hashed_password = generate_password_hash(password)
            user = User(username=username, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash(u"Sign up succeeded!", category="success")
            return render_template("login.html")
    # Return signup page if it is a GET request
    return render_template("signup.html")

# Logout Page
@app.route("/logout", methods=["POST"])
def logout():
    """
    Logout of the app.
    """
    session.pop("user_name", None)
    return redirect(url_for("index"))

@app.route("/search", methods=["GET"])
def search():
    """
    Get the search page.
    """
    return render_template("search.html")

@app.route("/books", methods=["POST"])
def books():
    """
    Get list of books based on search query.
    """
    # Search for books with exact or partial match of query and return them
    searchbox = request.form.get("searchbook")   
    bookfull = Book.query.filter(or_(Book.isbn == searchbox, Book.title == searchbox, Book.author == searchbox)).all()
    bookpart = Book.query.filter(or_(Book.isbn.ilike(f"%{searchbox}%"), Book.title.ilike(f"%{searchbox}%"), Book.author.ilike(f"%{searchbox}%"))).all()
    return render_template("books.html", searchbox=searchbox, bookfull=bookfull, bookpart=bookpart)

@app.route("/books/<book_isbn>", methods=["GET"])
def book(book_isbn):
    """
    Get book data of specific book.

        Parameters:
            isbn (string): The desired book ISBN.
            
    """
    book = Book.query.get(book_isbn)
    if book is None:
        return render_template("notfound.html", message="Couldn't find a book with that ISBN")
    #get GoodReads API data
    # api_key = os.getenv("GOODREADS_APIKEY")
    # res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": book.isbn})
    # data = res.json()
    datalist = get_good_reads_data(book.isbn)
    averagerating = datalist["average_rating"]
    ratingscount = datalist["ratings_count"]
    isAnonymous = session.get("user_name")
    reviewed = False
    # Check if user has posted review for book
    if isAnonymous is not None:
        current_user = session["user_name"]
        check_user = User.query.filter(User.username == current_user).first()
        check_review = Review.query.filter(Review.user_name == check_user.username).first()      
        if check_review is not None:
            reviewed = True
        else:
            reviewed = False
    reviews = Review.query.filter(Review.book_isbn == book.isbn).all()
    return render_template("book.html", book=book, ratingscount=ratingscount, averagerating=averagerating, reviewed=reviewed, reviews=reviews)

@app.route("/post-review", methods=["POST"])
def post_review():
    """
    Post a book review.
    """
    rating = request.form.get("book_rating")
    review = request.form.get("book_review")    
    book_isbn = request.form.get("book_isbn")
    user_name = session["user_name"]
    review = Review(review=review, rating=rating, book_isbn=book_isbn, user_name=user_name)
    db.session.add(review)
    db.session.commit()
    return redirect(url_for("book", book_isbn=book_isbn))

# API Endpoint  
@app.route("/api/books/<isbn>")
def book_api(isbn):
    """
    Get book data of specific book.

        Parameters:
            isbn (string): The desired book isbn.

        Returns:
            JSON: {title, author, year, isbn, review_count, average_score}
    """
    book = Book.query.get(isbn)
    if book is None:
        return jsonify({"error": "Invalid isbn"}), 422
    # api_key = os.getenv("GOODREADS_APIKEY")
    # res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": book.isbn})
    # data = res.json()
    datalist = get_good_reads_data(book.isbn)
    averagerating = datalist["average_rating"]
    ratingscount = datalist["ratings_count"]

    return jsonify({
    "title": book.title,
    "author": book.author,
    "year": book.year,
    "isbn": book.isbn,
    "review_count": ratingscount,
    "average_score": averagerating
    })
