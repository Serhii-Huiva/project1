import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR NOT NULL)")

fl = open("books.csv")
reader = csv.reader(fl)
count = 1
for isbn, title, author, year in reader:
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", 
                {"isbn": isbn, "title": title, "author": author, "year": year})
    print(f"Added book number {count} {title} by {author}.")
    count += 1
db.commit()
