import os
import pickle
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

model = pickle.load(open("artifact/modelo_rdfr_grid.pkl", "rb"))
columns = pickle.load(open("artifact/columns.pkl", "rb"))
ord_country = pickle.load(open("artifact/ord_country.pkl", "rb"))
ord_ed_level = pickle.load(open("artifact/ord_ed_level.pkl", "rb"))
scaler = pickle.load(open("artifact/scaler.pkl", "rb"))

BASEDIR = os.path.abspath(os.path.dirname(__file__))
DBPATH = os.path.join(BASEDIR, "db.sqlite3")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DBPATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Country(db.Model):
    __tablename__ = "countries"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Country {self.name}>"


class EducationLevel(db.Model):
    __tablename__ = "education_levels"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<EducationLevel {self.name}>"


class Professions(db.Model):
    __tablename__ = "professions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Professions {self.name}>"


@app.route("/")
def home():
    countries = Country.query.all()
    education_levels = EducationLevel.query.all()
    professions = Professions.query.all()
    return render_template(
        "index.html",
        countries=countries,
        education_levels=education_levels,
        professions=professions,
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
