
def expense(select):
    while select == True:
        print("Add Expense")
        print("View Expense")
        print("View Total Spending")
        print("Exit")
        choice = int(input("Enter your choice :"))
        expense_store =[]
        final_amount = []
        if choice == 1:
            
            expense_name = input("Enter the name of Expense :")
            expense_amount = int(input("Enter the amount :"))
            exp = {"1": "Food", "2": "Travel", "3": "Shopping", "4": "Bills"}
            print(exp)
            cat = input("select category :")
            if cat == "1":
                print("food")
            elif cat == "2":
                print("travel")
            elif cat == "3":
                print("shopping")
            elif cat == "4":
                print("bills")
            print(cat)
        elif choice== 2:
            expense_store.append((expense_name, expense_amount, cat))
            print("Expense List:", expense_store)
        elif choice == 3:
            final_amount.append(expense_amount)
            total = sum(final_amount)
            print("Total Spending:", total)
        elif choice == 4:
            print("Exit")
            break
expense(select = True)       
            