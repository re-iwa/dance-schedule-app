from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
import calendar
from datetime import datetime

app = Flask(__name__)

genres = ["HIPHOP", "LOCK", "POP", "HOUSE"]
events = ["新歓", "学祭", "コンテスト"]   # ← データは保持
places = ["体育館", "スタジオ", "外練"]

times = [
    "08:00","09:00","10:00","11:00",
    "12:00","13:00","14:00","15:00",
    "16:00","17:00","18:00","19:00"
]

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///schedule.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10))
    time = db.Column(db.String(10))
    genre = db.Column(db.String(50))
    event = db.Column(db.String(50))  # ← 残す
    place = db.Column(db.String(50))
    name = db.Column(db.String(50))   # ← 残す


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        new = Schedule(
            date=request.form.get("date"),
            time=request.form.get("time"),
            genre=request.form.get("genre"),
            event=request.form.get("event"),  # ← 値は受け取る（空でもOK）
            place=request.form.get("place"),
            name=request.form.get("name"),    # ← 同上
        )
        db.session.add(new)
        db.session.commit()
        return redirect("/")

    now = datetime.now()
    year = request.args.get("year", default=now.year, type=int)
    month = request.args.get("month", default=now.month, type=int)

    schedules = Schedule.query.filter(
        Schedule.date.like(f"{year}-{month:02d}-%")
    ).all()

    date_dict = defaultdict(list)
    for s in schedules:
        if s.date:
            date_dict[s.date].append(s)

    cal = calendar.monthcalendar(year, month)

    return render_template(
        "index.html",
        calendar=cal,
        year=year,
        month=month,
        date_dict=date_dict,
        genres=genres,
        events=events,
        places=places,
        times=times
    )


@app.route("/delete/<int:id>")
def delete(id):
    s = Schedule.query.get(id)
    if s:
        db.session.delete(s)
        db.session.commit()
    return redirect(request.referrer or "/")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    schedule = Schedule.query.get_or_404(id)

    if request.method == "POST":
        schedule.date = request.form.get("date")
        schedule.time = request.form.get("time")
        schedule.genre = request.form.get("genre")
        schedule.event = request.form.get("event")
        schedule.place = request.form.get("place")
        schedule.name = request.form.get("name")

        db.session.commit()
        return redirect("/")

    return render_template(
        "edit.html",
        schedule=schedule,
        genres=genres,
        events=events,
        places=places,
        times=times
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)