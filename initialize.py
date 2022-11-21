from aws import create_security_group_for_rds, create_rds, create_secret, create_posts_table, add_default_topics_to_db
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("username", help="Give username", type=str)
parser.add_argument("password", help="Give password", type=str)
parser.add_argument("region", help="Give AWS region i.e. eu-central-1", type=str)
args = parser.parse_args()

username = args.username
password = args.password
region = args.region

def main():
    try:
        # Create security group for RDS and return its id
        sg_id = create_security_group_for_rds(region)
    except:
        print("Well, something went wrong with SG...")  

    try:
        # Create RDS and return its host
        rds_host = create_rds(username, password, sg_id, region)
    except:
        print("Well, something went wrong with RDS...")  

    try:
        # Create Secret to SecretsManager
        if create_secret(username, password, rds_host, region):
            print("Secret created successfully")
    except:
        print("Well, something went wrong with SecretsManager...")  

    try:
        # Create table to RDS database
        if create_posts_table(region):
            print("Table created successfully")
        else:
            print("Something went wrong with create table")
    except:
        print("Well, something went wrong with creating table in RDS...")    

    try:
        # Insert test data to table
        if add_default_topics_to_db(region):
            print("Data inserted successfully")
        else:
            print("Something went wrong with insert data")
    except:
        print("Well, something went wrong wit add defaults topics...")

if __name__ == "__main__":
    main()