import sqlalchemy
from sqlalchemy.orm.session import sessionmaker
from typing import Dict, List, Tuple, Union

from footballAPI import logger

class MissingKeys(Exception):
    pass


class MicroAlchemy:

    def __init__(self,
                 server: str,
                 database: str,
                 driver: str,
                 username: str,
                 password: str,
                 **kwargs):
        self.server = server
        self.database = database
        self.driver = driver
        self.username = username
        self.password = password
        self.engine_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}'
        self.engine = sqlalchemy.create_engine(self.engine_string)
        self.metadata = sqlalchemy.MetaData()
        self.Session = sessionmaker(bind=self.engine)
        self.connection = self.engine.connect()

    def _reflect(self,
                 schema: str):
        """
        Adds metadata of tables already in the target schema to the metadata object
        schema: The name of the target schema
        """
        self.metadata.reflect(bind=self.engine, schema=schema)
        return

    def _extract_table_spec_keys(self,
                                 table_spec: Dict[str, Union[str, int, float, bool, List[sqlalchemy.Column]]]
                                 ) -> Tuple[str, str, List[sqlalchemy.Column]]:
        """
        Extracts the necessary keys from the provided table spec
        table_spec: The table spec to extract the keys from
        """
        table_name = table_spec.get('table_name')
        schema = table_spec.get('schema')
        columns = table_spec.get('columns')
        return (table_name, schema, columns)

    def _validate_table_spec_keys(self,
                                  table_values: Tuple[str, str, List[sqlalchemy.Column]]
                                  ):
        """
        Ensures that the required keys are present in the table_spec provided 
        and that they are of the correct data types
        table_values: The extracted table values to be validated
        """
        table_name, schema, columns = table_values[
            0], table_values[1], table_values[2]
        if not table_name:
            raise MissingKeys("Missing table_name key in spec")
        if not schema:
            raise MissingKeys("Missing schema key in spec")
        if not columns:
            raise MissingKey("Missing columns key in spec")
        if not type(table_name) == str:
            raise InvalidType("table_name key is not of type str")
        if not type(schema) == str:
            raise InvalidType("schema is not of type str")
        if not type(columns) == list:
            raise InvalidType("columns is not of type list")
        if len(columns) == 0:
            raise NoColumnsError("No columns in columns key")
        for column in columns:
            if not type(column) == sqlalchemy.Column:
                raise InvalidType("column not of type sqlalchemy.Column")
        return

    def table(self,
              table_spec: Dict[str, Union[str, int, float, bool, List[sqlalchemy.Column]]]
              ) -> sqlalchemy.Table:
        """
        Creates a sqlalchemy table object from a provided specs
        table_name: The name of the table
        schema: The name of the schema for the table
        columns: A list of sqlalchemy column objects for the table
        """
        spec_tuple = self._extract_table_spec_keys(table_spec)
        logger.debug("Validating schema spec")
        self._validate_table_spec_keys(spec_tuple)
        table_name, schema, columns = spec_tuple[
            0], spec_tuple[1], spec_tuple[2]
        logger.debug("Creating table object")
        table = sqlalchemy.Table(table_name,
                                 self.metadata,
                                 *columns,
                                 schema=schema,
                                 extend_existing=True)
        return table

    def create_schema(self,
                      schema_name: str,
                      execute: bool=False):
        """
        Creates a schema in the target database
        schema_name: The name of the schema to be created
        execute: Execute the creation or not
        """
        schema = sqlalchemy.schema.CreateSchema(schema_name)
        if execute:
            logger.debug(f"Creating schema {schema_name}")
            self.engine.execute(schema)
        return

    def tables_list(self,
                    table_specs: List[Dict[str, Union[str, int, bool, List[sqlalchemy.Column]]]]
                    ) -> List[sqlalchemy.Table]:
        """
        Creates a list of sqlalchemy tables
        table_specs: A list of specs dictionaries containing the required specifications
        """
        tables_list = list()
        for table_spec in table_specs:
            logger.debug(f"Creating table object for {table_spec.get('schema')}.{table_spec.get('table_name')}")
            table = self.table(table_spec=table_spec)
            tables_list.append(table)
        return tables_list

    def create_tables(self,
                      table_list: List[sqlalchemy.Table]):
        """
        Creates tables in the database from a list
        table_list: A list of sqlalchemy tables
        """
        logger.info(f"Creating {len(table_list)} tables")
        self.metadata.create_all(bind=self.engine, tables=table_list)
        return

    def _validate_testing_for_drop_tables(self,
                                          table: sqlalchemy.Table):
        """
        Ensures that a sqlalchemy.Table passed is in the testing schema for safety.
        """
        assert table.schema == 'testing', "Not using testing schema!"
        return

    def drop_tables(self,
                    table_list: List[sqlalchemy.Table],
                    testing: False):
        """
        Drops tables in the database from a list
        table_list: A list of sqlalchemy tables
        """
        logger.warning(f"This will drop {len(table_list)} tables")

        # Check table is testing if testing flag passed.
        if testing:
            for table in table_list:
                self._validate_testing_for_drop_tables(table)

        while True:
            confirmation = 'y' if testing else input("Are you sure?(y/n): ")
            if confirmation == 'y':
                logger.warning("Dropping tables")
                self.metadata.drop_all(bind=self.engine, tables=table_list)
                return
            elif confirmation == 'n':
                logger.warning("Not dropping tables")
                return
            else:
                logger.warning("Invalid input")

    def insert_values(self,
                      table: sqlalchemy.Table,
                      values: List[Tuple[str]],
                      execute: bool=False):
        """
        Inserts rows into a table
        table: A sqlalchemy table to insert rows into
        values: A list of tuples of the values to be inserted
        execute: Commit inserted rows or not
        """
        ins = table.insert().values(values)
        if execute:
            logger.info(f"Inserting {len(values)} rows into {table.schema}.{table.name}")
            self.connection.execute(ins)
        return

    def delete_values(self,
                      table: sqlalchemy.Table,
                      column: sqlalchemy.Column,
                      values: List[Union[str, int, float, bool]],
                      execute: bool=False):
        """
        Deletes rows from a table where a column is specific values
        table: The table to delete rows from
        column: The column used to identify values (typically PK)
        values: List of the values for column that are to be removed
        execute: Execute the deletion
        """
        deletion = table.delete().where(column.in_(values))
        if execute:
            logger.warning(f"Deleting values from {table.name}")
            self.engine.execute(deletion)
        return

    def reflect(self, schema: str):
        """
        Reflects all tables in the given schema into the metadata
        schema: the schema to be reflected
        """
        self._reflect(schema=schema)
        return

        
if __name__ == '__main__':
    from footballAPI.config.sql_alchemy.tables.leagues import leagues_spec
    from footballAPI import SECRETS

    sa = MicroAlchemy(**SECRETS)

    t = sa.table(leagues_spec)

    session = sa.Session()

    for row in session.query(t.c.league_id).filter(t.c.league_id==1).all():
        print(row.league_id)