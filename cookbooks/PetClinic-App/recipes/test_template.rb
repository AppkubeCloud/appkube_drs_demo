# This is a Chef Infra Client recipe file. It can be used to specify resources
# which will apply configuration to a server.

#require 'jinja2'

configdata = data_bag_item('configbag','dbconfig_items')


template '/tmp/appconfig1.txt'do 
  source 'appconfigfile.erb' 
  variables( DB_host: configdata['DB_host'], DB_user: configdata['DB_user'], DB_password: configdata['DB_password'] ) 
end

# For more information, see the documentation: https://docs.chef.io/recipes.html
