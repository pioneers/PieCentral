###############################################################################
# --- packages needed by pretty much everyone ---
package 'build-essential' do
  version '11.6ubuntu6'
end
package 'make' do
  version '3.81-8.2ubuntu3'
end
package 'gcc' do
  version '4:4.8.2-1ubuntu6'
end
# packages that we most likely won't care about which version we're running.
# Unless we get absurdly unlucky this shouldn't come back to bite us at any point
package 'cowsay'
package 'git'
package 'htop'

package 'samba'
package 'cifs-utils'
bash 'sambaSetup' do
  code <<-EOH
    if [ ! -d /home/vagrant/shared ]; then
      mkdir -p /home/vagrant/shared
      sudo smbpasswd -an vagrant
      sudo rm /etc/samba/smb.conf
      sudo cp /vagrant/resources/smb.conf /etc/samba/
      chmod a+rw /home/vagrant/shared
      sudo service smbd restart
    fi;
  EOH
end

###############################################################################
# --- packages for runtime and ui ---
#
# install nodejs, globally installed npm packages, and dawn specific packages
# (we're assuming the dawn repo has been cloned in the expected location)
bash 'nodejsSetup' do
  code <<-EOH
    curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -
    sudo apt-get install -y nodejs
    sudo apt-get install -y npm
    sudo npm install -g gulp
    sudo npm install -g coffee-script
  EOH
end

package 'python' do
  version '2.7.5-5ubuntu3'
end
package 'python-dev' do
  version '2.7.5-5ubuntu3'
end
package 'python-pip' do
  version '1.5.4-1'
end

# Note that the pip grizzly package is out of date. This ends up being a
# non-issue for us at the moment, though, as obviously a grizzly is never
# actually talked to using a VM, and we really only need the package to
# ensure that runtime can import the grizzly package without any problems
# This, of course, will be fixed if necessary.
bash 'pythonPackagesSetup' do
  code <<-EOH
    sudo pip install --upgrade pyserial
    sudo pip install --upgrade grizzly
  EOH
end

###############################################################################
# --- packages for web redesign ---
package 'ruby' do
  version '1:1.9.3.4'
end
package 'ruby-dev' do
  version '1:1.9.3.4'
end
bash 'jekyllSetup' do
  code <<-EOH
    sudo gem install jekyll -v '2.5.3'
  EOH
end
