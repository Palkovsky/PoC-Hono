sudo -u vagrant bash <<'EOF'
helm repo add eclipse-iot https://eclipse.org/packages/charts && \
helm repo update && \
kubectl create namespace hono && \
helm install --generate-name --dependency-update \
     --values /vagrant/yamls/hono.values.yaml \
     -n hono eclipse-iot/hono
EOF
