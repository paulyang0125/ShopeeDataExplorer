#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Paul Yang and Kana Kunikata
# Created Date: 24/05/2022
# version ='1.1'
# ---------------------------------------------------------------------------

"""This module provides the Shopee Data process functionality."""
# shopee_data_explorer/data_process.py



from typing import Any, Dict, List
import pandas as pd




class CrawlerDataProcesser:
    """data process"""

    def __init__(self, data_source:str) -> None:
        self.data_source = data_source
        self.product_items = []
        self.product_articles = []
        self.product_sku = []
        self.product_tags = []

    def process_product_data(self,product:Dict[str, Any]) -> None:
        """test"""
        if product:
            self.product_articles.append(product['description'])
            self.product_sku.append(product['models'])
            self.product_tags.append(product['hashtag_list'])
        else:
            self.product_articles.append('na')
            self.product_sku.append('na')
            self.product_tags.append('na')



    def clean_product_data(self):
        """test"""
        self.product_articles= []
        self.product_sku= []
        self.product_tags = []

    def write_shopee_goods_data(self,product_items_container:pd.DataFrame, my_keyword:str):
        """test"""
        product_items_container.to_csv(self.data_source + "_" + my_keyword +'_goods_data.csv',\
             encoding = 'utf-8-sig')

    def write_shopee_comments_data(self,product_comments_container:pd.DataFrame,my_keyword:str):
        """test"""
        product_comments_container.to_csv(self.data_source + "_" + my_keyword + \
            '_comments_data.csv', encoding = 'utf-8-sig')

    def process_comment_data(self,comment:List[Dict[str, Any]], product_comments_container:\
        pd.DataFrame) -> pd.DataFrame:
        """test"""
        user_comment = pd.DataFrame(comment) #covert comment to data frame
        if not user_comment.empty:
            models=[]
            for item in user_comment['product_items']:
                if pd.DataFrame(item).filter(regex = 'model_name').shape[1] != 0:
                    models.append(pd.DataFrame(item)['model_name'].tolist())
                else:
                    print('No model_name')
                    models.append(None)

            user_comment['product_items']= models # puts models aka SKUs in

        #todo: when do parallel in v1.3, this aggregation shouldn't work
        #so need a new way to aggreate later
        product_comments_container = pd.concat([product_comments_container, user_comment], \
            axis= 0)
        # debug
        #print("process_comment_data->comment_conatiner:head", product_comments_container.head(5))
        #print("process_comment_data->comment_conatiner:tail", product_comments_container.tail(5))

        return product_comments_container



    def aggregate_product_data(self, product_items_container: pd.DataFrame, product_items: \
        pd.DataFrame) -> pd.DataFrame:
        """it accumulate three items for a page and then aggregate"""
        product_items['articles'] = pd.Series(self.product_articles)
        product_items['SKU'] = pd.Series(self.product_sku)
        product_items['hashtag_list'] = pd.Series(self.product_tags)
        # debug
        #print("aggregate_product_data->product-item:head", product_items.head(5))
        #print("aggregate_product_data->product-item:tail", product_items.tail(5))
        product_items_container = pd.concat([product_items_container,product_items],\
            axis=0)
        # debug
        #print("aggregate_product_data->container:head", product_items_container.head(5))
        #print("aggregate_product_data->container:tail", product_items_container.tail(5))

        return product_items_container

    def process_raw_search_index(self,result:List[Dict[str, Any]]) -> pd.DataFrame:
        """test"""
        product_items = {}
        for count, _ in enumerate(result):
            product_items[count] = result[count]['item_basic']
        product_items=pd.DataFrame(product_items).T
        return product_items

        #product_items_container = pd.concat([product_items_container,product_items],axis=0)

