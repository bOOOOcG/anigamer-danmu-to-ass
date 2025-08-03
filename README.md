# 動畫瘋彈幕轉ASS工具

將動畫瘋（ani.gamer.com.tw）的彈幕數據轉換為PotPlayer支援的ASS字幕格式。
這樣你就可以在使用第三方播放器(如potplayer)播放劇集時使用動畫瘋的彈幕了。

## 功能特點

- 支援從動畫瘋API獲取彈幕數據
- 支援彈幕顏色轉換
- 支援三種彈幕位置：滾動、頂部、底部
- 支援從影片URL直接提取影片序列號
- 生成標準ASS格式，相容PotPlayer和其他播放器
- 精確的時間軸同步（API時間單位為0.1秒）
- 智能emoji和特殊字符處理（自動字體切換）
- 支持ASS字幕文件融合功能
- 根據弹幕長度智能調整滾動速度

## 安裝

1. 確保已安裝Python 3.6+
2. 安裝依賴包：
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
# 使用影片序列號
python main.py 44224

# 指定輸出檔案
python main.py 44224 -o my_danmaku.ass

# 使用影片URL（自動提取序列號）
python main.py "https://ani.gamer.com.tw/animeVideo.php?sn=44224"

# 調整時間偏移（如果彈幕時間不同步）
python main.py 44224 -t -60 -o synced_danmaku.ass
```

### 命令列參數

- `video_sn`: 影片序列號或動畫瘋影片URL（必需）
- `-o, --output`: 輸出ASS檔案路徑（預設：danmaku.ass）
- `-t, --time-offset`: 時間偏移量（秒），正數延後，負數提前（預設：0）
- `--preset`: 使用預設配置（720p, 1080p, 2k, 4k, 8k）
- `--config`: 指定配置檔案路徑（預設：config.json）
- `--merge`: 融合到現有ASS字幕檔案

### 使用範例

```bash
# 基本轉換（使用預設1080p配置）
python main.py 44224

# 自訂輸出檔案名
python main.py 44224 -o "ave mujica episode1.ass"

# 從完整URL獲取彈幕
python main.py "https://ani.gamer.com.tw/animeVideo.php?sn=44224" -o episode1.ass

# 使用4K預設配置
python main.py 44224 --preset 4k

# 調整時間偏移（彈幕提前了60秒）
python main.py 44224 -t 60 -o synced_danmaku.ass

# 使用自訂配置檔案
python main.py 44224 --config my_config.json

# 融合彈幕到現有字幕檔案
python main.py 44224 --merge existing_subtitle.ass -o merged_output.ass
```

## 配置檔案

程式會讀取 `config.json` 配置檔案來設定字體、解析度、顯示時間等參數。

### 預設配置

- **720p**: 字體28px，適用於1280x720影片
- **1080p**: 字體42px，適用於1920x1080影片（預設）
- **2k**: 字體56px，適用於2560x1440影片
- **4k**: 字體84px，適用於3840x2160影片  
- **8k**: 字體168px，適用於7680x4320影片

### 自訂配置

可以編輯 `config.json` 檔案來調整：

```json
{
    "default_settings": {
        "geo": "TW,HK",
        "scroll_duration": 12,
        "fixed_duration": 8,
        "font_size": 42,
        "font_name": "Noto Sans CJK TC",
        "resolution": "1920x1080",
        "opacity": 0.8,
        "enable_scroll": true,
        "enable_top": true,
        "enable_bottom": true,
        "filter_keywords": [],
        "filter_emoji": false
    }
}
```

## 如何在PotPlayer中使用

1. 執行工具生成ASS字幕檔案
2. 將生成的`.ass`檔案與影片檔案放在同一目錄下
3. 確保字幕檔案名與影片檔案名相同（副檔名不同）
4. 開啟PotPlayer播放影片，字幕會自動載入
5. 如需手動載入：右鍵 → 字幕 → 載入字幕檔案

## 彈幕樣式說明

轉換後的ASS檔案包含三種彈幕樣式：

- **scroll**: 從右到左滾動的彈幕（預設）
- **top**: 顯示在螢幕頂部的固定彈幕
- **bottom**: 顯示在螢幕底部的固定彈幕

## 支援的彈幕特性

- [√] 文字內容
- [√] 顯示時間
- [√] 彈幕顏色
- [√] 彈幕位置（滾動/頂部/底部）
- [√] 滾動動畫效果
- [√] Emoji和特殊字符顯示
- [√] 字幕檔案融合
- [√] 彈幕過濾（關鍵字、類型）
- [√] 智能滾動速度調整

## 常見問題

### Q: 獲取彈幕失敗怎麼辦？
A: 檢查網路連線，確認影片序列號正確，某些地區可能需要VPN。

### Q: 生成的字幕檔案無法顯示中文？
A: 確保PotPlayer的字幕編碼設定為UTF-8。

### Q: 彈幕顯示位置不對？
A: 可以在PotPlayer中調整字幕位置和樣式設定。

### Q: 彈幕時間軸不同步？
A: 使用 `-t` 參數調整時間偏移，例如：`python main.py 44224 -t -60`

### Q: 支援其他播放器嗎？
A: 支援所有相容ASS格式的播放器，如VLC、MPV等。

## 技術細節

- 彈幕顯示時長：滾動彈幕12秒，固定彈幕8秒（可在config.json中調整）
- 預設解析度：1920x1080（支援720p到8K）
- 預設字體：Noto Sans CJK TC, 42px（根據解析度自動調整大小）
- 編碼：UTF-8 with BOM
- Timer精度：10.0000（標準ASS精度）
- 時間單位：API返回0.1秒，自動轉換為標準秒數
- 滾動算法：根據文字長度動態調整移動距離，保證固定顯示時間
- 字體處理：自動檢測emoji和特殊字符，智能切換合適字體

## 授權條款

MIT License

## 貢獻

歡迎提交Issue和Pull Request！

---

**免責聲明**: 本工具僅供學習交流使用，請遵守動畫瘋的使用條款。
