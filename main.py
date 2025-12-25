import requests
import os
from datetime import datetime

def get_epic_free_games():
    # رابط الـ API الخاص بمتجر Epic Games
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=DZ&allowCountries=DZ"
    try:
        response = requests.get(url)
        data = response.json()
        games = data['data']['Catalog']['searchStore']['elements']
        
        free_games_list = []
        for game in games:
            # التأكد أن اللعبة مجانية حالياً
            price = game.get('price', {}).get('totalPrice', {}).get('discountPrice', -1)
            if price == 0:
                title = game.get('title', 'Unknown Title')
                desc = game.get('description', 'No description available.')
                image = game.get('keyImages', [{}])[0].get('url', '')
                
                # إنشاء رابط الصفحة المباشر
                product_slug = game.get('productSlug') or game.get('catalogNs', {}).get('mappings', [{}])[0].get('pageSlug', '')
                game_url = f"https://store.epicgames.com/en-US/p/{product_slug}"
                
                # جلب تاريخ انتهاء العرض
                try:
                    end_date_raw = game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['endDate']
                    end_date = datetime.strptime(end_date_raw, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
                except:
                    end_date = "غير محدد"
                
                free_games_list.append({
                    "title": title, "desc": desc, "image": image, "url": game_url, "expire": end_date
                })
        return free_games_list
    except Exception as e:
        print(f"Error: {e}")
        return []

def send_to_discord(games):
    # هنا نقوم بجلب الرابط من إعدادات GitHub Secrets
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    
    if not webhook_url:
        print("Error: Webhook URL not found in environment variables!")
        return

    for game in games:
        payload = {
            "username": "Epic Hunter Pro",
            "embeds": [{
                "title": f"🎁 لعبة مجانية جديدة: {game['title']}",
                "description": f"{game['desc']}\n\n⏳ **ينتهي العرض في:** {game['expire']}",
                "url": game['url'],
                "color": 0x000000,
                "image": {"url": game['image']},
                "footer": {"text": "برمجة يونس الهاكر 🛠️"}
            }]
        }
        requests.post(webhook_url, json=payload)

# تشغيل السكريبت
if __name__ == "__main__":
    games = get_epic_free_games()
    send_to_discord(games)
