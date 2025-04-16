from app.models.subscription import BillingFrequency

def calculate_amount(price, frequency):
    amount = 0.00
    if price != 0.00 and BillingFrequency.yearly:
        amount = price * 12
    return amount