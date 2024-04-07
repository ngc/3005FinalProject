from db import DBConnection

"""
def init_db(self):
        print("Starting Creating Club Database")
        cur = self.conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Metrics (metric_id SERIAL PRIMARY KEY, age INT, weight DECIMAL, height DECIMAL)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Member (member_id SERIAL PRIMARY KEY, email VARCHAR(255) UNIQUE, first_name VARCHAR(255), last_name VARCHAR(255), metric_id INT, FOREIGN KEY (metric_id) REFERENCES Metrics(metric_id))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Equipment (equipment_id SERIAL PRIMARY KEY, equipment_name VARCHAR(255), quality INT DEFAULT 100)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS ExerciseRoutine (exercise_routine_id SERIAL PRIMARY KEY, repititions INT, sets INT, equipment_id INT, FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS PersonalFitnessGoal (goal_id SERIAL PRIMARY KEY, weight DECIMAL, time INT)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS FitnessAchievement (achievement_id SERIAL PRIMARY KEY, achievement VARCHAR(255))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Trainer (trainer_id SERIAL PRIMARY KEY, first_name VARCHAR(255), last_name VARCHAR(255), start_time TIME, end_time TIME)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Room (room_id SERIAL PRIMARY KEY, room_name VARCHAR(255), room_number INT)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS PersonalTrainingSession (personal_training_session_id SERIAL PRIMARY KEY, room_id INT, FOREIGN KEY (room_id) REFERENCES Room(room_id))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS GroupFitnessClass (group_fitness_class_id SERIAL PRIMARY KEY, name VARCHAR(255))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Performs (member_id INT, exercise_routine_id INT, FOREIGN KEY (member_id) REFERENCES Member(member_id), FOREIGN KEY (exercise_routine_id) REFERENCES ExerciseRoutine(exercise_routine_id))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Has (member_id INT, goal_id INT, FOREIGN KEY (member_id) REFERENCES Member(member_id), FOREIGN KEY (goal_id) REFERENCES PersonalFitnessGoal(goal_id))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Achieved (member_id INT, achievement_id INT, FOREIGN KEY (member_id) REFERENCES Member(member_id), FOREIGN KEY (achievement_id) REFERENCES FitnessAchievement(achievement_id))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Teaches (trainer_id INT, personal_training_session_id INT, start_time TIME, end_time TIME, FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id), FOREIGN KEY (personal_training_session_id) REFERENCES PersonalTrainingSession(personal_training_session_id))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Attends (member_id INT, personal_training_session_id INT, FOREIGN KEY (member_id) REFERENCES Member(member_id), FOREIGN KEY (personal_training_session_id) REFERENCES PersonalTrainingSession(personal_training_session_id))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Frequents (member_id INT, group_fitness_class_id INT, FOREIGN KEY (member_id) REFERENCES Member(member_id), FOREIGN KEY (group_fitness_class_id) REFERENCES GroupFitnessClass(group_fitness_class_id))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Uses (group_fitness_class_id INT, room_id INT, start_time TIME, end_time TIME, FOREIGN KEY (group_fitness_class_id) REFERENCES GroupFitnessClass(group_fitness_class_id), FOREIGN KEY (room_id) REFERENCES Room(room_id))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Employs (exercise_routine_id INT, equipment_id INT, FOREIGN KEY (exercise_routine_id) REFERENCES ExerciseRoutine(exercise_routine_id), FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id))"
        )

        """

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
