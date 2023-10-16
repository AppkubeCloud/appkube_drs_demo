import json
import boto3

def lambda_handler(event, context):
    # Boto3 client
    ec2_client = boto3.client("ec2")

    # Getting instance information
    describe_instances = ec2_client.describe_instances()

    # Initialize instance IDs
    drWorkStationInstanceId = ""
    drAppInstanceId = ""
    drDBInstanceId = ""
    drWebInstanceId = ""
    instance_ids_to_associate = []
    # Get instance IDs for the required instances
    for reservation in describe_instances["Reservations"]:
        for instance in reservation["Instances"]:
            if instance["State"]["Name"] == "running" and "Tags" in instance:
                for tag in instance["Tags"]:
                    if tag["Key"] == "Name":
                        if tag["Value"] == "Dr-Chef-Workstation":
                            drWorkStationInstanceId = instance["InstanceId"]
                        elif tag["Value"] == "PetClinic-App":
                            drAppInstanceId = instance["InstanceId"]
                        elif tag["Value"] == "PetClinic-DB":
                            drDBInstanceId = instance["InstanceId"]
                        elif tag["Value"] == "PetClinic-Web":
                            drWebInstanceId = instance["InstanceId"]

    # Now you have the instance IDs for the required instances
    instance_ids_to_associate.append(drAppInstanceId)
    instance_ids_to_associate.append(drDBInstanceId)
    instance_ids_to_associate.append(drWebInstanceId)

    print(f"Workstation Instance ID: {drWorkStationInstanceId}")
    print(f"DB Instance ID: {drDBInstanceId}")
    print(f"Web Instance ID: {drWebInstanceId}")
    print(f"App Instance ID: {drAppInstanceId}")
    print(instance_ids_to_associate)
    for instance_id in instance_ids_to_associate:
        try:
            response = ec2_client.associate_iam_instance_profile(
                IamInstanceProfile={
                    'Arn': 'arn:aws:iam::657907747545:instance-profile/iampassrole'
                },
                InstanceId=instance_id
            )

            print(f"Associated IAM instance profile with instance ID: {instance_id}")
        except Exception as e:
            print(f"Error associating IAM instance profile with instance ID {instance_id}: {str(e)}")

    return {
        'statusCode': 200,
        'body': json.dumps('IAM instance profile association completed for running instances.')
    }