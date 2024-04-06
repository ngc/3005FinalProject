from hmac import new
import psycopg2
from psycopg2 import Error


# creates the Club database
def createClubDatabase(conn):
    try:
        # Create cursor
        cur = conn.cursor()
        # Execute SQL query
        print("Starting Creating Club Database")
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

        cur.close()
        print("Finished Creating Club Database")
    except Error as e:
        print(e)


# deletes the student database
def deleteClubDatabase(conn):
    try:
        # Create cursor
        cur = conn.cursor()
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
    except Error as e:
        print(e)
