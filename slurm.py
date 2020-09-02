import subprocess
import csv
import re
import sys
import codecs
from datetime import datetime

class SlurmConfig:
    def __init__(self, test=False):
        self.test = test
        if self.test:
            reader = open('test-data/scontrol.dmp', mode='rb')
        else:
            p = subprocess.Popen("scontrol show config", shell=True, stdout=subprocess.PIPE, close_fds=True)
            reader = p.stdout
        self.data = []
        for line in reader:
            line = line.decode('latin-1')
            m = re.match("(\S+)\s+=\s+(.*)", line)
            if m:
                (key,val) = m.groups()
                self.data.append({"key": key, "value":val})
        self.updated = datetime.now()

class ShareInfo:
    def __init__(self, test=False):
        self.test = test
        self.data = []
        self.updated = None

    def read_info(self):
        if self.test:
            reader = open('test-data/sshare.dmp')
        else:
            # From : sshare --helpformat | perl -0777 -pe 's{[\s\n]+}{,}g; chop'
            flds = "Account,Cluster,EffectvUsage,FairShare,GrpTRESMins,GrpTRESRaw,ID,LevelFS,NormShares,NormUsage,Partition,RawShares,RawUsage,TRESRunMins,User"
            cmd = "sshare -P -a -o {}".format(flds)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
            reader = codecs.iterdecode(p.stdout, 'latin-1')

        self.data = list(csv.DictReader(reader, delimiter='|'))
        self.updated = datetime.now()

class QOS:
    def __init__(self, test=False):
        self.test = test
        if self.test:
            reader = open('test-data/qos.dmp', mode='rb')
        else:
            p = subprocess.Popen("sacctmgr -p show qos", shell=True, stdout=subprocess.PIPE, close_fds=True)
            reader = codecs.iterdecode(p.stdout, 'latin-1')

        self.data = list(csv.DictReader(reader, delimiter='|'))
        # Delete any empty key in the dicts
        for d in self.data:
            d.pop('',None)
        self.updated = datetime.now()

class Partition:
    def __init__(self, test=False):
        self.test = test
        if self.test:
            reader = open('test-data/partitions.dmp', mode='rb')
        else:
            p = subprocess.Popen("scontrol show -o partition", shell=True, stdout=subprocess.PIPE, close_fds=True)
            reader = p.stdout
        self.data = []
        for line in reader:
            line = line.decode('latin-1')
            m = re.findall("(\S+)=(\S+)", line)
            self.data.append(dict(m))
        self.updated = datetime.now()


class Queue:
    def __init__(self, test=False):
        self.test = test
        self.data = []
        self.prio = []
        self.updated = None
        self.wanted_keys = ('JobId JobName UserId GroupId Priority Nice Account QOS '
                           'JobState Reason Requeue Restarts RunTime TimeLimit '
                           'SubmitTime AccrueTime StartTime EndTime RunTime '
                           'Partition AllocNode NodeList NumNodes NumCPUs NumTasks').split(' ')

    def read(self):
        self._read_prio()
        self._read_queue()
        # Merge prio & queue
        prio_by_id = {}
        for r in self.prio:
            prio_by_id[r['JOBID']] = r
        keys = self.prio[0].keys()
        for idx, r in enumerate(self.data):
            id = r['JobId']
            if id in prio_by_id:
                for key, value in prio_by_id[id].items():
                    self.data[idx]["sprio."+key] = value
            else:
                for key in keys:
                    self.data[idx]["sprio."+key] = None

        self.updated = datetime.now()

    def _read_prio(self):
        if self.test:
            # sprio -o "$(echo '%i\t%r\t%Y\t%A\t%F\t%J\t%P\t%Q\t%T')" > sprio.dmp
            reader = open('test-data/sprio.dmp')
        else:
            flds = "%i\t%r\t%Y\t%A\t%F\t%J\t%P\t%Q\t%T"
            cmd = "sprio -o '{}'".format(flds)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
            reader = codecs.iterdecode(p.stdout, 'latin-1')

        self.prio = list(csv.DictReader(reader, delimiter='\t'))

    def _read_queue(self):
        if self.test:
            # scontrol show job > scontrol-show-job.dmp
            reader = open('test-data/scontrol-show-job.dmp')
        else:
            cmd = "scontrol show job"
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
            reader = codecs.iterdecode(p.stdout, 'latin-1')

        # Parse the data
        data = []
        for line in reader:
            if line.startswith('JobId='):
                data.append({})
            for (key, value) in re.findall(r'(\S+)=(\S+)', line):
                if key in self.wanted_keys:
                    data[-1][key] = value

        self.data = data

def log(str):
    sys.stderr.write(str + "\n")
