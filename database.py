import sqlite3

def setup_database():
    conn = sqlite3.connect('data/makanApa.db')
    cursor = conn.cursor()

    # Create Customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customers (
            user_id BIGINT PRIMARY KEY,
            username VARCHAR(255),
            is_blocked BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            id VARCHAR(255) PRIMARY KEY,
            customer_id BIGINT,
            runner_id BIGINT,
            delivery_type VARCHAR(50),
            from_location TEXT,
            to_location TEXT,
            order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT 'pending',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accept_time TIMESTAMP,
            cancelled_at TIMESTAMP,
            customer_message_id BIGINT,
            runner_message_id BIGINT,
            FOREIGN KEY (customer_id) REFERENCES Customers(user_id),
            FOREIGN KEY (runner_id) REFERENCES Runners(user_id)
        )
    ''')

    # Create Runners table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Runners (
            user_id BIGINT PRIMARY KEY,
            username VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

    # Create order_counter.json if not exists
    import json, os
    order_counter_path = 'data/order_counter.json'
    if not os.path.exists(order_counter_path):
        with open(order_counter_path, 'w') as f:
            json.dump({"order_count": 0}, f)

setup_database()
