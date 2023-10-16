# script for git clone & updating recipe attributes

import json
import paramiko
import boto3

def lambda_handler(event, context):
    # boto3 client
    client = boto3.client("ec2")
    s3_client = boto3.client("s3")

    # getting instance information
    describeInstance = client.describe_instances()
    
    # Initialize all required variables
    drWorkStationPublicIP = ""
    drAppPublicIP = ""
    drDBPublicIP = ""
    drWorkStationName = "Dr-ChefWorkstation"
    drAppServerName = "PetClinic-App" 
    drDBServerName = "PetClinic-DB"
    drWebServerName = "PetClinic-Web"
    gitCheckoutLocation = "/home/ubuntu"
    gitURL = "https://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@github.com/AppkubeCloud/appkube_drs_demo"
    gitRepoName = gitURL.split("/")
    gitCheckoutLocation = gitCheckoutLocation+"/"+gitRepoName[-1].split(".")[0]

    # Location of databags
    dbDataBagFile = "/".join([gitCheckoutLocation, "data_bags", "drconfigbag", "dbconfig_items.json"])
    appDataBagFile = "/".join([gitCheckoutLocation, "data_bags", "drconfigbag", "appconfig_items.json"])
    webDataBagFile = "/".join([gitCheckoutLocation, "data_bags", "drconfigbag", "webconfig_items.json"])
    print("dbDataBagFile: " + dbDataBagFile)
    print("appDataBagFile: " + appDataBagFile)
    print("webDataBagFile: " + webDataBagFile)

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
                        drAppPublicIP = instance["PublicIpAddress"]
                        continue
            if instance["State"]["Name"] == "running" and "Tags" in instance:
                for tag in instance["Tags"]:
                    if tag["Key"] == "Name" and tag["Value"] == drDBServerName:
                        drDBPublicIP = instance["PublicIpAddress"]
                        continue
    print("DR Workstation public IP: " + drWorkStationPublicIP)
    print("DR PetClinic-App public IP: " + drAppPublicIP)
    print("DR PetClinic-DB public IP: " + drDBPublicIP)

    # downloading pem filr from S3
    s3_client.download_file("chefsyn1", "ec2keypair.pem", "/tmp/ec2keypair.pem")
    # reading pem file and creating key object
    key = paramiko.RSAKey.from_private_key_file("/tmp/ec2keypair.pem")
    # an instance of the Paramiko.SSHClient
    ssh_client_workstation = paramiko.SSHClient()
    # setting policy to connect to unknown host
    ssh_client_workstation.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("Connecting to : " + drWorkStationPublicIP)
    # connecting to server
    ssh_client_workstation.connect(hostname=drWorkStationPublicIP, username="ubuntu", pkey=key)
    print("Connected to :" + drWorkStationPublicIP)

    # command list
    cmd_git_clone = " ".join(["git clone", gitURL])
    print("Git clone command : " + cmd_git_clone)
    
    cmd_authentcate = " ".join(["git", "remote", "set-url", "origin", gitURL])

    # Change IP in data bags
    cmd_update_dbconfigdatabag = "".join(["""sed -i 's/.*"DB_host".*/""",
            """    "DB_host": \"""",
            drDBPublicIP,
            """\",/' """,
            dbDataBagFile])
    print("cmd_update_dbconfigdatabag: " + cmd_update_dbconfigdatabag)
    cmd_update_appconfigdatabag = "".join(["""sed -i 's/.*"APP_host".*/""",
            """    "APP_host": \"""",
            drAppPublicIP,
            """\"/' """,
            appDataBagFile])
    print("cmd_update_appconfigdatabag: " + cmd_update_appconfigdatabag)
    
    
    workstationInitCommands = [
        cmd_git_clone,
        cmd_authentcate,
        cmd_update_dbconfigdatabag,
        cmd_update_appconfigdatabag
        ]

    #executing list of commands within server
    for command in workstationInitCommands:
        print("Executing {command}", command)
        stdin, stdout, stderr = ssh_client_workstation.exec_command(command)
        print(stdout.read())
        print(stderr.read())
    
    return {
        'statusCode': 200,
        'body': json.dumps('Git cloned and attributes updated')
    }
