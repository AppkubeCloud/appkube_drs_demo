# Install Java 17 using the 'java' cookbook
jdk_package = 'openjdk-17-jre-headless'

apt_update 'update' do
  action :update
end

# Get DB config parameters from databag
dbconfigdata = data_bag_item(node['petclinic']['config_data_bag'],'dbconfig_items')

# Use the package resource to install OpenJDK 17
package jdk_package do
  action :install
end

log 'java_installation_complete' do
  message 'Java installation is complete.'
  level :info  # You can choose the log level (e.g., :info, :warn, :error) based on your preference.
  action :write
end

# Create a Maven directory
directory '/opt/maven' do
  owner 'root'
  group 'root'
  mode '0755'
  action :create
end

maven_extract_dir = "/opt/apache-maven"

# Define the Maven version and URL
#maven_version = '3.8.4'
maven_url = "https://dlcdn.apache.org/maven/maven-3/3.9.4/binaries/apache-maven-3.9.4-bin.tar.gz"

maven_home = '/opt/maven'
maven_bin = "#{maven_home}/bin"
maven_cmd = 'mvn'

execute 'download_maven' do
  command "wget #{maven_url} -O /tmp/apache-maven.tar.gz"
  user 'root'
  group 'root'
  not_if { ::File.exist?("#{maven_bin}/#{maven_cmd}") }
end

# Define environment variables for Maven
# Extract Maven and set environment variables
execute 'extract_maven' do
  command "tar xzf /tmp/apache-maven.tar.gz -C #{maven_home} --strip-components=1"
  environment 'M2_HOME' => maven_home,
              'M2' => "#{maven_bin}/#{maven_cmd}"
  action :run
  not_if { ::File.exist?("#{maven_bin}/#{maven_cmd}") }
end

# Create a symbolic link to Maven binary
link '/usr/bin/mvn' do
  to "#{maven_bin}/#{maven_cmd}"
end

log 'Maven_installation_complete' do
  message 'maven installation is complete.'
  level :info  # You can choose the log level (e.g., :info, :warn, :error) based on your preference.
  action :write
end

 #Define the target directory where you want to clone the repository
target_directory = '/home/ubuntu/spring-petclinic-rest'

# Define the Git repository URL
repository_url = 'https://github.com/spring-petclinic/spring-petclinic-rest.git'

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

log 'repo_clone_complete' do
  message 'pet-clinic repo clone is complete.'
  level :info  # You can choose the log level (e.g., :info, :warn, :error) based on your preference.
  action :write
end

# Configurations of applications
template '/home/ubuntu/spring-petclinic-rest/src/main/resources/application-postgresql.properties' do
  source 'appconfigfile.erb'
  variables( DB_host: dbconfigdata['DB_host'],
            DB_user: dbconfigdata['DB_user'], 
            DB_password: dbconfigdata['DB_password'] )
  notifies :run, 'execute[run_maven_build]', :delayed
  notifies :restart, 'service[petclinic]', :delayed
end

template '/home/ubuntu/spring-petclinic-rest/src/main/resources/application.properties' do
  source 'application_properties.erb'
  variables( DB_database: dbconfigdata['DB_database'])
  notifies :run, 'execute[run_maven_build]', :delayed
  notifies :restart, 'service[petclinic]', :delayed
end

log 'configuration_complete' do
  message 'pet-clinic configurations is complete.'
  level :info  # You can choose the log level (e.g., :info, :warn, :error) based on your preference.
  action :write
end

# Define the command to run
mvn_command = 'rm -rf /home/ubuntu/spring-petclinic-rest/target && mvn clean install -DskipTests=true'

# Use the execute resource to run the command with sudo as the root user
execute 'run_maven_build' do
  command "sudo #{mvn_command}"
  cwd '/home/ubuntu/spring-petclinic-rest' # Specify the path to your Maven project
  user 'root'
  action :nothing
end

# creating service for pet clinic
# Define the unit file path
unit_file_path = '/etc/systemd/system/petclinic.service'

# Define the content for the unit file
unit_file_content = <<-EOL
[Unit]
Description=My automobile App
After=syslog.target

[Service]
User=ubuntu
ExecStart=/usr/bin/java -jar /home/ubuntu/spring-petclinic-rest/target/spring-petclinic-rest-3.0.2.jar
SuccessExitStatus=143

[Install]
WantedBy=multi-user.target
EOL

# Use the file resource to create the unit file
file unit_file_path do
  content unit_file_content
  owner 'root'
  group 'root'
  mode '0644'
  action :create
end

# Enable and start the systemd service
service 'petclinic' do
  action [:enable, :start]
end

# Restart the petclinic service
service 'petclinic' do
  action :nothing
end
