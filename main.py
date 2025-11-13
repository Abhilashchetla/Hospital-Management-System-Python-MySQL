import re
from datetime import date, datetime
from python_connection import get_connection


def validate_name(name):
    return bool(re.fullmatch(r"[A-Za-z ]+", name))

def validate_username(username):
    return bool(re.fullmatch(r"[A-Za-z0-9]+", username))

def validate_phone(phone):
    return bool(re.fullmatch(r"\d{10}", phone))

def validate_age(age):
    return age.isdigit() and 0 < int(age) <= 120

def validate_password(password):
    return len(password) >= 4

def validate_time(time_str):
    """Accept both 12-hour (HH:MM AM/PM) and 24-hour (HH:MM)."""
    try:
        datetime.strptime(time_str.strip().upper(), "%I:%M %p")
        return True
    except ValueError:
        try:
            datetime.strptime(time_str.strip(), "%H:%M")
            return True
        except ValueError:
            return False
class Hospital:
    def __init__(self):
        self.con = get_connection()
        self.cursor = self.con.cursor()

    def login(self, username, password):
        self.cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))
        user = self.cursor.fetchone()
        if user:
            print(f"\n Login successful as {user[0].upper()}\n")
            return user[0]
        else:
            print("\n Invalid username or password\n")
            return None

    def register_patient(self, username, password, name, age, gender, phone, address, problem):
        # validations
        if not validate_username(username):
            print(" Username must contain only letters and numbers.")
            return
        if not validate_password(password):
            print(" Password must be at least 4 characters.")
            return
        if not validate_name(name):
            print(" Name should only contain alphabets and spaces.")
            return
        if not validate_age(str(age)):
            print(" Age must be between 1 and 120.")
            return
        if gender.lower() not in ['male', 'female', 'other']:
            print(" Gender must be Male, Female, or Other.")
            return
        if not validate_phone(phone):
            print("Phone must be exactly 10 digits.")
            return
        if not problem.strip() or not address.strip():
            print(" Problem/Address cannot be empty.")
            return

        # check duplicate username
        self.cursor.execute("SELECT username FROM users WHERE username=%s", (username,))
        if self.cursor.fetchone():
            print("This username is already taken. Please choose another.")
            return

        # check duplicate phone in patients
        self.cursor.execute("SELECT phone FROM patients WHERE phone=%s", (phone,))
        if self.cursor.fetchone():
            print("This phone number is already registered. Please use another number.")
            return

        # insert patient
        self.cursor.execute(
            "INSERT INTO patients (name, age, gender, phone, address, problem) VALUES (%s,%s,%s,%s,%s,%s)",
            (name, age, gender, phone, address, problem)
        )
        self.con.commit()

        # insert user
        self.cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s,%s,'patient')",
            (username, password)
        )
        self.con.commit()

        print(" Patient registered successfully! You can now log in.")

    def add_patient(self, name, age, gender, phone, address, problem):
        if not validate_name(name) or not validate_age(str(age)) or not validate_phone(phone):
            print("Invalid details. Please check input.")
            return
        # duplicate phone prevent
        self.cursor.execute("SELECT phone FROM patients WHERE phone=%s", (phone,))
        if self.cursor.fetchone():
            print("⚠️ This phone number is already registered. Use another.")
            return
        self.cursor.execute(
            "INSERT INTO patients (name, age, gender, phone, address, problem) VALUES (%s,%s,%s,%s,%s,%s)",
            (name, age, gender, phone, address, problem)
        )
        self.con.commit()
        print(" Patient added successfully")

    def view_patients(self):
        print("\n--- PATIENTS ---")
        self.cursor.execute("SELECT * FROM patients")
        patients = self.cursor.fetchall()
        if not patients:
            print("No patients found.")
        for p in patients:
            print(p)
        print()
    def add_doctor(self, name, specialization, phone):
        if not validate_name(name) or not validate_phone(phone):
            print("Invalid doctor details.")
            return

        # duplicate doctor phone check
        self.cursor.execute("SELECT phone FROM doctors WHERE phone=%s", (phone,))
        if self.cursor.fetchone():
            print("This phone number is already assigned to another doctor.")
            return

        self.cursor.execute(
            "INSERT INTO doctors (name, specialization, phone) VALUES (%s,%s,%s)",
            (name, specialization, phone)
        )
        self.con.commit()
        print("Doctor added successfully")

    def view_doctors(self):
        print("\n--- DOCTORS ---")
        self.cursor.execute("SELECT * FROM doctors")
        doctors = self.cursor.fetchall()
        if not doctors:
            print("No doctors found.")
        for d in doctors:
            print(d)
        print()
    def add_doctor_schedule(self, doctor_id, day_of_week, start_time, end_time):
        # verify doctor exists
        self.cursor.execute("SELECT doctor_id FROM doctors WHERE doctor_id=%s", (doctor_id,))
        if not self.cursor.fetchone():
            print("Doctor ID not found. Please add the doctor first.")
            return

        if not validate_time(start_time) or not validate_time(end_time):
            print("Invalid time format (use HH:MM AM/PM or HH:MM).")
            return

        # convert to 24-hour string HH:MM:SS
        start_24 = datetime.strptime(start_time.strip().upper(), "%I:%M %p").strftime("%H:%M:%S") if ("AM" in start_time.upper() or "PM" in start_time.upper()) else start_time + ":00"
        end_24 = datetime.strptime(end_time.strip().upper(), "%I:%M %p").strftime("%H:%M:%S") if ("AM" in end_time.upper() or "PM" in end_time.upper()) else end_time + ":00"

        if start_24 >= end_24:
            print("Start time must be earlier than end time.")
            return

        # check overlapping schedules for same doctor & same day
        self.cursor.execute("SELECT start_time, end_time FROM doctor_schedule WHERE doctor_id=%s AND day_of_week=%s", (doctor_id, day_of_week))
        existing = self.cursor.fetchall()
        for ex in existing:
            ex_start = datetime.strptime(str(ex[0]), "%H:%M:%S")
            ex_end = datetime.strptime(str(ex[1]), "%H:%M:%S")
            new_start = datetime.strptime(start_24, "%H:%M:%S")
            new_end = datetime.strptime(end_24, "%H:%M:%S")
            # overlap if new_start < ex_end and new_end > ex_start
            if new_start < ex_end and new_end > ex_start:
                print("Schedule overlaps with existing time slot for this doctor.")
                return

        self.cursor.execute(
            "INSERT INTO doctor_schedule (doctor_id, day_of_week, start_time, end_time) VALUES (%s,%s,%s,%s)",
            (doctor_id, day_of_week, start_24, end_24)
        )
        self.con.commit()
        print("Doctor schedule added successfully.")

    def view_doctor_schedule(self):
        print("\n--- DOCTOR SCHEDULE ---")
        self.cursor.execute("SELECT * FROM doctor_schedule")
        schedules = self.cursor.fetchall()
        if not schedules:
            print("No schedules found.")
        for s in schedules:
            self.cursor.execute("SELECT name FROM doctors WHERE doctor_id=%s", (s[1],))
            doc = self.cursor.fetchone()
            doctor_name = doc[0] if doc else "Unknown"
            start_12 = datetime.strptime(str(s[3]), "%H:%M:%S").strftime("%I:%M %p")
            end_12 = datetime.strptime(str(s[4]), "%H:%M:%S").strftime("%I:%M %p")
            print(f"Doctor: {doctor_name} | Day: {s[2]} | Time: {start_12} - {end_12}")
        print()

    def suggest_doctor_by_problem(self, problem):
        mapping = {
            'heart': 'Cardiologist',
            'chest pain': 'Cardiologist',
            'fever': 'General Physician',
            'cold': 'General Physician',
            'stomach': 'Gastroenterologist',
            'eye': 'Ophthalmologist',
            'skin': 'Dermatologist',
            'bone': 'Orthopedic',
            'pregnancy': 'Gynecologist',
            'tooth': 'Dentist',
            'cancer': 'Oncologist'
        }

        specialization = None
        for key in mapping:
            if key in problem.lower():
                specialization = mapping[key]
                break

        if specialization:
            print(f"\nSuggested Department: {specialization}")
            self.cursor.execute("SELECT doctor_id, name, specialization FROM doctors WHERE specialization=%s", (specialization,))
            doctors = self.cursor.fetchall()
            if doctors:
                for d in doctors:
                    print(f"Doctor ID: {d[0]} | Name: {d[1]} | Specialization: {d[2]}")
            else:
                print(" No doctor available in this specialization.")
        else:
            print("No specialization match found. Please choose manually.")
            self.view_doctors()

    def book_appointment(self, patient_id, doctor_id, app_date, app_time):
        # verify patient & doctor exist
        self.cursor.execute("SELECT patient_id FROM patients WHERE patient_id=%s", (patient_id,))
        if not self.cursor.fetchone():
            print("Invalid Patient ID. Please register first.")
            return

        self.cursor.execute("SELECT doctor_id FROM doctors WHERE doctor_id=%s", (doctor_id,))
        if not self.cursor.fetchone():
            print("Invalid Doctor ID.")
            return

        if not validate_time(app_time):
            print(" Invalid time format (use HH:MM AM/PM or HH:MM).")
            return

        app_time_24 = datetime.strptime(app_time.strip().upper(), "%I:%M %p").strftime("%H:%M:%S") if ("AM" in app_time.upper() or "PM" in app_time.upper()) else app_time + ":00"

        # check doctor availability in schedule for that day/time (optional)
        day_name = datetime.strptime(app_date, "%Y-%m-%d").strftime("%A")
        self.cursor.execute("""
            SELECT start_time, end_time FROM doctor_schedule
            WHERE doctor_id=%s AND day_of_week=%s
        """, (doctor_id, day_name))
        sch = self.cursor.fetchall()
        if not sch:
            print(" Doctor has no schedule on that day. Booking allowed but check availability.")
        else:
            # ensure appointment time within at least one schedule block
            appt_time_obj = datetime.strptime(app_time_24, "%H:%M:%S")
            within = False
            for block in sch:
                bstart = datetime.strptime(str(block[0]), "%H:%M:%S")
                bend = datetime.strptime(str(block[1]), "%H:%M:%S")
                if appt_time_obj >= bstart and appt_time_obj < bend:
                    within = True
                    break
            if not within:
                print("Appointment time is outside doctor's scheduled hours. Please choose a time within schedule.")
                return

        # check duplicate slot
        self.cursor.execute(
            "SELECT * FROM appointments WHERE doctor_id=%s AND appointment_date=%s AND appointment_time=%s",
            (doctor_id, app_date, app_time_24)
        )
        if self.cursor.fetchone():
            print(" Slot already booked.")
            return

        # insert appointment
        self.cursor.execute(
            "INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time) VALUES (%s,%s,%s,%s)",
            (patient_id, doctor_id, app_date, app_time_24)
        )
        self.con.commit()
        print(f"Appointment booked for {app_date} at {app_time.upper()}")

        # auto billing logic (ask paid/pending)
        specialization_fees = {
            'Cardiologist': 1500,
            'Dermatologist': 800,
            'General Physician': 600,
            'Gynecologist': 1000,
            'Orthopedic': 900,
            'Gastroenterologist': 1200,
            'Ophthalmologist': 700,
            'Dentist': 500,
            'Oncologist': 2000
        }

        self.cursor.execute("SELECT specialization FROM doctors WHERE doctor_id=%s", (doctor_id,))
        spec = self.cursor.fetchone()[0]
        fee = specialization_fees.get(spec, 600)
        today = date.today()

        status = input("Enter payment status (Paid/Pending): ").capitalize()
        if status not in ['Paid', 'Pending']:
            status = 'Pending'

        self.cursor.execute(
            "INSERT INTO billing (patient_id, doctor_id, total_amount, payment_status, bill_date) VALUES (%s,%s,%s,%s,%s)",
            (patient_id, doctor_id, fee, status, today)
        )
        self.con.commit()
        print(f"Bill generated: ₹{fee} ({spec}) | Status: {status}")

    def cancel_appointment(self, appointment_id):
        self.cursor.execute("SELECT appointment_id FROM appointments WHERE appointment_id=%s", (appointment_id,))
        if not self.cursor.fetchone():
            print("Appointment ID not found.")
            return
        confirm = input("Are you sure you want to cancel this appointment? (yes/no): ").lower()
        if confirm != 'yes':
            print("Cancellation aborted.")
            return
        # delete appointment
        self.cursor.execute("DELETE FROM appointments WHERE appointment_id=%s", (appointment_id,))
        self.con.commit()
        print("Appointment cancelled successfully.")
        # optionally: we keep billing record (administrator can handle refunds separately)

    def view_appointments(self):
        print("\n--- APPOINTMENTS ---")
        self.cursor.execute("SELECT * FROM appointments")
        apps = self.cursor.fetchall()
        if not apps:
            print("No appointments found.")
        for a in apps:
            pid, did = a[1], a[2]
            self.cursor.execute("SELECT name FROM patients WHERE patient_id=%s", (pid,))
            p = self.cursor.fetchone()
            pname = p[0] if p else "Unknown"
            self.cursor.execute("SELECT name FROM doctors WHERE doctor_id=%s", (did,))
            d = self.cursor.fetchone()
            dname = d[0] if d else "Unknown"
            time_12 = datetime.strptime(str(a[4]), "%H:%M:%S").strftime("%I:%M %p")
            print(f"Appointment ID: {a[0]} | Patient: {pname} | Doctor: {dname} | Date: {a[3]} | Time: {time_12}")
        print()

    def view_bills(self):
        print("\n--- BILLS ---")
        self.cursor.execute("SELECT * FROM billing")
        bills = self.cursor.fetchall()
        if not bills:
            print("No bills found.")
        for b in bills:
            print(b)
        print()

    def view_patient_summary(self, patient_id):
        self.cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (patient_id,))
        patient = self.cursor.fetchone()
        if not patient:
            print("No patient found.")
            return
        print(f"\n--- PATIENT SUMMARY ---\nID: {patient[0]} | Name: {patient[1]} | Age: {patient[2]} | Gender: {patient[3]}")
        print(f"Phone: {patient[4]} | Address: {patient[5]} | Problem: {patient[6]}")
        print("\n--- BILLING DETAILS ---")
        self.cursor.execute("SELECT total_amount, payment_status, bill_date FROM billing WHERE patient_id=%s", (patient_id,))
        bills = self.cursor.fetchall()
        if not bills:
            print("No billing records.")
        for bill in bills:
            print(f"Amount: ₹{bill[0]} | Status: {bill[1]} | Date: {bill[2]}")
        print()


def staff_menu(h):
    while True:
        print("\n" + "="*50)
        print("                STAFF MENU")
        print("="*50)
        print("1. Add Patient")
        print("2. View Patients")
        print("3. Add Doctor")
        print("4. View Doctors")
        print("5. Add Doctor Schedule")
        print("6. View Doctor Schedule")
        print("7. Book Appointment (Auto-Suggest + Bill)")
        print("8. View Appointments")
        print("9. View Bills")
        print("10. View Patient Summary")
        print("11. Cancel Appointment")
        print("12. Logout")
        print("="*50)
        c = input("Enter choice: ").strip()
        if c == '1':
            h.add_patient(input("Name: "), input("Age: "), input("Gender: "), input("Phone: "), input("Address: "), input("Problem: "))
        elif c == '2':
            h.view_patients()
        elif c == '3':
            h.add_doctor(input("Doctor Name: "), input("Specialization: "), input("Phone: "))
        elif c == '4':
            h.view_doctors()
        elif c == '5':
            h.add_doctor_schedule(int(input("Doctor ID: ")), input("Day: "), input("Start (HH:MM AM/PM): "), input("End (HH:MM AM/PM): "))
        elif c == '6':
            h.view_doctor_schedule()
        elif c == '7':
            pid = int(input("Patient ID: "))
            h.cursor.execute("SELECT problem FROM patients WHERE patient_id=%s", (pid,))
            pdata = h.cursor.fetchone()
            if pdata:
                problem = pdata[0]
                print(f"\nPatient Problem: {problem}")
                h.suggest_doctor_by_problem(problem)
            did = int(input("Enter Doctor ID to book: "))
            h.book_appointment(pid, did, input("Date (YYYY-MM-DD): "), input("Time (HH:MM AM/PM): "))
        elif c == '8':
            h.view_appointments()
        elif c == '9':
            h.view_bills()
        elif c == '10':
            h.view_patient_summary(int(input("Enter Patient ID: ")))
        elif c == '11':
            h.cancel_appointment(int(input("Enter Appointment ID to cancel: ")))
        elif c == '12':
            confirm = input("Are you sure you want to logout? (yes/no): ").lower()
            if confirm == 'yes':
                break
        else:
            print("Invalid choice. Try again.")


def patient_menu(h):
    while True:
        print("\n" + "="*50)
        print("              PATIENT MENU")
        print("="*50)
        print("1. View Doctors")
        print("2. View Doctor Schedule")
        print("3. Book Appointment")
        print("4. View My Appointments")
        print("5. Cancel Appointment")
        print("6. Logout")
        print("="*50)
        c = input("Enter choice: ").strip()
        if c == '1':
            h.view_doctors()
        elif c == '2':
            h.view_doctor_schedule()
        elif c == '3':
            h.book_appointment(int(input("Your Patient ID: ")), int(input("Doctor ID: ")), input("Date (YYYY-MM-DD): "), input("Time (HH:MM AM/PM): "))
        elif c == '4':
            h.view_appointments()
        elif c == '5':
            h.cancel_appointment(int(input("Enter Appointment ID to cancel: ")))
        elif c == '6':
            confirm = input("Logout? (yes/no): ").lower()
            if confirm == 'yes':
                break
        else:
            print("Invalid choice. Try again.")

def main():
    h = Hospital()
    while True:
        print("\n" + "="*50)
        print("        === AV* HOSPITAL MANAGEMENT SYSTEM ===")
        print("="*50)
        print("1. Login")
        print("2. Register as New Patient")
        print("3. Exit")
        print("="*50)
        choice = input("Enter choice: ").strip()
        if choice == '1':
            role = h.login(input("Username: "), input("Password: "))
            if role == 'staff':
                staff_menu(h)
            elif role == 'patient':
                patient_menu(h)
        elif choice == '2':
            print("\n--- PATIENT REGISTRATION ---")
            h.register_patient(
                input("Create Username: "),
                input("Create Password: "),
                input("Full Name: "),
                input("Age: "),
                input("Gender: "),
                input("Phone: "),
                input("Address: "),
                input("Problem: ")
            )
        elif choice == '3':
            print("Exiting system")
            break
        else:
            print("Invalid choice. Try again.")

print("\nStarting AV* Hospital Management System.\n")
main()
