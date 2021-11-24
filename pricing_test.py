from pricing import *
from datetime import datetime
import asyncio

def test():
    test_coroutines_wrapper()
    #test_antien()
    #test_hoangha()
    #test_linhanh()
    #test_viettablet()
    #test_ctmobile()
    #test_haloshop()
    #test_cellphones()
    #test_sangmobile()


def test_antien():
    link1 = 'https://antien.vn/tai-nghe/tai-nghe-apple-airpods-2-chinh-hang-vna-case-sac-thuong-mv7n2vna.html?gclid=Cj0KCQjwuL_8BRCXARIsAGiC51AgZri9aiG_9Rp3bTk0hKFtXv4XjNS0w_kwIYe3x85h3Vcbq_NfCgIaAvwAEALw_wcB&regid=12260648591603298072'
    link2 = 'https://antien.vn/dong-ho-chinh-hang/dong-ho-dinh-vi-wonlex-kt16.html'
    dtgk_crawler = AntienProductCrawler()
    print(dtgk_crawler.get_price(link1))
    print(dtgk_crawler.get_price(link2))


def test_coroutines_wrapper():
    #asyncio.run(test_minhtuan())
    #asyncio.run(test_ducthuy())
    #asyncio.run(test_hnam())
    #asyncio.run(test_xtmobile())
    #asyncio.run(test_baochau())
    asyncio.run(test_sangmobile())
    #asyncio.run(test_phuckhang())


async def test_coroutines(*tasks):
    starting_time = datetime.now().timestamp()
    done = await asyncio.gather(tasks)
    for done_task in done:
        print(done_task)

    ending_time = datetime.now().timestamp()
    time_diff = ending_time - starting_time
    print(f"take {time_diff} s")


async def test_hoangha():
    link1 = 'https://hoanghamobile.com/bo-phat-wifi-di-dong-kasda-kw9550-wireless-4g-chinh-hang-p13624.html'
    link2 = 'https://hoanghamobile.com/apple-iphone-12-128gb-chinh-hang-vna-p19301.html'
    crawler = HoangHaProductCrawler()
    task_queue = []
    task_queue.append(asyncio.create_task(crawler.get_price(link1)))
    task_queue.append(asyncio.create_task(crawler.get_price(link2)))

    done = await asyncio.gather(*task_queue)
    for done_task in done:
        print(done_task)


async def test_linhanh():
    link1 = 'https://dientulinhanh.com/jbl-pulse-4'
    link2 = 'https://dientulinhanh.com/loa-bluetooth-lg-xboomgo-pl5'
    crawler = LinhAnhProductCrawler()
    print(crawler.get_price(link1))
    print(crawler.get_price(link2))


async def test_baochau():
    link1 = 'https://baochauelec.com/loa-bluetooth-jbl-charge-4'
    link2 = 'https://baochauelec.com/loa-bluetooth-jbl-xtreme-2?gclid=Cj0KCQjwreT8BRDTARIsAJLI0KId8-a5F_LBBF107g_prpF5RirT5g51oAId00O7dC5kfLMFTl-CmsgaAsrKEALw_wcB'
    crawler = BaoChauProductCrawler()
    task_queue = []
    task_queue.append(asyncio.create_task(crawler.get_price(link1)))
    task_queue.append(asyncio.create_task(crawler.get_price(link2)))
    done = await asyncio.gather(*task_queue)
    for done_task in done:
        print(done_task)


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

async def test_bachlong():
    link1 = 'https://bachlongmobile.com/ipad-pro-11-inch-2020-1tb-wifi-chinh-hang.html'
    link2 = 'https://bachlongmobile.com/iphone-7-plus-32gb-moi-99.html'

    crawler = BachLongProductCrawler()
    task_queue = []
    task_queue.append(asyncio.create_task(crawler.get_price(link1)))
    task_queue.append(asyncio.create_task(crawler.get_price(link2)))
    done = await asyncio.gather(*task_queue)
    for done_task in done:
        print(done_task)


async def test_didongviet():
    link1 = 'https://didongviet.vn/samsung-galaxy-note-20-ultra-ban-256gb'
    link2 = 'https://didongviet.vn/ipad-air-2020-256gb'
    link3 = 'https://didongviet.vn/ipad-10-2inch-2020-32gb-wifi'

    crawler = DidongvietProductCrawler()
    task_queue = []
    task_queue.append(asyncio.create_task(crawler.get_price(link1)))
    task_queue.append(asyncio.create_task(crawler.get_price(link2)))
    task_queue.append(asyncio.create_task(crawler.get_price(link3)))
    done = await asyncio.gather(*task_queue)
    for done_task in done:
        print(done_task)


async def test_minhtuan():
    link1 = 'https://minhtuanmobile.com/ipad-pro-11-2020-128gb-wifi-likenew'
    link2 = 'https://minhtuanmobile.com/iphone-12-pro-max-128gb-chinh-hang'
    link3 = 'https://minhtuanmobile.com/macbook-pro-13-m1-late-2020-256gb-myd82-myda2-new-seal'

    crawler = MinhTuanMobileProductCrawler()
    task_queue = []
    task_queue.append(asyncio.create_task(crawler.get_price(link1)))
    task_queue.append(asyncio.create_task(crawler.get_price(link2)))
    task_queue.append(asyncio.create_task(crawler.get_price(link3)))
    done = await asyncio.gather(*task_queue)
    for done_task in done:
        print(done_task)


async def test_ducthuy():
    link1 = 'https://www.duchuymobile.com/samsung-galaxy-note-10'
    link2 = 'https://www.duchuymobile.com/iphone-12-pro-128gb-cu'
    link3 = 'https://www.duchuymobile.com/apple-watch-se-44mm-gps'

    crawler = DucHuyMobileProductCrawler()
    task_queue = []
    task_queue.append(asyncio.create_task(crawler.get_price(link1)))
    task_queue.append(asyncio.create_task(crawler.get_price(link2)))
    task_queue.append(asyncio.create_task(crawler.get_price(link3)))
    done = await asyncio.gather(*task_queue)
    for done_task in done:
        print(done_task)


async def test_hnam():
    link1 = 'https://www.hnammobile.com/dien-thoai/samsung-galaxy-s20-fe-g780.20730.html'
    link2 = 'https://www.hnammobile.com/dong-ho-thong-minh/apple-watch-se-40mm-gps-silver-aluminium-case-with-white-sport-band-mydm2.20275.html'
    link3 = 'https://www.hnammobile.com/kho-may-cu/may-tinh-bang/samsung-galaxy-tab-a8-8-t295-2019-99.19955.html'

    crawler = HNamMobileProductCrawler()
    task_queue = []
    task_queue.append(asyncio.create_task(crawler.get_price(link1)))
    task_queue.append(asyncio.create_task(crawler.get_price(link2)))
    task_queue.append(asyncio.create_task(crawler.get_price(link3)))
    done = await asyncio.gather(*task_queue)
    for done_task in done:
        print(done_task)


async def test_xtmobile():
    link1 = 'https://www.xtmobile.vn/iphone-11-pro-max-64-gb-ban-likenew'
    link2 = 'https://www.xtmobile.vn/loa-bluetooth-jbl-clip-3'
    link3 = 'https://www.xtmobile.vn/pin-du-phong-polymer-umetravel-trip10c-10000mah'

    crawler = XTMobileProductCrawler()
    task_queue = []
    task_queue.append(asyncio.create_task(crawler.get_price(link1)))
    task_queue.append(asyncio.create_task(crawler.get_price(link2)))
    task_queue.append(asyncio.create_task(crawler.get_price(link3)))
    done = await asyncio.gather(*task_queue)
    for done_task in done:
        print(done_task)


async def test_sangmobile():
    link1 = 'https://www.sangmobile.com/products/iphone-11-pro-max-64gb-99'
    link2 = 'https://www.sangmobile.com/collections/dong-ho/products/apple-watch-edition-series-5-lte-44mm-titanium-sport-loop'
    link3 = 'https://www.sangmobile.com/collections/dien-thoai-moi/products/samsung-galaxy-note-9-cong-ty'
    crawler = SangMobileProductCrawler()
    task_queue = []
    task_queue.append(asyncio.create_task(crawler.get_price(link1)))
    task_queue.append(asyncio.create_task(crawler.get_price(link2)))
    task_queue.append(asyncio.create_task(crawler.get_price(link3)))
    done = await asyncio.gather(*task_queue)
    for done_task in done:
        print(done_task)


async def test_phuckhang():
    link1 = 'https://phuckhangmobile.com/iphone-13-pro-128gb-chinh-hang-moi-100-vn-a-5723.html'
    link2 = 'https://phuckhangmobile.com/apple-macbook-pro-13-2020-m1-16gb-512gb-cu-99-5484.html'
    link3 = 'https://phuckhangmobile.com/airpods-pro-likenew-99-4937.html'
    crawler = PhucKhangProductCrawler()
    task_queue = []
    task_queue.append(asyncio.create_task(crawler.get_price(link1)))
    task_queue.append(asyncio.create_task(crawler.get_price(link2)))
    task_queue.append(asyncio.create_task(crawler.get_price(link3)))
    done = await asyncio.gather(*task_queue)
    for done_task in done:
        print(done_task)


if __name__ == '__main__':
    test()
