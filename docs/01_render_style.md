# D2R 渲染參數校準結果

## 校準方法
用 D2R 官方字體 + 不同參數渲染「闊劍」→ 反向 template match 真實遊戲截圖。

## 最佳組合（template match 0.749）

| 參數 | 最佳值 | 說明 |
|------|--------|------|
| 字體 | blizzardglobaltcunicode.ttf | D2R 繁中專用 |
| 字號 | 16px（720p） | 對應遊戲 1280×720 解析度 |
| Hinting | none / normal | 兩者幾乎相同，都可用 |
| 陰影 | (1,1) | sh1x1，輕微陰影 |
| Bold | 關閉 | Bold 反而降分（0.749→0.542） |
| Kerning | 不用 | 地上掉落物不用 ReducedSpacing |
| Gamma | 可選 1.2 | 作為 augmentation |
| Outline | 0 | Outline 在黑底上無效 |

## 合成資料分佈建議

- Base 70%：s16 + hnone/hnormal + sh1x1
- Augmentation 20%：s15/s17 + xy±1 + blur 0.3-0.5 + gamma 1.2
- Crop 汙染 10%：左右加碎字噪音

## D2R 官方 RGB 色碼

| 顏色 | RGB | 用途 |
|------|-----|------|
| white | (240,240,240) | 普通物品 |
| gray | (99,99,99) | 帶孔/無形 |
| blue | (110,110,255) | 魔法 |
| yellow | (255,255,100) | 稀有 |
| gold | (199,179,119) | 暗金 |
| green | (0,252,0) | 套裝 |
| orange | (255,168,0) | 符文/手工 |
