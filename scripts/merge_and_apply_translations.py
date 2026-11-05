# -*- coding: utf-8 -*-
"""
Merge all translations and inject quoteZh into masterpieces.js
"""
import json
import re
import sys

from translate_quotes import TRANSLATIONS as T1, clean_key
from complete_translations_dict import EXTRA_TRANSLATIONS as T2

def main():
    with open("quotes_all.json", "r", encoding="utf-8") as f:
        quotes = json.load(f)
        
    full_dict = {}
    full_dict.update(T1)
    full_dict.update(T2)
    
    clean_map = {clean_key(k): v for k, v in full_dict.items()}
    
    missing = []
    final_translations = {}
    
    for q in quotes:
        ck = clean_key(q)
        if ck in clean_map:
            final_translations[q] = f"“{clean_key(clean_map[ck])}”"
        else:
            # fuzzy fallback
            found = False
            for k, v in clean_map.items():
                if k in ck or ck in k:
                    final_translations[q] = f"“{clean_key(v)}”"
                    found = True
                    break
            if not found:
                missing.append(q)
                
    print(f"Total unique quotes: {len(quotes)}")
    print(f"Translated quotes: {len(final_translations)}")
    print(f"Missing count: {len(missing)}")
    if missing:
        for m in missing:
            print("STILL MISSING:", m)
        sys.exit(1)
        
    with open("data/quote_translations.json", "w", encoding="utf-8") as f:
        json.dump(final_translations, f, ensure_ascii=False, indent=2)
    print("Saved complete data/quote_translations.json (363/363 translated)!")
    
    # Now update data/masterpieces.js to add quoteZh to each masterpiece!
    with open("data/masterpieces.js", "r", encoding="utf-8") as f:
        content = f.read()
        
    # We want to insert `"quoteZh": "...",` right after `"quote": "...",`
    def replacer(match):
        full_line = match.group(1)
        q_val = match.group(2)
        zh = final_translations.get(q_val) or final_translations.get(f"“{clean_key(q_val)}”") or ""
        if not zh:
            ck = clean_key(q_val)
            zh = clean_map.get(ck, "")
            if zh:
                zh = f"“{clean_key(zh)}”"
        if not zh:
            print(f"Warning: no zh for {q_val}")
            return full_line
            
        # determine indent
        indent = match.group(0)[:match.group(0).find('"quote"')]
        return f'{full_line}\n{indent}"quoteZh": "{zh}",'
        
    # Check if quoteZh already exists
    if '"quoteZh":' in content:
        # remove old quoteZh first to avoid duplication
        content = re.sub(r'\n\s*"quoteZh":\s*"[^"]*",?', '', content)
        
    new_content = re.sub(r'(\s*"quote":\s*"([^"]+)",)', replacer, content)
    
    # Count how many quoteZh were added
    count_zh = len(re.findall(r'"quoteZh":', new_content))
    print(f"Added quoteZh to {count_zh} masterpieces (expected 420)!")
    assert count_zh == 420, f"Expected 420, got {count_zh}"
    
    with open("data/masterpieces.js", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully updated data/masterpieces.js with quoteZh for all 420 masterpieces!")

if __name__ == "__main__":
    main()
