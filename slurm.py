#!/bin/env python

import subprocess
import csv
import re
import sys

class SlurmConfig:
    def __init__(self, test=False):
        self.test = test
        if self.test:
            reader = open('test-data/scontrol.dmp')
        else:
            p = subprocess.Popen("scontrol show config", shell=True, stdout=subprocess.PIPE, close_fds=True)
            reader = p.stdout
        self.data = {}
        for line in reader:
            m = re.match("(\S+)\s+=\s+(.*)", line)
            if m:
                (key,val) = m.groups()
                self.data[key] = val

class ShareInfo:
    def __init__(self, test=False):
        self.test = test
        self.data = []

    def read_info(self):
        if self.test:
            reader = open('test-data/sshare.dmp')
        else:
            # From : sshare --helpformat | perl -0777 -pe 's{[\s\n]+}{,}g; chop'
            flds = "Account,Cluster,EffectvUsage,FairShare,GrpTRESMins,GrpTRESRaw,ID,LevelFS,NormShares,NormUsage,Partition,RawShares,RawUsage,TRESRunMins,User"
            cmd = "sshare -P -a -o {}".format(flds)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
            reader = p.stdout

        self.data = list(enumerate(csv.DictReader(reader, delimiter='|')))

class Queue:
    def __init__(self, test=False):
        self.test = test
        self.data = []

    def read_queue(self):
        if self.test:
            reader = open('test-data/squeue.dmp')
        else:
            flds = "%i\t%P\t%j\t%u\t%T\t%M\t%l\t%D\t%R\t%Q\t%C"
            cmd = "squeue -o '{}'".format(flds)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True)
            reader = p.stdout

        self.data = list(enumerate(csv.DictReader(reader, delimiter='\t')))

def log(str):
    sys.stderr.write(str + "\n")
