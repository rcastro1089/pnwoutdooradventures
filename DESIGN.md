# DESIGN.md — PNW Outdoor Adventures

## 🎨 Design System

**Inspiración combinada:**
- **Patagonia:** Limpieza, minimalismo, whitespace generoso
- **Hipcamp:** Photography-first, marketplace grid, warm
- **AllTrails:** Funcional, categorías claras, search-focused

---

## 🎨 Paleta de Colores

### Primary Brand
- **Forest Green** (`#2D5016`): Primary CTA, brand accent, active states
- **Deep Forest** (`#1A3A0A`): Pressed/dark variant

### Secondary
- **Earth Brown** (`#8B4513`): Secondary accent, badges
- **Sunset Orange** (`#FF6B35`): Highlights, featured items

### Text
- **Near Black** (`#1A1A1A`): Primary text (warm, not cold)
- **Stone Gray** (`#6B7280`): Secondary text, descriptions
- **Fog Gray** (`#9CA3AF`): Disabled, placeholder

### Surface
- **Pure White** (`#FFFFFF`): Page background
- **Snow** (`#F9FAFB`): Alternate sections, cards
- **Mist** (`#F3F4F6`): Hover states, subtle backgrounds

### Shadows
- **Card Shadow:** `0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)`
- **Hover Shadow:** `0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06)`
- **Lift Shadow:** `0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)`

---

## 📝 Tipografía

### Font Stack
```css
font-family: 'DM Sans', system-ui, -apple-system, sans-serif;
```

**Google Fonts:**
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&display=swap" rel="stylesheet">
```

### Jerarquía

| Role | Size | Weight | Line Height | Letter Spacing |
|------|------|--------|-------------|----------------|
| Display Hero | 56px | 700 | 1.1 | -0.02em |
| Section Heading | 40px | 700 | 1.2 | -0.01em |
| Card Title | 24px | 600 | 1.3 | normal |
| Subheading | 20px | 600 | 1.4 | normal |
| Body Large | 18px | 400 | 1.6 | normal |
| Body | 16px | 400 | 1.5 | normal |
| Caption | 14px | 400 | 1.4 | normal |
| Small | 12px | 500 | 1.3 | 0.05em |

---

## 🧩 Componentes

### Buttons

**Primary**
```css
background: #2D5016;
color: #FFFFFF;
padding: 12px 24px;
border-radius: 8px;
font-weight: 500;
transition: all 0.2s;
```
Hover: `background: #1A3A0A; transform: translateY(-1px);`

**Secondary**
```css
background: transparent;
color: #2D5016;
border: 2px solid #2D5016;
padding: 10px 24px;
border-radius: 8px;
```
Hover: `background: #2D5016; color: #FFFFFF;`

**Pill (Learn More)**
```css
background: transparent;
color: #2D5016;
border: 1px solid #2D5016;
border-radius: 9999px;
padding: 8px 16px;
font-size: 14px;
```

### Cards

**Trail Card (Hipcamp/AllTrails style)**
```css
background: #FFFFFF;
border-radius: 16px;
overflow: hidden;
box-shadow: 0 1px 3px rgba(0,0,0,0.1);
transition: all 0.3s;
```
Hover: `box-shadow: 0 4px 6px rgba(0,0,0,0.1); transform: translateY(-2px);`

**Card Structure:**
```
┌─────────────────────┐
│     [Image 16:10]   │
│                     │
├─────────────────────┤
│ Title               │
│ Location · Distance │
│ ⭐ 4.8 (120)       │
│ [Difficulty Badge]  │
└─────────────────────┘
```

**Product Card**
```css
background: #FFFFFF;
border-radius: 16px;
padding: 24px;
border: 1px solid #E5E7EB;
```

### Navigation

**Header (Patagonia style - minimal)**
```css
background: rgba(255,255,255,0.95);
backdrop-filter: blur(10px);
border-bottom: 1px solid #E5E7EB;
height: 64px;
position: sticky;
top: 0;
```

**Mega Menu**
```css
background: #FFFFFF;
border-radius: 0 0 16px 16px;
box-shadow: 0 10px 15px rgba(0,0,0,0.1);
```

### Search Bar (AllTrails style)
```css
background: #FFFFFF;
border: 1px solid #E5E7EB;
border-radius: 9999px;
padding: 12px 20px;
box-shadow: 0 1px 3px rgba(0,0,0,0.1);
```
Focus: `border-color: #2D5016; box-shadow: 0 0 0 3px rgba(45,80,22,0.1);`

### Badges

**Difficulty**
```css
Easy: background: #DCFCE7; color: #166534;
Moderate: background: #FEF9C3; color: #854D0E;
Hard: background: #FEE2E2; color: #991B1B;
```

---

## 📐 Layout

### Spacing System
```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
```

### Container
```css
max-width: 1280px;
margin: 0 auto;
padding: 0 24px;
```

### Grid

**Trail Grid (AllTrails style)**
```css
display: grid;
grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
gap: 24px;
```

**Featured Grid**
```css
display: grid;
grid-template-columns: repeat(3, 1fr);
gap: 24px;
```

### Sections
```css
padding: 64px 0;
```

---

## 🖼️ Imágenes

### Treatment
- **Trail photos:** 16:10 aspect ratio, object-fit: cover
- **Hero:** Full-width, min-height: 600px
- **Cards:** Aspect ratio 16:10, border-radius: 16px 16px 0 0

### Overlay
```css
.hero-overlay {
  background: linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,0.4) 100%);
}
```

---

## 🎯 Design Tokens (JSON)

```json
{
  "colors": {
    "primary": "#2D5016",
    "primary-dark": "#1A3A0A",
    "secondary": "#8B4513",
    "accent": "#FF6B35",
    "text": "#1A1A1A",
    "text-secondary": "#6B7280",
    "background": "#FFFFFF",
    "surface": "#F9FAFB",
    "border": "#E5E7EB"
  },
  "typography": {
    "font-family": "'DM Sans', system-ui, sans-serif",
    "font-size-xs": "0.75rem",
    "font-size-sm": "0.875rem",
    "font-size-base": "1rem",
    "font-size-lg": "1.125rem",
    "font-size-xl": "1.25rem",
    "font-size-2xl": "1.5rem",
    "font-size-3xl": "2rem",
    "font-size-4xl": "2.5rem",
    "font-size-5xl": "3.5rem",
    "font-weight-normal": "400",
    "font-weight-medium": "500",
    "font-weight-semibold": "600",
    "font-weight-bold": "700"
  },
  "spacing": {
    "1": "4px",
    "2": "8px",
    "3": "12px",
    "4": "16px",
    "5": "20px",
    "6": "24px",
    "8": "32px",
    "10": "40px",
    "12": "48px",
    "16": "64px"
  },
  "border-radius": {
    "none": "0",
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
    "2xl": "24px",
    "full": "9999px"
  },
  "shadows": {
    "sm": "0 1px 2px rgba(0,0,0,0.05)",
    "md": "0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)",
    "lg": "0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06)",
    "xl": "0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)"
  }
}
```

---

## 📱 Responsive

### Breakpoints
```css
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

### Mobile First
- Single column on mobile
- 2 columns on tablet
- 3-4 columns on desktop
- Hamburger menu on mobile

---

## ✅ Do's and Don'ts

### Do
- ✅ Use photography as hero content
- ✅ Keep whitespace generous (Patagonia)
- ✅ Use rounded corners (16px cards)
- ✅ Apply subtle shadows
- ✅ Use DM Sans at 500-700 weight
- ✅ Keep CTAs clear and actionable

### Don't
- ❌ Use pure black (#000000) for text
- ❌ Apply heavy shadows
- ❌ Use thin font weights (300) for headings
- ❌ Add gradients or textures
- ❌ Use emojis as icons
- ❌ Create cluttered layouts

---

*Design System v1.0 — PNW Outdoor Adventures*
*Inspired by Patagonia, Hipcamp, AllTrails*
