import psycopg
import asyncio
import unittest

class TestDatabaseConnection(unittest.IsolatedAsyncioTestCase):
    async def test_database_connection(self):
        connection_parameters = {
            'dbname' : 'rag_data',
            'user' : 'postgres',
            'host' : 'localhost',
            'port' : '5432'
        }
        try:
            conn = await psycopg.AsyncConnection.connect(**connection_parameters)
            self.assertIsNotNone(conn,"Unable to establish Connection")
        except psycopg.Error as e:
            self.fail(f"Async Connection failed: {e}")
        finally:
            if conn:
                print("Connection to database succesful!")
                await conn.close()
