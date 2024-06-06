from flask import Flask, request, abort
import subprocess
import os

app = Flask(__name__)

@app.route('/github-webhook/', methods=['POST'])
def github_webhook():
    if request.method == 'POST':
        if request.headers['Content-Type'] == 'application/json':
            payload = request.json
            if payload.get('ref') == 'refs/heads/main':
                # Pull the latest changes
                subprocess.call(['git', 'pull'], cwd=os.path.dirname(os.path.realpath(__file__)))
                # Restart the streamlit app and main_threading.py
                subprocess.call(['pkill', '-f', 'streamlit'])
                subprocess.call(['streamlit', 'run', 'streamlit_app.py'])
                subprocess.call(['pkill', '-f', 'main_threading.py'])
                subprocess.Popen(['python3', 'main_threading.py'])
                return 'Success', 200
            return 'Branch not main', 200
        else:
            abort(400)
    else:
        abort(400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=your_port)
