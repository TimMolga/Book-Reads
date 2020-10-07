import csv
import os

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    """
    Helper method to import data from books.csv file and commit to db.
    """
    rows = 0
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        book = Book(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
        print(f"Added {title} from books.csv")     
        db.session.commit()
        rows += 1
    print(f"Added {rows} from books.csv")

if __name__ == "__main__":
    with app.app_context():
        main()