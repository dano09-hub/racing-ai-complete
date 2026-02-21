def scrape_tips():
    races = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get("https://gg.co.uk/tips/today/", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')

        # 2026 GG tips page - broader selectors to catch tips
        tip_blocks = soup.find_all(['div', 'article', 'li'], attrs={"class": lambda x: x and ('tip' in x or 'bet' in x or 'selection' in x or 'horse' in x)})
        if not tip_blocks:
            tip_blocks = soup.find_all(['a', 'span', 'p'], string=lambda t: t and ('horse' in t.lower() or 'tip' in t.lower() or '@' in t))

        for block in tip_blocks[:5]:  # limit to 5 for speed
            horse = "Unknown Horse"
            odds = "TBD"

            # Try multiple ways to find horse name
            horse_tag = block.find(['span', 'a', 'h3', 'strong'], attrs={"class": lambda x: x and ('horse' in x.lower() or 'runner' in x.lower() or 'name' in x.lower())})
            if horse_tag:
                horse = horse_tag.text.strip()
            else:
                text = block.text.strip()
                if 'on ' in text or '@' in text or 'to win' in text.lower():
                    horse = text.split('on ')[0] or text.split('@')[0].strip()[:50]

            # Try to find odds
            odds_tag = block.find(['span', 'strong'], attrs={"class": lambda x: x and ('odds' in x.lower() or 'price' in x.lower() or '@' in x)})
            if odds_tag:
                odds = odds_tag.text.strip()

            if horse != "Unknown Horse":
                races.append({
                    "time": "TBD",
                    "track": "GG Tips",
                    "horse": horse,
                    "odds": odds,
                    "ai_score": 80,
                    "explanation": "Live scraped tip from GG.co.uk (2026 page)",
                    "highlighted": True
                })

        if not races:
            races.append({
                "horse": "No tips found",
                "odds": "N/A",
                "ai_score": 0,
                "explanation": "No matching tips on GG - selector may need update (page may be JS-loaded)",
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
