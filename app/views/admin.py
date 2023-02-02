from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from werkzeug.security import check_password_hash, generate_password_hash
from ..db import Admin, User, Statements, VisitorStats, db
from sqlalchemy import func, desc, cast, Date
from ..forms import AuthForm, EditUserForm
from ..functions import get_pie_chart, get_line_chart
from ..app_functions import admin_login_required
import math

admin = Blueprint("Admin",__name__, url_prefix="/admin")

@admin.route("/")
@admin_login_required
def dashboard():
    if 'admin-sign-id' not in session:
        return redirect(url_for(".admin_login"))
    
    admin = Admin.query.filter(Admin.session_id == session.get("admin-sign-id")).first_or_404()

    name = admin.username

    users_count = User.query.with_entities(func.count(User.id)).first()[0]
    statements_count = Statements.query.with_entities(func.count(Statements.id)).first()[0]

    visits_count = VisitorStats.query.with_entities(func.count(VisitorStats.browser)).first()[0]
    bots_visits = VisitorStats.query.filter(VisitorStats.is_bot == True).with_entities(func.count(VisitorStats.is_bot)).first()[0]
    other_user_agent_visits = VisitorStats.query.filter(VisitorStats.browser == "other").with_entities(func.count(VisitorStats.browser)).first()[0]

    most_used_useragent = VisitorStats.query.with_entities(VisitorStats.browser, func.count(VisitorStats.browser).label("browser_count")).group_by(VisitorStats.browser).order_by(desc("browser_count")).limit(1).first()[0]
    most_used_operating_system = VisitorStats.query.with_entities(VisitorStats.operating_system, func.count(VisitorStats.operating_system).label("os")).group_by(VisitorStats.operating_system).order_by(desc("os")).limit(1).first()[0]
    highest_visits_with_date = VisitorStats.query.with_entities(cast(VisitorStats.date, Date), func.count(cast(VisitorStats.date, Date)).label("date")).group_by(cast(VisitorStats.date, Date)).order_by(desc("date")).limit(1).first()

    less_used_useragent = VisitorStats.query.with_entities(VisitorStats.browser, func.count(VisitorStats.browser).label("browser_count")).group_by(VisitorStats.browser).order_by("browser_count").limit(1).first()[0]
    less_used_operating_system = VisitorStats.query.with_entities(VisitorStats.operating_system, func.count(VisitorStats.operating_system).label("os")).group_by(VisitorStats.operating_system).order_by("os").limit(1).first()[0]
    lowest_visits_with_date = VisitorStats.query.with_entities(cast(VisitorStats.date, Date), func.count(cast(VisitorStats.date, Date)).label("date")).group_by(VisitorStats.date).order_by("date").limit(1).first()

    browser_data = VisitorStats.query.with_entities(VisitorStats.browser, func.count(VisitorStats.browser)).group_by(VisitorStats.browser).all()
    browser_pie_chart = get_pie_chart(browser_data, "Browser used by visitors")

    operating_system_data = VisitorStats.query.with_entities(VisitorStats.operating_system, func.count(VisitorStats.operating_system)).group_by(VisitorStats.operating_system).all()
    operating_system_chart = get_pie_chart(operating_system_data, "Operating System of visitors")

    visits_data = VisitorStats.query.with_entities(cast(VisitorStats.date, Date), func.count(VisitorStats.date)).group_by(cast(VisitorStats.date, Date)).order_by(desc(cast(VisitorStats.date, Date))).limit(90).all()
    visits_line_chart = get_line_chart(visits_data, "Visit date", "Traffic amount", "Application visits statistics (last active 90 days)")

    return render_template(
        "admin/index.html",
        title="Admin : Dashboard : {}".format(name),
        name=name,
        table_data = {
            "Total users" : users_count,
            "Total Statements" : statements_count,
            "Average statements" : statements_count/users_count,
            "Total visits" : visits_count,
            "Bot(s) visits" : bots_visits,
            "Other user-agent visits" : other_user_agent_visits,
            "Total visits - Bot(s)" : visits_count - bots_visits,
            "Total visits - Bot(s) - Other(s)" : visits_count - bots_visits - other_user_agent_visits,
            "Most used user agent" : most_used_useragent,
            "Less used user agent" : less_used_useragent,
            "Most used OS" : most_used_operating_system,
            "Less used OS" : less_used_operating_system,
            "Highest hits date(count)" : f"{highest_visits_with_date[0]}({highest_visits_with_date[1]})",
            "Lowest hits date(count)" : f"{lowest_visits_with_date[0]}({lowest_visits_with_date[1]})",
        },
        browser_pie_chart=browser_pie_chart,
        visits_line_chart=visits_line_chart,
        operating_system_chart=operating_system_chart
    )


@admin.route("/login", methods=("GET","POST"))
def admin_login():
    form = AuthForm(request.form)

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        account = Admin.query.filter(Admin.email == email).first()

        if not account:
            flash("Admin account does not exists!","red")
        elif not check_password_hash(account.password, password):
            flash("Invalid password for admin account!","red")
        else:
            session["admin-sign-id"] = account.session_id
            return redirect(url_for(".dashboard"))

        return redirect(url_for(".admin_login"))

    return render_template(
        "admin/login.html",
        title="Admin Login",
        form=form,
        is_loggedin=False
    )    


@admin.route("/users")
@admin_login_required
def users():
    page = request.args.get("page", "1")
    users_per_page = request.args.get("upp","10")

    if not page.isnumeric() or int(page) <= 0:
        page = "1"
    page = int(page)-1

    if not users_per_page.isnumeric() or int(users_per_page) <= 0:
        users_per_page = "10"
    users_per_page = int(users_per_page)

    users_type = request.args.get("type","none").lower()
    if users_type not in ("user","admin"):
        users_type = "user"

    if users_type == "user":
        users = User.query.limit(users_per_page).offset(page*users_per_page).all()
        users_count = User.query.with_entities(func.count(User.id)).first()[0]
        page_count = math.ceil(users_count/users_per_page)
    else:
        users = Admin.query.limit(users_per_page).offset(page*users_per_page).all()
        users_count = Admin.query.with_entities(func.count(Admin.id)).first()[0]
        page_count = math.ceil(users_count/users_per_page)


    return render_template(
        "admin/users.html",
        title="Admin : users : {}".format(users_type.title()),
        users=users,
        users_count=users_count,
        users_per_page=users_per_page,
        page_count=page_count,
        current_page=page,
        prev_btn=page > 0,
        next_btn=page+1 < page_count,
        page_title=users_type.title()
    )


@admin.route("/user/<member_type>/<int:id>/<email>", methods=["GET","POST"])
@admin_login_required
def specific_user(member_type,id,email):
    member_type = member_type.lower()
    if member_type not in ("user", "admin"):
        return abort(404)
    
    if member_type == "user":
        user = User.query.filter(User.id == id, User.email == email).first()
    else:
        user = Admin.query.filter(Admin.id == id, Admin.email == email).first()
    
    if not user:
        return abort(404)

    form = EditUserForm(request.form)

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        update_account = form.update_account.data
        delete_account = form.delete_account.data

        if delete_account is True:
            db.session.delete(user)
            db.session.commit()

            flash("User deleted successfully", "green")
        
        elif update_account is True:
            if member_type == "user":
                user.name = name
            else:
                user.username = name
            user.email = email

            if password:
                user.password = generate_password_hash(password, "SHA256")
            
            db.session.commit()
            flash("User updated successfully", "green")

        else:
            flash("Operation is not supported!", "red")
        
        return redirect(url_for(".specific_user",member_type=member_type, email=email, id=id))

    if member_type == "user":
        form.name.data = user.name
    else:
        form.name.data = user.username

    form.email.data = user.email

    return render_template(
        "admin/user.html",
        title="Details of user {}".format(form.name.data),
        form=form,
    )

@admin.route("/logout", methods=["POST"])
@admin_login_required
def logout_admin():
    session.pop("admin-sign-id")
    flash("Logged out successfully.", "green")
    return redirect(url_for(".admin_login"))