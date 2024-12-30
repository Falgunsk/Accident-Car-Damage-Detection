import regex as re
import random
import mysql.connector
import config
import pandas as pd

def get_db_connection():
    return mysql.connector.connect(**config.credentials)

def check_user_exists(email = None, user_id = None):
    query = "SELECT COUNT(*) FROM user_data WHERE email = %s OR user_id = %s"
    
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (email, user_id))
            data = cursor.fetchone()
            return data[0] > 0
        
        connection.close()
           
        
def generate_user_id(name, phone):
    name_part = name[:3].lower()  # Lowercase to standardize
    phone_part = phone[-4:]  # Use the last 4 digits of the phone number

    while True:
        random_part = random.randint(100, 999)  # Generate random 3-digit number
        user_id = f"{name_part}{phone_part}{random_part}"

        if not check_user_exists(user_id):
            return user_id
        else:
            print("User ID already exists. Generating new user ID...")
            
 
def register_user(name, email, password, phone, address, city, state, zipcode, country, car_brand, car_model):
    # Normalize all necessary fields
    user_data = {
        'name': name.lower().strip(),
        'email': email.lower().strip(),
        'password': password,
        'phone': phone.strip(),
        'address': address.lower().strip(),
        'city': city.lower().strip(),
        'state': state.lower().strip(),
        'zipcode': zipcode.strip(),
        'country': country.lower().strip(),
        'car_brand': car_brand.lower().strip(),
        'car_model': car_model.lower().strip()       
    }
    
    # Generate user ID
    user_data['user_id'] = generate_user_id(user_data['name'], user_data['phone'])

    # SQL query for user registration
    query = """
        INSERT INTO user_data 
        (user_id, name, email, password, phone_number, address, city, state, zipcode, country, car_brand, car_model)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    # Execute the query with data insertion
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (
                    user_data['user_id'], user_data['name'], user_data['email'], 
                    user_data['password'], user_data['phone'], user_data['address'],
                    user_data['city'], user_data['state'], user_data['zipcode'],
                    user_data['country'], user_data['car_brand'], user_data['car_model']
                ))
                cursor.close()
                connection.commit()
                print("User registered successfully")
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def update_user(user_id, name=None, email=None, password=None, phone=None, address=None, city=None, state=None, zipcode=None, country=None, car_brand=None, car_model=None, picture=None):
    # Establish the database connection
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                # Fetch existing user data
                cursor.execute("SELECT * FROM user_data WHERE user_id = %s", (user_id,))
                user = cursor.fetchone()

                if not user:
                    print("User not found")
                    return False

                # Dictionary of user data fetched from the database
                user_data = {
                    'name': user['name'],
                    'email': user['email'],
                    'password': user['password'],  # password is hashed and stored securely
                    'phone': user['phone_number'],
                    'address': user['address'],
                    'city': user['city'],
                    'state': user['state'],
                    'zipcode': user['zipcode'],
                    'country': user['country'],
                    'car_brand': user['car_brand'],
                    'car_model': user['car_model'],
                    'picture': user['picture']
                }

                # Update only the fields that the user has provided (if not `None`)
                if name:
                    user_data['name'] = name.lower().strip()
                if email:
                    user_data['email'] = email.lower().strip()
                if password:
                    user_data['password'] = password  # Hash the password if necessary
                if phone:
                    user_data['phone'] = phone.strip()
                if address:
                    user_data['address'] = address.lower().strip()
                if city:
                    user_data['city'] = city.lower().strip()
                if state:
                    user_data['state'] = state.lower().strip()
                if zipcode:
                    user_data['zipcode'] = zipcode.strip()
                if country:
                    user_data['country'] = country.lower().strip()
                if car_brand:
                    user_data['car_brand'] = car_brand.lower().strip()
                if car_model:
                    user_data['car_model'] = car_model.lower().strip()
                if picture:
                    user_data['picture'] = picture

                # SQL query to update the user data
                query = """
                    UPDATE user_data
                    SET name = %s, email = %s, phone_number = %s, address = %s, city = %s, state = %s, zipcode = %s, country = %s, car_brand = %s, car_model = %s, password = %s, picture = %s
                    WHERE user_id = %s
                """

                # Execute the query with the updated data
                cursor.execute(query, (
                    user_data['name'], user_data['email'], user_data['phone'], user_data['address'],
                    user_data['city'], user_data['state'], user_data['zipcode'], user_data['country'],
                    user_data['car_brand'], user_data['car_model'], user_data['password'], user_data['picture'], user_id
                ))
                connection.commit()
                connection.close()
                print("User updated successfully")
                return True

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def delete_user(user_id):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM user_data WHERE user_id = %s", (user_id,))
                connection.commit()
                print("User deleted successfully")
                connection.close()
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        
def send_email(name, email, subject, message):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO message (name, email, subject, message) VALUES (%s, %s, %s, %s)", (name, email, subject, message))
                connection.commit()
                connection.close()
                print("Email sent successfully")
                
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
 

def get_car_data():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT brand, model FROM car_data")
            car_data = cursor.fetchall()
            car_data = pd.DataFrame(car_data, columns=['brand', 'model'])

            car_data = car_data.sort_values(by=['brand', 'model'])
            car_data = car_data.reset_index(drop=True)
            
            car_brands = car_data['brand'].unique()
            grouped = car_data.groupby('brand')
            
            car_models = {}
            for brand in car_brands:
                models = grouped.get_group(brand)['model'].values
                car_models[brand] = models
            
            cursor.close()
            return car_brands, car_models
        