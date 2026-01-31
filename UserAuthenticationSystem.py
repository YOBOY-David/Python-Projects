import csv
import bcrypt
from datetime import datetime
import time
import secrets

current_user = None
current_role = None

def log_event(user, action, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} | {user} | {action} | {details}\n"
    try:
        with open("audit_log.txt", "a") as file:
            file.write(log_line)   # safer than writelines
    except Exception as e:
        print(f"Logging failed: {e}")  # optional safeguard

def register_user():

  global current_user

  if current_user is not None:
    print("You must logout to for new registration")
    return


  while True:
    username = input("Enter your username: ").strip()
    if username == "":
      print("username cannot be empty. Try Agian!")
    else:
      break
  try:
    with open('accounts.csv', 'r') as file:
      reader = csv.reader(file)
      for row in reader:
        if row[0] == username:
          print('username already exists')
          return
  except FileNotFoundError:
    pass

  while True:
    password = input("Enter your password: ").strip()
    if password == "":
      print("password cannot be empty. Try Agian!")

    is_valid, message = is_strong_password(password)

    if not is_valid:
      print(message)

    else:
      break

  hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

  with open('accounts.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([username, hashed_password.decode(), 0, "", "", "", 'user'])

  print('Registration successful!')
  log_event(username, "REGISTER", "New account created")

def login_user():

  global current_user, current_role

  if current_user is not None:
    print(f"You are already logged in as {current_user}")
    return


  while True:
      username = input("Enter username: ").strip()
      if username == "":
          print("Username cannot be empty! Try again.")
      else:
          break

  while True:
      password = input("Enter password: ").strip()
      if password == "":
          print("Password cannot be empty! Try again.")
      else:
          break

  try:
    with open('accounts.csv', 'r', newline='') as file:
      reader = csv.reader(file)
      users = list(reader)
  except FileNotFoundError:
    print("No users registered yet. Plz register first")
    return
  
  user_row = None
  for row in users:

    row_username, row_hash, row_failed, row_locked_until, row_reset_token, row_token_expiry, row_role = row

    if row[0] == username:
      user_row = row
      break

  if user_row == None:
    print("User not found.")
    return
  
  username_csv, hashed_pw, failed_attempts_str, locked_until_str, reset_token, token_expiry, role = user_row
  failed_attempts = int(failed_attempts_str)
  locked_until = float(locked_until_str) if locked_until_str else None

  if locked_until is not None:
    now = time.time()
    if now < locked_until:
      remaining = int(locked_until - now)
      print(f"Account locked. Try again in {remaining} seconds.")
      return
    else:
      failed_attempts = 0
      locked_until = None
      user_row[2] = "0"
      user_row[3] = ""

  if bcrypt.checkpw(password.encode(), hashed_pw.encode()):
    print('Login successfull!')
    log_event(username, "LOGIN_SUCCESS", "User logged in")
    failed_attempts = 0
    locked_until = None
    user_row[2] = '0'
    user_row[3] = ''
    current_user = username
    current_role = role
  
  else:
    failed_attempts += 1
    user_row[2] = str(failed_attempts)
    log_event(username, "LOGIN_FAILED", "Wrong password")

    if failed_attempts >= 3:
      locked_until = time.time() + 600
      user_row[3] = str(locked_until)
      print('Account is locked due to many tries')
      log_event(username, "ACCOUNT_LOCKED", "Too many failed attempts")
    
    else:
       print(f"Invalid password. You have {3 - failed_attempts} attempts left.")

  with open('accounts.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(users)

def is_strong_password(password):

  has_upper = False
  has_lower = False
  has_digit = False
  has_special = False
  special_char = "!@#$%^&*()-_=+[]}{;:,.<>/?"

  for char in password:
    if char.isupper():
        has_upper = True
    if char.islower():
        has_lower = True
    if char.isdigit():
        has_digit = True
    if char in special_char:
      has_special = True

  if len(password) < 8:
      return False, "Password must be at least 8 characters long"
  if not has_upper:
      return False, "Password must contain at least one uppercase letter"
  if not has_lower:
      return False, "Password must contain at least one lowercase letter"
  if not has_digit:
      return False, "Password must contain at least one digit"
  if not has_special:
      return False, "Password must contain at least one special character"
  
  return True, "Strong password"

def logout_user():
    global current_user, current_role

    if current_user is None:
        print("No user is currently logged in.")
        return
    
    print(f"User {current_user} has been logged out.")
    log_event(current_user, "LOGOUT", "User logged out")
    current_user = None
    current_role = None

def require_admin():
  global current_role
  if current_role != "admin":
    print("Admin access required. This action is not allowed for normal users.")
    return False
  return True

def view_all_users():
  if not require_admin():
    return
  
  try:
    with open('accounts.csv', 'r', newline='') as file:
      reader = csv.reader(file)
      print("\n===== All Users ======\n")
      for row in reader:
        username, hashed_pw, failed_attempts, locked_until, reset_token, token_expiry, role = row
        print(f"Username: {username}, Role: {role}")
        print(f"Failed attempts: {failed_attempts}, Locked status: {locked_until} \n")
  except FileNotFoundError:
    print('User not found.')

def unlock_account():
  
  target = input('Enter the user name to unlock: ').strip()
  if target == "":
    print("Username cannot be empty.")
    return
  
  try:
    with open('accounts.csv', 'r', newline='') as file:
      users = list(csv.reader(file))
  except FileNotFoundError:
      print("No users file found.")
      return
  
  found = False
  for row in users:
    username, hashed_pw, failed_attempts, lock_until_status, role, reset_token, token_expiry = row
    if username == target:
      found = True
      unlocking = input('Do you want to unlock this user? Type (y/n) to proceed: ').lower().strip()
      if unlocking == 'y':
        row[2] = '0'
        row[3] = ''
        row[5] = ''
        row[6] = ''
        print("The user is now unlocked!")
        break
      else:
        break

  if not found:
      print("User not found.")
      return
  
  with open('accounts.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(users)
  
  log_event(current_user, "UNLOCK_ACCOUNT", f"Unlocked user: {target}")

def delete_user():
  if not require_admin():
    return
  
  target = input("Enter the username to delete: ").strip()
  
  if target == "":
      print("Username cannot be empty.")
      return
  
  if target == current_user:
    print('You cannot delete the admin account yourself.')
    return
  
  try:
    with open('accounts.csv', 'r', newline='') as file:
      users = list(csv.reader(file))
  except FileNotFoundError:
    print('User not found!')
    return
  
  new_users = []
  found = False
  for row in users:
    username, hashed_pw, failed_attempts, locked_status, role, reset_token, token_expiry = row
    if username == target:
      found = True
      print('The user account have been deleted!')
      continue
    new_users.append(row)

  
  if not found:
    print("User not found.")
    return
  
  with open('accounts.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(new_users)

  print("DEBUG: reached end of delete_user, about to log")
  log_event(current_user, "DELETE_USER", f"Deleted user: {target}")

def request_password_reset():
  username = input("Enter your username: ").strip()

  try:
    with open("accounts.csv", 'r', newline='') as file:
      users = list(csv.reader(file))
  except FileNotFoundError:
    print("If an account with that username exists, reset instructions have been generated.")
    return
  
  user_row = None
  for row in users:
    if row[0] == username:
      user_row = row
      break
  
  print("If an account with that username exists, reset instructions have been generated.")

  if user_row is None:
    return
  
  token = secrets.token_urlsafe(16)
  expiry = time.time() + 300

  user_row[4] = token
  user_row[5] = str(expiry)

  with open('accounts.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(users)

  print(f"Password reset token (simulated email): {token}")
  log_event(username, "RESET_REQUESTED", "Password reset token generated")

def reset_password():
  username = input("Username: ").strip()
  token = input("Enter reset token: ").strip()

  try:
    with open("accounts.csv", 'r', newline='') as file:
      users = list(csv.reader(file))
  except FileNotFoundError:
    print("Invalid request")
    return
  
  user_row = None
  for row in users:
    if row[0] == username:
      user_row = row
      break

  if user_row is None:
    print("Invalid request")
    return
  
  username_csv, hashed_pw, failed_attempts_str, lock_info_str, reset_token, token_expiry_str, role = user_row

  if reset_token != token:
    print('Invalid or Used token')
    return
  
  if time.time() > float(token_expiry_str):
    print('Token expired')
    user_row[4] = ""
    user_row[5] = ""
    with open('accounts.csv', 'w', newline='') as file:
      writer = csv.writer(file)
      writer.writerows(users)
    log_event(username_csv, "RESET_TOKEN_EXPIRED", "Tried to use expired reset token")
    return
  
  while True:
    new_password = input("Enter new password: ").strip()
    if new_password == "":
      print("Password cannot be empty!")
      continue

    is_valid, message = is_strong_password(new_password)

    if not is_valid:
      print(message)
    else:
      break

  new_hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

  user_row[1] = new_hashed
  user_row[2] = "0"
  user_row[3] = ""
  user_row[4] = ""
  user_row[5] = ""

  with open('accounts.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(users)

  print("Password reset successful.")
  log_event(username_csv, "PASSWORD_RESET", "Password reset via token")  

while True:

  if current_user is None:

    print("\n1. Register")
    print("2. Login")
    print("3. Request reset password")
    print("4. Reset password with token")
    print("5. Exit \n")

    choice = int(input("Please select from option (1-5): "))

    if choice == 1:
      register_user()

    elif choice == 2:
      login_user()

    elif choice == 3:
      request_password_reset()

    elif choice == 4:
      reset_password()

    elif choice == 5:
      break

  else:
    print(f"Logged in as: {current_user}")

    if current_role == 'admin':
      print("1. View all users")
      print("2. Unlock account")
      print("3. Delete user")
      print("4. Logout")

      choice = input("Please select an option (1-4): ").strip()

      if choice == '1':
        view_all_users()
      elif choice == '2':
        unlock_account()
      elif choice == '3':
        delete_user()
      elif choice == '4':
        logout_user()
      else:
        print("Invalid input! Please select from 1-5: ")

    else: 
      print(f"\nYou are logged in as: {current_user}")
      print("1. Logout")
      print("2. Exit")

      choice = input("Select from options (1-2): ").strip()

      if choice == '1':
        logout_user()
      elif choice == '2':
        break
      else:
        print("Invalid choice. Please enter 1 or 2.")
