# D2R 繁體中文 OCR 訓練

> 專門為《暗黑破壞神 II：獄火重生》繁中版掉落物品文字辨識而訓練的 Tesseract OCR 模型。

## 目標

輸入：單個物品名稱的 contour crop 圖片（來自遊戲截圖 HSV 分色）
輸出：物品名稱文字（或拒答）

## 訓練流程（關卡式）

| 關卡 | 做什麼 | 成功條件 |
|------|--------|----------|
| Step A | 提取 wordlist + charset | charset.txt 含 ~1245 個字 |
| Step B | 生成合成訓練圖（200 張 overfit） | 肉眼看 10 張覺得像遊戲字 |
| Step C | Overfit 測試 | 200 張讀對 >95% |
| Step D | 擴大到 3k 張 + augmentation | 真實 crop 短字錯誤率下降 |
| Step E | 整合到 bot | JSON loot filter 工作 |

## 目錄結構

```
data/
  wordlist.txt          # 1860 個物品名（每行一個）
  charset.txt           # 1245 個字元（模型允許輸出的字）
  overfit_words.txt     # 20 個代表詞（overfit 測試用）
  gt_overfit/           # 200 張 overfit 圖 + .gt.txt
  gt_train/             # 正式訓練集（Step D）
  gt_eval/              # 驗證集
  real_crops/           # 真實遊戲 contour crop
  fonts/                # D2R 官方字體
scripts/
  00_extract_wordlist.py
  01_render_gt.py       # 生成合成訓練圖
  02_train.sh           # 呼叫 tesstrain
  03_eval_real.py       # 用真實 crop 評估
docs/
  00_concepts.md        # 核心概念（人話版）
  01_render_style.md    # 渲染參數校準結果
```

## 環境需求

- Python 3.9+
- Tesseract 5.x（含訓練工具：lstmtraining, combine_tessdata）
- Pillow
- tesstrain（git clone https://github.com/tesseract-ocr/tesstrain.git）
