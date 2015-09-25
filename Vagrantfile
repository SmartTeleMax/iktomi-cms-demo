# vim: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = 'ubuntu1404'
  config.vm.box_url = 'http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box'

  config.vm.provider 'virtualbox' do |vb|
    vb.memory = '1024'
    vb.customize ['modifyvm', :id, '--groups', '/iktomi']
  end

  config.vm.provision 'ansible' do |ansible|
    ansible.playbook = 'ansible/playbook.yml'
    #ansible.verbose = 'vv'
  end

  config.vm.define 'py27', primary: true do |machine|
    config.vm.provider :virtualbox do |vb|
      vb.name = 'iktomi-cms-demo-py27'
    end
    config.vm.network 'forwarded_port', guest: 80, host: 8027
  end

  config.vm.define 'py34', autostart: false do |machine|
    config.vm.provider :virtualbox do |vb|
      vb.name = 'iktomi-cms-demo-py34'
    end
    config.vm.network 'forwarded_port', guest: 80, host: 8034
  end

end
