# Bootstrap nodes

import json
import boto3
import paramiko

def lambda_handler(event, context):
    # boto3 client
    client = boto3.client("ec2")
    s3_client = boto3.client("s3")

    # getting instance information
    describeInstance = client.describe_instances()
    
    # Initialize all required variables
    drWorkStationPublicIP = ""
    drAppPrivateIP = ""
    drAppPublicIP = ""
    drDBPrivateIP = ""
    drWorkStationName = "Dr-ChefWorkstation"
    drAppServerName = "PetClinic-App" 
    drDBServerName = "PetClinic-DB"
    drWebServerName = "PetClinic-Web"
    drAppNodeName = "AppNode"
    drWebNodeName = "WebNode"
    drDBNodeName = "DBNode"
    gitCheckoutLocation = "/home/ubuntu"
    gitURL = "https://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@github.com/AppkubeCloud/appkube_drs_demo"
    gitRepoName = gitURL.split("/")
    gitCheckoutLocation = gitCheckoutLocation+"/"+gitRepoName[-1].split(".")[0]

    # Get pubic or private IPs for the required machines
    for i in describeInstance["Reservations"]:
        for instance in i["Instances"]:
            if instance["State"]["Name"] == "running" and "Tags" in instance:
                for tag in instance["Tags"]:
                    if tag["Key"] == "Name" and tag["Value"] == drWorkStationName:
                        drWorkStationPublicIP = instance["PublicIpAddress"]
                        continue
            if instance["State"]["Name"] == "running" and "Tags" in instance:
                for tag in instance["Tags"]:
                    if tag["Key"] == "Name" and tag["Value"] == drAppServerName:
                        drAppPrivateIP = instance["PrivateIpAddress"]
                        continue
            if instance["State"]["Name"] == "running" and "Tags" in instance:
                for tag in instance["Tags"]:
                    if tag["Key"] == "Name" and tag["Value"] == drDBServerName:
                        drDBPrivateIP = instance["PrivateIpAddress"]
                        continue
            if instance["State"]["Name"] == "running" and "Tags" in instance:
                for tag in instance["Tags"]:
                    if tag["Key"] == "Name" and tag["Value"] == drWebServerName:
                        drWebPrivateIP = instance["PrivateIpAddress"]
                        continue
    print("DR Workstation public IP: " + drWorkStationPublicIP)
    print("DR PetClinic-DB private IP: " + drDBPrivateIP)
    print("DR PetClinic-App private IP: " + drAppPrivateIP)
    print("DR PetClinic-Web private IP: " + drWebPrivateIP)

    # Create ssh client for drWorkStation
    s3_client.download_file("chefsyn1", "ec2keypair.pem", "/tmp/ec2keypair.pem")
    key = paramiko.RSAKey.from_private_key_file("/tmp/ec2keypair.pem")
    ssh_client_workstation = paramiko.SSHClient()
    ssh_client_workstation.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("Connecting to : " + drWorkStationPublicIP)
    ssh_client_workstation.connect(hostname=drWorkStationPublicIP, username="ubuntu", pkey=key)
    print("Connected to :" + drWorkStationPublicIP)

    # Generate commands with string builder
    cmd_DB_bootstrap = " ".join(["cd", gitCheckoutLocation, "&& knife bootstrap", drDBPrivateIP, "--ssh-user ubuntu --sudo -i /home/ubuntu/ec2keypair.pem -N",  drDBNodeName, "-y"])
   
    print("DB bootstrap cmd : " + cmd_DB_bootstrap)
    cmd_app_bootstrap = " ".join(["cd", gitCheckoutLocation, "&& knife bootstrap", drAppPrivateIP, "--ssh-user ubuntu --sudo -i /home/ubuntu/ec2keypair.pem -N", drAppNodeName, "-y"])
    
    print("App bootstrap cmd : " + cmd_app_bootstrap)
    cmd_web_bootstrap = " ".join(["cd", gitCheckoutLocation, "&& knife bootstrap", drWebPrivateIP, "--ssh-user ubuntu --sudo -i /home/ubuntu/ec2keypair.pem -N", drWebNodeName, "-y"])
    print("Web bootstrap cmd : " + cmd_web_bootstrap)
    
    #Chef config update after bootstrap
    cmd_chef_config = "".join(["sh ",  gitCheckoutLocation,"/chefconfig_init.sh ", gitCheckoutLocation, "> /tmp/chefconfig_init.log 2>&1"])
    print("add config script cron job : " + cmd_chef_config)

    #Cron job for cookbooks & config update
    cmd_cron_job = "".join(["""crontab -l && echo "*/5 * * * *  sh """, gitCheckoutLocation,"/chefconfig_sync.sh ",  gitCheckoutLocation, """ > /tmp/chefconfig_sync.log 2>&1" | sort -u | crontab -"""])
    print("add config script cron job : " + cmd_cron_job)

    #return {"statusCode": 200, "body": json.dumps("Bootstrap successful !")}
    bootstrapcommands = [
        cmd_DB_bootstrap,
        cmd_app_bootstrap,
        cmd_web_bootstrap,
        cmd_chef_config,
        cmd_cron_job
        ]

    # executing list of commands within server
    for command in bootstrapcommands:
        print("Executing {command}", command)
        stdin, stdout, stderr = ssh_client_workstation.exec_command(command)
        print(stdout.read())
        print(stderr.read())

    ssh_client_workstation.close()
    
    return {"statusCode": 200, "body": json.dumps("Bootstrap successful !")}