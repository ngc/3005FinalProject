from db import DBConnection, DisplayTable
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


import os


class AdminSession:
    def __init__(self, db):
        self.db: DBConnection = db
        self.display = DisplayTable(db)

    def export_data_to_csv(self):
        print("Exporting data to CSV")
        self.db.export_data_to_csv()
        print("Data exported successfully")

    def room_booking_management(self):
        print("Room booking management")
        print("1. Cancel a room booking")
        user_input = int(get_valid_int_input("Please enter a number: "))

        if user_input == 1:
            print("Cancelling a room booking")

            self.display.display_room_bookings()

            booking_id = get_valid_int_input("Please enter the booking id: ")

            self.db.cancel_room_booking(booking_id)
            print("Room booking cancelled successfully")
        else:
            print("Invalid input. Please try again.")

    def equipment_maintenance_monitoring(self):
        print("Equipment maintenance monitoring")
        print(" ")
        DisplayTable.display_equipment(self)
        print(" ")
        print("1. Report equipment issue")
        print("2. Resolve equipment issue")
        print("3. Add new equipment")
        print("4. Remove equipment")
        user_input = int(get_valid_int_input("Please enter a number: "))

        def print_equipment():
            equipment = self.db.get_all_equipment()
            for item in equipment:
                print(
                    f"ID: {item[0]}, Name: {item[1]}, Quality: {item[2]}, Issue: {item[3]}"
                )

        if user_input == 1:
            print("Reporting equipment issue")

            print_equipment()

            equipment_id = get_valid_int_input("Please enter the equipment id: ")

            issue = input("Please enter the issue: ")

            self.db.report_equipment_issue(equipment_id, issue)
            print("Equipment issue reported successfully")
        elif user_input == 2:
            print("Resolving equipment issue")

            print_equipment()

            equipment_id = input("Please enter the id of the equipment that was fixed ")
            self.db.resolve_equipment_issue(equipment_id)
            print("Equipment issue resolved successfully")

        elif user_input == 3:
            print("Adding new equipment")

            print_equipment()

            equipment_name = input("Please enter the name of the equipment: ")
            equipment_quality = input("Please enter the quality of the equipment: ")
            equipment_issues = input("Please enter any issues with the equipment : ")
            self.db.add_new_equipment(
                equipment_name, equipment_quality, equipment_issues
            )
            print("Equipment added successfully")

        elif user_input == 4:
            print("Removing equipment")

            equipment_id = input(
                "Please enter the id of the equipment you would like to remove "
            )
            self.db.remove_equipment(equipment_id)
            print("Equipment removed successfully")

        else:
            print("Invalid input. Please try again.")

    def class_schedule_updating(self):
        print("Class schedule updating")
        print("1. Add a class")
        print("2. Remove a class")
        user_input = int(get_valid_int_input("Please enter a number: "))

        if user_input == 1:
            print("Adding a class")
            name = input("Please enter the class name: ")
            room_id = get_valid_int_input("Please enter the room id: ")
            start_time = input("Please enter the start time: ")
            end_time = input("Please enter the end time: ")
            date = input(
                "Please enter the date you would like to schedule the class in the format DAY/MONTH/YEAR: "
            )

            date_parts = date.split("/")
            day = int(date_parts[0])
            month = int(date_parts[1])
            year = int(date_parts[2])

            self.db.add_class(name, room_id, month, day, year, start_time, end_time)
            print("Class added successfully")
        elif user_input == 2:
            self.display.display_group_fitness_classes()

            print("Removing a class")
            class_id = get_valid_int_input("Please enter the group fitness class id: ")

            self.db.remove_class(class_id)
            print("Class removed successfully")
        else:
            print("Invalid input. Please try again.")

    def billing_and_payment_processing(self):
        print("Billing and payment processing")
        print("1. List all pending bills")
        print("2. Pay a bill")
        print("3. Bill a member")

        self.display.display_member()

        user_input = int(get_valid_int_input("Please enter a number: "))

        if user_input == 1:
            print("Listing all pending bills")
            pending_bills = self.db.get_all_pending_bills()
            bill_string = ""
            for bill in pending_bills:
                bill_string += f"Bill ID: {bill[0]}, Amount: ${bill[2]}, Member: {bill[5]} {bill[6]}\n"

            print(bill_string)

        elif user_input == 2:
            print("Paying a bill")
            bills = self.db.get_all_bills()
            for bill in bills:
                print(f"Bill ID: {bill[0]}, Amount: ${bill[1]}, Member: {bill[2]}")
            bill_id = get_valid_int_input("Please enter the bill id: ")
            if self.db.does_bill_exist(bill_id):
                self.db.pay_bill(bill_id)
                print("Bill paid successfully")
            else:
                print("Bill does not exist")
        elif user_input == 3:
            print("Billing a member")

            member_email = "email"
            while not self.db.does_user_exist_with_email(member_email):
                member_email = input("Please enter a valid member email: ")
            amount = get_valid_int_input("Please enter the amount: ")

            self.db.bill_member(member_email, amount)
            print("Member billed successfully")
        else:
            print("Invalid input. Please try again.")
        print("Billing and payment processing completed")


class MemberSession:
    def __init__(self, db, user_id):
        self.db: DBConnection = db
        self.user_id = user_id
        self.display = DisplayTable(db)

    def update_profile(self):
        print("Please select from the following options")
        print("1. Update personal information")
        print("2. Update fitness goals")
        print("3. Add new fitness goal")
        print("4. Mark fitness goal as complete")
        print("5. Update health metrics")
        print("6. Update excercise routine")
        # get user input
        option = int(get_valid_int_input("Please select from the following options: "))
        if option == 1:
            first_name = input("Please enter your first name: ")
            last_name = input("Please enter your last name: ")
            email = input("Please enter your email: ")
            self.db.update_personal_information(self, email, first_name, last_name)
        elif option == 2:
            # show all fitness goals
            goals = self.db.get_all_fitness_goals(self.user_id)
            for goal in goals:
                print(f"ID: {goal[0]}, Description: {goal[1]}, Time: {goal[2]}")
            fitness_goal_id = get_valid_int_input("Please enter the fitness goal id: ")
            goal_description = input("Please enter the fitness goal description:")
            time = get_valid_int_input(
                "Please enter the time you want to achieve it in: "
            )
            self.db.update_fitness_goals(fitness_goal_id, time, goal_description)
        elif option == 3:
            self.add_fitness_goal()
        elif option == 4:
            self.mark_fitness_goal_as_complete()
        elif option == 5:
            age = get_valid_int_input("Please enter your age: ")
            weight = get_valid_int_input("Please enter your weight: ")
            height = get_valid_int_input("Please enter your height: ")
            self.db.update_health_metrics(self.user_id, age, weight, height)
        elif option == 6:
            self.update_excercise_routine()
        else:
            print("Invalid input. Please try again.")
        print("Profile updated successfully")

    def submit_rating_for_trainer(self):
        self.display.display_trainers()

        list_of_trainer_ids = [trainer[0] for trainer in self.db.get_all_trainers()]

        trainer_id = -1
        while trainer_id not in list_of_trainer_ids:
            trainer_id = get_valid_int_input("Please enter a trainer id: ")
        rating = -1
        while rating < 1 or rating > 5:
            rating = get_valid_int_input("Please enter the rating 1-5: ")

        self.db.submit_rating_for_trainer(self.user_id, trainer_id, rating)

        print("Rating submitted successfully")
        print(
            "Average rating for trainer is now: ",
            self.db.get_average_rating_for_trainer(trainer_id),
        )

    def display_fitness_goals(self):
        goals = self.db.get_all_fitness_goals(self.user_id)
        print("Your fitness goals are:")

        if goals == None or len(goals) == 0:
            print("You have no fitness goals")
            return

        for index, goal in enumerate(goals):
            print(
                f"{index + 1}. {goal['description']} - complete by {goal['time']} - is complete: {goal['completed']}"
            )

        print("")

    def add_fitness_goal(self):
        fitness_goal = input("Please enter the fitness goal you want to achieve: ")
        time = get_valid_int_input(
            "Please enter the time in days you want to achieve it in: "
        )

        self.db.add_fitness_goal(self.user_id, time, fitness_goal)

    def mark_fitness_goal_as_complete(self):
        self.display_fitness_goals()
        goal_id = get_valid_int_input("Please enter the goal id you want to complete: ")
        goal_id -= 1

        self.db.complete_fitness_goal(self.user_id, goal_id)

    def display_dashboard(self):
        print("Displaying dashboard")
        user = self.db.get_user_dashboard(self.user_id)
        print(user)

        self.display_fitness_goals()

    def update_excercise_routine(self):
        filename = f"/tmp/{self.user_id}_excercise_routine.txt"
        with open(filename, "w") as f:
            f.write(self.db.get_member_exercise_routine(self.user_id))

        os.system(f"nano {filename}")

        with open(filename, "r") as f:
            excercise_routine = f.read()

        self.db.set_member_exercise_routine(self.user_id, excercise_routine)

        os.remove(filename)

    def schedule_management(self):
        print("Scheduling management")
        print("1. Schedule personal training session")
        print("2. Join group fitness class")
        user_input = int(get_valid_int_input("Please enter a number: "))

        if user_input == 1:
            print("Scheduling personal training session")
            date = input(
                "Please enter the date you would like for your personal training session in the format DAY/MONTH/YEAR: "
            )

            date_parts = date.split("/")
            day = int(date_parts[0])
            month = int(date_parts[1])
            year = int(date_parts[2])

            # print out the trainers that could train them on that day

            self.display.display_trainers()

            trainer_id = get_valid_int_input("Please enter the trainer id: ")

            self.display.display_rooms()

            room_id = get_valid_int_input("Please enter the room id: ")
            start_time = input("Please enter the start time: ")
            end_time = input("Please enter the end time: ")

            result = self.db.schedule_personal_training_session(
                self.user_id,
                trainer_id,
                room_id,
                day,
                month,
                year,
                start_time,
                end_time,
            )

            if result != False:
                print("Personal training session scheduled successfully")
            else:
                print("Personal training session could not be scheduled")

        elif user_input == 2:
            print("Join a group fitness class")

            self.display.display_group_fitness_classes()

            group_fitness_class_id = get_valid_int_input(
                "Please enter the group fitness class id: "
            )

            self.db.join_group_fitness_class(self.user_id, group_fitness_class_id)
            print("Group fitness class scheduled successfully")
        else:
            print("Invalid input. Please try again.")

    def pay_a_bill(self):
        print("Paying a bill")
        bills = self.db.get_bills_for_member(self.user_id)

        owed_amount = 0
        for bill in bills:
            owed_amount += bill[2]

        print(f"You owe ${owed_amount}")

        for bill in bills:
            print(f"Bill ID: {bill[0]}, Amount: ${bill[2]}")
        bill_id = get_valid_int_input("Please enter the bill id: ")
        if self.db.does_bill_exist(bill_id):
            self.db.pay_bill(bill_id)
            print("Bill paid successfully")
        else:
            print("Bill does not exist")


class TrainerSession:
    def __init__(self, db, trainer_id):
        self.db: DBConnection = db
        self.trainer_id = trainer_id
        self.display = DisplayTable(db)

    def schedule_management(self):

        print("Scheduling management")
        print("1. Set unavailable time")
        print("2. View my schedule")
        user_input = int(get_valid_int_input("Please enter a number: "))

        if user_input == 1:
            print("Setting available time")
            date = input(
                "Please enter the date you would like to set your unavailable time in the format DAY/MONTH/YEAR: "
            )

            date_parts = date.split("/")
            day = int(date_parts[0])
            month = int(date_parts[1])
            year = int(date_parts[2])

            weekday = day_of_week(day, month, year)
            print(f"The date you want to set your unavailable time for is {weekday}")

            self.db.set_unavailable_time(self.trainer_id, day, month, year)
            print("Unavailable time set successfully")

        elif user_input == 2:
            # view my current schedule instead
            print(self.db.view_trainer_schedule(self.trainer_id))

        else:
            print("Invalid input. Please try again.")

    def view_member_profile(self):
        print("Viewing member profile")
        member_id = get_valid_int_input("Please enter the member id: ")
        if not self.db.does_user_exist_with_member_id(member_id):
            print("User does not exist")
            return
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

        user_input = int(get_valid_int_input("Please enter a number: "))

        if user_input > 5 or user_input < 1:
            print("Invalid input. Please try again.")
        else:
            break

    if user_input == 1:
        print("Registering a new user")
        first_name = input("Please enter your first name: ")
        last_name = input("Please enter your last name: ")
        email = input("Please enter your email: ")
        age = get_valid_int_input("Please enter your age: ")
        weight = get_valid_int_input("Please enter your weight: ")
        height = get_valid_int_input("Please enter your height: ")

        password = input("Please enter your password: ")

        if db.does_user_exist_with_email(email):
            print("User already exists")
            return

        db.register_user(email, first_name, last_name, age, weight, height, password)
        print("User registered successfully")

    elif user_input == 2:
        print("Logging in as a user")
        email = input("Please enter your email: ")

        if not db.does_user_exist_with_email(email):
            print("User does not exist")
            return

        password = input("Please enter your password: ")

        if not db.does_user_password_match(email, password):
            print("Password does not match")
            return

        current_user = db.get_user_id(email)
        print("User logged in successfully")

    elif user_input == 3:
        print("Logging in as a trainer")
        id = get_valid_int_input("Please enter your trainer id: ")

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
        user_input = 0
        while user_input != 5:
            print("Welcome to the Member Dashboard")
            print("Please select from the following options:")
            print("1. Update Profile")
            print("2. Display Dashboard")
            print("3. Schedule Management")
            print("4. Submit rating for trainer")
            print("5. View and pay bills")
            print("6. Logout")

            user_input = int(get_valid_int_input("Please enter a number: "))

            if user_input > 6 or user_input < 1:
                print("Invalid input. Please try again.")
            elif user_input == 1:
                member_session.update_profile()
            elif user_input == 2:
                member_session.display_dashboard()
            elif user_input == 3:
                member_session.schedule_management()
            elif user_input == 4:
                member_session.submit_rating_for_trainer()
            elif user_input == 5:
                member_session.pay_a_bill()
        print("Logging out")
        current_user = None
        return

    elif current_trainer:
        user_input = 0
        trainer_session = TrainerSession(db, current_trainer)
        while user_input != 3:
            print("Welcome to the Trainer Dashboard")
            print("Please select from the following options:")
            print("1. Schedule Management")
            print("2. View Member Profile")
            print("3. Logout")

            user_input = int(get_valid_int_input("Please enter a number: "))

            if user_input > 3 or user_input < 1:
                print("Invalid input. Please try again.")

            if user_input == 1:
                trainer_session.schedule_management()
            elif user_input == 2:
                trainer_session.view_member_profile()
        print("Logging out")
        current_trainer = None
        quit()

    elif current_admin:
        user_input = 0
        session = AdminSession(db)
        while user_input != 5:
            print("Welcome to the Admin Dashboard")
            print("Please select from the following options:")
            print("1. Room Booking Management")
            print("2. Equipment Maintenance Monitoring")
            print("3. Class Schedule Updating")
            print("4. Billing and Payment Processing")
            print("5. Logout")
            print("6. Export data to CSV")

            user_input = int(get_valid_int_input("Please enter a number: "))

            if user_input > 6 or user_input < 1:
                print("Invalid input. Please try again.")

            if user_input == 1:
                session.room_booking_management()
            elif user_input == 2:
                session.equipment_maintenance_monitoring()
            elif user_input == 3:
                session.class_schedule_updating()
            elif user_input == 4:
                session.billing_and_payment_processing()
            elif user_input == 5:
                print("Logging out")
                quit()
            elif user_input == 6:
                session.export_data_to_csv()
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


def get_valid_int_input(prompt):
    value = "input"
    while True:
        value = input(prompt)
        if value.isdigit():
            return int(value)
        else:
            print("Invalid input. Please try again.")


if __name__ == "__main__":

    db = DBConnection()
    db.drop_db()
    db.init_db()
    db.populate_db()

    db.register_user(
        "me@nathancoulas.com", "Nathan", "Coulas", 25, 180, 140, "password"
    )

    while True:
        main(db)
