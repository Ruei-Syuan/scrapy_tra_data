import scrapy
import re
from scrapy_splash import SplashRequest #重新定義請求

# splash lua script
# city's script
script = """
         function main(splash, args)
            --local snapshots = {}
            local timer = splash:call_later(function()
                dis=500
                for a=1, 5, 1 do
                    --tag = tostring(a)
                    splash.scroll_position = {x=0, y=dis*a}
                    splash:wait(2.0)
                    --snapshots[tag] = splash:png()
                end
            end, 0.1)
            splash:go(args.url)
            splash:wait(11.5)
            return {
                --snapshots,
                html = splash:html() 
            }
         end
         """

BASE_URL = 'https://www.taiwan.net.tw'

class TPlaceItemBio(scrapy.Item):
    city_link = scrapy.Field() # 網頁連結
    tra_city = scrapy.Field() # 景點縣市
    city_bio = scrapy.Field() # 縣市簡介
    city_img_urls = scrapy.Field()  
    city_img_local = scrapy.Field() # 本地文檔保存路徑

class TPlaceSpiderBio(scrapy.Spider):
    name = 'travel_city'
    allowed_domains = ['taiwan.net.tw']
    start_urls = [
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001016"
    ]

    #套用管線 #放在custom_settings中才能確保只有爬取各景點才使用
    '''For Scrapy v 1.0+, custom_settings can override the item pipelines in settings'''
    custom_settings = {
        'ITEM_PIPELINES' : {'scrapy_selenium.pipelines.TravelImagesPipeline':1}
    }

    # 重新定義起始爬取點
    def start_requests(self):
        splash_args = {
            'wait': 5, # 透過SplashRequest请求等待5秒
            'lua_source': script,
            'time-out': 3600
        }
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args=splash_args, endpoint='execute')
    
    def parse(self, response):
        citys = response.xpath('//*[@id="grid"]')
        if citys:
            print("success categories\n\n")
            for w in citys.xpath('li'):
                wdata = {}
                wdata['city_link'] = BASE_URL +"/"+ w.xpath('a/@href').extract_first() #取得網頁連結
                wdata['city_img_urls'] = [w.xpath('a/img/@src').extract_first()] #取得縣市圖片
                wdata['tra_city'] = w.xpath('a/img/@alt').extract_first() #取得景點縣市

                #使用get_city_bio方法來處理，取得景點城市簡介描述與照片
                request = scrapy.Request(wdata['city_link'],
                                         callback=self.get_city_bio,
                                         dont_filter=True)
                request.meta['item'] = TPlaceItemBio(**wdata)
                yield request

    #第二層爬蟲
    ''' 把<p></p>的簡介，通通放入項目的 city_bio 欄位 '''
    def get_city_bio(self, response):
        ''' 取得城市簡介描述與照片 '''
        BASE_URL_ESCAPED = 'https:\/\/www.taiwan.net.tw'
        item = response.meta['item']
        
        city_bio = ""
        ps = response.xpath('//*[@id="c01"]/p').extract()
        for p in ps:
            city_bio += p #取得景點介紹
        item['city_bio'] = city_bio
        yield item