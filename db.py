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
    return start_time1 < end_time2 and start_time2 < end_time1


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

    def remove_class(self, group_fitness_class_id):
        cur = self.conn.cursor()
        cur.execute(
            "DELETE FROM GroupFitnessClass WHERE group_fitness_class_id = %s",
            (group_fitness_class_id,),
        )
        cur.close()

    # self.db.set_unavailable_time(
    #     self.trainer_id, day, month, year, start_time, end_time
    # )
    def set_unavailable_time(self, trainer_id, day, month, year, start_time, end_time):
        # add into trainer shifts unavailable times column

        cur = self.conn.cursor()
        cur.execute(
            "SELECT unavailable_times FROM TrainerShifts WHERE trainer_id = %s",
            (trainer_id,),
        )

        unavailable_times = cur.fetchone()[0]

        if unavailable_times is None:
            unavailable_times = {}
        else:
            unavailable_times = json.loads(unavailable_times)

        # this is an example of how the dictionary will look like '{"12/4/2024": [9,10], "13/4/2024": [9,10]}'
        date = f"{day}/{month}/{year}"
        if date in unavailable_times:
            unavailable_times[date].append(start_time)
            unavailable_times[date].append(end_time)
        else:
            unavailable_times[date] = [start_time, end_time]

        cur.execute(
            "UPDATE TrainerShifts SET unavailable_times = %s WHERE trainer_id = %s",
            (json.dumps(unavailable_times), trainer_id),
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
        cur.execute("DROP TABLE IF EXISTS Room CASCADE")
        cur.execute("DROP TABLE IF EXISTS TrainerShifts")
        cur.execute("DROP TABLE IF EXISTS Trainer")
        cur.execute("DROP TABLE IF EXISTS FitnessAchievement")
        cur.execute("DROP TABLE IF EXISTS PersonalFitnessGoal")
        cur.execute("DROP TABLE IF EXISTS ExerciseRoutine")
        cur.execute("DROP TABLE IF EXISTS Equipment")
        cur.execute("DROP TABLE IF EXISTS Member")
        cur.execute("DROP TABLE IF EXISTS Metrics")
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

        hex_hashed_password = result[5]
        hex_salt = result[6]

        cur.close()

        # unhexlify the hashed password and salt
        hashed_password = hashpw(password.encode("utf-8"), binascii.unhexlify(hex_salt))

        return hashed_password == binascii.unhexlify(hex_hashed_password)

    def register_user(
        self, email, first_name, last_name, age, weight, height, password
    ):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO Metrics (age, weight, height) VALUES (%s, %s, %s) RETURNING metric_id",
            (age, weight, height),
        )
        metric_id = cur.fetchone()[0]

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
            "INSERT INTO Member (email, first_name, last_name, metric_id, password, salt) VALUES (%s, %s, %s, %s, %s, %s) RETURNING member_id",
            (
                email,
                first_name,
                last_name,
                metric_id,
                hex_hashed_password,
                hex_salt,
            ),
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

    def trainer_is_available(self, trainer_id, month, day, year, start_time, end_time):
        return True

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

    def book_room(self, room_id, month, day, year, start_time, end_time, members):
        cur = self.conn.cursor()
        # return the booking id
        cur.execute(
            "INSERT INTO RoomBooking (room_id, month, day, year, start_time, end_time, members) VALUES (%s, %s, %s, %s, %s, %s) RETURNING booking_id",
            (room_id, month, day, year, start_time, end_time, NULL),
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
        # CREATE TABLE IF NOT EXISTS PersonalTrainingSession (personal_training_session_id SERIAL PRIMARY KEY, booking_id INT, FOREIGN KEY (booking_id) REFERENCES RoomBooking(booking_id), trainer_id INT, FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id));
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

        # add the member to the members list
        cur.execute(
            "SELECT members FROM GroupFitnessClass WHERE group_fitness_class_id = %s",
            (group_fitness_class_id,),
        )

        members = cur.fetchone()[0]
        if members is None:
            members = []
        else:
            members = json.loads(members)

        members.append(member_id)
        cur.execute(
            "UPDATE GroupFitnessClass SET members = %s WHERE group_fitness_class_id = %s",
            (json.dumps(members), group_fitness_class_id),
        )

        cur.close()
        return True

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

        scheduled_shifts_list = []
        for row in results:

            scheduled_shifts = json.loads(str(row[1]))
            print("the scheduled_shifts is ", scheduled_shifts)

            shifts = scheduled_shifts[str(weekday_num)]

            # break shifts up to be hourly
            hourly_shifts = []
            for shift in shifts:
                start_hour, end_hour = shift
                hourly_intervals = []
                for hour in range(start_hour, end_hour):
                    hourly_intervals.append([hour, hour + 1])
                hourly_shifts.extend(hourly_intervals)

            if str(weekday_num) in scheduled_shifts:
                # scheduled_shifts_list.append(scheduled_shifts[str(weekday_num)])
                scheduled_shifts_list.append(
                    {
                        "trainer_id": json.loads(str(row[0])),
                        "trainer name": self.get_trainer_name_by_id(row[0]),
                        "scheduled_shifts": hourly_shifts,
                    }
                )

                print("Available trainers:", scheduled_shifts_list)

        for entry in scheduled_shifts_list:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT unavailable_times FROM TrainerShifts WHERE trainer_id = %s",
                (entry["trainer_id"],),
            )
            results = cur.fetchall()
            cur.close()

            for times in results:
                print("times is", times)
                result = json.loads(str(times[0]))
                print("the result is ", result)

                for date_str, intervals in result.items():
                    print("Date:", date_str)
                    print("Intervals:")
                    for interval in intervals:
                        start_time, end_time = interval
                        print(f"  Start: {start_time}, End: {end_time}")

                # this is the date the trainer is unavailable for
                for date_str in result:
                    print("date string is", date_str)
                    date_str = date_str.replace(" ", "")
                    myday, mymonth, myyear = map(int, date_str.split("/"))
                    myyear = str(myyear)
                    print(" day is ", myday)
                    print(" year is ", myyear)

                    # check if they are unavailable on a day they normally work
                    print("days are ", str(myday), " and ", str(day))
                    print("months are ", str(mymonth), " and ", str(month))
                    print("year are ", str(myyear), " and ", str(year))
                    if (
                        int(myday) == int(day)
                        and int(month) == int(mymonth)
                        and int(year) == int(myyear)
                    ):
                        print("INSIDE HERE", start_time, " and ", end_time)
                        # now remove that trainers shifts from

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

    def display_room_bookings(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT * FROM RoomBooking")
        result = cur.fetchall()
        cur.close()

        print("Room Booking Table:")
        print("booking_id | room_id | month | day | year | start_time | end_time")
        for row in result:
            print(row)

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

        print("Equipment:")
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
