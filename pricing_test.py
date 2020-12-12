from pricing import *

def test():
    #test_antien()
    #test_hoangha()
    #test_linhanh()
    #test_viettablet()
    #test_ctmobile()
    #test_haloshop()
    test_cellphones()


def test_antien():
    link1 = 'https://antien.vn/tai-nghe/tai-nghe-apple-airpods-2-chinh-hang-vna-case-sac-thuong-mv7n2vna.html?gclid=Cj0KCQjwuL_8BRCXARIsAGiC51AgZri9aiG_9Rp3bTk0hKFtXv4XjNS0w_kwIYe3x85h3Vcbq_NfCgIaAvwAEALw_wcB&regid=12260648591603298072'
    link2 = 'https://antien.vn/dong-ho-chinh-hang/dong-ho-dinh-vi-wonlex-kt16.html'
    dtgk_crawler = AntienProductCrawler()
    print(dtgk_crawler.get_price(link1))
    print(dtgk_crawler.get_price(link2))


def test_hoangha():
    link1 = 'https://hoanghamobile.com/bo-phat-wifi-di-dong-kasda-kw9550-wireless-4g-chinh-hang-p13624.html'
    link2 = 'https://hoanghamobile.com/apple-iphone-12-128gb-chinh-hang-vna-p19301.html'
    crawler = HoangHaProductCrawler()
    print(crawler.get_price(link1))
    print(crawler.get_price(link2))


def test_linhanh():
    link1 = 'https://dientulinhanh.com/jbl-pulse-4'
    link2 = 'https://dientulinhanh.com/loa-bluetooth-lg-xboomgo-pl5'
    crawler = LinhAnhProductCrawler()
    print(crawler.get_price(link1))
    print(crawler.get_price(link2))


def test_viettablet():
    link1 = 'https://www.viettablet.com/iphone-11-pro-64gb-chua-active-tbh'
    link2 = 'https://www.viettablet.com/apple-watch-1-cu-like-new-99'
    crawler = ViettabletProductCrawler()
    print(crawler.get_price(link1))
    print(crawler.get_price(link2))


def test_ctmobile():
    link1 = 'https://ctmobile.vn/iphone-se2-128gb-new'
    link2 = 'https://ctmobile.vn/watch-series-5-lte-44mm---99?gclid=CjwKCAiAv4n9BRA9EiwA30WND8R9wQI9FQmzC19G9LnCW5LhOIbXzw4zPqC1jcM8rsZ2geIWO884WRoCLB4QAvD_BwE'
    crawler = CTMobileProductCrawler()
    print(crawler.get_price(link1))
    print(crawler.get_price(link2))


def test_haloshop():
    link1 = 'https://watch.haloshop.vn/apple-watch-series-6-list/apple-watch-s6-44mm-gps-blue-aluminum-case-with-deep-navy-sport-band'
    link2 = 'https://haloshop.vn/iphone-12-pro/iphone-12-pro-gold-128gb'
    crawler = HaloshopProductCrawler()
    print(crawler.get_price(link1))
    print(crawler.get_price(link2))


def test_cellphones():
    link1 = 'https://cellphones.com.vn/loa-bluetooth-jbl-go-2.html'
    link2 = 'https://cellphones.com.vn/xiaomi-redmi-note-9-pro.html'
    link3 = 'https://cellphones.com.vn/he-thong-wifi-mesh-cho-toan-ngoi-nha-ac1200-deco-m4.html'
    crawler = CellphoneProductCrawler()
    print(crawler.get_price(link1))
    print(crawler.get_price(link2))
    print(crawler.get_price(link3))

