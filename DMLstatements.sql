-- Trainers
INSERT INTO
    Trainer (first_name, last_name)
VALUES
    ('Nathan', 'Coulas'),
    ('Julie', 'Wechsler'),
    ('Barack', 'Obama'),
    ('Robert', 'Collier');

-- Robert Collier is unavailable on 4/21/2024
UPDATE
    Trainer
SET
    unavailable_times = '["4/21/2024"]'
WHERE
    trainer_id = 4;

-- Trainer ratings cannot be done here because the member_id foreign key is not yet created

INSERT INTO
    Room (room_name, room_number)
VALUES
    ('Yoga Studio', 101),
    ('Weight Room', 102),
    ('Cardio Room', 103),
    ('Spin Room', 104);


-- there is a user with member_id = 1 (this is done in code so that the password is hashed)
-- personal training session
INSERT INTO
    RoomBooking (
        room_id,
        month,
        day,
        year,
        start_time,
        end_time,
        members
    )
VALUES
    (1, 1, 1, 2021, 10, 11, '1'),
    (2, 1, 1, 2021, 11, 12, '1');

INSERT INTO
    PersonalTrainingSession (booking_id, trainer_id)
VALUES
    (1, 1),
    (2, 2);

-- group fitness class
INSERT INTO
    RoomBooking (
        room_id,
        month,
        day,
        year,
        start_time,
        end_time,
        members
    )
VALUES
    (3, 1, 1, 2021, 10, 11, '1'),
    (4, 1, 1, 2021, 11, 12, '1');

INSERT INTO
    GroupFitnessClass (name, booking_id, trainer_id)
VALUES
    ('Yoga', 3, 1),
    ('Spin', 4, 2);


-- equipment
INSERT INTO
    Equipment (equipment_name, quality, issue)
VALUES
    ('Treadmill', '100', NULL),
    ('Dumbbells', '70', 'broken'),
    ('Assisted Pullup Machine', '90', NULL),
    ('Bench Press', '80', 'missing a screw'),
    ('Leg Press', '100', NULL),
    ('Squat Rack', '100', NULL),
    ('Barbell', '100', NULL),
    ('Kettlebell', '100', NULL),
    ('Medicine Ball', '100', NULL),
    ('Jump Rope', '100', NULL),
    ('Resistance Bands', '100', NULL),
    ('Yoga Mat', '100', NULL),
    ('Foam Roller', '100', NULL),
    ('Bosu Ball', '100', NULL),
    ('Stability Ball', '100', NULL),
    ('Boxing Gloves', '100', NULL),
    ('Boxing Bag', '100', NULL),
    ('Speed Bag', '100', NULL),
    ('Punching Mitts', '100', NULL),
    ('Kettlebell Rack', '100', NULL),
    ('Dumbbell Rack', '100', NULL),
    ('Barbell Rack', '100', NULL),
    ('Weight Plate Rack', '100', NULL),
    ('Weight Bench', '100', NULL),
    ('Leg Curl Machine', '100', NULL),
    ('Leg Extension Machine', '100', NULL),
    ('Cable Machine', '100', NULL),
    ('Lat Pulldown Machine', '100', NULL),
    ('Row Machine', '100', NULL),
    ('Stationary Bike', '100', NULL),
    ('Rowing Machine', '100', NULL),
    ('Squat Machine', '100', NULL),
    ('Hack Squat Machine', '100', NULL),
    ('Calf Raise Machine', '100', NULL),
    ('Leg Press Machine', '100', NULL),
    ('Glute Ham Raise Machine', '100', NULL),
    ('Seated Leg Curl Machine', '100', NULL) 