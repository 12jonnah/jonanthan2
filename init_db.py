import os
import sqlite3
import logging

def init_db():
    """Initialize the database and create necessary tables."""
    # Configure logging
    logging.basicConfig(
        level=logging.ERROR,
        filename='db_errors.log',
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    conn = None  # Initialize connection to None
    try:
        # Use an absolute path for the database file
        db_path = os.getenv('DB_PATH', os.path.abspath(os.path.join(os.path.dirname(__file__), 'maize_milling.db')))
        conn = sqlite3.connect(db_path)  # SQLite database file
        cursor = conn.cursor()

        # Enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys = ON;')

        # Define table schemas
        TABLES = {
            'Customers': '''
                CREATE TABLE IF NOT EXISTS Customers (
                    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT NOT NULL,
                    address TEXT NOT NULL
                )
            ''',
            'Orders': '''
                CREATE TABLE IF NOT EXISTS Orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    order_date TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
                )
            ''',
            'Products': '''
                CREATE TABLE IF NOT EXISTS Products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT NOT NULL,
                    price_per_unit REAL NOT NULL,
                    available_stock INTEGER NOT NULL
                )
            '''
        }

        # Create tables
        for table_name, schema in TABLES.items():
            cursor.execute(schema)

        # Add indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer_id ON Orders(customer_id);')

        conn.commit()
        if __name__ == "__main__":
            logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()

# Ensure the script only runs when executed directly
if __name__ == "__main__":
    init_db()