import boto3
import logging
from botocore.exceptions import ClientError
import json
import time

logger = logging.getLogger(__name__)

def create_rds():
    db_identifier = 'w6pg1-rds-test6'
    rds = boto3.client('rds')
    data = get_secret_value("w6pg1_rds-test11")
    username = data["username"]
    password = data["password"]

    try:
        rds.create_db_instance(DBInstanceIdentifier=db_identifier,
                               AllocatedStorage=20,
                               DBName='blog',
                               Engine='postgres',
                               # General purpose SSD
                               StorageType='gp2',
                               StorageEncrypted=True,
                               AutoMinorVersionUpgrade=True,
                               # Set this to true later?
                               MultiAZ=False,
                               MasterUsername=username,
                               MasterUserPassword=password,
                               #VpcSecurityGroupIds=['YOUR_SECURITY_GROUP_ID'],
                               DBInstanceClass='db.t3.micro')
                               #Tags=[{'Key': 'MyTag', 'Value': 'Hawaii'}])
        print ("Starting RDS instance with ID: %s" % db_identifier)
    except ClientError as e:
        if 'DBInstanceAlreadyExists' in e.message:
            print ('DB instance %s exists already, continuing to poll ...' % db_identifier)
    finally:

        running = True
        while running:
            response = rds.describe_db_instances(DBInstanceIdentifier=db_identifier)

            db_instances = response['DBInstances']
            if len(db_instances) != 1:
                raise Exception('Whoa cowboy! More than one DB instance returned; this should never happen')

            db_instance = db_instances[0]

            status = db_instance['DBInstanceStatus']

            print ('Last DB status: %s' % status)

            time.sleep(5)
            if status == 'available':
                endpoint = db_instance['Endpoint']
                host = endpoint['Address']
                # port = endpoint['Port']

                print ('DB instance ready with host: %s' % host)
                running = False
        endpoint = db_instance['Endpoint']
        print(endpoint)
        #print(host)
        host = endpoint['Address']
        print(host)
        return host

def create_secret(username, password, host):
    """
    Creates a new secret. The secret value can be a string or bytes.

    :param name: The name of the secret to create.
    :param secret_value: The value of the secret.
    :return: Metadata about the newly created secret.
    """
    client = boto3.client("secretsmanager")
    name = "w6pg1_rds-secret"

    try:
        response = client.create_secret(Name = name,
                                        SecretString = '{"username":"%s","password":"%s","engine":"postgres","host":"%s","port":"5432","dbname":"blog","dbInstanceIdentifier":"w6pg1_rds"}' % (username, password, host))
        
        logger.info("Created secret %s.", name)
    except ClientError:
        logger.exception("Couldn't get secret %s.", name)
        raise
    else:
        return response

def get_secret_value(name):
        """
        Gets the value of a secret.

        :param stage: The stage of the secret to retrieve. If this is None, the
                      current stage is retrieved.
        :return: `SecretString` field as dictionary
        """
        client = boto3.client("secretsmanager")

        try:
            kwargs = {'SecretId': name}
            response = client.get_secret_value(**kwargs)
            logger.info("Got value for secret %s.", name)
        except ClientError:
            logger.exception("Couldn't get value for secret %s.", name)
            raise
        else:
            #return response
            return json.loads(response['SecretString'])

if __name__ == "__main__":
    #print(create_secret("simo", "Salasana2", "arn:2321"))
    #data = get_secret_value("w6pg1_rds-test11")
    # data = get_value("week5/group2/rds")
    # print(data)
    # data2 = json.loads(data['SecretString'])
    # print(data2['username'])
    #print(type(get_secret_value("w6pg1_rds-test11")))
    create_rds()
    pass