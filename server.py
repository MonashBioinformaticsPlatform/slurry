#!/usr/bin/env python

import argparse

from flask import Flask, send_file, jsonify, abort
from datetime import datetime, timedelta

from slurm import *

parser = argparse.ArgumentParser(
    description='Webserver for Slurry visualisation of slurm queue',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-d', '--debug', action="store_true",
    help='Run in debug mode.  Uses test-data/ instead of the slurm commands')
parser.add_argument('-a', '--addr', default='0.0.0.0',
    help='Host to listen on')
parser.add_argument('-p', '--port', default=5000,
    help='Port to listen on')

args = parser.parse_args()

conf = SlurmConfig(args.debug)
log("Read config {} settings".format(len(conf.data)))

share = ShareInfo(args.debug)

queue = Queue(args.debug)

app = Flask(__name__)

@app.route('/api/slurm/config')
def send_config():
    return jsonify({"data": conf.data, "updated": conf.updated.isoformat()})

@app.route('/api/slurm/sshare')
def send_sshare():
    if not share.updated or datetime.now()-share.updated>timedelta(minutes=30):
        share.read_info()
        log("Read sshare {} lines".format(len(share.data)))

    return jsonify({"data": share.data, "updated": share.updated.isoformat()})

@app.route('/api/slurm/queue')
def send_queue():
    if not queue.updated or datetime.now()-queue.updated>timedelta(minutes=5):
        queue.read()
        log("Read queue {} lines".format(len(queue.data)))

    return jsonify({"data": queue.data, "updated": queue.updated.isoformat()})

@app.route('/', defaults={'file': 'index.html'})
@app.route('/<path:file>')
def index(file):
    if '..' in file:
        abort(404)
    return send_file('app/dist/'+file)

if __name__ == '__main__':
    app.run(debug=args.debug, host='localhost',port=args.port)
