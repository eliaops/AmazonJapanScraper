#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon Japan 卖家信息提取工具 - 纯Selenium版 v5.0
终极方案：完全使用无头浏览器，绕过所有反爬虫限制
"""

import tkinter as tk
from tkinter import ttk, messagebox
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
import threading
import os
from datetime import datetime
from urllib.parse import urljoin

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_OK = True
except:
    SELENIUM_OK = False


class SeleniumOnlyScraper:
    """纯Selenium爬虫 - 终极方案"""
    
    def __init__(self):
        self.base_url = "https://www.amazon.co.jp"
        self.is_searching = False
        self.save_directory = "amazon_data"
        os.makedirs(self.save_directory, exist_ok=True)
    
    def search_products(self, keyword, max_pages=5, max_products=100,
                       progress_callback=None, stop_flag=None):
        """使用Selenium搜索产品和卖家信息"""
        if not SELENIUM_OK:
            if progress_callback:
                progress_callback("❌ Selenium未安装，请运行: pip install selenium undetected-chromedriver")
            return [], []
        
        self.is_searching = True
        all_products = []
        all_sellers = []
        driver = None
        
        try:
            if progress_callback:
                progress_callback("🚀 启动无头浏览器...")
            
            # 创建无头浏览器
            options = uc.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--lang=ja-JP')
            
            driver = uc.Chrome(options=options)
            driver.set_page_load_timeout(30)
            
            if progress_callback:
                progress_callback("✅ 浏览器启动成功")
            
            # 搜索每一页
            for page in range(1, max_pages + 1):
                if stop_flag and not stop_flag():
                    break
                
                if progress_callback:
                    progress_callback(f"🔍 搜索第 {page}/{max_pages} 页...")
                
                try:
                    # 访问搜索页
                    search_url = f"{self.base_url}/s?k={keyword}&page={page}"
                    driver.get(search_url)
                    
                    # 等待加载
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]'))
                        )
                    except:
                        if progress_callback:
                            progress_callback(f"⚠️ 第{page}页加载超时")
                        continue
                    
                    # 解析产品 - 直接用BeautifulSoup解析完整页面
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    items = soup.select('div[data-component-type="s-search-result"]')
                    
                    if not items:
                        if progress_callback:
                            progress_callback(f"⚠️ 第{page}页无产品")
                        continue
                    
                    if progress_callback:
                        progress_callback(f"📦 第{page}页找到{len(items)}个产品")
                    
                    # 提取每个产品 - items已经是BeautifulSoup对象
                    for idx, item in enumerate(items, 1):
                        if stop_flag and not stop_flag():
                            break
                        
                        if len(all_products) >= max_products:
                            break
                        
                        try:
                            # item已经是BeautifulSoup的Tag对象，直接提取
                            product = self._extract_product(item)
                            if not product or not product.get('url'):
                                continue
                            
                            if progress_callback:
                                progress_callback(f"📋 [{len(all_products)+1}/{max_products}] {product['title'][:30]}...")
                            
                            all_products.append(product)
                            
                            # 获取卖家信息
                            if product['url']:
                                seller = self._get_seller_with_browser(driver, product, progress_callback)
                                if seller:
                                    all_sellers.append(seller)
                            
                            # 延迟
                            time.sleep(random.uniform(0.5, 1.0))
                            
                        except Exception as e:
                            if progress_callback:
                                progress_callback(f"⚠️ 产品处理失败: {e}")
                    
                    if len(all_products) >= max_products:
                        break
                    
                    # 页面间延迟
                    time.sleep(random.uniform(2, 3))
                    
                except Exception as e:
                    if progress_callback:
                        progress_callback(f"❌ 第{page}页出错: {e}")
            
            # 保存结果
            if all_products:
                filename = self._save_to_excel(all_products, all_sellers)
                if progress_callback:
                    progress_callback(f"💾 已保存到: {filename}")
                    progress_callback(f"✅ 完成！产品:{len(all_products)}, 卖家:{len(all_sellers)}")
            else:
                if progress_callback:
                    progress_callback("❌ 未获取到任何产品")
            
            return all_products, all_sellers
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ 严重错误: {e}")
            return all_products, all_sellers
        finally:
            if driver:
                try:
                    driver.quit()
                    if progress_callback:
                        progress_callback("🔒 浏览器已关闭")
                except:
                    pass
            self.is_searching = False
    
    def _extract_product(self, element):
        """提取产品信息"""
        try:
            asin = element.get('data-asin', '')
            if not asin or len(asin) < 5:
                return None
            
            # 直接用ASIN构建URL（最可靠）
            url = f"{self.base_url}/dp/{asin}"
            
            # 标题 - 尝试多种选择器
            title = ''
            h2 = element.select_one('h2')
            if h2:
                # 获取h2下所有文本
                title = h2.get_text(strip=True)
            
            if not title or len(title) < 10:
                # 备用方案
                for selector in ['.a-size-medium', '.a-size-base-plus', 'span.a-text-normal']:
                    elem = element.select_one(selector)
                    if elem:
                        title = elem.get_text(strip=True)
                        if len(title) > 10:
                            break
            
            if not title or len(title) < 5:
                return None
            
            # 价格
            price = '价格未知'
            price_elem = element.select_one('.a-price .a-offscreen')
            if price_elem:
                price = price_elem.get_text(strip=True)
            else:
                price_whole = element.select_one('.a-price-whole')
                if price_whole:
                    price = price_whole.get_text(strip=True)
            
            # 评分
            rating = ''
            rating_elem = element.select_one('.a-icon-alt')
            if rating_elem:
                rating = rating_elem.get_text(strip=True)
            
            return {
                'asin': asin,
                'title': title[:150],
                'price': price,
                'rating': rating,
                'url': url,
            }
        except Exception as e:
            print(f"提取产品失败: {e}")
            return None
    
    def _get_seller_with_browser(self, driver, product, progress_callback):
        """使用浏览器获取卖家信息"""
        try:
            # 访问产品页
            driver.get(product['url'])
            
            # 等待页面加载
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#merchant-info, #buybox, #tabular-buybox, #availability'))
                )
            except:
                pass
            
            time.sleep(1)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # 提取卖家名称和链接
            seller_name = '未知卖家'
            seller_url = ''
            
            # 方法1: merchant-info区域（最常见）
            merchant_info = soup.select_one('#merchant-info')
            if merchant_info:
                link = merchant_info.select_one('a[href*="seller="], a[href*="/sp?"], a[href*="/shops/"]')
                if link:
                    seller_name = link.get_text(strip=True)
                    seller_url = urljoin(self.base_url, link.get('href'))
            
            # 方法2: tabular-buybox区域
            if seller_name == '未知卖家':
                tabular = soup.select_one('#tabular-buybox')
                if tabular:
                    # 查找"配送方"标签
                    seller_row = None
                    for span in tabular.find_all('span', string=re.compile(r'配送方|販売元|出品者|Sold by')):
                        seller_row = span.find_parent('div', class_=re.compile(r'tabular'))
                        if seller_row:
                            break
                    
                    if seller_row:
                        link = seller_row.select_one('a[href*="seller="], a[href*="/sp?"]')
                        if link:
                            seller_name = link.get_text(strip=True)
                            seller_url = urljoin(self.base_url, link.get('href'))
            
            # 方法3: 直接搜索"配送方"文本
            if seller_name == '未知卖家':
                text = soup.get_text()
                # 查找"配送方 Amazon" 或 "配送方 SENNWAK 直営店"这样的模式
                seller_match = re.search(r'配送方[：:\s]+([^\n\r]{2,50})', text)
                if seller_match:
                    seller_name = seller_match.group(1).strip()
                    # 尝试找到对应的链接
                    for link in soup.find_all('a', href=re.compile(r'/sp\?|seller=')):
                        link_text = link.get_text(strip=True)
                        if link_text and link_text in seller_name:
                            seller_url = urljoin(self.base_url, link.get('href'))
                            break
            
            # 方法4: 直接查找所有seller=链接（最通用）
            if seller_name == '未知卖家':
                seller_links = soup.find_all('a', href=re.compile(r'seller='))
                if seller_links:
                    # 优先选择带有店铺名称的链接
                    for link in seller_links:
                        text = link.get_text(strip=True)
                        href = link.get('href')
                        # 过滤掉空文本和无关链接
                        if text and len(text) > 2 and len(text) < 100:
                            # 排除一些常见的无关文本
                            if text not in ['詳細', '詳細を見る', 'View details', 'More', 'Learn more']:
                                seller_name = text
                                seller_url = urljoin(self.base_url, href)
                                break
            
            if progress_callback:
                progress_callback(f"   🏪 卖家: {seller_name}")
            
            seller_info = {
                'seller_name': seller_name,
                'seller_url': seller_url,
                'phone': '',
                'address': '',
                'business_name': '',
                'email': '',
                'fax': '',
                'product_title': product['title'],
                'product_price': product['price'],
                'product_url': product['url'],
                'product_asin': product['asin'],
            }
            
            # 如果有卖家链接且不是Amazon，获取详细信息
            if seller_url and 'amazon' not in seller_name.lower():
                time.sleep(random.uniform(1.5, 2.5))
                details = self._get_seller_details_with_browser(driver, seller_url)
                seller_info.update(details)
            
            return seller_info
        except Exception as e:
            if progress_callback:
                progress_callback(f"   ⚠️ 卖家信息获取失败: {e}")
            return None
    
    def _get_seller_details_with_browser(self, driver, seller_url):
        """使用浏览器获取卖家详细信息 - 根据Amazon日本卖家页面结构"""
        try:
            driver.get(seller_url)
            
            # 等待详细信息加载
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
                )
            except:
                pass
            
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            text = soup.get_text()
            
            details = {}
            
            # Business Name (事業者名) - 从"详尽的卖家信息"区域提取
            business_patterns = [
                r'Business Name[：:\s]*([^P\n]{3,100})(?:Phone|TEL|电话)',  # 匹配到Phone之前
                r'事業者名[：:\s]*([^\n]{3,100})',
                r'会社名[：:\s]*([^\n]{3,100})',
                r'販売業者[：:\s]*([^\n]{3,100})',
            ]
            for pattern in business_patterns:
                match = re.search(pattern, text)
                if match:
                    biz_name = match.group(1).strip()
                    # 清理可能的换行和多余空格
                    biz_name = re.sub(r'\s+', ' ', biz_name)
                    details['business_name'] = biz_name
                    break
            
            # Phone (咨询用电话号码) - 优先匹配标签后的数字
            phone_patterns = [
                r'Phone Number[：:\s]*(\d{10,15})',
                r'咨询用电话号码[：:\s]*(\d{10,15})',
                r'電話番号[：:\s]*(\d{10,15})',
                r'TEL[：:\s]*(\d{10,15})',
                r'电话[：:\s]*(\d{10,15})',
                r'Tel[：:\s]*(\d{10,15})',
                # 匹配独立的11位数字（中国手机号）
                r'(?:^|\n|\s)(\d{11})(?:\n|\s|Address|地址)',
                # 匹配日本电话号码格式（带连字符）
                r'(\d{2,4}[-\s]\d{2,4}[-\s]\d{4})',
            ]
            for pattern in phone_patterns:
                match = re.search(pattern, text)
                if match:
                    phone = match.group(1).strip()
                    # 清理电话号码中的连字符和空格
                    phone = re.sub(r'[-\s]', '', phone)
                    # 验证是合理的电话号码长度
                    if len(phone) >= 10:
                        details['phone'] = phone
                        break
            
            # Address (地址) - 提取完整地址
            address_patterns = [
                r'Address[：:\s]*([^\n]{15,250}CN)',  # 匹配到CN结尾
                r'地址[：:\s]*([^\n]{15,200})',
                r'住所[：:\s]*([^\n]{15,200})',
                # 直接匹配带Building的地址格式
                r'(\d+,\s*Building\s+A\d[^\n]+?CN)',
            ]
            for pattern in address_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    addr = match.group(1).strip()
                    # 清理地址中的多余空格和换行
                    addr = re.sub(r'\s+', ' ', addr)
                    # 移除可能的尾部垃圾
                    addr = re.sub(r'(CN).*$', r'\1', addr)
                    details['address'] = addr
                    break
            
            # Email
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if email_match:
                details['email'] = email_match.group(1)
            
            # Fax
            fax_patterns = [
                r'FAX[：:\s]*(\d{10,15})',
                r'ファックス[：:\s]*(\d{10,15})',
                r'传真[：:\s]*(\d{10,15})',
            ]
            for pattern in fax_patterns:
                match = re.search(pattern, text)
                if match:
                    details['fax'] = match.group(1).strip()
                    break
            
            # 购物代表姓名 (如果有)
            rep_match = re.search(r'購物代表的姓名[：:\s]*([^\n]{2,30})', text)
            if not rep_match:
                rep_match = re.search(r'代表者氏名[：:\s]*([^\n]{2,30})', text)
            if rep_match:
                details['representative'] = rep_match.group(1).strip()
            
            # 店铺名 (商店名)
            store_match = re.search(r'商店名[：:\s]*([^\n]{2,50})', text)
            if not store_match:
                store_match = re.search(r'店舗名[：:\s]*([^\n]{2,50})', text)
            if store_match:
                details['store_name'] = store_match.group(1).strip()
            
            return details
        except Exception as e:
            print(f"提取卖家详情失败: {e}")
            return {}
    
    def _save_to_excel(self, products, sellers):
        """保存到Excel"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.save_directory, f"amazon_products_{timestamp}.xlsx")
        
        products_df = pd.DataFrame(products)
        sellers_df = pd.DataFrame(sellers) if sellers else pd.DataFrame()
        
        # 中文列名
        product_mapping = {
            'asin': 'ASIN编号',
            'title': '产品标题',
            'price': '价格',
            'rating': '评分',
            'url': '产品链接',
        }
        
        seller_mapping = {
            'seller_name': '卖家名称',
            'seller_url': '卖家链接',
            'phone': '电话号码',
            'address': '地址',
            'business_name': '公司名称',
            'product_title': '关联产品',
            'product_price': '产品价格',
            'product_url': '产品链接',
            'product_asin': '产品ASIN',
        }
        
        products_df = products_df.rename(columns=product_mapping)
        if not sellers_df.empty:
            sellers_df = sellers_df.rename(columns=seller_mapping)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            products_df.to_excel(writer, sheet_name='产品信息', index=False)
            if not sellers_df.empty:
                sellers_df.to_excel(writer, sheet_name='卖家信息', index=False)
        
        return filename
    
    def stop(self):
        self.is_searching = False


class SeleniumOnlyGUI:
    """纯Selenium GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Amazon Japan 卖家信息提取工具 - 纯Selenium版 v5.0")
        self.root.geometry("800x650")
        
        self.scraper = SeleniumOnlyScraper()
        self.search_thread = None
        self.is_searching = False
        
        self.setup_gui()
    
    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="🚀 Amazon Japan 卖家信息提取工具",
                 font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Label(main_frame, text="纯Selenium版 - 绕过所有反爬虫限制",
                 font=('Arial', 10), foreground='#0066cc').grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        config_frame = ttk.LabelFrame(main_frame, text="🔍 搜索配置", padding="15")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(config_frame, text="关键词:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.keyword_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.keyword_var, width=40).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        ttk.Label(config_frame, text="页数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pages_var = tk.StringVar(value="3")
        ttk.Entry(config_frame, textvariable=self.pages_var, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Label(config_frame, text="产品数:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.products_var = tk.StringVar(value="50")
        ttk.Entry(config_frame, textvariable=self.products_var, width=10).grid(
            row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(0, 15))
        
        self.start_btn = ttk.Button(btn_frame, text="🚀 开始搜索", command=self.start_search)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹️ 停止", command=self.stop_search, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(btn_frame, text="📁 打开文件夹", command=self.open_folder).grid(row=0, column=2)
        
        log_frame = ttk.LabelFrame(main_frame, text="📝 运行日志", padding="15")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = tk.Text(log_frame, height=22, width=70, font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        config_frame.columnconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def start_search(self):
        keyword = self.keyword_var.get().strip()
        if not keyword:
            messagebox.showerror("错误", "请输入关键词")
            return
        
        try:
            max_pages = int(self.pages_var.get())
            max_products = int(self.products_var.get())
        except:
            messagebox.showerror("错误", "页数和产品数必须是数字")
            return
        
        if self.is_searching:
            return
        
        self.is_searching = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        
        self.search_thread = threading.Thread(
            target=self.search_worker,
            args=(keyword, max_pages, max_products),
            daemon=True
        )
        self.search_thread.start()
    
    def search_worker(self, keyword, max_pages, max_products):
        try:
            self.scraper.search_products(
                keyword=keyword,
                max_pages=max_pages,
                max_products=max_products,
                progress_callback=self.log_message,
                stop_flag=lambda: self.is_searching
            )
        except Exception as e:
            self.log_message(f"❌ 错误: {e}")
        finally:
            self.root.after(0, self.search_completed)
    
    def stop_search(self):
        self.is_searching = False
        self.scraper.stop()
        self.log_message("⏹️ 正在停止...")
    
    def search_completed(self):
        self.is_searching = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
    
    def log_message(self, message):
        def add():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
        self.root.after(0, add)
    
    def open_folder(self):
        import subprocess, platform
        path = os.path.abspath(self.scraper.save_directory)
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开: {e}")


def main():
    root = tk.Tk()
    app = SeleniumOnlyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

