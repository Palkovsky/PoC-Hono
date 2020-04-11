N = 1
POD_CIDR="10.244.0.0/16"

Vagrant.configure("2") do |config|
  config.vm.provision "shell", path: "provision.sh"
  config.vm.box = "debian/stretch64"

  config.vm.define "kube-master" do |master|
    MASTER_IP="192.168.10.10"
    master.vm.network :private_network, ip: MASTER_IP
    master.vm.hostname = "kube-master"
    master.vm.provision "shell", path: "master-provision.sh",
                        env: {
                          "HOST_IP" => MASTER_IP,
                          "POD_CIDR" => POD_CIDR
                        }
    master.vm.provider "virtualbox" do |v|
      v.memory = 4096
      v.cpus = 4
    end
  end

  (1..N).each do |i|
    config.vm.define "kube-node-#{i}" do |node|
      node.vm.network :private_network, ip: "192.168.10.#{i + 10}"
      node.vm.hostname = "kube-node-#{i}"
      node.vm.provision "shell", path: "node-provision.sh"
      node.vm.provider "virtualbox" do |v|
        v.memory = 4096
        v.cpus = 2
      end
    end
  end
end
