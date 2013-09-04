# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
	config.vm.box = "precise64"

	# The url from where the 'config.vm.box' box will be fetched if it
	# doesn't already exist on the user's system.
	config.vm.box_url = "http://files.vagrantup.com/precise64.box"

	# Create a public network, which generally matched to bridged network.
	# Bridged networks make the machine appear as another physical device on
	# your network.
	config.vm.network :public_network

	# Run provisioning scripts
	config.vm.provision :shell, :path => "bootstrap.sh"
end
