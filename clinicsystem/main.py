# clinicmanager.py
# TODO - Implement patient stuff

import os
import tkinter as tk
import pickle

class MedicalStaff:
    def __init__(self, name, staffid, hoursworked):
        self.name = name
        self.staffid = staffid
        self.hoursworked = hoursworked

    def __str__(self):
        return f"{self.name} | {self.staffid} | {self.hoursworked} hrs"

class Nurse(MedicalStaff):
    def __init__(self, name, staffid, hoursworked, patients):
        super().__init__(name, staffid, hoursworked)
        self.patients = patients

    def __str__(self):
        return f"{self.name} | {self.staffid} | {self.hoursworked}  hrs | Patients attended: {self.patients}"

class Doctor(MedicalStaff):
    def __init__(self, name, staffid, hoursworked, budget):
        super().__init__(name, staffid, hoursworked)
        self.budget = budget

    def __str__(self):
        return f"{self.name} | Staff ID: {self.staffid} | {self.hoursworked} hrs | Budget: ${self.budget:.2f}"

class Patient:
    def __init__(self, name, contact, visits=0):
        self.name = name
        self.contact = contact
        self.visits = visits

    def calculate_priority(self):
        return self.visits

    def visit(self):
        self.visits += 1

    def __str__(self):
        return f"Patient: {self.name} | Visits: {self.visits}"

class VIPPatient(Patient):
    def __init__(self, name, contact, tier):
        super().__init__(name, contact)
        self.tier = tier

    def calculate_priority(self):
        return self.visits + 100

    def __str__(self):
        return f"VIP Patient: {self.name} | Tier: {self.tier} | Visits: {self.visits}"


class ClinicManager:
    def __init__(self):
        self.loggedin = False
        self.current_user = None
        self.hoursworked = 0
        self.accounts = {}  # username -> data dict
        self.patientstoday = {}
        self.clinicver = 1.0
        self.accounts_file = os.path.join(os.path.dirname(__file__), "accounts.pkl")
        self.patients_file = os.path.join(os.path.dirname(__file__), "patients.pkl")

        self.load_accounts()
        self.load_patients()

    # clearscreen
    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    # load and saving accounts
    def load_accounts(self):
        if os.path.exists(self.accounts_file):
            with open(self.accounts_file, "rb") as f:
                self.accounts = pickle.load(f)

    def save_accounts(self):
        with open(self.accounts_file, "wb") as f:
            pickle.dump(self.accounts, f)

    def load_patients(self):
        if os.path.exists(self.patients_file):
            with open(self.patients_file, "rb") as f:
                self.patientstoday = pickle.load(f)

    def save_patients(self):
        with open(self.patients_file, "wb") as f:
            pickle.dump(self.patientstoday, f)

    # user account functions
    def createuseraccount(self):
        if not self.loggedin:
            username = input("Enter a username (6-15 chars, no spaces): ")
            password = input("Enter a password: ")
            kind = input("Docter or Nurse Account?: (D/N) ").upper()

            if kind not in ("N", "D"):
                print("Please select a doctor or a nurse")
                return

            if 5 < len(username) < 16 and " " not in username:
                if username in self.accounts:
                    print("This username has already been taken by another user account")
                    return

                if kind == "N":
                    data = {"password": password, "kind": "Nurse", "hours_worked": 0, "patients_attended": 0}
                else:
                    data = {"password": password, "kind": "Doctor", "hours_worked": 0, "budget": 15000}

                self.accounts[username] = data
                self.current_user = username
                self.loggedin = True
                self.save_accounts()
                print(f"Account created. Logged in as {self.current_user}")
            else:
                print("Invalid username. Must be 6-15 chars with no spaces.")
        else:
            print(f"You are logged into {self.current_user}, please logout before creating a new account")

    def deleteuseraccount(self):
        if not self.loggedin:
            print("Please login to the account you wish to delete.")
            return

        inputyesno = input("Are you sure you want to delete the current user account? (Y/N): ").strip().upper()
        if inputyesno != "Y":
            print("Account deletion cancelled.")
            return

        if self.current_user in self.accounts:
            del self.accounts[self.current_user]
            self.save_accounts()
            print(f"Account '{self.current_user}' has been deleted.")
            self.loggedin = False
            self.current_user = None

    def listuseraccounts(self):
        if not self.accounts:
            print("No registered users.")
            return
        print("\nRegistered Users")
        print("=" * 30)
        for username, data in self.accounts.items():
            print(f"Username : {username}")
            print(f"Role     : {data['kind']}")
            print(f"Hours    : {data['hours_worked']} hrs")
            print("-" * 30)

    def login(self):
        if self.loggedin:
            print(f"Already logged in as {self.current_user}. Please logoff first.")
            return

        username = input("Enter username or Staff ID: ")
        password = input("Enter password: ")

        if username in self.accounts and self.accounts[username]["password"] == password:
            self.loggedin = True
            self.current_user = username
            print(f"Login successful. Logged in as {self.current_user}")
        else:
            print("Invalid username or password.")

    def logoff(self):
        if self.loggedin:
            print(f"Logging out of {self.current_user}")
            self.loggedin = False
            self.current_user = None
        else:
            print("Not logged in.")

    def loghours(self):
        if not self.loggedin:
            print("You are not logged in, please log in first.")
            return
        try:
            hours = float(input("Enter the amount of hours you worked: "))
            self.accounts[self.current_user]['hours_worked'] += hours
            self.save_accounts()
            print(f"Logged {hours} hours worked")
        except Exception:
            print("Invalid input. Must be a number.")

    # patient functions
    def logpatients(self):
        if not self.loggedin or self.accounts[self.current_user]['kind'] != "Nurse":
            print("You are either not logged in or not logged into an account with permission to access this.")
            return

        try:
            patient_name = input("What was the patients name?: ")
            age = int(input("What was the patients age?: "))
            symptoms = input("Enter symptoms (comma separated): ")
            symptoms_list = [s.strip() for s in symptoms.split(",")]

            self.patientstoday[patient_name] = {"age": age, "symptoms": symptoms_list}
            self.accounts[self.current_user]['patients_attended'] += 1
            self.save_patients()
            self.save_accounts()
            print(f"Logged '{patient_name}'")
        except Exception as e:
            print(f"Could not log patient: {e}")

    def listpatients(self):
        if not self.loggedin:
            print("Please login to access this.")
            return
        if not self.patientstoday:
            print("No patients registered.")
            return
        for name, data in self.patientstoday.items():
            print("=" * 25)
            print(f"Patient Name : {name}")
            print(f"Age          : {data['age']}")
            print("Symptoms     :")
            for symptom in data["symptoms"]:
                print(f"  • {symptom}")

    def whoami(self):
        if not self.loggedin:
            print("You are not logged in")
            return
        data = self.accounts[self.current_user]
        print()
        print(f"You are logged in as: {self.current_user}")
        print(f"Hours Worked: {data['hours_worked']}")
        print(f"This is a {data['kind']} account.")
        if data['kind'] == "Nurse":
            print(f"{data['patients_attended']} Patients have been attended to by this nurse")
        else:
            print(f"The budget is ${data['budget']:.2f} AUD")
        print()

    # report gui
    def opengui(self):
        if not self.loggedin:
            print("Please log in first.")
            return

        root = tk.Tk()
        root.title("Clinic Dashboard")
        root.geometry("800x600")
        root.configure(bg="#E3F2FD")  # soft healthcare-blue background

        # clinic name
        tk.Label(root, text="MyClinic System", font=("Arial", 32, "bold"),
                fg="#0D47A1", bg="#E3F2FD").pack(pady=25)

        # report frame
        report_frame = tk.Frame(root, bg="#BBDEFB", padx=30, pady=30)
        report_frame.pack(fill="both", expand=True, padx=40, pady=15)

        # Function to refresh stats
        def refresh_report():
            for widget in report_frame.winfo_children():
                widget.destroy()

            total_staff = len(self.accounts)
            total_patients_today = sum(
                self.accounts[user].get("patients_attended", 0)
                for user in self.accounts if self.accounts[user]["kind"] == "Nurse"
            )
            top_nurse = None
            max_patients = 0
            for user, data in self.accounts.items():
                if data["kind"] == "Nurse" and data.get("patients_attended", 0) > max_patients:
                    max_patients = data.get("patients_attended", 0)
                    top_nurse = user

            total_budget = sum(
                data.get("budget", 0)
                for user, data in self.accounts.items()
                if data["kind"] == "Doctor"
            )
            total_logged_patients = len(self.patientstoday)

            stats = [
                f"Total Staff Count: {total_staff}",
                f"Total Patients Attended Today: {total_patients_today}",
                f"Top Nurse: {top_nurse if top_nurse else 'N/A'} ({max_patients} patients)",
                f"Doctors' Budget Status: ${total_budget:.2f}",
                f"Total Patients Logged Today: {total_logged_patients}"
            ]

            for stat in stats:
                tk.Label(report_frame, text=stat, font=("Arial", 18, "bold"), bg="#BBDEFB", anchor="w").pack(fill="x", pady=8)

        # Initial report
        refresh_report()

        # ===== Refresh Button =====
        tk.Button(root, text="Refresh Report", font=("Arial", 18, "bold"),
                fg="white", bg="#1565C0", activebackground="#0D47A1",
                command=refresh_report, padx=15, pady=10).pack(pady=20)

        # ===== Close Button =====
        tk.Button(root, text="Close Dashboard", font=("Arial", 18, "bold"),
                fg="white", bg="#C62828", activebackground="#B71C1C",
                command=root.destroy, padx=15, pady=10).pack(pady=10)

    #root.mainloop() # idk causes issues with stuff

    def about(self):
        self.clear()
        print()
        print("░█████╗░██╗░░░░░██╗███╗░░██╗██╗░█████╗░░██████╗██╗░░░██╗░██████╗████████╗███████╗███╗░░░███╗")
        print("██╔══██╗██║░░░░░██║████╗░██║██║██╔══██╗██╔════╝╚██╗░██╔╝██╔════╝╚══██╔══╝██╔════╝████╗░████║")
        print("██║░░╚═╝██║░░░░░██║██╔██╗██║██║██║░░╚═╝╚█████╗░░╚████╔╝░╚█████╗░░░░██║░░░█████╗░░██╔████╔██║")
        print("██║░░██╗██║░░░░░██║██║╚████║██║██║░░██╗░╚═══██╗░░╚██╔╝░░░╚═══██╗░░░██║░░░██╔══╝░░██║╚██╔╝██║")
        print("╚█████╔╝███████╗██║██║░╚███║██║╚█████╔╝██████╔╝░░░██║░░░██████╔╝░░░██║░░░███████╗██║░╚═╝░██║")
        print("░╚════╝░╚══════╝╚═╝╚═╝░░╚══╝╚═╝░╚════╝░╚═════╝░░░░╚═╝░░░╚═════╝░░░░╚═╝░░░╚══════╝╚═╝░░░░░╚═╝")
        print()
        print(f"Clinic System v{self.clinicver}")
        print("Created by Ben Perry - Project Lead/Class Developer, Samrat Basnet - GUI Developer.")

    # main
    def run(self):
        while True:
            command = input("Enter a command: ").lower().strip()
            match command:
                case "createaccount":
                    self.createuseraccount()
                case "deleteaccount":
                    self.deleteuseraccount()
                case "listaccounts":
                    self.listuseraccounts()
                case "login":
                    self.login()
                case "logoff":
                    self.logoff()
                case "opengui":
                    self.opengui()
                case "loghours":
                    self.loghours()
                case "logpatient":
                    self.logpatients()
                case "listpatient":
                    self.listpatients()
                case "whoami":
                    self.whoami()
                case "about":
                    self.about()
                case "exit":
                    exit()
                case "help":
                    print("Commands: createaccount, deleteaccount, listaccounts, login, logoff, loghours, logpatient, listpatient, opengui, whoami, help, about, exit")
                case _:
                    print("Unknown command. Type 'help' for commands.")


if __name__ == "__main__":
    ClinicManager().run()