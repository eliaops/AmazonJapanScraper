#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon Japan 卖家信息提取工具 - 简化高性能版本
Amazon Japan Seller Information Extractor - Simplified High-Performance Version
"""

import sys
import os
import time
import random
import requests
from datetime import datetime
from urllib.parse import urljoin, quote
import pandas as pd
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from queue import Queue, Empty
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SimplifiedAmazonScraper:
    """简化的Amazon爬虫类 - 专注于关键词搜索"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.amazon.co.jp"
        
        # 配置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        self.session.headers.update(self.headers)
        
        # 配置连接池和重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            pool_connections=5,
            pool_maxsize=10,
            max_retries=retry_strategy
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 性能配置
        self.max_concurrent_requests = 3  # 降低并发数，提高稳定性
        self.request_delay_range = (1.0, 2.0)  # 适中的延迟
        self.batch_size = 20  # 分批处理大小
        
    def search_products(self, keyword, max_pages=20, max_products=1000, progress_callback=None, stop_flag=None):
        """
        简化的产品搜索方法
        
        Args:
            keyword: 搜索关键词
            max_pages: 最大页数
            max_products: 最大产品数
            progress_callback: 进度回调函数
            stop_flag: 停止标志函数
        
        Returns:
            list: 产品信息列表
        """
        products = []
        page = 1
        
        try:
            while page <= max_pages and len(products) < max_products:
                if stop_flag and not stop_flag():
                    break
                
                # 构建搜索URL
                search_params = {
                    'k': keyword,
                    'page': page,
                    'ref': 'sr_pg_' + str(page)
                }
                
                search_url = f"{self.base_url}/s"
                
                if progress_callback:
                    progress_callback(f"正在搜索第 {page} 页...")
                
                try:
                    response = self.session.get(search_url, params=search_params, timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 查找产品元素
                    product_selectors = [
                        'div[data-component-type="s-search-result"]',
                        '.s-result-item[data-component-type="s-search-result"]',
                        '.s-search-result'
                    ]
                    
                    product_items = []
                    for selector in product_selectors:
                        product_items = soup.select(selector)
                        if product_items:
                            break
                    
                    if not product_items:
                        print(f"第 {page} 页未找到产品，可能已到最后一页")
                        break
                    
                    page_products = 0
                    for item in product_items:
                        if len(products) >= max_products:
                            break
                            
                        product_info = self._extract_product_info(item)
                        if product_info:
                            products.append(product_info)
                            page_products += 1
                    
                    if progress_callback:
                        progress_callback(f"第 {page} 页找到 {page_products} 个产品，总计 {len(products)} 个")
                    
                    if page_products == 0:
                        print("连续页面无产品，停止搜索")
                        break
                    
                    page += 1
                    
                    # 随机延迟
                    delay = random.uniform(*self.request_delay_range)
                    time.sleep(delay)
                    
                except requests.RequestException as e:
                    print(f"搜索第 {page} 页时出错: {e}")
                    page += 1
                    continue
                    
        except Exception as e:
            print(f"搜索过程出错: {e}")
        
        return products
    
    def _extract_product_info(self, product_element):
        """从产品元素中提取基本信息"""
        try:
            if not product_element:
                return None
            
            # 产品链接
            link_element = (product_element.select_one('h2 a') or
                          product_element.select_one('.a-link-normal') or
                          product_element.select_one('a[href*="/dp/"]'))
            
            if not link_element:
                return None
            
            product_url = urljoin(self.base_url, link_element.get('href', ''))
            if not product_url or '/dp/' not in product_url:
                return None
            
            # 产品标题
            title_element = (link_element.select_one('span') or
                           product_element.select_one('.a-size-mini span') or
                           product_element.select_one('.a-size-base-plus'))
            
            title = title_element.get_text(strip=True) if title_element else "未知产品"
            
            # 价格信息
            price_element = (product_element.select_one('.a-price-whole') or
                           product_element.select_one('.a-price .a-offscreen') or
                           product_element.select_one('.a-price-range'))
            
            price = price_element.get_text(strip=True) if price_element else "价格未知"
            
            return {
                'title': title[:100],  # 限制标题长度
                'price': price,
                'url': product_url
            }
            
        except Exception as e:
            print(f"提取产品信息时出错: {e}")
            return None
    
    def get_seller_info_batch(self, products, progress_callback=None, stop_flag=None):
        """
        批量获取卖家信息 - 分批处理避免内存问题
        
        Args:
            products: 产品列表
            progress_callback: 进度回调函数
            stop_flag: 停止标志函数
        
        Returns:
            list: 包含卖家信息的结果列表
        """
        results = []
        total_products = len(products)
        completed = 0
        
        # 分批处理
        for batch_start in range(0, total_products, self.batch_size):
            if stop_flag and not stop_flag():
                break
            
            batch_end = min(batch_start + self.batch_size, total_products)
            batch_products = products[batch_start:batch_end]
            
            if progress_callback:
                progress_callback(f"处理批次 {batch_start//self.batch_size + 1}/{(total_products-1)//self.batch_size + 1}")
            
            # 并发处理当前批次
            batch_results = self._process_batch(batch_products, progress_callback, stop_flag, completed, total_products)
            results.extend(batch_results)
            completed += len(batch_products)
            
            # 强制垃圾回收
            gc.collect()
            
            # 批次间延迟
            time.sleep(1)
        
        return results
    
    def _process_batch(self, batch_products, progress_callback, stop_flag, base_completed, total_products):
        """处理单个批次的产品"""
        batch_results = []
        
        def fetch_single_seller(product, index):
            try:
                if stop_flag and not stop_flag():
                    return None
                
                # 随机延迟
                time.sleep(random.uniform(*self.request_delay_range))
                
                seller_info = self._get_seller_info(product['url'])
                
                result = {
                    'product_title': product['title'],
                    'price': product['price'],
                    'product_url': product['url'],
                    'seller_name': seller_info.get('seller_name', '未知') if seller_info else '未知',
                    'business_name': seller_info.get('business_name', '') if seller_info else '',
                    'store_name': seller_info.get('store_name', '') if seller_info else '',
                    'phone': seller_info.get('phone', '') if seller_info else '',
                    'address': seller_info.get('address', '') if seller_info else '',
                    'representative': seller_info.get('representative', '') if seller_info else '',
                    'seller_url': seller_info.get('seller_url', '') if seller_info else ''
                }
                
                # 更新进度
                current_completed = base_completed + index + 1
                if progress_callback:
                    progress_callback(f"已处理 {current_completed}/{total_products} 个产品")
                
                return result
                
            except Exception as e:
                print(f"处理产品失败 {product.get('title', 'Unknown')}: {e}")
                return {
                    'product_title': product.get('title', '未知'),
                    'price': product.get('price', ''),
                    'product_url': product.get('url', ''),
                    'seller_name': '获取失败',
                    'business_name': '', 'store_name': '', 'phone': '', 'address': '', 'representative': '', 'seller_url': ''
                }
        
        # 使用较小的线程池处理批次
        with ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
            future_to_product = {
                executor.submit(fetch_single_seller, product, i): product 
                for i, product in enumerate(batch_products)
            }
            
            for future in as_completed(future_to_product):
                try:
                    if stop_flag and not stop_flag():
                        break
                    
                    result = future.result()
                    if result:
                        batch_results.append(result)
                        
                except Exception as e:
                    print(f"批次处理异常: {e}")
        
        return batch_results
    
    def _get_seller_info(self, product_url):
        """获取单个产品的卖家信息"""
        try:
            response = self.session.get(product_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找卖家信息
            seller_info = {}
            
            # 卖家名称和链接
            seller_element = (soup.find('a', {'id': 'sellerProfileTriggerId'}) or
                            soup.find('a', string=re.compile(r'.*販売.*')) or
                            soup.select_one('#merchant-info a'))
            
            if seller_element:
                seller_info['seller_name'] = seller_element.get_text(strip=True)
                seller_url = seller_element.get('href', '')
                if seller_url:
                    seller_info['seller_url'] = urljoin(self.base_url, seller_url)
                    
                    # 获取详细卖家信息
                    detailed_info = self._get_detailed_seller_info(seller_info['seller_url'])
                    if detailed_info:
                        seller_info.update(detailed_info)
            
            return seller_info if seller_info else None
            
        except Exception as e:
            print(f"获取卖家信息失败 {product_url}: {e}")
            return None
    
    def _get_detailed_seller_info(self, seller_url):
        """获取详细卖家信息 - 增强版本"""
        try:
            response = self.session.get(seller_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 方法1: 基于关键词和上下文的智能提取
            smart_info = self._smart_extract_seller_info(soup)
            
            # 方法2: 基于HTML结构提取
            structured_info = self._extract_from_html_structure(soup)
            
            # 方法3: 传统正则表达式提取（作为后备）
            regex_info = self._extract_with_regex(soup.get_text())
            
            # 合并结果，优先级：智能提取 > 结构提取 > 正则提取
            final_info = {}
            fields = ['business_name', 'phone', 'address', 'representative', 'store_name']
            
            for field in fields:
                final_info[field] = (
                    smart_info.get(field) or 
                    structured_info.get(field) or 
                    regex_info.get(field) or 
                    ''
                )
            
            # 清理和验证结果
            final_info = self._clean_seller_info(final_info)
            
            return final_info
            
        except Exception as e:
            print(f"获取详细卖家信息失败: {e}")
            return {}
    
    def _smart_extract_seller_info(self, soup):
        """基于关键词关联的智能提取"""
        info = {}
        
        # 关键词映射表 - 基于Amazon实际页面
        field_keywords = {
            'business_name': [
                'Business Name', 'business name', '会社名', '商号', '企业名称', 
                'Company Name', 'company name', '公司名称'
            ],
            'phone': [
                '咨询用电话号码', '电话号码', '電話番号', 'TEL', 'Tel',
                'Phone', 'phone', 'Telephone', '联系电话', '咨询电话'
            ],
            'address': [
                '地址', '住所', '所在地', 'Address', 'address',
                '联系地址', '公司地址', '营业地址'
            ],
            'representative': [
                '购物代表的姓名', '代表者', '代表取締役', '責任者',
                'Representative', 'representative', '联系人', '负责人', '代表人'
            ],
            'store_name': [
                '商店名', '店舗名', 'ショップ名', 'Store Name', 'store name',
                'Shop Name', 'shop name', '店铺名称'
            ]
        }
        
        # 查找包含卖家信息的区域
        seller_sections = soup.find_all(['div', 'section', 'table'], 
                                       string=re.compile(r'详尽的卖家信息|详民的卖家信息|seller.*info', re.I))
        
        if not seller_sections:
            # 扩大搜索范围
            seller_sections = soup.find_all(['div', 'section', 'table'])
        
        for section in seller_sections[:5]:  # 限制搜索范围
            section_text = section.get_text() if section else ""
            
            for field, keywords in field_keywords.items():
                if info.get(field):  # 已经找到该字段
                    continue
                
                for keyword in keywords:
                    # 在文本中查找关键词
                    if keyword.lower() in section_text.lower():
                        value = self._extract_value_near_keyword(section_text, keyword, field)
                        if value and self._validate_extracted_value(field, value):
                            info[field] = value
                            break
                
                if info.get(field):
                    break
        
        return info
    
    def _extract_from_html_structure(self, soup):
        """基于HTML结构提取"""
        info = {}
        
        # 查找表格结构
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key_text = cells[0].get_text().strip()
                    value_text = cells[1].get_text().strip()
                    
                    # 匹配字段
                    if not info.get('business_name') and any(k in key_text.lower() for k in ['business', '会社', '商号']):
                        info['business_name'] = value_text
                    elif not info.get('phone') and any(k in key_text.lower() for k in ['电话', 'tel', 'phone']):
                        info['phone'] = value_text
                    elif not info.get('address') and any(k in key_text.lower() for k in ['地址', '住所', 'address']):
                        info['address'] = value_text
                    elif not info.get('representative') and any(k in key_text.lower() for k in ['代表', 'representative']):
                        info['representative'] = value_text
                    elif not info.get('store_name') and any(k in key_text.lower() for k in ['店', 'store', 'shop']):
                        info['store_name'] = value_text
        
        return info
    
    def _extract_with_regex(self, text):
        """传统正则表达式提取（后备方法）"""
        info = {}
        
        # 增强的正则模式
        patterns = {
            'business_name': [
                r'Business\s*Name[：:\s]*([^\n\r]{3,50})',
                r'会社名[：:\s]*([^\n\r]{3,50})',
                r'商号[：:\s]*([^\n\r]{3,50})',
                r'([A-Za-z\s]{3,30}(?:株式会社|有限会社|Company|Ltd|Corporation|Inc))',
            ],
            'phone': [
                r'咨询用电话号码[：:\s]*(\+?[\d\-\(\)\s]{8,20})',
                r'電話番号[：:\s]*(\+?[\d\-\(\)\s]{8,20})',
                r'TEL[：:\s]*(\+?[\d\-\(\)\s]{8,20})',
                r'(\+?\d{1,3}[-\s]?\d{10,11})',
                r'(\d{2,4}[-\s]\d{4}[-\s]\d{4})',
            ],
            'address': [
                r'地址[：:\s]*([^\n\r]{10,100})',
                r'住所[：:\s]*([^\n\r]{10,100})',
                r'Address[：:\s]*([^\n\r]{10,100})',
                r'(〒\d{3}-\d{4}[^\n\r]{5,80})',
            ],
            'representative': [
                r'购物代表的姓名[：:\s]*([^\n\r]{2,30})',
                r'代表者[：:\s]*([^\n\r]{2,30})',
                r'代表取締役[：:\s]*([^\n\r]{2,30})',
                r'Representative[：:\s]*([^\n\r]{2,30})',
            ],
            'store_name': [
                r'商店名[：:\s]*([^\n\r]{2,30})',
                r'店舗名[：:\s]*([^\n\r]{2,30})',
                r'Store\s*Name[：:\s]*([^\n\r]{2,30})',
                r'ショップ名[：:\s]*([^\n\r]{2,30})',
            ]
        }
        
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if self._validate_extracted_value(field, value):
                        info[field] = value
                        break
            
        return info
    
    def _extract_value_near_keyword(self, text, keyword, field):
        """提取关键词附近的值"""
        try:
            # 找到关键词位置
            keyword_pos = text.lower().find(keyword.lower())
            if keyword_pos == -1:
                return None
            
            # 提取关键词后的文本
            after_keyword = text[keyword_pos + len(keyword):].strip()
            
            # 移除开头的分隔符
            after_keyword = re.sub(r'^[：:\s\-]+', '', after_keyword)
            
            if field == 'phone':
                # 电话号码特殊处理
                phone_patterns = [
                    r'\+?\d{1,3}[-\s]?\d{10,11}',
                    r'\+?\d{11,13}',
                    r'\d{2,4}[-\s]\d{4}[-\s]\d{4}',
                ]
                for pattern in phone_patterns:
                    match = re.search(pattern, after_keyword)
                    if match:
                        return match.group(0)
            elif field == 'address':
                # 地址通常是多行的
                lines = after_keyword.split('\n')[:3]  # 取前3行
                address_parts = []
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 3:
                        address_parts.append(line)
                        if len(' '.join(address_parts)) > 15:  # 地址足够长
                            break
                return ' '.join(address_parts) if address_parts else None
            else:
                # 其他字段取第一行
                first_line = after_keyword.split('\n')[0].strip()
                # 移除可能的后续字段标识
                first_line = re.split(r'[：:]', first_line)[0].strip()
                return first_line if len(first_line) > 1 else None
            
        except Exception:
            return None
    
    def _validate_extracted_value(self, field, value):
        """验证提取的值是否合理"""
        if not value or len(value.strip()) < 2:
            return False
        
        value = value.strip()
        
        if field == 'phone':
            # 电话号码必须包含足够的数字
            digit_count = len(re.findall(r'\d', value))
            return digit_count >= 8 and digit_count <= 15
        elif field == 'address':
            # 地址必须有一定长度且包含有意义字符
            return len(value) >= 8 and bool(re.search(r'[\u4e00-\u9fff]|[a-zA-Z]', value))
        elif field == 'business_name':
            # 公司名不能太短或太长
            return 3 <= len(value) <= 80
        elif field == 'representative':
            # 代表人姓名长度合理
            return 2 <= len(value) <= 40
        elif field == 'store_name':
            # 店铺名长度合理
            return 2 <= len(value) <= 40
        
        return True
    
    def _clean_seller_info(self, info):
        """清理卖家信息"""
        cleaned = {}
        
        for field, value in info.items():
            if not value:
                cleaned[field] = ''
                continue
            
            # 基本清理
            value = str(value).strip()
            value = re.sub(r'\s+', ' ', value)  # 合并空格
            value = re.sub(r'^[：:\-\s]+', '', value)  # 移除开头分隔符
            value = re.sub(r'[：:\-\s]+$', '', value)  # 移除结尾分隔符
            
            # 字段特定清理
            if field == 'phone':
                # 保留数字、加号、减号、括号、空格
                value = re.sub(r'[^\d\+\-\(\)\s]', '', value)
                value = re.sub(r'\s+', '', value)  # 移除空格使格式统一
            elif field == 'address':
                # 地址清理换行和多余空格
                value = re.sub(r'\n+', ' ', value)
                value = re.sub(r'\s{2,}', ' ', value)
            
            # 限制长度
            if field == 'address':
                cleaned[field] = value[:150]
            else:
                cleaned[field] = value[:100]
        
        return cleaned


class SimplifiedScraperGUI:
    """简化的GUI界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Amazon Japan 卖家信息提取工具 v3.0 - 简化高性能版")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # 初始化爬虫
        self.scraper = SimplifiedAmazonScraper()
        
        # 状态变量
        self.is_scraping = False
        self.scraping_thread = None
        self.results = []
        
        # 创建界面
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🛒 Amazon Japan 卖家信息提取工具", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 搜索配置框架
        config_frame = ttk.LabelFrame(main_frame, text="搜索配置", padding="10")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # 关键词输入
        ttk.Label(config_frame, text="搜索关键词:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.keyword_var = tk.StringVar(value="电脑")
        keyword_entry = ttk.Entry(config_frame, textvariable=self.keyword_var, width=30)
        keyword_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 参数设置
        params_frame = ttk.Frame(config_frame)
        params_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(params_frame, text="最大页数:").grid(row=0, column=0, sticky=tk.W)
        self.pages_var = tk.StringVar(value="20")
        pages_spinbox = ttk.Spinbox(params_frame, from_=1, to=100, textvariable=self.pages_var, width=10)
        pages_spinbox.grid(row=0, column=1, padx=(5, 20))
        
        ttk.Label(params_frame, text="最大产品数:").grid(row=0, column=2, sticky=tk.W)
        self.max_products_var = tk.StringVar(value="1000")
        products_spinbox = ttk.Spinbox(params_frame, from_=50, to=10000, increment=50, 
                                     textvariable=self.max_products_var, width=10)
        products_spinbox.grid(row=0, column=3, padx=(5, 20))
        
        ttk.Label(params_frame, text="并发数:").grid(row=0, column=4, sticky=tk.W)
        self.concurrent_var = tk.StringVar(value="3")
        concurrent_spinbox = ttk.Spinbox(params_frame, from_=1, to=5, textvariable=self.concurrent_var, width=10)
        concurrent_spinbox.grid(row=0, column=5, padx=(5, 0))
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="🚀 开始搜索", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ 停止", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.export_button = ttk.Button(button_frame, text="📊 导出数据", command=self.export_data, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ 清空", command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 进度和状态
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 结果表格
        results_frame = ttk.LabelFrame(main_frame, text="提取结果", padding="5")
        results_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # 创建表格
        columns = ('产品名称', '价格', '卖家名称', '商家名称', '店铺名称', '电话', '地址', '代表人')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题和宽度
        column_widths = [200, 80, 100, 120, 100, 100, 150, 80]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, minwidth=50)
        
        # 滚动条
        scrollbar_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def start_scraping(self):
        """开始爬取"""
        if self.is_scraping:
            return
        
        keyword = self.keyword_var.get().strip()
        if not keyword:
            messagebox.showerror("错误", "请输入搜索关键词")
            return
        
        try:
            pages = int(self.pages_var.get())
            max_products = int(self.max_products_var.get())
            concurrent = int(self.concurrent_var.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数值")
            return
        
        # 更新爬虫配置
        self.scraper.max_concurrent_requests = concurrent
        
        # 清空结果
        self.clear_results()
        
        # 更新UI状态
        self.is_scraping = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.DISABLED)
        self.progress_bar.start()
        
        # 启动爬虫线程
        self.scraping_thread = threading.Thread(
            target=self.scraping_worker,
            args=(keyword, pages, max_products)
        )
        self.scraping_thread.daemon = True
        self.scraping_thread.start()
    
    def stop_scraping(self):
        """停止爬取"""
        self.is_scraping = False
        self.update_status("正在停止...")
    
    def scraping_worker(self, keyword, pages, max_products):
        """爬虫工作线程"""
        try:
            # 搜索产品
            self.update_status(f"正在搜索关键词: {keyword}")
            
            def search_progress(message):
                self.update_status(message)
            
            def stop_flag():
                return self.is_scraping
            
            products = self.scraper.search_products(
                keyword, pages, max_products, 
                progress_callback=search_progress,
                stop_flag=stop_flag
            )
            
            if not products:
                self.update_status("未找到任何产品")
                self.scraping_finished(0, 0)
                return
            
            self.update_status(f"找到 {len(products)} 个产品，开始提取卖家信息...")
            
            # 提取卖家信息
            def seller_progress(message):
                self.update_status(message)
            
            results = self.scraper.get_seller_info_batch(
                products,
                progress_callback=seller_progress,
                stop_flag=stop_flag
            )
            
            # 更新UI
            successful_extractions = 0
            for result in results:
                if not self.is_scraping:
                    break
                self.root.after(0, self.add_result_to_tree, result)
                if result.get('seller_name', '未知') not in ['未知', '获取失败']:
                    successful_extractions += 1
            
            self.results = results
            self.root.after(0, self.scraping_finished, len(results), successful_extractions)
            
        except Exception as e:
            self.root.after(0, self.scraping_error, str(e))
    
    def add_result_to_tree(self, result):
        """添加结果到表格"""
        self.tree.insert('', tk.END, values=(
            result['product_title'][:50] + '...' if len(result['product_title']) > 50 else result['product_title'],
            result['price'],
            result['seller_name'],
            result['business_name'],
            result['store_name'],
            result['phone'],
            result['address'][:30] + '...' if len(result['address']) > 30 else result['address'],
            result['representative']
        ))
    
    def scraping_finished(self, total_results, successful_extractions):
        """爬取完成"""
        self.is_scraping = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.NORMAL if total_results > 0 else tk.DISABLED)
        self.progress_bar.stop()
        
        self.update_status(f"完成！共提取 {total_results} 个产品，成功获取 {successful_extractions} 个卖家信息")
    
    def scraping_error(self, error_message):
        """爬取出错"""
        self.is_scraping = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar.stop()
        
        self.update_status(f"出错: {error_message}")
        messagebox.showerror("错误", f"爬取过程中出现错误:\n{error_message}")
    
    def update_status(self, message):
        """更新状态"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def clear_results(self):
        """清空结果"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.results = []
        self.update_status("就绪")
    
    def export_data(self):
        """导出数据"""
        if not self.results:
            messagebox.showwarning("警告", "没有数据可导出")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("CSV文件", "*.csv")],
            title="保存数据"
        )
        
        if file_path:
            try:
                df = pd.DataFrame(self.results)
                
                if file_path.endswith('.xlsx'):
                    df.to_excel(file_path, index=False)
                else:
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                
                messagebox.showinfo("成功", f"数据已导出到: {file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {e}")


def main():
    """主函数"""
    root = tk.Tk()
    app = SimplifiedScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
