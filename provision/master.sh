#!/bin/bash
# generate kube config
kubeadm config images pull && \
    kubeadm init \
            --apiserver-advertise-address=$HOST_IP \
            --pod-network-cidr=$POD_CIDR >> /root/kubeinit.log && \
    # copy kube config
    mkdir /home/vagrant/.kube && \
    cp /etc/kubernetes/admin.conf /home/vagrant/.kube/config && \
    chown -R vagrant:vagrant /home/vagrant/.kube && \
    # generate cluster join script
    kubeadm token create --print-join-command > /joincluster.sh && \
    # install helm
    curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | /bin/bash && \
    sudo -u vagrant bash -s <<'EOF'
kubectl create -f /vagrant/yamls/kube-flannel.yaml && \
kubectl apply -f /vagrant/yamls/kube-dashboard.yaml
EOF
