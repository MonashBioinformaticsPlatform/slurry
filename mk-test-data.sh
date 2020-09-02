#!/bin/sh

mkdir -p test-data

scontrol show config > test-data/scontrol.dmp

sshare -P -a -o Account,Cluster,EffectvUsage,FairShare,GrpTRESMins,GrpTRESRaw,ID,LevelFS,NormShares,NormUsage,Partition,RawShares,RawUsage,TRESRunMins,User > test-data/sshare.dmp

sprio -o "$(/bin/echo -e '%i\t%r\t%Y\t%A\t%F\t%J\t%P\t%Q\t%T')" > test-data/sprio.dmp

scontrol show job > test-data/scontrol-show-job.dmp

scontrol show -o partition > test-data/partitions.dmp

sacctmgr -p show qos > test-data/qos.dmp