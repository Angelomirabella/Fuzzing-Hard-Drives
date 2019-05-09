# encoding: utf-8
# -*- mode: ruby -*-
# vi: set ft=ruby :

# Box / OS
VAGRANT_BOX = 'bento/ubuntu-18.04'

# Memorable name for your
VM_NAME = 'new-vm'

# VM User — 'vagrant' by default
VM_USER = 'vagrant'

# Username on your Ubuntu
UBUNTU_USER = 'angelo'

# Host folder to sync
HOST_PATH = '/home/' + UBUNTU_USER + '/' + VM_NAME

# Where to sync to on Guest — 'vagrant' is the default user name
GUEST_PATH = '/home/' + VM_USER + '/' + VM_NAME

# # VM Port — uncomment this to use NAT instead of DHCP
 VM_PORT = 8080

Vagrant.configure(2) do |config|

  # Vagrant box from Hashicorp
  config.vm.box = VAGRANT_BOX
  
  # Actual machine name
 # config.vm.hostname = VM_NAME

  # Set VM name in Virtualbox
  config.vm.provider "virtualbox" do |v|
  #  v.name = VM_NAME
    v.memory = 2048
  end

  #DHCP — comment this out if planning on using NAT instead
 #  config.vm.network "private_network", type: "dhcp"

  config.vm.network "forwarded_port", guest: 1500, host: 1500

  # # Port forwarding — uncomment this to use NAT instead of DHCP
  # config.vm.network "forwarded_port", guest: 80, host: VM_PORT

  # Sync folder
  config.vm.synced_folder HOST_PATH, GUEST_PATH
# Enable USB Controller on VirtualBox
   config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--usb", "on"]
    vb.customize ["modifyvm", :id, "--usbxhci", "on"]
    vb.customize ["usbfilter", "add", "0", 
      "--target", :id, 
      "--name", "ULT-Best Best USB Device [0100]",
      "--manufacturer", "ULT-Best",
      "--product", "Best USB Device",
      "--serialnumber", "12345882407D"]
   end

 # Install Git,ykush, pip , boofuzz
   config.vm.provision "shell", inline: <<-SHELL
     sudo python /vagrant/project/fuzzer.py -n 1500 sdb &
   SHELL
end

