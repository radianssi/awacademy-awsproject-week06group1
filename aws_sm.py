import boto3
import logging
from botocore.exceptions import ClientError
import json

logger = logging.getLogger(__name__)


def create(username, password, host):
    """
    Creates a new secret. The secret value can be a string or bytes.

    :param name: The name of the secret to create.
    :param secret_value: The value of the secret.
    :return: Metadata about the newly created secret.
    """
    client = boto3.client("secretsmanager")
    name = "w6pg1_rds-test11"

    try:
        response = client.create_secret(Name = name,
                                        SecretString = '{"username":"%s","password":"%s","engine":"postgres","host":"%s","port":"5432","dbname":"posts","dbInstanceIdentifier":"w6pg1_rds"}' % (username, password, host))
        
        logger.info("Created secret %s.", name)
    except ClientError:
        logger.exception("Couldn't get secret %s.", name)
        raise
    else:
        return response

def get_value(name):
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
        finally:
            #return response
            return json.loads(response['SecretString'])

if __name__ == "__main__":
    #print(create("simo", "Salasana2", "arn:2321"))
    #data = get_value("w6pg1_rds-test11")
    # data = get_value("week5/group2/rds")
    # print(data)
    # data2 = json.loads(data['SecretString'])
    # print(data2['username'])
    #print(type(get_value("w6pg1_rds-test11")))
    pass