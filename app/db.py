from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    session_id = db.Column(db.Text, nullable=False)

    statements = db.relationship("Statements", backref=db.backref("user"), passive_deletes=True)

    def __repr__(self) -> str:
        return "<Id:%s>"%(str(self.id))


class VisitorStats(db.Model):
    __tablename__ = "visitor_stats"
    id = db.Column(db.Integer, primary_key=True)
    browser = db.Column(db.String(100))
    device = db.Column(db.String(100))
    operating_system = db.Column(db.String(100))
    is_bot = db.Column(db.Boolean())
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self) -> str:
        return "<Id:%s>"%(str(self.id))


class Statements(db.Model):
    __tablename__ = "statements"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    operation_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    statement_id = db.Column(db.String(50), nullable=False, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))

    def __repr__(self) -> str:
        return "<Id:%s>"%(str(self.id))


class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    session_id = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self) -> str:
        return "<Id:%s>"%(str(self.id))