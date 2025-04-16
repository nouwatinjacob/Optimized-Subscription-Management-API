from dateutil.relativedelta import relativedelta
from app.models.subscription import BillingFrequency
from .time_util import utc_now

def get_subscription_date_bound(frequency):
    start_date = utc_now()
    print("frequency>>>>>>>>>", BillingFrequency.monthly.value)
    if isinstance(frequency, str):
        try:
            frequency = BillingFrequency(frequency)
        except ValueError:
            return start_date, None

    if frequency == BillingFrequency.monthly.value:
        end_date = start_date + relativedelta(months=1)
    elif frequency == BillingFrequency.yearly.value:
        end_date = start_date + relativedelta(years=1)
    else:
        end_date = None

    return start_date, end_date
    
def get_downgrade_bound(current_plan_end_date, frequency):
    
    start_date = current_plan_end_date
    
    if isinstance(frequency, str):
        try:
            frequency = BillingFrequency(frequency)
        except ValueError:
            return start_date, None

    if frequency == BillingFrequency.monthly.value:
        end_date = start_date + relativedelta(months=1)
    elif frequency == BillingFrequency.yearly.value:
        end_date = start_date + relativedelta(years=1)
    else:
        end_date = None

    return start_date, end_date