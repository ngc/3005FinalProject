from db import DBConnection
import datetime

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


class AdminSession:
    def __init__(self, db):
        self.db = db

    def room_booking_management(self):
        print("Room booking management")
        print("1. Book a room")
        print("2. Cancel a room booking")
        user_input = int(input("Please enter a number: "))

        if user_input == 1:
            print("Booking a room")
            room_id = input("Please enter the room id: ")
            start_time = input("Please enter the start time: ")
            end_time = input("Please enter the end time: ")

            self.db.book_room(room_id, start_time, end_time)
            print("Room booked successfully")
        elif user_input == 2:
            print("Cancelling a room booking")
            room_id = input("Please enter the room id: ")
            start_time = input("Please enter the start time: ")
            end_time = input("Please enter the end time: ")

            self.db.cancel_room_booking(room_id, start_time, end_time)
            print("Room booking cancelled successfully")
        else:
            print("Invalid input. Please try again.")

    def equipment_maintenance_monitoring(self):
        print("Equipment maintenance monitoring")
        print("1. Report equipment issue")
        print("2. Resolve equipment issue")
        user_input = int(input("Please enter a number: "))

        if user_input == 1:
            print("Reporting equipment issue")
            equipment_id = input("Please enter the equipment id: ")
            issue = input("Please enter the issue: ")

            self.db.report_equipment_issue(equipment_id, issue)
            print("Equipment issue reported successfully")
        elif user_input == 2:
            print("Resolving equipment issue")
            equipment_id = input("Please enter the equipment id: ")

            self.db.resolve_equipment_issue(equipment_id)
            print("Equipment issue resolved successfully")
        else:
            print("Invalid input. Please try again.")

    def class_schedule_updating(self):
        print("Class schedule updating")
        print("1. Add a class")
        print("2. Remove a class")
        user_input = int(input("Please enter a number: "))

        if user_input == 1:
            print("Adding a class")
            room_id = input("Please enter the room id: ")
            start_time = input("Please enter the start time: ")
            end_time = input("Please enter the end time: ")

            self.db.add_class(room_id, start_time, end_time)
            print("Class added successfully")
        elif user_input == 2:
            print("Removing a class")
            room_id = input("Please enter the room id: ")
            start_time = input("Please enter the start time: ")
            end_time = input("Please enter the end time: ")

            self.db.remove_class(room_id, start_time, end_time)
            print("Class removed successfully")
        else:
            print("Invalid input. Please try again.")

    def billing_and_payment_processing(self):
        print("Billing and payment processing")
        print("1. List all pending bills")
        print("2. Pay a bill")
        print("3. Bill a member")

        user_input = int(input("Please enter a number: "))
        if user_input == 1:
            print("Listing all pending bills")
            pending_bills = self.db.get_all_pending_bills()
            # [(1, 1, Decimal('100'), 1, 'john.doe@gmail.com', 'John', 'Doe', 1), (2, 2, Decimal('200'), 2, 'john.lu@cmail.com', 'John', 'Lu', 2)]
            bill_string = ""
            for bill in pending_bills:
                bill_string += f"Bill ID: {bill[0]}, Amount: ${bill[2]}, Member: {bill[5]} {bill[6]}\n"

            print(bill_string)

        elif user_input == 2:
            print("Paying a bill")
            bill_id = input("Please enter the bill id: ")

            self.db.pay_bill(bill_id)
            print("Bill paid successfully")
        elif user_input == 3:
            print("Billing a member")
            member_email = input("Please enter the member email: ")
            amount = input("Please enter the amount: ")

            self.db.bill_member(member_email, amount)
            print("Member billed successfully")
        else:
            print("Invalid input. Please try again.")
        print("Billing and payment processing completed")


class MemberSession:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id

    def update_profile(self):
        print("Please select from the following options")
        print("1. Update personal information")
        print("2. Update fitness goals")
        print("3. Add new fitness goal")
        print("4. Update health metrics")
        # get user input
        option = int(input("Please select from the following options: "))
        if option == 1:
            first_name = input("Please enter your first name: ")
            last_name = input("Please enter your last name: ")
            email = input("Please enter your email: ")
            self.db.update_personal_information(self, email, first_name, last_name)
        elif option == 2:
            fitness_goal_id = input("Please enter the fitness goal id: ")
            weight = input("Please enter the weight you want to achieve: ")
            time = input("Please enter the time you want to achieve it in: ")
            self.db.update_fitness_goals(fitness_goal_id, time, weight)
        elif option == 3:
            self.add_fitness_goal()
        elif option == 4:
            age = input("Please enter your age: ")
            weight = input("Please enter your weight: ")
            height = input("Please enter your height: ")
            self.db.update_health_metrics(self, age, weight, height)
        else:
            print("Invalid input. Please try again.")
        print("Profile updated successfully")

    def add_fitness_goal(self):
        fitness_goal = input("Please enter the fitness goal you want to achieve: ")
        time = input("Please enter the time in days you want to achieve it in: ")

        self.db.add_fitness_goal(self.user_id, time, fitness_goal)

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
            date = input(
                "Please enter the date you would like for your personal training session in the format DAY/MONTH/YEAR: "
            )

            date_parts = date.split("/")
            day = int(date_parts[0])
            month = int(date_parts[1])
            year = int(date_parts[2])

            weekday = day_of_week(day, month, year)
            print(f"The date you want to book for is {weekday}")
            myresult = self.db.get_trainer_by_day(day, month, year)

            # print out the trainers that could train them on that day

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
            group_fitness_class_id = input("Please enter the group fitness class id: ")

            self.db.schedule_group_fitness_class(self.user_id, group_fitness_class_id)
            print("Group fitness class scheduled successfully")
        else:
            print("Invalid input. Please try again.")


class TrainerSession:
    def __init__(self, db, trainer_id):
        self.db = db
        self.trainer_id = trainer_id

    def schedule_management(self):
        print("Scheduling management")
        print("1. Set available time")
        print("2. View member profile")
        user_input = int(input("Please enter a number: "))

        if user_input == 1:
            print("Setting available time")
            start_time = input("Please enter the start time: ")
            end_time = input("Please enter the end time: ")

            self.db.set_trainer_availability(self.trainer_id, start_time, end_time)
            print("Available time set successfully")
        elif user_input == 2:
            print("Viewing member profile")
            member_id = input("Please enter the member id: ")
            member = self.db.get_user_dashboard(member_id)
            print(member)
        else:
            print("Invalid input. Please try again.")

    def view_member_profile(self):
        print("Viewing member profile")
        member_id = input("Please enter the member id: ")
        member = self.db.get_user_dashboard(member_id)
        print(member)


def main(db: DBConnection):
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
        trainer_session = TrainerSession(db, current_trainer)
        while True:
            print("Welcome to the Trainer Dashboard")
            print("Please select from the following options:")
            print("1. Schedule Management")
            print("2. View Member Profile")
            print("3. Logout")

            user_input = int(input("Please enter a number: "))

            if user_input > 3 or user_input < 1:
                print("Invalid input. Please try again.")
            else:
                break

        if user_input == 1:
            trainer_session.schedule_management()
        elif user_input == 2:
            trainer_session.view_member_profile()
        else:
            print("Logging out")
            current_trainer = None
            return
    elif current_admin:
        session = AdminSession(db)
        while True:
            print("Welcome to the Admin Dashboard")
            print("Please select from the following options:")
            print("1. Room Booking Management")
            print("2. Equipment Maintenance Monitoring")
            print("3. Class Schedule Updating")
            print("4. Billing and Payment Processing")
            print("5. Logout")

            user_input = int(input("Please enter a number: "))

            if user_input > 5 or user_input < 1:
                print("Invalid input. Please try again.")
            else:
                break

        if user_input == 1:
            session.room_booking_management()
        elif user_input == 2:
            session.equipment_maintenance_monitoring()
        elif user_input == 3:
            session.class_schedule_updating()
        elif user_input == 4:
            session.billing_and_payment_processing()
        else:
            print("Logging out")
            current_admin = None

    return


def day_of_week(day, month, year):
    date_obj = datetime.datetime(year, month, day)
    weekday_num = date_obj.weekday()
    weekdays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    return weekdays[weekday_num]


if __name__ == "__main__":

    db = DBConnection()
    db.drop_db()
    db.init_db()
    db.populate_db()

    while True:
        main(db)
