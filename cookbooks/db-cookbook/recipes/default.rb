# Step 1: Check if PostgreSQL is already installed
postgresql_installed = system('pg_config --version')

apt_update 'update' do
  action :update
end

# Step 2: Install PostgreSQL if not installed
package 'postgresql' do
  action :install
  not_if { postgresql_installed }
end

package 'postgresql-contrib' do
  action :install
  not_if { postgresql_installed }
end

# Step 1: Check if PostgreSQL got installed 
postgresql_installed = system('pg_config --version')

# Step 3: Fetch PostgreSQL version
ruby_block 'fetch_postgresql_version' do
  block do
    postgresql_version = shell_out('pg_config --version').stdout.strip.split.last
    node.default['postgresql']['version'] = postgresql_version
    node.default['postgresql']['config_dir'] = "/etc/postgresql/#{postgresql_version}/main"
  end
  action :run
  only_if { postgresql_installed }
end

# Step 4: Set the PostgreSQL user and password
db_user = node['postgresql']['username']
db_pass = node['postgresql']['password']
db_name = node['postgresql']['dbname']

# Create a PostgreSQL user with full privileges
execute 'create_postgres_user' do
  command "sudo -u postgres psql -c \"CREATE ROLE #{db_user} WITH SUPERUSER LOGIN CREATEDB CREATEROLE PASSWORD '#{db_pass}';\""
  sensitive false
  not_if "sudo -u postgres psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='#{db_user}';\" | grep -q 1"
  action :run
  only_if { postgresql_installed }
end

# Alter the role to allow login
execute 'alter_postgres_user_login' do
  command "sudo -u postgres psql -c \"ALTER ROLE #{db_user} WITH LOGIN;\""
  sensitive false
  not_if "sudo -u postgres psql -tAc \"SELECT rolcanlogin FROM pg_roles WHERE rolname='#{db_user}';\" | grep -q t"
  action :run
  only_if { postgresql_installed }
end


# Step 5: Modify postgresql.conf
execute 'update_postgresql_conf' do
  command "sudo sed -i \"s/^#listen_addresses = 'localhost'/listen_addresses = '*'/\" /etc/postgresql/12/main/postgresql.conf"
  action :run
  notifies :restart, 'service[postgresql]', :immediately
  only_if { postgresql_installed }
end


#6  Modify pg_hba.conf to allow access from all IP addresses
pg_hba_conf_path = '/etc/postgresql/12/main/pg_hba.conf'

ruby_block 'update_pg_hba_conf' do
  block do
    current_contents = ::File.read(pg_hba_conf_path)
    if current_contents.include?('127.0.0.1/32')
      updated_contents = current_contents.gsub('127.0.0.1/32', '0.0.0.0/0')
      ::File.write(pg_hba_conf_path, updated_contents)
    end
  end
  action :run
  only_if { postgresql_installed }
end

# Notify PostgreSQL service to restart if changes were made
service 'postgresql' do
  action :nothing
end



# Step 7: Create the PostgreSQL database
execute 'create_postgresql_database' do
  command "sudo -u postgres createdb #{db_name}"
  sensitive false
  not_if "sudo -u postgres psql -l | grep -q #{db_name}"
  action :run
  only_if { postgresql_installed }
end

# Step 8: Grant privileges on the database to the user
execute 'grant_privileges_to_user' do
  command "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE #{db_name} TO #{db_user};\""
  sensitive false
  not_if "sudo -u postgres psql -c \"SELECT has_database_privilege('#{db_user}', '#{db_name}', 'CONNECT');\" | grep -q t"
  action :run
  only_if { postgresql_installed }
end

# Step 9: Configure PostgreSQL service
service 'postgresql' do
  action [:enable, :start]
end

