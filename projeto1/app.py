import os
import pickle
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sklearn.preprocessing import StandardScaler, OrdinalEncoder

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
    prediction_text = request.args.get("prediction_text")
    return render_template(
        "index.html",
        countries=countries,
        education_levels=education_levels,
        professions=professions,
        prediction_text=prediction_text,
    )


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = {
            "Country": request.form["countries"],
            "EdLevel": request.form["ed_levels"],
            "DevType": request.form.getlist("professions"),
            "YearsCodePro": int(request.form["yearscodepro"]),
        }
    except KeyError as e:
        return render_template(
            "index.html", prediction_text="Entrada de dados inválida."
        )

    if any(value == "" for value in data.values()):
        return render_template(
            "index.html",
            prediction_text="Verifique se todos os dados foram preenchidos.",
        )

    # transformação dos dados de entrada
    df = pd.DataFrame([data])

    df.loc[df.index, "Country"] = ord_country.transform(df[["Country"]])
    df.loc[df.index, "EdLevel"] = ord_ed_level.transform(df[["EdLevel"]])

    df_dummies = pd.get_dummies(df["DevType"].explode()).astype(int)
    df_grouped = df_dummies.groupby(df_dummies.index).sum()
    df = df.drop("DevType", axis=1).join(df_grouped)

    colunas_faltantes = set(columns) - set(df.columns)
    for col in colunas_faltantes:
        df[col] = 0

    df = df.reindex(columns=columns)
    df_scaled = scaler.transform(df)
    previsao = model.predict(df_scaled)

    return redirect(url_for("home", prediction_text=round(previsao[0], 2)))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
