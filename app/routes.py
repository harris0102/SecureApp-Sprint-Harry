from flask import Blueprint, request, render_template_string
import subprocess

bp = Blueprint('main', __name__)

# Mock database simulating user profiles for IDOR demonstration
USERS = {
    1: {"id": 1, "username": "alice", "role": "user", "bio": "Alice's secret profile data."},
    2: {"id": 2, "username": "bob", "role": "user", "bio": "Bob's private financial records."}
}

@bp.route('/')
def index():
    return "<h1>CYC386 SecureApp Sprint Home</h1><ul><li><a href='/profile?id=1'>View Profile (IDOR Demo)</a></li><li><a href='/ping'>Command Injection Demo</a></li></ul>"

# --- VULNERABILITY 1: IDOR (Insecure Direct Object Reference) ---
@bp.route('/profile')
def profile():
    # VULNERABLE CODE: Directly accepts user ID without checking session ownership
    # FIX: Ensure session_user_id == user_id before serving records
    user_id = int(request.args.get('id', 1))
    user = USERS.get(user_id, {"username": "Unknown", "bio": "Not found"})
    return f"<h1>User Profile</h1><p>Username: <b>{user['username']}</b></p><p>Bio: {user['bio']}</p>"

# --- VULNERABILITY 2: Command Injection ---
@bp.route('/ping', methods=['GET', 'POST'])
def ping():
    output = ""
    if request.method == 'POST':
        target = request.form.get('target', '')
        # VULNERABLE CODE: Passes raw input directly to shell
        # FIX: Use subprocess.run(["ping", "-c", "1", target], capture_output=True, text=True) without shell=True
        try:
            output = subprocess.check_output(f"ping -c 1 {target}", shell=True, text=True, timeout=3)
        except Exception as e:
            output = f"Execution error or timeout: {str(e)}"
            
    return f'''
        <h2>Network Diagnostics Tool (Command Injection Demo)</h2>
        <form method="POST">
            <input type="text" name="target" placeholder="Enter IP or domain" style="width: 300px;">
            <input type="submit" value="Run Ping">
        </form>
        <pre>{output}</pre>
    '''
