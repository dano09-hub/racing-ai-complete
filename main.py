def scrape_tips():
    races = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get("https://tipmeerkat.com/latest-tips-picks", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')

        # TipMeerkat 2026 selector - look for tip cards or horse names
        tip_blocks = soup.find_all(['div', 'article', 'li'], class_=lambda x: x and ('tip' in x.lower() or 'pick' in x.lower() or 'selection' in x.lower() or 'horse' in x.lower()))
        if not tip_blocks:
            tip_blocks = soup.find_all(['p', 'span', 'a'], string=lambda t: t and any(word in t.lower() for word in ['horse', 'runner', 'tip', 'nap', '@', 'odds', 'to win']))

        for block in tip_blocks[:5]:
            horse = "Unknown Horse"
            odds = "TBD"

            # Extract horse name (try multiple patterns)
            horse_tag = block.find(['span', 'a', 'strong', 'h4'], class_=lambda x: x and ('horse' in x.lower() or 'runner' in x.lower() or 'name' in x.lower()))
            if horse_tag:
                horse = horse_tag.text.strip()
            else:
                text = block.text.strip()
                if ' to win' in text.lower():
                    horse = text.split(' to win')[0].strip()
                elif '@' in text:
                    horse = text.split('@')[0].strip()

            # Extract odds if present
            odds_tag = block.find(['span', 'strong'], string=lambda t: t and '@' in t)
            if odds_tag:
                odds = odds_tag.text.strip()

            if horse != "Unknown Horse" and len(horse) > 3:
                races.append({
                    "time": "TBD",
                    "track": "TipMeerkat",
                    "horse": horse,
                    "odds": odds,
                    "ai_score": 80,
                    "explanation": "Live scraped tip from TipMeerkat (crowd favourite)",
                    "highlighted": True
                })

        if not races:
            races.append({
                "horse": "No tips found",
                "odds": "N/A",
                "ai_score": 0,
                "explanation": "No matching horse names on TipMeerkat - page may be fully JS-loaded or selector needs update (2026 version)",
                "highlighted": False
            })
    except Exception as e:
        races.append({
            "horse": "Scraping Error",
            "odds": "N/A",
            "ai_score": 0,
            "explanation": str(e)[:150],
            "highlighted": False
        })

    return races
