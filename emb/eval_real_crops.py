"""
Phase 1 驗收：用真實 crop 測試 prototype embedding 的 top-k 命中率
"""
import easyocr, torch, numpy as np, json
from PIL import Image
from pathlib import Path

def get_model():
    reader = easyocr.Reader(['ch_tra', 'en'], gpu=False, verbose=False)
    model = reader.recognizer
    model.eval()
    return model

def extract_feature(model, img_path):
    img = Image.open(img_path).convert('L')
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

def main():
    model = get_model()
    
    # 載入 prototype 庫
    data = np.load("emb/artifacts/prototypes.npz")
    prototypes = data["prototypes"]
    id_map = json.load(open("emb/artifacts/id_map.json", encoding="utf-8"))
    print(f"Loaded {len(id_map)} prototypes, dim={prototypes.shape[1]}")
    
    # 載入真實 crop manifest（有正確答案的）
    manifest = json.load(open("data/real_crops/crops_manifest.json", encoding="utf-8"))
    
    crops_dir = Path("data/real_crops")
    results = []
    
    for entry in manifest:
        fname = entry.get("filename", "")
        label = entry.get("label", entry.get("name", ""))
        if not label or not fname:
            continue
        
        crop_path = crops_dir / fname
        if not crop_path.exists():
            continue
        
        feat = extract_feature(model, crop_path)
        
        # cosine similarity（已 L2 normalize，直接 dot product）
        sims = prototypes @ feat
        top_indices = np.argsort(sims)[::-1][:5]
        
        top5_names = [id_map[i] for i in top_indices]
        top5_scores = [sims[i] for i in top_indices]
        
        hit1 = label in top5_names[:1]
        hit5 = label in top5_names[:5]
        margin = top5_scores[0] - top5_scores[1]
        
        results.append({
            "file": fname, "label": label,
            "top1": top5_names[0], "score1": top5_scores[0],
            "hit1": hit1, "hit5": hit5, "margin": margin,
            "top5": list(zip(top5_names, [f"{s:.4f}" for s in top5_scores]))
        })
    
    # 統計
    total = len(results)
    if total == 0:
        print("❌ No labeled crops found in manifest!")
        return
    
    hit1_count = sum(1 for r in results if r["hit1"])
    hit5_count = sum(1 for r in results if r["hit5"])
    
    print(f"\n📊 Embedding 匹配結果（{total} 張真實 crop）")
    print(f"   Top-1 命中率: {hit1_count}/{total} = {hit1_count/total*100:.1f}%")
    print(f"   Top-5 命中率: {hit5_count}/{total} = {hit5_count/total*100:.1f}%")
    
    # 顯示詳細結果
    print(f"\n{'File':50s} {'Label':12s} {'Top-1':12s} {'Score':6s} {'✓':2s}")
    print("-" * 90)
    for r in results[:30]:
        mark = "✅" if r["hit1"] else ("🔶" if r["hit5"] else "❌")
        print(f"{r['file']:50s} {r['label']:12s} {r['top1']:12s} {r['score1']:.4f} {mark}")
    
    if total > 30:
        print(f"  ... ({total-30} more)")
    
    # 錯誤分析
    misses = [r for r in results if not r["hit1"]]
    if misses:
        print(f"\n❌ Top-1 錯誤分析（{len(misses)} 個）:")
        for r in misses[:10]:
            print(f"  {r['file']}")
            print(f"    正確: {r['label']}")
            print(f"    Top-5: {r['top5']}")

if __name__ == "__main__":
    main()
