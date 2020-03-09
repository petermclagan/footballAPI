import pyodbc
import pytest
import sqlalchemy
from sqlalchemy.types import INT, VARCHAR
from sqlalchemy.orm.session import sessionmaker
from typing import Dict, List, Union

from footballAPI import SECRETS
from footballAPI.tools.micro_alchemy import MicroAlchemy

DATABASE = SECRETS['DATABASE']
DRIVER = SECRETS['DRIVER']
PASSWORD = SECRETS['PASSWORD']
SERVER = SECRETS['SERVER']
USERNAME = SECRETS['USERNAME']

sql = MicroAlchemy(server=SERVER,
                   database=DATABASE,
                   username=USERNAME,
                   password=PASSWORD,
                   driver=DRIVER)

connection = pyodbc.connect(f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}',
                            autocommit=True)
cursor = connection.cursor()


class TestMicroAlchemy:

    @classmethod
    def setup_class(cls):
        cursor.execute("CREATE SCHEMA testing")
        cursor.execute(
            "CREATE TABLE testing.test_table (col1 INT, col2 VARCHAR(5))")
        cursor.execute(
            "INSERT INTO testing.test_table VALUES (1, 'one'),(2, 'two')")
        return

    @classmethod
    def teardown_class(cls):
        cursor.execute("DROP TABLE testing.test_table")
        cursor.execute("DROP SCHEMA testing")
        return

    def setup_method(self):
        return

    def teardown_method(self):
        cursor.execute("DROP SCHEMA IF EXISTS testing_create_schema")
        cursor.execute("DROP TABLE IF EXISTS testing.test_creation")
        cursor.execute("DROP TABLE IF EXISTS testing.test_creation1")
        cursor.execute("DROP TABLE IF EXISTS testing.test_creation2")
        return

    def check_schemas(self) -> List[str]:
        cursor.execute("SELECT * FROM sys.schemas")
        all_schemas = list()
        for row in cursor.fetchall():
            all_schemas.append(row[0])
        return all_schemas

    def check_tables_in_schema(self, schema: str):
        cursor.execute(f"""SELECT 
                          * 
                          FROM {DATABASE}.INFORMATION_SCHEMA.tables 
                          WHERE table_schema = \'{schema}\'
                      """)
        tables_in_schema = list()
        for row in cursor.fetchall():
            tables_in_schema.append(row[2])
        return tables_in_schema

    def single_table(self) -> sqlalchemy.Table:
        table = sqlalchemy.Table('test_creation',
                                 sqlalchemy.MetaData(),
                                 sqlalchemy.Column('col1', INT),
                                 sqlalchemy.Column('col2', VARCHAR(25)),
                                 schema='testing')
        return table

    def multiple_tables(self) -> List[sqlalchemy.Table]:
        table1 = sqlalchemy.Table('test_creation1',
                                  sqlalchemy.MetaData(),
                                  sqlalchemy.Column('col1', INT),
                                  sqlalchemy.Column('col2', VARCHAR(25)),
                                  schema='testing')
        table2 = sqlalchemy.Table('test_creation2',
                                  sqlalchemy.MetaData(),
                                  sqlalchemy.Column('col1', INT),
                                  sqlalchemy.Column('col2', VARCHAR(25)),
                                  schema='testing')
        tables = [table1, table2]
        return tables

    def single_spec(self) -> Dict[str, Union[str, List[sqlalchemy.Column]]]:
        table_spec = {'table_name': 'test1',
                      'schema': 'testing',
                      'columns': [sqlalchemy.Column('c1', INT),
                                  sqlalchemy.Column('c2', VARCHAR(10))]}
        return table_spec

    def multiple_specs(self) -> List[Dict[str, Union[str, List[sqlalchemy.Column]]]]:
        schema_spec1 = {'table_name': 'table_list1',
                        'schema': 'testing',
                        'columns': [sqlalchemy.Column('one', INT)]}
        schema_spec2 = {'table_name': 'table_list2',
                        'schema': 'testing',
                        'columns': [sqlalchemy.Column('two', INT)]}
        schema_specs = [schema_spec1, schema_spec2]
        return schema_specs

    def test_table(self):
        table_specs = self.single_spec()
        table = sql.table(table_specs)
        assert table.name == 'test1'
        assert table.schema == 'testing'
        assert type(table) == sqlalchemy.Table
        assert type(table.c.c1.type) == sqlalchemy.sql.sqltypes.INTEGER
        assert type(table.c.c2.type) == sqlalchemy.types.VARCHAR
        return

    def test_create_schema_with_no_execute(self):
        schema_name = 'testing_create_schema_no_execute'
        sql.create_schema(schema_name=schema_name,
                          execute=False)
        all_schemas = self.check_schemas()
        assert schema_name not in all_schemas
        return

    def test_create_schema_with_execute(self):
        schema_name = 'testing_create_schema'
        sql.create_schema(schema_name=schema_name,
                          execute=True)
        all_schemas = self.check_schemas()
        assert schema_name in all_schemas
        return

    def test_tables_list(self):
        schema_specs = self.multiple_specs()
        tables = sql.tables_list(schema_specs)
        assert len(tables) == 2
        assert tables[0].name == 'table_list1'
        assert tables[1].name == 'table_list2'
        assert tables[0].schema == tables[1].schema == 'testing'
        assert type(tables[0]) == type(tables[1]) == sqlalchemy.Table
        assert type(tables[0].c.one.type) == type(
            tables[1].c.two.type) == sqlalchemy.types.INTEGER
        return

    def test_create_single_table(self):
        table = self.single_table()
        sql.create_tables([table])
        existing_tables = self.check_tables_in_schema('testing')
        assert table.name in existing_tables
        return

    def test_create_multiple_tables(self):
        table_list = self.multiple_tables()
        sql.create_tables(table_list)
        existing_tables = self.check_tables_in_schema('testing')
        assert table_list[0].name in existing_tables
        assert table_list[1].name in existing_tables
        return

    def test_drop_multiple_tables(self):
        table_list = self.multiple_tables()
        sql.create_tables(table_list)
        sql.drop_tables(table_list, testing=True)
        existing_tables = self.check_tables_in_schema('testing')
        assert table_list[0].name not in existing_tables
        assert table_list[1].name not in existing_tables
        return

    def test_querying_a_table(self):
        table = sqlalchemy.Table('test_table',
                                 sqlalchemy.MetaData(),
                                 sqlalchemy.Column('col1', INT),
                                 sqlalchemy.Column('col2', VARCHAR(5)),
                                 schema='testing')
        session = sql.Session()
        rows = session.query(table).all()
        assert rows == [(1, 'one'), (2, 'two')]
        session.close()
        return

    def test_insert_values_with_execute(self):
        table = sqlalchemy.Table('test_table',
                                 sqlalchemy.MetaData(),
                                 sqlalchemy.Column('col1', INT),
                                 sqlalchemy.Column('col2', VARCHAR(5)),
                                 schema='testing')
        values = [(3, 'three'), (4, 'four')]
        sql.insert_values(table=table, values=values, execute=True)
        rows = cursor.execute("SELECT * FROM testing.test_table").fetchall()
        tuple_rows = [tuple(row) for row in rows]
        assert values[0] in tuple_rows
        assert values[1] in tuple_rows
        return

    def test_insert_values_with_no_execute(self):
        table = sqlalchemy.Table('test_table',
                                 sqlalchemy.MetaData(),
                                 sqlalchemy.Column('col1', INT),
                                 sqlalchemy.Column('col2', VARCHAR(5)),
                                 schema='testing')
        values = [(5, 'five'), (6, 'six')]
        sql.insert_values(table=table, values=values, execute=False)
        rows = cursor.execute("SELECT * FROM testing.test_table").fetchall()
        tuple_rows = [tuple(row) for row in rows]
        assert values[0] not in tuple_rows
        assert values[1] not in tuple_rows
        return

    def test_delete_values_with_execute(self):
        table = sqlalchemy.Table('test_table',
                                 sqlalchemy.MetaData(),
                                 sqlalchemy.Column('col1', INT),
                                 sqlalchemy.Column('col2', VARCHAR(5)),
                                 schema='testing')
        values = [1, 2]
        sql.delete_values(table=table, values=values,
                          column=table.columns.col1, execute=True)
        rows = cursor.execute("SELECT col1 FROM testing.test_table").fetchall()
        tuple_rows = [tuple(row) for row in rows]
        expected_values = [expected_value[0] for expected_value in tuple_rows]
        assert values[0] not in expected_values
        assert values[1] not in expected_values
        return

    def test_delete_values_with_no_execute(self):
        table = sqlalchemy.Table('test_table',
                                 sqlalchemy.MetaData(),
                                 sqlalchemy.Column('col1', INT),
                                 sqlalchemy.Column('col2', VARCHAR(5)),
                                 schema='testing')
        values = [3, 4]
        sql.delete_values(table=table, values=values,
                          column=table.columns.col1, execute=False)
        rows = cursor.execute("SELECT col1 FROM testing.test_table").fetchall()
        tuple_rows = [tuple(row) for row in rows]
        expected_values = [expected_value[0] for expected_value in tuple_rows]
        assert values[0] in expected_values
        assert values[1] in expected_values
        return
