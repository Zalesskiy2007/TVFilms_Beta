from flask import Flask, render_template, request, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, logout_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import flask_login
import os
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DATABASE_URL']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ['SK']
db = SQLAlchemy(app)

login_manager = LoginManager(app)

class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(), nullable=False)
    short_desc = db.Column(db.String(), nullable=False)
    photo = db.Column(db.String(), nullable=False)
    video = db.Column(db.String(), nullable=False)
    actors = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    by = db.Column(db.String(), nullable=False)

class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filmid = db.Column(db.Integer, nullable=False)
    first = db.Column(db.String(), nullable=False)
    last = db.Column(db.String(), nullable=False)
    review = db.Column(db.String(), nullable=False)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)

@login_manager.user_loader
def user_loader(user_id):
    return Users.query.get(int(user_id))

@app.route("/", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        user = Users.query.filter_by(login=login).first()
        if check_password_hash(user.password, password):
            login_user(user)
        else:
            abort(400)
        return redirect("/home")
    return render_template("login.html")

@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        firstn = request.form["firstn"]
        lastn = request.form["lastn"]
        login = request.form["login"]
        if request.form["password"] == request.form["repeat_password"]:
            password = generate_password_hash(request.form["password"])
        else:
            abort(400)
        user = Users(
            login = login,
            password = password,
            first_name = firstn,
            last_name = lastn
        )
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=False)
        return redirect("/home")
    return render_template("register.html")
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")
@app.route("/home")
def main():
    films = Film.query.all()
    return render_template("main.html", films=films)

@app.route("/review/<int:id>", methods=["POST", "GET"])
def review(id):
    movie = Film.query.filter_by(id=id).first()
    if request.method == "POST":
        user = Users.query.filter_by().first()
        first = flask_login.current_user.first_name
        last = flask_login.current_user.last_name
        review = request.form["review"]
        filmid = movie.id
        added = Reviews(
            filmid = filmid,
            first = first,
            last = last,
            review = review
        )
        db.session.add(added)
        db.session.commit()
        return redirect(f"/{id}")
    else:
        return render_template("review.html")

@app.route("/<int:id>")
def film(id):
    movie = Film.query.filter_by(id=id).first()
    rev = Reviews.query.filter_by(filmid=movie.id)
    return render_template("film.html", mov = movie, rev=rev)

@app.route("/addfilm", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        c = description.split()
        short_desc = []
        for i in range(10):
            short_desc.append(c[i])
        short = " ".join(short_desc) + "..."
        photo = request.form['photo']
        video = request.form['video']
        actors = request.form['actors']
        price = request.form['price']
        by = f"{flask_login.current_user.first_name} {flask_login.current_user.last_name}"
        film = Film(
            title = title,
            description = description,
            photo = photo,
            video = video,
            actors = actors,
            price = price,
            by=by,
            short_desc=short
        )
        db.session.add(film)
        db.session.commit()
        return redirect("/home")
    else:
        return render_template("addfilm.html")
@app.route("/search", methods=["POST", "GET"])
def search():
    a = []
    if request.method == "POST":
        film = Film.query.all()
        str = request.form["searchholder"]
        if str != "":
            for i in film:
                if str in i.title:
                    a.append(i)
            return render_template("search.html", films=a)
        else:
            return render_template("search.html")
    return render_template("search.html")

if __name__ == "__main__":
    app.run(debug=False)
