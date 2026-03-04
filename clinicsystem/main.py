# TODO
# Implement compiledailyreport()
# Implement patient stuff

import os
import tkinter as tk
from encryption import encrypt, decrypt # if you want to remove the encryption, comment this line

loggedin = False
password = None
current_user = None
hoursworked = 0
accounts = {}  # key = username, value = password
patientstoday = {}
encryptpassword = "coolclinicencrypt" # DO NOT CHANGE IF ACCOUNTS ARE CREATED - Ben.P
clinicver = 1.0

# classes
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

    # overridden behaviour
    def calculate_priority(self):
        return self.visits + 100

    def __str__(self):
        return (
            f"VIP Patient: {self.name} | "
            f"Tier: {self.tier} | Visits: {self.visits}"
        )

accounts_file = os.path.join(os.path.dirname(__file__), "accounts.txt")
patients_file = os.path.join(os.path.dirname(__file__), "patients.txt")

if os.path.exists(accounts_file):
    with open(accounts_file, "r") as f:
        for line in f:
            parts = line.strip().split(",") # sets the data in an array expression called parts
            
            user = decrypt(parts[0], encryptpassword)  # username / user is a location 0 in the array
            pw = decrypt(parts[1], encryptpassword)    # password / passwords is a location 1 in the array
            kind = parts[2]                            # "Doctor" or "Nurse" / location 2 such and so on
            hours_worked = float(parts[-1])              # last field is always hours_worked so we use -1 to always get that
            
            user_data = {
                "password": pw,
                "kind": kind,
                "hours_worked": hours_worked
            }

            # assign specific fields based on if they're a nurse or doctor
            if kind == "Nurse":
                user_data["patients_attended"] = int(parts[3])
                current_user_classes = Nurse(user, "1", hours_worked, user_data["patients_attended"])
            elif kind == "Doctor":
                user_data["budget"] = float(parts[3])
                current_user_classes = Doctor(user, "1", hours_worked, user_data["budget"])

            # save to accounts dictionary
            accounts[user] = user_data 
            #current_user_classes = Nurse(user, "1", hours_worked, user_data)
            #print(current_user_classes) # debug, but could use this elsewhere as it looks nice - Ben.P

if os.path.exists(patients_file):
    with open(patients_file, "r") as f:
        for line in f:
            parts = line.strip().split("|")
            # format: name|age|type|tier|visits|symptoms(comma separated)
            name = parts[0]
            age = int(parts[1])
            ptype = parts[2]
            tier = parts[3] if parts[3] != "None" else None
            visits = int(parts[4])
            symptoms = parts[5].split(",") if parts[5] else []

            if ptype == "VIP":
                patient_obj = VIPPatient(name, age, tier)
            else:
                patient_obj = Patient(name, age)
            patient_obj.visits = visits

            patientstoday[name] = {
                "object": patient_obj,
                "age": age,
                "symptoms": symptoms
            }

    
def clear():
    if os.name == "nt":
        os.system("cls")
    else: 
        os.system("clear") 

def writetoaccounts(username, password):
    username_encrypted = encrypt(username, encryptpassword) # if you want to remove the encryption, comment these lines and lines #17 and #18
    password_encrypted = encrypt(password, encryptpassword) # if you want to remove the encryption, comment these lines and lines #17 and #18
    with open(accounts_file, "a") as f:
        if accounts[username]['kind'] == "Nurse":
            #print("true") #debug
            f.write(f"{username_encrypted},{password_encrypted},{accounts[username]['kind']},{accounts[username]['patients_attended']},{accounts[username]['hours_worked']}\n")
            return
        elif accounts[username]['kind'] == "Doctor":
            #print("false") #debug
            f.write(f"{username_encrypted},{password_encrypted},{accounts[username]['kind']},{accounts[username]['budget']},{accounts[username]['hours_worked']}\n")
            return

# functions
def createuseraccount():
    global loggedin, current_user, accounts

    if not loggedin:
        username = input("Enter a username (6-15 chars, no spaces): ")
        password = input("Enter a password: ")
        kind = input("Docter or Nurse Account?: (D/N) ").upper() # the .upper() makes sure that the input is returned in all uppercase

        if kind not in ("N", "D"):
            print("Please select a doctor or a nurse")
            #createuseraccount() # was gonna use this but then i realised theres no way to get back to the menu unless you error it out, actually you could enter a username longer than allowed.
            return 
        
        if 5 < len(username) < 16 and " " not in username:
            if username in accounts:
                print("This username has already been taken by another user account")
                return

            # saves to a dictionary
            #accounts[username] = password


            if kind == "N":
                user_data = {
                    "password": password,
                    "kind": "Nurse",
                    "hours_worked": 0, 
                    "patients_attended": 0            
                }
                user_data["patients_attended"] = 0
            elif kind == "D":
                user_data = {
                    "password": password,
                    "kind": "Doctor",
                    "hours_worked": 0, 
                    "budget": 15000 # idk if it have this as a value here or define it later :p            
                }
            accounts[username] = user_data
            current_user = username
            loggedin = True

            # saves to the file
            try:
                writetoaccounts(username, password)
                print(f"Account created. Logged in as {current_user}")
            except Exception as e:
                print(f"Could not save account: {e}")
        else:
            print("Invalid username. Must be 6-15 chars with no spaces.")
    else:
        print(f"You are logged into {current_user}, please logout before creating a new account")

def update_file(username):
    # Update only the current user's hours_worked in the accounts file.
    # read all lines
    if not os.path.exists(accounts_file):
        return
    
    lines = []
    with open(accounts_file, "r") as f:
        lines = f.readlines()
    
    # this rebuilds the file with updated data for current user since we cant append singluar thing, again another reason why i should've used json but im too lazy to refactor it all :P - Ben.P
    with open(accounts_file, "w") as f:
        for line in lines:
            parts = line.strip().split(",")
            user_decrypted = decrypt(parts[0], encryptpassword)
            
            if user_decrypted == username:
                # replace this user's line with updated hours
                pw_encrypted = parts[1]  # keep original encrypted password
                kind = accounts[username]['kind']
                
                if kind == "Nurse":
                    account = accounts[username].get('patients_attended', 0)
                elif kind == "Doctor":
                    account = accounts[username].get('budget', 0)
                
                hours = accounts[username].get('hours_worked', 0)
                username_encrypted = encrypt(username, encryptpassword)
                
                f.write(f"{username_encrypted},{pw_encrypted},{kind},{account},{hours}\n")
            else:
                f.write(line)  # keep other users intact
                

def listuseraccounts():
    global loggedin, current_user, accounts
    if not accounts:
        print("No registered users.")
        return

    print("\nRegistered Users")
    print("=" * 30)

    for username, data in accounts.items():
        print(f"Username : {username}")
        print(f"Role     : {data['kind']}")
        print(f"Hours    : {data['hours_worked']} hrs")
        print("-" * 30)
        
    # old code
    # if not accounts:
    #         print("There are currently no accounts registered")
    # else:
    #     for user in accounts:
    #         print(user)

def deleteuseraccount():
    global loggedin, current_user, accounts

    if not loggedin:
        print("Please login to the account you wish to delete.")
        return

    inputyesno = input("Are you sure you want to delete the current user account? (Y/N): ").strip().upper()

    if inputyesno == "Y":
        if current_user in accounts:
            del accounts[current_user]
            try:
                username_encrypted = encrypt(current_user, encryptpassword)  # comment out if not using encryption

                if current_user in accounts:
                    del accounts[current_user]

                with open(accounts_file, "w") as f:
                    for user, data in accounts.items():
                        user_encrypted = encrypt(user, encryptpassword)
                        pw_encrypted = encrypt(data['password'], encryptpassword)
                        
                        if data['kind'] == "Nurse":
                            extra_field = data.get('patients_attended', 0)
                        elif data['kind'] == "Doctor":
                            extra_field = data.get('budget', 0)
                        
                        f.write(f"{user_encrypted},{pw_encrypted},{data['kind']},{extra_field},{data.get('hours_worked', 0)}\n")

                current_user_decrypted = decrypt(username_encrypted, encryptpassword)  # comment out if not using encryption
                print(f"Account '{current_user_decrypted}' has been deleted.")

                loggedin = False
                current_user = None

            except Exception as e:
                print(f"Could not update accounts file: {e}")
    else:
        print("Account deletion cancelled.")

def login():
    global loggedin, current_user, accounts, hours_worked

    if loggedin:
        print(f"Already logged in as {current_user}. Please logoff first.")
        return

    username = input("Enter username or Staff ID: ")
    password = input("Enter password: ")

    if username in accounts and accounts[username]["password"] == password:
        loggedin = True
        current_user = username
        #loggedinstaff = MedicalStaff(username, "S001", hours_worked) # i need to get rid of the "S001" either compeletly or refactor it into something else.
        # debug
        # print(loggedinstaff.name)
        # print(loggedinstaff.staffid)
        # print(loggedinstaff.hoursworked)
        print(f"Login successful. Logged in as {current_user}")
    else:
        print("Invalid username or password.")

def loghours(username):
    global loggedin, current_user, user

    if not loggedin:
        print(f"You are not logged in, please log in first.")
        return
    try:
        hours = input("Enter the amount of hours you worked: ")
        hours = float(hours)
    except Exception:
        print(f"Please Enter a number.")
        return

    loggedinstaff = MedicalStaff(current_user, "N1", hours)
    # debug
    # print(loggedinstaff.name)
    # print(loggedinstaff.staffid)
    # print(loggedinstaff.hoursworked)
    # print(accounts[user]['hours_worked'])
    print(f"Logged {hours} hours worked")
    password = pw
    if user == None:
        user = username
    accounts[user]['hours_worked'] += hours
    update_file(current_user)

def logpatients(username):
    global loggedin, current_user, patientstoday

    if not loggedin or accounts[current_user]['kind'] != "Nurse":
        print("You are either not logged in or not logged into an account with permission to access this.")
        return
    
    try:
        patient_name = input("What is the patient's name?: ")
        age = int(input("What is the patient's age?: "))
        is_vip = input("Is this a VIP patient? (Y/N): ").strip().upper()
        
        if is_vip == "Y":
            tier = input("Enter VIP tier (Gold, Silver, Platinum): ").strip().upper()
            patient = VIPPatient(patient_name, age, tier)
            if tier == "GOLD" or tier == "SILVER" or tier == "PLATINUM":
                print(tier) # debug
                patient = VIPPatient(patient_name, age, tier)
        else:
            print("unkewl dood")
            patient = Patient(patient_name, age)
            tier = "None"  # for saving in file


        symptoms = input("Enter symptoms (comma separated): ")
        symptoms_list = [s.strip() for s in symptoms.split(",")]
        
        # Record patient in memory
        patientstoday[patient_name] = {
            "object": patient,
            "age": age,
            "symptoms": symptoms_list
        }

        # Increment nurse's patients attended
        accounts[username]['patients_attended'] += 1
        update_file(current_user)

        # Save all patients to file
        patients_file = os.path.join(os.path.dirname(__file__), "patients.txt")
        with open(patients_file, "w") as f:
            for name, data in patientstoday.items():
                patient_obj = data["object"]
                ptype = "VIP" if isinstance(patient_obj, VIPPatient) else "Regular"
                tier_to_save = getattr(patient_obj, "tier", "None")
                f.write(
                    f"{patient_obj.name}|{data['age']}|{ptype}|{tier_to_save}|{patient_obj.visits}|{','.join(data['symptoms'])}\n"
                )

        print(f"Logged patient: {patient_name} ({ptype})")

    except Exception as e:
        print(f"Could not log patient: {e}")

def updatepatient():
    global loggedin, current_user, patientstoday

    if not loggedin or accounts[current_user]['kind'] != "Nurse":
        print("You must be logged in as a Nurse to update patients.")
        return

    if not patientstoday:
        print("No patients registered.")
        return

    # Show patients
    print("\nRegistered Patients:")
    print("=" * 30)
    for name in patientstoday:
        print(f"- {name}")
    print()

    selected = input("Enter the name of the patient to update: ").strip()

    if selected not in patientstoday:
        print("Patient not found.")
        return

    patient_data = patientstoday[selected]
    patient_obj = patient_data["object"]

    # Increment visit count
    patient_obj.visits += 1

    # Increment nurse count
    accounts[current_user]['patients_attended'] += 1
    update_file(current_user)

    # Update symptoms
    update_symptoms = input("Update symptoms? (Y/N): ").strip().upper()
    if update_symptoms == "Y":
        new_symptoms = input("Enter new symptoms (comma separated): ")
        patient_data["symptoms"] = [s.strip() for s in new_symptoms.split(",")]

    # Save all patients back to file
    patients_file = os.path.join(os.path.dirname(__file__), "patients.txt")
    with open(patients_file, "w") as f:
        for name, data in patientstoday.items():
            obj = data["object"]
            ptype = "VIP" if isinstance(obj, VIPPatient) else "Regular"
            tier = getattr(obj, "tier", "None")
            symptoms = ",".join(data["symptoms"])

            f.write(
                f"{obj.name}|{data['age']}|{ptype}|{tier}|{obj.visits}|{symptoms}\n"
            )

    print(f"\nPatient '{selected}' updated successfully.")
    print(f"Visits: {patient_obj.visits}")

def top_nurse(typegui):
    if typegui == "GUI":
        #debug
        #print("is gui")
        nurses = [
            (username, data)
            for username, data in accounts.items()
            if data["kind"] == "Nurse"
        ]

        if not nurses:
            return None

        return max(
            nurses,
            key=lambda n: n[1].get("patients_attended", 0)
        )
    else:
        nurses = []

        # collect only nurse accounts
        for username, data in accounts.items():
            if data["kind"] == "Nurse":
                nurses.append((username, data))

        if not nurses:
            print("No nurses found.")
            return

        # find nurse with highest patients attended
        best = max(
            nurses,
            key=lambda n: n[1].get("patients_attended", 0)
        )

        username, data = best

        print("\nTop Performing Nurse")
        print("=" * 30)
        print(f"Name      : {username}")
        print(f"Patients  : {data['patients_attended']}")
        print(f"Hours     : {data['hours_worked']} hrs")

def listpatients():
    if not loggedin:
        print("Please login to access this.")
        return
    
    if not patientstoday:
        print("No patients registered.")
        return
    
    for name, data in patientstoday.items():
        patient_obj = data.get("object")
        symptoms = ", ".join(data["symptoms"])

        print("=" * 40)
        print(f"Name      : {patient_obj.name}")
        print(f"Type      : {'VIP' if isinstance(patient_obj, VIPPatient) else 'Regular'}")

        if isinstance(patient_obj, VIPPatient):
            print(f"Tier      : {patient_obj.tier}")

        print(f"Age       : {data['age']}")
        print(f"Visits    : {patient_obj.visits}")
        print(f"Symptoms  : {symptoms}")

def whoami():
    if loggedin:
        print()
        if accounts[current_user]['kind'] == "Nurse":
            print(f"You are logged in as: {current_user}")
            print(f"Hours Worked: {accounts[current_user]['hours_worked']}")
            print(f"This is a {accounts[current_user]['kind']} account.")
            print(f"{accounts[current_user]['patients_attended']} Patients have been attended to by this nurse")
        else:
            print(f"You are logged in as: {current_user}")
            print(f"Hours Worked: {accounts[current_user]['hours_worked']}")
            print(f"This is a {accounts[current_user]['kind']} account.")
            print(f"The budget is ${accounts[current_user]['budget']:.2f} AUD")
        print()
    else:
        print("You are not logged in")

def logoff():
    global loggedin, current_user
    if loggedin:
        print(f"Logging out of {current_user}")
        loggedin = False
        current_user = None
        accounts[user] = ""
    else:
        print("Not logged in.")

def opengui():
    if not loggedin:
        print("Please log in first.")
        return

    root = tk.Tk()
    root.title("Clinic App")
    root.geometry("640x480")

    # Logged in label
    tk.Label(
        root,
        text=f"Logged in as: {current_user}",
        font=("Arial", 24)
    ).pack(anchor="nw", pady=10)

    # Hours worked label
    tk.Label(
        root,
        text=f"Hours Worked: {accounts[current_user]['hours_worked']} hrs",
        font=("Arial", 24),
        fg="green"
        ).pack(pady=20)

    # Top nurse label
    top = top_nurse("GUI")
    if top:
        username, data = top
        tk.Label(
            root,
            text=f"Top Nurse: {username} | Patients: {data['patients_attended']}",
            font=("Arial", 20),
            fg="green"
        ).pack(pady=10)
    else:
        tk.Label(
            root,
            text="No nurses registered yet.",
            font=("Arial", 20),
            fg="red"
        ).pack(pady=10)

    # Finish button
    tk.Button(
        root,
        text="Close GUI",
        command=root.destroy
    ).pack(side="bottom", padx=20, pady=10)

def about():
        clear()
        print()
        print("░█████╗░██╗░░░░░██╗███╗░░██╗██╗░█████╗░░██████╗██╗░░░██╗░██████╗████████╗███████╗███╗░░░███╗")
        print("██╔══██╗██║░░░░░██║████╗░██║██║██╔══██╗██╔════╝╚██╗░██╔╝██╔════╝╚══██╔══╝██╔════╝████╗░████║")
        print("██║░░╚═╝██║░░░░░██║██╔██╗██║██║██║░░╚═╝╚█████╗░░╚████╔╝░╚█████╗░░░░██║░░░█████╗░░██╔████╔██║")
        print("██║░░██╗██║░░░░░██║██║╚████║██║██║░░██╗░╚═══██╗░░╚██╔╝░░░╚═══██╗░░░██║░░░██╔══╝░░██║╚██╔╝██║")
        print("╚█████╔╝███████╗██║██║░╚███║██║╚█████╔╝██████╔╝░░░██║░░░██████╔╝░░░██║░░░███████╗██║░╚═╝░██║")
        print("░╚════╝░╚══════╝╚═╝╚═╝░░╚══╝╚═╝░╚════╝░╚═════╝░░░░╚═╝░░░╚═════╝░░░░╚═╝░░░╚══════╝╚═╝░░░░░╚═╝")
        print()
        print(f"Clinic System v{clinicver}")
        print("Created by Ben Perry - Project Lead/Class Developer, Samrat Basnet - GUI Developer.")

def main():
    global loggedin, current_user


    while True:
        #about()
        command = input("Enter a command: ").lower().strip()

        # decided to do everything with functions to make it nicer to look at and reduce the clutter
        match command:
            case "createaccount":
                createuseraccount()
            case "deleteaccount":
                deleteuseraccount()
            case "listaccounts":
                listuseraccounts()
            case "login":
                login()
            case "logoff":
                logoff()
            case "opengui":
                top_nurse("GUI")
                opengui()
            case "topnurse":
                top_nurse("NONGUI")
            case "loghours":
                loghours(current_user)
            case "logpatient":
                logpatients(current_user)
            case "listpatient":
                listpatients()
            case "whoami":
                whoami()
            case "about":
                about()
            case "exit":
                exit()
            case "help":
                print("Commands: createaccount, deleteaccount, listaccounts, login, logoff, loghours, logpatient, listpatient opengui, topnurse, whoami, help, about, exit")
            case _:
                print("Unknown command. Type 'help' for commands.")

main()