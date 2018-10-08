import scrapy
import re
from scrapy_splash import SplashRequest

# splash lua script
script = """
        function main(splash, args)
            --local snapshots = {}
            local timer = splash:call_later(function()
                dis=500
                splash.scroll_position = {x=0, y=dis*1}
                splash:wait(1.0)
                splash.scroll_position = {x=0, y=dis*2}
                splash:wait(1.0)
                splash.scroll_position = {x=0, y=dis*3}
                splash:wait(1.0)
                splash.scroll_position = {x=0, y=dis*4}
                splash:wait(1.0)
            end, 0.1)
            splash:go("https://www.taiwan.net.tw/m1.aspx?sNo=0001016")
            splash:wait(4.2)
            return {
                html = splash:html(),
                --png = splash:png(),
                --har = splash:har(),
            }
        end
        """

BASE_URL = 'https://www.taiwan.net.tw'

class TPlaceItemBio(scrapy.Item):
    city_link = scrapy.Field() # 網頁連結
    tra_city = scrapy.Field() # 景點縣市
    city_bio = scrapy.Field() # 景點簡介
    city_img_urls = scrapy.Field()  
    city_img_local = scrapy.Field() # 本地文檔保存路徑
    tra_img_urls = scrapy.Field() # 圖片連接
    tra_img_local = scrapy.Field() # 本地文檔保存路徑

class TPlaceSpiderBio(scrapy.Spider):
    name = 'travel_city'
    allowed_domains = ['taiwan.net.tw']
    start_urls = [
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001016"
    ]

    #套用管線 #放在custom_settings中才能確保只有爬取各景點才使用
    '''For Scrapy v 1.0+, custom_settings can override the item pipelines in settings'''
    custom_settings = {
        'ITEM_PIPELINES' : {'scrapy_tra_data.pipelines.TravelImagesPipeline':1}
    }

    # 重新定義起始爬取點
    def start_requests(self):
        splash_args = {
            'wait': 5, # 透過SplashRequest请求等待1秒
            'lua_source': script
            # 'page': page
        }
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args=splash_args, endpoint='execute')
    
    def parse(self, response):
        grids = response.xpath('//*[@id="grid"]')
        if grids:
            print("success categories\n\n")
            for w in grids.xpath('li'):
                wdata = {}
                wdata['city_link'] = BASE_URL +"/"+ w.xpath('a/@href').extract_first()#.extract()[0] #取得網頁連結
                wdata['city_img_urls'] = [w.xpath('a/img/@src').extract_first()]#extract()[0] #取得縣市圖片
                wdata['tra_city'] = w.xpath('a/img/@alt').extract_first()#extract() #取得景點縣市

                #使用get_mini_bio方法來處理得主履歷頁面
                request = scrapy.Request(wdata['city_link'],
                                         callback=self.get_mini_bio,
                                         dont_filter=True)
                request.meta['item'] = TPlaceItemBio(**wdata)
                yield request

    #第二層爬蟲
    ''' 把任何可用照片URL加入image_urls串列，並且把到<p></p>停止點之前ra的傳記段落，通通放入項目的 city_bio 欄位 '''
    def get_mini_bio(self, response):
        ''' 取得景點簡介描述與照片 '''
        BASE_URL_ESCAPED = 'https:\/\/www.taiwan.net.tw'
        item = response.meta['item']
 
        # 這個XPath會取得id為 mw-content-text 的<div>所有段落，若段落為空(text() == False)，使用normalize-space(.)強迫段落內容成為空字串("."表段落節點)
        # 用意識讓任何空字串都能比對成功傳記區段的停止點表示
        city_bio = ""
        ps = response.xpath('//*[@id="c01"]/p').extract()
        for p in ps:
            #if p == '<p>&nbsp;</p>': #碰到空段落停止點時跳出 break
            city_bio += p #取得景點介紹
        item['city_bio'] = city_bio
        yield item