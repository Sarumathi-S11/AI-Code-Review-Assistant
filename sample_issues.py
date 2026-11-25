import os
import math

def CalculateTotal(price, quantity, tax, discount, shipping, extra):
    subtotal = price * quantity
    total = subtotal + tax - discount + shipping + extra
    return total

class data_processor:
    def process_data(self):
        try:
            value = 10 / 0
        except:
            pass
        return value
