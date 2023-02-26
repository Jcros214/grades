from flask import Flask, render_template, request
# from flask import Blueprint

# app = Blueprint('grades', __name__, template_folder='/home/jcros792/mysite/grades/templates')
app = Flask(__name__)

from Sycamore import User

class Creds:
    def __init__(self, username, password):
        self.username = username
        self.password = password

form = """\
<form method="post">
    <input type="text" name="username" placeholder="Username" autofocus="">
    <input type="text" name="password" placeholder="Password" autofocus="">
    <input type="submit" value="Submit">
</form>"""


import threading
import queue

# Define a custom exception to handle errors in the worker thread
class WorkerException(Exception):
    pass

class PlotWorker(threading.Thread):
    def __init__(self, user, queue):
        super().__init__()
        self.user = user
        self.queue = queue

    def run(self):
        try:
            plot = self.user.showPlot(60)
            self.queue.put(plot)
        except Exception as e:
            # Raise a custom exception to propagate the error to the main thread
            raise WorkerException(str(e))

@app.route('/', methods=['GET', 'POST'])
def grades():
    if request.method == "POST":
        if 'username' in request.form and 'password' in request.form:
            import subprocess
            subprocess.Popen(["python", "Sycamore.py", request.form.get('username'), request.form.get('password')])

            import time
            time.sleep(5)

            with open('plot.png', 'r') as f:
                plot = f.read()

            return render_template('base.html', plot=plot)
        else:
            return "You forgot to specify credentials." + form
    else:
        return form


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
