## AWS Disater Recovery of 3-Tier Application

**DR-Application Overview**

This repository includes documentation and scripts for establishing and overseeing disaster recovery procedures for a 3-Tier application running on AWS. Disaster recovery is critical for maintaining uninterrupted business operations in the face of unforeseen disruptions or system outages.

## Prerequisite
Before implementing disaster recovery for your 3-Tier application, make sure you have the following prerequisites:
- Chef Setup and configured on AWS Account in Primary and disaster recovery regions.
- AWS Account with requied permissions.
- AWS 3-Tier Application deployed and running on PR site.
- Familiarity with AWS services such as EC2, VPC, AWS Backup & Restore, Lambda, AWS SNS, AWS Eventbridge, Step Function, IAM, Route53.
- DR chef server is preconfigured with separate organization for disaster workflow.
## Architecture

![alt text](https://github.com/abdul-rajak/Dr-Chef-Git-Repo/blob/main/Architecture/DR-Architecture.jpg?raw=true)


## Version Control
1. Ensure that the primary Chef server is under version control using Git.
+ Version control is a crucial aspect of managing configuration and code changes in a Chef server environment. By placing the primary Chef server under version control using Git, you gain several benefits.

2. Make sure Git is accessible from the DR site.
+ In a disaster recovery scenario, ensuring that Git is accessible from the DR (Disaster Recovery) site is essential for a smooth recovery process.
## Application Stack
- The sample application is a 3-tier architecture managed by the Chef server through Chef recipes.
- Components include a DB node (PostgreSQL), App node (Spring Boot), and Web node (Angular).

## StepFunction flow

![alt text](https://github.com/abdul-rajak/Dr-Chef-Git-Repo/blob/main/Architecture/StepFunction-flow.jpg?raw=true)

## Disaster Recovery Workflow

**Backup Strategy** :
+ AWS backups are scheduled for essential nodes and stored securely in the DR backup vault.

**Disaster Simulation & Auto trigger**:
+ Simulate a disaster by disabling the Web node.
+ AWS EventBridge detects the state change (stopped) and triggers an SNS notification, initiating the Step Function.

**Step Function** :
The Step Function orchestrates recovery by systematically invoking Lambda functions.
Key steps include :
+ Pet-Clinic-DB-server-Restore, Pet-Clinic-App-server-Restore, Pet-Clinic-Web-server-Restore: These functions restores respective server.
+ Assigning-Iam-Pass-Role function: Assign the necessary IAM roles to restore servers.
+ AssociateEIP: Assign predetermine IPs to restore servers.
+ dr-workstation-git-setup: Git repository cloning on the DR workstation and update DR Data bags as per DR site configuration.
+ dr_bootstrap_nodes: Bootstrap the nodes and Applies configuration changes to DR Chef Server.
     + Upload cookbooks
     + Create databags and load items
     + Create dr-role and assigned nodes to this role.
     + Add recipes to the nodes.
+ Route-53-Record-Add: Update DNS records for DR site.
    
**Chef Client**: 
+ Automatically reapplies changes from the updated Chef server on the nodes.

## Testing
+ Access the 3-tier application at the DR (Disaster Recovery) site and verify application is operational.
+ Verify a new entry can be added to application.
+ Verify Elastic IPs are assinged to Nodes.


