# Expense Tracker

Expense tracker in Python Flask supports following actions

- Login/Signup
- Add statement
- Delete statement
- Calculate final amount
- Show all statements
- Admin functionality
- Download all statements

## Run the project

> You must have python3 installed on your system before running

> used python 3.10.2 for this project

### Create virtual environment and activate it

```bash
# bash
$ python3 -m venv env

# windows
> python -m venv env
> env\Scripts\activate
```

### Install requirements

```bash
$ pip install -r requirements.txt
```

### Set secret key and database URI

```bash
# bash
(env) $ export DB_URI="database uri"
(env) $ export SECRET_KEY="secret key"

# windows
(env) > SET DB_URI=database_uri
(env) > SET SECRET_KEY=secret_key
```

### final run
```bash
$ flask run
```