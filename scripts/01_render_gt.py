"""
Step B: 生成合成訓練圖（ground truth）

用法：
  python scripts/01_render_gt.py --overfit    # 200 張 overfit 測試
  python scripts/01_render_gt.py --full       # 完整訓練集

輸入：data/overfit_words.txt 或 data/wordlist.txt
輸出：data/gt_overfit/ 或 data/gt_train/（.tif + .gt.txt）
"""
import argparse, random, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "data/fonts/blizzardglobaltcunicode.ttf"

# D2R 官方 RGB → 灰階亮度
BRIGHTNESSES = [240, 99, 150, 230, 170, 200, 200]  # white,gray,blue,yellow,gold,green,orange

def render_one(name, font_size=16, brightness=200, shadow=(1,1), 
               blur=0, x_off=0, y_off=0):
    """渲染一個物品名稱，回傳灰階 PIL Image"""
    font = ImageFont.truetype(FONT_PATH, font_size)
    
    # 量測文字大小
    dummy = Image.new("L", (1, 1))
    bbox = ImageDraw.Draw(dummy).textbbox((0, 0), name, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # 建立圖片（黑底，高度固定）
    pad = 4
    img_w = tw + pad * 2 + abs(shadow[0]) + 2
    img_h = th + pad * 2 + abs(shadow[1]) + 2
    
    img = Image.new("L", (img_w, img_h), 0)
    draw = ImageDraw.Draw(img)
    
    x0 = pad + x_off
    y0 = pad + y_off - bbox[1]
    
    # 陰影
    if shadow != (0, 0):
        draw.text((x0+shadow[0], y0+shadow[1]), name, 
                  fill=int(brightness*0.15), font=font)
    
    # 文字
    draw.text((x0, y0), name, fill=brightness, font=font)
    
    # 模糊
    if blur > 0:
        from PIL import ImageFilter
        img = img.filter(ImageFilter.GaussianBlur(blur))
    
    return img


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--overfit", action="store_true", help="200 張 overfit 測試")
    parser.add_argument("--full", action="store_true", help="完整訓練集")
    parser.add_argument("--count", type=int, default=10, help="每個詞生成幾張（overfit 用）")
    args = parser.parse_args()
    
    if not Path(FONT_PATH).exists():
        print(f"❌ 找不到字體: {FONT_PATH}")
        print(f"   請把 d2r-pixelbot/data/fonts/blizzardglobaltcunicode.ttf 複製到 data/fonts/")
        return
    
    if args.overfit:
        words_file = Path("data/overfit_words.txt")
        out_dir = Path("data/gt_overfit")
        per_word = args.count
    elif args.full:
        words_file = Path("data/wordlist.txt")
        out_dir = Path("data/gt_train")
        per_word = 2  # base + 1 aug
    else:
        print("請指定 --overfit 或 --full")
        return
    
    words = [w.strip() for w in words_file.read_text(encoding="utf-8").splitlines() if w.strip()]
    out_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for word in words:
        for i in range(per_word):
            if i == 0:
                # Base: s16, 隨機亮度, sh1x1
                img = render_one(word, font_size=16, 
                                brightness=random.choice(BRIGHTNESSES),
                                shadow=(1,1))
            else:
                # Aug: 隨機變體
                img = render_one(word,
                                font_size=random.choice([15, 16, 17]),
                                brightness=random.choice(BRIGHTNESSES),
                                shadow=random.choice([(1,1), (0,0), (2,2)]),
                                blur=random.choice([0, 0, 0.3, 0.5]),
                                x_off=random.choice([-1, 0, 0, 1]),
                                y_off=random.choice([-1, 0, 0, 1]))
            
            fname = f"{count:06d}"
            img.save(out_dir / f"{fname}.tif")
            (out_dir / f"{fname}.gt.txt").write_text(word, encoding="utf-8")
            count += 1
    
    print(f"\n✅ 生成 {count} 張訓練圖")
    print(f"   目錄: {out_dir}")
    print(f"   詞數: {len(words)}")
    print(f"   每詞: {per_word} 張")
    print(f"\n   驗收：打開幾張 .tif 看看像不像遊戲掉落字！")

if __name__ == "__main__":
    main()
