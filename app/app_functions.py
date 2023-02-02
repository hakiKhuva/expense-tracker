from flask import session, redirect, url_for
from .db import User, Statements, Admin
from .functions import get_base64_decode
from sqlalchemy import func
from functools import wraps


def get_login() -> bool:
    """
    returns wheather user is logged in or not
    """
    sign_id = session.get("session-sign-id")
    if sign_id:
        sign_id = get_base64_decode(sign_id)
        if sign_id and sign_id != "":
            user = User.query.filter(User.session_id == sign_id).first()
            if user:
                return True
            session.pop("session-sign-id")
    return False


def get_admin_login() -> bool:
    """
    returns wheather user is logged in or not
    """
    sign_id = session.get("admin-sign-id")
    if sign_id:
        sign_id = get_base64_decode(sign_id)
        if sign_id and sign_id != "":
            user = Admin.query.filter(User.session_id == sign_id).first()
            if user:
                return True
            session.pop("admin-sign-id")
    return False


def get_current_user():
    """
    returns current user if logged in, run `get_login`
    before running this function to check login status

    returns User if loggedin
    
    return None if not loggedin
    """
    sign_id = session.get("session-sign-id")
    if sign_id:
        sign_id = get_base64_decode(sign_id)
        if sign_id and sign_id != "":
            user = User.query.filter(User.session_id == sign_id).first()
            return user
    return None

# def get_current_user_account(user_id):
def get_current_user_balance():
    """
    returns the user_account table user information
    """
    user_id = get_current_user().id
    account_balance = Statements.query.with_entities(func.sum(Statements.amount)).filter(Statements.user_id == user_id).first()[0]
    if account_balance is None:
        return 0.00
    return account_balance



def user_login_required(f):
    @wraps(f)
    def fun(*args, **kwargs):
        if get_login() is True:
            return f(*args, **kwargs)
        return redirect(url_for("Auth.auth_index"))
    return fun


def admin_login_required(f):
    @wraps(f)
    def fun(*args, **kwargs):
        if 'admin-sign-id' in session:
            return f(*args, **kwargs)
        return redirect(url_for("Admin.admin_login"))
    return fun