from bs4 import BeautifulSoup
from abc import ABCMeta, abstractmethod
from datetime import datetime
import asyncio
import requests
import re
import logging
import configparser
import os
import re
import json

from gsheet_client import GSheetClient
from logger import SheetLogger, LogInfo
from helper import human_price_to_integer


#env = 'test'
env = 'prod'

class Product:

    def __init__(self, original_price: float, sale_price: float, name: str = None):
        self.name = name
        self.original_price = original_price
        self.sale_price = sale_price

    def __str__(self):
        return "original_price: " + str(self.original_price ) + ", sale_price: " + str(self.sale_price)


class CrawlerListener():

    __metaclass__ = ABCMeta

    @abstractmethod
    def onFailed(self, product_link, err): raise NotImplementedError

    @abstractmethod
    def onSuccess(self, product_link, product): raise NotImplementedError


class LoggingListener(CrawlerListener):

    def __init__(self, sheet_logger):
        self.sheet_logger = sheet_logger

    def onFailed(self, product_link, err):
        log_infos = [LogInfo(product_link=product_link, err=err, time=datetime.now())]
        sheet_logger.log(log_infos)

    def onSuccess(self, product_link, product):
        pass


class TikiProductCrawler:
    
    async def get_price(self, link: str) -> Product:
        matcher = re.search("p(\d+)\.html", link)
        if not matcher:
            for listener in self.listeners:
                listener.onFailed(link, "Not found product_id pattern")
            raise Exception("Couldn't get product id from link " + link)
        product_id = matcher.group(1)
        p_link = f'https://tiki.vn/api/v2/products/{product_id}?platform=web'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
        }
        r = requests.get(p_link, headers=headers)
        if r.status_code not in (200, 201):
            raise Exception(f"error getting Tiki product: {product_id}, link: {link}")
        res = r.json()
        return Product(res["list_price"], res["price"], res["name"])
        

class M24hProductCrawler:

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting 24h product " + link)
        soup = BeautifulSoup(r.text, 'html.parser')
        original_price_tag = soup.find(id="data_price_old")
        sale_price_tag = soup.find(id="data_price")
        return Product(int(original_price_tag["value"]), int(sale_price_tag["value"]))


# Dien thoai gia kho
class DTGKProductCrawler:

    async def get_price(self, link: str) -> Product:
        last_part = link.split("/")[-1]
        last_part = last_part.split("?")[0]
        p_link = f'https://api.dienthoaigiakho.vn/api/products/{last_part}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
        }
        r = requests.get(p_link, headers=headers)
        if r.status_code not in (200, 201):
            raise Exception("error getting DTGK product " + p_link)
        res = r.json()
        return Product(res['price'], res['salePrice'], res['name'])


class BaoChauProductCrawler:

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting BaoChau product " + link)
        soup = BeautifulSoup(r.text, 'html.parser')
        pricing_tag = soup.find("div", {"class": "price_and_no"})
        p_tags = pricing_tag.find_all("p")
        current_price = human_price_to_integer(p_tags[0].strong.text)
        origianl_price = human_price_to_integer(p_tags[1].find("del").text)
        return Product(origianl_price, current_price)



# Antien antien.vn
class AntienProductCrawler:



    # Regular products
    # <div class="price-pro"> 
    #   <strong>3,450,000 đ</strong>
    # </div>

    # Products that on sale
    # <div class="price-pro"> 
    #   <strong>1,850,000 đ</strong>
    #   <span class="mid-line">
    #       2,250,000 đ  
    #   </span> 
    # </div>

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting Antien product " + link)
        soup = BeautifulSoup(r.text, 'html.parser')
        pricing_tag = soup.find("div", {"class": "price-pro"})
        original_price_tag = pricing_tag.find("strong")
        sale_price_tag = pricing_tag.find("strong")
        original_price = human_price_to_integer(original_price_tag.text)
        sale_price = human_price_to_integer(sale_price_tag.text if sale_price_tag is not None else original_price_tag.text)
        return Product(original_price, sale_price)


# Hoang Ha hoanghamobile.com
class HoangHaProductCrawler:

    # Regular products
    # <p class="price current-product-price"><strong> 11,990,000 ₫ </strong>

    # Prodcuts that on sale
    #<p class="price current-product-price">undefined
    #  <strong> 3,350,000 ₫ </strong>undefined
    #  <i>Giá Niêm Yết: undefined
    #  <strike>3,990,000 ₫</strike>undefined</i>undefined

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting HoangHa product " + link)
        soup = BeautifulSoup(r.text, 'html.parser')
        pricing_div = soup.find("p", {"class": "price current-product-price"})
        sale_price_tags = pricing_div.strong
        original_price_tags = pricing_div.strike
        original_price = 0
        sale_price = 0
        if original_price_tags:
            sale_price = human_price_to_integer(sale_price_tags.text)
            original_price = human_price_to_integer(original_price_tags.text)
        else:
            sale_price = human_price_to_integer(sale_price_tags.text)
            original_price = sale_price
        return Product(original_price, sale_price)


# Cellphone cellphones.com.vn
class CellphoneProductCrawler:


    PATTERN = re.compile(r"var\s+productJsonConfig\s+=(.*);?")

    async def get_price(self, link: str) -> Product:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
        }
        r = requests.get(link, headers = headers)
        if r.status_code not in (200, 201):
            raise Exception("error getting Cellphone product " + link)
        text = r.text
        try:
            return self._get_price_case1(text)
        except Exception:
            return self._get_price_case2(text)

    def _get_price_case1(self, text):
        matcher = self.PATTERN.search(text)
        if not matcher:
            raise Exception("error getting Cellphone product, not found pattern. Link" + link)
        jsonStr = matcher.group(1).strip()
        if jsonStr[-1] == ';':
            jsonStr = jsonStr[:-1]
        jsonConfig = json.loads(jsonStr)
        product_id = jsonConfig["productId"]
        soup = BeautifulSoup(text, 'html.parser')
        original_price_tag = soup.find("span", {"id": f"old-price-{product_id}"})
        sale_price_tag = soup.find("span", {"id": f"product-price-{product_id}"})
        original_price = human_price_to_integer(original_price_tag.text)
        sale_price = human_price_to_integer(sale_price_tag.text)
        return Product(original_price, sale_price)

    def _get_price_case2(self, text):
        soup = BeautifulSoup(text, 'html.parser')
        product_id_tag = soup.find("input", {"id": 'lastProductId'})
        product_id = product_id_tag["value"]
        sale_price_tag_id = f'product-price-{product_id}'
        original_price_tag_id = f'old-price-{product_id}'
        sale_price_tag = soup.find(id=sale_price_tag_id)
        original_price_tag = soup.find(id=original_price_tag_id)
        sale_price = human_price_to_integer(sale_price_tag.text)
        original_price = sale_price
        if original_price_tag:
            original_price = human_price_to_integer(original_price_tag.text)
        return Product(original_price, sale_price)


# Linh Anh dientulinhanh.com
class LinhAnhProductCrawler:

    # Regular price
    # <div class="price">
    #   <strong>1,050,000đ</strong>
    # </div>

    # Not found any product that on sale 

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting LinhAnh product " + link)
        soup = BeautifulSoup(r.text, 'html.parser')
        pricing_div = soup.find("div", {"class": "price"})
        price_tag = pricing_div.find("strong")
        original_price = human_price_to_integer(price_tag.text)
        return Product(original_price, original_price)


# Viettablet viettablet.com
class ViettabletProductCrawler:

    # Regular price
    # <span class="price" id="line_discounted_price_3261"><span id="sec_discounted_price_3261" class="price-num">23.590.000</span><span class="price-num">đ</span></span>

    # Products that on sale

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting Viettablet product " + link)
        soup = BeautifulSoup(r.text, 'html.parser')
        pricing_div = soup.find("span", {"class": "price-num"})
        # Not get original_price
        sale_price = human_price_to_integer(pricing_div.text)
        return Product(sale_price, sale_price)


# CTmobile ctmobile.vn
class CTMobileProductCrawler:

    # <div class="price-group price-group-varible">
    #   <div class="variation-price">
    #       <span class="price">23,600,000 đ</span>
    #       <span class="price_baohanh" hidden="">23600000</span>  
    #   </div>
    # </div>

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting CTMobile product " + link)
        soup = BeautifulSoup(r.text, 'html.parser')
        pricing_div = soup.find("span", {"class": "price"}) # get first
        sale_price = human_price_to_integer(pricing_div.text)
        return Product(sale_price, sale_price)


# Haloshop haloshop.v
class HaloshopProductCrawler:

    # Regular product
    # <div class="product-price-group">
    #   <div class="price-wrapper">
    #       <div class="price-group">
    #           <div class="product-price">28,700,000₫</div>
    #       </div>
    #   </div>
    # </div>


    # Products that on sale
    # <div class="product-price-group">
    #   <div class="price-wrapper">
    #       <div class="price-group">
    #           <div class="product-price-new">23,300,000₫</div>
    #           <div class="product-price-old">24,900,000₫</div>
    #       </div>
    #   </div>
    # </div>

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting Halo product " + link)
        soup = BeautifulSoup(r.text, 'html.parser')
        sale_price_tag = soup.find("div", {"class": "product-price"})
        if sale_price_tag:
            sale_price = human_price_to_integer(sale_price_tag.text)
            return Product(sale_price, sale_price)

        sale_price_tag = soup.find("div", {"class": "product-price-new"})
        original_price_tag = soup.find("div", {"class": "product-price-old"})
        sale_price = human_price_to_integer(sale_price_tag.text)
        original_price = human_price_to_integer(original_price_tag.text)
        return Product(original_price, sale_price)


class CrawlerGetter:
    CRAWLERS = {
                "tiki.vn": TikiProductCrawler(),
                "24hstore.vn": M24hProductCrawler(),
                "baochauelec.com": BaoChauProductCrawler(),
                "haloshop.vn": HaloshopProductCrawler(),
                "dienthoaigiakho.vn": DTGKProductCrawler(),
                "antien.vn": AntienProductCrawler(),
                "hoanghamobile.com": HoangHaProductCrawler(),
                "cellphones.com.vn": CellphoneProductCrawler(),
                "dientulinhanh.com": LinhAnhProductCrawler(),
                "viettablet.com": ViettabletProductCrawler(),
                "ctmobile.vn": CTMobileProductCrawler(),
            }

    def get_crawler(self, link: str):
        if "tiki.vn" in link:
            return self.CRAWLERS.get("tiki.vn")
        if "24hstore.vn" in link:
            return self.CRAWLERS.get("24hstore.vn")
        if "baochauelec.com" in link:
            return self.CRAWLERS.get("baochauelec.com")
        if "haloshop.vn" in link:
            return self.CRAWLERS.get("haloshop.vn")
        if "dienthoaigiakho.vn" in link:
            return self.CRAWLERS.get("dienthoaigiakho.vn")
        if "antien.vn" in link:
            return self.CRAWLERS.get("antien.vn")
        if "hoanghamobile.com" in link:
            return self.CRAWLERS.get("hoanghamobile.com")
        if "cellphones.com.vn" in link:
            return self.CRAWLERS.get("cellphones.com.vn")
        if "dientulinhanh.com" in link:
            return self.CRAWLERS.get("dientulinhanh.com")
        if "viettablet.com" in link:
            return self.CRAWLERS.get("viettablet.com")
        if "ctmobile.vn" in link:
            return self.CRAWLERS.get("ctmobile.vn")
        raise Exception("not found suitable crawler for link {}".format(link))


def run():
    asyncio.run(populate_prices())


async def populate_prices():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'app.ini'))

    #logging.info(f"Running...")
    SPREADSHEET_ID = config['DEFAULT']['SPREADSHEET_ID']
    LINK_RANGE_FORMART = config['DEFAULT']['LINK_RANGE_FORMART']
    PRICING_RANGE_FORMAT = config['DEFAULT']['PRICING_RANGE_FORMAT']
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.edit']
    LOGGING_SPREADSHEET_ID =  config['DEFAULT']['LOGGING_SPREADSHEET_ID']
    LOGGING_LOG_RANGE_FORMAT =  config['DEFAULT']['LOGGING_LOG_RANGE_FORMAT']
    LOGGING_METADATA_RANGE =  config['DEFAULT']['LOGGING_METADATA_RANGE']
    gsheet_client = GSheetClient(SPREADSHEET_ID, SCOPES)
    logging_gsheet_client = GSheetClient(LOGGING_SPREADSHEET_ID, SCOPES)
    sheet_logger = SheetLogger(logging_gsheet_client, LOGGING_METADATA_RANGE, LOGGING_LOG_RANGE_FORMAT)

    crawler_getter = CrawlerGetter()
    starting_index = 2
    STEPS = 20

    while True:
        link_range = LINK_RANGE_FORMART.format(starting_index, starting_index + STEPS)
        result = gsheet_client.get(link_range)
        if not result:
            break

        log_errors = []
        tasks = []
        values = []
        for row in result:
            if len(row) == 0:
                tasks.append(asyncio.create_task(empty()))
                continue
            link = row[0]
            crawler = crawler_getter.get_crawler(link)
            tasks.append(asyncio.create_task(crawler.get_price(link)))

        products = await asyncio.gather(*tasks, return_exceptions=True)
        for product in products:
            if product is None:
                values.append([])
            elif isinstance(product, Product):
                values.append([product.sale_price, product.original_price])
            else:
                e = product
                log_info = LogInfo("", str(e), datetime.now())
                log_errors.append(log_info)
                #logging.error("error crawling {}".format(str(e)))
                values.append([0,0])

        pricing_range = PRICING_RANGE_FORMAT.format(starting_index, starting_index + STEPS)
        gsheet_client.update(pricing_range, values) 
        sheet_logger.log(log_errors)
        starting_index += STEPS
    #logging.info("Done")


async def empty():
    return None


def setup():
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='app.log', filemode='a', level=logging.INFO)


if __name__ == "__main__":
    #setup()
    run()
