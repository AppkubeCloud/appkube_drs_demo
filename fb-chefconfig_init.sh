#!/bin/bash
if [ "$#" -lt 1 ]; then
  echo 'Required 1 parameter, usage:- ./chefconfig_init.sh git_repo_path'
  exit 1
fi
repopath=$1
# Define the local repository path
repo_path="$repopath"
# Change to the local repository directory
cd "$repo_path" || exit
    echo "Upload cookbooks,data bags,roles and add runlist ..."
    # pull changes from the remote master branch
    git pull origin main
    # upload the cookbook
    knife cookbook upload --cookbook-path "$repo_path"/cookbooks/ --all
    # create pr data bag
    knife data bag create configbag
    # import pr data bags
    knife data bag from file configbag --all
    # create dr data bag
    knife data bag create drconfigbag
    # import dr data bags
    knife data bag from file drconfigbag --all
    # import role
    knife role from file roles/*.json
    # Attach pr node to role
    knife node run_list add DBNode role['pr_role']
    knife node run_list add WebNode role['pr_role']
    knife node run_list add AppNode role['pr_role']
    # add runlist for dbnode,webnode and appnode
    knife node run_list add DBNode 'recipe[db-cookbook::default]'
    knife node run_list add AppNode 'recipe[PetClinic-App::default]'
    knife node run_list add WebNode 'recipe[PetClinic-Web::default]'
    # exit the script    
    exit 0
