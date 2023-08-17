import sqlite3
import time
from blessed import Terminal
from inquirer import prompt, List
import inquirer
from tabulate import tabulate
import sys
import pickle
import argparse

DB_FILE = 'blood_bank.db'

# Define a function to load and save the state using pickle
def load_state(state_file):
    try:
        with open(state_file, 'rb') as f:
            state = pickle.load(f)
    except:
        state = {}
    return state

def save_state(state, state_file):
    with open(state_file, 'wb') as f:
        pickle.dump(state, f)

# Create an ArgumentParser object
parser = argparse.ArgumentParser()

# Add the required arguments
parser.add_argument('-u', '--username', help='User name')
parser.add_argument('-p', '--password', help='Password')

# Parse the arguments
args = parser.parse_args()

# Load the state from the file
state_file = 'state.pkl'
state = load_state(state_file)

# Store the user name and password in the state
state['username'] = args.username
state['password'] = args.password

# Save the state to the file
save_state(state, state_file)

# Retrieve the user name and password from the state
username = state['username']
password = state['password']

term = Terminal()

def validate_input(_, value):
    if len(value) == 0:
        raise inquirer.errors.ValidationError('', reason='This field is required') # type: ignore
    return True
def validate_str_num(_, value):
    if len(value) == 0 or not value.isdigit():
        raise inquirer.errors.ValidationError('', reason='This field is required') # type: ignore
    return True

class System:
    def __init__(self):
        self.database = Database()
        self.uoda()
        self.bloodsrc()
        self.term = Terminal()

    def uoda(self):
        uoda = '''
        @@@@%. :@@@@*       .=#%@@@%*=.       #@@@@*#@@@%#=.            :#@@@@     
       @@@@%.  :@@@@*     .*@@% @@@@@@@*.     #@@@@   :*@@@@#:         +% +@@@@    
      @@@@@    :@@@@*     @@@#  @@@@@@@@%     #@@@@     :@@@@@:       ##   %@@@@    
     @@@@@:    :@@@@*    #@@%  :%@@@@@@@@*    #@@@@      #@@@@#      %@     *@@@@   
    *@@@@=     :@@@@*    #@@+     :@@@@@@#    #@@@@      @@@@@%     #@%      +@@@@  
    @@@@@      :@@@@*    =@@%     *@@@@@@-    #@@@@    +@@@@@@+    =@@@+      %@@@@. 
    @@@@@==*@+.:@@@@*     =@@@*=:=@@@@@@=     #@@@@-#@@@@@@@@#     +@@@@@@@@=: @@@@# 
    -@@@@@#*   :@@@@*       +%@@@@@@@%=       #@@@@.=@@@@@#:         +@@@@@%.   +@@@@'''
        return uoda
    def bloodsrc(self):
        bloodsrc = '\033[31m'+'''
            888888b.   888                        888  .d8888b.                  
            888  "88b  888                        888 d88P  Y88b                 
            888  .88P  888                        888 Y88b.                      
            8888888K.  888  .d88b.   .d88b.   .d88888  "Y888b.   888d888 .d8888b 
            888  "Y88b 888 d88""88b d88""88b d88" 888     "Y88b. 888P"  d88P"    
            888    888 888 888  888 888  888 888  888       "888 888    888      
            888   d88P 888 Y88..88P Y88..88P Y88b 888 Y88b  d88P 888    Y88b.    
            8888888P"  888  "Y88P"   "Y88P"   "Y88888  "Y8888P"  888     "Y8888P'''+'\033[0m'
        return bloodsrc
    
    def title(self, title):
        print(self.uoda())
        print(self.bloodsrc())
        print(term.center('--------------------------------------------------------------------------------'))
        print(term.center(title))
        print(term.center('--------------------------------------------------------------------------------'))

    def clear(self):
        print(self.term.home + self.term.clear)

    def exit(self):
        # Exit the program
        print(term.clear)
        print(term.cyan(term.center('-~- Goodbye! Thank you for using our system! -~-')))
        print()
        time.sleep(1)
        print(term.clear)
        sys.exit()


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS blood_bank
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                name TEXT,
                batch INTEGER,
                department TEXT,
                contact TEXT,
                blood_group TEXT,
                status TEXT,
                user_type TEXT)''')
        self.conn.commit()

    def insert(self, student_id, name, batch, department, contact, blood_group, status, user_type):
        try:
            self.cur.execute('''INSERT INTO blood_bank (student_id, name, batch, department, contact, blood_group, status, user_type)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (student_id, name, batch, department, contact, blood_group, status, user_type))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print('Data entry failed. ID already exists.')
    
    def list(self):
        self.cur.execute("SELECT * FROM blood_bank")
        rows = self.cur.fetchall()
        return rows
    
    def search(self, search, value):
        self.cur.execute("SELECT * FROM blood_bank WHERE " + search + "=?", (value,))
        rows = self.cur.fetchall()
        return rows
    
    def delete(self, student_id):
        self.cur.execute("DELETE FROM blood_bank WHERE student_id=?", (student_id,))
        self.conn.commit()
    
    def update(self, student_id, name, batch, department, contact, blood_group, status, user_type):
        self.cur.execute("UPDATE blood_bank SET name=?, batch=?, department=?, contact=?, blood_group=?, status=?, user_type=? WHERE student_id=?", (name, batch, department, contact, blood_group, status, user_type, student_id))
        self.conn.commit()

    def count(self):
        self.cur.execute("SELECT COUNT(*) FROM blood_bank")
        count = self.cur.fetchone()
        return count
    
    def count_filter(self, search, value):
        self.cur.execute("SELECT COUNT(*) FROM blood_bank WHERE " + search + "=?", (value,))
        count = self.cur.fetchone()
        return count

    def __del__(self):
        self.conn.close()

class BloodBank:
    def __init__(self):
        self.database = Database()
        self.system = System()

    def add_donor(self):
        print(term.home + term.clear)
        self.system.title('Add a new donor')
        print()
        try: 
            questions = [
                inquirer.Text('student_id', message="Enter student ID", validate=validate_str_num),
                inquirer.Text('name', message="Enter name", validate=validate_input),
                inquirer.Text('batch', message="Enter batch", validate=validate_str_num),
                inquirer.Text('department', message="Enter department" , validate=validate_input),
                inquirer.Text('contact', message="Enter contact" , validate=validate_str_num),
                inquirer.List('blood_group', message="Select blood group:", choices=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'], carousel=True, validate=lambda _, x: len(x) > 0), # type: ignore
                inquirer.List('status', message="Enter status", default='active', choices=['active', 'inactive']),
                inquirer.List('user_type', message="Select user type:", choices=['student', 'ex-student'], carousel=True, validate=lambda _, x: len(x) > 0), # type: ignore
                inquirer.Confirm('confirm', message="Are you sure you want to add this record?", default=True),
            ]
            answers = inquirer.prompt(questions)
            # Check if the user wants to exit
            if answers is None or not answers.get('confirm'):
                print(term.home + term.clear)
                return
            
            # Check if the student ID already exists
            if self.database.search('student_id', answers.get('student_id')):
                print(term.home + term.clear)
                print(term.center('''\033[1;31m'Error: Student ID already exists!'\033[0m'''))
                print()
                print(term.center('Press Enter to continue...'))
                input()
                return
            else:
                self.database.insert(answers.get('student_id'), answers.get('name'), answers.get('batch'), answers.get('department'), answers.get('contact'), answers.get('blood_group'), answers.get('status'), answers.get('user_type'))
                print(term.home + term.clear)
                print(term.center('''\033[1m Successfully added a new donor! \033[0m'''))
                print()
                print(term.center('Press Enter to continue...'))
                input()

        except KeyboardInterrupt:
            self.system.clear()
            print(term.center('\033[1;33m'+'Operation cancelled by user'+'\033[0m'))
            print()
            print(term.center('Press Enter to continue...'))
            input()

    def update_donor(self):
        print(term.home + term.clear)
        self.system.title('Update Blood Donor')
        print()
        try:
            # Prompt the user to enter the ID of the record to update
            questions = [
                inquirer.Text('student_id', message="Enter the ID of the record to update", validate=validate_str_num),
                inquirer.Confirm('confirm', message="Are you sure you want to update this record?", default=True),
            ]
            answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)

            # Check if the user wants to exit
            if answers is None or not answers.get('confirm'):
                print(term.clear)
                return

            # Query the database for the record with the specified ID
            rows = self.database.search('student_id', answers['student_id'])
            if len(rows) == 0:
                print(term.clear)
                print(term.center('''\033[1;31m Record not found! \033[0m'''))
                print()
                print(term.center('Press Enter to continue ...'))
                input()
                return
            
            # Prompt the user to enter the new values for the record
            update_donor_promt = [
                inquirer.Text('student_id', message="Student ID", default=rows[0][1], validate=validate_str_num),
                inquirer.Text('name', message="Name", default=rows[0][2], validate=validate_input),
                inquirer.Text('batch', message="Batch", default=rows[0][3], validate=validate_str_num),
                inquirer.Text('department', message="Department", default=rows[0][4], validate=validate_input),
                inquirer.Text('contact', message="Contact", default=rows[0][5], validate=validate_str_num),
                inquirer.List('blood_group', message="Blood Group", default=rows[0][6], choices=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'], carousel=True, validate=lambda _, x: len(x) > 0), # type: ignore
                inquirer.List('status', message="Status", default=rows[0][7], choices=['active', 'inactive']),
                inquirer.List('user_type', message="User Type", default=rows[0][8], choices=['student', 'ex-student'], carousel=True, validate=lambda _, x: len(x) > 0), # type: ignore
                inquirer.Confirm('confirm', message="Are you sure you want to update this record?", default=True),
            ]
            answers = inquirer.prompt(update_donor_promt)
            self.database.update(answers['student_id'], answers['name'], answers['batch'], answers['department'], answers['contact'], answers['blood_group'], answers['status'], answers['user_type'])  # type: ignore
            print(term.home + term.clear)
            self.system.clear()
            print(term.center('''\033[1m Successfully updated the record! \033[0m'''))
            print()
            print(term.center('Press Enter to continue ...'))

        except KeyboardInterrupt:
            self.system.clear()
            print(term.center('Blood Donor Updating Cancelled'))
            print()
            print(term.center('Press Enter to continue...'))
            input()

    def delete_donor(self):
        print(term.home + term.clear)
        self.system.title('Delete Blood Donor')
        print()
        try:
            # Prompt the user to enter the ID of the record to delete
            questions = [
                inquirer.Text('student_id', message="Enter the ID of the record to delete", validate=validate_str_num),
                inquirer.Confirm('confirm', message="Are you sure you want to delete this record?"),
            ]
            answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)

            # Check if the user wants to exit
            if answers is None or not answers.get('confirm'):
                print(term.clear)
                return

            # Query the database for the record with the specified ID
            rows = self.database.search('student_id', answers['student_id'])
            if len(rows) == 0:
                print(term.clear)
                print(term.center('No record found with the specified ID'))
                print()
                print(term.center('Press Enter to continue ...'))
                input()
                return

            # Delete the record from the database
            self.database.delete(answers['student_id'])
            print(term.home + term.clear)
            self.system.clear()
            print(term.center('''\033[1m Successfully deleted the record! \033[0m'''))
            print()
            print(term.center('Press Enter to continue ...'))

        except KeyboardInterrupt:
            self.system.clear()
            print(term.center('Blood Donor Deleting Cancelled'))
            print()
            print(term.center('Press Enter to continue...'))
            input()

    def search_donor(self):
        print(term.home + term.clear)
        self.system.title('Search Blood Donor')
        print()
        try:
            # Prompt the user to enter the ID of the record to search
            questions = [
                    inquirer.List('criteria', message="Search by", choices=['Student ID', 'Blood Type', 'Name', 'Back']),
            ]
            answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)

            # Check if the user wants to exit
            if answers is None:
                print(term.clear)
                return
            rows = []
            if answers['criteria'] == 'Student ID':
                questions = [
                    inquirer.Text('student_id', message="Enter the Student ID", validate=validate_str_num),
                ]
                answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)
                rows = self.database.search('student_id', answers['student_id']) # type: ignore
            elif answers['criteria'] == 'Blood Type':
                questions = [
                    inquirer.List('blood_group', message="Enter the Blood Group", choices=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                ]
                answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)
                rows = self.database.search('blood_group', answers['blood_group']) # type: ignore
            elif answers['criteria'] == 'Name':
                questions = [
                    inquirer.Text('name', message="Enter the Name", validate=validate_input),
                ]
                answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)
                rows = self.database.search('name', answers['name']) # type: ignore

            # Display the records
            print(term.center(f'{len(rows)} Record(s) Found')) # type: ignore
            print()
            print(tabulate(rows, headers=['#', 'Student ID', 'Name', 'Batch', 'Department', 'Contact', 'Blood Group', 'Status', 'User Type'], tablefmt='fancy_grid')) # type: ignore
            print()
            print(term.center('Press Enter to continue ...'))
            input()

        except KeyboardInterrupt:
            self.system.clear()
            print(term.center('Blood Donor Searching Cancelled'))
            print()
            print(term.center('Press Enter to continue...'))
            input()

    def list_donors(self):
        print(term.home + term.clear)
        self.system.title('List All Blood Donors')
        print()
        try:
            # Query the database for all records
            rows = self.database.list()
            if len(rows) == 0:
                print(term.center('No records found'))
                print()
                print(term.center('Press Enter to continue ...'))
                input()
                return

            # Display the records
            print(term.center(f'{len(rows)} Record(s) Found'))
            print()
            print(tabulate(rows, headers=['#', 'Student ID', 'Name', 'Batch', 'Department', 'Contact', 'Blood Group', 'Status', 'User Type'], tablefmt='fancy_grid'))
            print(term.center('Press Enter to continue ...'))
            input()

        except KeyboardInterrupt:
            self.system.clear()
            print(term.center('Blood Donor Listing Cancelled'))
            print()
            print()
            print(term.center('Press Enter to continue...'))
            input()

    def exit(self):
        print(term.home + term.clear)
        self.system.title('Exit')
        print()
        try:
            # Prompt the user to confirm exit
            questions = [
                inquirer.Confirm('confirm', message="Are you sure you want to exit?"),
            ]
            answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)

            # Check if the user wants to exit
            if answers is None or not answers.get('confirm'):
                print(term.clear)
                return

            # Exit the program
            self.system.exit()

        except KeyboardInterrupt:
            self.system.clear()
            print(term.center('Exit Cancelled'))
            print()
            print(term.center('Press Enter to continue...'))
            input()

class Admin:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.database = Database()
        self.system = System()
        self.blood_bank = BloodBank()

    def admin_login(self):
        if self.username == "admin" and self.password == "admin":
            return True
        elif username == 'admin' and password != 'admin' or username != 'admin' and password == 'admin' or username != 'admin' and password != 'admin':
            return False
        else:
            return False
        
    def admin_menu(self):
        print(term.home + term.clear)
        self.system.title('Admin Menu')
        print(term.center('Welcome Admin'))
        print()

        # Count Total Active Donors
        active = self.database.count_filter('status', 'active')
        active = active[0] if active else 0

        # Count Total Inactive Donors
        inactive = self.database.count_filter('status', 'inactive')
        inactive = inactive[0] if inactive else 0

        # Count Total Donors from each blood group using loop
        blood_group = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        blood_group_count = []
        for i in blood_group:
            count = self.database.count_filter('blood_group', i)
            count = count[0] if count else 0
            blood_group_count.append(count)
        
        # Doner Counts
        print(tabulate([['Total Records', 'Active Donors', 'Inactive Donors'], [(active+inactive), active, inactive]], headers='firstrow', tablefmt='simple'))
        # Blood Group Counts
        print(tabulate([blood_group, blood_group_count], headers='firstrow', tablefmt='fancy_grid'))


        admin_menu_promt = [
            List('operation', message="Select an operation", choices=['Add Blood Donor', 'Update Blood Donor', 'Delete Blood Donor', 'Search Blood Donor', 'List All Blood Donors', 'Exit'], carousel=True),
        ]
        
        # Get the user's choice
        answers = prompt(admin_menu_promt)
        if not answers:
            print(term.center('-~ Goodbye! ~-'))
            exit(1)
        choice = answers.get('operation')

        switcher = {
            'Add Blood Donor': self.blood_bank.add_donor,
            'Update Blood Donor': self.blood_bank.update_donor,
            'Delete Blood Donor': self.blood_bank.delete_donor,
            'Search Blood Donor': self.blood_bank.search_donor,
            'List All Blood Donors': self.blood_bank.list_donors,
            'Exit': self.blood_bank.exit,
        }
        func = switcher.get(choice, lambda: 'Invalid') # type: ignore
        func()
        
class Public:
    # Public don't have access to add, update, delete. they can only search and list. the dont need to login
    def __init__(self):
        self.database = Database()
        self.system = System()
        self.blood_bank = BloodBank()

    def public_menu(self):
        print(term.home + term.clear)
        self.system.title('Public Menu')
        print(term.center('Welcome Public'))
        print()
        public_menu_promt = [
            List('operation', message="Select an operation", choices=['Search Blood Donor', 'List All Blood Donors', 'Exit'], carousel=True),
        ]
        
        # Get the user's choice
        answers = prompt(public_menu_promt)
        if not answers:
            print(term.center('-~ Goodbye! ~-'))
            exit(1)
        choice = answers.get('operation')

        switcher = {
            'Search Blood Donor': self.blood_bank.search_donor,
            'List All Blood Donors': self.blood_bank.list_donors,
            'Exit': self.blood_bank.exit,
        }
        func = switcher.get(choice, lambda: 'Invalid') # type: ignore
        func()

# Run the program
if __name__ == '__main__':
    # Create the database
    database = Database()

    # Create the system
    system = System()

    # Create the blood bank
    blood_bank = BloodBank()

    # Create the admin
    admin = Admin(username, password)
    
    # Create the public
    public = Public()

    while True:
        if admin.admin_login():
            # Show the admin menu
            admin.admin_menu()
        else:    
            # Show the public menu
            public.public_menu()