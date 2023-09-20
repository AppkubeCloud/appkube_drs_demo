# Step 1: Check if PostgreSQL is already installed
postgresql_installed = system('dpkg -l | grep -q postgresql')

# Step 2: Install PostgreSQL if not installed
package 'postgresql' do
  action :install
  not_if { postgresql_installed }
end

package 'postgresql-contrib' do
  action :install
  not_if { postgresql_installed }
end

# Step 3: Fetch PostgreSQL version
ruby_block 'fetch_postgresql_version' do
  block do
    postgresql_version = shell_out('pg_config --version').stdout.strip.split.last
    node.default['postgresql']['version'] = postgresql_version
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
  command "sudo -u postgres psql -c \"CREATE ROLE #{db_user} WITH SUPERUSER CREATEDB CREATEROLE PASSWORD '#{db_pass}';\""
  sensitive false
  not_if "sudo -u postgres psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='#{db_user}';\" | grep -q 1"
  action :run
  only_if { postgresql_installed }
end


# Step 5: Modify postgresql.conf
execute 'update_postgresql_conf' do
  command "sed -i 's/^#listen_addresses = 'localhost'/listen_addresses = '*'/' /etc/postgresql/#{node['postgresql']['version']}/main/postgresql.conf"
  action :run
  notifies :restart, 'service[postgresql]', :immediately
  only_if { postgresql_installed }
end


# Step 6: Modify pg_hba.conf
execute 'update_pg_hba_conf' do
  command <<-EOH
    echo "host #{db_name} #{db_user} 0.0.0.0/0 md5" >> /etc/postgresql/#{node['postgresql']['version']}/main/pg_hba.conf
    EOH
  action :run
  notifies :restart, 'service[postgresql]', :immediately
  only_if { postgresql_installed }
end


# Step 7: Configure PostgreSQL service
service 'postgresql' do
  action [:enable, :start]
end

