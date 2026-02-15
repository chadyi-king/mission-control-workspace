# ELLUMINATE — Design Strategy Document
**Project:** B6 — Elluminate Website  
**Phase:** 1 — Discovery  
**Date:** 2026-02-14  
**Designer:** FORGER

---

## 1. PROJECT SUMMARY

**Company:** Elluminate — Team building for schools, corporates, and government  
**Mission:** Generate leads, showcase activities, build credibility  
**Target:** HR managers, school admins, government coordinators  
**Vibe:** Energetic, Professional, Transformative  

---

## 2. COMPETITOR ANALYSIS

### Direct Competitors (Singapore)

| Competitor | Strengths | Weaknesses | Design Notes |
|------------|-----------|------------|--------------|
| **ActionTeams** | Clear service categories | Cluttered layout, dated design | Too text-heavy, busy UI |
| **Hidden.sg** | Fun, casual tone | Limited visual impact | Good FAQ section, playful copy |
| **TeamBonding.com** | Clean hierarchy, trust signals (35 years), clear CTAs | US-focused | Excellent "How It Works" section, strong testimonials |
| **Cohesion.sg** | Local credibility | Generic stock imagery | Average, forgettable design |

### Key Insights

**What competitors do WRONG:**
- Sites look dated (2015-era design)
- Too much text, not enough visuals
- Hard to find pricing/booking info
- Generic stock photos of "business people shaking hands"
- Poor mobile experience
- Slow loading times

**What competitors do RIGHT:**
- Clear activity descriptions
- Easy contact methods (WhatsApp/phone prominent)
- Client testimonials with photos
- "How It Works" process sections
- Trust signals (years in business, client logos)

**Elluminate's Opportunity:**
Be the modern, visually-striking alternative. Clean design + energetic imagery + frictionless contact = winning formula.

---

## 3. BRAND FOUNDATION

### Brand Personality
- **Energetic** — Movement, action, excitement
- **Professional** — Trusted, reliable, organized
- **Transformative** — Teams change, grow, improve

### The "Vibe" in Practice

| Element | Expression |
|---------|------------|
| **Energy** | Dynamic angles, action photography, micro-interactions |
| **Professional** | Clean layouts, clear typography, trust signals |
| **Transformative** | Before/after visuals, testimonials with results, progress indicators |

### Voice & Tone
- **Headlines:** Bold, confident, benefit-driven
- **Body:** Friendly but not casual, professional but not stiff
- **CTAs:** Action-oriented, low-commitment ("Get Quote" not "Buy Now")

---

## 4. COLOR SYSTEM

### Primary Palette

| Color | Hex | Usage | Psychology |
|-------|-----|-------|------------|
| **Forest Green** | `#2E5C4F` | Primary brand, headers, CTAs | Growth, nature, trust, teams |
| **Warm Orange** | `#F4A261` | Accents, hover states, energy | Action, enthusiasm, creativity |
| **Gold** | `#E9C46A` | Highlights, achievements, icons | Excellence, success, quality |

### Supporting Colors

| Color | Hex | Usage |
|-------|-----|-------|
| **Dark Green** | `#1A3D34` | Footer, dark sections |
| **Light Green** | `#4A7C6F` | Secondary buttons, links |
| **Cream** | `#FDF8F3` | Section backgrounds, cards |
| **Charcoal** | `#2D2D2D` | Body text |
| **White** | `#FFFFFF` | Primary background |

### Color Application Rules

1. **60-30-10 Rule:** 60% white/neutral, 30% forest green, 10% orange/gold accents
2. **CTAs:** Forest green primary, orange for secondary/hover
3. **Text:** Charcoal on light, white on dark green
4. **Never use:** Pure black (too harsh), corporate blue (too boring)

---

## 5. TYPOGRAPHY

### Font Stack

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| **Headings** | Inter | 700-800 | H1-H6, display text |
| **Body** | Inter | 400-500 | Paragraphs, descriptions |
| **Accent** | Inter | 600 | Labels, buttons, nav |

### Type Scale (Mobile → Desktop)

| Level | Mobile | Tablet | Desktop | Line Height |
|-------|--------|--------|---------|-------------|
| **H1** | 2.5rem | 3.5rem | 4rem | 1.1 |
| **H2** | 2rem | 2.5rem | 3rem | 1.2 |
| **H3** | 1.5rem | 1.75rem | 2rem | 1.3 |
| **H4** | 1.25rem | 1.25rem | 1.5rem | 1.4 |
| **Body Large** | 1.125rem | 1.125rem | 1.25rem | 1.6 |
| **Body** | 1rem | 1rem | 1rem | 1.6 |
| **Small** | 0.875rem | 0.875rem | 0.875rem | 1.5 |

### Typography Principles

1. **Bold headings** — High contrast for impact
2. **Generous line height** — 1.5-1.6 for readability
3. **Max-width for body** — 65ch for comfortable reading
4. **Consistent rhythm** — 8px baseline grid

---

## 6. IMAGERY STYLE

### Photography Guidelines

**DO:**
- Real people in action (laser tag, archery, gel blitz)
- Genuine emotions — laughter, focus, celebration
- Diverse teams (age, ethnicity, ability)
- Both indoor and outdoor settings
- Dynamic angles and movement
- Natural lighting when possible

**DON'T:**
- Generic stock photos of business handshakes
- Stiff, posed group photos
- Overly processed/filtered images
- Images without people (show the experience)

### Image Treatment

- **Slight warmth** in color grading (match orange accent)
- **High contrast** for energy
- **Consistent aspect ratios** within sections
- **Lazy loading** for performance

### Unsplash Keywords for Placeholders

- "team building activities"
- "laser tag game"
- "archery target"
- "corporate team outdoor"
- "group celebration"
- "school students activity"

---

## 7. LAYOUT PRINCIPLES

### Grid System
- **12-column grid** on desktop
- **4-column grid** on mobile
- **24px gutter** (16px on mobile)
- **Max container:** 1280px

### Spacing Scale (8px base)

| Token | Value | Usage |
|-------|-------|-------|
| `space-xs` | 8px | Tight spacing, icon gaps |
| `space-sm` | 16px | Component padding |
| `space-md` | 24px | Section element gaps |
| `space-lg` | 32px | Between components |
| `space-xl` | 48px | Section padding (mobile) |
| `space-2xl` | 64px | Section padding (desktop) |
| `space-3xl` | 96px | Major section breaks |

### Section Patterns

1. **Hero:** Full-width, impactful imagery, clear CTA
2. **Feature Grid:** 3-column cards with icons
3. **Testimonials:** Carousel or masonry grid
4. **Gallery:** Masonry or grid with lightbox
5. **Contact:** Split layout (form + info)

---

## 8. COMPONENT LIBRARY

### Buttons

**Primary Button (CTA)**
- Background: Forest Green (`#2E5C4F`)
- Text: White
- Padding: 16px 32px
- Border-radius: 8px
- Hover: Darken 10%, subtle scale(1.02)

**Secondary Button**
- Background: Transparent
- Border: 2px solid Forest Green
- Text: Forest Green
- Hover: Background Forest Green, text white

**WhatsApp Button (Floating)**
- Background: #25D366 (WhatsApp green)
- Position: Fixed bottom-right
- Size: 56px circle
- Shadow: Large, soft
- Animation: Subtle pulse

### Cards

**Service Card**
- White background
- Border-radius: 12px
- Shadow: 0 4px 6px rgba(0,0,0,0.1)
- Hover: Lift up, shadow increase
- Image top, content bottom

**Testimonial Card**
- Cream background (`#FDF8F3`)
- Quote icon (gold)
- Avatar + name + company
- Border-left: 4px gold accent

### Forms

**Input Fields**
- Border: 1px solid #E5E5E5
- Border-radius: 8px
- Padding: 12px 16px
- Focus: Border color Forest Green

**Contact Form Layout**
- 2-column on desktop
- Full-width on mobile
- Labels above inputs
- Required field indicators

---

## 9. INTERACTIONS & ANIMATIONS

### Micro-interactions

| Element | Trigger | Animation |
|---------|---------|-----------|
| Buttons | Hover | Scale 1.02, shadow increase |
| Cards | Hover | translateY(-4px), shadow deepen |
| Links | Hover | Color shift, underline slide-in |
| Images | Scroll into view | Fade up + scale from 0.95 |
| Icons | Hover | Subtle bounce or rotate |

### Scroll Animations
- **Reveal:** Elements fade up as they enter viewport
- **Stagger:** Card grids animate in sequence (50ms delay each)
- **Parallax:** Subtle on hero background (0.5 rate)

### Performance Rules
- Use `transform` and `opacity` only
- Respect `prefers-reduced-motion`
- Keep animations under 300ms for interactions
- Lazy-load images below the fold

---

## 10. SECTION BREAKDOWN

### 1. Navigation
- Sticky header on scroll
- Logo left, nav center/right, CTA button far right
- Mobile: Hamburger menu with slide-in drawer
- Height: 72px desktop, 64px mobile

### 2. Hero Section
- Full-viewport height (min 600px)
- Background: Video or carousel of activities
- Headline: "Team Building That Actually Works"
- Subheadline: "Laser tag, archery, gel blitz & more — customized for your team"
- Primary CTA: "Get a Quote" (scrolls to contact)
- Secondary CTA: "View Activities" (scrolls to services)
- Trust badges below: "Trusted by 100+ companies"

### 3. Services/Activities
- Section title: "Activities Your Team Will Love"
- 6 activity cards in 3x2 grid (2-col on mobile)
- Each card: Icon, title, short description, "Learn More" link
- Activities: Laser Tag, Archery, Gel Blitz, Nerf Wars, Drone Racing, Custom Challenges

### 4. Why Choose Us
- Section title: "Why Teams Trust Elluminate"
- 4-5 trust factors with icons
- Stats row: "500+ Events", "10,000+ Participants", "98% Satisfaction"

### 5. How It Works
- 4-step process visualization
- Step 1: Consultation → Step 2: Design → Step 3: Execute → Step 4: Follow-up
- Visual connector between steps
- Icons + brief descriptions

### 6. Testimonials
- Section title: "What Our Clients Say"
- 3-4 testimonial cards
- Include: Quote, client photo, name, company, result metric
- Optional: Carousel for mobile

### 7. Gallery
- Section title: " moments in Action"
- Masonry grid of event photos
- Lightbox on click
- Filter by activity type (optional)

### 8. Contact/Quote Form
- Section title: "Get Your Custom Quote"
- 2-column layout: Form left, contact info right
- Form fields: Name, Email, Company, Participants, Date, Activities (checkboxes), Budget, Message
- WhatsApp button prominent
- Phone number and email

### 9. Footer
- 4-column layout: Logo + about, Quick links, Services, Contact
- Social media icons
- Certification badges (safety, insurance)
- Copyright + privacy policy

---

## 11. TECHNICAL CONSIDERATIONS

### Performance Targets
- **First Contentful Paint:** < 1.5s
- **Largest Contentful Paint:** < 2.5s
- **Time to Interactive:** < 3.5s
- **Lighthouse Score:** 90+ all categories

### SEO Strategy
- **Primary keyword:** "team building singapore"
- **Secondary keywords:** "corporate team building", "school team building activities", "laser tag singapore", "team bonding activities"
- Meta tags, structured data (LocalBusiness), alt text for all images
- Semantic HTML (header, main, section, article, footer)

### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation
- Focus indicators
- Alt text for images
- Color contrast ratios (4.5:1 minimum)
- ARIA labels where needed

### Mobile-First Breakpoints
- **Mobile:** < 640px
- **Tablet:** 640px - 1024px
- **Desktop:** > 1024px
- **Large:** > 1280px

---

## 12. DESIGN DIRECTIONS (Phase 2 Preview)

I will create 3 distinct design directions:

### Direction A: "Bold & Energetic"
- Strong diagonal elements
- High-contrast imagery
- Dynamic typography
- Best for: Maximum impact, standing out

### Direction B: "Clean & Professional"
- Minimal, spacious layout
- Refined typography
- Subtle animations
- Best for: Corporate trust, sophistication

### Direction C: "Playful & Modern"
- Rounded elements
- Vibrant color accents
- Friendly illustrations (optional)
- Best for: Approachability, schools/younger teams

---

## 13. SUCCESS CRITERIA

**Design Quality Gates:**
- [ ] G1: Design principles (spacing, typography, color) consistent
- [ ] G2: Mobile responsive at all breakpoints
- [ ] G3: Performance (Lighthouse 90+)
- [ ] G4: Security (no vulnerabilities)
- [ ] G5: Brand consistency throughout

**Business Success Metrics:**
- [ ] Contact form submissions increase
- [ ] WhatsApp inquiries increase
- [ ] Time on site > 2 minutes
- [ ] Mobile traffic converts well
- [ ] Caleb approves: "This represents my brand"

---

## NEXT STEPS

1. ✅ **Phase 1 Complete** — Discovery & Strategy
2. 🔄 **Phase 2** — Create 3 design mockup directions
3. ⏳ **Phase 3** — Build approved design
4. ⏳ **Phase 4** — Deploy to Netlify

---

**FORGER:** *"Strategy complete. Ready to forge something extraordinary."*
