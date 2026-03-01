"""
Step A: 從 D2R CASC 資料提取 wordlist 和 charset

用法：python scripts/00_extract_wordlist.py <casc_strings_dir>

輸入：data/casc_strings/ 目錄（含 item-names.json 等）
輸出：data/wordlist.txt, data/charset.txt
"""
import json, re, sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        casc_dir = Path("data/casc_strings")
    else:
        casc_dir = Path(sys.argv[1])
    
    if not casc_dir.exists():
        print(f"❌ 找不到 {casc_dir}")
        print(f"   請把 d2r-pixelbot/data/casc_strings/ 複製到 data/ 下")
        sys.exit(1)
    
    all_names = []
    for fname in ["item-names.json", "item-runes.json", "item-gems.json"]:
        p = casc_dir / fname
        if p.exists():
            d = json.load(open(p, encoding="utf-8-sig"))
            if isinstance(d, list):
                all_names.extend(x.get("zhTW","") for x in d if x.get("zhTW"))
            print(f"  ✅ {fname}: {len(d)} 條")
    
    names = sorted(set(n.strip() for n in all_names 
                       if n.strip() and re.search(r'[\u4e00-\u9fff]', n)))
    
    chars = set()
    for n in names:
        chars.update(n)
    chars = sorted(chars)
    
    cn = [c for c in chars if '\u4e00' <= c <= '\u9fff']
    other = [c for c in chars if not ('\u4e00' <= c <= '\u9fff')]
    
    out = Path("data")
    out.mkdir(exist_ok=True)
    (out / "wordlist.txt").write_text("\n".join(names), encoding="utf-8")
    (out / "charset.txt").write_text("\n".join(chars), encoding="utf-8")
    
    print(f"\n📊 結果:")
    print(f"  物品名: {len(names)} 個 → data/wordlist.txt")
    print(f"  字元集: {len(chars)} 個（中文 {len(cn)} + 其他 {len(other)}）→ data/charset.txt")
    print(f"  其他字元: {other}")
    print(f"\n✅ Step A 完成！")
    print(f"   驗收：打開 data/charset.txt 確認裡面都是中文字")

if __name__ == "__main__":
    main()
