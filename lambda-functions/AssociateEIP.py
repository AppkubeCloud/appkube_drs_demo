import json
import boto3

def associate_existing_eip_with_instance_tags(ec2_client, elastic_ip, tag_key, tag_value):
    try:
        # Get the instance ID for the required instance with the specified tag key and value
        response = ec2_client.describe_instances(Filters=[
            {
                'Name': f'tag:{tag_key}',
                'Values': [tag_value]
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ])

        # Extract the instances from the response
        instances = response.get('Reservations', [])

        if instances:
            instance = instances[0]['Instances'][0]
            DBInstanceId = instance.get('InstanceId', '')

            # Associate the existing Elastic IP with the instance
            ec2_client.associate_address(
                InstanceId=DBInstanceId,
                PublicIp=elastic_ip
            )

            print(f"Associated Elastic IP {elastic_ip} with instance {DBInstanceId} (Tag Key: {tag_key}, Tag Value: {tag_value})")

    except Exception as e:
        print(f"Error: {str(e)}")
        return{"statusCode": 424, "body": json.dumps({"message": "Elastic IP not allocated or Either in use"})}

def lambda_handler(event, context):
    # Create an EC2 client
    ec2_client = boto3.client("ec2")

    # Elastic IPs and their corresponding tags
    elastic_ips_and_tags = {
        "54.151.123.242": {"tag_key": "Name", "tag_value": "PetClinic-DB"},
        "50.18.115.83": {"tag_key": "Name", "tag_value": "PetClinic-App"},
        "54.151.76.213": {"tag_key": "Name", "tag_value": "PetClinic-Web"}
    }

    for elastic_ip, tag_info in elastic_ips_and_tags.items():
        tag_key = tag_info["tag_key"]
        tag_value = tag_info["tag_value"]
        associate_existing_eip_with_instance_tags(ec2_client, elastic_ip, tag_key, tag_value)

    # Return a JSON response indicating completion
    return {"statusCode": 200, "body": json.dumps({"message": "Elastic IPs associated with tags"})}
