class OverseaDecisionProcessor:
    def __init__(self):
        pass

    def should_buy(self,
                   row: dict,
                   purchasable_amount: int,
                   current_price: float,
                   ) -> bool:
        if purchasable_amount == 0:
            return False

        if current_price < row['should_buy_price']:
            return True
        else:
            return False

    def should_sell(self,
                    row: dict,
                    current_price: float):
        if current_price > row['should_sell_price']:
            return True
        else:
            return False
