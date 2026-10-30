from flask import Blueprint, request, render_template_string, session, make_response
import subprocess
import secrets

bp = Blueprint('main', __name__)

USERS = {
    1: {"id": 1, "username": "alice", "role": "user", "bio": "Alice's secret profile data.", "balance": 500},
    2: {"id": 2, "username": "bob", "role": "user", "bio": "Bob's private records.", "balance": 1000}
}

@bp.route('/')
def index():
    return '''
    <h1>CYC386 SecureApp Sprint Home</h1>
    <ul>
        <li><a href='/profile?id=1'>View Profile (IDOR Demo)</a></li>
        <li><a href='/ping'>Command Injection Demo</a></li>
        <li><a href='/transfer_form'>Fund Transfer (CSRF Demo)</a></li>
        <li><a href='/clickjacking'>Clickjacking Test Page</a></li>
    </ul>
    '''

# --- 1. IDOR Demo ---
@bp.route('/profile')
def profile():
    user_id = int(request.args.get('id', 1))
    user = USERS.get(user_id, {"username": "Unknown", "bio": "Not found"})
    return f"<h1>User Profile</h1><p>Username: <b>{user['username']}</b></p><p>Bio: {user['bio']}</p><br><a href='/'>Home</a>"

# --- 2. Command Injection Demo ---
@bp.route('/ping', methods=['GET', 'POST'])
def ping():
    output = ""
    if request.method == 'POST':
        target = request.form.get('target', '')
        try:
            output = subprocess.check_output(f"ping -c 1 {target}", shell=True, text=True, timeout=3)
        except Exception as e:
            output = f"Execution error: {str(e)}"
    return f'''
        <h2>Network Diagnostics Tool (Command Injection Demo)</h2>
        <form method="POST">
            <input type="text" name="target" placeholder="Enter IP or domain" style="width: 300px;">
            <input type="submit" value="Run Ping">
        </form>
        <pre>{output}</pre><br><a href='/'>Home</a>
    '''

# --- 3. CSRF Demo ---
@bp.route('/transfer_form', methods=['GET', 'POST'])
def transfer_form():
    msg = ""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
        
    if request.method == 'POST':
        # VULNERABLE if token is ignored. SECURE checks token:
        token = request.form.get('csrf_token')
        # if token != session.get('csrf_token'): return "CSRF Token Invalid!", 403
        amount = request.form.get('amount')
        recipient = request.form.get('recipient')
        msg = f"Successfully transferred ${amount} to {recipient}!"
        
    return f'''
        <h2>Fund Transfer (CSRF Demonstration)</h2>
        <form method="POST">
            <input type="hidden" name="csrf_token" value="{session.get('csrf_token')}">
            <label>Recipient:</label><br><input type="text" name="recipient"><br>
            <label>Amount ($):</label><br><input type="text" name="amount"><br><br>
            <input type="submit" value="Transfer Funds">
        </form>
        <p style="color: green;"><b>{msg}</b></p><br><a href='/'>Home</a>
    '''

# --- 4. Clickjacking Demo Page ---
@bp.route('/clickjacking')
def clickjacking():
    return '''
        <h2>Clickjacking Vulnerability Test Frame</h2>
        <p>This page is protected by X-Frame-Options: DENY and CSP frame-ancestors 'none'.</p>
        <iframe src="/ping" width="600" height="300"></iframe>
        <br><a href='/'>Home</a>
    '''
