from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from ..forms import SettingsForm1, SettingsForm2, SettingsForm3
from ..db import db
from ..app_functions import get_current_user, user_login_required


settings = Blueprint("Settings", __name__, url_prefix="/settings")


@settings.route("/", methods=("GET","POST"))
@user_login_required
def settings_index():
    form1 = SettingsForm1(request.form)
    form2 = SettingsForm2(request.form)
    form3 = SettingsForm3(request.form)

    if form1.validate_on_submit():
        name = form1.name.data.strip()

        user = get_current_user()
        user.name = name
        db.session.commit()
        
        flash("Name was changed successfully", "green")
        return redirect(url_for(".settings_index"))

    elif form3.validate_on_submit():
        password = form3.password.data
        new_password = form3.new_password.data
        
        update_password = form3.update_password.data
        delete_account = form3.delete_account.data

        user = get_current_user()

        if check_password_hash(user.password, password):
            if update_password:
                if password == new_password:
                    flash("Could not update the password as same as old password!","red")
                else:
                    user.password = generate_password_hash(new_password)
                    db.session.commit()
                    flash("Password updated successfully","green")

            elif delete_account:
                if password != new_password:
                    flash("current and confirm password does not matched!")
                else:
                    db.session.delete(user)
                    db.session.commit()
                    flash("Account deleted successfully.")
            
            else:
                flash("cannot process your request, tryagain", "red")
            return redirect(url_for("Auth.auth_index"))
        else:
            flash("Incorrect password to perform operation!","red")
            return redirect(url_for(".settings_index"))

    user = get_current_user()

    form1.name.data = user.name
    form2.email.data = user.email

    return render_template(
        "settings/index.html",
        title="Settings",
        form1=form1,
        form2=form2,
        form3=form3,
        footer=True
    )