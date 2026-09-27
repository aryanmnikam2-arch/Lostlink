"""
app.py  –  VIT Bhopal Lost & Found System
Main Flask application entry point.
"""

import os
import sqlite3
import random
import hashlib
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

import json
import urllib.request
import urllib.error

# pyrefly: ignore [missing-import]
from flask import (
    Flask, render_template, request, session,
    redirect, url_for, flash, jsonify
)
# pyrefly: ignore [missing-import]
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# ── Bootstrap ─────────────────────────────────────────────────────────────────
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "vit-bhopal-lf-secret-2024")

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
DB_PATH        = os.path.join(BASE_DIR, "lost_found.db")
UPLOAD_DIR     = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_DOMAIN     = os.getenv("ALLOWED_DOMAIN", "vitbhopal.ac.in")
GEMINI_KEY         = os.getenv("GEMINI_API_KEY", "")
SMTP_HOST          = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT          = int(os.getenv("SMTP_PORT", 587))
SMTP_USER          = os.getenv("SMTP_USER", "")
SMTP_PASS          = os.getenv("SMTP_PASS", "")
MAX_UPLOAD_MB      = int(os.getenv("MAX_UPLOAD_MB", 5))
DEV_BYPASS_LOGIN   = os.getenv("DEV_BYPASS_LOGIN", "false").lower() == "true"
DEV_USER_EMAIL     = os.getenv("DEV_USER_EMAIL", "devtest@vitbhopal.ac.in")
OTP_EXPIRY_SEC = 600   # 10 minutes

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)

GEMINI_REST_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent?key={key}"
)



# ── Database helpers ──────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query_db(sql, args=(), one=False):
    conn = get_db()
    cur  = conn.execute(sql, args)
    rv   = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(sql, args=()):
    conn = get_db()
    cur  = conn.execute(sql, args)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


# ── Auth helpers ──────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


# ── Email helper ──────────────────────────────────────────────────────────────
def send_otp_email(to_email: str, otp: str) -> bool:
    """Send OTP via SMTP. Returns True on success."""
    if not SMTP_USER or not SMTP_PASS:
        # Dev mode: print OTP to console
        print(f"\n[DEV MODE] OTP for {to_email}  ->  {otp}\n")
        return True
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Your VIT Bhopal Lost & Found – Verification Code"
        msg["From"]    = SMTP_USER
        msg["To"]      = to_email

        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;
                    border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;">
          <div style="background:#1a237e;padding:20px;text-align:center;">
            <h2 style="color:#f9a825;margin:0;">VIT Bhopal</h2>
            <p style="color:#fff;margin:4px 0 0;">Lost &amp; Found Portal</p>
          </div>
          <div style="padding:32px;">
            <p style="color:#333;">Your one-time verification code is:</p>
            <div style="font-size:40px;font-weight:700;letter-spacing:8px;
                        color:#1a237e;text-align:center;padding:16px 0;">{otp}</div>
            <p style="color:#666;font-size:13px;">
              This code expires in <strong>10 minutes</strong>.<br>
              Do not share it with anyone.
            </p>
          </div>
        </div>
        """
        msg.attach(MIMEText(html, "html"))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[SMTP ERROR] {e}")
        return False


# ── Gemini AI matcher ─────────────────────────────────────────────────────────
def get_ai_matches(lost_name: str, lost_desc: str) -> list:
    """
    Query Gemini 2.5 Flash via REST to find probable found-item matches.
    Returns a list of dicts: [{id, item_name, reason}, ...]
    """
    if not GEMINI_KEY:
        return []

    found_items = query_db(
        "SELECT id, item_name, description, location_found FROM found_items "
        "WHERE status='UNCLAIMED' ORDER BY created_at DESC LIMIT 50"
    )
    if not found_items:
        return []

    items_text = "\n".join(
        f"ID:{row['id']} | Name:{row['item_name']} | Desc:{row['description']} | Location:{row['location_found']}"
        for row in found_items
    )

    prompt = (
        "You are a lost-and-found assistant for VIT Bhopal University campus.\n\n"
        f"A student has reported a LOST item:\n  Name: {lost_name}\n  Description: {lost_desc}\n\n"
        f"Here are the currently FOUND (unclaimed) items on campus:\n{items_text}\n\n"
        "Identify up to 3 found items that most likely match the lost item.\n"
        "Reply ONLY in this exact JSON format (no markdown fences, no extra text):\n"
        '[\n  {"id": <integer_id>, "item_name": "<name>", "reason": "<one-sentence explanation>"},\n  ...\n]\n'
        "If there are no matches, return an empty JSON array: []"
    )

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")

    url = GEMINI_REST_URL.format(key=GEMINI_KEY)
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text = body["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        matches = json.loads(text)
        return matches if isinstance(matches, list) else []
    except Exception as e:
        print(f"[GEMINI ERROR] {e}")
        return []


def get_lost_matches(found_name: str, found_desc: str) -> list:
    """
    Reverse matcher: given a FOUND item, query Gemini to find
    open LOST item reports that likely describe this item.
    Returns [{id, item_name, contact_details, reason}, ...]
    """
    if not GEMINI_KEY:
        return []

    lost_items = query_db(
        "SELECT id, item_name, description, contact_details "
        "FROM lost_items WHERE status='OPEN' ORDER BY created_at DESC LIMIT 50"
    )
    if not lost_items:
        return []

    items_text = "\n".join(
        f"ID:{row['id']} | Name:{row['item_name']} | Desc:{row['description']}"
        for row in lost_items
    )

    prompt = (
        "You are a lost-and-found assistant for VIT Bhopal University campus.\n\n"
        f"Someone just FOUND an item:\n  Name: {found_name}\n  Description: {found_desc}\n\n"
        f"Here are open LOST item reports on campus:\n{items_text}\n\n"
        "Identify up to 3 lost reports that most likely describe this found item.\n"
        "Reply ONLY in this exact JSON format (no markdown fences, no extra text):\n"
        '[\n  {"id": <integer_id>, "item_name": "<name>", "reason": "<one-sentence explanation>"},\n  ...\n]\n'
        "If there are no matches, return an empty JSON array: []"
    )

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")

    url = GEMINI_REST_URL.format(key=GEMINI_KEY)
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text = body["candidates"][0]["content"]["parts"][0]["text"].strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        matches = json.loads(text)
        # Attach contact details from DB so template can show them
        if isinstance(matches, list):
            lost_map = {row["id"]: row for row in lost_items}
            for m in matches:
                row = lost_map.get(m.get("id"))
                m["contact_details"] = row["contact_details"] if row else ""
                m["db_row"] = dict(row) if row else {}
        return matches if isinstance(matches, list) else []
    except Exception as e:
        print(f"[GEMINI ERROR - lost_match] {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    # Dev bypass: skip straight to dashboard
    if DEV_BYPASS_LOGIN:
        return redirect(url_for("dev_login"))
    return redirect(url_for("login"))


# ── Dev auto-login (bypass) ───────────────────────────────────────────────────
@app.route("/_dev_login")
def dev_login():
    """Instant login for development — only works when DEV_BYPASS_LOGIN=true."""
    if not DEV_BYPASS_LOGIN:
        return redirect(url_for("login"))
    user = query_db("SELECT id FROM users WHERE email=?", (DEV_USER_EMAIL,), one=True)
    if user:
        uid = user["id"]
    else:
        uid = execute_db("INSERT INTO users (email) VALUES (?)", (DEV_USER_EMAIL,))
    session["user_id"] = uid
    session["email"]   = DEV_USER_EMAIL
    print(f"[DEV] Bypassed login as {DEV_USER_EMAIL}")
    return redirect(url_for("dashboard"))


# ── Login ─────────────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    # Dev bypass — skip the whole login page
    if DEV_BYPASS_LOGIN:
        return redirect(url_for("dev_login"))
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        # Domain validation
        if not email.endswith(f"@{ALLOWED_DOMAIN}"):
            flash(f"Only @{ALLOWED_DOMAIN} email addresses are allowed.", "error")
            return render_template("login.html", allowed_domain=ALLOWED_DOMAIN)

        # Generate OTP
        otp      = str(random.randint(100000, 999999))
        otp_hash = hash_otp(otp)
        otp_ts   = time.time()

        ok = send_otp_email(email, otp)
        if not ok:
            flash("Failed to send OTP. Please try again.", "error")
            return render_template("login.html", allowed_domain=ALLOWED_DOMAIN)

        # Save in session temporarily
        session["pending_email"] = email
        session["otp_hash"]      = otp_hash
        session["otp_ts"]        = otp_ts

        flash("A 6-digit code has been sent to your email.", "info")
        return redirect(url_for("verify_otp"))

    return render_template("login.html", allowed_domain=ALLOWED_DOMAIN)


# ── OTP Verification ──────────────────────────────────────────────────────────
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "pending_email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()
        otp_hash    = session.get("otp_hash", "")
        otp_ts      = session.get("otp_ts", 0)
        email       = session.get("pending_email", "")

        # Check expiry
        if time.time() - otp_ts > OTP_EXPIRY_SEC:
            session.pop("otp_hash", None)
            session.pop("otp_ts", None)
            session.pop("pending_email", None)
            flash("OTP expired. Please request a new one.", "error")
            return redirect(url_for("login"))

        # Check correctness
        if hash_otp(entered_otp) != otp_hash:
            flash("Incorrect code. Please try again.", "error")
            return render_template("verify_otp.html", email=email)

        # Upsert user
        user = query_db("SELECT id FROM users WHERE email=?", (email,), one=True)
        if user:
            user_id = user["id"]
        else:
            user_id = execute_db("INSERT INTO users (email) VALUES (?)", (email,))

        # Clear OTP state, set auth session
        session.pop("otp_hash", None)
        session.pop("otp_ts", None)
        session.pop("pending_email", None)
        session["user_id"] = user_id
        session["email"]   = email

        flash("Logged in successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("verify_otp.html", email=session.get("pending_email", ""))


# ── Resend OTP ────────────────────────────────────────────────────────────────
@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    email = session.get("pending_email")
    if not email:
        return redirect(url_for("login"))

    otp      = str(random.randint(100000, 999999))
    otp_hash = hash_otp(otp)
    otp_ts   = time.time()

    ok = send_otp_email(email, otp)
    if ok:
        session["otp_hash"] = otp_hash
        session["otp_ts"]   = otp_ts
        flash("A new code has been sent to your email.", "info")
    else:
        flash("Could not resend OTP. Try again.", "error")

    return redirect(url_for("verify_otp"))


# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    email = session.get("email", "")
    return render_template("dashboard.html", email=email)


# ── Found Item Form ───────────────────────────────────────────────────────────
@app.route("/found/new", methods=["GET", "POST"])
@login_required
def found_new():
    if request.method == "POST":
        item_name   = request.form.get("item_name", "").strip()
        description = request.form.get("description", "").strip()
        location    = request.form.get("location_found", "").strip()
        time_found  = request.form.get("time_found", "").strip()
        contact     = request.form.get("contact_details", "").strip()

        errors = []
        if not item_name:   errors.append("Item name is required.")
        if not description: errors.append("Description is required.")
        if not location:    errors.append("Location found is required.")
        if not time_found:  errors.append("Time found is required.")
        if not contact:     errors.append("Contact details are required.")

        # Mandatory image
        file = request.files.get("image")
        if not file or not file.filename:
            errors.append("An image of the found item is required.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("found_form.html", form_data=request.form)

        if not allowed_file(file.filename):
            flash("Invalid image type. Allowed: png, jpg, jpeg, gif, webp", "error")
            return render_template("found_form.html", form_data=request.form)

        filename  = secure_filename(f"found_{int(time.time())}_{file.filename}")
        save_path = os.path.join(UPLOAD_DIR, filename)
        file.save(save_path)
        image_path = f"uploads/{filename}"

        execute_db(
            """INSERT INTO found_items
               (user_id, item_name, description, location_found,
                time_found, contact_details, image_path)
               VALUES (?,?,?,?,?,?,?)""",
            (session["user_id"], item_name, description,
             location, time_found, contact, image_path)
        )

        # Run reverse AI matching against open lost reports
        lost_matches  = get_lost_matches(item_name, description)
        session["lost_matches"]     = lost_matches
        session["lost_found_name"]  = item_name

        flash(f'Found item "{item_name}" registered successfully!', "success")
        return redirect(url_for("catalog"))

    return render_template("found_form.html", form_data={})


# ── Catalog ───────────────────────────────────────────────────────────────────
@app.route("/catalog")
@login_required
def catalog():
    q = request.args.get("q", "").strip()

    if q:
        found_items = query_db(
            """SELECT * FROM found_items
               WHERE item_name LIKE ? OR description LIKE ?
               ORDER BY created_at DESC""",
            (f"%{q}%", f"%{q}%")
        )
    else:
        found_items = query_db(
            "SELECT * FROM found_items ORDER BY created_at DESC"
        )

    # Pull AI matches from session (set after lost form submission)
    ai_matches   = session.pop("ai_matches", [])
    ai_lost_name = session.pop("ai_lost_name", "")

    # Pull reverse matches (set after found form submission)
    lost_matches      = session.pop("lost_matches", [])
    lost_found_name   = session.pop("lost_found_name", "")

    # Attach full found-item rows to AI match dicts
    if ai_matches:
        match_ids   = {m["id"] for m in ai_matches}
        ai_item_map = {row["id"]: row for row in found_items if row["id"] in match_ids}
        for m in ai_matches:
            m["item_row"] = ai_item_map.get(m["id"])

    return render_template(
        "catalog.html",
        found_items      = found_items,
        ai_matches       = ai_matches,
        ai_lost_name     = ai_lost_name,
        lost_matches     = lost_matches,
        lost_found_name  = lost_found_name,
        query            = q
    )


# ── Reveal Contact (AJAX) ─────────────────────────────────────────────────────
@app.route("/reveal-contact/<int:item_id>")
@login_required
def reveal_contact(item_id):
    row = query_db(
        "SELECT contact_details, item_name FROM found_items WHERE id=?",
        (item_id,), one=True
    )
    if not row:
        return jsonify({"error": "Item not found"}), 404
    return jsonify({
        "contact":   row["contact_details"],
        "item_name": row["item_name"]
    })


# ── Mark as Claimed ───────────────────────────────────────────────────────────
@app.route("/claim/<int:item_id>", methods=["POST"])
@login_required
def claim_item(item_id):
    execute_db(
        "UPDATE found_items SET status='CLAIMED' WHERE id=?", (item_id,)
    )
    return jsonify({"status": "CLAIMED"})


# ── Logout ────────────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ── Error handlers ────────────────────────────────────────────────────────────
@app.errorhandler(413)
def too_large(e):
    flash(f"File too large. Maximum size is {MAX_UPLOAD_MB} MB.", "error")
    return redirect(request.referrer or url_for("dashboard"))


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Auto-initialise DB if missing
    if not os.path.exists(DB_PATH):
        from init_db import init
        init()
    app.run(debug=os.getenv("FLASK_DEBUG", "True") == "True", port=5000)
