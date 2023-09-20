# In attributes/default.rb

# Define the PostgreSQL database user
#default['db-cookbook']['db_user'] = 'database_user'

# Define the PostgreSQL database password
#default['db-cookbook']['password'] = 'password'

# Define the PostgreSQL database name
#default['db-cookbook']['db_name'] = 'petclinic'
#
#
# db-cookbook/attributes/default.rb

# Default PostgreSQL attributes
default['postgresql']['username'] = 'database_user'
default['postgresql']['password'] = 'password'
default['postgresql']['dbname'] = 'petclinic'

