import os

from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__: "users"
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)
    user_reviews = db.relationship("Review", backref="user_review")

class Book(db.Model):
    __tablename__: "books"
    isbn = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    book_reviews = db.relationship("Review", backref="book_review")

class Review(db.Model):
    __tablename__: "reviews"
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.String, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    book_isbn = db.Column(db.String, db.ForeignKey("book.isbn"), nullable=False)
    user_name = db.Column(db.String, db.ForeignKey("user.username"), nullable=False)