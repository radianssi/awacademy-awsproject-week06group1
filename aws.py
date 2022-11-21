import boto3
import logging
from botocore.exceptions import ClientError
import json
import time
import psycopg2

logger = logging.getLogger(__name__)

#myregion = "ap-southeast-2"

def create_security_group_for_rds(myregion):
    ec2 = boto3.client('ec2', region_name=myregion)

    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

    try:
        response = ec2.create_security_group(GroupName='w6pg1_rds_sg',
                                            Description='Security Group for RDS',
                                            VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

        data = ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                'FromPort': 5432,
                'ToPort': 5432,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])
        print('Ingress Successfully Set %s' % data)
        return security_group_id
    except ClientError as e:
        print(e)
        

def create_rds(username, password, sg_id, myregion):
    db_identifier = 'w6pg1-rds'
    rds = boto3.client('rds', region_name=myregion)

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
                               VpcSecurityGroupIds=[sg_id],
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

            time.sleep(10)
            if status == 'available':
                endpoint = db_instance['Endpoint']
                host = endpoint['Address']
                # port = endpoint['Port']

                print ('DB instance ready with host: %s' % host)
                running = False
        #endpoint = db_instance['Endpoint']
        #host = endpoint['Address']
        return host


def create_secret(username, password, host, myregion):
    """
    Creates a new secret. The secret value can be a string or bytes.

    :param name: The name of the secret to create.
    :param secret_value: The value of the secret.
    :return: Metadata about the newly created secret.
    """
    client = boto3.client("secretsmanager", region_name=myregion)
    name = "w6pg1_rds-secret"

    try:
        response = client.create_secret(Name = name,
                                        SecretString = '{"username":"%s","password":"%s","engine":"postgres","host":"%s","port":"5432","dbname":"blog","dbInstanceIdentifier":"w6pg1-rds"}' % (username, password, host))
        
        logger.info("Created secret %s.", name)
    except ClientError:
        logger.exception("Couldn't get secret %s.", name)
        raise
    else:
        return True

def get_secret_value(name, myregion):
        client = boto3.client("secretsmanager", region_name=myregion)

        try:
            kwargs = {'SecretId': name}
            response = client.get_secret_value(**kwargs)
            logger.info("Got value for secret %s.", name)
        except ClientError:
            logger.exception("Couldn't get value for secret %s.", name)
            raise
        else:
            return json.loads(response['SecretString'])

def get_db_connection(myregion):
    data = get_secret_value("w6pg1_rds-secret", myregion)
    conn = psycopg2.connect("host=%s dbname=%s port=%s user=%s password=%s" % (data['host'], data['dbname'], data['port'], data['username'], data['password']))
    return conn

def create_posts_table(myregion):
    try:
        connection = get_db_connection(myregion)
        cur = connection.cursor()
        try:
            cur.execute("""
            CREATE TABLE posts (
            id SERIAL PRIMARY KEY,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            title TEXT NOT NULL,
            content TEXT NOT NULL);
            """)
        except:
            print("No working command")
        connection.commit()
        connection.close()
        return True
    except:
        return False

def add_default_topics_to_db(myregion):
    try:
        connection = get_db_connection(myregion)
        cur = connection.cursor()

        cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s)",
                    ('Jämähditkö? Tee kuten Heidi ja muuta urasi suuntaa', 'Jokaisen maanantain ei tarvitse olla nousukiitoa, mutta jos perjantaihin mennessä ei sorvin ääressä ole juuri ilon tai innostumisen kokemuksia irronnut, ollaan lähellä jämähtämistä. Oireet on helppo tunnistaa ja hoito on jokaisen ulottuvilla – uranvaihto ei katso taustaa eikä vaadi vuosien opiskelua.')
                    )

        cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s)",
                    ('Tradenomista IT-ammattilaiseksi: Ilkan tarina', """Kansainvälisen kaupan tradenomiksi valmistunut ja useita vuosia työuraa LVI-alalla rakentanut Ilkka Jokela hyppäsi Academyn kiihdytyskaistalle saatuaan kipinän koodiin.

    “Olin jo päättänyt, että haluan koodata ja kouluttautua IT-alalle. Hain ja pääsinkin yliopistoon lukemaan tietotekniikkaa. Huomasin kuitenkin Academyn, joten en ottanut opiskelupaikkaa vastaan. Olen aina ollut kiinnostunut teknologiasta ja haluan tehdä jotain, mikä on tätä päivää”, Ilkka avaa omaa polkuaan.

    Muiden academylaisten tyyliin myös Ilkalle halu ja kyky oppia uutta on luontaista. Ilkka painottaakin, että “uuden oppiminen on upeaa, ja varsinkin se fiilis, kun on ihan pihalla. Se samanaikaisesti sekä turhauttaa että antaa nautintoa, koska tietää että nyt oppii varmasti jotakin uutta.”

    Ilkka muistelee jännittäneensä Academyn intensiivistä prässiä enemmän kuin oli syytä. 12 viikkoa meni nopeasti ja uusia oppeja tuli ennalta-arvaamaton määrä. Koulutuksen paras anti meni kuitenkin pelkkää tietoa syvemmälle.

    “Parasta Academyssa oli ehdottomasti porukan yhteishenki sekä mahtavat opettajat. Käteen koulutuksesta jäi ennen kaikkea tieto siitä, että mitä vain voi oppia, kun on halu oppia.”""")
                    )

        cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s)",
                    ('Tätä haluat kysyä AW Academysta ja uranvaihdosta', """Uudenlaisen koulutusmallin saapuminen Suomeen on herättänyt vuosien varrella keskustelua ja kirvoittanut kysymyksiä. Kokosimme tähän blogikirjoitukseen muutamia verkkokeskusteluissa (mm. Helsingin Sanomat, Taloussanomat) esiintyneitä kysymyksiä ja vastauksia.""")
                    )

        cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s)",
                    ('Kaiken takana on koodi – ja sen voi oppia 12 viikossa', """Miten koodi pyörittää maailmaa? Ja miten sen oppiminen 12 viikon intensiivikoulutuksessa on mahdollista? IT-konsulttina ja -kouluttajana työskentelevä Tommi Teräsvirta kertoo.

    Tietokoneet ja niiden käyttämä kieli on muuttanut maailmaamme käsittämättömän paljon kohtuullisen pienessä ajassa. Jos kuka tahansa saisi kyydin aikakoneella 30 vuoden takaa nykypäivään, jäisi aikamatkustajan suu taatusti auki monessa arkisessa kohtaamisessa 2019-luvun alkuasukkaan kanssa.

    Koodi on yksi käytetyimmistä ja arkemme kannalta vaikuttavimmista kielistä. Sen osaamisesta on pelkästään hyötyä ja sen osaajille on työmarkkinoilla jatkuvaa tilausta.

    Academyn 12 viikon ja vakituisen työpaikan Academic Workin asiakasyrityksen palveluksessa takaavan koodauskoulutusohjelman opettaja Tommi Teräsvirta Sovellolta osaa avata tämän kiehtovan kielen sekä sen oppimisen saloja syvemmin.""")
                    )

        connection.commit()
        connection.close()
        return True
    except:
        return False
    



if __name__ == "__main__":
    #print(create_secret("simo", "Salasana2", "arn:2321"))
    #data = get_secret_value("w6pg1_rds-test11")
    # data = get_value("week5/group2/rds")
    #print(data)
    # data2 = json.loads(data['SecretString'])
    # print(data2['username'])
    #print(type(get_secret_value("w6pg1_rds-test11")))
    #create_rds()
    #create_security_group_for_rds("ap-south-1")
    #create_rds("basso", "bassomarsu", "sg-00919eef68055e0b8", "ap-south-1")
    create_posts_table()
    pass