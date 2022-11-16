import boto3
import logging
from botocore.exceptions import ClientError

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
        # kwargs = {"username":username,"password":password,"engine":"postgres","host":host,"port":"5432","dbname":"posts","dbInstanceIdentifier":"w6pg1_rds"}
        # if isinstance(secret_value, str):
        #     kwargs["SecretString"] = secret_value
        # elif isinstance(secret_value, bytes):
        #     kwargs["SecretBinary"] = secret_value
        # response = client.create_secret(**kwargs)
        response = client.create_secret(Name = name,
                                        SecretString = '{"username":"%s","password":"%s","engine":"postgres","host":"%s","port":"5432","dbname":"posts","dbInstanceIdentifier":"w6pg1_rds"}' % (username, password, host))
        
        logger.info("Created secret %s.", name)
    except ClientError:
        logger.exception("Couldn't get secret %s.", name)
        raise
    else:
        return response

if __name__ == "__main__":
    #print(create("simo", "Salasana2", "arn:2321"))
    pass