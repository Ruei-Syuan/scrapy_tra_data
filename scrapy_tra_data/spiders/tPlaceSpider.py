import scrapy
import re
from scrapy_splash import SplashRequest #重新定義請求

# splash lua script
# place's lua
scriptPlace = """
              function main(splash, args)
                --local snapshots = {}
                local timer = splash:call_later(function()
                    dis=550
                    for a=1, 12, 1 do
                        --tag = tostring(a)
                        splash.scroll_position = {x=0, y=dis*a}
                        splash:wait(1.0)
                        --snapshots[tag] = splash:png()
                    end
                end, 0.3)
                splash:go(args.url)
                splash:wait(20.0)
                return {
                    html = splash:html(),
                    --snapshots
                }
              end
              """
# place's bio lua
scriptPlaceBio = """
                 function main(splash, args)
                    local timer = splash:call_later(function()
                        dis=500
                        splash.scroll_position = {x=0, y=dis*1}
                        splash:wait(4.0)
                    end, 0.2)
                    splash:go(args.url)
                    splash:wait(8.0)
                    return {
                        html = splash:html()
                    }
                 end
                 """
        
BASE_URL = 'https://www.taiwan.net.tw'

class TPlaceItemBio(scrapy.Item):
    place_city = scrapy.Field() # 景點縣市
    place_type = scrapy.Field() # 景點分類
    tra_place = scrapy.Field() # 景點名稱
    place_link = scrapy.Field() # 景點連結
    place_bio = scrapy.Field() # 景點簡介
    place_img_urls = scrapy.Field()  # 景點團片url
    place_img_local = scrapy.Field() # 本地圖片檔保存路徑
    place_img_lon = scrapy.Field() # 景點經度
    place_img_lat = scrapy.Field() # 景點緯度
    place_img_address = scrapy.Field() # 景點地址

class TPlaceSpiderBio(scrapy.Spider):
    name = 'travel_place'
    allowed_domains = ['taiwan.net.tw']
    start_urls = [
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001090", #台北市
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001105", #基隆市
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001091", #新北市
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001106", #宜蘭縣
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001107", #桃園市
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001108", #新竹縣
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001109", #新竹市
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001110", #苗栗縣
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001112", #臺中市
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001113", #彰化縣
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001114", #南投縣
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001115", #雲林縣
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001116", #嘉義縣
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001117", #嘉義市
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001119", #臺南市
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001121", #高雄市
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001122", #屏東縣
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001123", #臺東縣
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001124", #花蓮縣
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001125", #澎湖縣
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001126", #金門縣
        "https://www.taiwan.net.tw/m1.aspx?sNo=0001127" #連江縣(馬祖)
    ]

    #套用管線 #放在custom_settings中才能確保只有爬取各景點才使用
    '''For Scrapy v 1.0+, custom_settings can override the item pipelines in settings'''
    custom_settings = {
        'ITEM_PIPELINES' : {'scrapy_selenium.pipelines.PlaceImagesPipeline':1}
    }

    # 重新定義起始爬取點
    def start_requests(self):
        splash_args = {
            'wait': 5, # 透過SplashRequest请求等待1秒
            'lua_source': scriptPlace
        }
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args=splash_args, endpoint='execute')

    def parse(self, response):
        city = response.xpath('//*[@id="c01"]/div[1]/h1/text()').extract()#'hotSpotsNationalPark\'
        CONST_CITY = ""
        if(len(city)!=0):
            CONST_CITY = city[0]

        grids = response.xpath('//*[@id="c01"]/h2/text()').extract() #'hotSpotsNationalPark\'
        i=0 
        if grids:
            print("success grids \n\n ")
            for place_type in grids:
                i+=1
                print("success place_type : ")
                if(i==1 or i==2): # 前兩個是標題
                    print("i = "+str(i))
                    continue
                j=i-1
                placediv = response.xpath('//*[@id="c01"]/div['+str(j)+"]/ul")#.extract()
                if placediv:
                    print("success placediv\n")
                    for w in placediv.xpath('li'):
                        wdata = {}
                        wdata['place_city'] = CONST_CITY
                        wdata['place_type'] = place_type
                        wdata['place_link'] = BASE_URL + "/" + w.xpath('a/@href').extract_first() #取得網頁連結
                        wdata['place_img_urls'] = [w.xpath('a/img/@src').extract_first()] #取得景點圖片
                        wdata['tra_place'] = w.xpath('a/img/@alt').extract_first() #取得景點名稱
                        
                        # 修正景點名稱
                        wdata['tra_place'] = wdata['tra_place'].replace('/', '-')
                                                
                        splash_args = {
                                        'wait': 5, # 透過SplashRequest请求等待5秒
                                        'lua_source': scriptPlaceBio
                                      }
                        # for url in self.start_urls:
                        yield SplashRequest(wdata['place_link'], self.parse, args=splash_args, endpoint='execute')
                        
                        #使用get_place_bio方法來處理，取得景點簡介描述與照片 
                        request = scrapy.Request(wdata['place_link'],
                                                callback=self.get_place_bio,
                                                dont_filter=True)
                        request.meta['item'] = TPlaceItemBio(**wdata)
                        yield request

    #第二層爬蟲
    ''' 把任何可用照片URL加入image_urls串列，並且把到<p></p>停止點之前ra的傳記段落，通通放入項目的 city_bio 欄位 '''
    def get_place_bio(self, response):
        ''' 取得景點簡介描述與照片 '''
        BASE_URL_ESCAPED = 'https:\/\/www.taiwan.net.tw'
        item = response.meta['item']
        
        place_bio = ""
        ps = response.xpath('//*[@id="fixPagination"]/article/div/div')
        if ps:
            for p in ps.xpath('p/text()'):
                #if p == '<p>&nbsp;</p>': #碰到空段落停止點時跳出 break
                place_bio += "  "
                place_bio += p.extract() #取得景點介紹
                place_bio += "</br>"
                
        place_img_locate = response.xpath('//*[@id="fixPagination"]/article/div/div/dl/dd[3]/text()').extract()
        
        if(len(place_img_locate)!=0):
            place_img_loc = place_img_locate[0].replace('/', ' ').split(' ')
            place_img_lon = place_img_loc[0] # 景點經度
            place_img_lat = place_img_loc[1] # 景點緯度
        else:
            place_img_lon = "" # 景點經度
            place_img_lat = "" # 景點緯度

        place_img_address = response.xpath('//*[@id="fixPagination"]/article/div/div/dl/dd[2]/text()').extract_first()

        item['place_bio'] = place_bio
        item['place_img_lon'] = place_img_lon
        item['place_img_lat'] = place_img_lat
        item['place_img_address'] = place_img_address
        yield item