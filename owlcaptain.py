from flask import Flask, render_template, request, abort, redirect, url_for
from flask import g as fl_g
import db
import configparser
import datetime
import telegram
from raven.contrib.flask import Sentry

app = Flask(__name__)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

config = configparser.ConfigParser()
config.read("config.ini")

app.secret_key = config["Flask"]["secret_key"]

telegram_bot = telegram.Bot(config["Telegram"]["bot_token"])

sentry = Sentry(app, dsn=config["Sentry"]["token"])


@app.before_request
def pre_request():
    fl_g.event_started, fl_g.event_progress = db.Halloween.puzzle_status()
    fl_g.all_moons_done = True
    for moon in fl_g.event_progress:
        if not moon:
            fl_g.all_moons_done = False
    fl_g.time_left = datetime.datetime.fromtimestamp(1540999800) - datetime.datetime.now()
    fl_g.display_on_main_site = (fl_g.time_left < datetime.timedelta(days=7)) or __debug__
    fl_g.css = "spoopy.less" if (fl_g.event_started or __debug__) else "nryg.less"
    fl_g.rygconf = config


@app.route("/")
def page_owlcaptain():
    return render_template("owlcaptain.html")


@app.route("/voiceofevil", methods=["POST"])
def page_voiceofevil():
    if request.form.get("solution", "") != "1":
        abort(400)
        return
    if "user_id" not in request.form:
        abort(403)
        return
    db_session = db.Session()
    halloween = db_session.query(db.Halloween).filter_by(royal_id=request.form["user_id"]).one_or_none()
    if halloween is None:
        abort(403)
        return
    halloween[4] = datetime.datetime.now()
    db_session.commit()
    return redirect(url_for("page_owlcaptain"))


@app.route("/mansion", methods=["POST"])
def page_mansion():
    if request.form.get("solution", "") != "bobooboooboooo":
        abort(400)
        return
    db_session = db.Session()
    halloween = db_session.query(db.Halloween).filter_by(royal_id=request.form["user_id"]).one_or_none()
    if halloween is None:
        abort(403)
        return
    halloween[6] = datetime.datetime.now()
    db_session.commit()
    return redirect(url_for("page_owlcaptain"))


@app.route("/whatpumpkin", methods=["POST"])
def page_whatpumpkin():
    return redirect("https://t.me/Steffo")


if __name__ == "__main__":
    app.run(debug=True, port=1234)