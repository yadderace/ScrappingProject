import scrapy
import webdriver_manager
from selenium import webdriver



class MainSpider(scrapy.Spider):
    name = "main"

    def __init__(self):
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=op)

    def start_requests(self):
        urls = [
            'https://www.olx.com.gt/items/q-apartamentos'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        
        self.driver.get(response.url)

        clicks = 0
        while True:
            try:
                next = self.driver.find_element_by_xpath('//*[@class="rui-3sH3b rui-3K5JC rui-1zK8h"]')
                next.click()
                clicks = clicks + 1
            except:
                    break

            print("Click #" + str(clicks))
        
        self.driver.close()