import psycopg2
from dotenv import load_dotenv
import os

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
        print("Starting Creating Club Database")
        cur = self.conn.cursor()
        with open('DMLstatements.sql', 'r') as file:
            sql = file.read()
            cur.execute(sql)
            self.conn.commit()

        cur.close()

    def init_db(self):
        print("Starting populating  Club Database")
        cur = self.conn.cursor()
        with open('DDLstatements.sql', 'r') as file:
            sql = file.read()
            cur.execute(sql)
            self.conn.commit()

        cur.close()

    def drop_db(self):
        cur = self.conn.cursor()
        print("Starting Deleting Club Database")
        # Drop tables in reverse
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
        cur.execute("DROP TABLE IF EXISTS Trainer")
        cur.execute("DROP TABLE IF EXISTS FitnessAchievement")
        cur.execute("DROP TABLE IF EXISTS PersonalFitnessGoal")
        cur.execute("DROP TABLE IF EXISTS ExerciseRoutine")
        cur.execute("DROP TABLE IF EXISTS Equipment")
        cur.execute("DROP TABLE IF EXISTS Member")
        cur.execute("DROP TABLE IF EXISTS Metrics")
        cur.close()
        print("Finished Deleting Club Database")

    def does_user_exist(self, email):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Member WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()
        return result is not None

    def get_user_id(self, email):
        cur = self.conn.cursor()
        cur.execute("SELECT member_id FROM Member WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()
        return result[0]

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

    def update_user(self, email, first_name, last_name, age, weight, height):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT metric_id FROM Member WHERE email = %s",
            (email,),
        )
        metric_id = cur.fetchone()[0]
        cur.execute(
            "UPDATE Metrics SET age = %s, weight = %s, height = %s WHERE metric_id = %s",
            (age, weight, height, metric_id),
        )
        cur.execute(
            "UPDATE Member SET first_name = %s, last_name = %s WHERE email = %s",
            (first_name, last_name, email),
        )
        cur.close()

    def get_user_dashboard(self, email):
        # returns a string with all the user's information
        cur = self.conn.cursor()
        cur.execute(
            "SELECT first_name, last_name, age, weight, height FROM Member JOIN Metrics ON Member.metric_id = Metrics.metric_id WHERE email = %s",
            (email,),
        )

        result = cur.fetchone()
        cur.close()
        return result

    def does_trainer_exist(self, id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Trainer WHERE trainer_id = %s", (id,))
        result = cur.fetchone()
        cur.close()
        return result is not None

    def get_connection(self):
        return self.conn
