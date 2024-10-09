import csv
from datetime import datetime, date
import sqlite3

# Database connection setup (for demonstration, using SQLite)
conn = sqlite3.connect('hospital_data.db')
cursor = conn.cursor()

# Create staging table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS staging (
        customer_name TEXT,
        customer_id TEXT,
        open_date TEXT,
        last_consulted_date TEXT,
        vaccination_id TEXT,
        doctor_name TEXT,
        state TEXT,
        country TEXT,
        dob TEXT,
        is_active TEXT
    )
''')

# Function to calculate age based on DOB
def calculate_age(dob):
    birth_date = datetime.strptime(dob, '%d%m%Y').date()
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# Function to calculate days since last consulted
def days_since_last_consulted(last_date):
    consulted_date = datetime.strptime(last_date, '%Y%m%d').date()
    today = date.today()
    delta = today - consulted_date
    return delta.days

# Function to load data into staging table
def load_staging_table(data):
    for row in data:
        cursor.execute('''
            INSERT INTO staging (customer_name, customer_id, open_date, last_consulted_date, vaccination_id, 
                                doctor_name, state, country, dob, is_active) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', row)
    conn.commit()

# Function to split data into country-specific tables and apply transformations
def split_and_transform_data():
    cursor.execute('SELECT * FROM staging')
    rows = cursor.fetchall()

    # Process each row
    for row in rows:
        customer_name, customer_id, open_date, last_consulted_date, vaccination_id, doctor_name, state, country, dob, is_active = row
        
        # Calculate age and days since last consulted
        age = calculate_age(dob)
        days_since_last = days_since_last_consulted(last_consulted_date)

        # Create or insert data into country-specific table
        table_name = f'table_{country.lower()}'
        
        # Create country-specific table if not exists
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                customer_name TEXT,
                customer_id TEXT,
                open_date TEXT,
                last_consulted_date TEXT,
                vaccination_id TEXT,
                doctor_name TEXT,
                state TEXT,
                country TEXT,
                dob TEXT,
                is_active TEXT,
                age INTEGER,
                days_since_last INTEGER
            )
        ''')

        # Insert data into country table
        cursor.execute(f'''
            INSERT INTO {table_name} (customer_name, customer_id, open_date, last_consulted_date, 
                                      vaccination_id, doctor_name, state, country, dob, is_active, age, days_since_last)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (customer_name, customer_id, open_date, last_consulted_date, vaccination_id, doctor_name, state, 
             country, dob, is_active, age, days_since_last))

    conn.commit()

# Sample data
data = [
    ['Alex', '123457', '20101012', '20121013', 'MVD', 'Paul', 'SA', 'USA', '06031987', 'A'],
    ['John', '123458', '20101012', '20121013', 'MVD', 'Paul', 'TN', 'IND', '06031987', 'A'],
    ['Mathew', '123459', '20101012', '20121013', 'MVD', 'Paul', 'WAS', 'PHIL', '06031987', 'A'],
    ['Matt', '12345', '20101012', '20121013', 'MVD', 'Paul', 'BOS', 'NYC', '06031987', 'A'],
    ['Jacob', '1256', '20101012', '20121013', 'MVD', 'Paul', 'VIC', 'AU', '06031987', 'A']
]

# Load data into the staging table
load_staging_table(data)

# Transform and split data into country-specific tables
split_and_transform_data()

# Closing database connection
conn.close()
