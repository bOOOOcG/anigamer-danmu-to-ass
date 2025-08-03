#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动画疯弹幕转PotPlayer工具
将动画疯的弹幕数据转换为PotPlayer支持的ASS字幕格式
"""

import requests
import json
import argparse
import sys
import os
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import re
import unicodedata

class AnimeFongDanmakuConverter:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def fetch_danmaku(self, video_sn, geo='TW,HK'):
        """
        从动画疯API获取弹幕数据
        
        Args:
            video_sn (str): 视频序列号
            geo (str): 地理位置参数，默认为'TW,HK'
        
        Returns:
            dict: 弹幕数据
        """
        url = f"https://api.gamer.com.tw/anime/v1/danmu.php"
        params = {
            'videoSn': video_sn,
            'geo': geo
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # 检查是否为JSON响应
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' not in content_type:
                print(f"警告: 響應類型不是JSON: {content_type}")
            
            data = response.json()
            
            # 检查API响应是否包含弹幕数据
            if 'data' not in data or 'danmu' not in data['data']:
                print("錯誤: API響應中沒有找到彈幕數據")
                return None
                
            return data
            
        except requests.RequestException as e:
            print(f"網絡請求錯誤: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析錯誤: {e}")
            return None
        except Exception as e:
            print(f"獲取彈幕數據時發生錯誤: {e}")
            return None
    
    def format_time(self, seconds):
        """
        将秒数转换为ASS格式的时间戳 (H:MM:SS.CC)
        
        Args:
            seconds (float): 秒数
        
        Returns:
            str: ASS格式时间戳
        """
        total_seconds = float(seconds)
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        secs = total_seconds % 60
        centiseconds = int((secs - int(secs)) * 100)
        
        return f"{hours}:{minutes:02d}:{int(secs):02d}.{centiseconds:02d}"
    
    def process_text_with_emoji(self, text, font_name):
        """
        处理包含特殊字符的文本，为每种字符指定合适的字体
        
        Args:
            text (str): 原始文本
            font_name (str): 主要字体名称
        
        Returns:
            str: 处理后的ASS格式文本
        """
        result = ""
        i = 0
        while i < len(text):
            char = text[i]
            
            # 检查是否为特殊字符（emoji、符号等）
            if self.is_special_char(char):
                # 为特殊字符使用适合的字体
                special_font = self.get_special_char_font(char)
                result += f"{{\\fn{special_font}}}{char}{{\\fn{font_name}}}"
            else:
                result += char
            i += 1
        
        return result
    
    def is_special_char(self, char):
        """
        检查字符是否为特殊字符（emoji、符号等需要特殊字体处理）
        
        Args:
            char (str): 要检查的字符
        
        Returns:
            bool: 是否为特殊字符
        """
        code = ord(char)
        
        # emoji和特殊符号Unicode范围
        special_ranges = [
            # Emoji范围
            (0x1F600, 0x1F64F),  # 表情符号
            (0x1F300, 0x1F5FF),  # 杂项符号和象形文字
            (0x1F680, 0x1F6FF),  # 交通和地图符号
            (0x1F1E0, 0x1F1FF),  # 区域指示符号
            (0x1F900, 0x1F9FF),  # 补充符号和象形文字
            (0x1F018, 0x1F270),  # 各种符号
            
            # 其他特殊符号范围
            (0x2600, 0x26FF),    # 杂项符号
            (0x2700, 0x27BF),    # 装饰符号
            (0x2B00, 0x2BFF),    # 杂项符号和箭头
            (0x3200, 0x32FF),    # 带圈CJK字母和月份
            (0x3300, 0x33FF),    # CJK兼容性
            (0xFE00, 0xFE0F),    # 变体选择器
            (0xFF00, 0xFFEF),    # 半形和全形字符
            
            # 特殊标点和符号
            (0x2000, 0x206F),    # 一般标点
            (0x2070, 0x209F),    # 上标和下标
            (0x20A0, 0x20CF),    # 货币符号
            (0x20D0, 0x20FF),    # 组合变音符号
            (0x2100, 0x214F),    # 字母式符号
            (0x2150, 0x218F),    # 数字形式
            (0x2190, 0x21FF),    # 箭头
            (0x2200, 0x22FF),    # 数学运算符
            (0x2300, 0x23FF),    # 杂项技术符号
            (0x2400, 0x243F),    # 控制图像
            (0x2440, 0x245F),    # 光学字符识别
            (0x2460, 0x24FF),    # 带圈字母数字
            (0x2500, 0x257F),    # 制表符
            (0x2580, 0x259F),    # 块元素
            (0x25A0, 0x25FF),    # 几何图形
        ]
        
        for start, end in special_ranges:
            if start <= code <= end:
                return True
        
        # 检查Unicode分类
        cat = unicodedata.category(char)
        # So: 其他符号, Sm: 数学符号, Sk: 修饰符号, Sc: 货币符号
        return cat in ('So', 'Sm', 'Sk', 'Sc')
    
    def is_emoji(self, char):
        """
        检查字符是否为emoji（向后兼容）
        
        Args:
            char (str): 要检查的字符
        
        Returns:
            bool: 是否为emoji
        """
        return self.is_special_char(char)
    
    def get_special_char_font(self, char):
        """
        根据特殊字符类型获取合适的字体
        
        Args:
            char (str): 特殊字符
        
        Returns:
            str: 适合的字体名称
        """
        import platform
        system = platform.system()
        
        code = ord(char)
        
        # emoji字体
        if ((0x1F600 <= code <= 0x1F64F) or  # 表情符号
            (0x1F300 <= code <= 0x1F5FF) or  # 杂项符号和象形文字
            (0x1F680 <= code <= 0x1F6FF) or  # 交通和地图符号
            (0x1F900 <= code <= 0x1F9FF)):   # 补充符号和象形文字
            
            if system == "Windows":
                return "Segoe UI Emoji"
            elif system == "Darwin":  # macOS
                return "Apple Color Emoji"
            else:  # Linux
                return "Noto Color Emoji"
        
        # 数学和科学符号
        elif ((0x2200 <= code <= 0x22FF) or  # 数学运算符
              (0x2070 <= code <= 0x209F) or  # 上标和下标
              (0x2100 <= code <= 0x214F)):   # 字母式符号
            
            if system == "Windows":
                return "Segoe UI Symbol"
            elif system == "Darwin":
                return "Helvetica Neue"
            else:
                return "DejaVu Sans"
        
        # 其他特殊符号使用通用符号字体
        else:
            if system == "Windows":
                return "Segoe UI Symbol"
            elif system == "Darwin":
                return "SF Pro Display"
            else:
                return "Noto Sans Symbols"
    
    def get_emoji_font(self):
        """
        获取适合emoji的字体（向后兼容）
        
        Returns:
            str: emoji字体名称
        """
        import platform
        system = platform.system()
        
        if system == "Windows":
            return "Segoe UI Emoji"
        elif system == "Darwin":  # macOS
            return "Apple Color Emoji"
        else:  # Linux
            return "Noto Color Emoji"
    
    def clean_text(self, text):
        """
        清理文本，移除emoji（备用方案）
        
        Args:
            text (str): 原始文本
        
        Returns:
            str: 清理后的文本
        """
        # 移除emoji和其他图形字符
        cleaned_text = ""
        for char in text:
            if not self.is_emoji(char):
                cleaned_text += char
        
        return cleaned_text.strip()
    
    def calculate_display_length(self, text):
        """
        计算文字的显示长度（考虑emoji和ASS标签）
        
        Args:
            text (str): 原始文字
        
        Returns:
            int: 显示长度
        """
        # 计算真实可见字符数（不包含ASS格式标签）
        visible_chars = 0
        i = 0
        while i < len(text):
            char = text[i]
            
            # 跳过ASS格式标签（如果有的话）
            if char == '{' and i + 1 < len(text) and text[i + 1] == '\\':
                # 找到匹配的结束括号
                j = i + 2
                while j < len(text) and text[j] != '}':
                    j += 1
                i = j + 1 if j < len(text) else len(text)
                continue
            
            # 计算字符宽度
            if self.is_special_char(char):
                visible_chars += 2  # 特殊字符通常占2个字符宽度
            elif ord(char) > 127:  # 中文等寬字符
                visible_chars += 2
            else:  # ASCII字符
                visible_chars += 1
            
            i += 1
        
        return visible_chars
    
    def create_smooth_scroll(self, start_x, end_x, y_pos, duration, text, ass_color, start_time, style):
        """
        創建流暢滾動彈幕
        
        Args:
            start_x (int): 起始X位置
            end_x (int): 結束X位置  
            y_pos (int): Y位置
            duration (int): 持續時間
            text (str): 文本內容
            ass_color (str): 顏色
            start_time (str): 開始時間
            style (str): 樣式名稱
        
        Returns:
            str: 單個滾動事件
        """
        # 解析開始時間
        time_parts = start_time.split(':')
        start_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])
        
        # 標準實現：單個move事件
        end_seconds = start_seconds + duration
        end_time = self.format_time(end_seconds)
        
        segment_text = f"{{\\move({start_x},{y_pos},{end_x},{y_pos})\\c{ass_color}}}{text}"
        segment = f"Dialogue: 0,{start_time},{end_time},{style},,0,0,0,,{segment_text}"
        
        return segment
    
    def get_danmaku_position_style(self, position):
        """
        根据弹幕位置返回对应的ASS样式
        
        Args:
            position (int): 弹幕位置 (0=滚动, 1=顶部, 2=底部)
        
        Returns:
            str: ASS样式名称
        """
        position_map = {
            0: 'scroll',  # 滚动弹幕
            1: 'top',     # 顶部弹幕
            2: 'bottom'   # 底部弹幕
        }
        return position_map.get(position, 'scroll')
    
    def convert_to_ass(self, danmaku_data, output_file, time_offset=0, scroll_duration=12, fixed_duration=8, font_size=42, font_name="Noto Sans CJK TC", resolution="1920x1080", opacity=0.8, enable_scroll=True, enable_top=True, enable_bottom=True, filter_keywords=None, merge_file=None, filter_emoji=True):
        """
        将弹幕数据转换为ASS格式并保存到文件
        
        Args:
            danmaku_data (dict): 弹幕数据
            output_file (str): 输出文件路径
            time_offset (float): 时间偏移量（秒），正数表示延后，负数表示提前
            scroll_duration (int): 滚动弹幕显示时长（秒）
            fixed_duration (int): 固定弹幕显示时长（秒）
            font_size (int): 字体大小
            font_name (str): 字体名称
            resolution (str): 屏幕分辨率，格式为"宽x高"
            opacity (float): 弹幕不透明度（0.0-1.0）
            enable_scroll (bool): 是否显示滚动弹幕
            enable_top (bool): 是否显示顶部弹幕
            enable_bottom (bool): 是否显示底部弹幕
            filter_keywords (list): 过滤关键字列表
            merge_file (str): 要融合的现有ASS字幕文件路径
            filter_emoji (bool): 是否过滤emoji
        """
        if not danmaku_data or 'data' not in danmaku_data:
            print("錯誤: 沒有有效的彈幕資料")
            return False
        
        danmu_list = danmaku_data['data']['danmu']
        
        # 初始化过滤关键字
        if filter_keywords is None:
            filter_keywords = []
        
        # 解析分辨率
        try:
            width, height = map(int, resolution.split('x'))
        except ValueError:
            print(f"錯誤: 無效的分辨率格式 '{resolution}'，使用預設分辨率 1920x1080")
            width, height = 1920, 1080
        
        # 分析弹幕时间范围
        if danmu_list:
            times = [float(danmu.get('time', 0)) / 10.0 for danmu in danmu_list]
            min_time = min(times)
            max_time = max(times)
            print(f"彈幕時間範圍: {min_time}秒 到 {max_time}秒 (總時長: {max_time - min_time}秒)")
            
            # 如果最小时间不是0，询问是否需要调整
            if min_time > 60:  # 如果最小时间超过1分钟，可能需要调整
                print(f"檢測到彈幕起始時間為 {min_time}秒，可能需要時間偏移調整")
        
        # 计算不透明度（ASS格式使用16进制，&H00BBGGRR格式）
        alpha_value = int((1.0 - opacity) * 255)
        alpha_hex = f"{alpha_value:02X}"
        
        # ASS文件头部 - 优化超高帧率显示
        ass_header = f"""[Script Info]
!This file was created by AnimeFong Danmaku Converter
Title: AnimeFong Danmaku
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: {width}
PlayResY: {height}
Timer: 10.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: scroll,{font_name},{font_size},&H{alpha_hex}FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1
Style: top,{font_name},{font_size},&H{alpha_hex}FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,0,8,10,10,10,1
Style: bottom,{font_name},{font_size},&H{alpha_hex}FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        events = []
        
        filtered_count = 0
        for danmu in danmu_list:
            try:
                text = danmu.get('text', '').strip()
                if not text:
                    continue
                
                # 处理emoji文本
                if filter_emoji:
                    # 移除emoji（旧方案）
                    original_text = text
                    text = self.clean_text(text)
                    if not text:  # 如果清理后文本为空，跳过
                        filtered_count += 1
                        continue
                else:
                    # 保留emoji并为其指定合适字体（新方案）
                    text = self.process_text_with_emoji(text, font_name)
                
                # 确保正确获取时间戳 - API返回的时间单位是0.1秒
                time_raw = danmu.get('time', 0)
                if isinstance(time_raw, str):
                    time_sec = float(time_raw) / 10.0
                else:
                    time_sec = float(time_raw) / 10.0
                
                color = danmu.get('color', '#FFFFFF')
                position = int(danmu.get('position', 0))
                size = int(danmu.get('size', 1))
                
                # 根据位置类型过滤弹幕
                if position == 0 and not enable_scroll:  # 滚动弹幕
                    filtered_count += 1
                    continue
                elif position == 1 and not enable_top:  # 顶部弹幕
                    filtered_count += 1
                    continue
                elif position == 2 and not enable_bottom:  # 底部弹幕
                    filtered_count += 1
                    continue
                
                # 关键字过滤
                if filter_keywords:
                    should_filter = False
                    for keyword in filter_keywords:
                        if keyword in text:
                            should_filter = True
                            break
                    if should_filter:
                        filtered_count += 1
                        continue
                
                
                # 转换颜色格式从 #RRGGBB 到 &H00BBGGRR
                if color.startswith('#') and len(color) == 7:
                    r = color[1:3]
                    g = color[3:5]
                    b = color[5:7]
                    ass_color = f"&H00{b.upper()}{g.upper()}{r.upper()}"
                else:
                    ass_color = "&H00FFFFFF"  # 默认白色
                
                # 应用时间偏移
                adjusted_time = time_sec + time_offset
                start_time = self.format_time(adjusted_time)
                # 根据位置类型选择显示时长
                duration = scroll_duration if position == 0 else fixed_duration
                end_time = self.format_time(adjusted_time + duration)
                
                style = self.get_danmaku_position_style(position)
                
                # 构建弹幕文本，包含颜色信息
                ass_text = f"{{\\c{ass_color}}}{text}"
                
                # 添加滚动效果（仅对滚动弹幕）
                if position == 0:  # 滚动弹幕
                    # 根据弹幕长度动态调整起始位置，保证显示时间固定
                    display_length = self.calculate_display_length(text)
                    text_width = display_length * (font_size * 0.6)  # 估算文字宽度
                    
                    # 起始位置需要容纳整个文字，结束位置是文字完全离开屏幕
                    start_x = width + text_width + 50  # 文字完全在右侧外
                    end_x = -text_width - 50  # 文字完全在左侧外
                    
                    # 滚动弹幕使用整个屏幕高度范围（留一些边距避免裁切）
                    margin = font_size  # 上下边距
                    available_height = height - 2 * margin
                    y_pos = margin + (hash(danmu.get('text', '').strip()) % available_height)
                    
                    # 使用流畅滚动
                    scroll_event = self.create_smooth_scroll(
                        start_x, end_x, y_pos, duration, text, ass_color, start_time, style
                    )
                    events.append(scroll_event)
                else:
                    # 固定弹幕（顶部/底部）保持原有实现
                    event = f"Dialogue: 0,{start_time},{end_time},{style},,0,0,0,,{ass_text}"
                    events.append(event)
                
            except (ValueError, KeyError) as e:
                print(f"處理彈幕時出錯: {e}, 彈幕資料: {danmu}")
                continue
        
        # 处理融合或直接写入
        try:
            if merge_file and os.path.exists(merge_file):
                # 融合模式：将弹幕加入现有ASS文件
                print(f"正在融合彈幕到現有字幕檔案: {merge_file}")
                merged_content = merge_ass_files(merge_file, events)
                if merged_content:
                    with open(output_file, 'w', encoding='utf-8-sig') as f:
                        f.write(merged_content)
                    print(f"成功融合 {len(events)} 條彈幕到 {output_file}")
                else:
                    print("融合失敗，使用純彈幕模式")
                    with open(output_file, 'w', encoding='utf-8-sig') as f:
                        f.write(ass_header)
                        f.write('\n'.join(events))
                        f.write('\n')
                    print(f"成功轉換 {len(events)} 條彈幕到 {output_file}")
            else:
                # 纯弹幕模式
                if merge_file:
                    print(f"警告: 指定的融合檔案 {merge_file} 不存在，使用純彈幕模式")
                with open(output_file, 'w', encoding='utf-8-sig') as f:
                    f.write(ass_header)
                    f.write('\n'.join(events))
                    f.write('\n')
                print(f"成功轉換 {len(events)} 條彈幕到 {output_file}")
            
            if filtered_count > 0:
                print(f"已過濾 {filtered_count} 條彈幕")
            return True
            
        except IOError as e:
            print(f"寫入檔案時出錯: {e}")
            return False

def parse_video_url(url):
    """
    从动画疯视频URL中提取videoSn参数
    
    Args:
        url (str): 动画疯视频URL
    
    Returns:
        str: videoSn参数值，如果没找到返回None
    """
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # 检查URL参数中的sn参数（动画疯使用sn而不是videoSn）
        if 'sn' in query_params:
            return query_params['sn'][0]
        
        # 检查URL参数中的videoSn
        if 'videoSn' in query_params:
            return query_params['videoSn'][0]
        
        # 检查路径中的数字（可能的视频ID）
        path_numbers = re.findall(r'\d+', parsed.path)
        if path_numbers:
            return path_numbers[-1]  # 返回最后一个数字
        
        return None
    except Exception as e:
        print(f"解析URL時出錯: {e}")
        return None

def merge_ass_files(base_ass_file, danmaku_events):
    """
    融合现有ASS字幕文件与弹幕
    
    Args:
        base_ass_file (str): 现有ASS字幕文件路径
        danmaku_events (list): 弹幕事件列表
    
    Returns:
        str: 融合后的ASS内容
    """
    try:
        with open(base_ass_file, 'r', encoding='utf-8-sig') as f:
            base_content = f.read()
        
        # 分析ASS文件结构
        sections = {}
        current_section = None
        lines = base_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                current_section = line
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)
        
        # 将弹幕事件加入到Events区段
        if '[Events]' in sections:
            # 找到Format行
            format_line = None
            for line in sections['[Events]']:
                if line.startswith('Format:'):
                    format_line = line
                    break
            
            # 如果沒有Format行，添加標準格式
            if not format_line:
                sections['[Events]'].insert(0, 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')
            
            # 添加彈幕事件
            for event in danmaku_events:
                sections['[Events]'].append(event)
        else:
            # 如果沒有Events區段，創建一個
            sections['[Events]'] = [
                'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text'
            ] + danmaku_events
        
        # 重構ASS檔案
        merged_content = []
        for section_name, section_lines in sections.items():
            merged_content.append(section_name)
            merged_content.extend(section_lines)
            merged_content.append('')  # 空行分隔
        
        return '\n'.join(merged_content)
        
    except Exception as e:
        print(f"融合ASS檔案時出錯: {e}")
        return None

def load_config(config_file="config.json"):
    """載入配置檔案"""
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"載入配置檔案失敗: {e}")
    else:
        print(f"配置檔案 {config_file} 不存在，使用預設值")
    return None

def get_settings(config, preset_name=None):
    """獲取設定值"""
    # 預設值
    default_settings = {
        'geo': 'TW,HK',
        'scroll_duration': 12,
        'fixed_duration': 8,
        'font_size': 42,
        'font_name': 'Noto Sans CJK TC',
        'resolution': '1920x1080',
        'opacity': 0.8,
        'enable_scroll': True,
        'enable_top': True,
        'enable_bottom': True,
        'filter_keywords': [],
        'filter_emoji': False
    }
    
    if not config:
        return default_settings
    
    # 從配置檔案獲取預設值
    settings = {**default_settings, **config.get('default_settings', {})}
    
    # 如果指定了預設配置，套用預設配置
    if preset_name and 'presets' in config and preset_name in config['presets']:
        settings.update(config['presets'][preset_name])
        print(f"已套用預設配置: {preset_name}")
    
    return settings

def main():
    parser = argparse.ArgumentParser(description="將動畫瘋彈幕轉換為PotPlayer支援的ASS格式")
    parser.add_argument('video_sn', help="影片序列號或動畫瘋影片URL")
    parser.add_argument('-o', '--output', help="輸出檔案路徑", default="danmaku.ass")
    parser.add_argument('-t', '--time-offset', type=float, help="時間偏移量（秒），正數延後，負數提前", default=0)
    parser.add_argument('--preset', help="使用預設配置", choices=['720p', '1080p', '2k', '4k', '8k'])
    parser.add_argument('--config', help="指定配置檔案路徑", default="config.json")
    parser.add_argument('--merge', help="融合到現有ASS字幕檔案")
    
    args = parser.parse_args()
    
    # 加载配置文件
    config = load_config(args.config)
    
    # 获取设定值
    settings = get_settings(config, args.preset)
    
    # 检查输入是否为URL
    video_sn = args.video_sn
    if video_sn.startswith('http'):
        extracted_sn = parse_video_url(video_sn)
        if extracted_sn:
            video_sn = extracted_sn
            print(f"從URL中提取到影片序列號: {video_sn}")
        else:
            print("錯誤: 無法從URL中提取影片序列號")
            sys.exit(1)
    
    converter = AnimeFongDanmakuConverter()
    
    print(f"正在獲取影片 {video_sn} 的彈幕資料...")
    danmaku_data = converter.fetch_danmaku(video_sn, settings['geo'])
    
    if danmaku_data is None:
        print("獲取彈幕資料失敗")
        sys.exit(1)
    
    danmu_count = len(danmaku_data['data']['danmu']) if 'data' in danmaku_data and 'danmu' in danmaku_data['data'] else 0
    print(f"獲取到 {danmu_count} 條彈幕")
    
    if danmu_count == 0:
        print("沒有找到彈幕資料")
        sys.exit(1)
    
    print(f"正在轉換彈幕格式並儲存到 {args.output}...")
    if args.time_offset != 0:
        print(f"套用時間偏移: {args.time_offset}秒")
    
    success = converter.convert_to_ass(
        danmaku_data, 
        args.output, 
        args.time_offset,
        settings['scroll_duration'],
        settings['fixed_duration'],
        settings['font_size'],
        settings['font_name'],
        settings['resolution'],
        settings['opacity'],
        settings['enable_scroll'],
        settings['enable_top'],
        settings['enable_bottom'],
        settings['filter_keywords'],
        args.merge,
        settings['filter_emoji']
    )
    
    if success:
        print("轉換完成！")
        print(f"請將 {args.output} 檔案與影片檔案放在同一目錄下，PotPlayer會自動載入字幕。")
    else:
        print("轉換失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()