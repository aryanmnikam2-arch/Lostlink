from flask import Flask, render_template, request, redirect, url_for, session
from database import init_db, get_db

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        item_type = request.form["item_type"]
        name = request.form["name"]
        category = request.form["category"]
        location = request.form["location"]
        date = request.form["date"]
        description = request.form["description"]

        db = get_db()
        db.execute(
            """INSERT INTO items
               (item_type, name, category, location, date, description, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (item_type, name, category, location, date, description, "ACTIVE")
        )
        db.commit()
        db.close()
        return redirect(url_for("search"))

    return render_template("report.html")

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    db = get_db()

    if q:
        items = db.execute(
            """SELECT * FROM items
               WHERE name LIKE ? OR category LIKE ?
                  OR location LIKE ? OR description LIKE ?
               ORDER BY id DESC""",
            (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%")
        ).fetchall()
    else:
        items = db.execute("SELECT * FROM items ORDER BY id DESC").fetchall()

    db.close()
    return render_template("search.html", items=items, q=q)

if __name__ == "__main__":
    app.run(debug=True)
