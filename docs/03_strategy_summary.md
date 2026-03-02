# 策略總結與決策記錄（2026-03-01）

> Jones × GPT × Jarvis 三方討論的完整結論

## 今天的核心轉折

**早上：** Tesseract OCR 自訓練 → 失敗（BCER 82-97%）

**轉折點：** Jones 提出「遊戲只有 1860 種物品，是封閉集合，不會有 user input」
→ 問題本質從「OCR 逐字解碼」變成「封閉集合視覺匹配」

**傍晚：** CNN Embedding + Nearest Neighbor → Top-1 96.6%，門檻 0.88 零錯撿，30ms/張

## Phase 決策準則

### Phase 1：Prototype Embedding（✅ 已完成）
- 不需訓練，用 EasyOCR backbone 抽 feature
- 已通過 77 張真實 crop 驗證

### Phase 2：自訓練 Siamese / Metric Learning（⏸️ 待定）
**只在以下情況才做：**
1. 漏撿率太高（門檻降到 0.84 就開始錯撿 → feature 不夠分離）
2. 特定類別一直混淆（符文短字、形近字）
3. 跨環境變動崩壞（不同顯示器、不同 AA 設定）
4. 想擴充到交易視窗、倉庫等其他 UI

**如果真實測試沒碰到以上情況 → Phase 2 完全不用做**

### Phase 3-Lite：最小工程化（📋 下一步）
即使 Phase 1 夠用，也值得做 4 件事：
1. **Margin 門檻**：除了 score >= 0.88，加 top1-top2 margin 判斷
2. **小 crop 規則**：寬 < 35px 或高 < 15px → 一律 UNKNOWN
3. **金幣/火光保護**：白色 + OCR 含數字 → 強制 UNKNOWN
4. **疊字分割**：crop 高度 > 1.5× 平均 → 上下切割分別辨識

## 下一步流程

```
d2r-ocr-zhtw (研究引擎)          d2r-pixelbot (bot)
         ↓                              ↓
    已完成驗證               tools/ 寫測試腳本
         ↓                              ↓
                    Jones 手動丟物品到地上
                              ↓
                    搭配 d2r-loot-config
                              ↓
                    驗證：撿對? 漏撿? 速度? UNKNOWN?
                              ↓
                    通過 → 正式整合到 bot/
```

## GPT 的評語

> 「今天不是小突破。今天是整個架構轉向成功。
> 你從 OCR 認字走到 Embedding 封閉集合匹配，
> 這是一個質變級轉折。而且是 Jones 自己推導出來的。」
