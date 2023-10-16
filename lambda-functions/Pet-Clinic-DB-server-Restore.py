import uuid
import boto3

 

def lambda_handler(event, context):
    # Initialize the AWS Backup client
    backup_client = boto3.client("backup")

    # Define the parameters for the restore job
    restore_params = {
        "RecoveryPointArn": "arn:aws:ec2:us-west-1::image/ami-08c9fec91534a45e4",
        "Metadata": {
            "VPCId": "vpc-0d5d6aff345974479",
            "SubnetId": "subnet-08223abd186c8a58f", ##### this subnet have auto assing public ip #####
            # "SecurityGroupIds": "sg-0b54a23613da50bd2",
            "InstanceType": "t2.medium",
            # Add more metadata as needed
        },
        "IamRoleArn": "arn:aws:iam::657907747545:role/service-role/AWSBackupDefaultServiceRole",
        "IdempotencyToken": str(uuid.uuid4()),
        "ResourceType": "EC2",
        "CopySourceTagsToRestoredResource": True,
    }


    # Start the restore job
    response = backup_client.start_restore_job(**restore_params)

    return {"statusCode": 200, "body": response}
    