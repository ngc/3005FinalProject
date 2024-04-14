import psycopg2
from dotenv import load_dotenv
import os
import json
import datetime
from bcrypt import hashpw, gensalt
import binascii


load_dotenv()


# uses UNIX timestamp of seconds
def is_overlap(start_time1, end_time1, start_time2, end_time2):
    start_time1 = int(start_time1)
    end_time1 = int(end_time1)
    start_time2 = int(start_time2)
    end_time2 = int(end_time2)

    return (
        (start_time1 >= start_time2 and start_time1 <= end_time2)
        or (end_time1 >= start_time2 and end_time1 <= end_time2)
        or (start_time2 >= start_time1 and start_time2 <= end_time1)
        or (end_time2 >= start_time1 and end_time2 <= end_time1)
    )


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

    def export_data_to_csv(self):
        cur = self.conn.cursor()
        tables = [
            "Metrics",
            "Member",
            "Equipment",
            "ExerciseRoutine",
            "PersonalFitnessGoal",
            "FitnessAchievement",
            "Trainer",
            "TrainerShifts",
            "Room",
            "PersonalTrainingSession",
            "GroupFitnessClass",
            "Performs",
        ]

        for table in tables:
            cur.execute(
                f"COPY {table} TO '{os.getcwd()}/{table}.csv' DELIMITER ',' CSV HEADER"
            )

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
            "SELECT booking_id FROM RoomBooking WHERE room_id = %s AND start_time = %s AND end_time = %s",
            (room_id, start_time, end_time),
        )

        booking_id = cur.fetchone()[0]

        cur.execute(
            "DELETE FROM GroupFitnessClass WHERE booking_id = %s",
            (booking_id,),
        )

        cur.execute(
            "DELETE FROM PersonalTrainingSession WHERE booking_id = %s",
            (booking_id,),
        )

        cur.execute(
            "DELETE FROM RoomBooking WHERE booking_id = %s",
            (booking_id,),
        )

        cur.close()

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

    def add_new_equipment(self, equipment_name, quality, issue):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO Equipment (equipment_name, quality, issue) VALUES (%s, %s, %s)",
            (equipment_name, quality, issue),
        )
        cur.close()

    def remove_equipment(self, equipment_id):
        cur = self.conn.cursor()
        cur.execute(
            "DELETE FROM Equipment WHERE equipment_id = %s",
            (equipment_id,),
        )
        cur.close()

    def add_class(self, name, room_id, month, day, year, start_time, end_time):
        # CREATE TABLE IF NOT EXISTS GroupFitnessClass (group_fitness_class_id SERIAL PRIMARY KEY, name VARCHAR(255), booking_id INT, FOREIGN KEY (booking_id) REFERENCES RoomBooking(booking_id), trainer_id INT, FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id), members TEXT);

        # check if the room is available
        if not self.room_is_available(room_id, month, day, year, start_time, end_time):
            return False

        booking_id = self.book_room(room_id, month, day, year, start_time, end_time)

        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO GroupFitnessClass (name, booking_id) VALUES (%s, %s) RETURNING group_fitness_class_id",
            (name, booking_id),
        )

        group_fitness_class_id = cur.fetchone()[0]
        cur.close()

        return group_fitness_class_id

    def set_unavailable_time(self, trainer_id, day, month, year):
        # day off

        cur = self.conn.cursor()
        cur.execute(
            "SELECT unavailable_times FROM Trainer WHERE trainer_id = %s",
            (trainer_id,),
        )

        unavailable_times = cur.fetchone()[0]
        if unavailable_times is None:
            unavailable_times = []

        date_str = f"{day}/{month}/{year}"

        if date_str in unavailable_times:
            return

        unavailable_times.append(date_str)

        cur.execute(
            "UPDATE Trainer SET unavailable_times = %s WHERE trainer_id = %s",
            (json.dumps(unavailable_times), trainer_id),
        )

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
        cur.execute("DROP TABLE IF EXISTS GroupFitnessClass")
        cur.execute("DROP TABLE IF EXISTS PersonalTrainingSession")
        cur.execute("DROP TABLE IF EXISTS Room CASCADE")
        cur.execute("DROP TABLE IF EXISTS Trainer")
        cur.execute("DROP TABLE IF EXISTS Equipment")
        cur.execute("DROP TABLE IF EXISTS Member")
        cur.execute("DROP TABLE IF EXISTS RoomBooking")

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

    def does_user_password_match(self, email, password):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Member WHERE email = %s", (email,))
        result = cur.fetchone()

        if result is None:
            return False

        hex_hashed_password = result[4]
        hex_salt = result[5]

        cur.close()

        # unhexlify the hashed password and salt
        hashed_password = hashpw(password.encode("utf-8"), binascii.unhexlify(hex_salt))

        return hashed_password == binascii.unhexlify(hex_hashed_password)

    def register_user(
        self, email, first_name, last_name, age, weight, height, password
    ):

        cur = self.conn.cursor()

        # use bcrypt to hash the password
        salt = gensalt()
        hashed_password = hashpw(
            password.encode("utf-8"), salt.decode().encode("utf-8")
        )
        hex_hashed_password = binascii.hexlify(hashed_password).decode()
        hex_salt = binascii.hexlify(salt).decode()

        print("SALT: ", salt.decode())
        print("HASHED PASSWORD: ", hashed_password)

        cur.execute(
            "INSERT INTO Member (email, first_name, last_name, password, salt, age, weight, height) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING member_id",
            (
                email,
                first_name,
                last_name,
                hex_hashed_password,
                hex_salt,
                age,
                weight,
                height,
            ),
        )
        cur.close()

    def update_personal_information(self, member_session, email, first_name, last_name):
        cur = self.conn.cursor()

        cur.execute(
            "UPDATE Member SET email = %s, first_name = %s, last_name = %s WHERE member_id = %s",
            (email, first_name, last_name, member_session.user_id),
        )

        cur.close()

    def trainer_is_available(self, trainer_id, month, day, year, start_time, end_time):
        # get the trainer row
        cur = self.conn.cursor()
        cur.execute(
            "SELECT unavailable_times FROM Trainer WHERE trainer_id = %s",
            (trainer_id,),
        )

        unavailable_times = cur.fetchone()[0]

        date_str = f"{day}/{month}/{year}"
        if unavailable_times is not None and date_str in unavailable_times:
            return False

        # check all PersonalTrainingSessions
        cur.execute(
            "SELECT * FROM PersonalTrainingSession JOIN RoomBooking ON PersonalTrainingSession.booking_id = RoomBooking.booking_id WHERE trainer_id = %s",
            (trainer_id,),
        )

        result = cur.fetchall()
        cur.close()

        print(result)

        for session in result:
            if is_overlap(start_time, end_time, session[8], session[9]):
                return False

        # check all GroupFitnessClasses
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM GroupFitnessClass JOIN RoomBooking ON GroupFitnessClass.booking_id = RoomBooking.booking_id WHERE trainer_id = %s",
            (trainer_id,),
        )

        result = cur.fetchall()
        cur.close()

        for group in result:
            if is_overlap(start_time, end_time, group[8], group[9]):
                return False

        return True

    def find_available_trainers(self, month, day, year, start_time, end_time):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Trainer")
        result = cur.fetchall()
        cur.close()

        available_trainers = []

        for trainer in result:
            if self.trainer_is_available(
                trainer[0], month, day, year, start_time, end_time
            ):
                available_trainers.append(trainer)

        return available_trainers

    def get_group_fitness_schedule_string_for_trainer(self, trainer_id):
        group_fitness_classes = self.get_trainer_group_fitness_classes(trainer_id)

        formatted_schedule = "Group Fitness Classes:\n"
        for group in group_fitness_classes:
            room_info = self.group_fitness_class_to_string(group[0])
            formatted_schedule += str(room_info) + "\n\n"

        if group_fitness_classes == []:
            formatted_schedule += "No scheduled classes\n"

        return formatted_schedule

    def get_personal_training_schedule_string_for_trainer(self, trainer_id):
        personal_training_sessions = self.get_trainer_personal_training_sessions(
            trainer_id
        )

        formatted_schedule = "Personal Training Sessions:\n"
        for session in personal_training_sessions:
            room_info = self.training_session_to_string(session[0])
            formatted_schedule += str(room_info) + "\n\n"

        if personal_training_sessions == []:
            formatted_schedule += "No scheduled classes or sessions"

        return formatted_schedule

    def view_trainer_schedule(self, _id):
        formatted_schedule = self.get_group_fitness_schedule_string_for_trainer(_id)
        formatted_schedule += "\n\n"
        formatted_schedule += self.get_personal_training_schedule_string_for_trainer(
            _id
        )

        return formatted_schedule

    def room_is_available(self, room_id, month, day, year, start_time, end_time):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM RoomBooking WHERE room_id = %s AND month = %s AND day = %s AND year = %s",
            (room_id, month, day, year),
        )

        result = cur.fetchall()
        cur.close()

        for booking in result:
            if is_overlap(start_time, end_time, booking[5], booking[6]):
                return False
        return True

    def book_room(self, room_id, month, day, year, start_time, end_time):
        cur = self.conn.cursor()
        # return the booking id
        cur.execute(
            "INSERT INTO RoomBooking (room_id, month, day, year, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s) RETURNING booking_id",
            (room_id, month, day, year, start_time, end_time),
        )
        booking_id = cur.fetchone()[0]
        cur.close()
        return booking_id

    def add_member_to_room_booking(self, booking_id, member_id):
        cur = self.conn.cursor()
        # room booking table has member TEXT field which is a json array
        cur.execute(
            "SELECT members FROM RoomBooking WHERE booking_id = %s",
            (booking_id,),
        )

        members = cur.fetchone()[0]

        if members is None:
            members = []
        else:
            members = json.loads(members)

        members.append(member_id)

        cur.execute(
            "UPDATE RoomBooking SET members = %s WHERE booking_id = %s",
            (json.dumps(members), booking_id),
        )

        cur.close()

    def schedule_personal_training_session(
        self, member_id, trainer_id, room_id, month, day, year, start_time, end_time
    ):
        if not self.trainer_is_available(
            trainer_id, month, day, year, start_time, end_time
        ):
            return False

        if not self.room_is_available(room_id, month, day, year, start_time, end_time):
            return False

        booking_id = self.book_room(room_id, month, day, year, start_time, end_time)

        self.add_member_to_room_booking(booking_id, member_id)

        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO PersonalTrainingSession (booking_id, trainer_id) VALUES (%s, %s) RETURNING personal_training_session_id",
            (booking_id, trainer_id),
        )

        personal_training_session_id = cur.fetchone()[0]

        return personal_training_session_id

    def join_group_fitness_class(self, member_id, group_fitness_class_id):
        cur = self.conn.cursor()

        # check if the group fitness class exists
        cur.execute(
            "SELECT * FROM GroupFitnessClass WHERE group_fitness_class_id = %s",
            (group_fitness_class_id,),
        )

        result = cur.fetchone()

        if result is None:
            return False

        # add a member to the associated room booking
        cur.execute(
            "SELECT booking_id FROM GroupFitnessClass WHERE group_fitness_class_id = %s",
            (group_fitness_class_id,),
        )

        booking_id = cur.fetchone()[0]

        self.add_member_to_room_booking(booking_id, member_id)

        cur.close()
        return True

    def get_user_personal_training_sessions(self, id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT personal_training_session_id, members FROM PersonalTrainingSession JOIN RoomBooking ON PersonalTrainingSession.booking_id = RoomBooking.booking_id WHERE members::jsonb @> %s::jsonb",
            (json.dumps([id]),),
        )

        result = cur.fetchall()
        cur.close()
        print(result)

        return result

    def get_user_group_fitness_classes(self, id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT group_fitness_class_id, members FROM GroupFitnessClass JOIN RoomBooking ON GroupFitnessClass.booking_id = RoomBooking.booking_id WHERE members::jsonb @> %s::jsonb",
            (json.dumps([id]),),
        )

        result = cur.fetchall()
        cur.close()
        return result

    def get_trainer_personal_training_sessions(self, id):
        # join with RoomBooking to get the date and time
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM PersonalTrainingSession JOIN RoomBooking ON PersonalTrainingSession.booking_id = RoomBooking.booking_id WHERE trainer_id = %s",
            (id,),
        )

        result = cur.fetchall()
        cur.close()
        return result

    def get_trainer_group_fitness_classes(self, id):
        # join with RoomBooking to get the date and time
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM GroupFitnessClass JOIN RoomBooking ON GroupFitnessClass.booking_id = RoomBooking.booking_id WHERE trainer_id = %s",
            (id,),
        )

        result = cur.fetchall()
        cur.close()
        return result

    def group_fitness_class_to_string(self, group_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM GroupFitnessClass JOIN RoomBooking ON GroupFitnessClass.booking_id = RoomBooking.booking_id WHERE group_fitness_class_id = %s",
            (group_id,),
        )

        # this is a tuple in the format of (group_fitness_class_id, booking_id, trainer_id, booking_id, room_id, month, day, year, start_time, end_time, members)

        result = cur.fetchone()
        cur.close()
        trainer_id = result[2]
        room_id = result[4]
        month = result[5]
        day = result[6]
        year = result[7]
        start_time = result[8]
        end_time = result[9]

        trainer_name = self.get_trainer_name_by_id(trainer_id)

        result = f"Trainer: {trainer_name}\nRoom: {room_id}\nDate: {month}/{day}/{year}\nTime: {start_time} - {end_time}"

        return result

    def training_session_to_string(self, session_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM PersonalTrainingSession JOIN RoomBooking ON PersonalTrainingSession.booking_id = RoomBooking.booking_id WHERE personal_training_session_id = %s",
            (session_id,),
        )
        result = cur.fetchone()

        # this is a tuple in the format of (personal_training_session_id, booking_id, trainer_id, booking_id, room_id, month, day, year, start_time, end_time, members)
        trainer_id = result[2]
        room_id = result[4]
        month = result[5]
        day = result[6]
        year = result[7]
        start_time = result[8]
        end_time = result[9]

        trainer_name = self.get_trainer_name_by_id(trainer_id)

        result = f"Trainer: {trainer_name}\nRoom: {room_id}\nDate: {month}/{day}/{year}\nTime: {start_time} - {end_time}"

        cur.close()
        return result

    def get_user_dashboard(self, id):

        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM Member WHERE member_id = %s",
            (id,),
        )

        result = cur.fetchone()
        cur.close()

        formatted_user_info = f"Name: {result[2]} {result[3]}\nEmail: {result[1]}\n Age: {result[6]}\nWeight: {result[7]}\nHeight: {result[8]}"

        print("Excersise Routines: ", self.get_member_exercise_routine(id))

        formatted_user_info += "\n\nPersonal Training Sessions:\n"

        for session in self.get_user_personal_training_sessions(id):
            room_info = self.training_session_to_string(session[0])
            formatted_user_info += str(room_info) + "\n\n"

        formatted_user_info += "\nGroup Fitness Classes:\n"
        for group in self.get_user_group_fitness_classes(id):
            room_info = self.group_fitness_class_to_string(group[0])
            formatted_user_info += str(room_info) + "\n\n"

        return formatted_user_info

    def does_trainer_exist(self, id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Trainer WHERE trainer_id = %s", (id,))
        result = cur.fetchone()
        cur.close()
        return result is not None

    def get_connection(self):
        return self.conn

    def get_all_trainers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Trainer")

        result = cur.fetchall()
        cur.close()

        return result

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

    def update_health_metrics(self, member_id, age, weight, height):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT metric_id FROM Member WHERE member_id = %s",
            (member_id,),
        )

        metric_id = cur.fetchone()[0]

        cur.execute(
            "UPDATE Metrics SET age = %s, weight = %s, height = %s WHERE metric_id = %s",
            (age, weight, height, metric_id),
        )

        cur.close()

    def add_fitness_goal(self, member_id, time, fitness_goal):
        cur = self.conn.cursor()

        time = datetime.datetime.now() + datetime.timedelta(days=time)
        time = time.strftime("%Y-%m-%d")

        cur.execute(
            "SELECT fitness_goals FROM Member WHERE member_id = %s",
            (member_id,),
        )

        fitness_goals = cur.fetchone()[0]

        if fitness_goals is None:
            fitness_goals = []
        else:
            fitness_goals = json.loads(fitness_goals)

        fitness_goals.append(
            {"time": time, "description": fitness_goal, "completed": False}
        )

        cur.execute(
            "UPDATE Member SET fitness_goals = %s WHERE member_id = %s",
            (json.dumps(fitness_goals), member_id),
        )

    def set_member_exercise_routine(self, member_id, exercise_routine):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE Member SET exercise_routines = %s WHERE member_id = %s",
            (exercise_routine, member_id),
        )

    def get_member_exercise_routine(self, member_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT exercise_routines FROM Member WHERE member_id = %s",
            (member_id,),
        )

        result = cur.fetchone()[0]
        cur.close()
        return result

    def complete_fitness_goal(self, member_id, goal_id):
        cur = self.conn.cursor()

        cur.execute(
            "SELECT fitness_goals FROM Member WHERE member_id = %s",
            (member_id,),
        )

        fitness_goals = cur.fetchone()[0]

        if fitness_goals is None:
            return

        # get the goal_idth goal
        fitness_goals[goal_id]["completed"] = True

        cur.execute(
            "UPDATE Member SET fitness_goals = %s WHERE member_id = %s",
            (json.dumps(fitness_goals), member_id),
        )

    def get_all_fitness_goals(self, member_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT fitness_goals FROM Member WHERE member_id = %s",
            (member_id,),
        )

        fitness_goals = cur.fetchone()[0]

        if fitness_goals is None:
            return None

        return fitness_goals


class DisplayTable:
    def __init__(self, db):
        self.db = db

    def display_room_bookings(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM RoomBooking")
        result = cur.fetchall()
        cur.close()

        print("Room Booking Table:")
        print("booking_id | room_id | month | day | year | start_time | end_time")
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

        print("Equipment:")
        print("equipment_id | equipment_name | quality | issue")
        for row in result:
            print(row)

    def display_trainers(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM Trainer")
        result = cur.fetchall()
        cur.close()

        print("Trainer Table:")
        print("trainer_id | first_name | last_name | unavailable_times")
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
