def human_price_to_integer(human_price):
    price_str = ''.join(filter(str.isnumeric, human_price))
    return int(price_str, 10)

