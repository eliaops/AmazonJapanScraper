#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon Japan 卖家信息提取工具 - 终极版 v4.0
Ultimate Amazon Japan Seller Information Extractor v4.0

新功能：
- 扩大关键词搜索范围，支持更多小商品
- 无限制连续搜索，想搜多久搜多久
- 实时保存功能，一边搜索一边保存
- 进一步优化的卖家信息提取算法
- 支持后台运行，可以离开桌面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
import threading
import os
from datetime import datetime
from urllib.parse import urljoin, quote
import json
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class UltimateAmazonScraper:
    """终极版Amazon日本站爬虫"""
    
    def __init__(self):
        self.base_url = "https://www.amazon.co.jp"
        self.session = requests.Session()
        
        # 智能User-Agent池 - 模拟不同浏览器和设备
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        # 智能请求头配置
        self.base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        }
        
        # 会话状态管理
        self.session_initialized = False
        self.last_request_time = 0
        self.request_count = 0
        self.current_user_agent_index = 0
        
        # 配置连接池和重试策略 - 优化503处理
        retry_strategy = Retry(
            total=2,  # 减少重试次数
            backoff_factor=2,  # 增加退避时间
            status_forcelist=[429, 500, 502, 504],  # 移除503，直接失败而不重试
        )
        adapter = HTTPAdapter(
            pool_connections=20,
            pool_maxsize=50,
            max_retries=retry_strategy
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 性能配置 - 智能化设置
        self.max_concurrent_requests = 1  # 单线程避免检测
        self.request_delay_range = (3.0, 8.0)  # 更人性化的延迟
        self.batch_size = 3  # 更小的批处理大小
        
        # 智能反检测配置
        self.max_requests_per_session = 20  # 每个会话最大请求数
        self.session_cooldown_time = 30  # 会话冷却时间(秒)
        self.user_agent_rotation_interval = 5  # User-Agent轮换间隔
        
        # 搜索优化配置
        self.search_strategies = [
            'default',      # 默认搜索
            'category',     # 分类搜索
            'brand',        # 品牌搜索
            'price_range',  # 价格区间搜索
        ]
        
        # 扩展的搜索参数
        self.search_params_variants = [
            {},  # 默认
            {'sort': 'price-asc-rank'},  # 价格低到高
            {'sort': 'price-desc-rank'}, # 价格高到低
            {'sort': 'review-rank'},     # 评价排序
            {'sort': 'date-desc-rank'},  # 最新商品
        ]
        
        # 实时保存配置
        self.auto_save_interval = 50  # 每50个产品自动保存一次
        self.save_directory = "amazon_data"
        self.ensure_save_directory()
        
        # 搜索状态
        self.is_searching = False
        self.total_products_found = 0
        self.total_sellers_extracted = 0
        self.current_save_file = None
        
    def ensure_save_directory(self):
        """确保保存目录存在"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def _initialize_session(self):
        """智能会话初始化 - 模拟真实用户行为"""
        if self.session_initialized:
            return True
            
        try:
            print("🔄 初始化智能会话...")
            
            # 1. 设置当前User-Agent
            current_ua = self.user_agents[self.current_user_agent_index]
            headers = self.base_headers.copy()
            headers['User-Agent'] = current_ua
            self.session.headers.update(headers)
            
            # 2. 先访问Amazon首页建立会话
            print("   📱 访问Amazon首页...")
            response = self.session.get(self.base_url, timeout=15)
            
            if response.status_code != 200:
                print(f"   ❌ 首页访问失败: {response.status_code}")
                return False
                
            # 3. 模拟用户浏览行为 - 访问几个常见页面
            common_pages = [
                '/gp/bestsellers',  # 畅销商品
                '/gp/new-releases', # 新品发布
            ]
            
            for page in common_pages:
                time.sleep(random.uniform(2, 4))  # 人性化延迟
                try:
                    self.session.get(f"{self.base_url}{page}", timeout=10)
                    print(f"   ✅ 访问页面: {page}")
                except:
                    pass  # 忽略错误，继续
            
            # 4. 等待一段时间模拟真实用户
            wait_time = random.uniform(3, 6)
            print(f"   ⏱️ 等待 {wait_time:.1f}秒...")
            time.sleep(wait_time)
            
            self.session_initialized = True
            self.request_count = 0
            print("   ✅ 会话初始化完成")
            return True
            
        except Exception as e:
            print(f"   ❌ 会话初始化失败: {e}")
            return False
    
    def _smart_request(self, url, params=None, **kwargs):
        """智能请求方法 - 包含反检测机制"""
        
        # 检查是否需要初始化会话
        if not self.session_initialized:
            if not self._initialize_session():
                raise Exception("会话初始化失败")
        
        # 检查是否需要轮换User-Agent
        if self.request_count > 0 and self.request_count % self.user_agent_rotation_interval == 0:
            self.current_user_agent_index = (self.current_user_agent_index + 1) % len(self.user_agents)
            new_ua = self.user_agents[self.current_user_agent_index]
            self.session.headers.update({'User-Agent': new_ua})
            print(f"🔄 轮换User-Agent: {new_ua[:50]}...")
        
        # 检查是否需要重置会话
        if self.request_count >= self.max_requests_per_session:
            print(f"🔄 达到最大请求数({self.max_requests_per_session})，重置会话...")
            self._reset_session()
            if not self._initialize_session():
                raise Exception("会话重置失败")
        
        # 智能延迟 - 基于上次请求时间
        current_time = time.time()
        if self.last_request_time > 0:
            elapsed = current_time - self.last_request_time
            min_delay = self.request_delay_range[0]
            if elapsed < min_delay:
                additional_delay = min_delay - elapsed + random.uniform(0, 2)
                print(f"⏱️ 智能延迟: {additional_delay:.1f}秒")
                time.sleep(additional_delay)
        
        # 执行请求
        try:
            # 添加随机化的请求头
            headers = kwargs.get('headers', {})
            if 'Referer' not in headers and self.request_count > 0:
                headers['Referer'] = self.base_url
            kwargs['headers'] = headers
            
            response = self.session.get(url, params=params, **kwargs)
            
            # 特殊处理503错误
            if response.status_code == 503:
                print("⚠️ 遇到503错误，启动智能恢复...")
                self._handle_503_error()
                # 重试一次
                time.sleep(random.uniform(10, 20))
                response = self.session.get(url, params=params, **kwargs)
            
            self.last_request_time = time.time()
            self.request_count += 1
            
            return response
            
        except Exception as e:
            print(f"❌ 智能请求失败: {e}")
            raise
    
    def _reset_session(self):
        """重置会话"""
        self.session.close()
        self.session = requests.Session()
        
        # 重新配置适配器
        retry_strategy = Retry(
            total=2,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 504],
        )
        adapter = HTTPAdapter(
            pool_connections=20,
            pool_maxsize=50,
            max_retries=retry_strategy
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session_initialized = False
        self.request_count = 0
        print("🔄 会话已重置")
    
    def _handle_503_error(self):
        """处理503错误的智能策略"""
        print("🛡️ 启动503错误处理策略...")
        
        # 1. 轮换User-Agent
        self.current_user_agent_index = (self.current_user_agent_index + 1) % len(self.user_agents)
        new_ua = self.user_agents[self.current_user_agent_index]
        self.session.headers.update({'User-Agent': new_ua})
        print(f"   🔄 轮换User-Agent")
        
        # 2. 清除可能的追踪cookie
        self.session.cookies.clear()
        print("   🍪 清除cookies")
        
        # 3. 等待冷却时间
        cooldown = random.uniform(self.session_cooldown_time, self.session_cooldown_time * 1.5)
        print(f"   ❄️ 冷却等待: {cooldown:.1f}秒")
        time.sleep(cooldown)
        
        # 4. 重置会话状态
        self.session_initialized = False
        print("   ✅ 503错误处理完成")
    
    def unlimited_search(self, keyword, progress_callback=None, stop_flag=None, save_callback=None):
        """
        无限制搜索功能 - 核心改进
        
        Args:
            keyword: 搜索关键词
            progress_callback: 进度回调
            stop_flag: 停止标志
            save_callback: 保存回调
        """
        self.is_searching = True
        self.total_products_found = 0
        self.total_sellers_extracted = 0
        
        # 创建保存文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_save_file = os.path.join(
            self.save_directory, 
            f"amazon_search_{keyword}_{timestamp}.xlsx"
        )
        
        all_products = []
        all_sellers = []
        page = 1
        consecutive_empty_pages = 0
        max_consecutive_empty = 5  # 连续5页无结果则停止
        
        try:
            while self.is_searching:
                # 检查停止条件：stop_flag()返回True表示继续搜索，False表示停止
                if stop_flag and not stop_flag():
                    self.is_searching = False  # 重要：设置状态为False以退出while循环
                    break
                
                if progress_callback:
                    progress_callback(f"🔍 搜索第 {page} 页 | 已找到 {self.total_products_found} 个产品 | 已提取 {self.total_sellers_extracted} 个卖家")
                
                # 使用多种搜索策略
                page_products = []
                for strategy_idx, search_params in enumerate(self.search_params_variants):
                    if stop_flag and not stop_flag():
                        break
                    
                    products = self._search_page_with_strategy(
                        keyword, page, search_params, strategy_idx
                    )
                    
                    if products:
                        page_products.extend(products)
                        consecutive_empty_pages = 0
                    
                    # 避免过于频繁的请求
                    time.sleep(random.uniform(0.5, 1.0))
                
                # 去重处理
                unique_products = self._deduplicate_products(page_products, all_products)
                
                if not unique_products:
                    consecutive_empty_pages += 1
                    if consecutive_empty_pages >= max_consecutive_empty:
                        if progress_callback:
                            progress_callback(f"⚠️ 连续 {max_consecutive_empty} 页无新产品，搜索可能已完成")
                        self.is_searching = False  # 设置状态为False以退出while循环
                        break
                else:
                    all_products.extend(unique_products)
                    self.total_products_found = len(all_products)
                    
                    # 批量提取卖家信息
                    if unique_products:
                        sellers = self._extract_sellers_batch(
                            unique_products, progress_callback, stop_flag
                        )
                        all_sellers.extend(sellers)
                        self.total_sellers_extracted = len(all_sellers)
                
                # 实时保存
                if len(all_products) % self.auto_save_interval == 0 and all_products:
                    self._save_data_realtime(all_products, all_sellers, save_callback)
                
                page += 1
                
                # 页面间延迟
                delay = random.uniform(*self.request_delay_range)
                time.sleep(delay)
                
                # 内存管理
                if page % 20 == 0:
                    gc.collect()
        
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ 搜索过程中出错: {e}")
        
        finally:
            # 最终保存
            if all_products:
                self._save_data_final(all_products, all_sellers, save_callback)
            
            self.is_searching = False
            
            if progress_callback:
                progress_callback(f"✅ 搜索完成！总计找到 {self.total_products_found} 个产品，提取 {self.total_sellers_extracted} 个卖家信息")
        
        return all_products, all_sellers
    
    def _search_page_with_strategy(self, keyword, page, search_params, strategy_idx):
        """使用特定策略搜索页面"""
        try:
            # 构建搜索URL和参数
            base_params = {
                'k': keyword,
                'page': page,
                'ref': f'sr_pg_{page}'
            }
            base_params.update(search_params)
            
            # 添加随机化参数以获得更多结果
            if strategy_idx > 0:
                base_params['qid'] = str(int(time.time()))
            
            search_url = f"{self.base_url}/s"
            
            # 使用智能请求方法
            response = self._smart_request(search_url, params=base_params, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 扩展的产品选择器 - 支持更多商品类型
            product_selectors = [
                'div[data-component-type="s-search-result"]',
                '.s-result-item[data-component-type="s-search-result"]',
                '.s-search-result',
                '.sg-col-inner .s-widget-container',
                '[data-asin]:not([data-asin=""])',
                '.s-card-container',
                '.AdHolder',  # 广告商品
                '.s-sponsored-list-item',  # 赞助商品
            ]
            
            products = []
            for selector in product_selectors:
                items = soup.select(selector)
                for item in items:
                    product_info = self._extract_product_info_enhanced(item)
                    if product_info:
                        products.append(product_info)
            
            return products
            
        except Exception as e:
            print(f"搜索策略 {strategy_idx} 第 {page} 页失败: {e}")
            return []
    
    def _extract_product_info_enhanced(self, product_element):
        """增强的产品信息提取"""
        try:
            if not product_element:
                return None
            
            # 获取ASIN（Amazon标准识别号）
            asin = product_element.get('data-asin', '')
            
            # 多种链接提取策略
            link_selectors = [
                'h2 a',
                '.a-link-normal',
                'a[href*="/dp/"]',
                'a[href*="/gp/product/"]',
                '.s-link-style a',
                '.a-size-mini a',
                '.a-size-base-plus a'
            ]
            
            link_element = None
            for selector in link_selectors:
                link_element = product_element.select_one(selector)
                if link_element:
                    break
            
            if not link_element:
                return None
            
            product_url = urljoin(self.base_url, link_element.get('href', ''))
            # 修复：接受更多类型的产品链接，包括赞助商品链接
            if not product_url or not any(pattern in product_url for pattern in ['/dp/', '/gp/product/', '/sspa/click', '/gp/slredirect/']):
                return None
            
            # 多种标题提取策略
            title_selectors = [
                'h2 a span',
                '.a-size-mini span',
                '.a-size-base-plus',
                '.s-size-mini',
                'h2 span',
                '.a-link-normal span'
            ]
            
            title = "未知产品"
            for selector in title_selectors:
                title_element = product_element.select_one(selector)
                if title_element:
                    title = title_element.get_text(strip=True)
                    if title and len(title) > 5:  # 确保标题有意义
                        break
            
            # 多种价格提取策略
            price_selectors = [
                '.a-price .a-offscreen',
                '.a-price-whole',
                '.a-price-range .a-offscreen',
                '.a-price-symbol + .a-price-whole',
                '.s-price-instructions-style .a-price .a-offscreen',
                '.a-price-range',
                'span[data-a-color="price"]'
            ]
            
            price = "价格未知"
            for selector in price_selectors:
                price_element = product_element.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    if price_text and any(char.isdigit() for char in price_text):
                        price = price_text
                        break
            
            # 提取评分和评价数
            rating_element = product_element.select_one('.a-icon-alt')
            rating = rating_element.get_text(strip=True) if rating_element else ""
            
            review_count_element = product_element.select_one('.a-size-base')
            review_count = review_count_element.get_text(strip=True) if review_count_element else ""
            
            # 提取图片URL
            img_element = product_element.select_one('img')
            image_url = img_element.get('src', '') if img_element else ""
            
            return {
                'asin': asin,
                'title': title[:150],  # 增加标题长度限制
                'price': price,
                'rating': rating,
                'review_count': review_count,
                'image_url': image_url,
                'url': product_url,
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"提取产品信息失败: {e}")
            return None
    
    def _deduplicate_products(self, new_products, existing_products):
        """去重处理"""
        existing_urls = {p['url'] for p in existing_products}
        existing_asins = {p.get('asin', '') for p in existing_products if p.get('asin')}
        
        unique_products = []
        for product in new_products:
            if (product['url'] not in existing_urls and 
                product.get('asin', '') not in existing_asins):
                unique_products.append(product)
        
        return unique_products
    
    def _extract_sellers_batch(self, products, progress_callback=None, stop_flag=None):
        """批量提取卖家信息"""
        sellers = []
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
            # 提交任务
            future_to_product = {
                executor.submit(self._get_seller_info_ultimate, product['url']): product 
                for product in products
            }
            
            # 处理结果
            for future in as_completed(future_to_product):
                if stop_flag and not stop_flag():
                    break
                
                product = future_to_product[future]
                try:
                    seller_info = future.result(timeout=30)
                    if seller_info:
                        seller_info.update({
                            'product_title': product['title'],
                            'product_url': product['url'],
                            'product_asin': product.get('asin', ''),
                            'extracted_at': datetime.now().isoformat()
                        })
                        sellers.append(seller_info)
                        
                        if progress_callback:
                            progress_callback(f"✅ 已提取卖家: {seller_info.get('seller_name', '未知')} | 总计: {len(sellers)}")
                
                except Exception as e:
                    if progress_callback:
                        progress_callback(f"⚠️ 提取卖家信息失败: {product['title'][:30]}... - {e}")
                
                # 批次间延迟
                time.sleep(random.uniform(0.3, 0.8))
        
        return sellers
    
    def _get_seller_info_ultimate(self, product_url):
        """终极版卖家信息提取"""
        try:
            # 跳过赞助商品链接，避免重定向导致的挂起问题
            if '/sspa/click' in product_url or '/gp/slredirect/' in product_url:
                return {
                    'seller_name': '赞助商品',
                    'seller_url': '',
                    'business_name': '',
                    'phone': '',
                    'address': '',
                    'representative_name': '',
                    'store_name': '',
                    'email': '',
                    'fax': ''
                }
            
            # 第一步：获取产品页面 - 使用智能请求
            response = self._smart_request(product_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找卖家信息的多种策略
            seller_info = {}
            
            # 策略1：查找"出售方"信息 - 增强版
            seller_selectors = [
                '#merchant-info',
                '#merchantInfoFeature_feature_div',
                '#tabular-buybox',
                '#buybox',
                '.a-section.a-spacing-small:contains("出售方")',
                '.a-section:contains("販売")',
                '.a-section:contains("Sold by")',
                '.a-section:contains("销售")',
                '#tabular-buybox .a-section',
                '#buybox-see-all-buying-choices',
                '.a-box-group .a-box',
                'span:contains("出售方")',
                'span:contains("販売")',
                'span:contains("Sold by")'
            ]
            
            seller_name = None
            seller_url = None
            
            for selector in seller_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text()
                    if any(keyword in text for keyword in ['出售方', '販売', 'Sold by', '销售']):
                        # 查找卖家链接
                        seller_link = element.select_one('a[href*="/sp?"]')
                        if seller_link:
                            seller_name = seller_link.get_text(strip=True)
                            seller_url = urljoin(self.base_url, seller_link.get('href'))
                            break
                
                if seller_name and seller_url:
                    break
            
            # 策略2：如果没找到，尝试其他方法
            if not seller_name:
                # 查找buybox中的卖家信息
                buybox_selectors = [
                    '#buybox .a-section a[href*="/sp?"]',
                    '.a-box-group a[href*="/sp?"]',
                    '#merchant-info a'
                ]
                
                for selector in buybox_selectors:
                    seller_link = soup.select_one(selector)
                    if seller_link:
                        seller_name = seller_link.get_text(strip=True)
                        seller_url = urljoin(self.base_url, seller_link.get('href'))
                        break
            
            # 如果找到卖家链接，获取详细信息
            if seller_url:
                detailed_info = self._get_detailed_seller_info_ultimate(seller_url)
                seller_info.update(detailed_info)
            
            # 基本信息
            seller_info.update({
                'seller_name': seller_name or '未知卖家',
                'seller_url': seller_url or '',
            })
            
            return seller_info
            
        except Exception as e:
            print(f"获取卖家信息失败 {product_url}: {e}")
            return None
    
    def _get_detailed_seller_info_ultimate(self, seller_url):
        """终极版详细卖家信息提取"""
        try:
            response = self._smart_request(seller_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 四层提取策略
            info = {}
            
            # 第一层：智能关键词提取
            smart_info = self._smart_extract_seller_info_ultimate(soup)
            
            # 第二层：HTML结构提取
            structured_info = self._extract_from_html_structure_ultimate(soup)
            
            # 第三层：正则表达式提取
            regex_info = self._extract_with_regex_ultimate(soup.get_text())
            
            # 第四层：深度文本分析
            deep_info = self._deep_text_analysis(soup.get_text())
            
            # 合并结果，优先级：智能 > 结构 > 正则 > 深度分析
            fields = ['business_name', 'phone', 'address', 'representative', 'store_name', 'email', 'fax']
            
            for field in fields:
                info[field] = (
                    smart_info.get(field) or 
                    structured_info.get(field) or 
                    regex_info.get(field) or 
                    deep_info.get(field) or 
                    ''
                )
            
            # 清理和验证
            info = self._clean_seller_info_ultimate(info)
            
            return info
            
        except Exception as e:
            print(f"获取详细卖家信息失败: {e}")
            return {}
    
    def _smart_extract_seller_info_ultimate(self, soup):
        """终极版智能关键词提取"""
        info = {}
        
        # 扩展的关键词映射
        field_keywords = {
            'business_name': [
                'Business Name', 'business name', 'BUSINESS NAME',
                '会社名', '商号', '企业名称', '公司名称', '法人名称',
                'Company Name', 'company name', 'COMPANY NAME',
                '株式会社', '有限会社', 'Corporation', 'Corp', 'Ltd', 'Inc',
                '事業者名', '販売業者', '販売事業者名'
            ],
            'phone': [
                '咨询用电话号码', '电话号码', '電話番号', 'TEL', 'Tel', 'tel',
                'Phone', 'phone', 'PHONE', 'Telephone', 'telephone',
                '联系电话', '咨询电话', '客服电话', '服务电话',
                '電話', 'でんわ', 'ＴＥＬ', '☎', '📞'
            ],
            'address': [
                '地址', '住所', '所在地', 'Address', 'address', 'ADDRESS',
                '联系地址', '公司地址', '营业地址', '事业所所在地',
                '本社所在地', '事務所', '事务所', '営業所'
            ],
            'representative': [
                '购物代表的姓名', '代表者', '代表取締役', '責任者', '负责人',
                'Representative', 'representative', 'REPRESENTATIVE',
                '联系人', '代表人', '担当者', '責任者氏名',
                '代表者氏名', '代表取締役氏名', 'CEO', 'President'
            ],
            'store_name': [
                '商店名', '店舗名', 'ショップ名', 'Store Name', 'store name',
                'Shop Name', 'shop name', '店铺名称', '店名',
                'ストア名', '販売店名', 'Seller Name'
            ],
            'email': [
                'Email', 'email', 'E-mail', 'e-mail', 'EMAIL',
                'メール', 'メールアドレス', '电子邮件', '邮箱',
                '联系邮箱', 'Contact Email', '@'
            ],
            'fax': [
                'Fax', 'fax', 'FAX', 'ファックス', 'ファクス',
                '传真', '传真号码', 'Fax Number'
            ]
        }
        
        # 查找包含卖家信息的区域
        info_sections = soup.find_all(['div', 'section', 'table', 'dl', 'ul'], 
                                     string=re.compile(r'详尽的卖家信息|详民的卖家信息|seller.*info|事業者情報|販売業者情報', re.I))
        
        if not info_sections:
            # 扩大搜索范围
            info_sections = soup.find_all(['div', 'section', 'table', 'dl', 'ul'])
        
        for section in info_sections[:10]:  # 限制搜索范围
            section_text = section.get_text() if section else ""
            
            for field, keywords in field_keywords.items():
                if info.get(field):  # 已经找到该字段
                    continue
                
                for keyword in keywords:
                    if keyword.lower() in section_text.lower():
                        value = self._extract_value_near_keyword_ultimate(section_text, keyword, field)
                        if value and self._validate_extracted_value_ultimate(field, value):
                            info[field] = value
                            break
                
                if info.get(field):
                    break
        
        return info
    
    def _extract_from_html_structure_ultimate(self, soup):
        """终极版HTML结构提取"""
        info = {}
        
        # 查找表格结构
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key_text = cells[0].get_text().strip().lower()
                    value_text = cells[1].get_text().strip()
                    
                    # 匹配字段
                    if not info.get('business_name') and any(k in key_text for k in ['business', '会社', '商号', '法人', '事業者']):
                        info['business_name'] = value_text
                    elif not info.get('phone') and any(k in key_text for k in ['电话', 'tel', 'phone', '電話']):
                        info['phone'] = value_text
                    elif not info.get('address') and any(k in key_text for k in ['地址', '住所', 'address', '所在地']):
                        info['address'] = value_text
                    elif not info.get('representative') and any(k in key_text for k in ['代表', 'representative', '責任者', '担当']):
                        info['representative'] = value_text
                    elif not info.get('store_name') and any(k in key_text for k in ['店', 'store', 'shop', 'ショップ']):
                        info['store_name'] = value_text
                    elif not info.get('email') and any(k in key_text for k in ['email', 'mail', 'メール', '@']):
                        info['email'] = value_text
                    elif not info.get('fax') and any(k in key_text for k in ['fax', 'ファックス', '传真']):
                        info['fax'] = value_text
        
        # 查找定义列表
        dls = soup.find_all('dl')
        for dl in dls:
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            
            for dt, dd in zip(dts, dds):
                key_text = dt.get_text().strip().lower()
                value_text = dd.get_text().strip()
                
                if not info.get('business_name') and any(k in key_text for k in ['business', '会社', '商号']):
                    info['business_name'] = value_text
                elif not info.get('phone') and any(k in key_text for k in ['电话', 'tel', 'phone']):
                    info['phone'] = value_text
                # ... 其他字段类似处理
        
        return info
    
    def _extract_with_regex_ultimate(self, text):
        """终极版正则表达式提取"""
        info = {}
        
        # 增强的正则模式
        patterns = {
            'business_name': [
                r'Business\s*Name[：:\s]*([^\n\r]{3,80})',
                r'会社名[：:\s]*([^\n\r]{3,80})',
                r'商号[：:\s]*([^\n\r]{3,80})',
                r'事業者名[：:\s]*([^\n\r]{3,80})',
                r'法人名称[：:\s]*([^\n\r]{3,80})',
                r'([A-Za-z\s]{3,50}(?:株式会社|有限会社|Company|Ltd|Corporation|Inc|Corp))',
            ],
            'phone': [
                r'咨询用电话号码[：:\s]*(\+?[\d\-\(\)\s]{8,25})',
                r'電話番号[：:\s]*(\+?[\d\-\(\)\s]{8,25})',
                r'TEL[：:\s]*(\+?[\d\-\(\)\s]{8,25})',
                r'Phone[：:\s]*(\+?[\d\-\(\)\s]{8,25})',
                r'(\+?\d{1,4}[-\s]?\d{10,12})',
                r'(\d{2,4}[-\s]\d{4}[-\s]\d{4})',
                r'(\(\d{2,4}\)\s?\d{4}[-\s]?\d{4})',
            ],
            'address': [
                r'地址[：:\s]*([^\n\r]{10,150})',
                r'住所[：:\s]*([^\n\r]{10,150})',
                r'Address[：:\s]*([^\n\r]{10,150})',
                r'所在地[：:\s]*([^\n\r]{10,150})',
                r'(〒\d{3}-\d{4}[^\n\r]{5,120})',
                r'(\d{6}[^\n\r]{8,120})',  # 中国邮编格式
            ],
            'representative': [
                r'购物代表的姓名[：:\s]*([^\n\r]{2,40})',
                r'代表者[：:\s]*([^\n\r]{2,40})',
                r'代表取締役[：:\s]*([^\n\r]{2,40})',
                r'Representative[：:\s]*([^\n\r]{2,40})',
                r'責任者[：:\s]*([^\n\r]{2,40})',
                r'担当者[：:\s]*([^\n\r]{2,40})',
            ],
            'store_name': [
                r'商店名[：:\s]*([^\n\r]{2,50})',
                r'店舗名[：:\s]*([^\n\r]{2,50})',
                r'Store\s*Name[：:\s]*([^\n\r]{2,50})',
                r'ショップ名[：:\s]*([^\n\r]{2,50})',
                r'販売店名[：:\s]*([^\n\r]{2,50})',
            ],
            'email': [
                r'Email[：:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'メール[：:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            ],
            'fax': [
                r'Fax[：:\s]*(\+?[\d\-\(\)\s]{8,25})',
                r'ファックス[：:\s]*(\+?[\d\-\(\)\s]{8,25})',
                r'传真[：:\s]*(\+?[\d\-\(\)\s]{8,25})',
            ]
        }
        
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if self._validate_extracted_value_ultimate(field, value):
                        info[field] = value
                        break
        
        return info
    
    def _deep_text_analysis(self, text):
        """深度文本分析提取"""
        info = {}
        
        # 使用更复杂的文本分析
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 分析上下文
            context = ' '.join(lines[max(0, i-2):i+3])  # 前后2行的上下文
            
            # 电话号码模式匹配
            if not info.get('phone'):
                phone_match = re.search(r'(\+?\d{1,4}[-\s]?\d{8,12})', line)
                if phone_match and any(keyword in context.lower() for keyword in ['电话', 'tel', 'phone', '連絡']):
                    info['phone'] = phone_match.group(1)
            
            # 邮箱模式匹配
            if not info.get('email'):
                email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
                if email_match:
                    info['email'] = email_match.group(1)
            
            # 地址模式匹配（包含邮编）
            if not info.get('address'):
                if re.search(r'〒\d{3}-\d{4}', line) or re.search(r'\d{6}', line):
                    # 可能是地址行，取当前行和下一行
                    address_parts = [line]
                    if i + 1 < len(lines):
                        address_parts.append(lines[i + 1].strip())
                    potential_address = ' '.join(address_parts)
                    if len(potential_address) > 10:
                        info['address'] = potential_address
        
        return info
    
    def _extract_value_near_keyword_ultimate(self, text, keyword, field):
        """终极版关键词附近值提取"""
        try:
            # 找到关键词位置
            keyword_pos = text.lower().find(keyword.lower())
            if keyword_pos == -1:
                return None
            
            # 提取关键词后的文本
            after_keyword = text[keyword_pos + len(keyword):].strip()
            
            # 移除开头的分隔符
            after_keyword = re.sub(r'^[：:\s\-=]+', '', after_keyword)
            
            if field == 'phone':
                # 电话号码特殊处理
                phone_patterns = [
                    r'\+?\d{1,4}[-\s]?\d{10,12}',
                    r'\+?\d{11,15}',
                    r'\d{2,4}[-\s]\d{4}[-\s]\d{4}',
                    r'\(\d{2,4}\)\s?\d{4}[-\s]?\d{4}',
                ]
                for pattern in phone_patterns:
                    match = re.search(pattern, after_keyword)
                    if match:
                        return match.group(0)
            elif field == 'email':
                # 邮箱特殊处理
                email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                match = re.search(email_pattern, after_keyword)
                if match:
                    return match.group(1)
            elif field == 'address':
                # 地址通常是多行的
                lines = after_keyword.split('\n')[:4]  # 取前4行
                address_parts = []
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 2:
                        address_parts.append(line)
                        if len(' '.join(address_parts)) > 20:  # 地址足够长
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
    
    def _validate_extracted_value_ultimate(self, field, value):
        """终极版值验证"""
        if not value or len(value.strip()) < 2:
            return False
        
        value = value.strip()
        
        if field == 'phone':
            # 电话号码必须包含足够的数字
            digit_count = len(re.findall(r'\d', value))
            return 8 <= digit_count <= 20
        elif field == 'email':
            # 邮箱格式验证
            return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value))
        elif field == 'address':
            # 地址必须有一定长度且包含有意义字符
            return len(value) >= 8 and bool(re.search(r'[\u4e00-\u9fff]|[a-zA-Z]', value))
        elif field == 'business_name':
            # 公司名不能太短或太长
            return 3 <= len(value) <= 100
        elif field == 'representative':
            # 代表人姓名长度合理
            return 2 <= len(value) <= 50
        elif field == 'store_name':
            # 店铺名长度合理
            return 2 <= len(value) <= 60
        elif field == 'fax':
            # 传真号码验证
            digit_count = len(re.findall(r'\d', value))
            return 8 <= digit_count <= 20
        
        return True
    
    def _clean_seller_info_ultimate(self, info):
        """终极版信息清理"""
        cleaned = {}
        
        for field, value in info.items():
            if not value:
                cleaned[field] = ''
                continue
            
            # 基本清理
            value = str(value).strip()
            value = re.sub(r'\s+', ' ', value)  # 合并空格
            value = re.sub(r'^[：:\-\s=]+', '', value)  # 移除开头分隔符
            value = re.sub(r'[：:\-\s=]+$', '', value)  # 移除结尾分隔符
            
            # 字段特定清理
            if field == 'phone' or field == 'fax':
                # 保留数字、加号、减号、括号、空格
                value = re.sub(r'[^\d\+\-\(\)\s]', '', value)
                value = re.sub(r'\s+', '', value)  # 移除空格使格式统一
            elif field == 'email':
                # 邮箱清理
                value = re.sub(r'\s+', '', value)  # 移除所有空格
            elif field == 'address':
                # 地址清理换行和多余空格
                value = re.sub(r'\n+', ' ', value)
                value = re.sub(r'\s{2,}', ' ', value)
            
            # 限制长度
            if field == 'address':
                cleaned[field] = value[:200]
            elif field == 'business_name':
                cleaned[field] = value[:100]
            else:
                cleaned[field] = value[:80]
        
        return cleaned
    
    def _get_column_mappings(self):
        """获取中文列名映射"""
        # 产品信息列名中文映射
        product_columns_mapping = {
            'asin': 'ASIN编号',
            'title': '产品标题',
            'price': '价格',
            'rating': '评分',
            'review_count': '评价数量',
            'image_url': '图片链接',
            'url': '产品链接',
            'extracted_at': '提取时间'
        }
        
        # 卖家信息列名中文映射
        seller_columns_mapping = {
            'seller_name': '卖家名称',
            'seller_url': '卖家链接',
            'business_name': '公司名称',
            'phone': '电话号码',
            'address': '地址',
            'representative': '代表人姓名',
            'store_name': '店铺名称',
            'email': '电子邮箱',
            'fax': '传真号码',
            'product_title': '关联产品标题',
            'product_url': '关联产品链接',
            'product_asin': '关联产品ASIN',
            'extracted_at': '提取时间'
        }
        
        return product_columns_mapping, seller_columns_mapping
    
    def _save_data_realtime(self, products, sellers, save_callback=None):
        """实时保存数据"""
        try:
            if not products:
                return
            
            # 创建DataFrame并重命名列名为中文
            products_df = pd.DataFrame(products)
            sellers_df = pd.DataFrame(sellers) if sellers else pd.DataFrame()
            
            # 获取中文列名映射
            product_columns_mapping, seller_columns_mapping = self._get_column_mappings()
            
            # 重命名列名
            if not products_df.empty:
                products_df = products_df.rename(columns=product_columns_mapping)
            
            if not sellers_df.empty:
                sellers_df = sellers_df.rename(columns=seller_columns_mapping)
            
            # 保存到Excel
            with pd.ExcelWriter(self.current_save_file, engine='openpyxl') as writer:
                products_df.to_excel(writer, sheet_name='产品信息', index=False)
                if not sellers_df.empty:
                    sellers_df.to_excel(writer, sheet_name='卖家信息', index=False)
            
            if save_callback:
                save_callback(f"💾 已保存 {len(products)} 个产品，{len(sellers)} 个卖家信息到 {self.current_save_file}")
        
        except Exception as e:
            print(f"实时保存失败: {e}")
    
    def _save_data_final(self, products, sellers, save_callback=None):
        """最终保存数据"""
        try:
            if not products:
                return
            
            # 创建DataFrame并重命名列名为中文
            products_df = pd.DataFrame(products)
            sellers_df = pd.DataFrame(sellers) if sellers else pd.DataFrame()
            
            # 获取中文列名映射
            product_columns_mapping, seller_columns_mapping = self._get_column_mappings()
            
            # 重命名列名
            if not products_df.empty:
                products_df = products_df.rename(columns=product_columns_mapping)
            
            if not sellers_df.empty:
                sellers_df = sellers_df.rename(columns=seller_columns_mapping)
            
            # 保存到Excel
            with pd.ExcelWriter(self.current_save_file, engine='openpyxl') as writer:
                products_df.to_excel(writer, sheet_name='产品信息', index=False)
                if not sellers_df.empty:
                    sellers_df.to_excel(writer, sheet_name='卖家信息', index=False)
            
            # 同时保存CSV格式（也使用中文列名）
            csv_file = self.current_save_file.replace('.xlsx', '_products.csv')
            products_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            
            if not sellers_df.empty:
                sellers_csv = self.current_save_file.replace('.xlsx', '_sellers.csv')
                sellers_df.to_csv(sellers_csv, index=False, encoding='utf-8-sig')
            
            if save_callback:
                save_callback(f"✅ 最终保存完成！产品: {len(products)}，卖家: {len(sellers)}")
                save_callback(f"📁 文件位置: {self.current_save_file}")
        
        except Exception as e:
            print(f"最终保存失败: {e}")
    
    def stop_search(self):
        """停止搜索"""
        self.is_searching = False


class UltimateScraperGUI:
    """终极版GUI界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Amazon Japan 卖家信息提取工具 - 终极版 v4.0")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.scraper = UltimateAmazonScraper()
        self.search_thread = None
        self.is_searching = False
        
        self.setup_gui()
    
    def setup_gui(self):
        """设置GUI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="🚀 Amazon Japan 终极版卖家信息提取工具", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 搜索配置区域
        search_frame = ttk.LabelFrame(main_frame, text="🔍 搜索配置", padding="15")
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 关键词输入
        ttk.Label(search_frame, text="搜索关键词:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.keyword_var = tk.StringVar()
        keyword_entry = ttk.Entry(search_frame, textvariable=self.keyword_var, width=40, font=('Arial', 10))
        keyword_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # 提示文本
        tip_label = ttk.Label(search_frame, text="💡 支持任何商品关键词，如：手机壳、数据线、小商品等", 
                             font=('Arial', 9), foreground='#666')
        tip_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 10))
        
        # 无限搜索说明
        unlimited_label = ttk.Label(search_frame, text="🔄 无限制搜索模式：想搜多久搜多久，实时保存数据", 
                                   font=('Arial', 10, 'bold'), foreground='#0066cc')
        unlimited_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=(0, 15))
        
        self.start_button = ttk.Button(control_frame, text="🚀 开始无限搜索", 
                                      command=self.start_unlimited_search, 
                                      style='Accent.TButton')
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ 停止搜索", 
                                     command=self.stop_search, 
                                     state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.open_folder_button = ttk.Button(control_frame, text="📁 打开保存文件夹", 
                                           command=self.open_save_folder)
        self.open_folder_button.grid(row=0, column=2)
        
        # 进度显示区域
        progress_frame = ttk.LabelFrame(main_frame, text="📊 搜索进度", padding="15")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 进度条
        self.progress_var = tk.StringVar(value="准备开始搜索...")
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var, font=('Arial', 10))
        progress_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 统计信息
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.products_count_var = tk.StringVar(value="产品数量: 0")
        self.sellers_count_var = tk.StringVar(value="卖家数量: 0")
        self.time_elapsed_var = tk.StringVar(value="运行时间: 00:00:00")
        
        ttk.Label(stats_frame, textvariable=self.products_count_var, font=('Arial', 9)).grid(row=0, column=0, padx=(0, 20))
        ttk.Label(stats_frame, textvariable=self.sellers_count_var, font=('Arial', 9)).grid(row=0, column=1, padx=(0, 20))
        ttk.Label(stats_frame, textvariable=self.time_elapsed_var, font=('Arial', 9)).grid(row=0, column=2)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="📝 搜索日志", padding="15")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # 创建文本框和滚动条
        self.log_text = tk.Text(log_frame, height=15, width=80, font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        search_frame.columnconfigure(1, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 初始化时间
        self.start_time = None
        self.update_timer()
    
    def start_unlimited_search(self):
        """开始无限制搜索"""
        keyword = self.keyword_var.get().strip()
        if not keyword:
            messagebox.showerror("错误", "请输入搜索关键词")
            return
        
        if self.is_searching:
            messagebox.showwarning("警告", "搜索正在进行中")
            return
        
        # 更新UI状态
        self.is_searching = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 重置统计
        self.products_count_var.set("产品数量: 0")
        self.sellers_count_var.set("卖家数量: 0")
        self.start_time = time.time()
        
        # 启动搜索线程
        self.search_thread = threading.Thread(
            target=self.search_worker,
            args=(keyword,),
            daemon=True
        )
        self.search_thread.start()
        
        self.log_message(f"🚀 开始无限制搜索: {keyword}")
        self.log_message("💡 可以最小化窗口，搜索将在后台继续运行")
        self.log_message("💾 数据将自动保存，无需担心丢失")
    
    def search_worker(self, keyword):
        """搜索工作线程"""
        try:
            self.scraper.unlimited_search(
                keyword=keyword,
                progress_callback=self.update_progress,
                stop_flag=lambda: self.is_searching and self.scraper.is_searching,
                save_callback=self.log_message
            )
        except Exception as e:
            self.log_message(f"❌ 搜索过程中出错: {e}")
        finally:
            # 恢复UI状态
            self.root.after(0, self.search_completed)
    
    def stop_search(self):
        """停止搜索"""
        if not self.is_searching:
            return
        
        self.is_searching = False
        self.scraper.stop_search()
        self.log_message("⏹️ 正在停止搜索...")
    
    def search_completed(self):
        """搜索完成后的UI更新"""
        self.is_searching = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.log_message("✅ 搜索已完成或停止")
    
    def update_progress(self, message):
        """更新进度显示"""
        def update_ui():
            self.progress_var.set(message)
            self.log_message(message)
            
            # 更新统计信息
            self.products_count_var.set(f"产品数量: {self.scraper.total_products_found}")
            self.sellers_count_var.set(f"卖家数量: {self.scraper.total_sellers_extracted}")
        
        self.root.after(0, update_ui)
    
    def log_message(self, message):
        """添加日志消息"""
        def add_log():
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
        
        self.root.after(0, add_log)
    
    def update_timer(self):
        """更新运行时间"""
        if self.start_time and self.is_searching:
            elapsed = time.time() - self.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.time_elapsed_var.set(f"运行时间: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # 每秒更新一次
        self.root.after(1000, self.update_timer)
    
    def open_save_folder(self):
        """打开保存文件夹"""
        import subprocess
        import platform
        
        save_path = os.path.abspath(self.scraper.save_directory)
        
        try:
            if platform.system() == "Windows":
                os.startfile(save_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", save_path])
            else:  # Linux
                subprocess.run(["xdg-open", save_path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {e}")


def main():
    """主函数"""
    root = tk.Tk()
    app = UltimateScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
