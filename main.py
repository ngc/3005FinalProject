from db import DBConnection

"""
Member Functions:
1. User Registration
2. Profile Management (Updating personal information, fitness goals, health metrics)
3. Dashboard Display (Displaying exercise routines, fitness achievements, health statistics)
4. Schedule Management (Scheduling personal training sessions or group fitness classes. The system
must ensure that the trainer is available)
Trainer Functions:
1. Schedule Management (Trainer can set the time for which they are available.)
2. Member Profile Viewing (Search by Member’s name)
Administrative Staff Functions:
1. Room Booking Management
2. Equipment Maintenance Monitoring
3. Class Schedule Updating
4. Billing and Payment Processing (Your system should assume integration with a payment service
[Note: Do not actually integrate with a payment service])
"""


class MemberSession:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id

    def update_profile(self):
        print("Updating profile")
        first_name = input("Please enter your first name: ")
        last_name = input("Please enter your last name: ")
        email = input("Please enter your email: ")
        age = input("Please enter your age: ")
        weight = input("Please enter your weight: ")
        height = input("Please enter your height: ")

        self.db.update_user(
            self.user_id, first_name, last_name, email, age, weight, height
        )
        print("Profile updated successfully")

    def display_dashboard(self):
        print("Displaying dashboard")
        user = self.db.get_user_dashboard(self.user_id)
        print(user)

    def schedule_management(self):
        print("Scheduling management")
        print("1. Schedule personal training session")
        print("2. Schedule group fitness class")
        user_input = int(input("Please enter a number: "))

        if user_input == 1:
            print("Scheduling personal training session")
            trainer_id = input("Please enter the trainer id: ")
            room_id = input("Please enter the room id: ")
            start_time = input("Please enter the start time: ")
            end_time = input("Please enter the end time: ")

            self.db.schedule_personal_training_session(
                self.user_id, trainer_id, room_id, start_time, end_time
            )
            print("Personal training session scheduled successfully")
        elif user_input == 2:
            print("Scheduling group fitness class")
            room_id = input("Please enter the room id: ")
            start_time = input("Please enter the start time: ")
            end_time = input("Please enter the end time: ")

            self.db.schedule_group_fitness_class(
                self.user_id, room_id, start_time, end_time
            )
            print("Group fitness class scheduled successfully")
        else:
            print("Invalid input. Please try again.")


def main():
    # Database info
    db = DBConnection()
    db.init_db()
    db.populate_db()

    current_user = None
    current_trainer = None
    current_admin = None

    user_input = 0
    while True:
        print("Welcome to the Health and Fitness Club CLI")
        print("Please select from the following options:")
        print("1. Register a User")
        print("2. Login as a User")
        print("3. Login as a Trainer")
        print("4. Login as an Administrative Staff")
        print("5. Exit")

        user_input = int(input("Please enter a number: "))

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

        if db.does_user_exist(email):
            print("User already exists")
            return

        db.register_user(email, first_name, last_name, age, weight, height)
        print("User registered successfully")

    elif user_input == 2:
        print("Logging in as a user")
        email = input("Please enter your email: ")

        if not db.does_user_exist(email):
            print("User does not exist")
            return

        current_user = db.get_user_id(email)
        print("User logged in successfully")

    elif user_input == 3:
        print("Logging in as a trainer")
        id = input("Please enter your trainer id: ")

        if not db.does_trainer_exist(id):
            print("Trainer does not exist")
            return

        print("Trainer logged in successfully")

        current_trainer = id
    elif user_input == 4:
        print("Logging in as an administrative staff")
        current_admin = True
    else:
        print("Exiting the CLI")
        quit()

    """
    Member Functions:
    1. User Registration
    2. Profile Management (Updating personal information, fitness goals, health metrics)
    3. Dashboard Display (Displaying exercise routines, fitness achievements, health statistics)
    4. Schedule Management (Scheduling personal training sessions or group fitness classes. The system
    must ensure that the trainer is available)
    Trainer Functions:
    1. Schedule Management (Trainer can set the time for which they are available.)
    2. Member Profile Viewing (Search by Member’s name)
    Administrative Staff Functions:
    1. Room Booking Management
    2. Equipment Maintenance Monitoring
    3. Class Schedule Updating
    4. Billing and Payment Processing (Your system should assume integration with a payment service
    [Note: Do not actually integrate with a payment service])
    """

    if current_user:
        member_session = MemberSession(db, current_user)
        while True:
            print("Welcome to the Member Dashboard")
            print("Please select from the following options:")
            print("1. Update Profile")
            print("2. Display Dashboard")
            print("3. Schedule Management")
            print("4. Logout")

            user_input = int(input("Please enter a number: "))

            if user_input > 4 or user_input < 1:
                print("Invalid input. Please try again.")
            else:
                break

        if user_input == 1:
            member_session.update_profile()
        elif user_input == 2:
            member_session.display_dashboard()
        elif user_input == 3:
            member_session.schedule_management()
        else:
            print("Logging out")
            current_user = None
            return

    elif current_trainer:
        pass
    elif current_admin:
        pass

    return


if __name__ == "__main__":
    main()
