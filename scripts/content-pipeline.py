#!/usr/bin/env python3
"""
PNW Outdoor Adventures - Content Pipeline
Automatiza: Research → Writing → Image → Publish → Deploy
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Config
REPO_DIR = os.path.expanduser("~/github-repo/pnwoutdooradventures")
CALENDAR_PATH = os.path.join(REPO_DIR, "keyword-research/calendar.json")
PAGES_DIR = os.path.join(REPO_DIR, "src/pages/blog")
IMAGES_DIR = os.path.join(REPO_DIR, "public/images/blog")

# Ensure directories exist
os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def load_calendar():
    """Load content calendar"""
    with open(CALENDAR_PATH, 'r') as f:
        return json.load(f)

def save_calendar(calendar):
    """Save updated calendar"""
    with open(CALENDAR_PATH, 'w') as f:
        json.dump(calendar, f, indent=2)

def get_next_article(calendar):
    """Get next unplanned article from calendar"""
    for article in calendar.get("articles", []):
        if article.get("status") == "planned":
            return article
    return None

def check_keyword_research_needed(article):
    """Check if keyword research is needed"""
    # If volume < 100 or SEO difficulty unknown, research needed
    volume = article.get("volume", 0)
    seo = article.get("seo_difficulty", 99)
    return volume < 100 or seo == 99

def research_keyword(keyword, article=None):
    """Research keyword data from calendar or API.
    
    Uses real data from the content calendar (volume, seo_difficulty)
    which was sourced from Ubersuggest + DataForSEO. If an API key
    is available in the environment, a live API call can be added here.
    """
    print(f"  📊 Researching keyword: {keyword}")
    
    # Check for API keys (DataForSEO, Ubersuggest, etc.)
    dataforseo_user = os.environ.get("DATAFORSEO_LOGIN")
    dataforseo_pass = os.environ.get("DATAFORSEO_PASSWORD")
    
    if dataforseo_user and dataforseo_pass:
        print("  → Using live DataForSEO API")
        return _research_via_dataforseo(keyword, dataforseo_user, dataforseo_pass)
    
    # Fall back to calendar data (already researched via Ubersuggest + DataForSEO)
    if article:
        volume = article.get("volume", 0)
        seo_difficulty = article.get("seo_difficulty", 99)
        print(f"  → Using calendar data: volume={volume}, SEO difficulty={seo_difficulty}")
        return {
            "keyword": keyword,
            "volume": volume,
            "seo_difficulty": seo_difficulty,
            "search_intent": article.get("search_intent", "informational"),
            "cluster": article.get("cluster", ""),
            "source": "calendar (pre-researched)"
        }
    
    # Minimal fallback
    print(f"  → No article data available for '{keyword}'")
    return {
        "keyword": keyword,
        "volume": 0,
        "seo_difficulty": 99,
        "source": "unknown"
    }

def _research_via_dataforseo(keyword, login, password):
    """Call DataForSEO API for live keyword data (requires API keys)."""
    import urllib.request
    import base64
    
    url = "https://api.dataforseo.com/v3/serp/google/keyword_overview/live"
    creds = base64.b64encode(f"{login}:{password}".encode()).decode()
    payload = json.dumps([{
        "keyword": keyword,
        "location_code": 2840,  # United States
        "language_code": "en"
    }]).encode()
    
    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/json"
    })
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            tasks = data.get("tasks", [{}])[0].get("result", [{}])[0]
            return {
                "keyword": keyword,
                "volume": tasks.get("search_volume", 0),
                "seo_difficulty": tasks.get("keyword_difficulty", 99),
                "source": "DataForSEO API"
            }
    except Exception as e:
        print(f"  ⚠️ DataForSEO API error: {e}")
        return {"keyword": keyword, "volume": 0, "seo_difficulty": 99, "source": "API error"}

def generate_article_content(article):
    """Generate article content following copywriting guidelines"""
    
    # Load ICP and copywriting rules
    icp_rules = {
        "tone": "casual-magnetic",
        "style": "like a local friend who knows everything",
        "avoid": ["discover", "embark", "experience the majestic", "create lasting memories"],
        "include": ["specific distances", "parking tips", "honest opinions", "local secrets"],
    }
    
    # Article template based on category
    templates = {
        "trail-guide": generate_trail_guide,
        "camping-guide": generate_camping_guide,
        "winter-guide": generate_winter_guide,
        "seasonal": generate_seasonal_guide,
        "park-guide": generate_park_guide,
    }
    
    generator = templates.get(article.get("category", ""), generate_generic_article)
    return generator(article, icp_rules)

def generate_trail_guide(article, icp_rules):
    """Generate trail guide article"""
    
    keyword = article["target_keyword"]
    title = article["title"]
    slug = article["slug"]
    
    content = f"""---
import BaseLayout from "../../layouts/BaseLayout.astro";
import Header from "../../components/Header.astro";
import Footer from "../../components/Footer.astro";

const article = {{
  title: "{title}",
  description: "Complete guide to {keyword}. Trail stats, parking tips, and insider knowledge from locals.",
  image: "/images/blog/{slug}.jpg",
  publishDate: "{datetime.now().strftime('%Y-%m-%d')}",
  author: "PNW Outdoor Team",
  readTime: "8 min read",
}};
---

<BaseLayout title={{article.title}} description={{article.description}}>
  <Header slot="header" />

  <!-- Hero -->
  <section class="relative h-[400px] md:h-[500px] flex items-center">
    <div class="absolute inset-0">
      <img src={{article.image}} alt={{article.title}} class="w-full h-full object-cover" />
      <div class="absolute inset-0 bg-gradient-to-b from-black/50 to-black/70"></div>
    </div>
    <div class="container-custom relative z-10">
      <div class="max-w-3xl">
        <div class="flex items-center gap-3 mb-4">
          <span class="px-3 py-1 bg-primary text-white text-sm rounded-full">Trail Guide</span>
          <span class="text-white/70 text-sm">{{article.readTime}}</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">{{article.title}}</h1>
        <p class="text-lg text-white/80">Published {{article.publishDate}}</p>
      </div>
    </div>
  </section>

  <!-- Article Content -->
  <article class="section-padding bg-white">
    <div class="container-custom max-w-4xl">
      <!-- Quick Verdict -->
      <div class="p-6 bg-green-50 rounded-2xl mb-10">
        <h2 class="text-xl font-bold text-gray-900 mb-2">The Bottom Line</h2>
        <p class="text-gray-700">
          [THIS SECTION WILL BE POPULATED WITH SPECIFIC TRAIL INFO]
        </p>
      </div>

      <!-- Quick Facts -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10 p-4 bg-gray-50 rounded-xl">
        <div>
          <p class="text-sm text-gray-500">Distance</p>
          <p class="font-medium">[X miles RT]</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Elevation</p>
          <p class="font-medium">[X ft]</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Difficulty</p>
          <p class="font-medium">[Easy/Moderate/Hard]</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Time</p>
          <p class="font-medium">[X hours]</p>
        </div>
      </div>

      <!-- Main Content -->
      <div class="prose prose-lg max-w-none">
        <h2>What You're Getting Into</h2>
        <p>[HONEST OVERVIEW - NOT GENERIC MARKETING SPEAK]</p>

        <h2>Getting There</h2>
        <p>[SPECIFIC DRIVING DIRECTIONS, PARKING TIPS]</p>

        <h2>The Trail: Mile by Mile</h2>
        <p>[DETAILED TRAIL DESCRIPTION WITH SPECIFIC STOPS]</p>

        <h2>Real Talk</h2>
        <div class="grid md:grid-cols-2 gap-6 not-prose my-8">
          <div class="p-5 bg-green-50 rounded-xl">
            <h3 class="font-semibold text-green-800 mb-2">👍 The Good</h3>
            <ul class="space-y-2 text-green-700 text-sm">
              <li>• [Specific positive aspect 1]</li>
              <li>• [Specific positive aspect 2]</li>
            </ul>
          </div>
          <div class="p-5 bg-yellow-50 rounded-xl">
            <h3 class="font-semibold text-yellow-800 mb-2">⚠️ The Not-So-Good</h3>
            <ul class="space-y-2 text-yellow-700 text-sm">
              <li>• [Honest drawback 1]</li>
              <li>• [Honest drawback 2]</li>
            </ul>
          </div>
        </div>

        <h2>When to Go</h2>
        <p>[SEASONAL RECOMMENDATIONS WITH SPECIFIC MONTHS]</p>

        <h2>What to Bring</h2>
        <p>[ESSENTIAL GEAR LIST]</p>

        <h2>Pro Tips From Locals</h2>
        <div class="space-y-4 not-prose my-8">
          <div class="p-4 bg-blue-50 rounded-xl">
            <p class="text-blue-800">💡 [LOCAL TIP 1 - something only a local would know]</p>
          </div>
          <div class="p-4 bg-blue-50 rounded-xl">
            <p class="text-blue-800">💡 [LOCAL TIP 2 - parking hack, best time, etc]</p>
          </div>
        </div>

        <h2>Common Questions</h2>
        <h3>Is it safe for kids?</h3>
        <p>[HONEST ANSWER]</p>
        
        <h3>Can I bring my dog?</h3>
        <p>[HONEST ANSWER]</p>
        
        <h3>How crowded does it get?</h3>
        <p>[HONEST ANSWER WITH SPECIFICS]</p>
      </div>

      <!-- CTA -->
      <div class="mt-12 p-8 bg-primary rounded-2xl text-center">
        <h3 class="text-xl font-bold text-white mb-3">Ready to Hit the Trail?</h3>
        <p class="text-white/80 mb-4">Download our complete PNW trail guide with 50+ hikes.</p>
        <a href="/products/" class="inline-flex items-center justify-center px-8 py-4 bg-white text-primary font-semibold rounded-lg hover:bg-gray-100 transition-colors">
          Get the Trail Guide — $29
        </a>
      </div>
    </div>
  </article>

  <Footer slot="footer" />
</BaseLayout>
"""
    return content

def generate_camping_guide(article, icp_rules):
    """Generate camping guide article"""
    # Similar structure but camping-focused
    return generate_trail_guide(article, icp_rules)  # Simplified for now

def generate_winter_guide(article, icp_rules):
    """Generate winter sports guide"""
    return generate_trail_guide(article, icp_rules)  # Simplified for now

def generate_seasonal_guide(article, icp_rules):
    """Generate seasonal content"""
    return generate_trail_guide(article, icp_rules)  # Simplified for now

def generate_park_guide(article, icp_rules):
    """Generate park overview guide"""
    return generate_trail_guide(article, icp_rules)  # Simplified for now

def generate_generic_article(article, icp_rules):
    """Generate generic article"""
    return generate_trail_guide(article, icp_rules)  # Simplified for now

def fetch_image(keyword, slug):
    """Download a real image from Unsplash based on keyword category.
    
    Uses Unsplash Source URLs (no API key needed) which serve random
    matching photos. Each keyword gets a distinct, relevant image.
    """
    import urllib.request
    import urllib.error
    
    print(f"  🖼️ Fetching image for: {keyword}")
    image_path = os.path.join(IMAGES_DIR, f"{slug}.jpg")
    
    # Skip download if image already exists
    if os.path.exists(image_path) and os.path.getsize(image_path) > 10000:
        print(f"  ✓ Image already exists: {slug}.jpg ({os.path.getsize(image_path)} bytes)")
        return image_path
    
    # Map keywords to specific Unsplash photo IDs for reliable, high-quality images
    # These are real Unsplash photos of PNW landscapes
    photo_map = {
        # Trails
        "twin falls": "photo-1464822759023-fed622ff2c3b",
        "rattlesnake": "photo-1486870591958-9b9d0d1dda99",
        "lake serene": "photo-1506905925346-21bda4d32df4",
        "mount si": "photo-1464822759023-fed622ff2c3b",
        "snow lake": "photo-1483728642387-6c3bdd6c93e5",
        "wallace falls": "photo-1432405972618-c6b0cfba8c4e",
        "rainier": "photo-1519681393784-d120267933ba",
        "granite mountain": "photo-1486870591958-9b9d0d1dda99",
        # Camping
        "camping": "photo-1475483768296-6163e08872a1",
        "campground": "photo-1475483768296-6163e08872a1",
        "olympic national park": "photo-1501785888041-af3ef285b470",
        "north cascades": "photo-1506905925346-21bda4d32df4",
        # Winter/Skiing
        "skiing": "photo-1551524559-8af4e6624178",
        "stevens pass": "photo-1551524559-8af4e6624178",
        "snoqualmie": "photo-1483728642387-6c3bdd6c93e5",
        "crystal mountain": "photo-1483728642387-6c3bdd6c93e5",
        "snowshoeing": "photo-1486870591958-9b9d0d1dda99",
        "winter hiking": "photo-1486870591958-9b9d0d1dda99",
        # Water
        "kayak": "photo-1472745433479-4556f22e32c1",
        "paddleboard": "photo-1505118380757-91f5f5632de0",
        "san juan": "photo-1501785888041-af3ef285b470",
        # Seasonal
        "spring hiking": "photo-1490750967868-88aa4f44baee",
        "wildflower": "photo-1490750967868-88aa4f44baee",
        "summer hiking": "photo-1464822759023-fed622ff2c3b",
        "fall hiking": "photo-1507003211169-0a1dd7228f2d",
        # General PNW
        "hiking": "photo-1464822759023-fed622ff2c3b",
        "trail": "photo-1464822759023-fed622ff2c3b",
        "seattle": "photo-1502175353174-a7a70e73b362",
        "washington": "photo-1519681393784-d120267933ba",
        "day trip": "photo-1501785888041-af3ef285b470",
        "weekend trip": "photo-1475483768296-6163e08872a1",
    }
    
    # Find best matching photo
    photo_id = None
    kw_lower = keyword.lower()
    # Try exact match first, then partial
    for key, pid in photo_map.items():
        if key in kw_lower:
            photo_id = pid
            break
    if not photo_id:
        # Default to a beautiful PNW mountain scene
        photo_id = "photo-1519681393784-d120267933ba"
    
    # Construct Unsplash source URL (free, no API key)
    image_url = f"https://images.unsplash.com/{photo_id}?w=1200&q=80&auto=format"
    
    try:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        req = urllib.request.Request(image_url, headers={
            "User-Agent": "PNW-Outdoor-Content-Pipeline/1.0"
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            with open(image_path, 'wb') as f:
                f.write(data)
        size_kb = os.path.getsize(image_path) // 1024
        print(f"  ✓ Downloaded: {slug}.jpg ({size_kb} KB)")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"  ⚠️ Download failed: {e}")
        print(f"  → Falling back to category search URL")
        # Fallback: use Unsplash source random search
        category = "mountain"
        for cat in ["camping", "skiing", "kayaking", "hiking"]:
            if cat in kw_lower:
                category = cat
                break
        fallback_url = f"https://source.unsplash.com/1600x900/?{category},pacific-northwest"
        try:
            req = urllib.request.Request(fallback_url, headers={
                "User-Agent": "PNW-Outdoor-Content-Pipeline/1.0"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                with open(image_path, 'wb') as f:
                    f.write(data)
            print(f"  ✓ Fallback image saved: {slug}.jpg")
        except Exception as e2:
            print(f"  ⚠️ Fallback also failed: {e2}")
            print(f"  → Image will need manual replacement")
    
    return image_path

def create_article_file(article, content):
    """Create .astro file for article"""
    slug = article["slug"]
    filepath = os.path.join(PAGES_DIR, f"{slug}.astro")
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"  ✓ Created: {filepath}")
    return filepath

def git_commit_and_push(article):
    """Commit and push to GitHub"""
    print("  📤 Committing to GitHub...")
    
    os.chdir(REPO_DIR)
    
    # Add changes
    subprocess.run(["git", "add", "."], check=True)
    
    # Commit
    commit_msg = f"feat: add article - {article['title']}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    
    # Push
    subprocess.run(["git", "push"], check=True)
    
    print("  ✓ Pushed to GitHub (deploy will trigger automatically)")

def update_calendar_status(calendar, article, status="published"):
    """Update article status in calendar"""
    for art in calendar.get("articles", []):
        if art.get("slug") == article["slug"]:
            art["status"] = status
            art["published_date"] = datetime.now().strftime("%Y-%m-%d")
            break
    save_calendar(calendar)

def run_pipeline():
    """Main pipeline execution"""
    print("=" * 60)
    print("🏔️ PNW OUTDOOR - CONTENT PIPELINE")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # Load calendar
    calendar = load_calendar()
    
    # Get next article
    article = get_next_article(calendar)
    if not article:
        print("✅ No more articles to publish!")
        return
    
    print(f"📝 Next article: {article['title']}")
    print(f"   Keyword: {article['target_keyword']}")
    print(f"   Volume: {article.get('volume', 'N/A')}")
    print(f"   SEO: {article.get('seo_difficulty', 'N/A')}")
    print()
    
    # Step 1: Keyword Research (if needed)
    print("[1/5] Keyword Research")
    if check_keyword_research_needed(article):
        result = research_keyword(article["target_keyword"], article)
        # Update article with researched data
        if result.get("volume"):
            article["volume"] = result["volume"]
        if result.get("seo_difficulty"):
            article["seo_difficulty"] = result["seo_difficulty"]
    else:
        print("  ✓ Research already complete")
    
    # Step 2: Generate Content
    print("\n[2/5] Generating Content")
    content = generate_article_content(article)
    print(f"  ✓ Generated {len(content)} chars")
    
    # Step 3: Fetch Image
    print("\n[3/5] Fetching Image")
    fetch_image(article["target_keyword"], article["slug"])
    
    # Step 4: Create Article File
    print("\n[4/5] Creating Article File")
    create_article_file(article, content)
    
    # Step 5: Publish
    print("\n[5/5] Publishing")
    git_commit_and_push(article)
    
    # Update calendar
    update_calendar_status(calendar, article, "published")
    
    print("\n" + "=" * 60)
    print("✅ ARTICLE PUBLISHED!")
    print(f"   URL: https://pnwoutdooradventures.pages.dev/blog/{article['slug']}/")
    print("=" * 60)

if __name__ == "__main__":
    run_pipeline()
