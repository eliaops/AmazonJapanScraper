#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的卖家信息提取器 - 基于关键词关联和上下文分析
Enhanced Seller Information Extractor - Based on Keyword Association and Context Analysis
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class EnhancedSellerExtractor:
    """增强的卖家信息提取器"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        self.session.headers.update(self.headers)
        
        # 关键词字典 - 基于Amazon实际页面结构
        self.field_keywords = {
            'business_name': [
                'Business Name', 'business name', 'Business name',
                '会社名', '商号', '企业名称', '公司名称',
                'Company Name', 'company name'
            ],
            'phone': [
                '咨询用电话号码', '电话号码', '電話番号', 'TEL', 'Tel',
                'Phone', 'phone', 'Telephone', 'Contact Number',
                '联系电话', '咨询电话'
            ],
            'address': [
                '地址', '住所', '所在地', 'Address', 'address',
                '联系地址', '公司地址', '营业地址'
            ],
            'representative': [
                '购物代表的姓名', '代表者', '代表取締役', '責任者',
                'Representative', 'representative', 'Contact Person',
                '联系人', '负责人', '代表人'
            ],
            'store_name': [
                '商店名', '店舗名', 'ショップ名', 'Store Name', 'store name',
                'Shop Name', 'shop name', '店铺名称'
            ]
        }
        
        # 电话号码格式模式
        self.phone_patterns = [
            r'\+?\d{1,3}[-\s]?\d{10,11}',  # 国际格式
            r'\+?\d{11,13}',                # 连续数字格式
            r'\d{2,4}[-\s]\d{4}[-\s]\d{4}', # 分段格式
            r'\d{3}[-\s]\d{3,4}[-\s]\d{4}', # 美式格式
            r'\(\d{2,4}\)\s?\d{4}[-\s]?\d{4}', # 括号格式
        ]
        
        # 地址格式模式
        self.address_patterns = [
            r'〒\d{3}-\d{4}[^\n\r]+',       # 日本邮编格式
            r'\d{6}[^\n\r]+',               # 中国邮编格式
            r'[^\n\r]*[市区县][^\n\r]*[路街道号][^\n\r]*', # 中文地址
            r'[^\n\r]*[都府県市区][^\n\r]*',  # 日文地址
        ]
    
    def extract_seller_info(self, seller_url):
        """
        提取卖家信息的主方法
        
        Args:
            seller_url: 卖家信息页面URL
            
        Returns:
            dict: 提取的卖家信息
        """
        try:
            response = self.session.get(seller_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 方法1: 基于HTML结构提取
            structured_info = self._extract_from_structure(soup)
            
            # 方法2: 基于文本关键词提取
            text_info = self._extract_from_text(soup.get_text())
            
            # 方法3: 基于特定元素提取
            element_info = self._extract_from_elements(soup)
            
            # 合并结果，优先级：结构化 > 元素 > 文本
            final_info = {}
            for key in self.field_keywords.keys():
                final_info[key] = (
                    structured_info.get(key) or 
                    element_info.get(key) or 
                    text_info.get(key) or 
                    ''
                )
            
            # 后处理清理
            final_info = self._clean_extracted_info(final_info)
            
            return final_info
            
        except Exception as e:
            print(f"提取卖家信息失败 {seller_url}: {e}")
            return {}
    
    def _extract_from_structure(self, soup):
        """基于HTML结构提取信息"""
        info = {}
        
        # 查找包含卖家信息的区域
        seller_sections = soup.find_all(['div', 'section', 'table'], 
                                       class_=re.compile(r'seller|merchant|store', re.I))
        
        for section in seller_sections:
            section_text = section.get_text()
            
            # 在每个区域内查找字段
            for field, keywords in self.field_keywords.items():
                if info.get(field):
                    continue
                    
                for keyword in keywords:
                    # 查找包含关键词的元素
                    keyword_elements = section.find_all(
                        text=re.compile(re.escape(keyword), re.I)
                    )
                    
                    for element in keyword_elements:
                        # 获取关键词后的内容
                        value = self._extract_value_after_keyword(
                            element.parent if element.parent else element, 
                            keyword, 
                            field
                        )
                        if value:
                            info[field] = value
                            break
                    
                    if info.get(field):
                        break
        
        return info
    
    def _extract_from_text(self, text):
        """基于文本关键词提取信息"""
        info = {}
        
        for field, keywords in self.field_keywords.items():
            for keyword in keywords:
                # 构建查找模式
                patterns = self._build_text_patterns(keyword, field)
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        value = match.group(1).strip()
                        if self._validate_field_value(field, value):
                            info[field] = value
                            break
                
                if info.get(field):
                    break
        
        return info
    
    def _extract_from_elements(self, soup):
        """基于特定HTML元素提取信息"""
        info = {}
        
        # 查找表格结构
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key_cell = cells[0].get_text().strip()
                    value_cell = cells[1].get_text().strip()
                    
                    # 匹配字段
                    for field, keywords in self.field_keywords.items():
                        if info.get(field):
                            continue
                        for keyword in keywords:
                            if keyword.lower() in key_cell.lower():
                                if self._validate_field_value(field, value_cell):
                                    info[field] = value_cell
                                break
        
        # 查找定义列表
        dls = soup.find_all('dl')
        for dl in dls:
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            
            for dt, dd in zip(dts, dds):
                key_text = dt.get_text().strip()
                value_text = dd.get_text().strip()
                
                for field, keywords in self.field_keywords.items():
                    if info.get(field):
                        continue
                    for keyword in keywords:
                        if keyword.lower() in key_text.lower():
                            if self._validate_field_value(field, value_text):
                                info[field] = value_text
                            break
        
        return info
    
    def _build_text_patterns(self, keyword, field):
        """构建文本提取模式"""
        patterns = []
        
        # 基本模式：关键词 + 分隔符 + 值
        separators = [r'[：:\s]*', r'[：:\s]+', r'\s*:\s*', r'\s+']
        
        for sep in separators:
            if field == 'phone':
                # 电话号码特殊处理
                for phone_pattern in self.phone_patterns:
                    patterns.append(f'{re.escape(keyword)}{sep}({phone_pattern})')
            elif field == 'address':
                # 地址特殊处理
                patterns.append(f'{re.escape(keyword)}{sep}([^\n\r]{{10,100}})')
            else:
                # 通用模式
                patterns.append(f'{re.escape(keyword)}{sep}([^\n\r]{{1,50}})')
        
        return patterns
    
    def _extract_value_after_keyword(self, element, keyword, field):
        """提取关键词后的值"""
        try:
            element_text = element.get_text()
            
            # 查找关键词位置
            keyword_pos = element_text.lower().find(keyword.lower())
            if keyword_pos == -1:
                return None
            
            # 提取关键词后的内容
            after_keyword = element_text[keyword_pos + len(keyword):].strip()
            
            # 移除开头的分隔符
            after_keyword = re.sub(r'^[：:\s]+', '', after_keyword)
            
            # 根据字段类型提取值
            if field == 'phone':
                for pattern in self.phone_patterns:
                    match = re.search(pattern, after_keyword)
                    if match:
                        return match.group(0)
            elif field == 'address':
                # 地址通常到下一个字段或换行
                lines = after_keyword.split('\n')
                if lines:
                    address_parts = []
                    for line in lines[:3]:  # 最多取3行
                        line = line.strip()
                        if line and len(line) > 2:
                            address_parts.append(line)
                        if len(' '.join(address_parts)) > 20:  # 地址足够长
                            break
                    return ' '.join(address_parts) if address_parts else None
            else:
                # 其他字段取第一行
                first_line = after_keyword.split('\n')[0].strip()
                return first_line if first_line else None
                
        except Exception as e:
            print(f"提取值时出错: {e}")
            return None
    
    def _validate_field_value(self, field, value):
        """验证字段值是否合理"""
        if not value or len(value.strip()) < 2:
            return False
        
        value = value.strip()
        
        if field == 'phone':
            # 电话号码验证
            return bool(re.search(r'\d{8,}', value))
        elif field == 'address':
            # 地址验证
            return len(value) >= 10 and bool(re.search(r'[\u4e00-\u9fff]|[a-zA-Z]', value))
        elif field == 'business_name':
            # 公司名验证
            return len(value) >= 3 and len(value) <= 100
        elif field == 'representative':
            # 代表人验证
            return len(value) >= 2 and len(value) <= 50
        elif field == 'store_name':
            # 店铺名验证
            return len(value) >= 2 and len(value) <= 50
        
        return True
    
    def _clean_extracted_info(self, info):
        """清理提取的信息"""
        cleaned = {}
        
        for field, value in info.items():
            if not value:
                cleaned[field] = ''
                continue
            
            # 基本清理
            value = value.strip()
            value = re.sub(r'\s+', ' ', value)  # 合并多个空格
            value = re.sub(r'^[：:\-\s]+', '', value)  # 移除开头的分隔符
            value = re.sub(r'[：:\-\s]+$', '', value)  # 移除结尾的分隔符
            
            # 字段特定清理
            if field == 'phone':
                # 电话号码清理
                value = re.sub(r'[^\d\+\-\(\)\s]', '', value)
                value = re.sub(r'\s+', '', value)  # 移除空格
            elif field == 'address':
                # 地址清理
                value = re.sub(r'\n+', ' ', value)  # 换行转空格
                value = re.sub(r'\s{2,}', ' ', value)  # 多个空格合并
            
            cleaned[field] = value[:200]  # 限制长度
        
        return cleaned


def test_extractor():
    """测试提取器"""
    extractor = EnhancedSellerExtractor()
    
    # 测试URL（需要替换为实际的卖家页面URL）
    test_url = "https://www.amazon.co.jp/sp?seller=EXAMPLE"
    
    print("测试增强卖家信息提取器...")
    result = extractor.extract_seller_info(test_url)
    
    print("提取结果:")
    for field, value in result.items():
        print(f"  {field}: {value}")


if __name__ == "__main__":
    test_extractor()
