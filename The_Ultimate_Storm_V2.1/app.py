from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def Home():
    Game_State = {"Round": 1, "Ocean ACE": 2500}

    return (render_template("index.html", Game_State=Game_State))


if __name__ == "__main__":
    app.run(debug=True)