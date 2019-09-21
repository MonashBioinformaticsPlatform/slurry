#!/usr/bin/env python

from flask import Flask, send_file

from slurm import *

test=True

conf = SlurmConfig(test)
log("Read config {} settings".format(len(conf.data)))

share = ShareInfo(test)
share.read_info()
log("Read sshare {} lines".format(len(share.data)))

queue = Queue(test)
queue.read_queue()
log("Read queue {} lines".format(len(queue.data)))

app = Flask(__name__)

@app.route('/', defaults={'file': 'index.html'})
@app.route('/<path:file>')
def index(file):
    return send_file('app/dist/'+file)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
