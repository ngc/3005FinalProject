INSERT INTO Metrics (age, weight, height) VALUES (25, 150, 130), (30, 180, 180);
INSERT INTO Member (email, first_name, last_name, metric_id) VALUES ('john.doe@gmail.com', 'John', 'Doe', 1), ('john.lu@cmail.com', 'John', 'Lu', 2);
INSERT INTO Equipment (equipment_name) VALUES ('Treadmill'), ('Dumbbells');
INSERT INTO ExerciseRoutine (repititions, sets, equipment_id) VALUES (10, 3, 1), (15, 2, 2);
INSERT INTO PersonalFitnessGoal (weight, time) VALUES (145, 30), (160.0, 60);
INSERT INTO FitnessAchievement (achievement) VALUES ('Completed 5k Run'), ('Lost 10 Pounds');
INSERT INTO Trainer (first_name, last_name, start_time, end_time) VALUES ('Nathan', 'Coulas', '08:00:00', '12:00:00'), ('Julie', 'Wechsler', '13:00:00', '17:00:00');
INSERT INTO Room (room_name, room_number) VALUES ('Yoga Studio', 101), ('Weight Room', 102);
INSERT INTO PersonalTrainingSession (room_id) VALUES (1), (2);
INSERT INTO GroupFitnessClass (name) VALUES ('Yoga Class'), ('Strength Training');
INSERT INTO Performs (member_id, exercise_routine_id) VALUES (1, 1), (2, 2);
INSERT INTO Has (member_id, goal_id) VALUES (1, 1), (2, 2);
INSERT INTO Achieved (member_id, achievement_id) VALUES (1, 1), (2, 2);
INSERT INTO Teaches (trainer_id, personal_training_session_id, start_time, end_time) VALUES (1, 1, '09:00:00', '10:00:00'), (2, 2, '14:00:00', '15:00:00');
INSERT INTO Attends (member_id, personal_training_session_id) VALUES (1, 1), (2, 2);
INSERT INTO Frequents (member_id, group_fitness_class_id) VALUES (1, 1), (2, 2);
INSERT INTO Uses (group_fitness_class_id, room_id, start_time, end_time) VALUES (1, 1, '08:00:00', '09:00:00'), (2, 2, '10:00:00', '11:00:00');
INSERT INTO Employs (exercise_routine_id, equipment_id) VALUES (1, 1), (2, 2);

