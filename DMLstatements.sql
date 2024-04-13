INSERT INTO Metrics (age, weight, height) VALUES (25, 150, 130), (30, 180, 180), (30, 180, 180);
INSERT INTO Member (email, first_name, last_name, metric_id) VALUES ('john.doe@gmail.com', 'John', 'Doe', 1), ('john.lu@cmail.com', 'John', 'Lu', 2), ('julie', 'Julie', 'Lu', 3);



INSERT INTO Equipment (equipment_name, quality, issue) VALUES ('Treadmill', 100, 'none'), ('Dumbbells',70, 'broken' );
INSERT INTO ExerciseRoutine (repititions, sets) VALUES (10, 3), (15, 2);
INSERT INTO PersonalFitnessGoal (time, goal_description) VALUES (30, 'Run 5k'), (60, 'Lose 10 Pounds');
INSERT INTO FitnessAchievement (achievement) VALUES ('Completed 5k Run'), ('Lost 10 Pounds');
INSERT INTO Trainer (first_name, last_name) VALUES ('Nathan', 'Coulas'), ('Julie', 'Wechsler');
INSERT INTO Room (room_name, room_number) VALUES ('Yoga Studio', 101), ('Weight Room', 102);
-- INSERT INTO PersonalTrainingSession (room_id) VALUES (1), (2);
-- INSERT INTO GroupFitnessClass (name) VALUES ('Yoga Class'), ('Strength Training');
INSERT INTO Performs (member_id, exercise_routine_id) VALUES (1, 1), (2, 2);
INSERT INTO Has (member_id, goal_id) VALUES (1, 1), (2, 2);
INSERT INTO Achieved (member_id, achievement_id) VALUES (1, 1), (2, 2);
INSERT INTO PendingBill (member_id, amount) VALUES (1, 100), (2, 200);

INSERT INTO RoomBooking (room_id, month, day, year, start_time, end_time, members) values (1, 1, 1, 2024, 1, 3, '[1,2]'), (2, 3, 1, 2022, 1, 3, '[1]'); 
INSERT INTO PersonalTrainingSession (booking_id, trainer_id) values  (2, 1);
INSERT INTO GroupFitnessClass (name, booking_id, trainer_id) values ('pilates', 1, 1);

