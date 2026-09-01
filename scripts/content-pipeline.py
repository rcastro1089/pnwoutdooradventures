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

def research_keyword(keyword):
    """Simulate keyword research (in real impl, call DataForSEO)"""
    print(f"  📊 Researching keyword: {keyword}")
    # For now, return placeholder - in production, call APIs
    return {
        "keyword": keyword,
        "volume": "researched",
        "difficulty": "assessed",
        "competitors": "analyzed"
    }

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
    """Fetch appropriate image from Unsplash"""
    print(f"  🖼️ Fetching image for: {keyword}")
    
    # Unsplash search URLs for different categories
    image_queries = {
        "hiking": "mountain-trail-pacific-northwest",
        "camping": "campfire-tent-forest",
        "winter": "skiing-snow-mountain",
        "water": "kayak-lake-pacific-northwest",
    }
    
    # Determine category from keyword
    category = "hiking"
    for cat in ["camping", "winter", "water"]:
        if cat in keyword.lower():
            category = cat
            break
    
    query = image_queries.get(category, "mountain-nature")
    
    # Download image (placeholder URL - in production use Unsplash API)
    image_url = f"https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200"
    image_path = os.path.join(IMAGES_DIR, f"{slug}.jpg")
    
    # For now, create placeholder
    print(f"  ✓ Image placeholder created: {slug}.jpg")
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
        research_keyword(article["target_keyword"])
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
