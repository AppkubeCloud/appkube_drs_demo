# This is a Chef Infra Client recipe file. It can be used to specify resources
# which will apply configuration to a server.

#require 'jinja2'

data = data_bag_item('example','example_item')

log "Welcome to Chef Infra Client, #{node['example']['name']}!" do
  level :info
end

template '/tmp/info.html' do
  owner 'root'
  group 'root'
  mode '0644'
  source 'info.html.erb'
  action :create_if_missing
end

#gem_package 'jinja2' do
#chef_gem 'jinja2' do
  #gem_binary '/opt/chef/embedded/lib/ruby/gems/2.6.0/gems'
#  clear_sources true
#  source 'https://rubygems.org/gems/jinja2'
#  action :install
#end

#jinja2_file '/tmp/jinjaoutput.txt'do 
template '/tmp/jinjaoutput1.txt'do 
  source 'rubysample.erb' 
  variables( name: data['name'], age: data['age'] ) 
end

# For more information, see the documentation: https://docs.chef.io/recipes.html
