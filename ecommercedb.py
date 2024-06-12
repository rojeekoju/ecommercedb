import mysql.connector

# Try to make connection to DB
try:
    connection = mysql.connector.connect(
        host = "localhost",
        user = "root",
        # Change to your MySQL database password.
        password = "password1.",
        database = "ecommerce"
    )
    cursor = connection.cursor()
except mysql.connector.Error as error:
    print('Cannot connect to database: ', error)

def list_inventory_products():

    query = '''
        SELECT p.product_id, p.name, p.description, p.price, i.quantity
        FROM Product p
        JOIN Inventory i ON p.product_id = i.product_id;
    '''

    cursor.execute(query)

    for row in cursor.fetchall():
        print(row)

def add_product(catalog_id, name, description, price):

    insert_query = '''
        INSERT INTO Product (catalog_id, name, description, price) 
        VALUES (%s, %s, %s, %s);
    '''

    product_data = (catalog_id, name, description, price)

    cursor.execute(insert_query, product_data)
    connection.commit()
    print("Product added successfully!")

def inventory_add(product_id, quantity):
    remove_trigger = ( ''' 
        DROP TRIGGER IF EXISTS inventoryadd;
         ''')

    create_trigger = ('''
                CREATE TRIGGER inventoryadd
                        AFTER INSERT
                        ON PRODUCT FOR EACH ROW
                        INSERT INTO INVENTORY(product_id, quantity)
                        VALUES 
                        (%s, %s);
    ''')
    cursor.execute(remove_trigger)
    connection.commit()

    cursor.execute(create_trigger, (product_id, quantity))
    connection.commit()
    print("Inventory updated successfully!")



def modify_product_amount(product_name, inventory_quantity):

    update = '''
        UPDATE Inventory
        SET quantity = %s
        WHERE product_id = (
            SELECT product_id
            FROM Product
            WHERE name = %s
        );
    '''

    cursor.execute(update, (inventory_quantity, product_name))
    connection.commit()
    print("Product amount modified successfully!")

def delete_product_from_inventory(product_name):

    delete = '''
        DELETE FROM Inventory
        WHERE product_id = (
            SELECT product_id
            FROM Product
            WHERE name = %s
        );
    '''

    cursor.execute(delete, (product_name,))
    # Then, delete from Product
    delete_product = '''
        DELETE FROM Product
        WHERE name = %s;
    '''
    cursor.execute(delete_product, (product_name,))

    connection.commit()
    print("Removed product data " + product_name + " successfully!")


def most_popular_products(start_date, end_date):

    query = '''
        SELECT p.product_id, p.name, SUM(oi.quantity) AS total_quantity_sold, AVG(r.rating) AS average_rating
        FROM Product p
        JOIN OrderItem oi ON p.product_id = oi.product_id
        JOIN OrderItem o ON oi.order_id = o.order_id
        JOIN Review r ON o.order_id = r.order_id
        WHERE o.date BETWEEN %s AND %s AND r.rating >= 4
        GROUP BY p.product_id
        ORDER BY total_quantity_sold * average_rating DESC;
    '''

    cursor.execute(query, (start_date, end_date))

    for row in cursor.fetchall():
        print(row)


def least_popular_products(start_date, end_date):

    query = '''
        SELECT p.product_id, p.name, SUM(oi.quantity) AS total_quantity_sold, AVG(r.rating) AS average_rating
        FROM Product p
        JOIN OrderItem oi ON p.product_id = oi.product_id
        JOIN OrderItem o ON oi.order_id = o.order_id
        JOIN Review r ON o.order_id = r.order_id
        WHERE o.date BETWEEN %s AND %s AND r.rating <= 3
        GROUP BY p.product_id
        ORDER BY total_quantity_sold * average_rating ASC;
    '''

    cursor.execute(query, (start_date, end_date))

    for row in cursor.fetchall():
        print(row)

def get_inactive_users(start_date, end_date):

    query = '''
        SELECT u.user_id, u.fullname, SUM(oi.quantity) AS total_orders
        FROM User u
        LEFT JOIN OrderItem o ON u.user_id = o.user_id
        LEFT JOIN OrderItem oi ON o.order_id = oi.order_id
        WHERE o.date BETWEEN %s AND %s 
        GROUP BY u.user_id, u.fullname
        HAVING total_orders < 1;
    '''

    cursor.execute(query, (start_date, end_date))

    for row in cursor.fetchall():
        print(row)

def get_user_information(user_id):

    remove_procedure = '''
        DROP PROCEDURE IF EXISTS GetUserInformation;
    '''

    create_procedure = '''
        CREATE PROCEDURE GetUserInformation(
            IN p_user_id INT
        )
        BEGIN
            SELECT user_id, fullname, email, location_id, role_id, phone_number, date_of_birth, username
            FROM User
            WHERE user_id = p_user_id;
        END
    '''

    procedure_call = 'CALL GetUserInformation(%s)'

    cursor.execute(remove_procedure)
    cursor.execute(create_procedure)
    cursor.callproc('GetUserInformation', (user_id,))

    for result in cursor.stored_results():
        for row in result.fetchall():
            print(row)

    connection.commit()

def get_product_information(product_id):

    remove_procedure = '''
        DROP PROCEDURE IF EXISTS GetProductInformation;
    '''

    create_procedure = '''
        CREATE PROCEDURE GetProductInformation(
            IN p_product_id INT
        )
        BEGIN
            SELECT *
            FROM Product
            WHERE product_id = p_product_id;
        END
    '''

    procedure_call = 'CALL GetProductInformation(%s)'

    cursor.execute(remove_procedure)
    cursor.execute(create_procedure)
    cursor.callproc('GetProductInformation', (product_id,))

    for result in cursor.stored_results():
        for row in result.fetchall():
            print(row)

    connection.commit()


def main_menu():
    current_product_id = 11
    while True:
        print("\nMain Menu:")
        print("1. List Inventory Products")
        print("2. Add Product Information")
        print("3. Add New Product to Inventory (Trigger)")
        print("4. Modify Product Amount")
        print("5. Remove Product")
        print("6. Most Popular Products")
        print("7. Least Popular Products")
        print("8. List Inactive User")
        print("9. Get User Information(Procedure)")
        print("10. Get Product Information(Procedure)")
        print("11. Exit")

        choice = input("Select an option: ")

        if choice == '1':
            list_inventory_products()
        elif choice == '2':
            catalog_id = int(input("Enter catalog ID: "))
            name = input("Enter product name: ")
            description = input("Enter product description: ")
            price = float(input("Enter price: "))
            add_product(catalog_id, name, description, price)
            current_product_id += 1
        elif choice == '3':
            inventory_add(current_product_id, 0)
        elif choice == '4':
            product_name = input("Enter product name: ")
            inventory_quantity = int(input("Enter inventory quantity: "))
            modify_product_amount(product_name, inventory_quantity)
        elif choice == '5':
            product_name = input("Enter product name: ")
            delete_product_from_inventory(product_name)
            current_product_id -= 1
        elif choice == '6':
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            most_popular_products(start_date, end_date)
        elif choice == '7':
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            least_popular_products(start_date, end_date)
        elif choice == '8':
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            get_inactive_users(start_date, end_date)
        elif choice == '9':
            user_id = int(input("Enter user ID: "))
            get_user_information(user_id)
        elif choice == '10':
            product_id = int(input("Enter product ID: "))
            get_product_information(product_id)
        elif choice == '11':
            if connection:
                connection.close()
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main_menu()

