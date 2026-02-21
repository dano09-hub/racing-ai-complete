def scrape_tips():
    races = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get("https://gg.co.uk/tips/today/", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')

        # More precise: look for tip containers or text with horse/odds patterns
        tip_containers = soup.find_all(['div', 'section', 'article'], class_=lambda x: x and ('tip' in x.lower() or 'selection' in x.lower() or 'bet' in x.lower()))
        if not tip_containers:
            tip_containers = soup.find_all('div', recursive=True)  # fallback broad search

        for container in tip_containers[:5]:
            # Clean text - remove style/script tags
            for tag in container.find_all(['style', 'script']):
                tag.decompose()
            text = container.get_text(separator=' ', strip=True)

            # Extract horse-like phrase (e.g. "Horse Name @ 5/1")
            if '@' in text or ' to win' in text.lower() or 'tip' in text.lower():
                parts = text.split('@') if '@' in text else text.split(' to win')
                horse_part = parts[0].strip()[-30:]  # take last part before @
                horse = horse_part.split()[-2:] if len(horse_part.split()) > 1 else horse_part
                horse = ' '.join(horse) if isinstance(horse, list) else horse
                odds = parts[1].strip()[:10] if len(parts) > 1 else "TBD"

                races.append({
                    "time": "TBD",
                    "track": "GG Tips",
                    "horse": horse or "Unknown Horse",
                    "odds": odds,
                    "ai_score": 80,
                    "explanation": "Live scraped tip from GG.co.uk (cleaned text match)",
                    "highlighted": True
                })

        if not races:
            races.append({
                "horse": "No tips found",
                "odds": "N/A",
                "ai_score": 0,
                "explanation": "No horse/odds patterns on GG - page is JS-heavy or content blocked (2026 version)",
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
