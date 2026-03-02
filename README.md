# D2R 繁中物品辨識引擎

> 《暗黑破壞神 II：獄火重生》繁中版掉落物品辨識系統
> 方法：CNN Embedding + Nearest Neighbor（封閉集合匹配）

## 🎯 一句話說明

用 EasyOCR 的 CNN backbone 把每個物品 crop 轉成向量，在 1874 個已知物品名的向量庫裡找最像的。
**不是 OCR（逐字解碼），是視覺指紋匹配。**

## 📊 當前成果（2026-03-01）

| 指標 | 數值 |
|------|------|
| Top-1 命中率 | **96.6%**（56/58 張真實 crop） |
| 門檻 0.88 後錯撿率 | **0%** |
| 推論速度 | **~30ms/張**（CPU, Mac mini M-series） |
| Prototype 數量 | 1874 個物品名 |
| Embedding 維度 | 1536 |

### 錯誤分析（2/58）
1. `特等的攏煙之球` → 帶魔法前綴的長名超出 prototype 覆蓋（score 0.857）
2. `符文：烏姆 + 藍姆` → 兩行符文疊在同一個 contour（score 0.812）

兩個錯誤都在門檻 0.88 以下，設門檻後 **零錯撿**。

## 🏗️ 系統架構

```
遊戲截圖 (1280×720)
    ↓
HSV 分色 → contour 偵測（座標已知）
    ↓
每個 contour 裁切成 crop（小圖）
    ↓
crop → EasyOCR CNN backbone → 1536 維向量
    ↓
cosine similarity → 1874 個 prototype 比對
    ↓
score >= 0.88 ? → 回傳物品名 → loot_filter.json 決策
score < 0.88  ? → UNKNOWN → 跳過不撿
```

### 為什麼不用 OCR？

| | OCR（Tesseract/EasyOCR 文字模式） | Embedding + NN |
|---|---|---|
| 本質 | 逐字解碼（開放詞彙） | 封閉集合分類 |
| 會輸出不存在的物品名？ | ✅ 會（「閉劍」「己矢」） | ❌ 不會 |
| 中文訓練難度 | 極高（1245 字 × 形近字） | 不需要訓練 |
| 速度 | 300-500ms/張 | 30ms/張 |
| 適合封閉集合？ | 不適合 | 天然適合 |

### 為什麼不用 Tesseract 自訓練？

我們嘗試過，記錄在 `docs/02_tesseract_postmortem.md`：
- Fine-tune chi_tra: BCER 93-97%（越訓越差）
- 從零訓練 10000 輪: BCER 82%（收斂停滯）
- 根因：中文 1245 字需要幾萬張圖 + 幾萬輪，工程成本遠超收益

## 📁 目錄結構

```
d2r-ocr-zhtw/
├── README.md                          # ← 你在這裡
├── requirements.txt
├── data/
│   ├── wordlist.txt                   # 1860 個繁中物品名（每行一個）
│   ├── charset.txt                    # 1245 個字元集
│   ├── overfit_words.txt              # 20 個 overfit 測試詞
│   ├── casc_strings/                  # D2R CASC 原始資料
│   │   ├── item-names.json
│   │   ├── item-runes.json
│   │   └── item-gems.json
│   ├── fonts/
│   │   └── blizzardglobaltcunicode.ttf  # D2R 官方繁中字體
│   ├── gt_overfit/                    # 200 張合成訓練圖（Tesseract 用，已不需要）
│   └── real_crops/                    # 77 張真實遊戲 contour crop + 標註
│       ├── *.png                      # 真實 crop 圖片
│       ├── crops_manifest.json        # crop 元資料（顏色、座標、大小）
│       └── pre_labels.json            # 人工標註結果（Jones 2026-03-01）
├── emb/                               # Embedding 引擎（主線）
│   ├── build_prototypes.py            # 生成 1874 個 prototype 向量庫
│   ├── eval_real_crops.py             # 用真實 crop 評估 top-k 命中率
│   └── artifacts/
│       ├── prototypes.npz             # 1874×1536 prototype 矩陣
│       └── id_map.json                # index → 物品名 映射
├── scripts/                           # 資料工具
│   ├── 00_extract_wordlist.py         # 提取 wordlist + charset
│   └── 01_render_gt.py                # 生成合成訓練圖
└── docs/
    ├── 00_concepts.md                 # 核心概念（人話版）
    ├── 01_render_style.md             # 渲染參數校準結果
    └── 02_tesseract_postmortem.md     # Tesseract 失敗記錄
```

## 🔧 關鍵檔案說明

### `emb/build_prototypes.py`
- 載入 EasyOCR recognizer（`ch_tra` + `en`，CPU 模式）
- 對 1874 個物品名各渲染 5 種變體（不同字號/亮度/陰影）
- 取 CNN FeatureExtraction 層輸出 → AdaptiveAvgPool → 展平為 1536 維
- 對每個物品名取 5 變體的平均向量作為 prototype
- 輸出：`prototypes.npz` + `id_map.json`

### `emb/eval_real_crops.py`
- 載入 prototype 庫
- 對 `data/real_crops/` 的每張 crop 提取 embedding
- 計算 cosine similarity → 報告 Top-1/Top-5 命中率

### `data/real_crops/pre_labels.json`
- Jones 人工標註的 77 張真實 crop
- 每筆包含：`auto_label`（機器預標）、`human_label`（Jones 確認）、`emb_score`
- 58 張有物品名，19 張 UNKNOWN（金幣/火光/碎片）

## 🚀 下一步計畫

### Phase 1：在 d2r-pixelbot 中做測試腳本（優先）
- **不直接整合到 bot 主流程**
- 在 `d2r-pixelbot/tools/` 寫測試腳本：
  - Jones 手動丟物品到地上
  - 腳本截圖 → contour → crop → embedding → 匹配 → 顯示結果
  - 搭配 `d2r-loot-config/loot_filter.json` 測試撿拾決策
- 目標：驗證「真實遊戲場景中的端到端效果」

### Phase 2：三個已知優化項
1. **前綴覆蓋**：prototype 加入「特等的/優質的 + 基礎名」變體，提高帶前綴物品的命中率
2. **雙行切割**：crop 高度 > 1.5× 平均時，上下切割分別辨識
3. **金幣規則保護**：白色 + 數字特徵 → 強制 UNKNOWN

### Phase 3：正式整合到 bot
- 確認 Phase 1 測試通過後，替換現有的顏色-only 撿拾邏輯
- embedding 引擎作為 `bot/item_identifier.py` 模組

### 未來研究（可選）
- **Phase 2 Siamese/Metric Learning**：用 5080 GPU 自訓練專用 embedding（如果 Phase 1 精度不夠）
- **符文專用子庫**：橘色 contour 只在符文清單中比對，提高短名辨識率
- **crop 放大重採樣**：小圖 2× upscale 後再送 embedding

## 🔑 環境需求

```bash
pip install easyocr pillow numpy torch
```

- Python 3.9+
- CPU 即可（不需要 GPU）
- EasyOCR 會自動下載 `ch_tra` + `en` 模型（~100MB）

## 📝 開發歷史

| 日期 | 事件 |
|------|------|
| 2026-03-01 上午 | Tesseract fine-tune chi_tra 失敗（BCER 93%） |
| 2026-03-01 中午 | Tesseract 從零訓練失敗（BCER 82%，10000 輪收斂停滯） |
| 2026-03-01 下午 | 與 GPT 討論 → 轉向 CNN Embedding + NN |
| 2026-03-01 傍晚 | Phase 1 prototype 建庫完成 → 合成圖 100%、真實 crop 96.6% |
| 2026-03-01 晚上 | Jones 人工標註 77 張 → 門檻 0.88 零錯撿 → **驗證成功** |

## 🔗 相關 Repo

- [`d2r-pixelbot`](https://github.com/jonesandjay123/d2r-pixelbot) — Bot 主 repo（整合目標）
- [`d2r-loot-config`](https://github.com/jonesandjay123/d2r-loot-config) — 撿拾規則 JSON（手機遠端控制）
