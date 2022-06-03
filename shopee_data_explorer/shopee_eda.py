#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Paul Yang and Kana Kunikata
# Created Date: 24/05/2022
# version ='1.1'
# ---------------------------------------------------------------------------

"""This module provides the Shopee EDA functionality."""
# shopee_data_explorer/shopee_eda.py

####### utilities #########

import ast
import random
import base64
from io import BytesIO
import os
from pathlib import Path
from typing import Any, List, NamedTuple
import pandas as pd
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import numpy as np

from adjustText import adjust_text
from shopee_data_explorer import SUCCESS

class EDAResponse(NamedTuple):
    """data model to controller"""
    result: List[str]
    error: int

class ShopeeEDA():
    """ test """
    ####### contant and Instance Variables ########

    def __init__(self,data_path:Path,charts:List[str], product_data:pd.DataFrame,\
        comments_data:pd.DataFrame,myfont:FontProperties,chart_color=None)->None:
        """thid class is doing EDA"""

        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        plt.rcParams['axes.unicode_minus'] = False
        if not chart_color:
            self.colors_group = ['#427f8f','#8B0000','#559db0','#8B0000','#0000FF','#FF6347',\
            '#006400','#4682B4','#4169E1','#D2691E']
            self.chart_color = self.rotate_color()
        else:
            self.chart_color = chart_color
        self.comments = comments_data
        self.contents = product_data
        self.myfont = myfont
        self.contents_final = pd.DataFrame()
        self.comments_final = pd.DataFrame()
        self.tag_data = pd.DataFrame()
        self.consumer_power = pd.DataFrame()
        self.charts = charts
        self.data_path = data_path

    def rotate_color(self) -> str:
        """ test """
        color_index = random.randint(0, len(self.colors_group) - 1)
        print("New color index: " + str(color_index))
        return self.colors_group[color_index]

    def clean_data(self) -> None:
        """ test """
        # divide price by 100000
        self.contents['price'] = self.contents['price'] / 100000

    def create_tags(self) -> None:
        """ test """
        tag_list = []
        for i in self.contents['articles']:
            if isinstance(i,str):
                tagg = i.split('#')
                tagg = tagg[1::]
                tagg = [g.replace(' ','') for g in tagg]
            else:
                tagg = []

            tag_list.append(tagg)

        self.contents['Tag'] = tag_list

    def evaluation(self,the_str:str) -> Any:
        """
        make string tranform to its orignal type
        such as '{'A':1}' --> {'A':1}
        """
        return ast.literal_eval(the_str)

    def process_rating(self) -> None:
        """把欄位的內容放入evaluation方法進行轉換"""
        self.contents['item_rating'] = self.contents['item_rating'].apply(self.evaluation)
        self.contents['rating_star'] = self.contents['item_rating']\
            .apply(lambda x:x['rating_star'])
        self.contents['rating_numbers'] = self.contents['item_rating']\
            .apply(lambda x:np.sum( \
        x['rating_count']))

    def create_preprocessed_dataframes(self):
        """ test """
        # put sku（商品規格）into content
        comment_sku = self.comments.drop_duplicates('itemid')
        self.contents = self.contents.merge(comment_sku[['itemid', 'product_items']], \
        how = 'left', on='itemid')
        # get out the key columns from contents
        self.contents_final = self.contents[['itemid','name','brand','Tag' ,'price', \
            'historical_sold',\
            'articles', 'shopid','rating_numbers','rating_star','liked_count']]
        # mege content的'itemid', 'price','name'to comment
        self.comments = self.comments.merge(self.contents[['itemid', 'price','name']], \
        how = 'left', on='itemid')
        # issue：remove duplicatied items
        # hint：drop_duplicates
        self.comments = self.comments.drop_duplicates()
        # get the key columns for comments_final
        self.comments_final = self.comments[['itemid',	'shopid',	'name',	'price',\
            'userid','ctime','orderid', 'rating_star', 'comment','product_items']]
        owd = os.getcwd()
        os.chdir(self.data_path)
        self.save_preprocessed_dataframes()
        os.chdir(owd)

    def save_preprocessed_dataframes(self):
        """ test """
        shopee_product_name = "shopee_processed_product_data.csv"
        shopee_comment_name = "shopee_processed_comment_data.csv"
        self.contents_final.to_csv(shopee_product_name,encoding = 'UTF-8-sig')
        self.comments_final.to_csv(shopee_comment_name,encoding= 'UTF-8-sig')


    def make_figures(self,charts:list) -> EDAResponse:
        """ test """
        errors = []
        candidates = [self.make_figure1, self.make_figure2, \
            self.make_figure3,self.make_figure4,self.make_figure5,self.make_figure6]
        for index, _ in enumerate(charts):
            if charts[index] in candidates[index].__name__:
                #try:
                if candidates[index]() != SUCCESS:
                    errors.append(candidates[index].__name__)
                #except:
                    #print(f"failed to run {candidates[index].__name__}")
                    #errors.append(candidates[index].__name__)
                    #return FIGURE_ERROR
        return EDAResponse(errors,SUCCESS)


    def prepare_figures_header(self):
        """ test """
        html = '<h1 style="font-size:60px; text-align:center;">Shopee EDA charts</h1>\n \
        <hr style="border-top: 8px solid #bbb; border-radius: 5px;">\n'
        with open('test.html','w',encoding="utf-8") as htm_file:
            htm_file.write(html)

    def make_pics_html(self, fig_object,num) -> int:
        """ test """
        owd = os.getcwd()
        os.chdir(self.data_path)
        tmpfile = BytesIO()
        fig_object.savefig(tmpfile, format='png')
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
        #html = '<img src=\'data:image/png;base64,{}\'>\n'.format(encoded)
        html = f'<img src=\'data:image/png;base64,{encoded}\'>\n'
        with open('test.html','a',encoding="utf-8") as htm_file:
            htm_file.write(html)
        fig_object.savefig(f'figure{str(num)}.png', bbox_inches='tight')
        os.chdir(owd)
        return SUCCESS

    def make_figure1(self):
        """ test """
        plt.figure( figsize = (10,6))
        plt.scatter(self.contents_final['price'],self.contents_final['historical_sold'],
            color=self.chart_color,alpha=0.5)
        plt.title("Analsys of product prices and sales", color='white',\
            fontsize=30,bbox=dict(boxstyle='square,pad=0', fc=self.chart_color, ec='none'))
        #plt.title("Analsys of product prices and sales",fontsize=30)
        plt.ylabel("Historical Sales",fontsize=20,)
        plt.xlabel("Price",fontsize=20,)
        plt.grid(True)
        plt.tight_layout()
        self.make_pics_html(plt,1)
        return SUCCESS


    def make_figure2(self):
        """ test """
        product_data_melt_zero = self.contents_final[self.contents_final['rating_star']>3]
        plt.figure( figsize = (10,6))
        plt.scatter(product_data_melt_zero['rating_star'],product_data_melt_zero['rating_numbers'],
            color=self.chart_color,
            alpha=0.5)
        plt.title("Comparison of rating products",fontsize=30,fontproperties=self.myfont,\
            color='white',bbox=dict(boxstyle='square,pad=0', fc=self.chart_color, ec='none'))
        plt.ylabel("Sum of Rating Items",fontsize=20,fontproperties=self.myfont)
        plt.xlabel("Star Rating",fontsize=20,fontproperties=self.myfont)
        plt.grid(True)
        plt.tight_layout()
        self.make_pics_html(plt,2)
        return SUCCESS

    def make_figure3(self):
        """ test """
        self.consumer_power = self.comments_final[['userid','price']].groupby('userid').sum()
        self.consumer_power = pd.concat([self.consumer_power,self.comments_final[['userid',\
            'price']].groupby('userid').mean()], axis=1)
        self.consumer_power.columns = ['total_amount_of_money_spent','avg_purchase_price']
        plt.figure( figsize = (10,6))
        plt.scatter(self.consumer_power['avg_purchase_price'],self.consumer_power\
            ['total_amount_of_money_spent'],
            color=self.chart_color,
            alpha=0.5)
        plt.title("Summary of Consumer Purchasing Power",fontsize=30,fontproperties=self.myfont\
            ,color='white',bbox=dict(boxstyle='square,pad=0', fc=self.chart_color, ec='none'))
        plt.xlabel("Average purchase price",fontsize=20,fontproperties=self.myfont)
        plt.ylabel("Total amount of money spent",fontsize=20,fontproperties=self.myfont)
        plt.grid(True)
        plt.tight_layout()
        self.make_pics_html(plt,3)
        return SUCCESS

    def make_figure4(self):
        """ test """
        consumer_power_interval = pd.DataFrame(self.consumer_power['avg_purchase_price']\
            .value_counts())
        consumer_power_interval.sort_index(inplace=True)
        consumer_power_interval.columns = ['total_amount_of_customer']
        plt.figure( figsize = (10,6))
        plt.scatter(consumer_power_interval.index,consumer_power_interval,color=self.chart_color)
        plt.title("Deep-dive of Consumer Purchasing Power",fontsize=30,\
            fontproperties=self.myfont,color='white',bbox=dict(boxstyle='square,pad=0',\
                 fc=self.chart_color, ec='none'))
        plt.xlabel("Average purchase price",fontsize=20,fontproperties=self.myfont)
        plt.ylabel("Total amount of customer",fontsize=20,fontproperties=self.myfont)
        plt.grid(True)
        plt.tight_layout()
        self.make_pics_html(plt,4)
        return SUCCESS

    def make_figure5(self):
        """ test """
        tags_list = []
        count_list = []
        like_list = []
        sale_list = []
        for tags,likes,his_sold in zip(self.contents_final['Tag'].tolist(), \
            self.contents_final['liked_count'].tolist()\
            ,self.contents_final['historical_sold'].tolist()):
            #print("i: " + str(type(i)))
            if not isinstance(tags, list):
                tags =  ast.literal_eval(tags)

            for tag in tags:
                # if not repeate, add the new tag to the four lists
                if tag not in tags_list and tag:
                    tags_list.append(tag)
                    count_list.append(1)
                    like_list.append(likes)
                    sale_list.append(his_sold)
                # if repeate, increase the numbers for that repeated tag in count_list、\
                # like_list、sale_list
                else:
                    if tag:
                        count_list[tags_list.index(tag)] = count_list[tags_list.index(tag)]+1
                        like_list[tags_list.index(tag)] = like_list[tags_list.index(tag)]+likes
                        sale_list[tags_list.index(tag)] = sale_list[tags_list.index(tag)]+his_sold

        dic = {
            'Tag': tags_list,
            'total_usage':count_list,
            'total_likes':like_list,
            'sales':sale_list
            }

        self.tag_data = pd.DataFrame(dic)
        self.tag_data =  self.tag_data.sort_values(by=['total_usage'], ascending = False)
        print(self.tag_data['Tag'][:10])
        plt.figure( figsize = (10,6))
        plt.bar(self.tag_data['Tag'][:10],  self.tag_data['total_usage'][:10],\
            color=self.chart_color)
        plt.title("Tag rankings",fontsize=30,fontproperties=self.myfont,color='white',\
            bbox=dict(boxstyle='square,pad=0', fc=self.chart_color, ec='none'))
        plt.xlabel("Tag Name",fontsize=20,fontproperties=self.myfont)
        plt.ylabel("Total Usage",fontsize=20,fontproperties=self.myfont)
        plt.xticks(fontsize=20,rotation=90)
        plt.tight_layout()
        self.make_pics_html(plt,5)
        return SUCCESS


    def make_figure6(self):
        """ test """
        plt.figure( figsize = (10,6))
        plt.scatter(self.tag_data['total_likes'],self.tag_data['sales'],color=self.chart_color)
        plt.title("Corelationship between tags and sales",fontsize=30,\
            fontproperties=self.myfont,color='white',bbox=dict(boxstyle='square,pad=0',\
                fc=self.chart_color, ec='none'))
        #txt_height = 0.0037*(plt.ylim()[1] - plt.ylim()[0])
        #txt_width = 0.018*(plt.xlim()[1] - plt.xlim()[0])
        tags = []
        likes = []
        sales = []
        for like,sale,tag in zip(self.tag_data['total_likes'],self.tag_data['sales'],\
            self.tag_data['Tag']):
            if like > self.tag_data['total_likes'].mean()+self.tag_data['total_likes'].std()*1 \
                and sale > self.tag_data['sales'].mean()+self.tag_data['sales'].std()*1:
                #plt.text(like, sale, tag, fontsize=12,) # annotate the tag name on the last day
                #if not like in likes or not sale in sales:
                tags.append(tag)
                likes.append(like)
                sales.append(sale)

        texts = []
        for x_pos, y_pos, text in zip(likes[:], sales[:], tags[:]):
            texts.append(plt.text(x_pos, y_pos, text))

        plt.xlabel("Like Counts",fontsize=20,)
        plt.ylabel("Total amount of sales",fontsize=20,)

        #text_positions = self.get_text_positions(tags, likes, sales, txt_width, txt_height)
        #self.text_plotter(tags, likes, sales, text_positions, txt_width, txt_height)
        #adjust_text(texts,arrowprops=dict(arrowstyle="->", color='r', lw=0.5))
        adjust_text(texts,only_move={'points':'y', 'texts':'y'},\
            arrowprops=dict(arrowstyle="->", color='r', lw=0.5))
        plt.grid(True)
        plt.tight_layout()
        self.make_pics_html(plt,6)
        return SUCCESS

    def do_eda(self) -> EDAResponse:
        """ test """
        # preprocessing
        print("1. start preprocessing!")
        self.clean_data()
        self.create_tags()
        self.process_rating()
        self.create_preprocessed_dataframes()
        # drawing
        print("2. start drawing!")
        #os.chdir(self.data_path)
        owd = os.getcwd()
        os.chdir(self.data_path)
        self.prepare_figures_header()
        os.chdir(owd)
        read = self.make_figures(self.charts)
        return read

"""     def get_text_positions(self,text, x_data, y_data, txt_width, txt_height):

        x_y = zip(y_data, x_data)
        text_positions = list(y_data)
        for index, (y, x) in enumerate(x_y):
            local_text_positions = [i for i in x_y if i[0] > (y - txt_height)
                                and (abs(i[1] - x) < txt_width * 2) and i != (y,x)]
            if local_text_positions:
                sorted_ltp = sorted(local_text_positions)
                if abs(sorted_ltp[0][0] - y) < txt_height: #True == collision
                    differ = np.diff(sorted_ltp, axis=0)
                    x_y[index] = (sorted_ltp[-1][0] + txt_height, x_y[index][1])
                    text_positions[index] = sorted_ltp[-1][0] + txt_height*1.01
                    for k, (j, m) in enumerate(differ):
                        #j is the vertical distance between words
                        if j > txt_height * 2: #if True then room to fit a word in
                            x_y[index] = (sorted_ltp[k][0] + txt_height, x_y[index][1])
                            text_positions[index] = sorted_ltp[k][0] + txt_height
                            break
        return text_positions

    def text_plotter(self,text, x_data, y_data, text_positions, txt_width,txt_height):

        for z,x,y,t in zip(text, x_data, y_data, text_positions):
            plt.annotate(str(z), xy=(x-txt_width/2, t), size=12)
            if y != t:
                plt.arrow(x, t,0,y-t, color='red',alpha=0.3, width=txt_width*0.1,
                    head_width=txt_width, head_length=txt_height*0.5,
                    zorder=0,length_includes_head=True) """
