import psycopg2
import boto3
import logging
from botocore.exceptions import ClientError
import json

logger = logging.getLogger(__name__)

def get_secret_value(name):   
        client = boto3.client("secretsmanager")

        try:
            kwargs = {'SecretId': name}
            response = client.get_secret_value(**kwargs)
            logger.info("Got value for secret %s.", name)
        except ClientError:
            logger.exception("Couldn't get value for secret %s.", name)
            raise
        else:
            return json.loads(response['SecretString'])

def get_db_connection():
    data = get_secret_value("w6pg1_rds-test11")
    conn = psycopg2.connect("host=%s dbname=%s port=%s user=%s password=%s" % (data['host'], data['dbname'], data['port'], data['username'], data['password']))
    return conn

def do_init():
    connection = get_db_connection()
    cur = connection.cursor()
    #connection = sqlite3.connect('database.db')

    #with open('schema.sql') as f:
        #connection.executescript(f.read())

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

if __name__ == "__main__":
    do_init()
