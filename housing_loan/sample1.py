from calculator_loan import CalcLoan


# 1) variables input
borrowing_amount = 30_000_000
building_amount = 15_000_000
prepayment_amount = 2_500_000

borrowing_period = 35
initial_year, initial_month = 2022, 1
prepayment_date = [2032, 1]
methods = ["shorten"]
prepayment = 4_000_000

rate1 = 0.8
rate2 = 1.0
change_rate_year = 10

# 2) calculate 
loan_calculator = CalcLoan(borrowing_amount)
loan_calculator.set_initial(borrowing_period, rate1, initial_year, initial_month)
loan_calculator.set_gradual_rate([rate2], [change_rate_year])
loan_calculator.set_advanced_payment(prepayment_amount, prepayment_date, methods=methods)
loan_calculator.set_deduction_housing_loan(building_amount)

loan_calculator.calculate(print_show=True, timer=None)

# 3) summary
print(f"\nSUMMARY:\n borrowing_amount: {borrowing_amount:,} yen")
print(f" prepayment: {prepayment:,}yen, prepayment_date: {prepayment_date}, methods: {methods},")
print(f" total_repayment - return: {(sum(loan_calculator._repayment_list) - sum(loan_calculator._return_deduction_list)):,} yen")
print(f" last repayment date: {loan_calculator._date_pointer}")