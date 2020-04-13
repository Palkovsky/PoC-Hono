apt install -y  nfs-kernel-server && \
    mkdir -p /mnt/shared && \
    chown nobody:nogroup /mnt/shared && \
    chmod 777 /mnt/shared && \
    echo "/mnt/shared *(rw,sync,no_subtree_check,no_root_squash,insecure)" \
        | tee -a /etc/exports && \
    exportfs -a && \
    systemctl restart nfs-kernel-server && \
sudo -u vagrant bash <<'EOF'
kubectl apply -f /vagrant/yamls/storage.yaml
EOF
