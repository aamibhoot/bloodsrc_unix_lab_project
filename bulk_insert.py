import random
import sqlite3

def contact_generator():
    # random contact generator
    contact = '01' + str(random.randint(100000000, 999999999))
    return contact
    

def bulk_insert():
    # connect to the database
    conn = sqlite3.connect('blood_bank.db')
    # create a cursor
    c = conn.cursor()
    query = '''
    INSERT INTO blood_bank (student_id, name, batch, department, contact, blood_group, status, user_type)
    VALUES 
    (011201001, 'Erfat Ara Jukaiya', '53', 'CSE', '01789746512', 'A+', 'active', 'student'),
    (011201002, 'Rayojan Khan Nayem', '53', 'CSE', '01872438531', 'B-', 'inactive', 'student'),
    (011201003, 'Sheikh Rakib Raihan', '53', 'CSE', '01589076453', 'AB+', 'active', 'student'),
    (011201005, 'Md Muksitur Rahman Shihab', '53', 'CSE', '01158967342', 'O-', 'inactive', 'student'),
    (011201006, 'Tushar Alam', '53', 'CSE', '01638429567', 'B+', 'active', 'student'),
    (011201007, 'Sha Md. Ramim Islam', '53', 'CSE', '01358976542', 'A-', 'inactive', 'student'),
    (011201008, 'M. Neehal Sharif', '53', 'CSE', '01758674321', 'AB-', 'active', 'student'),
    (011201009, 'Harun Or Rashid', '53', 'CSE', '01974658312', 'O+', 'inactive', 'student'),
    (011201010, 'Azizul Hakim', '53', 'CSE', '01829764351', 'B-', 'active', 'student'),
    (011201011, 'Sharif R. Prantor', '53', 'CSE', '01769485632', 'A+', 'inactive', 'student'),
    (011201012, 'Maisha Ara Maymona', '53', 'CSE', '01587643219', 'AB+', 'active', 'student'),
    (011201013, 'Munshi Arafat Hosen', '53', 'CSE', '01128965437', 'O-', 'inactive', 'student'),
    (011201014, 'Monoj Uddin Piash', '53', 'CSE', '01358769423', 'B+', 'active', 'student'),
    (011201015, 'Saidur Rahman Sifat', '53', 'CSE', '01928765432', 'A-', 'inactive', 'student'),
    (011201016, 'Raiyan Bin Ramim', '53', 'CSE', '01789567342', 'AB-', 'active', 'student')
    '''

    c.execute(query)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    bulk_insert()