import string
import random

def password_generate(length):
  UPPERCASE = string.ascii_uppercase
  LOWERCASE = string.ascii_lowercase
  DIGITS = string.digits
  SPECIAL = string.punctuation

  password_parts = []

  password_parts.append(random.choice(UPPERCASE))
  password_parts.append(random.choice(LOWERCASE))
  password_parts.append(random.choice(DIGITS))
  password_parts.append(random.choice(SPECIAL))

  ALL_CHRCS = UPPERCASE + LOWERCASE + DIGITS + SPECIAL

  remaining_length = length - 4

  for _ in range(remaining_length):
    password_parts.append(random.choice(ALL_CHRCS))

  random.shuffle(password_parts)

  final_password = ''.join(password_parts)

  return final_password

def problems_pass(has_upper, has_lower, has_digit, has_special, is_long_enough):
  if not has_upper:
    print("Missing uppercase letter")

  if not has_lower:
    print("Missing lowercase letter")
  
  if not has_digit:
    print("Missing numbers")

  if not has_special:
    print("Missing speciel characters")

  if not is_long_enough:
    print("Not long enough")

def check_password_strength(password):
  has_upper = False
  has_lower = False
  has_digit = False
  has_special = False
  is_long_enough = False
  special_char = "!@#$%^&*()-_=+[]}{;:,.<>/?"
  score = 0

  for char in password:
    if char.isupper():
      has_upper = True

    if char.islower():
      has_lower = True

    if char.isdigit():
      has_digit = True

    if char in special_char:
      has_special = True
    
  if len(password) >= 8:
    is_long_enough = True

  if has_upper:
    score += 1
  
  if has_lower:
    score += 1

  if has_digit:
    score += 1

  if has_special:
    score += 1

  if is_long_enough:
    score += 1 

  return score, has_upper, has_lower, has_digit, has_special, is_long_enough

while True:
  print("\n1. Check password strength ")
  print("2. Generate strong password ")
  print("3. Exit ")

  choice = int(input("Please choose between (1-3) \n"))

  if choice == 1:
    password = input("Share your password to check it's strength: ")
    score, has_upper, has_lower, has_digit, has_special, is_long_enough = check_password_strength(password)

    if score <= 2:
      print('Weak password \nProblems:')
      problems_pass(has_upper, has_lower, has_digit, has_special, is_long_enough)

    elif score <= 4:
      print('Medium password \nProblems:')
      problems_pass(has_upper, has_lower, has_digit, has_special, is_long_enough)
    
    else:
      print('Strong password Congratulations!')
      print('Your password satisfy all conditions.')
      print(f'And is {len(password)} characters long')

  if choice == 2:
    length = int(input("How much length of password you are looking for? "))
    generate_pass = password_generate(length)
    print(f"Your strong password is: {generate_pass}")

  if choice == 3:
    break
