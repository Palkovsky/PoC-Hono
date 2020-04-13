sudo -u vagrant bash <<'EOF'
helm repo add stable https://kubernetes-charts.storage.googleapis.com && \
helm repo update && \

kubectl create namespace prometheus && \
helm install --generate-name \
     --values /vagrant/yamls/prometheus.values.yaml \
     -n prometheus stable/prometheus && \

kubectl create namespace grafana && \
helm install --generate-name \
     --values /vagrant/yamls/grafana.values.yaml \
     -n grafana stable/grafana

EOF
