from bs4 import BeautifulSoup
from abc import ABCMeta, abstractmethod
import requests
import re
import json
import lxml
import cchardet

from helper import human_price_to_integer


#env = 'test'
env = 'prod'

class Product:

    def __init__(self, original_price: float, sale_price: float, name: str = None, link: str = None):
        self.name = name
        self.original_price = original_price
        self.sale_price = sale_price
        self.link = link

    def __str__(self):
        return "original_price: " + str(self.original_price ) + ", sale_price: " + str(self.sale_price)


class CrawlerListener():

    __metaclass__ = ABCMeta

    @abstractmethod
    def onFailed(self, product_link, err): raise NotImplementedError

    @abstractmethod
    def onSuccess(self, product_link, product): raise NotImplementedError


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
        return Product(original_price=res["list_price"], sale_price=res["price"], name=res["name"], link=link)
        

class M24hProductCrawler:

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting 24h product " + link)
        soup = BeautifulSoup(r.text, 'lxml')
        price_div = soup.find("div", {"class": "price_ins"})
        if not price_div:
            raise Exception(f"error getting m24 product, not found price_ins class, link: {link}")

        original_price_tag = price_div.find("span", {"class": "_price"})
        if not original_price_tag:
            raise Exception(f"error getting m24 product, not found span _price class, link: {link}")
        original_price = human_price_to_integer(original_price_tag.text)
        sale_price_tag = price_div.find("span", {"class": "price_old"})
        sale_price = original_price
        if sale_price_tag:
            sale_price = human_price_to_integer(sale_price_tag.text)

        return Product(original_price=original_price, sale_price=sale_price, link=link)


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
        return Product(original_price=res['price'], sale_price=res['salePrice'], name=res['name'], link=link)


class BaoChauProductCrawler:

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting BaoChau product " + link)
        soup = BeautifulSoup(r.text, 'lxml')
        pricing_tag = soup.find("div", {"class": "price_and_no"})
        p_tags = pricing_tag.find_all("p")
        current_price = human_price_to_integer(p_tags[0].strong.text)
        origianl_price_tag = p_tags[1].find("del") if len(p_tags) >= 2 else None
        original_price = current_price
        if origianl_price_tag:
            original_price = human_price_to_integer(origianl_price_tag.text)

        return Product(original_price=original_price, sale_price=current_price, link=link)



# Antien antien.vn
class AntienProductCrawler:


    # Regular products, Products that on sale
    # <div class="product-detail-info">
    #   <div class="product-price">
    #      <span class="price product-main-price">1.700.000 ₫</span> # on sale
    #      <span class="old-price">2.190.000 ₫</span>                # regular price
    #   </div>
    # </div>

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting Antien product " + link)
        soup = BeautifulSoup(r.text, 'lxml')
        product_tag = soup.find("div", {"class": "product-detail-info"})
        
        original_price_tag = product_tag.find("span", {"class": "price product-main-price"})
        sale_price_tag = product_tag.find("span", {"class": "old-price"})
        original_price = human_price_to_integer(original_price_tag.text)
        sale_price = human_price_to_integer(sale_price_tag.text if sale_price_tag is not None else original_price_tag.text)
        return Product(original_price=original_price, sale_price=sale_price, link=link)


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
        soup = BeautifulSoup(r.text, 'lxml')
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
        return Product(original_price=original_price, sale_price=sale_price, link=link)


# Cellphone cellphones.com.vn
class CellphoneProductCrawler:

    # <div class="box-info__box-price">
    #  <p class="product__price--show">590.000 ₫</p>
    #  <p class="product__price--through">699.000 ₫</p>
    # </div>

    async def get_price(self, link: str) -> Product:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
        }
        r = requests.get(link, headers = headers)
        if r.status_code not in (200, 201):
            raise Exception("error getting Cellphone product " + link)
        soup = BeautifulSoup(r.text, 'lxml')
        pricing_div = soup.find("div", {"class": "box-info__box-price"})
        sale_price_tag = pricing_div.find("p", {"class": "product__price--show"})
        original_price_tag = pricing_div.find("p", {"class": "product__price--through"})
        original_price = 0
        sale_price = 0
        if original_price_tag:
            sale_price = human_price_to_integer(sale_price_tag.text)
            original_price = human_price_to_integer(original_price_tag.text)
        else:
            sale_price = human_price_to_integer(sale_price_tag.text)
            original_price = sale_price
        return Product(original_price=original_price, sale_price=original_price, link=link)


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
        soup = BeautifulSoup(r.text, 'lxml')
        pricing_div = soup.find("div", {"class": "price"})
        price_tag = pricing_div.find("strong")
        original_price = human_price_to_integer(price_tag.text)
        return Product(original_price=original_price, sale_price=original_price, link=link)


# Viettablet viettablet.com
class ViettabletProductCrawler:

    # Regular price
    # <span class="price" id="line_discounted_price_3261"><span id="sec_discounted_price_3261" class="price-num">23.590.000</span><span class="price-num">đ</span></span>

    # Products that on sale

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting Viettablet product " + link)
        soup = BeautifulSoup(r.text, 'lxml')
        pricing_div = soup.find("span", {"class": "price-num"})
        # Not get original_price
        sale_price = human_price_to_integer(pricing_div.text)
        return Product(original_price=sale_price, sale_price=sale_price, link=link)


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
        soup = BeautifulSoup(r.text, 'lxml')
        pricing_div = soup.find("span", {"class": "price"}) # get first
        sale_price = human_price_to_integer(pricing_div.text)
        return Product(original_price=sale_price, sale_price=sale_price, link=link)


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
        soup = BeautifulSoup(r.text, 'lxml')
        sale_price_tag = soup.find("div", {"class": "product-price"})
        if sale_price_tag:
            sale_price = human_price_to_integer(sale_price_tag.text)
            return Product(sale_price=sale_price, original_price=sale_price, link=link)

        sale_price_tag = soup.find("div", {"class": "product-price-new"})
        original_price_tag = soup.find("div", {"class": "product-price-old"})
        sale_price = human_price_to_integer(sale_price_tag.text)
        original_price = human_price_to_integer(original_price_tag.text)
        return Product(original_price=original_price, sale_price=sale_price, link=link)


class BachLongProductCrawler:

    # Regular product
    # <div class="box-title-product">
    #   <input type="hidden" name="pricedetail" data-price="31990000">
    #   <p class="giathuoc" style="color:teal">(Chính hãng)</p>
    #   <strong class="price">
    #      <span class="price">31.990.000 ₫</span>
    #   </strong>
    #   <p class="is_vat"><i>(VAT 10%)</i></p>                
    # </div>
    
    # Products that on sale
    # <div class="box-title-product">
    #   <input type="hidden" name="pricedetail" data-price="6290000">
    #   <p class="giathuoc" style="color:teal">(Chính hãng)</p>
    #   <strong class="specialprice">
    #      <span class="price">6.290.000 ₫</span>
    #   </strong>
    #   <span class="oldprice">
    #      <span class="price">6.990.000 ₫</span>
    #   </span>
    #   <p class="is_vat"><i>(VAT 10%)</i></p>
    # </div>

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting Bach Long product " + link)
        soup = BeautifulSoup(r.text, 'lxml')
        price_div = soup.find("div", {"class": "box-title-product"})
        sale_price_tag = price_div.find("span", {"class": "price"})
        original_price_tag = soup.find("span", {"class": "oldprice"})
        original_price = 0
        sale_price = 0
        if original_price_tag:
            sale_price = human_price_to_integer(sale_price_tag.text)
            original_price = human_price_to_integer(original_price_tag.text)
        else:
            sale_price = human_price_to_integer(sale_price_tag.text)
            original_price = sale_price
        return Product(original_price=original_price, sale_price=sale_price, link=link)


class DidongvietProductCrawler:

    ### Original price from html tags
    # Regular product
    # <span class="price-container price-final_price tax weee"     itemprop="offers" itemscope itemtype="http://schema.org/Offer">
    #   <span class="price">8.990.000 ₫</span>        
    #   <span class="price-old">10.790.000 ₫</span> 
    # </span>

    # Products that on sale
    # <span class="price-container price-final_price tax weee"     itemprop="offers" itemscope itemtype="http://schema.org/Offer">
    #   <span class="price">8.990.000 ₫</span> <--- ORIGINAL PRICE HERE
    # </span>

    ### Get sale price from <script>
    #    <script>
    #    dataLayer.push({
    #      'dr_event_type' : 'view_item',
    #      'dr_value' : 6590000,   // product price   <---- SALE PRICE HERE
    #      'dr_items' : [{
    #          'id': '4782',   // should be the same as the id in Google Merchant Center, 
    #          'google_business_vertical': 'retail'
    #        }],
    #      'event':'dynamic_remarketing'
    #    });
    #    </script>

    PATTERN = re.compile(r"<script>\s*dataLayer\.push\(((.|\n)*?)\s*\);\s*</script>")

    # sale prices are taken from <script>
    # original prices (market prices) are taken from html tags
    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting di dong viet product " + link)
        body = r.text
        return self.get_original_price(body, body, link)
        #sale_price = self.get_sale_price(body, link)
        #product_in_html = self.get_original_price(body)

        # replace by sale_price from <script>
        #product_in_html.sale_price = sale_price
        #return product_in_html

    def get_original_price(self, text, link) -> Product:
        soup = BeautifulSoup(text, 'lxml')
        price_div = soup.find("span", {"class": "price-container price-final_price tax weee"})
        sale_price_tag = price_div.find("span", {"class": "price"})
        original_price_tag = soup.find("span", {"class": "price-old"})
        original_price = 0
        sale_price = 0
        if original_price_tag:
            sale_price = human_price_to_integer(sale_price_tag.text)
            original_price = human_price_to_integer(original_price_tag.text)
        else:
            sale_price = human_price_to_integer(sale_price_tag.text)
            original_price = sale_price

        return Product(original_price=original_price, sale_price=sale_price, link=link)

    # In-progress
    def get_sale_price(self, text, link) -> int:
        matcher = self.PATTERN.search(text)
        if not matcher:
            raise Exception("error getting Didongviet product, not found pattern. Link" + link)
        jsonStr = matcher.group(1).strip()
        # remove last ;
        if jsonStr[-1] == ';':
            jsonStr = jsonStr[:-1]
        print(jsonStr)
        #jsonStr = jsonStr.replace("'", "\"")
        product = json.loads(jsonStr)
        return product["dr_value"]
        

class MinhTuanMobileProductCrawler:

    ## Sale price
    # var price_current = 4990000;

    ## Original price
    # price: 'Giá thị trường: 5,990,000 vnđ',

    SALE_PRICE_PATTERN = re.compile(r"var\s+price_current\s+=\s*(\d+);")
    ORIGINAL_PRICE_PATTERN = re.compile(r"price:\s+'Giá thị trường:\s*(.*)',")

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting minhtuanmobile product " + link)
        text = r.text
        sale_price_matcher = self.SALE_PRICE_PATTERN.search(text)
        original_price_matcher = self.ORIGINAL_PRICE_PATTERN.search(text)

        if not sale_price_matcher:
            raise Exception("error getting MinhTuanMobile product, not found price. Link " + link)

        sale_price_text = sale_price_matcher.group(1).strip()
        sale_price = human_price_to_integer(sale_price_text)
        original_price = sale_price
        if original_price_matcher:
            original_price = human_price_to_integer(original_price_matcher.group(1).strip())
        return Product(original_price=original_price, sale_price=sale_price, link=link)


class DucHuyMobileProductCrawler:

    # <script> dataLayer = [{ 'ID': '4241', 'value': 1 }]; </script> // get product id
    # <span id="sec_discounted_price_4241" class="price-num">1.899.000</span>

    PATTERN = re.compile(r"<script>\s*dataLayer\s*=(.*?);\s*</script>")

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting duc huy product " + link)
        matcher = self.PATTERN.search(r.text)
        if not matcher:
            raise Exception("error getting Cellphone product, not found pattern. Link" + link)
        soup = BeautifulSoup(r.text, 'lxml')
        jsonStr = matcher.group(1).strip()
        if jsonStr[-1] == ';':
            jsonStr = jsonStr[:-1]
        jsonStr = jsonStr.replace("'", "\"")
        p_arr = json.loads(jsonStr)
        first_pid = p_arr[0]['ID']
        sale_price_tag = soup.find(id=f"sec_discounted_price_{first_pid}")
        sale_price = 0
        if sale_price_tag:
            sale_price = human_price_to_integer(sale_price_tag.text)
        return Product(sale_price=sale_price, original_price=sale_price, link=link)


class HNamMobileProductCrawler:


    # Regular
    # <input type="hidden" name="price" class="product-item-value-price" value="4799000">
    # <input type="hidden" name="price-base" class="product-item-value-price-base" value="0">


    # On sale
    # <input type="hidden" name="price" class="product-item-value-price" value="4049000">
    # <input type="hidden" name="price-base" class="product-item-value-price-base" value="4490000">

    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting Hnam product " + link)
        soup = BeautifulSoup(r.text, 'lxml')
        sale_price_tag = soup.find("input", {"class": "product-item-value-price"})
        original_price_tag = soup.find("input", {"class": "product-item-value-price-base"})
        sale_price = human_price_to_integer(sale_price_tag['value'])
        original_price = human_price_to_integer(original_price_tag['value'])
        if original_price == 0:
            original_price = sale_price
        return Product(original_price=original_price, sale_price=sale_price, link=link)


class XTMobileProductCrawler:

    # Regular
    # <div class="prod_dt_price"><span class="price" id="price" itemprop="price" content="5290000">5.290.000đ</span></div>

    # On sale
    # <div class="prod_dt_price"><span class="price" id="price" itemprop="price" content="5290000">5.290.000đ</span><span class="price_old">6.490.000đ</span></div>


    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting xtmobile product " + link)
        soup = BeautifulSoup(r.text, 'lxml')
        sale_price_tag = soup.find("span", {"itemprop": "price"})
        original_price_tag = soup.find("span", {"class": "price_old"})
        sale_price = human_price_to_integer(sale_price_tag['content'])
        original_price = sale_price
        if original_price_tag:
            original_price = human_price_to_integer(original_price_tag.text)
        return Product(original_price=original_price, sale_price=sale_price, link=link)


class SangMobileProductCrawler:

    # Regular
    # <span class="current-price ProductPrice">17,390,000₫</span>


    # On sale
    # <span class="original-price ComparePrice"><s>18,390,000₫</s></span>


    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting xtmobile product " + link)
        soup = BeautifulSoup(r.text, 'lxml')
        sale_price_tag = soup.find("span", {"class": "current-price ProductPrice"})
        original_price_tag = soup.find("span", {"class": "original-price ComparePrice"})
        sale_price, original_price = 0, 0
        if sale_price_tag:
            sale_price = self.convert_to_price(sale_price_tag.text)
        if original_price_tag:
            original_price = self.convert_to_price(original_price_tag.text)
        else:
            original_price = sale_price
        return Product(original_price=original_price, sale_price=sale_price, link=link)

    def convert_to_price(self, text):
        if text == "" or "Liên hệ" in text:
            return 0
        return human_price_to_integer(text)


class PhucKhangProductCrawler:

    # Regular
    # <span class="price-buy">28.250.000 ₫</span>


    # On sale
    # <span class="price-vmarket">31.990.000 ₫</span>


    async def get_price(self, link: str) -> Product:
        r = requests.get(link)
        if r.status_code not in (200, 201):
            raise Exception("error getting xtmobile product " + link)
        soup = BeautifulSoup(r.text, 'lxml')
        sale_price_tag = soup.find("span", {"class": "price-buy"})
        original_price_tag = soup.find("span", {"class": "price-vmarket"})
        sale_price, original_price = 0, 0
        if sale_price_tag:
            sale_price = self.convert_to_price(sale_price_tag.text)
        if original_price_tag:
            original_price = self.convert_to_price(original_price_tag.text)
        return Product(original_price=original_price, sale_price=sale_price, link=link)

    def convert_to_price(self, text):
        if text == "" or "Vui lòng gọi" in text:
            return 0
        return human_price_to_integer(text)


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
                "bachlongmobile.com": BachLongProductCrawler(),
                "didongviet.vn": DidongvietProductCrawler(),
                "minhtuanmobile.com": MinhTuanMobileProductCrawler(),
                "duchuymobile.com": DucHuyMobileProductCrawler(),
                "hnammobile.com": HNamMobileProductCrawler(),
                "xtmobile.vn": XTMobileProductCrawler(),
                "sangmobile.com": SangMobileProductCrawler(),
                "phuckhangmobile.com": PhucKhangProductCrawler(),
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
        if "bachlongmobile.com" in link:
            return self.CRAWLERS.get("bachlongmobile.com")
        if "didongviet.vn" in link:
            return self.CRAWLERS.get("didongviet.vn")
        if "minhtuanmobile.com" in link:
            return self.CRAWLERS.get("minhtuanmobile.com")
        if "duchuymobile.com" in link:
            return self.CRAWLERS.get("duchuymobile.com")
        if "hnammobile.com" in link:
            return self.CRAWLERS.get("hnammobile.com")
        if "xtmobile.vn" in link:
            return self.CRAWLERS.get("xtmobile.vn")
        if "sangmobile.com" in link:
            return self.CRAWLERS.get("sangmobile.com")
        if "phuckhangmobile.com" in link:
            return self.CRAWLERS.get("phuckhangmobile.com")
        raise Exception("not found suitable crawler for link {}".format(link))
