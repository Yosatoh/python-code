from calculator_loan import CalcLoan

test = CalcLoan(30_000_000)
test.set_initial(35, 0.8, 2022, 1)

test.set_gradual_rate([1.0], [10])

# methods = "shorten" or "reduce"
test.set_advanced_payment(2_500_000, [2033,5], methods=["shorten"])

test.calculate(print_show=True, timer=None)