all_expenses =[]

def load_data():
  try:
    with open("Expenses.txt", "r") as file:
      for line in file:
        part = line.strip().split(",")

        expenses = {
          "amount": float(part[0]),
          "category": part[1],
          "description": part[2]
        }
        all_expenses.append(expenses)
  except FileNotFoundError:
    pass

def add_expense(amount, category, description):
  expense = {
    "amount": float(amount),
    "category": category,
    "description": description
  }
  all_expenses.append(expense)

  with open("Expenses.txt", "a") as file:
    file.write(f"{amount}, {category}, {description} \n")

def view_expense():
  if not all_expenses:
    print("No records found!")
    return
  for index, expense in enumerate(all_expenses, start=1):
    print(f"{index}, ${expense['amount']}, {expense['category']}, {expense['description']}")

def total_expense():
  total = sum(expense['amount'] for expense in all_expenses)
  print(f"${total}")      


load_data()

while True:
  print("\n1. Add Expense")
  print("2. View Expenses")
  print("3. Total Expenses")
  print("4. Exit")

  choice = int(input("Please choose between (1-4) \n"))

  if choice == 1:
    amount = float(input("Add your amount: $"))
    category = input("What is the category ").strip()
    description = input("what is the description ").strip()

    add_expense(amount, category, description)

  elif choice == 2:
    view_expense()

  elif choice == 3:
    total_expense()

  elif choice == 4:
    break
