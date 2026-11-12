import os
from flask_mail import Mail, Message #was told to inmort this to use the gmail sending

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd, lookup

from flask import jsonify #jsonify will be used to translate my python data into smth that java script that understand (WHAT IS UNDERSTOOD FROM "jsonify translates your Python data into standard stringified JSON format")

# Configure application
app = Flask(__name__)

#had to add as it showed connection refused so took help from ai to debug and also learnt this from the video
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

#gmail was rejecting login so had to add by learning from ai
app.config["MAIL_USERNAME"] = "chiragmishra2108@gmail.com"
app.config["MAIL_PASSWORD"] = "eisodutpchjuwary"

#could not find so took help from ai
mail = Mail(app)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def homepage():
    """Homepage"""
    return render_template("homepage.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get(
                "username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

            if not request.form.get("username"):
                return apology("must provide username", 400)

            elif not request.form.get("password"):
                return apology("must provide password", 400)

            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

            if not len(rows) == 0:
                return apology("Username already exists", 400)

            if not request.form.get("password")==request.form.get("confirmation"):
                return apology("Both passwords have to be same", 400)

            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

            return redirect("/")

    else:
        return render_template("register.html")


@app.route("/details", methods=["GET", "POST"])
@login_required
def details():
    """Get stock details"""

    if request.method == "POST":

        if not request.form.get("symbol"):
                return apology("must provide symbol", 400)

        symbol=request.form.get("symbol")
        stock=lookup(symbol)

        if stock is None:
            return apology("invalid symbol", 400)

        return render_template("details_shown.html",stock=stock)

    else:

        return render_template("details.html")


@app.route("/track", methods=["GET", "POST"])
@login_required
def track():
    """Track stock price"""

    if request.method == "POST":

        if not request.form.get("symbol"):
                return apology("must provide symbol", 400)

        if not request.form.get("min_price"):
                return apology("must provide a minimum price", 400)

        if not request.form.get("mail"):
                return apology("must provide mail", 400)

        symbol=request.form.get("symbol")
        min_price=request.form.get("min_price")
        min_price=int(min_price)
        stock=lookup(symbol)
        session["tracking_mail"] = request.form.get("mail")

        if stock is None:
            return apology("invalid symbol", 400)

        return render_template("tracking.html",symbol=symbol,min_price=min_price)

    else:

        return render_template("track.html")


@app.route("/tracking/<symbol>", methods=["GET", "POST"])
@login_required
def tracking(symbol):
    """Pulling current stock price"""

    stock=lookup(symbol)
    return jsonify(price=stock["price"])


@app.route("/mail", methods=["POST"])
@login_required
def send_mail():
    recipient_email = session.get("tracking_mail")

    msg = Message(
                subject="Stock Price Alert",
                sender="chiragmishra2108@gmail.com",
                recipients=[recipient_email])

    msg.body = "The stock is now below the price you wanted to buy it at."

    mail.send(msg)
    return "" #sucess
