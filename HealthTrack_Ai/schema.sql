-- Create database
CREATE DATABASE IF NOT EXISTS healthtrackkai;
USE healthtrackkai;

-- Insert doctors from your Excel data
INSERT INTO doctors (hospital, name, qualification, specialization, timings) VALUES
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Shahzad Gul', 'MBBS, FCPS, (Medicine) , FCPS, (Rheumatology) MRCP,(Rheumatology) , SCE Rheumatology(UK), Post graduate Dip in Diabetes ( AKU, Karachi)', 'Rheumatologist', '11:00 AM - 02:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Niaz Akbar Afridi', 'MBBS, Diploma (Dermatology)', 'Dermatologist', '02:30 PM - 05:30 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Syed Danish Mehmood', 'MBBS, FCPS (Orthopaedic Surgery)', 'Orthopedic Surgeon', '03:00 PM - 05:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Arif Hussain', 'MBBS, FCPS (Paediatrics)', 'Pediatrician', '08:30 AM - 01:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Malik Ehsan', 'MBBS, MD (Neurology)', 'Neurologist', '04:00 PM - 06:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Abdul Qadeer Khan', 'MBBS, MS (Orthopaedic Surgery)', 'Orthopedic Surgeon', '10:00 AM - 02:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Muhammad Akram Khan', 'MBBS', 'Internal Medicine Specialist', '04:00 PM - 08:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Mubbashir Ali Baig', 'MBBS, MS Neurosurgery', 'Neuro Surgeon', '04:00 PM - 08:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Ayesha Imtiaz', 'MBBS, FCPS (Obstetrics & Gynaecology)', 'Gynecologist', '04:00 PM - 07:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Ghullam Kibriya', 'MBBS, MCPS Family Medicine, Diploma in Cardiology', 'Cardiologist', '08:30 AM - 02:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Nazneen Dilnawaz Pt', 'DPT', 'Physiotherapist', '09:00 AM - 01:30 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Syed Ali Akbar', 'MBBS, FCPS (General Surgery)', 'General Surgeon', '09:00 AM - 12:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Atif Khan', 'MBBS, FCPS (Surgery)', 'General Surgeon', '10:00 AM - 05:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Adnan Tahir', 'MBBS, MS (Cardiac Surgery)', 'Cardiac Surgeon', '09:00 AM - 02:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Anfal Tahir', 'MBBS', 'General Physician', '09:30 AM - 02:00 PM'),
('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Najam Siddiqui', 'MBBS, FCPS', 'Pediatrician', '10:00 AM - 10:00 PM'),
('Haripur International Hospital Haripur', 'Dr. Ibrahim Mushtaq', 'MBBS, FCPS (Neuro Surgery)', 'Neuro Surgeon', '10:00 AM - 02:00 PM'),
('Haripur International Hospital Haripur', 'Ms. Sidra Mufti', 'M.Phil (Psychology), Post Magistral Diploma in Clinical Psychology, M.Sc. (Psychology)', 'Psychologist', ''),
('Mehar General Hospital', 'Dr. Imran Ullah', 'MBBS , MCPS (PSYCHIATRY)', 'Psychiatrist', '10:00 AM - 05:00 PM'),
('Mehar General Hospital', 'Dr. Muhammad Ashraf', 'BDS', 'Dentist', '09:00 AM - 08:00 PM'),
('Yahya Hospital Haripur', 'Dr. Hina Shaukat', 'MBBS, FCPS (Gastroenterology), MRCP', 'Gastroenterologist', '04:00 PM - 06:30 PM'),
('Yahya Hospital Haripur', 'Dr. Zahid Hassan', 'MBBS, FCPS (Neurology), Fellowship In Stroke & vascular Neurology', 'Neurologist', '02:00 PM - 04:00 PM'),
('Yahya Hospital Haripur', 'Dr. Muhammad Umer Suleman', 'MBBS, R.M.P (Pak), G.M.C (U.K), I.M.C (Ireland)', 'General Practitioner', '09:00 AM - 05:00 PM'),
('Yahya Hospital Haripur', 'Dr. Muhammad Tahir', 'MBBS', 'General Practitioner', '03:00 PM - 05:30 PM');