from db import DBConnection


def main():
    # Database info
    db = DBConnection()
    db.init_db()

    user_input = 0
    while True:
        print("Welcome to the Health and Fitness Club CLI")
        print("Please select from the following options:")
        print("1. Register a User")
        print("2. Login as a User")
        print("3. Login as a Trainer")
        print("4. Login as an Administrative Staff")
        print("5. Exit")

        user_input = input("Please enter a number: ")

        if user_input > 5 or user_input < 1:
            print("Invalid input. Please try again.")
        else:
            break

    if user_input == 1:
        print("Registering a new user")
        first_name = input("Please enter your first name: ")
        last_name = input("Please enter your last name: ")
        email = input("Please enter your email: ")
        age = input("Please enter your age: ")
        weight = input("Please enter your weight: ")
        height = input("Please enter your height: ")

        # Register the user
    elif user_input == 2:
        print("Logging in as a user")
        email = input("Please enter your email: ")
        # attempt to login as a user
    elif user_input == 3:
        print("Logging in as a trainer")
        email = input("Please enter your email: ")
        # attempt to login as a trainer
    elif user_input == 4:
        print("Logging in as an administrative staff")
        email = input("Please enter your email: ")
        # attempt to login as an administrative staff
    else:
        print("Exiting the CLI")
        quit()


if __name__ == "__main__":
    main()
