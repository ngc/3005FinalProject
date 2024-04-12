import psycopg2
from dotenv import load_dotenv
import os
import json
import datetime

load_dotenv()


class DBConnection:
    def __init__(self):
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        self.conn.autocommit = True

    def init_db(self):
        print("Starting initializing  Club Database")
        cur = self.conn.cursor()
        with open("DDLstatements.sql", "r") as file:
            sql = file.read()
            cur.execute(sql)
            self.conn.commit()

        cur.close()

    def populate_db(self):
        print("Starting Populating Club Database")
        cur = self.conn.cursor()
        with open("DMLstatements.sql", "r") as file:
            sql = file.read()
            cur.execute(sql)
            self.conn.commit()

        cur.close()

    def book_room(
        self, room_name, room_number, fitness_class_name, start_time, end_time
    ):
        # insert into room
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO Room (room_name, room_number) VALUES (%s, %s) RETURNING room_id",
            (room_name, room_number),
        )

        room_id = cur.fetchone()[0]

        # insert into fitness class with only name
        cur.execute(
            "INSERT INTO GroupFitnessClass (name) VALUES (%s) RETURNING group_fitness_class_id",
            (fitness_class_name,),
        )
        group_fitness_class_id = cur.fetchone()[0]

        # insert into uses
        cur.execute(
            "INSERT INTO Uses (room_id, group_fitness_class_id, start_time, end_time) VALUES (%s, %s, %s, %s)",
            (room_id, group_fitness_class_id, start_time, end_time),
        )
        cur.close()

    def get_billing_info(self, user_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM Member WHERE member_id = %s",
            (user_id,),
        )
        result = cur.fetchone()
        cur.close()
        return result

    def cancel_room_booking(self, room_id, start_time, end_time):
        cur = self.conn.cursor()
        cur.execute(
            "DELETE FROM Uses WHERE room_id = %s AND start_time = %s AND end_time = %s",
            (room_id, start_time, end_time),
        )
        cur.close()
        return False

    def report_equipment_issue(self, equipment_id, issue):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE Equipment SET issue = %s WHERE equipment_id = %s",
            (issue, equipment_id),
        )
        cur.close()

    def resolve_equipment_issue(self, equipment_id):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE Equipment SET issue = NULL WHERE equipment_id = %s",
            (equipment_id,),
        )
        cur.close()

    def add_class(self, name, room_id, start_time, end_time):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO GroupFitnessClass (name) VALUES (%s) RETURNING group_fitness_class_id",
            (name,),
        )

        group_fitness_class_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO Uses (room_id, group_fitness_class_id, start_time, end_time) VALUES (%s, %s, %s, %s)",
            (room_id, group_fitness_class_id, start_time, end_time),
        )

        cur.close()

    def remove_class(self, name, room_id, start_time, end_time):
        cur = self.conn.cursor()

        # delete the uses
        cur.execute(
            "DELETE FROM Uses WHERE room_id = %s AND start_time = %s AND end_time = %s",
            (room_id, start_time, end_time),
        )

        # delete the class based on name
        cur.execute(
            "DELETE FROM GroupFitnessClass WHERE name = %s",
            (name,),
        )
        cur.close()

    def submit_rating_for_trainer(self, user_id, trainer_id, rating):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM TrainerRating WHERE trainer_id = %s AND submited_by = %s",
            (trainer_id, user_id),
        )

        result = cur.fetchone()

        if result is not None:
            print("User has already submitted a rating for this trainer")
            return

        cur.execute(
            "INSERT INTO TrainerRating (trainer_id, rating, submited_by) VALUES (%s, %s, %s)",
            (trainer_id, rating, user_id),
        )
        cur.close()

    def get_trainer_ratings(self, trainer_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM TrainerRating WHERE trainer_id = %s",
            (trainer_id,),
        )
        result = cur.fetchall()
        cur.close()
        return result

    def get_average_rating_for_trainer(self, trainer_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT AVG(rating) FROM TrainerRating WHERE trainer_id = %s",
            (trainer_id,),
        )
        result = cur.fetchone()
        cur.close()
        return result[0]

    def drop_db(self):
        cur = self.conn.cursor()
        print("Starting Deleting Club Database")
        # Drop tables in reverse
        cur.execute("DROP TABLE IF EXISTS TrainerRating")
        cur.execute("DROP TABLE IF EXISTS PendingBill")
        cur.execute("DROP TABLE IF EXISTS Employs")
        cur.execute("DROP TABLE IF EXISTS Uses")
        cur.execute("DROP TABLE IF EXISTS Frequents")
        cur.execute("DROP TABLE IF EXISTS Attends")
        cur.execute("DROP TABLE IF EXISTS Teaches")
        cur.execute("DROP TABLE IF EXISTS Achieved")
        cur.execute("DROP TABLE IF EXISTS Has")
        cur.execute("DROP TABLE IF EXISTS Performs")
        cur.execute("DROP TABLE IF EXISTS GroupFitnessClass")
        cur.execute("DROP TABLE IF EXISTS PersonalTrainingSession")
        cur.execute("DROP TABLE IF EXISTS Room")
        cur.execute("DROP TABLE IF EXISTS TrainerShifts")
        cur.execute("DROP TABLE IF EXISTS Trainer")
        cur.execute("DROP TABLE IF EXISTS FitnessAchievement")
        cur.execute("DROP TABLE IF EXISTS PersonalFitnessGoal")
        cur.execute("DROP TABLE IF EXISTS ExerciseRoutine")
        cur.execute("DROP TABLE IF EXISTS Equipment")
        cur.execute("DROP TABLE IF EXISTS Member")
        cur.execute("DROP TABLE IF EXISTS Metrics")
        cur.close()
        print("Finished Deleting Club Database")

    def does_user_exist_with_email(self, email):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Member WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()
        return result is not None

    def does_user_exist_with_member_id(self, member_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Member WHERE member_id = %s", (member_id,))
        result = cur.fetchone()
        cur.close()
        return result is not None

    def get_user_id(self, email):
        cur = self.conn.cursor()
        cur.execute("SELECT member_id FROM Member WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()
        return result[0]

    def get_all_equipment(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Equipment")
        result = cur.fetchall()
        cur.close()
        return result

    def register_user(self, email, first_name, last_name, age, weight, height):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO Metrics (age, weight, height) VALUES (%s, %s, %s) RETURNING metric_id",
            (age, weight, height),
        )
        metric_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO Member (email, first_name, last_name, metric_id) VALUES (%s, %s, %s, %s)",
            (email, first_name, last_name, metric_id),
        )
        cur.close()

    def update_personal_information(self, member_session, email, first_name, last_name):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT metric_id FROM Member WHERE member_id = %s",
            (member_session.user_id,),
        )
        metric_id = cur.fetchone()[0]
        cur.execute(
            "UPDATE Member SET email = %s, first_name = %s, last_name = %s WHERE member_id = %s",
            (email, first_name, last_name, member_session.user_id),
        )

        cur.close()

    def update_fitness_goals(self, fitness_goal_id, time, goal_description):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE PersonalFitnessGoal SET goal_description = %s, time = %s WHERE goal_id = %s",
            (goal_description, time, fitness_goal_id),
        )
        cur.close()

    def update_health_metrics(self, member_session, age, weight, height):
        cur = self.conn.cursor()
        # get metric id from the member's email
        cur.execute(
            "SELECT metric_id FROM Member WHERE member_id = %s",
            (str(member_session.user_id)),
        )
        metric_id = cur.fetchone()[0]
        cur.execute(
            "UPDATE Metrics SET age = %s, weight = %s, height = %s WHERE metric_id = %s",
            (age, weight, height, metric_id),
        )
        cur.close()

    def schedule_personal_training_session(
        self, member_id, trainer_id, room_id, start_time, end_time
    ):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO PersonalTrainingSession (room_id) VALUES (%s) RETURNING personal_training_session_id",
            (room_id,),
        )
        personal_training_session_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO Teaches (trainer_id, personal_training_session_id, start_time, end_time) VALUES (%s, %s, %s, %s)",
            (trainer_id, personal_training_session_id, start_time, end_time),
        )
        cur.execute(
            "INSERT INTO Attends (member_id, personal_training_session_id) VALUES (%s, %s)",
            (member_id, personal_training_session_id),
        )
        cur.close()

    def schedule_group_fitness_class(self, member_id, group_fitness_class_id):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO Frequents (member_id, group_fitness_class_id) VALUES (%s, %s)",
            (member_id, group_fitness_class_id),
        )
        cur.close()

    def get_user_personal_training_sessions(self, id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM PersonalTrainingSession JOIN Attends ON PersonalTrainingSession.personal_training_session_id = Attends.personal_training_session_id WHERE member_id = %s",
            (id,),
        )
        result = cur.fetchall()
        cur.close()
        return result

    def get_user_dashboard(self, id):
        # returns a string with all the user's information
        cur = self.conn.cursor()
        cur.execute(
            "SELECT email, first_name, last_name, age, weight, height FROM Member JOIN Metrics ON Member.metric_id = Metrics.metric_id WHERE member_id = %s",
            (id,),
        )

        result = cur.fetchone()
        cur.close()

        formatted_user_info = f"Email: {result[0]}\nFirst Name: {result[1]}\nLast Name: {result[2]}\nAge: {result[3]}\nWeight: {result[4]}\nHeight: {result[5]}"

        # get metrics
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM Has WHERE member_id = %s",
            (id,),
        )

        result = cur.fetchone()
        cur.close()

        if result is not None:
            goal_id = result[1]
            cur = self.conn.cursor()
            cur.execute(
                "SELECT * FROM PersonalFitnessGoal WHERE goal_id = %s",
                (goal_id,),
            )

            result = cur.fetchone()
            cur.close()

            formatted_user_info += (
                f"\n\nPersonal Fitness Goal:\nWeight: {result[1]}\nTime: {result[2]}"
            )

        # get achievements
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM Achieved WHERE member_id = %s",
            (id,),
        )

        result = cur.fetchone()
        cur.close()

        if result is not None:
            achievement_id = result[1]
            cur = self.conn.cursor()
            cur.execute(
                "SELECT * FROM FitnessAchievement WHERE achievement_id = %s",
                (achievement_id,),
            )

            result = cur.fetchone()
            cur.close()

            formatted_user_info += f"\n\nFitness Achievement: {result[1]}"

        # get personal training sessions
        cur = self.conn.cursor()

        cur.execute(
            "SELECT * FROM PersonalTrainingSession JOIN Attends ON PersonalTrainingSession.personal_training_session_id = Attends.personal_training_session_id WHERE member_id = %s",
            (id,),
        )

        result = cur.fetchall()
        cur.close()

        if result is not None:
            formatted_user_info += "\n\nPersonal Training Sessions:"
            for session in result:
                formatted_user_info += f"\nRoom ID: {session[1]}"
                formatted_user_info += f"\nStart Time: {session[2]}"
                formatted_user_info += f"\nEnd Time: {session[3]}"
                formatted_user_info += "\n"

        # get group fitness classes
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM GroupFitnessClass JOIN Frequents ON GroupFitnessClass.group_fitness_class_id = Frequents.group_fitness_class_id WHERE member_id = %s",
            (id,),
        )

        result = cur.fetchall()
        cur.close()

        if result is not None:
            formatted_user_info += "\nGroup Fitness Classes:"
            for group in result:
                formatted_user_info += f"\nName: {group[1]}"
                formatted_user_info += "\n"

        # get fitness goals
        goals = self.get_all_fitness_goals(id)
        if goals is not None:
            formatted_user_info += "\nFitness Goals:"
            for goal in goals:
                formatted_user_info += f"\nGoal Description: {goal[2]}"
                formatted_user_info += f"\nTime: {goal[1]}"
                formatted_user_info += "\n"
        else:
            formatted_user_info += "\nFitness Goals: None"
        return formatted_user_info

    def does_trainer_exist(self, id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Trainer WHERE trainer_id = %s", (id,))
        result = cur.fetchone()
        cur.close()
        return result is not None

    def get_trainer_by_day(self, day, month, year):
        cur = self.conn.cursor()
        date_obj = datetime.datetime(year, month, day)
        weekday_num = date_obj.weekday() + 1
        cur.execute("SELECT * FROM TrainerShifts")
        results = cur.fetchall()
        cur.close()

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Trainer")
        trainers = cur.fetchall()
        cur.close()

        scheduled_shifts_list = []
        for row in results:
            # scheduled_shifts_list.append(json.loads(row[0]))
            scheduled_shifts = json.loads(row[0])
            if str(weekday_num) in scheduled_shifts:
                scheduled_shifts_list.append(
                    {
                        "trainer id": json.loads(str(row[0])),
                        "trainer name": self.get_trainer_name_by_id(row[0]),
                        "scheduled_shifts": scheduled_shifts[str(weekday_num)],
                    }
                )

        print("Available trainers:", scheduled_shifts_list)
        # get the TrainerShifts row for the trainer_id

        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM TrainerShifts WHERE trainer_id = %s",
            (1,),
        )

        result = cur.fetchone()
        cur.close()

        unavailablity = json.loads(result[1])

        scheduled_shifts_list_copy = scheduled_shifts_list.copy()
        for trainer in scheduled_shifts_list_copy:
            for unavailable in unavailablity:
                if unavailable["day"] == weekday_num:
                    if (
                        unavailable["start_time"]
                        <= scheduled_shifts_list[trainer]["scheduled_shifts"]
                        <= unavailable["end_time"]
                    ):
                        scheduled_shifts_list.remove(trainer)

        return scheduled_shifts_list is not None

    def get_connection(self):
        return self.conn

    def add_fitness_goal(self, user_id, time, goal_description):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO PersonalFitnessGoal (time, goal_description) VALUES (%s, %s) RETURNING goal_id",
            (time, goal_description),
        )
        goal_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO Has (member_id, goal_id) VALUES (%s, %s)",
            (user_id, goal_id),
        )

        cur.close()

    def get_all_fitness_goals(self, user_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM Has WHERE member_id = %s",
            (user_id,),
        )

        # iterate through all the goals and return a list of tuples
        result = cur.fetchall()
        goals = []

        for goal in result:
            cur.execute(
                "SELECT * FROM PersonalFitnessGoal WHERE goal_id = %s",
                (goal[1],),
            )

            goal_info = cur.fetchone()
            goals.append(goal_info)

        cur.close()

        return goals

    def get_all_trainers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Trainer")

        result = cur.fetchall()
        cur.close()

        return result

    def add_fitness_achievement(self, user_id, achievement):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO FitnessAchievement (achievement) VALUES (%s) RETURNING achievement_id",
            (achievement,),
        )
        achievement_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO Achieved (member_id, achievement_id) VALUES (%s, %s)",
            (user_id, achievement_id),
        )

        cur.close()

    def get_all_fitness_achievements(self, user_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM Achieved WHERE member_id = %s",
            (user_id,),
        )

        result = cur.fetchall()
        achievements = []

        for achievement in result:
            cur.execute(
                "SELECT * FROM FitnessAchievement WHERE achievement_id = %s",
                (achievement[1],),
            )

            achievement_info = cur.fetchone()
            achievements.append(achievement_info)

        cur.close()

        return achievements

    def convert_goal_to_achievement(self, user_id, goal_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM Has WHERE member_id = %s AND goal_id = %s",
            (user_id, goal_id),
        )

        result = cur.fetchone()

        if result is not None:
            cur.execute(
                "DELETE FROM Has WHERE member_id = %s AND goal_id = %s",
                (user_id, goal_id),
            )

            cur.execute(
                "INSERT INTO Achieved (member_id, achievement_id) VALUES (%s, %s)",
                (user_id, goal_id),
            )

        cur.close()

    def get_all_pending_bills(self):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM PendingBill JOIN Member ON PendingBill.member_id = Member.member_id"
        )

        result = cur.fetchall()
        cur.close()

        return result

    def bill_member(self, email, amount):
        cur = self.conn.cursor()
        cur.execute("SELECT member_id FROM Member WHERE email = %s", (email,))
        member_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO PendingBill (member_id, amount) VALUES (%s, %s)",
            (member_id, amount),
        )

        cur.close()
        return

    def get_trainer_name_by_id(self, id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT first_name, last_name FROM Trainer WHERE trainer_id = %s", (id,)
        )
        trainer_name = cur.fetchone()[0]
        print("trainer name is ", trainer_name)
        cur.close()
        return trainer_name

    def does_bill_exist(self, bill_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM PendingBill WHERE bill_id = %s", (bill_id,))
        result = cur.fetchone()
        cur.close()
        return result is not None

    def pay_bill(self, bill_id):
        cur = self.conn.cursor()
        cur.execute(
            "DELETE FROM PendingBill WHERE bill_id = %s",
            (bill_id,),
        )
        cur.close()

    def get_all_bills(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM PendingBill")
        result = cur.fetchall()
        cur.close()
        return result


class DisplayTable:
    def __init__(self, db):
        self.db = db

    def display_metrics(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Metrics")
        result = cur.fetchall()
        cur.close()

        print("Metrics Table:")
        print("metric_id | age | weight | height")
        for row in result:
            print(row)

    def display_member(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Member")
        result = cur.fetchall()
        cur.close()

        print("Member Table:")
        print("member_id | email | first_name | last_name | metric_id")
        for row in result:
            print(row)

    def display_equipment(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Equipment")
        result = cur.fetchall()
        cur.close()

        print("Equipment Table:")
        print("equipment_id | equipment_name | quality | issue")
        for row in result:
            print(row)

    def display_exercise_routines(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM ExerciseRoutine")
        result = cur.fetchall()
        cur.close()

        print("Exercise Routine Table:")
        print("exercise_routine_id | repititions | sets | equipment_id")
        for row in result:
            print(row)

    def display_personal_fitness_goals(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM PersonalFitnessGoal")
        result = cur.fetchall()
        cur.close()

        print("Personal Fitness Goal Table:")
        print("goal_id | time | goal_description")
        for row in result:
            print(row)

    def display_fitness_achievements(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM FitnessAchievement")
        result = cur.fetchall()
        cur.close()

        print("Fitness Achievement Table:")
        print("achievement_id | achievement")
        for row in result:
            print(row)

    def display_trainers(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Trainer")
        result = cur.fetchall()
        cur.close()

        print("Trainer Table:")
        print("trainer_id | first_name | last_name")
        for row in result:
            print(row)

    def display_trainer_shifts(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM TrainerShifts")
        result = cur.fetchall()
        cur.close()

        print("Trainer Shifts Table:")
        print("trainer_id | scheduled_shifts | unavailable_times")
        for row in result:
            print(row)

    def display_rooms(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Room")
        result = cur.fetchall()
        cur.close()

        print("Room Table:")
        print("room_id | room_name | room_number")
        for row in result:
            print(row)

    def display_personal_training_sessions(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM PersonalTrainingSession")
        result = cur.fetchall()
        cur.close()

        print("Personal Training Session Table:")
        print("personal_training_session_id | room_id")
        for row in result:
            print(row)

    def display_group_fitness_classes(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM GroupFitnessClass")
        result = cur.fetchall()
        cur.close()

        print("Group Fitness Class Table:")
        print("group_fitness_class_id | name")
        for row in result:
            print(row)

    def display_performs(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Performs")
        result = cur.fetchall()
        cur.close()

        print("Performs Table:")
        print("member_id | exercise_routine_id")
        for row in result:
            print(row)

    def display_has(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Has")
        result = cur.fetchall()
        cur.close()

        print("Has Table:")
        print("member_id | goal_id")
        for row in result:
            print(row)

    def display_achieved(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Achieved")
        result = cur.fetchall()
        cur.close()

        print("Achieved Table:")
        print("member_id | achievement_id")
        for row in result:
            print(row)

    def display_teaches(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Teaches")
        result = cur.fetchall()
        cur.close()

        print("Teaches Table:")
        print("trainer_id | personal_training_session_id | start_time | end_time")
        for row in result:
            print(row)

    def display_attends(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Attends")
        result = cur.fetchall()
        cur.close()

        print("Attends Table:")
        print("member_id | personal_training_session_id")
        for row in result:
            print(row)

    def display_frequents(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Frequents")
        result = cur.fetchall()
        cur.close()

        print("Frequents Table:")
        print("member_id | group_fitness_class_id")
        for row in result:
            print(row)

    def display_uses(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Uses")
        result = cur.fetchall()
        cur.close()

        print("Uses Table:")
        print("group_fitness_class_id | room_id | start_time | end_time")
        for row in result:
            print(row)

    def display_employs(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Employs")
        result = cur.fetchall()
        cur.close()

        print("Employs Table:")
        print("exercise_routine_id | equipment_id")
        for row in result:
            print(row)

    def display_pending_bills(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM PendingBill")
        result = cur.fetchall()
        cur.close()

        print("Pending Bill Table:")
        print("bill_id | member_id | amount")
        for row in result:
            print(row)

    def display_trainer_ratings(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM TrainerRating")
        result = cur.fetchall()
        cur.close()

        print("Trainer Rating Table:")
        print("rating_id | trainer_id | rating | submited_by")
        for row in result:
            print(row)

    def display_all_tables(self):
        self.display_metrics()
        self.display_member()
        self.display_equipment()
        self.display_exercise_routines()
        self.display_personal_fitness_goals()
        self.display_fitness_achievements()
        self.display_trainers()
        self.display_trainer_shifts()
        self.display_rooms()
        self.display_personal_training_sessions()
        self.display_group_fitness_classes()
        self.display_performs()
        self.display_has()
        self.display_achieved()
        self.display_teaches()
        self.display_attends()
        self.display_frequents()
        self.display_uses()
        self.display_employs()
        self.display_pending_bills()
        self.display_trainer_ratings()
