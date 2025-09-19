"""
User DAO (Data Access Object)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import os
from dotenv import load_dotenv
import mysql.connector
from models.user import User

class UserDAO:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
        try:
            # Try multiple locations for .env file
            env_paths = [".env", "../.env", "../../.env"]
            env_path = None
            for path in env_paths:
                if os.path.exists(path):
                    env_path = path
                    break
            
            if env_path:
                print(f"Loading .env from: {os.path.abspath(env_path)}")
                load_dotenv(dotenv_path=env_path)
            else:
                print("No .env file found, trying environment variables")
                load_dotenv()  # Try default locations
            
            # Get environment variables
            db_host = os.getenv("MYSQL_HOST")
            db_name = os.getenv("MYSQL_DB_NAME")
            db_user = os.getenv("DB_USERNAME")
            db_pass = os.getenv("DB_PASSWORD")
            
            # Debug: Print connection parameters (without password)
            print(f"Connecting to MySQL:")
            print(f"  Host: {db_host}")
            print(f"  Database: {db_name}")
            print(f"  Username: {db_user}")
            print(f"  Password: {'*' * len(db_pass) if db_pass else 'None'}")
            
            # Validate required parameters
            if not all([db_host, db_name, db_user, db_pass]):
                missing = [name for name, value in [
                    ("MYSQL_HOST", db_host),
                    ("MYSQL_DB_NAME", db_name), 
                    ("DB_USERNAME", db_user),
                    ("DB_PASSWORD", db_pass)
                ] if not value]
                raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
            
            # Attempt database connection
            self.conn = mysql.connector.connect(
                host=db_host, 
                user=db_user, 
                password=db_pass, 
                database=db_name,
                autocommit=False
            )
            self.cursor = self.conn.cursor()
            print("Successfully connected to MySQL database")
            
        except FileNotFoundError as e:
            error_msg = f"Environment file not found: {e}"
            print(f"ERROR: {error_msg}")
            raise ConnectionError(error_msg)
        except mysql.connector.Error as e:
            error_msg = f"MySQL connection error: {e}"
            print(f"ERROR: {error_msg}")
            raise ConnectionError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in UserDAO initialization: {e}"
            print(f"ERROR: {error_msg}")
            raise ConnectionError(error_msg)

    def select_all(self):
        """ Select all users from MySQL """
        if not self.cursor:
            raise RuntimeError("Database connection not established")
        
        self.cursor.execute("SELECT id, name, email FROM users")
        rows = self.cursor.fetchall()
        return [User(*row) for row in rows]

    def insert(self, user):
        """ Insert given user into MySQL """
        if not self.cursor:
            raise RuntimeError("Database connection not established")
            
        self.cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (user.name, user.email)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update(self, user):
        """ Update given user in MySQL """
        if not self.cursor:
            raise RuntimeError("Database connection not established")
            
        self.cursor.execute(
            "UPDATE users SET name = %s, email = %s WHERE id = %s",
            (user.name, user.email, user.id)
        )
        self.conn.commit()

    def delete(self, user_id):
        """ Delete user from MySQL with given user ID """
        if not self.cursor:
            raise RuntimeError("Database connection not established")
            
        self.cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        self.conn.commit()

    def delete_all(self):
        """ Empty users table in MySQL """
        if not self.cursor:
            raise RuntimeError("Database connection not established")
            
        self.cursor.execute("DELETE FROM users")
        self.conn.commit()
        
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()