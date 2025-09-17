# Eriberto Salgado - MSIIP - LLNL
# 9/16/25
# The purpose of this code is to connect an HID card reader and receive the FASCN number
# then parse it for query in the Hostinger database.
# TURN OFF VPN

import pymysql
import keyboard
import time

# --- Database configuration ---
DB_HOST = "srv869.hstgr.io"
DB_USER = "u537162232_db_EribertoSal"
DB_PASS = "Erick5100"
DB_NAME = "u537162232_EribertoSal"

# --- FASC-N format ---
# FASC-N is a 25-byte object. When output via keyboard wedge, it is a 32-digit string.
# We will use a listener to capture the entire string.
FASC_N_LENGTH = 32

def find_user_in_db(FASCN):
    """Connects to the database and finds a matching user."""
    connection = None
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            # Assuming your table is named 'users' and contains a 'fasc_n' column
            sql = "SELECT FASCN, name, clearance, expiration_date, affiliation FROM LEAP WHERE FASCN = %s"
            cursor.execute(sql, (FASCN,))
            result = cursor.fetchone()
            return result
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return None
    finally:
        if connection:
            connection.close()

def main():
    print("HID card reader is ready. Please swipe a card.")
    print("Press Ctrl+C to exit.")

    try:
        # Use a list to store captured keystrokes
        captured_input = []
        
        def on_key_press(event):
            """Keypress handler to capture input from the reader."""
            nonlocal captured_input
            
            # Filter for alphanumeric and relevant characters from reader output
            if event.name.isalnum():
                captured_input.append(event.name)
            
            # Assuming the reader sends a 'return' key after the data
            if event.name == 'enter' and len(captured_input) >= FASC_N_LENGTH:
                # Join the list into a string
                fasc_n_raw = "".join(captured_input)
                # Parse the FASC-N from the captured string
                # This assumes a clean, well-formed input from the reader
                parsed_fasc_n = fasc_n_raw[:FASC_N_LENGTH]
                
                print(f"Captured FASC-N: {parsed_fasc_n}")
                
                user_data = find_user_in_db(parsed_fasc_n)
                
                if user_data:
                    print("Match found!")
                    print("--- User Details ---")
                    print(f"FASCN: {user_data['FASCN']}")
                    print(f"Name: {user_data['name']}")
                    print(f"Clearance: {user_data['clearance']}")
                    print(f"Expiration Date: {user_data['expiration_date']}")
                    print(f"Affiliation: {user_data['affiliation']}")
                    print("--------------------")
                else:
                    print("No matching user found in the database.")
                
                # Reset the buffer for the next scan
                captured_input = []
        
        # Listen for keyboard events indefinitely
        keyboard.on_press(on_key_press)
        
        # Keep the script running
        keyboard.wait('esc') # Waits until the 'esc' key is pressed
        
    except KeyboardInterrupt:
        print("\nExiting script.")

if __name__ == "__main__":
    main()

