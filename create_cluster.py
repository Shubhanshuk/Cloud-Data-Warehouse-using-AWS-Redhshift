import pandas as pd
import boto3
import json
import configparser

'''
Load DWH Params from a file
'''
config = configparser.ConfigParser()
config.read_file(open('dwh.cfg'))

KEY                    = config.get('AWS','KEY')
SECRET                 = config.get('AWS','SECRET')

DWH_CLUSTER_TYPE       = config.get("DWH","DWH_CLUSTER_TYPE")
DWH_NUM_NODES          = config.get("DWH","DWH_NUM_NODES")
DWH_NODE_TYPE          = config.get("DWH","DWH_NODE_TYPE")

DWH_CLUSTER_IDENTIFIER = config.get("DWH","DWH_CLUSTER_IDENTIFIER")
DWH_DB                 = config.get("CLUSTER","DB_NAME")
DWH_DB_USER            = config.get("CLUSTER","DB_USER")
DWH_DB_PASSWORD        = config.get("CLUSTER","DB_PASSWORD")
DWH_PORT               = config.get("CLUSTER","DB_PORT")

DWH_IAM_ROLE_NAME      = config.get("DWH", "DWH_IAM_ROLE_NAME")

(DWH_DB_USER, DWH_DB_PASSWORD, DWH_DB)

pd.DataFrame(
{
"Param": ["DWH_CLUSTER_TYPE", 
          "DWH_NUM_NODES", 
          "DWH_NODE_TYPE", 
          "DWH_CLUSTER_IDENTIFIER", 
          "DWH_DB", 
          "DWH_DB_USER", 
          "DWH_DB_PASSWORD", 
          "DWH_PORT", 
          "DWH_IAM_ROLE_NAME"], 
    
"Value": [DWH_CLUSTER_TYPE, 
         DWH_NUM_NODES, 
         DWH_NODE_TYPE, 
         DWH_CLUSTER_IDENTIFIER, 
         DWH_DB, 
         DWH_DB_USER, 
         DWH_DB_PASSWORD,
         DWH_PORT, 
         DWH_IAM_ROLE_NAME]
}

)


'''
Create clients for EC2, S3, IAM, and Redshift
'''



s3 = boto3.resource (
                        's3',
                         region_name='us-west-2',
                         aws_access_key_id=KEY,
                         aws_secret_access_key=SECRET

                    )

iam = boto3.client (
                        'iam',
                         region_name='us-west-2',
                         aws_access_key_id=KEY,
                         aws_secret_access_key=SECRET

                    )

redshift = boto3.client (
                        'redshift',
                         region_name='us-west-2',
                         aws_access_key_id=KEY,
                         aws_secret_access_key=SECRET

                    )

'''
Create an IAM Role that makes Redshift able to access S3 bucket (ReadOnly)
'''
from botocore.exceptions import ClientError

# TODO: Create the IAM role
try:
    print('1.1 Creating a new IAM Role')
    dwhRole = iam.create_role(

        RoleName=DWH_IAM_ROLE_NAME,
        Description="Allows redshift clusters to call AWS services on your behalf",
        AssumeRolePolicyDocument=json.dumps(
            {'Statement': [{'Action': 'sts:AssumeRole',
                            'Effect': 'Allow',
                            'Principal': {'Service': 'redshift.amazonaws.com'}}],
             'Version': '2012-10-17'}))

except Exception as e:
    print(e)

print("1.2 Attaching Policy")

iam.attach_role_policy(RoleName=DWH_IAM_ROLE_NAME,
                       PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
                       )['ResponseMetadata']['HTTPStatusCode']

print("1.3 Get the IAM role ARN")
roleArn = iam.get_role(RoleName=DWH_IAM_ROLE_NAME)['Role']['Arn']

print(roleArn)


'''
STEP 2: Redshift Cluster
Create a RedShift Cluster
For complete arguments to create_cluster, see docs
'''

try:
    response = redshift.create_cluster(
        # HW
        ClusterType=DWH_CLUSTER_TYPE,
        NodeType=DWH_NODE_TYPE,
        NumberOfNodes=int(DWH_NUM_NODES),

        # Identifiers & Credentials
        DBName=DWH_DB,
        ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,
        MasterUsername=DWH_DB_USER,
        MasterUserPassword=DWH_DB_PASSWORD,

        # Roles (for s3 access)
        IamRoles=[roleArn]
    )
except Exception as e:
    print(e)


'''
2.1 Describe the cluster to see its status
run this block several times until the cluster status becomes Available
'''
def prettyRedshiftProps(props):
    pd.set_option('display.max_colwidth', -1)
    keysToShow = ["ClusterIdentifier", "NodeType", "ClusterStatus", "MasterUsername", "DBName", "Endpoint", "NumberOfNodes", 'VpcId']
    x = [(k, v) for k,v in props.items() if k in keysToShow]
    return pd.DataFrame(data=x, columns=["Key", "Value"])

myClusterProps = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
prettyRedshiftProps(myClusterProps)
print(myClusterProps)

'''
2.2 Take note of the cluster endpoint and role ARN 
DO NOT RUN THIS unless the cluster status becomes "Available"
'''
DWH_ENDPOINT = myClusterProps['Endpoint']['Address']
DWH_ROLE_ARN = myClusterProps['IamRoles'][0]['IamRoleArn']
print("DWH_ENDPOINT :: ", DWH_ENDPOINT)
print("DWH_ROLE_ARN :: ", DWH_ROLE_ARN)


'''
STEP 3: Open an incoming TCP port to access the cluster end point

try:
    vpc = ec2.Vpc(id=myClusterProps['VpcId'])
    defaultSg = list(vpc.security_groups.all())[0]
    print(defaultSg)

    defaultSg.authorize_ingress(
        GroupName=defaultSg.group_name,  #
        CidrIp='0.0.0.0/0',  #
        IpProtocol='TCP',  #
        FromPort=int(DWH_PORT),
        ToPort=int(DWH_PORT)
    )
except Exception as e:
    print(e)


STEP 4: Make sure you can connect to the clusterConnect to the cluster

%load_ext sql
conn_string="postgresql://{}:{}@{}:{}/{}".format(DWH_DB_USER, DWH_DB_PASSWORD, DWH_ENDPOINT, DWH_PORT,DWH_DB)
print(conn_string)
%sql $conn_string
'''
'''
STEP 5: Clean up your resources
'''

'''

#### CAREFUL!!
#-- Uncomment & run to delete the created resources
redshift.delete_cluster( ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,  SkipFinalClusterSnapshot=True)
#### CAREFUL!!

myClusterProps = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
prettyRedshiftProps(myClusterProps)

#### CAREFUL!!
#-- Uncomment & run to delete the created resources
iam.detach_role_policy(RoleName=DWH_IAM_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
iam.delete_role(RoleName=DWH_IAM_ROLE_NAME)
#### CAREFUL!!
'''