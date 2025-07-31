import os
import psycopg2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Could not connect to the database: {e}")
        raise

def setup_database():
    """Sets up the database tables and sequences if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Create Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Customers (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                is_blocked BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("Customers table checked/created.")

        # Create Runners table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Runners (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("Runners table checked/created.")

        # Create Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Orders (
                id VARCHAR(255) PRIMARY KEY,
                customer_id BIGINT,
                runner_id BIGINT,
                delivery_type VARCHAR(50),
                from_location TEXT,
                to_location TEXT,
                order_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'pending',
                accept_time TIMESTAMPTZ,
                cancelled_at TIMESTAMPTZ,
                customer_message_id BIGINT,
                runner_message_id BIGINT,
                FOREIGN KEY (customer_id) REFERENCES Customers(user_id),
                FOREIGN KEY (runner_id) REFERENCES Runners(user_id)
            )
        ''')
        logger.info("Orders table checked/created.")

        # Create order_id_seq sequence for order counter
        cursor.execute('''
            CREATE SEQUENCE IF NOT EXISTS order_id_seq START 1;
        ''')
        logger.info("order_id_seq sequence checked/created.")

        conn.commit()
    except Exception as e:
        logger.error(f"Error during database setup: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    logger.info("Setting up the database...")
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable is not set. Please configure it in your .env file.")
    else:
        try:
            setup_database()
            logger.info("Database setup completed successfully.")
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
