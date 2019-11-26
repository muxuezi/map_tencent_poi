#!/usr/bin/env python
# coding: utf-8

# In[1]:
import time
from glob import glob
from tqdm import tqdm
import requests
import pandas as pd


# In[2]:
class Tmap(object):
    def __init__(self, name):
        self.name = name
        self.fname = f"{self.name}-{pd.datetime.today().date()}.xlsx"
        self.cities = ["北京", "天津", "南京", "上海", "常州", "杭州", "廊坊", "苏州", "无锡"]
        self.cols = ["城市", "名称", "联系电话", "地址", "经度", "纬度"]
        # 请替换成自己的apikey
        self.key = ""
        self.total_record = 0  # 定义全局变量，总行数
        self.base_url = f"http://apis.map.qq.com/ws/place/v1/search?page_size=20&filter=category=便利店&output=json&orderby=_distance&keyword={self.name}&key={self.key}"

    # 获取单页面数据
    def get_data(self, ct, p):
        time.sleep(0.5)
        rr = requests.get(f"{self.base_url}&boundary=region({ct},0)&page_index={p}").json()
        if self.total_record == 0:
            self.total_record = int(rr["count"])
        return rr["data"]

    # 获取所有城市数据
    def get_all(self):
        data = []
        for ct in tqdm(self.cities):
            time.sleep(1)
            jdata = self.get_data(ct, 1)
            if (self.total_record % 20) != 0:
                page_number = int(self.total_record / 20) + 2
            else:
                page_number = int(self.total_record / 20) + 1
            data.append(jdata)
            for each_page in range(2, page_number):
                jdata = self.get_data(ct, each_page)
                if jdata:
                    data.append(jdata)
        df = pd.concat([pd.DataFrame.from_records(_) for _ in data], sort=False)
        df["经度"] = df.location.apply(lambda _: _["lng"])
        df["纬度"] = df.location.apply(lambda _: _["lat"])
        df["城市"] = df.ad_info.apply(lambda _: _["city"])
        df = (
            df[df.title.str.contains(self.name)]
            .drop_duplicates(subset=["title"])
            .sort_values(by="tel")
            .rename(columns={"title": "名称", "address": "地址", "tel": "联系电话"})[self.cols]
        )
        df.to_excel(self.fname, index=False)
        print(f"输出文件：{self.fname}")
        return df


# In[3]:
if __name__ == "__main__":
    df = Tmap("家乐福").get_all()
