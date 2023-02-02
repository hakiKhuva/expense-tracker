from flask import Blueprint, request, render_template, redirect, url_for, flash, Response, stream_with_context

from ..app_functions import get_current_user, get_current_user_balance, user_login_required
from ..functions import generate_string
from ..forms import NewStatementForm, StatementEditForm
from ..db import db, Statements, User
from sqlalchemy import func


home = Blueprint("Home", __name__)


@home.route("/")
@user_login_required
def home_index():
    user = get_current_user()

    user_details = {}
    user_details["name"] = user.name
    user_details["account_balance"] = round(get_current_user_balance(),2)
    
    statements = Statements.query.filter(Statements.user_id == user.id).order_by(Statements.operation_time.desc()).limit(5).all()

    user_details["statements"] = list(
        {"desc":x.description, "amount":x.amount, "at":x.operation_time, "id": x.statement_id} for x in statements
    )

    return render_template(
        "home/index.html",
        user= user_details
    )

@home.route("/new", methods=("GET","POST"))
@user_login_required
def new_statement():
    form = NewStatementForm(request.form)
    if form.validate_on_submit():
        amount = form.amount.data
        description = form.description.data
        at = form.datetime_data.data
        income = form.income.data
        expense = form.expense.data

        if not income and not expense:
            flash("Cannot add statement that is neither income nor expense!","red")
            return redirect(url_for(".new_statement"))
        
        amount = abs(amount)
        if expense is True:
            amount = -amount

        current_user = get_current_user()
        user_id = current_user.id
        
        statement = Statements(
            description = description,
            amount = amount,
            operation_time = at,
            user_id = user_id,
            statement_id = generate_string()
        )

        db.session.add(statement)
        db.session.commit()

        flash("Statement was added to your account successfully.", "green")
        return redirect(url_for("Home.home_index"))

    return render_template(
        "home/new_statement.html",
        title="New statement",
        form=form
    )

@home.route("/statements")
@user_login_required
def statements():
    try:
        page = int(request.args.get("page","0"))
    except:
        page = 0
    finally:
        if page < 0:
            page = 0

    page_size = 6

    user = get_current_user()

    if request.args.get("t") == "expense":
        statements = Statements.query.filter(Statements.user_id == user.id, Statements.amount < 0).order_by(Statements.operation_time.desc()).limit(page_size).offset(page_size*page).all()
    elif request.args.get("t") == "income":
        statements = Statements.query.filter(Statements.user_id == user.id, Statements.amount >= 0).order_by(Statements.operation_time.desc()).limit(page_size).offset(page_size*page).all()
    else:
        statements = Statements.query.filter(Statements.user_id == user.id).order_by(Statements.operation_time.desc()).limit(page_size).offset(page_size*page).all()

    statements = list(
        {"desc":x.description, "amount":x.amount, "at": str(x.operation_time), "id": x.statement_id} for x in statements
    )

    current_balance = get_current_user_balance()
    total_expense = Statements.query.with_entities(func.sum(Statements.amount)).filter(Statements.user_id == user.id, Statements.amount < 0).first()[0]
    if total_expense is None:
        total_expense = 0.0
    total_expense = abs(total_expense)
    total_income = Statements.query.with_entities(func.sum(Statements.amount)).filter(Statements.user_id == user.id, Statements.amount >= 0).first()[0]
    if total_income is None:
        total_income = 0.0

    if request.args.get("__a") == "1":
        return statements

    date = []
    expense_amount = []
    income_amount = []
    amount = []

    for x in Statements.query.filter(Statements.user_id == user.id).order_by(Statements.operation_time).all():
        date.append(x.operation_time)
        money = x.amount

        amount.append(abs(money))

        if money < 0:
            expense_amount.append(abs(money))
            income_amount.append(None)
        else:
            income_amount.append(money)
            expense_amount.append(None)


    return render_template(
        "home/statements.html",
        title="All statements",
        statements=statements,
        total_income=total_income,
        total_expense=total_expense,
        current_balance=current_balance,
        page_size=page_size,
        round=round
    )

@home.route("/statement/<statement_id>", methods=("GET","POST"))
@user_login_required
def specific_statement(statement_id):
    statement = Statements.query.filter(Statements.statement_id == statement_id).first_or_404()

    form = StatementEditForm(request.form)

    if form.validate_on_submit():
        amount = form.amount.data
        description = form.description.data
        date_time = form.datetime_data.data
        
        income = form.income.data
        expense = form.expense.data
        delete = form.delete_statement.data

        amount = abs(amount)

        if income is True:
            statement.amount = amount
            statement.description = description
            statement.operation_time = date_time

            db.session.commit()

            flash("Updated statement as income successfully", "green")
        
        elif expense is True:
            statement.amount = -amount
            statement.description = description
            statement.operation_time = date_time

            db.session.commit()

            flash("Updated statement as expense successfully", "green")

        elif delete is True:
            db.session.delete(statement)
            db.session.commit()

            flash("The statement was deleted successfully", "green")

            return redirect(url_for(".home_index"))

        else:
            flash("Unsupported action to perform!", "red")
        
        return redirect(url_for(".specific_statement", statement_id=statement_id))

    form.amount.data = abs(statement.amount)
    form.description.data = statement.description
    form.datetime_data.data = statement.operation_time


    return render_template(
        "home/statement.html",
        title="Statement",
        form=form,
        statement_id=statement_id
    )

@home.route("/download-statements")
@user_login_required
def download_statements():
    user = get_current_user()
    statements = Statements.query.filter(Statements.user_id == user.id)

    content_disposition = "attachment; filename={}'s-statements.csv".format(user.name)
    
    def data():
        first_iter = True
        for statement in statements.yield_per(5):
            if first_iter is True:
                first_iter = False
                yield "amount, description, datetime, type\n"

            if statement.amount < 0:
                statement_type = "expense"
            else:
                statement_type = "income"
            yield f"{abs(statement.amount)},{statement.description},{statement.operation_time.isoformat()},{statement_type}\n"

    return Response(stream_with_context(data()), 200, mimetype="text/csv",headers={
        "Content-Disposition" : content_disposition
    })