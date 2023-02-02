import datetime
import hashlib
import random
import uuid
import string
import base64
import typing
import io
from matplotlib.figure import Figure
from matplotlib.axes import Axes

def generate_id(name, email, hashed_password, limit=16):
    req = "--".join([name, email, hashed_password, str(datetime.datetime.now())])
    req += uuid.uuid4().hex
    return hashlib.sha1("".join(random.choice(req) for _ in range(limit)).encode()).hexdigest()


def generate_string(limit:int = 12):
    data = str(datetime.datetime.now())
    uuid4 = uuid.uuid4().hex
    confirm_data = string.ascii_letters+data+uuid4
    return "".join(random.choice(confirm_data) for _ in range(limit))


def get_base64_encode(buffer:str):
    if isinstance(buffer, str):
        buffer = buffer.encode()
    return base64.urlsafe_b64encode(buffer).decode()

def get_base64_decode(buffer):
    try:
        return base64.urlsafe_b64decode(buffer).decode()
    except ValueError:
        return ""


def get_pie_chart(data:list[tuple[str,typing.Union[int, float]]], title:str):
    pie_data = [x[1] for x in data]

    percentages = [x*100/sum(pie_data) for x in pie_data]
    labels = [f"{data[i][0]}({data[i][1]}) - {percentages[i]:.2f}%" for i in range(len(data))]
    explode = [0.001*x for x in percentages]

    data_buf = io.BytesIO()
    fig = Figure(figsize=(10,4))

    ax = fig.subplots()
    ax.pie(
        pie_data,
        explode=explode,
        startangle=90,
    )
    ax.set_title(title)

    fig.tight_layout()
    fig.legend(labels=labels, loc="lower left",)

    fig.savefig(data_buf, format="png", transparent=True)
    data_buf.seek(0)
    return base64.b64encode(data_buf.read()).decode("utf-8")


def get_line_chart(data:list[tuple[str,typing.Union[float, int]]], xlabel:str, ylabel:str, title:str):
    fig = Figure(figsize=(10,4))
    
    data_buf = io.BytesIO()

    ax:Axes = fig.subplots()
    ax.plot(
        [x[0] for x in data],
        [x[1] for x in data],
    )
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()

    fig.savefig(data_buf, transparent=True)

    data_buf.seek(0)
    return base64.b64encode(data_buf.read()).decode("utf-8")


def get_bar_chart(data:list[tuple[str,typing.Union[float, int]]], xlabel:str, ylabel:str, title:str):
    fig = Figure(figsize=(10,4))
    
    data_buf = io.BytesIO()

    ax:Axes = fig.subplots()
    ax.bar(
        [x[0] for x in data],
        [x[1] for x in data],
    )
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()

    fig.savefig(data_buf, transparent=True)

    data_buf.seek(0)
    return base64.b64encode(data_buf.read()).decode("utf-8")