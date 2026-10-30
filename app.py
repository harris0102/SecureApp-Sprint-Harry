from flask import Flask
from app.routes import bp

app = Flask(__name__)
app.secret_key = "cyc386_secure_sprint_secret"

app.register_blueprint(bp)

@app.after_request
def apply_security_headers(response):
    # Remediation for Clickjacking: Blocks framing entirely
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'none'"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
