class Trove:
    def __init__(self, coll_price, coll_amount, min_coll_ratio, loan_value):
        if coll_price < 0 or coll_amount < 0 or loan_value < 0:
            raise Exception("Numbers below zero forbidden")
        if min_coll_ratio <= 1:
            raise Exception("min_coll_ratio must be greater than 1")
        coll_value =  coll_price * coll_amount
        if coll_value < min_coll_ratio * loan_value:
            raise Exception("Violation of min_coll_ratio")
        liquidation_buffer = coll_value / min_coll_ratio - loan_value
        
        self.__latest_coll_price = coll_price
        self.coll_amount = coll_amount
        self.coll_value = coll_value
        self.loan_value = loan_value
        self.liquidated = False
        self.liquidated_value = 0
        self.liquidation_buffer = liquidation_buffer
        self.coll_surplus = coll_value - liquidation_buffer - loan_value
        self.min_coll_ratio = min_coll_ratio
        
    def __liquidate(self, updated_coll_value):
        self.coll_amount = 0
        self.coll_value = 0
        self.liquidated = True
        self.liquidated_value = updated_coll_value - self.loan_value
        self.liquidation_buffer = 0
        self.coll_surplus = 0
    
    def update_coll_price(self, coll_price):
        if coll_price < 0:
            raise Exception("Collateral price must not be negative")
        if not self.liquidated:
            updated_coll_value = self.coll_amount * coll_price
            self.__latest_coll_price = coll_price
            min_coll_ratio_criterion = updated_coll_value >= self.min_coll_ratio * self.loan_value
            if min_coll_ratio_criterion:
                self.coll_value = updated_coll_value
                self.liquidation_buffer = self.coll_value / self.min_coll_ratio - self.loan_value
                self.coll_surplus = self.coll_value - self.liquidation_buffer - self.loan_value
            else:
                self.__liquidate(updated_coll_value)
    
    def update_loan(self, delta_coll_amount, delta_loan_value):    
        if not self.liquidated:
            updated_coll_amount = self.coll_amount + delta_coll_amount
            updated_loan_value = self.loan_value + delta_loan_value
            # negative values are allowed
            if updated_coll_amount < 0 or updated_loan_value < 0:
                raise Exception("Cannot extract more from the trove than it holds")
            updated_coll_value = updated_coll_amount * self.__latest_coll_price
            min_coll_ratio_criterion = updated_coll_value >= self.min_coll_ratio * updated_loan_value
            if min_coll_ratio_criterion:
                self.coll_amount = updated_coll_amount
                self.loan_value = updated_loan_value
                self.coll_value = updated_coll_value   
                self.liquidation_buffer = self.coll_value / self.min_coll_ratio - self.loan_value
                self.coll_surplus = self.coll_value - self.liquidation_buffer - self.loan_value
        
    def __str__(self):
        return str({
            'coll_amount': self.coll_amount,
            'coll_value': self.coll_value,
            'loan_value': self.loan_value,
            'liquidated': self.liquidated,
            'liquidated_value' : self.liquidated_value,
            'liquidation_buffer' : self.liquidation_buffer,
            'coll_surplus' : self.coll_surplus,
            'min_coll_ratio': self.min_coll_ratio
        })