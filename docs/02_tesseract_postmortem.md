# Tesseract 自訓練失敗記錄（Postmortem）

> 2026-03-01，完整記錄 Tesseract 路線的嘗試與失敗原因。

## 嘗試 1：Fine-tune chi_tra（通用繁中模型）

**方法：** 用 D2R 字體渲染 14916 張合成圖，fine-tune `chi_tra` 的 LSTM

**結果：** BCER 93-97%（越訓越差）

**失敗原因：**
- chi_tra 的 unicharset 缺少 D2R 專用字（劊、鬃、慟、椏、弒等）
- 含這些字的 ground truth 被跳過（skip ratio 2-4%）
- 訓練圖高度 22-26px，Tesseract LSTM 期望 48px
- unicharset / traineddata / ground truth 三者不對齊 → 模型學錯字典

## 嘗試 2：Fine-tune chi_tra（48px 高度 v2）

**方法：** 圖片高度改為 48px，用 tessdata_best float 模型

**結果：** BCER 94%，比 v1 更差

**失敗原因：** 根本問題未解（unicharset 不對齊），放大圖片無幫助

## 嘗試 3：從零訓練（tesstrain + 200 張 overfit）

**方法：** 不基於任何模型，用 tesstrain Makefile 從零訓練

**結果：** 2000 輪 BCER 90% → 10000 輪 BCER 82%（收斂停滯）

**失敗原因：**
- 200 張只涵蓋 53 個不同字元
- 中文 1245 字需要每個字至少出現 50-100 次
- 估計需要 6 萬+ 張圖 + 數天訓練時間
- 對比英文（26 字母），中文複雜度高 18 倍

## 結論

Tesseract 自訓練繁中 OCR 的工程成本遠超收益：
- 需要幾萬張圖、幾天訓練
- 即使訓練成功，仍會輸出不存在的物品名組合
- 不適合「封閉集合匹配」這個本質問題

**轉向 CNN Embedding + Nearest Neighbor：不需要訓練，Top-1 96.6%，30ms/張。**
