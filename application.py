import os
import random
import requests

from flask import Flask, session, url_for, render_template, redirect, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = "secret"

#Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"

#Session(app)


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.pop("user", None)

        name = request.form.get("username")
        pas = request.form.get("password")

        if not name:
            return render_template("error.html", message='No username specified!')

        if not pas:
            return render_template("error.html", message='No password specified!')

        if db.execute("SELECT * FROM users WHERE username = :user", {"user": name}).rowcount == 0:
            return render_template("error.html", message='Username does not exist.')

        row = db.execute("SELECT * FROM users WHERE username = :user", {'user': name})
        user = row.fetchone()

        if user[2] != pas:
            return render_template("error.html", message="Invalid password")
        else:
            session["user"] = name
            session["user_id"] = user[0]
            return redirect( "/main.html")

    else:
        return render_template("login.html")

@app.route("/registration.html", methods=["GET", "POST"])
def registr():
    if request.method == "POST":

        name = request.form.get("username")
        pas = request.form.get("password")

        if not name:
            return render_template("error.html", message='To register, you must specify the username!')

        if not pas:
            return render_template("error.html", message='To register, you must specify the password!')

        if db.execute("SELECT * FROM users WHERE username = :user", {"user": name}).rowcount != 0:
            return render_template("error.html", message='This username is already taken, please think of something else.')

        db.execute("INSERT INTO users (username, password) VALUES (:user, :pass)",
                {"user": name, "pass": pas} )
        db.commit()

        return render_template("sucses.html", message='Are you registered! Now you can log in to the site.')

    else:    
        return render_template("registration.html")

@app.route("/main.html", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        value = request.form.get("search")
        type_search = request.form.get("search_mode")

        if value is None:
            return render_template("error.html", message='Search text not set!')

        if type_search == "isbn":
            rows = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", {'isbn': '%' + value + '%'})
            rowCount = rows.rowcount
            books = rows.fetchall()
        elif type_search == "title":
            rows = db.execute("SELECT * FROM books WHERE title LIKE :title", {'title': '%' + value + '%'})
            rowCount = rows.rowcount
            books = rows.fetchall()
        elif type_search == "author":
            rows = db.execute("SELECT * FROM books WHERE author LIKE :author", {'author': '%' + value + '%'})
            rowCount = rows.rowcount
            books = rows.fetchall()

        if rowCount == 0:
            return render_template("error.html", message='No results were found for your request!')

        return render_template("main.html", books=books, count=rowCount)
    
    else:
        if "user" in session:
            return render_template("main.html", books=randomBooks(), count=25)

        else:
            return render_template("error.html", message='You are not authorized!')


def randomBooks():
    books=[]
    for b in range(25):
        book = db.execute("SELECT * FROM books ORDER BY RANDOM() LIMIT 1").fetchone()
        books.append(book)
    return books

@app.route("/logout")
def logout():
    session.pop("user", None)
    return render_template("sucses.html", message='You are logged out! Thank you for being with us!')

@app.route("/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :book_id", {'book_id': book_id}).fetchone()
    if request.method == "POST":
        user_id = session["user_id"]
        rating = int(request.form.get("rating"))
        comment = request.form.get("coment")

        db.execute("INSERT INTO coments (range, coment, user_id, book_id) VALUES (:range, :coment, :user, :book)",
                    {'range': rating, 
                    'coment': comment, 
                    'user': user_id, 
                    'book': book_id})
        db.commit()

        return render_template("sucses.html", message='Your comment has been added.')

    else:
        if "user" in session:
            goodreadGet = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "4ob2Ylynj5tJWZVmiqhQ", "isbns": book[1]})
            if goodreadGet.status_code != 200:
                goodreadStatus = False
            else:
                goodreadStatus = True
            goodread = goodreadGet.json()
            grAverage = goodread["books"][0]["average_rating"]
            grNumRating = goodread["books"][0]["work_ratings_count"]

            rows = db.execute("SELECT range, coment, user_id FROM coments WHERE book_id = :book", {'book': book_id})
            comentCount = rows.rowcount
            coments = rows.fetchall()
            if comentCount != 0:
                usersComents = []
                rang = 0
                for i in range(comentCount):
                    rang = rang + coments[i][0]
                    usersComents.append([])
                    user_id = coments[i][2]
                    user = db.execute("SELECT * FROM users WHERE id = :user", {'user': user_id}).fetchone() 
                    usersComents[i].append(user[1])
                    usersComents[i].append(coments[i][0])
                    usersComents[i].append(coments[i][1])
                userRange = round(rang / comentCount, 2)
            else:
                usersComents = 0
                userRange = 0

            if db.execute("SELECT * FROM coments WHERE user_id = :user AND book_id = :book", 
                        {'user': session["user_id"], 
                        'book': book_id}).rowcount != 0:
                writeComent = False
            else:
                writeComent = True
            
            return render_template("book.html", 
                                    book = book, 
                                    grSt = goodreadStatus, 
                                    grA = grAverage, 
                                    grNR = grNumRating, 
                                    userRating = userRange, 
                                    comCount = comentCount,
                                    coments = usersComents, 
                                    writeCom = writeComent)

        else:
            return render_template("error.html", message='You are not authorized!')

@app.route("/api/<int:book_isbn>", methods=["GET"])
def book_api(book_isbn):
    bookISBN = str(book_isbn)
    while (len(bookISBN) != 10):
        bookISBN = '0'+bookISBN
    
    row = db.execute("SELECT id, title, author, year FROM books WHERE isbn = :book", {'book': bookISBN})
    rCount = row.rowcount
    book = row.fetchone()
    
    rows = db.execute("SELECT * FROM coments WHERE book_id = :book_id", {'book_id': book[0]})
    reviewCount = rows.rowcount
    coments = rows.fetchall()
    if reviewCount != 0:
        rang = 0
        for i in range(reviewCount):
            rang = rang + coments[i][1]
        averageScore = round(rang/reviewCount, 2)
    else:
        averageScore = 0

    if book is None:
        return jsonify({"error": "Invalid book_isbn"}), 422
    
    return jsonify({"isbn": book_isbn, 
                    "title": book[1], 
                    "author": book[2], 
                    "year": book[3], 
                    "review_count": reviewCount, 
                    "average_score": averageScore})