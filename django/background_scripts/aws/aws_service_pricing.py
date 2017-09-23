import math
import datetime
import calendar


class AwsSupportPricing:
    dev_support = 'AWS Support (Developer)'
    biz_support = 'AWS Support (Business)'
    enp_support = 'AWS Support (Enterprise)'

    def __init__(self):
        self.dev_support_cost = 0
        self.biz_support_cost = 0
        self.enp_support_cost = 0

        self.dev_subscription_duration = 0
        self.biz_subscription_duration = 0
        self.enp_subscription_duration = 0

    def pricing(self, product, cost):
        """ Cost calculation as per AWS Support Plan Pricing """
        support_cost = 0

        if product == self.dev_support:
            if cost <= 29:
                support_cost = 29
            else:
                support_cost = cost * 0.03

        elif product == self.biz_support:
            if cost <= 100:
                support_cost = 100
            elif cost <= 10000:
                support_cost = cost * 0.10
            elif 10000 < cost <= 80000:
                support_cost = 1000 + ((cost - 10000) * 0.07)
            elif 80000 < cost <= 250000:
                support_cost = 1000 + 4900 + ((cost - 80000) * 0.05)
            elif 250000 < cost:
                support_cost = 1000 + 4900 + 8500 + ((cost - 250000) * 0.03)

        elif product == self.enp_support:
            if cost <= 15000:
                support_cost = 15000
            elif cost <= (150 * math.pow(10, 3)):
                support_cost = cost * 0.10
            elif (150 * math.pow(10, 3)) < cost <= (500 * math.pow(10, 3)):
                support_cost = 15000 + ((cost - (150 * math.pow(10, 3))) * 0.07)
            elif (500 * math.pow(10, 3)) < cost <= math.pow(10, 6):
                support_cost = 15000 + 24500 + ((cost - (500 * math.pow(10, 3))) * 0.05)
            elif math.pow(10, 6) < cost:
                support_cost = 15000 + 24500 + 25000 + ((cost - math.pow(10, 6)) * 0.03)

        return support_cost

    def add_duration(self, product, days=0):

        if product == self.dev_support:
            self.dev_subscription_duration += days
        elif product == self.biz_support:
            self.biz_subscription_duration += days
        elif product == self.enp_support:
            self.enp_subscription_duration += days

    def add_cost(self, product, cost):
        cost = float(cost)

        if product == self.dev_support:
            self.dev_support_cost += cost
        elif product == self.biz_support:
            self.biz_support_cost += cost
        elif product == self.enp_support:
            self.enp_support_cost += cost

    def prorate_costs(self, total_charge, year, month):
        """ Prorating support service cost for no of days of subscription from monthly total service cost """

        max_days_in_month = calendar.monthrange(year=year, month=month)[1]

        self.dev_support_cost += (self.pricing(self.dev_support, total_charge) / max_days_in_month) * self.dev_subscription_duration
        self.biz_support_cost += (self.pricing(self.biz_support, total_charge) / max_days_in_month) * self.biz_subscription_duration
        self.enp_support_cost += (self.pricing(self.enp_support, total_charge) / max_days_in_month) * self.enp_subscription_duration

    def get_total_cost(self):
        """ Totaling all support service costs together """

        return self.dev_support_cost + self.biz_support_cost + self.enp_support_cost
