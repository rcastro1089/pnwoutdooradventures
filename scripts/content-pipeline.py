#!/usr/bin/env python3
"""
PNW Outdoor Adventures - Content Pipeline
Automatiza: Research → Writing → Image → Publish → Deploy

Trail guides (category=trail-guide) → src/pages/hiking/ using ArticleLayout
Blog posts (other categories)       → src/pages/blog/ using BaseLayout
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Config
REPO_DIR = os.path.expanduser("~/github-repo/pnwoutdooradventures")
CALENDAR_PATH = os.path.join(REPO_DIR, "keyword-research/calendar.json")
BLOG_DIR = os.path.join(REPO_DIR, "src/pages/blog")
HIKING_DIR = os.path.join(REPO_DIR, "src/pages/hiking")
IMAGES_DIR = os.path.join(REPO_DIR, "public/images/blog")
HIKING_INDEX = os.path.join(HIKING_DIR, "index.astro")

# Ensure directories exist
os.makedirs(BLOG_DIR, exist_ok=True)
os.makedirs(HIKING_DIR, exist_ok=True)
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
    volume = article.get("volume", 0)
    seo = article.get("seo_difficulty", 99)
    return volume < 100 or seo == 99


def research_keyword(keyword, article=None):
    """Research keyword data from calendar or API."""
    print(f"  📊 Researching keyword: {keyword}")

    dataforseo_user = os.environ.get("DATAFORSEO_LOGIN")
    dataforseo_pass = os.environ.get("DATAFORSEO_PASSWORD")

    if dataforseo_user and dataforseo_pass:
        print("  → Using live DataForSEO API")
        return _research_via_dataforseo(keyword, dataforseo_user, dataforseo_pass)

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
        "location_code": 2840,
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


# ---------------------------------------------------------------------------
# Trail-specific data lookup
# ---------------------------------------------------------------------------

# Static trail details keyed by slug. Used to populate ArticleLayout props
# and write realistic content. New trails can be added here as the site grows.
TRAIL_DATA = {
    "tubal-cain": {
        "location": "Port Angeles, WA",
        "distance": "6.6 miles roundtrip",
        "elevation": "1,800 ft",
        "difficulty": "moderate",
        "time": "3-4 hours",
        "image": "https://images.unsplash.com/photo-1445363692815-ebcd599f7621?w=1200",
        "description": "Tubal Cain Trail leads to the ruins of a WWI-era copper mine and a historic mountain lodge, making it one of the most unique hikes on the Olympic Peninsula.",
        "overview": "Tubal Cain is not your typical PNW trail. You're hiking to actual ruins—a WWI-era copper mine and the remnants of an old mountain lodge that once served miners in the early 1900s. The trail winds through dense old-growth forest on the eastern slopes of the Olympic Mountains, with occasional peeks of the jagged Bailey Range. It's a moderate climb with a story at the end.",
        "getting_there": "From Port Angeles, drive west on US-101 for about 20 miles, then turn north onto paved Forest Road 2920. Follow it for 6 miles to the trailhead parking area. The road is steep and narrow in spots—take it slow. Parking is free and holds about 30 cars. Arrive before 9am on summer weekends.",
        "trail_description": (
            "Mile 0–1: The trail starts with a gentle climb through second-growth Douglas fir. You'll cross a couple of small creeks on wooden bridges—these can be slick after rain.\n\n"
            "Mile 1–2.5: Steeper switchbacks through increasingly dense forest. Ferns and moss blanket everything. You might spot a Roosevelt elk if you're quiet.\n\n"
            "Mile 2.5–3: The mine ruins appear—concrete foundations, rusted equipment, and collapsed tunnels. Explore carefully. The old mountain lodge site is nearby with partial stone walls still standing. This is a great spot for lunch."
        ),
        "what_to_bring": "Sturdy hiking boots (the trail gets muddy), 1.5L water, rain jacket (Olympics are wet), snacks, and a headlamp if you want to peek into the mine tunnels. A Discover Pass is required for parking.",
        "highlights": ["WWI-era mine ruins", "Old mountain lodge remnants", "Olympic Peninsula old-growth forest", "Views of the Bailey Range"],
    },
    "olympic-national-park-hiking": {
        "location": "Port Angeles, WA",
        "distance": "Varies by trail",
        "elevation": "Varies",
        "difficulty": "moderate",
        "time": "Half-day to multi-day",
        "image": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=1200",
        "description": "Olympic National Park offers everything from rainforest walks to alpine scrambles—over 600 miles of trails across three distinct ecosystems.",
        "overview": "Olympic National Park is a world unto itself. Three million acres of wilderness split into three dramatically different zones: the temperate Hoh Rain Forest, the rugged Pacific coast, and the glacier-capped alpine interior. Whether you want a casual forest stroll or a backcountry expedition, this park delivers.",
        "getting_there": "The main access point is Port Angeles on the north side of the peninsula. From Seattle, take the Bainbridge Island ferry (35 min) or drive around via Tacoma (2.5 hours). The Hurricane Ridge Visitor Center is 17 miles from Port Angeles—check road status before going.",
        "trail_description": (
            "Top trails by difficulty:\n\n"
            "Easy: Hall of Mosses Trail (0.8 mi) in the Hoh Rain Forest—walking through a surreal, moss-draped world. Marymere Falls (1.8 mi) near Lake Crescent is a quick waterfall hike.\n\n"
            "Moderate: Hurricane Hill (3.2 mi) for panoramic mountain views. Sol Duc Falls (1.6 mi) for an easy waterfall walk.\n\n"
            "Hard: Mount Storm King (4 mi, 2,000 ft gain) for lake views with a rope-assisted scramble. Grand Valley to Enchanted Valley (30 mi) is a multi-day backcountry classic."
        ),
        "what_to_bring": "Layered clothing, waterproof everything, bear canister for backcountry, Discover Pass or America the Beautiful Pass, offline maps (no cell service inside the park).",
        "highlights": ["Hoh Rain Forest", "Hurricane Ridge alpine views", "Wild Pacific coastline", "Glacier-carved valleys"],
    },
    "north-cascades-hiking": {
        "location": "Concrete, WA",
        "distance": "Varies by trail",
        "elevation": "Varies",
        "difficulty": "hard",
        "time": "Half-day to multi-day",
        "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200",
        "description": "North Cascades National Park is Washington's most rugged and least-visited national park—over 300 glaciers and 400 miles of trails in true wilderness.",
        "overview": "North Cascades is the real deal. Over 300 glaciers, jagged granite spires, and almost nobody around. It's the least-visited national park in the lower 48 for a reason—access takes effort. But if you want solitude with jaw-dropping alpine scenery, this is it. The drive in on the North Cascades Highway (SR 20) is an adventure in itself.",
        "getting_there": "From Seattle, head north on I-5 to Burlington, then east on SR 20 (North Cascades Highway). The drive takes about 2.5 hours to reach the Colonial Creek campground area. The highway is closed in winter (typically November–April).",
        "trail_description": (
            "Top picks:\n\n"
            "Easy: Blue Lake Trail (4.4 mi) in the Diablo Lake area—stunning turquoise water surrounded by peaks.\n\n"
            "Moderate: Cascade Pass (7 mi RT, 1,800 ft gain) for sweeping views of theCascade Range. Easy to mix with Sahale Arm for a full day.\n\n"
            "Hard: Copper Ridge Loop (35 mi) for a multi-day backcountry experience with alpine meadows and glacier views. The infamous Picket Range traverse is for experts only."
        ),
        "what_to_bring": "Bear canister (required for backcountry), rain gear, warm layers, offline maps, water filter, extra food (services are minimal). Fill up gas and buy groceries before entering the park.",
        "highlights": ["300+ glaciers", "Turquoise Diablo Lake", "Solitude and remote wilderness", "Jagged Cascade peaks"],
    },
}

# Image mapping for trails (slug → unsplash photo id)
TRAIL_IMAGE_MAP = {
    "tubal-cain": "photo-1445363692815-ebcd599f7621",
    "olympic-national-park-hiking": "photo-1501785888041-af3ef285b470",
    "north-cascades-hiking": "photo-1506905925346-21bda4d32df4",
}


# ---------------------------------------------------------------------------
# Content generation
# ---------------------------------------------------------------------------

def generate_article_content(article):
    """Generate article content following copywriting guidelines"""

    icp_rules = {
        "tone": "casual-magnetic",
        "style": "like a local friend who knows everything",
        "avoid": ["discover", "embark", "experience the majestic", "create lasting memories"],
        "include": ["specific distances", "parking tips", "honest opinions", "local secrets"],
    }

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
    """Generate trail guide as an Astro page using ArticleLayout.

    Returns (content, trail_props) where trail_props is the dict passed
    to ArticleLayout and content is the slot HTML body.
    """
    slug = article["slug"]
    title = article["title"]
    keyword = article["target_keyword"]

    # Look up trail-specific data; fall back to generating from calendar fields
    td = TRAIL_DATA.get(slug, _build_trail_data_from_article(article))

    trail_props = {
        "title": title,
        "description": td["description"],
        "image": td["image"],
        "location": td["location"],
        "distance": td["distance"],
        "elevation": td["elevation"],
        "difficulty": td["difficulty"],
        "time": td["time"],
    }

    # Build slot HTML with real content
    body = _build_trail_body(td, title, keyword)
    return body, trail_props


def _build_trail_data_from_article(article):
    """Synthesize trail data from calendar article fields."""
    slug = article["slug"]
    title = article["title"]
    keyword = article["target_keyword"]
    category = article.get("category", "trail-guide")

    # Determine difficulty from keyword hints
    kw_lower = keyword.lower()
    if any(w in kw_lower for w in ["mount rainier", "mount si", "granite"]):
        difficulty = "hard"
    elif any(w in kw_lower for w in ["lake serene", "snow lake", "wallace"]):
        difficulty = "moderate"
    else:
        difficulty = "moderate"

    # Unsplash image
    photo_id = TRAIL_IMAGE_MAP.get(slug)
    if not photo_id:
        for key, pid in TRAIL_IMAGE_MAP.items():
            if key in slug:
                photo_id = pid
                break
    if not photo_id:
        photo_id = "photo-1519681393784-d120267933ba"
    image = f"https://images.unsplash.com/{photo_id}?w=1200"

    return {
        "location": "Pacific Northwest, WA",
        "distance": "Varies",
        "elevation": "Varies",
        "difficulty": difficulty,
        "time": "Half-day",
        "image": image,
        "description": f"Complete guide to {keyword}. Trail stats, parking tips, and insider knowledge from locals who hike these trails regularly.",
        "overview": f"{title} is one of the most popular hikes in the Pacific Northwest. This guide covers everything you need to know—from parking logistics to trail conditions—so you can plan with confidence.",
        "getting_there": "Take the main highway toward the trailhead. Check Google Maps for current driving times from Seattle or your starting point. Parking fills up early on weekends, so plan to arrive before 8am during peak season.",
        "trail_description": "The trail winds through classic Pacific Northwest terrain—tall conifers, fern-covered forest floor, and the occasional stream crossing. Elevation gain is steady but manageable for most fitness levels. Keep an eye out for wildlife and enjoy the journey as much as the destination.",
        "what_to_bring": "Sturdy hiking shoes, at least 1 liter of water, rain jacket (PNW weather is unpredictable), snacks, and a Discover Pass for parking. Layers are essential—you'll warm up as you climb.",
        "highlights": ["Stunning mountain views", "Old-growth forest", "PNW wilderness experience", "Great workout"],
    }


def _build_trail_body(td, title, keyword):
    """Build the HTML body (slot content) for a trail guide page."""

    difficulty_label = td["difficulty"].capitalize()

    # Parse overview into paragraphs
    overview_paras = td["overview"].split("\n\n")
    overview_html = "\n    ".join(
        f'<p class="text-gray-600 mb-4">{p.strip()}</p>' for p in overview_paras
    )

    # Parse getting_there
    getting_there_paras = td["getting_there"].split("\n\n")
    getting_there_html = "\n    ".join(
        f'<p class="text-gray-600 mb-4">{p.strip()}</p>' for p in getting_there_paras
    )

    # Parse trail description into sections
    trail_sections = _parse_trail_sections(td["trail_description"])

    # What to bring items
    bring_items = _parse_bring_items(td["what_to_bring"])

    # Highlights
    highlights_html = "\n      ".join(
        f'<span class="px-3 py-1 bg-white rounded-full">✓ {h}</span>'
        for h in td.get("highlights", [])
    )

    # Seasonal tips (generic but real-sounding for PNW)
    seasonal = _seasonal_tips(td.get("difficulty", "moderate"))

    body = f"""  <!-- Quick Verdict -->
  <div class="p-6 bg-green-50 rounded-2xl mb-10">
    <h2 class="text-xl font-bold text-gray-900 mb-2">The Bottom Line</h2>
    <p class="text-gray-700">
      <strong>Worth it?</strong> Absolutely. {td['description']}
    </p>
    <div class="mt-4 flex flex-wrap gap-4 text-sm">
      {highlights_html}
    </div>
  </div>

  <!-- Overview -->
  <section class="mb-12">
    <h2 class="text-2xl font-bold text-gray-900 mb-4">What You're Getting Into</h2>
    {overview_html}

    <!-- Quick Facts -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 p-4 bg-gray-50 rounded-xl">
      <div>
        <p class="text-sm text-gray-500">Distance</p>
        <p class="font-medium">{td['distance']}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Elevation Gain</p>
        <p class="font-medium">{td['elevation']}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Difficulty</p>
        <p class="font-medium">{difficulty_label}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Time</p>
        <p class="font-medium">{td['time']}</p>
      </div>
    </div>
  </section>

  <!-- Getting There -->
  <section class="mb-12">
    <h2 class="text-2xl font-bold text-gray-900 mb-4">Parking: The Part Nobody Talks About</h2>
    {getting_there_html}

    <div class="p-4 bg-yellow-50 rounded-xl mt-4">
      <p class="text-yellow-800 font-medium">⚠️ Important: You need a Discover Pass ($30/year or $10/day) for parking at Washington State trailheads. Rangers do check.</p>
    </div>
  </section>

  <!-- Trail Description -->
  <section class="mb-12">
    <h2 class="text-2xl font-bold text-gray-900 mb-4">The Trail: Mile by Mile</h2>

    <div class="space-y-6">
      {trail_sections}
    </div>
  </section>

  <!-- What to Bring -->
  <section class="mb-12">
    <h2 class="text-2xl font-bold text-gray-900 mb-4">What to Bring</h2>

    <div class="p-6 bg-gray-50 rounded-2xl">
      <div class="grid md:grid-cols-2 gap-6">
        <div>
          <h3 class="font-semibold text-gray-900 mb-3">The Essentials</h3>
          <ul class="space-y-2 text-gray-600 text-sm">
            {bring_items[0]}
          </ul>
        </div>

        <div>
          <h3 class="font-semibold text-gray-900 mb-3">Nice to Have</h3>
          <ul class="space-y-2 text-gray-600 text-sm">
            {bring_items[1]}
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- When to Go -->
  <section class="mb-12">
    <h2 class="text-2xl font-bold text-gray-900 mb-4">When to Go (And When to Avoid)</h2>

    <div class="space-y-4">
      {seasonal}
    </div>
  </section>

  <!-- Pro Tips -->
  <section class="mb-12">
    <h2 class="text-2xl font-bold text-gray-900 mb-4">Pro Tips From Locals</h2>

    <div class="space-y-4">
      <div class="p-4 bg-blue-50 rounded-xl">
        <p class="text-blue-800">
          <strong>🏷️ Parking hack:</strong> Arrive before 8am on weekends. If the lot is full, check for overflow parking along the access road—it's usually just a short walk back.
        </p>
      </div>

      <div class="p-4 bg-blue-50 rounded-xl">
        <p class="text-blue-800">
          <strong>📸 Best photo time:</strong> Golden hour (1-2 hours before sunset) creates the best light through the trees. Morning light works well for east-facing viewpoints.
        </p>
      </div>

      <div class="p-4 bg-blue-50 rounded-xl">
        <p class="text-blue-800">
          <strong>🍜 Post-hike food:</strong> Check local cafes and breweries near the trailhead. Most PNW trail towns have at least one solid burger spot within 15 minutes.
        </p>
      </div>
    </div>
  </section>

  <!-- FAQ -->
  <section class="mb-12">
    <h2 class="text-2xl font-bold text-gray-900 mb-6">Common Questions</h2>

    <div class="space-y-6">
      <div>
        <h3 class="font-semibold text-gray-900 mb-2">Is this trail safe for kids?</h3>
        <p class="text-gray-600">{'Yes, kids 6+ can handle this trail comfortably.' if td.get('difficulty') in ('easy', 'moderate') else 'This is a challenging trail—best suited for fit teens and adults. Kids with hiking experience can do it, but be prepared for steep sections.'}</p>
      </div>

      <div>
        <h3 class="font-semibold text-gray-900 mb-2">Can I bring my dog?</h3>
        <p class="text-gray-600">Check current regulations for this specific trail—some require leashes at all times, others prohibit dogs entirely. Most state lands in Washington allow dogs on leash. Bring water for them.</p>
      </div>

      <div>
        <h3 class="font-semibold text-gray-900 mb-2">How crowded does it get?</h3>
        <p class="text-gray-600">On summer weekends, popular trails can see 50-100+ hikers. Weekday mornings are much quieter. The further you go from the trailhead, the fewer people you'll encounter.</p>
      </div>

      <div>
        <h3 class="font-semibold text-gray-900 mb-2">Is there cell service?</h3>
        <p class="text-gray-600">Spotty to none. You'll likely get some signal at the trailhead but it fades quickly. Download offline maps before you go.</p>
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section class="p-8 bg-primary rounded-2xl text-center">
    <h3 class="text-xl font-bold text-white mb-3">Ready to Hit the Trail?</h3>
    <p class="text-white/80 mb-4">Download our complete PNW trail guide with 50+ hikes, detailed maps, and insider tips.</p>
    <a href="/products/" class="inline-flex items-center justify-center px-8 py-4 bg-white text-primary font-semibold rounded-lg hover:bg-gray-100 transition-colors">
      Get the Trail Guide — $29
    </a>
  </section>"""
    return body


def _parse_trail_sections(text):
    """Parse trail description into styled HTML sections."""
    sections = []
    parts = text.split("\n\n")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # If it starts with a heading-like line, extract it
        lines = part.split("\n", 1)
        heading = lines[0].strip().rstrip(":")
        body = lines[1].strip() if len(lines) > 1 else ""
        # Color the last section green (the payoff)
        border_class = "border-primary"
        if "reward" in heading.lower() or "summit" in heading.lower() or "view" in heading.lower() or "ruins" in heading.lower() or "lake" in heading.lower() or "falls" in heading.lower():
            border_class = "border-green-500"
        sections.append(f"""      <div class="p-4 border-l-4 {border_class}">
        <h3 class="font-semibold text-gray-900">{heading}</h3>
        <p class="text-gray-600 mt-2">{body}</p>
      </div>""")
    return "\n".join(sections) if sections else f"""      <div class="p-4 border-l-4 border-primary">
        <h3 class="font-semibold text-gray-900">The Trail</h3>
        <p class="text-gray-600 mt-2">The trail winds through classic Pacific Northwest terrain. Take your time and enjoy the journey.</p>
      </div>"""


def _parse_bring_items(text):
    """Parse what-to-bring text into essential and nice-to-have lists."""
    items = [i.strip() for i in text.split(", ") if i.strip()]
    # Split roughly in half: first half essentials, second half nice-to-have
    mid = max(1, len(items) // 2)
    essentials = items[:mid]
    extras = items[mid:] if len(items) > mid else ["Snacks", "Camera"]

    CHECK = '<svg class="w-4 h-4 text-primary mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>'
    CHECK_GRAY = '<svg class="w-4 h-4 text-gray-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>'

    def render(items_list, icon):
        return "\n            ".join(
            f'<li class="flex items-start gap-2">\n              {icon}\n              {item}\n            </li>'
            for item in items_list
        )

    return render(essentials, CHECK), render(extras, CHECK_GRAY)


def _seasonal_tips(difficulty):
    """Generate seasonal recommendation blocks."""
    # All-season friendly wording
    winter_tip = "Trail can be icy—microspikes recommended." if difficulty in ("hard", "moderate") else "Trail may be muddy. Check conditions before going."
    return f"""      <div class="p-4 bg-gray-50 rounded-xl">
        <h3 class="font-semibold text-gray-900">🌸 Spring (March-May)</h3>
        <p class="text-gray-600 text-sm mt-1">Snowmelt feeds water features. Trail can be muddy early in the season. Wildflowers starting to bloom. Fewer crowds than summer.</p>
      </div>

      <div class="p-4 bg-gray-50 rounded-xl">
        <h3 class="font-semibold text-gray-900">☀️ Summer (June-August)</h3>
        <p class="text-gray-600 text-sm mt-1">Best weather, driest trail. Most crowded time—arrive early or go weekday. Bring sun protection and plenty of water.</p>
      </div>

      <div class="p-4 bg-gray-50 rounded-xl">
        <h3 class="font-semibold text-gray-900">🍂 Fall (September-November)</h3>
        <p class="text-gray-600 text-sm mt-1">Beautiful fall colors. Crowds thin out. Weather gets unpredictable—bring layers and rain gear. Trails can be slippery when wet.</p>
      </div>

      <div class="p-4 bg-gray-50 rounded-xl">
        <h3 class="font-semibold text-gray-900">❄️ Winter (December-February)</h3>
        <p class="text-gray-600 text-sm mt-1">{winter_tip} Magical with snow. Very few people on the trail—great for solitude seekers.</p>
      </div>"""


# ---------------------------------------------------------------------------
# Legacy generators (for non-trail-guide categories)
# ---------------------------------------------------------------------------

def generate_camping_guide(article, icp_rules):
    """Generate camping guide article (blog format)."""
    return generate_blog_article(article, icp_rules)

def generate_winter_guide(article, icp_rules):
    """Generate winter sports guide (blog format)."""
    return generate_blog_article(article, icp_rules)

def generate_seasonal_guide(article, icp_rules):
    """Generate seasonal content (blog format)."""
    return generate_blog_article(article, icp_rules)

def generate_park_guide(article, icp_rules):
    """Generate park overview guide (blog format)."""
    return generate_blog_article(article, icp_rules)

def generate_generic_article(article, icp_rules):
    """Generate generic article (blog format)."""
    return generate_blog_article(article, icp_rules)


def generate_blog_article(article, icp_rules):
    """Generate a blog post with BaseLayout (legacy format)."""
    title = article["title"]
    keyword = article["target_keyword"]
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
          <span class="px-3 py-1 bg-primary text-white text-sm rounded-full">Guide</span>
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
      <div class="prose prose-lg max-w-none">
        <h2>Getting Started</h2>
        <p>Everything you need to know about {keyword} in the Pacific Northwest. This guide covers logistics, trail conditions, and insider tips from locals.</p>
      </div>
    </div>
  </article>

  <Footer slot="footer" />
</BaseLayout>"""
    return content


# ---------------------------------------------------------------------------
# File creation
# ---------------------------------------------------------------------------

def create_article_file(article, content, trail_props=None):
    """Create .astro file for article.

    For trail-guide category: writes to src/pages/hiking/[slug].astro
    For everything else:      writes to src/pages/blog/[slug].astro
    """
    slug = article["slug"]
    is_trail = article.get("category") == "trail-guide"

    if is_trail:
        # Build the full .astro file with ArticleLayout
        filepath = os.path.join(HIKING_DIR, f"{slug}.astro")
        full_content = _build_trail_astro_file(trail_props, content)
    else:
        filepath = os.path.join(BLOG_DIR, f"{slug}.astro")
        full_content = content

    with open(filepath, 'w') as f:
        f.write(full_content)

    print(f"  ✓ Created: {filepath}")
    return filepath


def _build_trail_astro_file(props, slot_html):
    """Build a complete .astro file for a trail guide using ArticleLayout."""
    difficulty = props["difficulty"]
    return f"""---
import ArticleLayout from "../../layouts/ArticleLayout.astro";

const trail = {{
  title: "{props['title']}",
  description: "{props['description']}",
  image: "{props['image']}",
  location: "{props['location']}",
  distance: "{props['distance']}",
  elevation: "{props['elevation']}",
  difficulty: "{difficulty}" as const,
  time: "{props['time']}",
}};
---

<ArticleLayout {{...trail}}>
{slot_html}
</ArticleLayout>
"""


# ---------------------------------------------------------------------------
# Hiking index update
# ---------------------------------------------------------------------------

def update_hiking_index(article, trail_props):
    """Append a new trail to the hiking/index.astro trails array."""
    if not os.path.exists(HIKING_INDEX):
        print(f"  ⚠️ Hiking index not found: {HIKING_INDEX}")
        return

    with open(HIKING_INDEX, 'r') as f:
        content = f.read()

    slug = article["slug"]

    # Check if trail already exists in index
    if f'slug: "{slug}"' in content or f"slug: '{slug}'" in content:
        print(f"  → Trail '{slug}' already in hiking index, skipping")
        return

    # Build the new trail entry
    difficulty = trail_props["difficulty"]
    # Use an unsplash image for the card (smaller size)
    image = trail_props["image"].replace("w=1200", "w=800") if "w=" in trail_props["image"] else trail_props["image"]

    new_trail = f"""  {{
    title: "{trail_props['title']}",
    slug: "{slug}",
    image: "{image}",
    location: "{trail_props['location']}",
    distance: "{trail_props['distance']}",
    difficulty: "{difficulty}" as const,
    rating: 4.7,
    reviews: 0,
  }}"""

    # Find the closing bracket of the trails array and insert before it
    # We look for the pattern of the last entry's closing } and the array's ]
    # Strategy: find the last `];` that closes the trails array
    insert_marker = "];\n\nconst easyTrails"
    if insert_marker in content:
        new_content = content.replace(
            insert_marker,
            f",\n{new_trail}\n{insert_marker}"
        )
    else:
        # Fallback: find the closing of the trails array differently
        # Look for the last entry before the closing ];
        lines = content.split('\n')
        insert_idx = None
        for i, line in enumerate(lines):
            if 'const easyTrails' in line:
                insert_idx = i
                break
        if insert_idx:
            # Find the last } before this line
            for j in range(insert_idx - 1, -1, -1):
                if lines[j].strip() == '},':
                    lines.insert(j + 1, f"  {{{new_trail.strip()}}},")
                    break
                elif lines[j].strip() == '};':
                    # Insert before the ];
                    lines.insert(j, f",\n{new_trail}")
                    break
            new_content = '\n'.join(lines)
        else:
            print(f"  ⚠️ Could not find insertion point in hiking index")
            return

    with open(HIKING_INDEX, 'w') as f:
        f.write(new_content)

    print(f"  ✓ Updated hiking/index.astro with '{article['title']}'")


# ---------------------------------------------------------------------------
# Image fetch
# ---------------------------------------------------------------------------

def fetch_image(keyword, slug):
    """Download a real image from Unsplash based on keyword category."""
    import urllib.request
    import urllib.error

    print(f"  🖼️ Fetching image for: {keyword}")
    image_path = os.path.join(IMAGES_DIR, f"{slug}.jpg")

    if os.path.exists(image_path) and os.path.getsize(image_path) > 10000:
        print(f"  ✓ Image already exists: {slug}.jpg ({os.path.getsize(image_path)} bytes)")
        return image_path

    photo_map = {
        "twin falls": "photo-1433086966358-54859d0ed716",
        "rattlesnake": "photo-1486870591958-9b9d0d1dda99",
        "lake serene": "photo-1506905925346-21bda4d32df4",
        "mount si": "photo-1464822759023-fed622ff2c3b",
        "snow lake": "photo-1483728642387-6c3bdd6c93e5",
        "wallace falls": "photo-1432405972618-c6b0cfba8c4e",
        "rainier": "photo-1519681393784-d120267933ba",
        "granite mountain": "photo-1486870591958-9b9d0d1dda99",
        "tubal cain": "photo-1445363692815-ebcd599f7621",
        "olympic": "photo-1501785888041-af3ef285b470",
        "north cascades": "photo-1506905925346-21bda4d32df4",
        "camping": "photo-1475483768296-6163e08872a1",
        "skiing": "photo-1551524559-8af4e6624178",
        "kayak": "photo-1472745433479-4556f22e32c1",
        "hiking": "photo-1464822759023-fed622ff2c3b",
        "trail": "photo-1464822759023-fed622ff2c3b",
        "seattle": "photo-1502175353174-a7a70e73b362",
        "washington": "photo-1519681393784-d120267933ba",
    }

    kw_lower = keyword.lower()
    photo_id = None
    for key, pid in photo_map.items():
        if key in kw_lower:
            photo_id = pid
            break
    if not photo_id:
        photo_id = "photo-1519681393784-d120267933ba"

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
        print(f"  → Image will need manual replacement")

    return image_path


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------

def git_commit_and_push(article):
    """Commit and push to GitHub"""
    print("  📤 Committing to GitHub...")

    os.chdir(REPO_DIR)

    subprocess.run(["git", "add", "."], check=True)

    commit_msg = f"feat: add article - {article['title']}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)

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


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline():
    """Main pipeline execution"""
    print("=" * 60)
    print("🏔️ PNW OUTDOOR - CONTENT PIPELINE")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    calendar = load_calendar()

    article = get_next_article(calendar)
    if not article:
        print("✅ No more articles to publish!")
        return

    is_trail_guide = article.get("category") == "trail-guide"
    article_type = "Trail Guide (→ /hiking/)" if is_trail_guide else f"Blog Post (→ /blog/) [{article.get('category', 'unknown')}]"

    print(f"📝 Next article: {article['title']}")
    print(f"   Type: {article_type}")
    print(f"   Keyword: {article['target_keyword']}")
    print(f"   Volume: {article.get('volume', 'N/A')}")
    print(f"   SEO: {article.get('seo_difficulty', 'N/A')}")
    print()

    # Step 1: Keyword Research (if needed)
    print("[1/6] Keyword Research")
    if check_keyword_research_needed(article):
        result = research_keyword(article["target_keyword"], article)
        if result.get("volume"):
            article["volume"] = result["volume"]
        if result.get("seo_difficulty"):
            article["seo_difficulty"] = result["seo_difficulty"]
    else:
        print("  ✓ Research already complete")

    # Step 2: Generate Content
    print("\n[2/6] Generating Content")
    trail_props = None
    if is_trail_guide:
        slot_html, trail_props = generate_trail_guide(article, {
            "tone": "casual-magnetic",
            "style": "like a local friend who knows everything",
            "avoid": ["discover", "embark", "experience the majestic"],
            "include": ["specific distances", "parking tips", "honest opinions"],
        })
        print(f"  ✓ Generated trail guide ({len(slot_html)} chars slot content)")
        print(f"    Props: {trail_props['distance']} | {trail_props['elevation']} | {trail_props['difficulty']}")
    else:
        slot_html = generate_article_content(article)
        print(f"  ✓ Generated {len(slot_html)} chars")

    # Step 3: Fetch Image (for blog posts; trail guides use unsplash URL in props)
    print("\n[3/6] Fetching Image")
    if is_trail_guide:
        print(f"  ✓ Using Unsplash image from trail props")
    else:
        fetch_image(article["target_keyword"], article["slug"])

    # Step 4: Create Article File
    print("\n[4/6] Creating Article File")
    if is_trail_guide:
        create_article_file(article, slot_html, trail_props)
    else:
        create_article_file(article, slot_html)

    # Step 5: Update hiking index (trail guides only)
    print("\n[5/6] Updating Hiking Index")
    if is_trail_guide and trail_props:
        update_hiking_index(article, trail_props)
    else:
        print("  → Not a trail guide, skipping hiking index update")

    # Step 6: Publish
    print("\n[6/6] Publishing")
    git_commit_and_push(article)

    update_calendar_status(calendar, article, "published")

    url = f"https://pnwoutdooradventures.pages.dev/hiking/{article['slug']}/" if is_trail_guide else f"https://pnwoutdooradventures.pages.dev/blog/{article['slug']}/"
    print("\n" + "=" * 60)
    print("✅ ARTICLE PUBLISHED!")
    print(f"   URL: {url}")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
