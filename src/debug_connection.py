#!/usr/bin/env python3
"""
Debug script to test database connection
"""
import os
import sys
from dotenv import load_dotenv
import mysql.connector

def debug_connection():
    print("=== Database Connection Debug ===")
    
    # Check current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Try to find .env file
    env_paths = [".env", "../.env", "../../.env"]
    env_found = False
    
    for path in env_paths:
        abs_path = os.path.abspath(path)
        exists = os.path.exists(path)
        print(f"Checking {abs_path}: {'Found' if exists else 'Not found'}")
        if exists and not env_found:
            print(f"Loading .env from: {abs_path}")
            load_dotenv(dotenv_path=path)
            env_found = True
    
    if not env_found:
        print("No .env file found, trying system environment variables")
        load_dotenv()
    
    # Check environment variables
    print("\n=== Environment Variables ===")
    env_vars = ["MYSQL_HOST", "MONGODB_HOST", "MYSQL_DB_NAME", "DB_USERNAME", "DB_PASSWORD"]
    for var in env_vars:
        value = os.getenv(var)
        display_value = value if var != "DB_PASSWORD" else ("*" * len(value) if value else None)
        print(f"{var}: {display_value}")
    
    # Test MySQL connection
    print("\n=== Testing MySQL Connection ===")
    try:
        db_host = os.getenv("MYSQL_HOST")
        db_name = os.getenv("MYSQL_DB_NAME") 
        db_user = os.getenv("DB_USERNAME")
        db_pass = os.getenv("DB_PASSWORD")
        
        if not all([db_host, db_name, db_user, db_pass]):
            missing = [var for var in env_vars[:1] + env_vars[2:] if not os.getenv(var)]
            print(f"ERROR: Missing environment variables: {missing}")
            return False
        
        print(f"Attempting to connect to MySQL at {db_host}...")
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user, 
            password=db_pass,
            database=db_name
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✓ Connection successful! Test query result: {result}")
        
        # Test if users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        table_exists = cursor.fetchone()
        if table_exists:
            print("✓ 'users' table exists")
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            print(f"✓ Users table has {count} rows")
        else:
            print("✗ 'users' table does not exist")
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"✗ MySQL connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = debug_connection()
    sys.exit(0 if success else 1)