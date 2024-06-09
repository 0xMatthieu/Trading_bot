from flask import Flask, request, abort
import subprocess
import os

app = Flask(__name__)

def is_process_running(process_name):
    """Check if there is any running process that contains the given name."""
    try:
        subprocess.check_output(['pgrep', '-f', process_name])
        return True
    except subprocess.CalledProcessError:
        return False

def start_processes():
    """Start streamlit and Trading_main.py if they are not running."""
    repo_dir = os.path.dirname(os.path.realpath(__file__))

    if not is_process_running('streamlit'):
        streamlit_command = ['python3.8', '-m', 'streamlit', 'run', 'streamlit_app.py']
        subprocess.Popen(streamlit_command, cwd=repo_dir)

    if not is_process_running('Trading_main.py'):
        main_threading_command = ['python3.8', 'Trading_main.py']
        subprocess.Popen(main_threading_command, cwd=repo_dir)

@app.route('/github-webhook/', methods=['POST'])
def github_webhook():
    if request.method == 'POST':
        if request.headers['Content-Type'] == 'application/json':
            payload = request.json
            if payload.get('ref') == 'refs/heads/main':
                # Define the repo directory
                repo_dir = os.path.dirname(os.path.realpath(__file__))
                
                # Pull the latest changes
                subprocess.call(['git', 'reset', '--hard', 'HEAD'], cwd=repo_dir)
                subprocess.call(['git', 'pull'], cwd=repo_dir)
                
                # Restart the streamlit app
                subprocess.call(['pkill', '-f', 'streamlit'])
                subprocess.Popen(['python3.8', '-m', 'streamlit', 'run', 'streamlit_app.py'], cwd=repo_dir)
                
                # Restart the main_threading.py
                subprocess.call(['pkill', '-f', 'Trading_main.py'])
                subprocess.Popen(['python3.8', 'Trading_main.py'], cwd=repo_dir)
                
                return 'Success', 200
            return 'Branch not main', 200
        else:
            abort(400)
    else:
        abort(400)

if __name__ == '__main__':
    start_processes()
    app.run(host='0.0.0.0', port=8701)
