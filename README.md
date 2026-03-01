# D2R 繁體中文 OCR 訓練

> 專門為《暗黑破壞神 II：獄火重生》繁中版掉落物品文字辨識而訓練的 Tesseract OCR 模型。

## 目標

輸入：單個物品名稱的 contour crop 圖片（來自遊戲截圖 HSV 分色，1280×720）
輸出：物品名稱文字（或拒答）

## 核心依賴

合成訓練圖使用校準過的渲染參數：`ft_s16 + hnone/hnormal + sh1x1 (+ gamma 1.2)`
校準方法與完整參數見 `docs/01_render_style.md`

## 訓練環境

- **訓練**在 macOS / Linux 跑（tesstrain + training tools 更穩定）
- **Windows** 端負責收集 `real_crops` 與最終推論整合
- Python 3.9+
- Tesseract 5.x（含訓練工具：lstmtraining, combine_tessdata）
- Pillow
- tesstrain（`git clone https://github.com/tesseract-ocr/tesstrain.git`）

## 訓練流程（關卡式）

| 關卡 | 做什麼 | 成功條件 |
|------|--------|----------|
| Step A | 提取 wordlist + charset | `charset.txt` 含 1245 個字元（中文 1238 + 標點/符號 7）。統計方法：從 item-names/runes/gems.json 的 zhTW 欄位提取所有唯一字元，含 `：/‧（）` 等遊戲內標點，不含數字和 ASCII 字母。 |
| Step B | 生成 200 張合成訓練圖（overfit） | ① 肉眼看 10 張覺得像遊戲字 ② 用 `chi_tra` 跑這 200 張，baseline 正確率 >80% |
| Step C | Overfit 測試 | 200 張訓練後讀對 >95%。⚠️ 這是驗證訓練管線正確，不代表真實 crop 也會 95%。 |
| Step D | 擴大到 3k 張 + augmentation | 在 `data/real_crops/` 固定測試集上：2-3 字詞 top-1 正確率（或 edit distance ≤1 的比例）較 chi_tra baseline 提升 ≥15%；噪音 crop 的 reject rate 維持 >80% |
| Step E | 整合到 bot | JSON loot filter 端到端工作 |

## 目錄結構

```
data/
  wordlist.txt          # 1860 個物品名（每行一個）
  charset.txt           # 1245 個字元（模型允許輸出的字）
  overfit_words.txt     # 20 個代表詞（overfit 測試用）
  casc_strings/         # D2R CASC 原始資料（item-names/runes/gems.json）
  fonts/                # D2R 官方字體（blizzardglobaltcunicode.ttf）
  gt_overfit/           # 200 張 overfit 圖 + .gt.txt（gitignored）
  gt_train/             # 正式訓練集（gitignored）
  gt_eval/              # 驗證集（gitignored）
  real_crops/           # 真實遊戲 contour crop（來自 5080）
scripts/
  00_extract_wordlist.py    # Step A: 提取 wordlist + charset
  01_render_gt.py           # Step B: 生成合成訓練圖
  02_train.sh               # Step C: 呼叫 tesstrain（待建）
  03_eval_real.py           # Step D: 用真實 crop 評估（待建）
docs/
  00_concepts.md        # 核心概念（人話版）
  01_render_style.md    # 渲染參數校準結果
```
