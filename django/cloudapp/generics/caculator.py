import datetime
from django.utils import timezone
from dateutil.tz import tzutc


def calculate_discount_percentage(price, discounted_price):
    """ Calculating discount price from price and reduced price """

    discounted_amount = price - discounted_price

    if discounted_amount >= 0 and price > 0:
        discount_percentage = (discounted_amount / price) * 100
        return round(discount_percentage, 2)
    else:
        return round(0, 2)

def calculate_sale_price(original_price, discount):
    """ Calculating sale price from original price and discount """
    if discount > 0:
        discount_amount = original_price * (discount / 100)
        sale_price = original_price - discount_amount
        return round(sale_price, 2)
    else:
        return round(original_price, 2)


def calculate_azure_partner_cost(cost, partner_discount=None):
    """ Calculating azure service cost from redington price to partner price """
    if partner_discount:
        return (cost / 0.85) * ((100-partner_discount)/100)
    else:
        return (cost / 0.85) * 0.90


def descend_quarters_from_now():
    """ Listing year quarters descending from current month """
    today = datetime.datetime.now()
    default_timezone = tzutc()
    quarter_ranges = ((1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12))
    current_quarter = (today.month - 1) // 3
    previous_four_quarters = []
    quater_month =[]

    for i in range(0, 4):
        quarter, yd = (current_quarter - i, 0) if current_quarter - i >= 0 else (4 + current_quarter - i, -1)
        start_date = datetime.datetime(today.year + yd, quarter_ranges[quarter][0], 1,tzinfo=tzutc())
        end_date = None

        if (quarter_ranges[quarter][2] + 1) <= 12:
            end_date = datetime.datetime(today.year + yd, (quarter_ranges[quarter][2]) + 1, 1,tzinfo=tzutc()) - datetime.timedelta(seconds=1)
        else:
            end_date = datetime.datetime(today.year + yd + 1, 1, 1,tzinfo=tzutc()) - datetime.timedelta(
                seconds=1)
        Quarter_start = start_date.strftime('%b')
        quarter_end = end_date.strftime('%b-%Y')
        month_obj = Quarter_start + '-' + quarter_end
        quater_month.append(month_obj)
        date_range = (start_date, end_date)
        previous_four_quarters.append(
            {
                'year': today.year + yd,
                'quarter': quarter_ranges[quarter],
                'date_range': date_range
            })

    return previous_four_quarters,quater_month


def month_list_range():
    #default_timezone = datetime.timezone.get_default_timezone()
    month_namearray = []
    month_list=[]
    today = datetime.date.today()
    for k in range(1, 13):
        if k == 1:
            today = datetime.date.today()
            list = today.strftime("%Y,%m")
            getmonth_name = today.strftime('%b-%Y')
            month_namearray.append(getmonth_name)
            month_list.append(list)
        else:
            today = months
        first = today.replace(day=1)
        lastMonth = first - datetime.timedelta(days=1)
        months = lastMonth.replace(day=1)
        list = months.strftime("%Y,%m")
        getmonth_name = months.strftime('%b-%Y')
        month_namearray.append(getmonth_name)
        month_list.append(list)

    return month_list, month_namearray


def half_year_arange():
    today = datetime.datetime.now()
    quarter_ranges = ((1, 6), (7, 12))
    current_quarter = (today.month - 1) // 6
    previous_six_quarters = []
    halfrange_month=[]
    default_timezone = tzutc()

    for i in range(0, 2):
        quarter, yd = (current_quarter - i, 0) if current_quarter - i >= 0 else (2 + current_quarter - i, -1)
        start_date = datetime.datetime(today.year + yd, quarter_ranges[quarter][0], 1,tzinfo=default_timezone)
        end_date = None

        if (quarter_ranges[quarter][1] + 1) <= 12:
            end_date = datetime.datetime(today.year + yd, (quarter_ranges[quarter][1]) + 1, 1,tzinfo=default_timezone) - datetime.timedelta(seconds=1)
        else:
            end_date = datetime.datetime(today.year + yd + 1, 1, 1,tzinfo=default_timezone) - datetime.timedelta(
                seconds=1)
        half_startmonth = start_date.strftime('%b')
        half_endmonth = end_date.strftime('%b-%Y')
        halfmonth_obj = half_startmonth + '-' + half_endmonth
        halfrange_month.append(halfmonth_obj)

        date_range = (start_date, end_date)
        previous_six_quarters.append(
            {
                'year': today.year + yd,
                'quarter': quarter_ranges[quarter],
                'date_range': date_range
            })

    return previous_six_quarters,halfrange_month


