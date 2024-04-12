CREATE TABLE IF NOT EXISTS Metrics (metric_id SERIAL PRIMARY KEY, age INT, weight DECIMAL, height DECIMAL);
CREATE TABLE IF NOT EXISTS Member (member_id SERIAL PRIMARY KEY, email VARCHAR(255) UNIQUE, first_name VARCHAR(255), last_name VARCHAR(255), metric_id INT, FOREIGN KEY (metric_id) REFERENCES Metrics(metric_id), password VARCHAR(255), salt VARCHAR(255));
CREATE TABLE IF NOT EXISTS Equipment (equipment_id SERIAL PRIMARY KEY, equipment_name VARCHAR(255), quality INT DEFAULT 100, issue VARCHAR(255));
CREATE TABLE IF NOT EXISTS ExerciseRoutine (exercise_routine_id SERIAL PRIMARY KEY, repititions INT, sets INT, equipment_id INT, FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id));
CREATE TABLE IF NOT EXISTS PersonalFitnessGoal (goal_id SERIAL PRIMARY KEY, time INT, goal_description VARCHAR(255));
CREATE TABLE IF NOT EXISTS FitnessAchievement (achievement_id SERIAL PRIMARY KEY, achievement VARCHAR(255));
CREATE TABLE IF NOT EXISTS Trainer (trainer_id SERIAL PRIMARY KEY, first_name VARCHAR(255), last_name VARCHAR(255));
CREATE TABLE IF NOT EXISTS TrainerShifts (trainer_id INT, scheduled_shifts TEXT, unavailable_times TEXT, FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id));
CREATE TABLE IF NOT EXISTS Room (room_id SERIAL PRIMARY KEY, room_name VARCHAR(255), room_number INT, unavailable_times TEXT);

CREATE TABLE IF NOT EXISTS RoomBooking (booking_id SERIAL PRIMARY KEY, room_id INT, month INT, day INT, year INT, start_time TIME, end_time TIME, FOREIGN KEY (room_id) REFERENCES Room(room_id), members TEXT);

CREATE TABLE IF NOT EXISTS PersonalTrainingSession (personal_training_session_id SERIAL PRIMARY KEY, booking_id INT, FOREIGN KEY (booking_id) REFERENCES RoomBooking(booking_id), trainer_id INT, FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id));
CREATE TABLE IF NOT EXISTS GroupFitnessClass (group_fitness_class_id SERIAL PRIMARY KEY, name VARCHAR(255), booking_id INT, FOREIGN KEY (booking_id) REFERENCES RoomBooking(booking_id), trainer_id INT, FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id), members TEXT);


CREATE TABLE IF NOT EXISTS Performs (member_id INT, exercise_routine_id INT, FOREIGN KEY (member_id) REFERENCES Member(member_id), FOREIGN KEY (exercise_routine_id) REFERENCES ExerciseRoutine(exercise_routine_id));
CREATE TABLE IF NOT EXISTS Has (member_id INT, goal_id INT, FOREIGN KEY (member_id) REFERENCES Member(member_id), FOREIGN KEY (goal_id) REFERENCES PersonalFitnessGoal(goal_id));
CREATE TABLE IF NOT EXISTS Achieved (member_id INT, achievement_id INT, FOREIGN KEY (member_id) REFERENCES Member(member_id), FOREIGN KEY (achievement_id) REFERENCES FitnessAchievement(achievement_id));
CREATE TABLE IF NOT EXISTS Teaches (trainer_id INT, personal_training_session_id INT, start_time TIME, end_time TIME, FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id), FOREIGN KEY (personal_training_session_id) REFERENCES PersonalTrainingSession(personal_training_session_id)); 
CREATE TABLE IF NOT EXISTS Attends (member_id INT, personal_training_session_id INT, FOREIGN KEY (member_id) REFERENCES Member(member_id), FOREIGN KEY (personal_training_session_id) REFERENCES PersonalTrainingSession(personal_training_session_id));
CREATE TABLE IF NOT EXISTS Frequents (member_id INT, group_fitness_class_id INT, FOREIGN KEY (member_id) REFERENCES Member(member_id), FOREIGN KEY (group_fitness_class_id) REFERENCES GroupFitnessClass(group_fitness_class_id));
CREATE TABLE IF NOT EXISTS Employs (exercise_routine_id INT, equipment_id INT, FOREIGN KEY (exercise_routine_id) REFERENCES ExerciseRoutine(exercise_routine_id), FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id));
CREATE TABLE IF NOT EXISTS PendingBill (bill_id SERIAL PRIMARY KEY, member_id INT, amount DECIMAL, FOREIGN KEY (member_id) REFERENCES Member(member_id));
CREATE TABLE IF NOT EXISTS TrainerRating (rating_id SERIAL PRIMARY KEY, trainer_id INT, rating INT, submited_by INT, FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id), FOREIGN KEY (submited_by) REFERENCES Member(member_id) ON DELETE CASCADE, check (rating >= 1 AND rating <= 5));
