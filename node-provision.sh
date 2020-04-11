#!/bin/bash
apt install -y sshpass && \
    sshpass -p "vagrant" \
            scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
            vagrant@kube-master.local:/joincluster.sh /joincluster.sh && \
    /bin/bash /joincluster.sh
