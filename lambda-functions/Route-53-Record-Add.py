import json
import boto3
import paramiko


def lambda_handler(event, context):

    HOSTED_ZONE_ID = "ZY8RNBR15YWYU"
    client = boto3.client("ec2")
    route53 = boto3.client("route53")

    # getting instance information
    describeInstance = client.describe_instances()

    # Initialize all required variables
    drWebPublicIP = ""
    drWebServerName = "PetClinic-Web"


    # Get pubic or private IPs for the required machines
    for i in describeInstance["Reservations"]:
        for instance in i["Instances"]:
            if instance["State"]["Name"] == "running" and "Tags" in instance:
                for tag in instance["Tags"]:
                    if tag["Key"] == "Name" and tag["Value"] == drWebServerName:
                        if "PublicIpAddress" in instance:
                            drWebPublicIP = instance["PublicIpAddress"]
                        continue
    if not drWebPublicIP:
        print("Error finding WebServerPublicIP")
        return {"statusCode": 500, "body": json.dumps({"message": "Error finding WebServerPublicIP"})}
    print("DR PetClinic-Web public IP: " + drWebPublicIP)
    
    #Create record set dr-web1.synectiks.net
    dns_changes={
        "Changes": [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": "dr-web1.synectiks.net",
                    "ResourceRecords": [
                        {
                            "Value": drWebPublicIP
                        },
                    ],
                    "TTL": 300,
                    "Type": "A",
                },
            },
        ],
        "Comment": "Web Server"
    }
    print("Updating Route53 for DR Web1:")
    response = route53.change_resource_record_sets(
        HostedZoneId=HOSTED_ZONE_ID,
        ChangeBatch=dns_changes
    )

    #Update record set to web1.synectick.net
    dns_changes={
        "Changes": [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": "web1.synectiks.net",
                    "ResourceRecords": [
                        {
                            "Value": drWebPublicIP
                        },
                    ],
                    "TTL": 300,
                    "Type": "A",
                },
            },
        ],
        "Comment": "Web Server"
    }
    
    # print(dns_changes)
    # return {"statusCode": 200, "body": json.dumps(dns_changes)}

    print("Updating Route53 for Web1:")
    response = route53.change_resource_record_sets(
        HostedZoneId=HOSTED_ZONE_ID,
        ChangeBatch=dns_changes
    )

    return {'status':response['ChangeInfo']['Status']}