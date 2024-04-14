
CREATE TABLE IF NOT EXISTS Member (member_id SERIAL PRIMARY KEY, email VARCHAR(255) UNIQUE, first_name VARCHAR(255), last_name VARCHAR(255), password VARCHAR(255), salt VARCHAR(255), age INT, weight DECIMAL, height DECIMAL, fitness_goals JSONB);
CREATE TABLE IF NOT EXISTS Equipment (equipment_id SERIAL PRIMARY KEY, equipment_name VARCHAR(255), quality INT DEFAULT 100, issue VARCHAR(255));
CREATE TABLE IF NOT EXISTS Trainer (trainer_id SERIAL PRIMARY KEY, first_name VARCHAR(255), last_name VARCHAR(255), unavailable_times TEXT);
CREATE TABLE IF NOT EXISTS Room (room_id SERIAL PRIMARY KEY, room_name VARCHAR(255), room_number INT);
CREATE TABLE IF NOT EXISTS RoomBooking (booking_id SERIAL PRIMARY KEY, room_id INT, month INT, day INT, year INT, start_time INT, end_time INT, FOREIGN KEY (room_id) REFERENCES Room(room_id), members TEXT);
CREATE TABLE IF NOT EXISTS PersonalTrainingSession (personal_training_session_id SERIAL PRIMARY KEY, booking_id INT, FOREIGN KEY (booking_id) REFERENCES RoomBooking(booking_id), trainer_id INT, FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id));
CREATE TABLE IF NOT EXISTS GroupFitnessClass (group_fitness_class_id SERIAL PRIMARY KEY, name VARCHAR(255), booking_id INT, FOREIGN KEY (booking_id) REFERENCES RoomBooking(booking_id), trainer_id INT, FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id));
CREATE TABLE IF NOT EXISTS PendingBill (bill_id SERIAL PRIMARY KEY, member_id INT, amount DECIMAL, FOREIGN KEY (member_id) REFERENCES Member(member_id));
CREATE TABLE IF NOT EXISTS TrainerRating (rating_id SERIAL PRIMARY KEY, trainer_id INT, rating INT, submited_by INT, FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id), FOREIGN KEY (submited_by) REFERENCES Member(member_id) ON DELETE CASCADE, check (rating >= 1 AND rating <= 5));

-- 