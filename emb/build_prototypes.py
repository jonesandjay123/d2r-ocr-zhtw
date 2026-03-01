"""
Phase 1: 建立 1860 個物品名的 prototype embedding 向量庫
用 EasyOCR recognizer backbone 的 CNN feature 作為 embedding
"""
import easyocr, torch, numpy as np, json
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

FONT_PATH = "data/fonts/blizzardglobaltcunicode.ttf"

def get_model():
    reader = easyocr.Reader(['ch_tra', 'en'], gpu=False, verbose=False)
    model = reader.recognizer
    model.eval()
    return model

def extract_feature(model, img):
    """從 PIL Image 提取 feature embedding"""
    img = img.convert('L')
    h = 64
    w = max(1, int(img.width * h / img.height))
    img = img.resize((w, h))
    arr = np.array(img, dtype=np.float32) / 255.0
    tensor = torch.FloatTensor(arr).unsqueeze(0).unsqueeze(0)
    with torch.no_grad():
        visual = model.FeatureExtraction(tensor)
        visual = model.AdaptiveAvgPool(visual)
        feat = visual.squeeze().reshape(-1).numpy()
    feat = feat / (np.linalg.norm(feat) + 1e-8)
    return feat

def render_name(name, font_size=16, brightness=200, shadow=(1,1)):
    font = ImageFont.truetype(FONT_PATH, font_size)
    dummy = Image.new("L", (1, 1))
    bbox = ImageDraw.Draw(dummy).textbbox((0, 0), name, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    pad = 4
    img_w = tw + pad*2 + abs(shadow[0]) + 2
    img_h = th + pad*2 + abs(shadow[1]) + 2
    img = Image.new("L", (img_w, img_h), 0)
    draw = ImageDraw.Draw(img)
    x0, y0 = pad, pad - bbox[1]
    if shadow != (0,0):
        draw.text((x0+shadow[0], y0+shadow[1]), name, fill=int(brightness*0.15), font=font)
    draw.text((x0, y0), name, fill=brightness, font=font)
    return img

VARIANTS = [
    {"font_size": 16, "brightness": 240, "shadow": (1,1)},
    {"font_size": 15, "brightness": 200, "shadow": (1,1)},
    {"font_size": 17, "brightness": 170, "shadow": (1,1)},
    {"font_size": 16, "brightness": 99,  "shadow": (1,1)},
    {"font_size": 16, "brightness": 230, "shadow": (0,0)},
]

def main():
    model = get_model()
    wordlist = [w.strip() for w in open("data/wordlist.txt", encoding="utf-8") if w.strip()]
    print(f"Building prototypes for {len(wordlist)} items with {len(VARIANTS)} variants each...")
    
    prototypes = []
    id_map = []
    
    for i, word in enumerate(wordlist):
        feats = []
        for v in VARIANTS:
            img = render_name(word, **v)
            feat = extract_feature(model, img)
            feats.append(feat)
        proto = np.mean(feats, axis=0)
        proto = proto / (np.linalg.norm(proto) + 1e-8)
        prototypes.append(proto)
        id_map.append(word)
        if (i+1) % 200 == 0:
            print(f"  {i+1}/{len(wordlist)}")
    
    prototypes = np.array(prototypes)
    
    out = Path("emb/artifacts")
    out.mkdir(parents=True, exist_ok=True)
    np.savez(str(out / "prototypes.npz"), prototypes=prototypes)
    json.dump(id_map, open(str(out / "id_map.json"), "w", encoding="utf-8"), ensure_ascii=False)
    
    print(f"\n✅ Prototype matrix: {prototypes.shape}")
    print(f"✅ Saved to emb/artifacts/")

if __name__ == "__main__":
    main()
