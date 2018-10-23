# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
'''
class ScrapyTraDataPipeline(object):
    def process_item(self, item, spider):
        return item
'''

#=========================================================================================#
# 若要自己放一個管線進專案的蜘蛛中，需修改setting.py模組，註冊管線，加入管線字典中，並啟用
import scrapy,os
from scrapy.utils.project import get_project_settings

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

class TravelscrapyPipeline(object):
    def process_item(self, item, spider):
        return item

# For Scrapy v1.0+:
# from scrapy.pipelines.images import ImagesPipeline
class TravelImagesPipeline(ImagesPipeline):
    IMAGES_STORE = get_project_settings().get('IMAGES_STORE')

    def get_media_requests(self, item, info):
        # 獲取圖片的鏈接
        for image_url in item['city_img_urls']:
            # 向圖片的url地址發送請求獲取圖片
            yield scrapy.Request(image_url)
    
    # 發出圖片請求後，其結果會交由 item_compoleted 方法接手處理
    def item_completed(self, results, item, info):
        # 獲取文檔的名字 [這個 Python 串列生成式，會過濾結果元組串列，儲存檔案的路徑相對setting.py裡記載的IMAGE_STORE變數]
        image_paths = [x['path'] for ok, x in results if ok] # result（狀態，{"path":"","url":"https://***"}）
        # 沒有資料夾就自己建
        if image_paths:
            # 更改文檔的名字為景點名稱並放入該景點隸屬縣市folder
            os.rename(self.IMAGES_STORE + "/" + image_paths[0], self.IMAGES_STORE + "/" + item["tra_city"] + "/" + item["tra_city"] + ".jpg")
            # 將圖片儲存的路徑保存到item中，返回item
            item["city_img_local"] = self.IMAGES_STORE  + "/" + item["tra_city"]+ "/" + item["tra_city"] + ".jpg"#將提取到的path寫入到Item中　
        return item #將加工後的Item傳遞給下一個管道進行處理

# For Scrapy v1.0+:
# from scrapy.pipelines.images import ImagesPipeline
class PlaceImagesPipeline(ImagesPipeline):
    IMAGES_STORE = get_project_settings().get('IMAGES_STORE')

    def get_media_requests(self, item, info):
        # 獲取圖片的鏈接
        for image_url in item['place_img_urls']:
            # 向圖片的url地址發送請求獲取圖片
            yield scrapy.Request(image_url)
    
    # 發出圖片請求後，其結果會交由 item_compoleted 方法接手處理
    def item_completed(self, results, item, info):
        # 獲取文檔的名字 [這個 Python 串列生成式，會過濾結果元組串列，儲存檔案的路徑相對setting.py裡記載的IMAGE_STORE變數]
        image_paths = [x['path'] for ok, x in results if ok] # result（狀態，{"path":"","url":"https://***"}）
        # 沒有資料夾就自己建
        if image_paths:
            # 更改文檔的路徑為城市名稱/景點名稱.jpg
            os.rename(self.IMAGES_STORE + "/" + image_paths[0], self.IMAGES_STORE + "/" + item["place_city"] + "/"+ item["tra_place"] + ".jpg")
            # 將圖片儲存的路徑保存到item中，返回item
            item["place_img_local"] = self.IMAGES_STORE + "/" + item["place_city"] + "/"+ item["tra_place"] + ".jpg"#將提取到的path寫入到Item中　
        return item #將加工後的Item傳遞給下一個管道進行處理