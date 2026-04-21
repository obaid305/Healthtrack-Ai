@echo off
mkdir templates 2>nul

echo Creating template files...

:: Create base.html if it doesn't exist
if not exist templates\base.html (
    echo Creating base.html...
    copy nul templates\base.html
)

:: Create index.html
echo Creating index.html...
copy nul templates\index.html

:: Create login.html
echo Creating login.html...
copy nul templates\login.html

:: Create register.html
echo Creating register.html...
copy nul templates\register.html

:: Create find_doctors.html
echo Creating find_doctors.html...
copy nul templates\find_doctors.html

:: Create symptom_checker.html
echo Creating symptom_checker.html...
copy nul templates\symptom_checker.html

:: Create doctor_profile.html
echo Creating doctor_profile.html...
copy nul templates\doctor_profile.html

:: Create appointments.html
echo Creating appointments.html...
copy nul templates\appointments.html

:: Create book_appointment.html
echo Creating book_appointment.html...
copy nul templates\book_appointment.html

:: Create error.html
echo Creating error.html...
copy nul templates\error.html

echo All template files created!
pause