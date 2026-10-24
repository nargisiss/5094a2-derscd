from datetime import datetime
from functools import wraps
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key-for-production")
DB_PATH = os.path.join(os.path.dirname(__file__), "events.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user','admin')),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category_id INTEGER NOT NULL REFERENCES categories(id),
        event_date TEXT NOT NULL,
        event_time TEXT NOT NULL,
        location TEXT NOT NULL,
        capacity INTEGER NOT NULL CHECK(capacity > 0),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
        registered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, event_id)
    );
    """)
    for category in ["Konfrans", "Seminar", "Təlim", "Müsabiqə", "Digər"]:
        db.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (category,))
    admin_email = "admin@university.az"
    existing = db.execute("SELECT id FROM users WHERE email=?", (admin_email,)).fetchone()
    if not existing:
        db.execute("INSERT INTO users(full_name,email,password_hash,role) VALUES(?,?,?,?)",
                   ("Administrator", admin_email, generate_password_hash("Admin123!"), "admin"))
    count = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    if count == 0:
        cats = {r[1]: r[0] for r in db.execute("SELECT id,name FROM categories").fetchall()}
        samples = [
            ("Süni intellekt üzrə tələbə konfransı", "Universitetdə süni intellektin tətbiqləri haqqında təqdimatlar və müzakirələr.", cats["Konfrans"], "2027-02-15", "10:00", "Əsas bina, zal 1", 100),
            ("Effektiv təqdimat bacarıqları", "Təqdimat və ictimai çıxış bacarıqlarını inkişaf etdirmək üçün praktiki seminar.", cats["Seminar"], "2027-03-10", "14:00", "Kitabxana, seminar otağı", 35),
            ("Python proqramlaşdırma təlimi", "Python dilinin əsasları və kiçik proqramların hazırlanması.", cats["Təlim"], "2027-04-05", "12:00", "Laboratoriya 204", 25),
        ]
        db.executemany("""INSERT INTO events(title,description,category_id,event_date,event_time,location,capacity)
                          VALUES(?,?,?,?,?,?,?)""", samples)
    db.commit()
    db.close()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Bu əməliyyat üçün əvvəlcə sistemə daxil olun.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Bu səhifəyə yalnız administrator daxil ola bilər.", "danger")
            return redirect(url_for("index"))
        return fn(*args, **kwargs)
    return wrapper

def event_registration_count(event_id):
    return get_db().execute("SELECT COUNT(*) FROM registrations WHERE event_id=?", (event_id,)).fetchone()[0]

@app.context_processor
def inject_globals():
    return {"current_user": session.get("full_name"), "current_role": session.get("role")}

@app.route("/")
def index():
    db = get_db()
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    location = request.args.get("location", "").strip()
    sql = """SELECT e.*, c.name AS category_name,
             (SELECT COUNT(*) FROM registrations r WHERE r.event_id=e.id) AS registered
             FROM events e JOIN categories c ON c.id=e.category_id WHERE 1=1"""
    params = []
    if q:
        sql += " AND e.title LIKE ?"
        params.append(f"%{q}%")
    if category_id.isdigit():
        sql += " AND e.category_id=?"
        params.append(int(category_id))
    if date_from:
        sql += " AND e.event_date>=?"
        params.append(date_from)
    if date_to:
        sql += " AND e.event_date<=?"
        params.append(date_to)
    if location:
        sql += " AND e.location LIKE ?"
        params.append(f"%{location}%")
    sql += " ORDER BY e.event_date, e.event_time"
    events = db.execute(sql, params).fetchall()
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    today = datetime.now().date().isoformat()
    return render_template("index.html", events=events, categories=categories, today=today,
                           filters={"q":q,"category":category_id,"date_from":date_from,"date_to":date_to,"location":location})

@app.route("/event/<int:event_id>")
def event_detail(event_id):
    db = get_db()
    event = db.execute("""SELECT e.*, c.name category_name,
        (SELECT COUNT(*) FROM registrations r WHERE r.event_id=e.id) registered
        FROM events e JOIN categories c ON c.id=e.category_id WHERE e.id=?""", (event_id,)).fetchone()
    if not event:
        flash("Tədbir tapılmadı.", "danger")
        return redirect(url_for("index"))
    registered = False
    if session.get("user_id"):
        registered = db.execute("SELECT id FROM registrations WHERE user_id=? AND event_id=?",
                                (session["user_id"], event_id)).fetchone() is not None
    return render_template("event_detail.html", event=event, registered=registered,
                           today=datetime.now().date().isoformat())

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or not password:
            flash("Bütün sahələri doldurun.", "danger")
            return render_template("register.html")
        if len(password) < 8:
            flash("Şifrə ən azı 8 simvol olmalıdır.", "danger")
            return render_template("register.html")
        db = get_db()
        try:
            db.execute("INSERT INTO users(full_name,email,password_hash) VALUES(?,?,?)",
                       (name, email, generate_password_hash(password)))
            db.commit()
        except sqlite3.IntegrityError:
            flash("Bu e-poçt ünvanı artıq qeydiyyatdan keçib.", "danger")
            return render_template("register.html")
        flash("Hesab yaradıldı. İndi sistemə daxil ola bilərsiniz.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            flash("Sistemə uğurla daxil oldunuz.", "success")
            return redirect(url_for("admin_dashboard" if user["role"] == "admin" else "index"))
        flash("E-poçt və ya şifrə yanlışdır.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sistemdən çıxış edildi.", "success")
    return redirect(url_for("index"))

@app.route("/event/<int:event_id>/join", methods=["POST"])
@login_required
def join_event(event_id):
    db = get_db()
    event = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not event:
        flash("Tədbir tapılmadı.", "danger")
        return redirect(url_for("index"))
    if event["event_date"] < datetime.now().date().isoformat():
        flash("Keçmiş tarixli tədbirə qeydiyyat mümkün deyil.", "warning")
        return redirect(url_for("event_detail", event_id=event_id))
    existing = db.execute("SELECT id FROM registrations WHERE user_id=? AND event_id=?",
                          (session["user_id"], event_id)).fetchone()
    if existing:
        flash("Bu tədbirə artıq qeydiyyatdan keçmisiniz.", "warning")
    elif event_registration_count(event_id) >= event["capacity"]:
        flash("Tədbir üçün bütün yerlər dolub.", "danger")
    else:
        try:
            db.execute("INSERT INTO registrations(user_id,event_id) VALUES(?,?)", (session["user_id"], event_id))
            db.commit()
            flash("Tədbirə qeydiyyatınız təsdiqləndi.", "success")
        except sqlite3.IntegrityError:
            db.rollback()
            flash("Təkrar qeydiyyata icazə verilmir.", "warning")
    return redirect(url_for("event_detail", event_id=event_id))

@app.route("/event/<int:event_id>/cancel", methods=["POST"])
@login_required
def cancel_registration(event_id):
    db = get_db()
    db.execute("DELETE FROM registrations WHERE user_id=? AND event_id=?", (session["user_id"], event_id))
    db.commit()
    flash("Qeydiyyat ləğv edildi (əgər qeydiyyat mövcud idisə).", "success")
    return redirect(url_for("event_detail", event_id=event_id))

@app.route("/my-registrations")
@login_required
def my_registrations():
    rows = get_db().execute("""SELECT e.*, c.name category_name, r.registered_at,
        (SELECT COUNT(*) FROM registrations rr WHERE rr.event_id=e.id) registered
        FROM registrations r JOIN events e ON e.id=r.event_id
        JOIN categories c ON c.id=e.category_id WHERE r.user_id=?
        ORDER BY e.event_date,e.event_time""", (session["user_id"],)).fetchall()
    return render_template("my_registrations.html", events=rows, today=datetime.now().date().isoformat())

@app.route("/admin")
@admin_required
def admin_dashboard():
    db = get_db()
    stats = {
        "events": db.execute("SELECT COUNT(*) FROM events").fetchone()[0],
        "registrations": db.execute("SELECT COUNT(*) FROM registrations").fetchone()[0],
        "users": db.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0],
        "categories": db.execute("SELECT COUNT(*) FROM categories").fetchone()[0],
    }
    popular = db.execute("""SELECT e.id,e.title,e.event_date,COUNT(r.id) AS total
        FROM events e LEFT JOIN registrations r ON r.event_id=e.id
        GROUP BY e.id ORDER BY total DESC,e.event_date LIMIT 5""").fetchall()
    by_category = db.execute("""SELECT c.name,COUNT(DISTINCT e.id) event_count,COUNT(r.id) registrations
        FROM categories c LEFT JOIN events e ON e.category_id=c.id
        LEFT JOIN registrations r ON r.event_id=e.id
        GROUP BY c.id ORDER BY event_count DESC,c.name""").fetchall()
    all_events = db.execute("""SELECT e.*,c.name category_name,
        (SELECT COUNT(*) FROM registrations r WHERE r.event_id=e.id) registered
        FROM events e JOIN categories c ON c.id=e.category_id
        ORDER BY e.event_date,e.event_time""").fetchall()
    return render_template("admin.html", stats=stats, popular=popular, by_category=by_category, all_events=all_events)

@app.route("/admin/events/new", methods=["GET", "POST"])
@admin_required
def create_event():
    db = get_db()
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    if request.method == "POST":
        data = get_event_form()
        error = validate_event(data)
        if error:
            flash(error, "danger")
            return render_template("event_form.html", event=data, categories=categories, page_title="Yeni tədbir")
        db.execute("""INSERT INTO events(title,description,category_id,event_date,event_time,location,capacity)
                      VALUES(?,?,?,?,?,?,?)""",
                   (data["title"],data["description"],int(data["category_id"]),data["event_date"],
                    data["event_time"],data["location"],int(data["capacity"])))
        db.commit()
        flash("Tədbir yaradıldı.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("event_form.html", event={}, categories=categories, page_title="Yeni tədbir")

def get_event_form():
    return {key: request.form.get(key, "").strip() for key in
            ["title","description","category_id","event_date","event_time","location","capacity"]}

def validate_event(data):
    required = ["title","description","category_id","event_date","event_time","location","capacity"]
    if any(not data[k] for k in required):
        return "Bütün sahələr məcburidir."
    try:
        datetime.strptime(data["event_date"], "%Y-%m-%d")
        datetime.strptime(data["event_time"], "%H:%M")
        capacity = int(data["capacity"])
        category_id = int(data["category_id"])
        if capacity < 1:
            return "İştirakçı limiti ən azı 1 olmalıdır."
        if not get_db().execute("SELECT id FROM categories WHERE id=?", (category_id,)).fetchone():
            return "Düzgün kateqoriya seçin."
    except ValueError:
        return "Tarix, saat, kateqoriya və limit düzgün formatda olmalıdır."
    return None

@app.route("/admin/events/<int:event_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_event(event_id):
    db = get_db()
    event = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not event:
        flash("Tədbir tapılmadı.", "danger")
        return redirect(url_for("admin_dashboard"))
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    if request.method == "POST":
        data = get_event_form()
        error = validate_event(data)
        count = event_registration_count(event_id)
        if not error and int(data["capacity"]) < count:
            error = f"Limit qeydiyyatda olan iştirakçı sayından ({count}) az ola bilməz."
        if error:
            flash(error, "danger")
            return render_template("event_form.html", event=data, categories=categories, page_title="Tədbiri redaktə et", event_id=event_id)
        db.execute("""UPDATE events SET title=?,description=?,category_id=?,event_date=?,event_time=?,location=?,capacity=?
                      WHERE id=?""",
                   (data["title"],data["description"],int(data["category_id"]),data["event_date"],
                    data["event_time"],data["location"],int(data["capacity"]),event_id))
        db.commit()
        flash("Tədbir yeniləndi.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("event_form.html", event=event, categories=categories, page_title="Tədbiri redaktə et", event_id=event_id)

@app.route("/admin/events/<int:event_id>/delete", methods=["POST"])
@admin_required
def delete_event(event_id):
    db = get_db()
    db.execute("DELETE FROM events WHERE id=?", (event_id,))
    db.commit()
    flash("Tədbir və ona bağlı qeydiyyatlar silindi.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/events/<int:event_id>/participants")
@admin_required
def participants(event_id):
    db = get_db()
    event = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not event:
        flash("Tədbir tapılmadı.", "danger")
        return redirect(url_for("admin_dashboard"))
    people = db.execute("""SELECT u.full_name,u.email,r.registered_at FROM registrations r
        JOIN users u ON u.id=r.user_id WHERE r.event_id=? ORDER BY u.full_name""", (event_id,)).fetchall()
    return render_template("participants.html", event=event, people=people)

@app.route("/admin/events/<int:event_id>/export")
@admin_required
def export_participants(event_id):
    import csv
    from io import StringIO
    from flask import make_response
    db = get_db()
    event = db.execute("SELECT title FROM events WHERE id=?", (event_id,)).fetchone()
    if not event:
        flash("Tədbir tapılmadı.", "danger")
        return redirect(url_for("admin_dashboard"))
    people = db.execute("""SELECT u.full_name,u.email,r.registered_at FROM registrations r
        JOIN users u ON u.id=r.user_id WHERE r.event_id=? ORDER BY u.full_name""", (event_id,)).fetchall()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Ad soyad", "E-poçt", "Qeydiyyat tarixi"])
    for person in people:
        writer.writerow([person["full_name"], person["email"], person["registered_at"]])
    response = make_response("\\ufeff" + output.getvalue())
    response.headers["Content-Disposition"] = f'attachment; filename="event_{event_id}_participants.csv"'
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response

@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(_error):
    return render_template("500.html"), 500

init_db()

if __name__ == "__main__":
    app.run(debug=True)
