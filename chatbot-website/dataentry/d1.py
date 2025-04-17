import mysql.connector
import uuid
from faker import Faker
import random

# Database connection configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Aditya@1998",
    "database": "chatbot"
}

# Initialize Faker for random data generation
faker = Faker()

# Function to insert random users into the table
def insert_random_users(n=100):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        inserted = 0
        faker = Faker()
        while inserted < n:
            # Generate random user data
            uid = str(uuid.uuid4())[:10]  # Random UID
            print(uid)
            name = faker.name()
            
            faker = Faker()

            # Generate a random length between 10 and 15
            length = 10 + random.randint(0, 5)

            # Generate a phone number and truncate or pad it to the desired length
            phone_number = faker.phone_number()

            # Adjust the length of the phone number
            phone_number = ''.join([ch for ch in phone_number if ch.isdigit()])  # remove non-digit characters

            # If the phone number is longer than the desired length, truncate it
            if len(phone_number) > length:
                phone_number = phone_number[:length]
            # If the phone number is shorter, pad it with zeros
            elif len(phone_number) < length:
                phone_number = phone_number.ljust(length, '0')

            # print(phone_number)
            number = phone_number

            gender = random.choice(['Male', 'Female', 'Other'])
            language = random.choice(['English', 'Hindi', 'Spanish', 'French', 'German'])
            password = faker.password(length=10)

            # asdfg
            cursor.execute("SELECT number FROM users WHERE number = %s", (number,))
            if cursor.fetchone():
                print(f"Skipping duplicate number: {number}")
                continue
            cursor.execute("SELECT uid FROM users WHERE uid = %s", (uid,))
            if cursor.fetchone():
                print(f"Skipping duplicate UID: {uid}")
                continue
            

            # Insert new user
            query = """
            INSERT INTO users (uid, name, number, gender, language, password)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (uid, name, number, gender, language, password)
            
            cursor.execute(query, values)
            conn.commit()

            inserted += 1
            print(f"[{inserted}/{n}] Inserted: {name}, {number}, {gender}, {language}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ✅ Run the function to insert 100 random users
insert_random_users(100)
