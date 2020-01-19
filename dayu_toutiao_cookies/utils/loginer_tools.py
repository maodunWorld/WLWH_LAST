# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     login_tools
   Description :
   Author :       maodun
   date：          2019-06-11
-------------------------------------------------
   Change Activity:
                   2019-06-11:
-------------------------------------------------
"""
__author__ = 'maodun'
import random
from selenium import webdriver
CHROME_OPTION_toutiao =  webdriver.ChromeOptions()
CHROME_OPTION_toutiao.add_experimental_option('excludeSwitches', ['enable-automation'])


def action_list(num):
    list_len = 6
    factor = num // list_len
    action_list = [factor for _ in range(list_len)]
    for index, action in enumerate(action_list[:list_len // 2]):
        rand = random.randrange(factor - 10, factor)
        action_list[index] = action_list[index] - rand
        action_list[-(index + 1)] = action_list[-(index + 1)] + rand
        factor -= 10
    return action_list

if __name__ == '__main__':
    d = action_list(101)
    print(d)