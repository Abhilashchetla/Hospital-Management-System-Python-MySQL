create database mini_project;
use mini_project;

CREATE TABLE users (user_id INT PRIMARY KEY AUTO_INCREMENT,username VARCHAR(50) UNIQUE NOT NULL,password VARCHAR(100) NOT NULL,role ENUM('staff', 'patient') NOT NULL);
select *from users;
CREATE TABLE patients (patient_id INT PRIMARY KEY AUTO_INCREMENT,name VARCHAR(50) NOT NULL,age INT CHECK (age > 0 AND age <= 120),gender ENUM('Male', 'Female', 'Other'),phone VARCHAR(15) UNIQUE NOT NULL,address VARCHAR(100) NOT NULL,
problem VARCHAR(100) NOT NULL);
CREATE TABLE doctors (doctor_id INT PRIMARY KEY AUTO_INCREMENT,name VARCHAR(50) NOT NULL,specialization VARCHAR(50) NOT NULL,phone VARCHAR(15) UNIQUE NOT NULL);
select *from doctors;
CREATE TABLE doctor_schedule (schedule_id INT PRIMARY KEY AUTO_INCREMENT,doctor_id INT NOT NULL,day_of_week VARCHAR(15) NOT NULL,start_time TIME NOT NULL,end_time TIME NOT NULL,FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
ON DELETE CASCADE ON UPDATE CASCADE);
CREATE TABLE appointments (appointment_id INT PRIMARY KEY AUTO_INCREMENT,patient_id INT NOT NULL,doctor_id INT NOT NULL,appointment_date DATE NOT NULL,appointment_time TIME NOT NULL,FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
ON DELETE CASCADE ON UPDATE CASCADE,FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE ON UPDATE CASCADE);
select *from appointments;
CREATE TABLE billing (bill_id INT PRIMARY KEY AUTO_INCREMENT,patient_id INT NOT NULL,doctor_id INT NOT NULL,total_amount DECIMAL(10,2) NOT NULL,payment_status VARCHAR(20) DEFAULT 'Paid',bill_date DATE NOT NULL,
FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE ON UPDATE CASCADE,FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE ON UPDATE CASCADE);
-- STAFF USER
INSERT INTO users (username, password, role) VALUES ('admin', '1234', 'staff');
INSERT INTO doctors (name, specialization, phone) VALUES
('Dr. Arjun', 'Cardiologist', '9999990001'),        -- ₹1500
('Dr. Priya', 'Dermatologist', '9999990002'),       -- ₹800
('Dr. Ravi', 'General Physician', '9999990003'),    -- ₹600
('Dr. Sneha', 'Gynecologist', '9999990004'),        -- ₹1000
('Dr. Raj', 'Orthopedic', '9999990005'),            -- ₹900
('Dr. Nikhil', 'Gastroenterologist', '9999990006'), -- ₹1200
('Dr. Kavya', 'Ophthalmologist', '9999990007'),     -- ₹700
('Dr. Varun', 'Dentist', '9999990008'),             -- ₹500
('Dr. Neha', 'Oncologist', '9999990009');           -- ₹2000
select *from doctor_schedule;
-- Dr. Arjun – Cardiologist
INSERT INTO doctor_schedule (doctor_id, day_of_week, start_time, end_time) VALUES
(1, 'Monday', '09:00:00', '13:00:00'),
(1, 'Thursday', '14:00:00', '18:00:00'),
(2, 'Tuesday', '10:00:00', '14:00:00'),
(2, 'Friday', '09:30:00', '13:30:00'),
(3, 'Wednesday', '09:30:00', '12:30:00'),
(3, 'Saturday', '10:00:00', '13:00:00'),
(4, 'Monday', '09:00:00', '15:00:00'),
(4, 'Thursday', '10:00:00', '14:00:00'),
(5, 'Friday', '08:30:00', '13:30:00'),
(5, 'Saturday', '14:00:00', '17:00:00'),
(6, 'Tuesday', '09:00:00', '13:00:00'),
(6, 'Friday', '11:00:00', '15:00:00'),
(7, 'Monday', '10:00:00', '14:00:00'),
(7, 'Thursday', '09:00:00', '12:00:00'),
(8, 'Tuesday', '09:30:00', '13:30:00'),
(8, 'Saturday', '10:00:00', '14:00:00'),
(9, 'Wednesday', '09:00:00', '12:00:00'),
(9, 'Friday', '14:00:00', '17:00:00');
