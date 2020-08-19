import boto3
import sys


def main():

    try:
        region = sys.argv[1]
        tag_name = sys.argv[2]
        tag_value = sys.argv[3]
    except:
        print ("Please privde a Region, EC2 ID, and an AutoScalingGroupName")
        return

    f = {
            'Name': 'tag:{0}'.format(tag_name),
            'Values': ['{0}'.format(tag_value)],
        }

    client = boto3.client('ec2', region_name=region,)
    response = client.describe_instances(
        Filters=[f],
    )

    r = response['Reservations'][0]

    instances = r['Instances']
    ips = []
    for i in instances:
        ips.append(i['PrivateIpAddress'])

    print (",".join(ips))

if __name__ == '__main__':
    main()
