# Get DB config parameters from databag
appconfigdata = data_bag_item(node['petclinic']['config_data_bag'],'appconfig_items')
# Get WEB config parameters from databag
webconfigdata = data_bag_item(node['petclinic']['config_data_bag'],'webconfig_items')

apt_update 'update' do
  action :update
end

# Use the execute resource to download and run the Node.js setup script as root
execute 'download_and_run_nodesource_setup' do
  command 'curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -'
  user 'root'
  action :run
  not_if 'dpkg -l | grep -E "^ii\s+nodejs\b"'  # Check if "nodejs" package is installed
end

# Install Node.js as root if it's not already installed
package 'nodejs' do
  action :install
  not_if 'dpkg -l | grep -E "^ii\s+nodejs\b"'  # Check if "nodejs" package is installed
end

# Use the execute resource to update npm to the latest version
execute 'update_npm' do
  command 'npm install -g npm@latest'
  user 'root'
  action :run
  not_if 'npm -v | grep -q "^10"'
end

# Install the latest version of the Angular CLI globally
execute 'install_angular_cli' do
  command 'npm install -g @angular/cli@latest'
  user 'root'
  action :run
  not_if 'ng version | grep -q "^Angular:"'
end

# Install Nginx
package 'nginx' do
  action :install
end

# Start and enable the Nginx service
service 'nginx' do
  action [:enable, :start]
end
target_directory = '/home/ubuntu/spring-petclinic-angular'

# Define the Git repository URL
repository_url = 'https://github.com/spring-petclinic/spring-petclinic-angular.git'

# Set the owner and group for the target directory to 'root'
directory target_directory do
  owner 'root'
  group 'root'
  mode '0755'
  action :create
end

git target_directory do
  repository repository_url
  revision 'master'
  action :sync
end
# Define the path to your configuration file
template '/home/ubuntu/spring-petclinic-angular/src/environments/environment.ts' do
  source 'environment.ts.erb'
  variables( APP_host: appconfigdata['APP_host'])
  notifies :run, 'execute[npm_install]', :delayed
  notifies :run, 'execute[ng_build]', :delayed
end

# recipes/build_angular_app.rb
# Define the path to your Angular project directory
angular_project_dir = '/home/ubuntu/spring-petclinic-angular/'

execute 'npm_install' do
  command 'npm install'
  cwd angular_project_dir  # Set the working directory to the project directory
  action :nothing
end

# Execute the ng build command
execute 'ng_build' do
  command "cd #{angular_project_dir} && ng build"
  user 'root'  # Replace with the username that should run the command
  action :nothing
end

# recipes/configure_nginx.rb
template '/etc/nginx/sites-enabled/petclinic' do
  source 'petclinic.erb'
  variables( WEB_dns: webconfigdata['WEB_dns'])
  notifies :reload, 'service[nginx]', :delayed
end

# Use the service resource to reload Nginx
service 'nginx' do
  action :nothing
end
