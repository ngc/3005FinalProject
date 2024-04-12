INSERT INTO Metrics (age, weight, height) VALUES (25, 150, 130), (30, 180, 180);
INSERT INTO Member (email, first_name, last_name, metric_id) VALUES ('john.doe@gmail.com', 'John', 'Doe', 1), ('john.lu@cmail.com', 'John', 'Lu', 2);
INSERT INTO Equipment (equipment_name) VALUES ('Treadmill'), ('Dumbbells');
INSERT INTO ExerciseRoutine (repititions, sets, equipment_id) VALUES (10, 3, 1), (15, 2, 2);
INSERT INTO PersonalFitnessGoal (time, goal_description) VALUES (30, 'Run 5k'), (60, 'Lose 10 Pounds');
INSERT INTO FitnessAchievement (achievement) VALUES ('Completed 5k Run'), ('Lost 10 Pounds');
INSERT INTO Trainer (first_name, last_name) VALUES ('Nathan', 'Coulas'), ('Julie', 'Wechsler');
INSERT INTO TrainerShifts (trainer_id, scheduled_shifts, unavailable_times) VALUES (1, '{"1": [[9,10],[10,11]], "2": [[9,10],[10,11]], "5": [[9,10],[10,11]], "7": [[9,10],[10,11]]}', '{"4/11/2024": [[9,10]]}'), 
(2, '{"4": [[9,10],[10,11]], "5": [[9,10],[10,11]], "7": [[9,10],[10,11]]}', '        [
            {
                "day": 1,
                "start_time": 12:00,
                "end_time": 13:00
            }
        ]');


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
INSERT INTO PendingBill (member_id, amount) VALUES (1, 100), (2, 200);