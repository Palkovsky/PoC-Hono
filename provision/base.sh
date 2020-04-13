#!/bin/bash
# Docker
apt-get update -y && \
    apt install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" && \
    apt install -y docker && \
    apt-get update -y && \
    apt-cache policy docker-ce && \
    apt install -y docker-ce && \
    systemctl enable docker && \
    systemctl start docker && \
    # avahi for mDNS
    apt install -y avahi-daemon avahi-discover avahi-utils libnss-mdns && \
    sed -i  '/deny-interfaces/c deny-interfaces=docker0' /etc/avahi/avahi-daemon.conf && \
    systemctl enable avahi-daemon && \
    systemctl restart avahi-daemon && \
    # disable swap
    swapoff -a && \
    sed -i '/swap/d' /etc/fstab && \
    # kubernetes
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    add-apt-repository "deb https://apt.kubernetes.io/ kubernetes-xenial main" && \
    apt-get update -y && \
    apt install -y kubelet kubeadm kubectl && \
    systemctl enable kubelet && \
    systemctl start kubelet && \
    # ssh
    sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    systemctl reload sshd && \
    # NFS utils
    apt-get install -y nfs-common
