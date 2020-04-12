# Project 1
This project was created as part of a Harvard University training course "Web Programming with Python and JavaScript". 
The project is written in Python for the Flask micro framework, and meets project requirements.

https://docs.cs50.net/web/2020/x/projects/1/project1.html

The project is a web site with a search for information about books.
To use the site you need to register. If you are not registered, then you will not be able to access the site. After registration, or if you have done this before, you must log in to the site. 
If you did everything correctly, you will go to the main page of the site. At the top of the main page is the site logo, search menu and user section. There are three search modes available to the user: search by ISBN, search by book title, search by author. The user section displays the user's greeting and the logout button. Below the menu bar on the main page, random 25 books are displayed. The ISBN number, title of the book, its author and year of publication are displayed. If one of these books interested the user, he can click on it and go to the page of the book. Also, the user can search for the book he needs by ISBN number, title or author. Then, from the list of found books, select the one you are interested in.
On the book page, the user is provided with information about the selected book. Information includes ISBN number, title of the book, author, year of publication. Below is displayed information obtained by the API from the GoodRead resource, namely the average rating of the book and the number of views. Below, the user can rate the book and leave a short comment. Further displayed are the ratings and comments that other users have left.
This project also includes the API service. Everyone can access it. To do this, just make a request /api/isbn, where isbn is the ISBN number of the book of interest.
