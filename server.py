#!/usr/bin/env python

from flask import Flask, send_file, jsonify
from datetime import datetime, timedelta

from slurm import *

test=False

if len(sys.argv)>1 and sys.argv[1]=='-d':
    test=True

conf = SlurmConfig(test)
log("Read config {} settings".format(len(conf.data)))

share = ShareInfo(test)

queue = Queue(test)

app = Flask(__name__)

@app.route('/api/slurm/config')
def send_config():
    return jsonify({"data": conf.data, "updated": conf.updated.isoformat()})

@app.route('/api/slurm/sshare')
def send_sshare():
    if not share.updated or datetime.now()-share.updated>timedelta(minutes=30):
        share.read_info()
        log("Read sshare {} lines".format(len(share.data)))

    return jsonify({"data": share.data, "updated": conf.updated.isoformat()})

@app.route('/api/slurm/queue')
def send_queue():
    if not queue.updated or datetime.now()-queue.updated>timedelta(minutes=5):
        queue.read()
        log("Read queue {} lines".format(len(queue.data)))

    return jsonify({"data": queue.data, "updated": conf.updated.isoformat()})

@app.route('/', defaults={'file': 'index.html'})
@app.route('/<path:file>')
def index(file):
    return send_file('app/dist/'+file)

if __name__ == '__main__':
#    app.run(debug=test, host='0.0.0.0')
    app.run(debug=test, host='localhost')
