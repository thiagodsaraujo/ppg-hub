import psycopg2

class DatabaseTester:
    def __init__(self, host, port, dbname, user, password):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password

    def test_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            print("Conexão bem-sucedida!")
            conn.close()
            return True
        except Exception as e:
            print("Erro ao conectar ao banco de dados:")
            print(e)
            return False

    def list_schemas(self):
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            with conn.cursor() as cur:
                cur.execute("SELECT schema_name FROM information_schema.schemata;")
                schemas = [row[0] for row in cur.fetchall()]
                print("Schemas disponíveis:", schemas)
            conn.close()
            return schemas
        except Exception as e:
            print("Erro ao listar schemas:")
            print(e)
            return []

def get_tester():
    return DatabaseTester(
        host='148.230.76.86',
        port='5433',
        dbname='ppghub_dev',
        user='postgres',
        password='NIgBA3LQgmXTanJ8GjDewwOob5vxk8yJLkPgv1pa823mHhM9ovbtKFh4qMUP8WpF'
    )

def test_connection():
    tester = get_tester()
    assert tester.test_connection() is True

def test_list_schemas():
    tester = get_tester()
    schemas = tester.list_schemas()
    assert isinstance(schemas, list)
    assert "public" in schemas  # espera-se que o schema 'public' exista

if __name__ == "__main__":
    tester = DatabaseTester(
        host='148.230.76.86',
        port='5433',
        dbname='ppghub_dev',
        user='postgres',
        password='NIgBA3LQgmXTanJ8GjDewwOob5vxk8yJLkPgv1pa823mHhM9ovbtKFh4qMUP8WpF/ppghub_dev'
    )
    tester.test_connection()
    tester.list_schemas()
