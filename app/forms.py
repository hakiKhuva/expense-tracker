from flask_wtf import FlaskForm
from wtforms.validators import Email, Length, DataRequired,NumberRange,EqualTo
from wtforms.fields import EmailField, PasswordField, SubmitField, TextAreaField, FloatField, DateTimeLocalField, StringField, SelectField


class AuthForm(FlaskForm):
    email = EmailField(
        "Your email",
        [
            DataRequired("Email is required!"),
            Email("Enter a valid email!"),
            Length(
                max=95,
                message="Email should not contain more than 95 characters!"
            )
        ]
    )

    password = PasswordField(
        "Password",
        [
            DataRequired("Password is required!"),
            Length(
                8, 30, "Password should contain 8 to 30 characters."
            )
        ]
    )

    submit = SubmitField(
        "Log in"
    )

class NewStatementForm(FlaskForm):
    amount = FloatField(
        "Enter amount",
        [
            DataRequired("Amount is required!"),
            NumberRange(0.0001,9999999999.99, "Entered amount could not be added to your statement!")
        ]
    )
    description = TextAreaField(
        "Enter description",
        [
            DataRequired("Description is required!"),
            Length(5,180,"Description can contain 5 to 180 characters!")
        ],
        render_kw={
            "class" : "textarea-h",
            "rows" : "2"
        }
    )

    datetime_data = DateTimeLocalField(
        format="%Y-%m-%dT%H:%M",
        validators=[
            DataRequired("This field is required!")
        ]
    )

    expense = SubmitField("Add Expense")
    income = SubmitField("Add Income")


class SettingsForm1(FlaskForm):
    name = StringField(
        "Your name",
        [
            DataRequired("Cannot set empty string as the name!"),
            Length(
                min=5, max=45,
                message="Name can contain 5 to 45 characters."
            )
        ]
    )

    update_name = SubmitField("Update name")

class SettingsForm2(FlaskForm):
    email = EmailField(
        "Your email",
        render_kw={
            "disabled" : "true"
        }
    )

class SettingsForm3(FlaskForm):
    password = PasswordField(
        "Current password",
        [
            DataRequired("Current password is required!"),
            Length(
                8, 30, "Password should contain 8 to 30 characters."
            )
        ]
    )

    new_password = PasswordField(
        "New/Confirm password",
        [
            DataRequired("New/Confirm Password password is required!"),
            Length(
                8, 30, "Password should contain 8 to 30 characters."
            ),
            # not EqualTo("password", "Password should not match with older password!")
        ]
    )
    update_password = SubmitField("Update password")

    delete_account = SubmitField("Delete account", render_kw={
        "class" : "delete"
    })

class StatementEditForm(NewStatementForm):
    expense = SubmitField("Update as Expense")
    income = SubmitField("Update as Income")
    delete_statement = SubmitField("Delete Statement", render_kw={
        "class" : "delete"
    })



class EditUserForm(SettingsForm1, AuthForm):
    update_name = None
    submit = None
    
    password = PasswordField(
        "Password to update",
        [
            Length(
                max=30, message="Password should contain 8 to 30 characters."
            )
        ]
    )

    update_account = SubmitField(
        "Update data"
    )

    delete_account = SubmitField(
        "Delete account", render_kw={
            "class" : "delete"
        })

    def __init__(self, formdata=..., **kwargs):
        super().__init__(formdata, **kwargs)
        self.name.label = "Name"
        self.email.label = "Email"