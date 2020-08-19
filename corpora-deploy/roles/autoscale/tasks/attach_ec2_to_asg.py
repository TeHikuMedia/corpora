import boto3
import sys


def main():

    try:
        region = sys.argv[1]
        ec2 = sys.argv[2]
        asg = sys.argv[3]
    except:
        print ("Please privde a Region, EC2 ID, and an AutoScalingGroupName")
        return

    print (region, ec2, asg)

    client = boto3.client('autoscaling', region_name=region,)

    response = client.attach_instances(
        AutoScalingGroupName=asg,
        InstanceIds=[
            ec2,
        ],
    )

    print(response)


if __name__ == '__main__':
    main()
