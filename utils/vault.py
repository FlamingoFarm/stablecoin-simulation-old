class Vault:
    def __init__(self, coll_price: float, coll_balance: float, min_coll_ratio: float, loan_value: float):
        if coll_price < 0 or coll_balance < 0 or loan_value < 0:
            raise Exception("Numbers below zero forbidden")
        if min_coll_ratio <= 1:
            raise Exception("min_coll_ratio must be greater than 1")
        coll_value =  coll_price * coll_balance
        if coll_value < min_coll_ratio * loan_value:
            raise Exception("Violation of min_coll_ratio")
        liquidation_buffer = coll_value / min_coll_ratio - loan_value
        
        self.__latest_coll_price = coll_price
        self.coll_balance = coll_balance
        self.coll_value = coll_value
        self.loan_value = loan_value
        self.liquidated = False
        self.liquidated_value = 0
        self.liquidation_buffer = liquidation_buffer
        self.volatility_buffer = coll_value - liquidation_buffer - loan_value
        self.min_coll_ratio = min_coll_ratio
        
    def __liquidate(self, updated_coll_value: float):
        self.coll_balance = 0
        self.coll_value = 0
        self.liquidated = True
        self.liquidated_value = updated_coll_value - self.loan_value
        self.liquidation_buffer = 0
        self.volatility_buffer = 0
    
    def update_coll_price(self, coll_price: float):
        if coll_price < 0:
            raise Exception("Collateral price must not be negative")
        if not self.liquidated:
            updated_coll_value = self.coll_balance * coll_price
            self.__latest_coll_price = coll_price
            min_coll_ratio_criterion = updated_coll_value >= self.min_coll_ratio * self.loan_value
            if min_coll_ratio_criterion:
                self.coll_value = updated_coll_value
                self.liquidation_buffer = self.coll_value / self.min_coll_ratio - self.loan_value
                self.volatility_buffer = self.coll_value - self.liquidation_buffer - self.loan_value
            else:
                self.__liquidate(updated_coll_value)
    
    def update_loan(self, delta_coll_balance: float, delta_loan_value: float):    
        if not self.liquidated:
            updated_coll_balance = self.coll_balance + delta_coll_balance
            updated_loan_value = self.loan_value + delta_loan_value
            # negative values are allowed
            if updated_coll_balance < 0 or updated_loan_value < 0:
                raise Exception("Cannot extract more from vault than it holds")
            updated_coll_value = updated_coll_balance * self.__latest_coll_price
            min_coll_ratio_criterion = updated_coll_value >= self.min_coll_ratio * updated_loan_value
            if min_coll_ratio_criterion:
                self.coll_balance = updated_coll_balance
                self.loan_value = updated_loan_value
                self.coll_value = updated_coll_value   
                self.liquidation_buffer = self.coll_value / self.min_coll_ratio - self.loan_value
                self.volatility_buffer = self.coll_value - self.liquidation_buffer - self.loan_value
        
    def __str__(self):
        return str({
            'coll_balance': self.coll_balance,
            'coll_value': self.coll_value,
            'loan_value': self.loan_value,
            'liquidated': self.liquidated,
            'liquidated_value' : self.liquidated_value,
            'liquidation_buffer' : self.liquidation_buffer,
            'volatility_buffer' : self.volatility_buffer,
            'min_coll_ratio': self.min_coll_ratio
        })