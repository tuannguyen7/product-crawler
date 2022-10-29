import time


def human_price_to_integer(human_price):
    price_str = ''.join(filter(str.isnumeric, human_price))
    return int(price_str, 10)

def execution_time(func_name, func):
    start = time.time()
    result = func
    end = time.time()
    print(f"{func_name} took {end-start}s")
    return result