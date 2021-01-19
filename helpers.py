from functools import wraps
from flask import session, request, redirect, url_for, render_template

def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'logged_in' in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code=400):
    def escape(s):
        """ for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s """

    return render_template("apology.html", top=code, bottom=message), code