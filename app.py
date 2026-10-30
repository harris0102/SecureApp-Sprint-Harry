"""
CYC386 SecureApp Sprint - single-file Flask application.
Every mandatory vulnerability class has BOTH a vulnerable and a secure path.
VULN_MODE selects which runs, so 'before' and 'after' evidence come from one app.
    VULN_MODE=1 python3 app.py   -> vulnerable (lab demo only)
    python3 app.py               -> secure (default)
"""
import os
import re
import secrets
import subprocess
from flask import Flask, request, session, redirect, abort, render_template_string
from markupsafe import escape

VULN_MODE = os.environ.get("VULN_MODE") == "1"
MODE_LABEL = "VULNERABLE (lab demo)" if VULN_MODE else "SECURE (hardened)"

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax" if VULN_MODE else "Strict",
)

USERS = {
    "alice": {"id": 1, "password": "alicepw", "bio": "Alice CONFIDENTIAL: card ending 4417"},
    "bob":   {"id": 2, "password": "bobpw",   "bio": "Bob CONFIDENTIAL: card ending 9921"},
}
BY_ID = {u["id"]: dict(username=n, **u) for n, u in USERS.items()}

PAGE = """<!doctype html><title>SecureApp Sprint</title>
<div style="font-family:system-ui,sans-serif;max-width:780px;margin:24px auto">
<p style="padding:6px 10px;border-radius:6px;background:{{ '#fde2e2' if vuln else '#e3f7e6' }}">
  <b>Mode:</b> {{ mode }}
  {% if user %}&nbsp;|&nbsp;logged in as <b>{{ user }}</b> (<a href="/logout">logout</a>)
  {% else %}&nbsp;|&nbsp;<a href="/login">login</a>{% endif %}
</p>
{{ body|safe }}
<hr><a href="/">Home</a>
</div>"""


def current_user():
    uid = session.get("user_id")
    return BY_ID[uid]["username"] if uid in BY_ID else None


def render(body):
    return render_template_string(PAGE, body=body, mode=MODE_LABEL,
                                  vuln=VULN_MODE, user=current_user())


@app.after_request
def security_headers(resp):
    if not VULN_MODE:
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
    return resp


@app.route("/")
def index():
    return render("""<h1>CYC386 SecureApp Sprint</h1>
    <ul>
      <li><a href="/profile?id=1">Profile (IDOR demo)</a></li>
      <li><a href="/ping">Ping tool (Command Injection demo)</a></li>
      <li><a href="/transfer">Fund transfer (CSRF demo)</a></li>
      <li><a href="/clickjacking">Clickjacking test page</a></li>
    </ul>""")


LOGIN_FORM = """<h2>Login</h2><form method="post">
username <input name="username" value="alice"><br>
password <input name="password" type="password" value="alicepw"><br>
<button>Login</button></form><p>Users: alice/alicepw &nbsp; bob/bobpw</p>"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = USERS.get(request.form.get("username", ""))
        if u and request.form.get("password") == u["password"]:
            session["user_id"] = u["id"]
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        return render("<p style='color:red'>Invalid credentials</p>" + LOGIN_FORM)
    return render(LOGIN_FORM)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# --- 1. IDOR (CWE-639) ---
@app.route("/profile")
def profile():
    rid = int(request.args.get("id", 1))
    if VULN_MODE:
        user = BY_ID.get(rid)                         # no ownership check -> IDOR
    else:
        if "user_id" not in session:
            return redirect("/login")
        if rid != session["user_id"]:                 # object-level authorization
            abort(403)
        user = BY_ID.get(rid)
    if not user:
        abort(404)
    return render(f"<h2>Profile #{user['id']}</h2>"
                  f"<p>User: <b>{escape(user['username'])}</b></p>"
                  f"<p>Bio: {escape(user['bio'])}</p>")


# --- 2. Command Injection (CWE-78) ---
HOST_RE = re.compile(r"^[A-Za-z0-9.\-]{1,64}$")


@app.route("/ping", methods=["GET", "POST"])
def ping():
    out = ""
    if request.method == "POST":
        target = request.form.get("target", "")
        if VULN_MODE:
            try:
                out = subprocess.check_output(f"ping -c 1 {target}", shell=True,  # nosec B602 - intentional lab-only injectable path
                                              text=True, timeout=4)
            except Exception as e:
                out = str(e)
        else:
            if not HOST_RE.match(target):
                out = "Rejected: only letters, digits, '.' and '-' are allowed."
            else:
                r = subprocess.run(["ping", "-c", "1", target],
                                   capture_output=True, text=True, timeout=4)
                out = r.stdout or r.stderr
    body = ("<h2>Network Diagnostics (ping)</h2>"
            "<form method='post'><input name='target' placeholder='IP or domain' size='40'>"
            " <button>Run</button></form>"
            f"<pre>{escape(out)}</pre>")
    return render(body)


# --- 3. CSRF (CWE-352) ---
@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if "user_id" not in session:
        return redirect("/login")
    msg = ""
    if request.method == "POST":
        if not VULN_MODE:
            if request.form.get("csrf_token") != session.get("csrf_token"):
                abort(403)
        amt = escape(request.form.get("amount", "0"))
        rcpt = escape(request.form.get("recipient", "?"))
        msg = f"<p style='color:green'>Transferred ${amt} to {rcpt}.</p>"
    token = session.get("csrf_token", "")
    hidden = "" if VULN_MODE else f"<input type='hidden' name='csrf_token' value='{token}'>"
    body = (f"<h2>Fund Transfer</h2>{msg}<form method='post'>{hidden}"
            "recipient <input name='recipient'><br>amount <input name='amount'><br>"
            "<button>Transfer</button></form>")
    return render(body)


# --- 4. Clickjacking (CWE-1021) ---
@app.route("/clickjacking")
def clickjacking():
    body = ("<h2>Clickjacking test</h2>"
            "<p>This iframe tries to embed the transfer page. SECURE mode blocks it "
            "(X-Frame-Options: DENY); VULNERABLE mode lets it load.</p>"
            "<iframe src='/transfer' width='600' height='220'></iframe>")
    return render(body)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
