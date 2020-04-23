N = 1

Vagrant.configure("2") do |config|
  config.vm.box = "debian/stretch64"
  config.vm.synced_folder ".", "/vagrant", type: "virtualbox"
  config.vm.provision "shell", path: "provision/base.sh"

  config.vm.define "kube-master" do |master|
    MASTER_IP="192.168.10.10"
    master.disksize.size = "100GB"
    master.vm.network :private_network, ip: MASTER_IP
    master.vm.network "forwarded_port", guest: 31000, host: 31000 # Kube dashboard
    master.vm.network "forwarded_port", guest: 31001, host: 31001 # Prometheus
    master.vm.network "forwarded_port", guest: 31002, host: 31002 # Grafana
    master.vm.network "forwarded_port", guest: 30080, host: 32000 # HTTP Adapter
    master.vm.network "forwarded_port", guest: 31883, host: 32001 # MQTT Adapter
    master.vm.network "forwarded_port", guest: 32672, host: 32002 # AMQP Adapter
    master.vm.network "forwarded_port", guest: 30672, host: 33000 # Dispatch router
    master.vm.network "forwarded_port", guest: 31080, host: 33001 # Device registry
    master.vm.hostname = "kube-master"
    master.vm.provision "shell", path: "provision/master.sh",
                        env: { "HOST_IP" => MASTER_IP, "POD_CIDR" => "10.244.0.0/16" }
    master.vm.provision "shell", path: "provision/dynamic-pvc.sh"
    master.vm.provision "shell", path: "provision/hono.sh"
    master.vm.provider "virtualbox" do |v|
      v.memory = 8192
      v.cpus = 4
    end
  end

  (1..N).each do |i|
    config.vm.define "kube-node-#{i}" do |node|
      node.vm.network :private_network, ip: "192.168.10.#{i + 10}"
      node.vm.hostname = "kube-node-#{i}"
      node.vm.provision "shell", path: "provision/node.sh"
      node.vm.provider "virtualbox" do |v|
        v.memory = 8192
        v.cpus = 2
      end
    end
  end

end
