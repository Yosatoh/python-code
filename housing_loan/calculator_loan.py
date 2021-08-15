from datetime import datetime
import time


class CalcLoan(object):
    """
    Calulate loan payment 
    """

    def __init__(self, initial_debt):
        
        self._loan_balances = [initial_debt]
        # for calculating of gradual rate in function(set_gradual_rate)
        self.loan_balance = initial_debt

    def set_initial(self, repay_period, initial_rate, initial_year=None, initial_month=None):
        """
        
        Args:
            repay_period (int): Repayment period(year)
            initial_rate (float): interest rates(annual interest[%]) 
            inital_year (int): Repayment start year (ex: 2022)
            initial_month (int): Repayment start month (ex: 6)
        """

        if initial_year is None:
            initial_year = datetime.now().year
        if initial_month is None:
            initial_month = datetime.now().month

        self.repay_period = repay_period
        self.rate = initial_rate
        self.initial_year = initial_year
        self.initial_month = initial_month
        self._date_pointer = [initial_year, initial_month]

        self.repayment = self.calc_repay(repay_period, initial_rate)

    def set_gradual_rate(self, rates, change_years, date_pointer=None):

        if date_pointer is None:
            date_pointer = self._date_pointer

        if isinstance(rates, int) or isinstance(rates, float):
            rates = [rates]
        if isinstance(change_years, int) or isinstance(change_years,float):
            change_years = [change_years]
        if len(rates) != len(change_years):
            raise Exception("The length of the rate list should be same as change_years")
                
        # Initializaion
        self._for_gradual_rate = []
        change_date_list = []
        change_years.sort()

        for change_year in change_years:
            if change_year < 1:
                raise ValueError("change_years should be equal and larger than 1")
            else:
                change_year += self.initial_year
            change_date_list.append([change_year, self.initial_month])

        # Initialization for calculate repayment amount.
        rate = self.rate
        repayment = self.repayment
        temporary_date_pointer = date_pointer.copy()
        loan_balance = self.loan_balance

        while True:
            # Update temporary_date_pointer
            temporary_date_pointer = self._update_date_pointer(temporary_date_pointer)

            # calculate loan_balance
            interest = int(loan_balance * (rate * 0.01 / 12))
            if loan_balance < repayment:                
                self._for_gradual_rate = [list(x) for x in zip(*self._for_gradual_rate)]

                if self._for_gradual_rate == []:
                    del self._for_gradual_rate
                break
            else:                
                loan_balance -= repayment - interest
                for i, graduate_date in enumerate(change_date_list):
                    if temporary_date_pointer == graduate_date:
                        repay_period = self.repay_period \
                                        + (self.initial_year - graduate_date[0]) \
                                        + (self.initial_month - graduate_date[1]) / 12
                        update_rate =  rates[i]
                        update_repayment = self.calc_repay(repay_period, update_rate, loan_balance)
                        self._for_gradual_rate.append([update_rate, update_repayment, graduate_date, change_years[i]])     

    def set_advanced_payment(self, amounts, dates, methods=None):
        """
        Args:
            methods = "shorten" or "reduce"
                "shorted": Shortening the period
                "reduce": Reducing the repayment amount
        """
        
        # TODO: create Error
        # the list of argument can be an integer or a float!
        if isinstance(amounts, int) or isinstance(amounts, float):
            amounts = [amounts]
        if isinstance(dates, int) or isinstance(dates,float):
            raise TypeError("Dates should be list")
        if methods is None:
            methods = []
            for _ in range(len(amounts)):
                methods.append("shorten")
        if not isinstance(dates[0], list):
            dates = [dates]

        self._prepay_amount_list = amounts
        self._prepay_date_list = dates
        self._prepay_method_list = methods

    def set_deduction_housing_loan(self, building_price, max_return=500_000):
        
        self._building_price = building_price
        self._max_return = max_return

    def _calc_deduction_housing_loan(self, ):
        
        try:
            building_price = self._building_price
            max_return = self._max_return
            loan_balance = self._loan_balances[-1]
        except AttributeError:
            return None

        if self._date_pointer[0] - self.initial_year + 1 <= 10:
            return_deduction = max_return if loan_balance * 0.01 >= max_return else loan_balance * 0.01
        elif self._date_pointer[0] - self.initial_year + 1 <= 13:
            if loan_balance * 0.01 >= building_price * 0.02 / 3:
                return_deduction = building_price * 0.02 / 3
            else:
                return_deduction = loan_balance * 0.01
        else:
            return None

        self._return_deduction_list.append(int(return_deduction))

    def calc_repay(self, repay_period, rate, loan_balance=None):

        if loan_balance is None:
            loan_balance = self._loan_balances[-1] 

        month_rate = rate * 0.01 / 12
        repayment =  loan_balance * month_rate * (1+month_rate)**(repay_period*12) / \
                       ((1 + month_rate) ** (repay_period*12) -1)
        return int(repayment)

    def _calc_prepay(self, loan_balance, rate, repayment, date_pointer=None):

        if date_pointer is None:
            date_pointer = self._date_pointer

        calculate_date = [date_pointer[0], date_pointer[1]]
        for i, prepayment_date in enumerate(self._prepay_date_list):
            if calculate_date == prepayment_date:
                loan_balance -= self._prepay_amount_list[i]
                self.loan_balance = loan_balance
                self.temp_prepayment = self._prepay_amount_list[i]
                if self._prepay_method_list[i] == "shorten":
                    self.temp_prepayment = self._prepay_amount_list[i]
                    return loan_balance, rate, repayment
                elif self._prepay_method_list[i] == "reduce":
                    # rewrite "prepayment_date" for calculate self._for_guradual_rate
                    if prepayment_date[1] != 1:
                        prepayment_date[1] -= 1
                    else:
                        prepayment_date[0] -= 1
                        prepayment_date[1] = 12                    

                    repay_period = self.repay_period \
                                    + (self.initial_year - prepayment_date[0]) \
                                    + (self.initial_month - prepayment_date[1]) / 12
                    update_repayment = self.calc_repay(repay_period, rate, loan_balance)
                    self.repayment = update_repayment
                    try:
                        rates = self._for_gradual_rate[0]
                        change_years = self._for_gradual_rate[3]
                        self.set_gradual_rate(rates, change_years, prepayment_date)
                    except AttributeError:
                        pass
                    return loan_balance, rate, update_repayment
                else:
                    raise Exception('the method of self.set_advanced_payment should be "shorten" or "reduce".')
        return loan_balance, rate, repayment

    def _calc_rate_repayment(self, rate, repayment, date_pointer=None):
        
        if date_pointer is None:
            date_pointer = self._date_pointer

        rate_list = self._for_gradual_rate[0]
        repayment_list = self._for_gradual_rate[1]
        change_date_list = self._for_gradual_rate[2]

        calculate_date = [date_pointer[0], date_pointer[1]]
        for i, graduate_date in enumerate(change_date_list):
            if calculate_date == graduate_date:
                repay_period = self.repay_period \
                                + (self.initial_year - graduate_date[0]) \
                                + (self.initial_month - graduate_date[1]) / 12
                update_rate =  rate_list[i]
                update_repayment = repayment_list[i]
                return update_rate, update_repayment
        return rate, repayment

    def _initialize_for_calculate(self):

        try:
            self.date_list
        except AttributeError:
            self.date_list = [datetime(self._date_pointer[0], self._date_pointer[1], 10)]

        try:
            self._repayment_list
        except AttributeError:
            self._repayment_list = [0]

        try:
            self.interest_list
        except AttributeError:
            self.interest_list = [0]

        try:
            self._return_deduction_list
        except AttributeError:
            self._return_deduction_list = []

        self.temp_prepayment = 0


    def _update_date_pointer(self, date_pointer=None):

        if date_pointer is None:
            if self._date_pointer[1] != 12:
                self._date_pointer[1] += 1
            else:
                self._date_pointer[0] += 1
                self._date_pointer[1] = 1
        else:
            if date_pointer[1] != 12:
                date_pointer[1] += 1
            else:
                date_pointer[0] += 1
                date_pointer[1] = 1
        
        return date_pointer

    def _print_results(self, timer=None):
        print(f"date: {self._date_pointer}")
        print(f"interest: {self.interest_list[-1]}")
        print(f"repayment: {self._repayment_list[-1]}")
        print(f"loan_balance: {self._loan_balances[-1]}")
        print()
        if timer is not None:
            try:
                time.sleep(timer)
            except ValueError:
                time.sleep(0.001)

    def calculate(self, print_show=True, timer=None):

        # initial setting
        self._initialize_for_calculate()

        # Before the while loop, assign initial values to variables.
        loan_balance = self._loan_balances[-1]
        rate = self.rate
        repayment = self.repayment

        while True:
            # Update day-pointer
            self._update_date_pointer()
            self.date_list.append(datetime(self._date_pointer[0], self._date_pointer[1], 10))

            # calculate of prepayment
            # Assumed that the repayment will be advanced before the repayment of this month.
            try:
                loan_balance, rate, repayment = self._calc_prepay(loan_balance, rate, repayment)
            except AttributeError:
                pass

            # calculate loan_balance
            interest = int(loan_balance * (rate * 0.01 / 12))
            if loan_balance < repayment:
                loan_balance = 0
                self.interest_list.append(interest)
                self._repayment_list.append(self._loan_balances[-1] + interest)
                self._loan_balances.append(loan_balance)

                if print_show:
                    self._print_results(timer=timer)
                print(f"total_repayment: {sum(self._repayment_list):,} yen")
                try:
                    # Don't show return of deduction in the case of not using function "set_deduction~"
                    self._max_return
                    print(f"total_return_of_deduction_housing_loan: {sum(self._return_deduction_list):,} yen")
                    print(f"total_repayment - return: {(sum(self._repayment_list) - sum(self._return_deduction_list)):,} yen")
                except AttributeError:
                    pass
                break
            else:                
                loan_balance -= repayment - interest
                self.interest_list.append(interest)
                self._loan_balances.append(loan_balance)
                self._repayment_list.append(repayment + self.temp_prepayment)
                self.temp_prepayment = 0

                if print_show:
                    self._print_results(timer=timer)

                # Update rate & repayment amount
                try:
                    rate, repayment = self._calc_rate_repayment(rate, repayment)
                    self.rate = rate
                    self.repayment = repayment
                except AttributeError:
                    pass

                # calculate deduction_housing_loan
                if self._date_pointer[1] == 12:
                    self._calc_deduction_housing_loan()