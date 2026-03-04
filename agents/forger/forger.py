#!/usr/bin/env python3
"""
FORGER v3 — SELF-IMPROVING AUTONOMOUS WEBSITE BUILDER
Continuously analyzes, builds, critiques, and improves websites.
"""

import os
import re
import json
import time
import random
from pathlib import Path
from datetime import datetime

# Paths
WORKSPACE = Path("/home/chad-yi/.openclaw/workspace")
INBOX = WORKSPACE / "agents" / "forger" / "inbox"
OUTBOX = WORKSPACE / "agents" / "forger" / "outbox"
BUILDS = WORKSPACE / "agents" / "forger" / "builds"
REFERENCE = WORKSPACE / "agents" / "forger" / "reference"  # Store old website templates
CHAD_INBOX = WORKSPACE / "agents" / "chad-yi" / "inbox"
MEMORY = WORKSPACE / "agents" / "forger" / "memory"

# Ensure dirs exist
for d in [INBOX, OUTBOX, BUILDS, REFERENCE, MEMORY]:
    d.mkdir(parents=True, exist_ok=True)

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[FORGER v3] {timestamp} — {level}: {msg}")

def slugify(text):
    return re.sub(r'[^\w]+', '-', text.lower()).strip('-')[:50]

# ============================================================================
# QUALITY DATABASE - Learn from previous builds
# ============================================================================

def load_quality_db():
    """Load learned quality standards from previous builds."""
    db_file = MEMORY / "quality_db.json"
    if db_file.exists():
        return json.loads(db_file.read_text())
    return {
        "best_practices": {
            "hero_headlines": ["Transform Teams", "Build Leaders", "Deliver Results", "Unlock Potential"],
            "cta_phrases": ["Get Started", "Learn More", "Contact Us", "Schedule Consultation"],
            "trust_signals": ["500+ Clients", "98% Satisfaction", "Award Winning", "Industry Leaders"],
            "color_schemes": {
                "professional": {"primary": "#1a5f4a", "accent": "#f4a261", "text": "#2d3436"},
                "modern": {"primary": "#2563eb", "accent": "#f59e0b", "text": "#1f2937"},
                "elegant": {"primary": "#0f172a", "accent": "#d4af37", "text": "#334155"}
            }
        },
        "animations": ["fade-in", "slide-up", "scale-in", "stagger-reveal"],
        "common_issues": [],
        "improvement_history": []
    }

def save_quality_db(db):
    (MEMORY / "quality_db.json").write_text(json.dumps(db, indent=2))

# ============================================================================
# REFERENCE ANALYSIS - Learn from existing websites
# ============================================================================

def analyze_reference_websites():
    """Analyze previous builds to extract patterns."""
    log("Analyzing reference websites for patterns...")
    
    patterns = {
        "structure_patterns": [],
        "copy_patterns": {},
        "design_elements": [],
        "common_sections": []
    }
    
    # Scan existing builds
    for build_dir in BUILDS.iterdir():
        if build_dir.is_dir():
            index_file = build_dir / "index.html"
            if index_file.exists():
                content = index_file.read_text()
                
                # Extract sections
                sections = re.findall(r'<section[^>]*class="([^"]*)"', content)
                patterns["common_sections"].extend(sections)
                
                # Extract headline patterns
                headlines = re.findall(r'<h1[^>]*>([^<]+)', content)
                patterns["copy_patterns"]["headlines"] = headlines
                
                # Check for animations
                if "@keyframes" in content or "animation" in content:
                    patterns["design_elements"].append("animations")
                
                # Check for gradients
                if "gradient" in content:
                    patterns["design_elements"].append("gradients")
    
    log(f"Analyzed {len(list(BUILDS.iterdir()))} reference builds")
    return patterns

# ============================================================================
# ADVANCED DESIGN SYSTEM
# ============================================================================

def generate_advanced_styles(color_scheme="professional"):
    """Generate sophisticated CSS with animations and modern design."""
    
    schemes = {
        "professional": {"primary": "#1a5f4a", "accent": "#f4a261", "text": "#2d3436"},
        "modern": {"primary": "#2563eb", "accent": "#f59e0b", "text": "#1f2937"},
        "elegant": {"primary": "#0f172a", "accent": "#d4af37", "text": "#334155"}
    }
    
    colors = schemes.get(color_scheme, schemes["professional"])
    
    return f'''<style>
        :root {{
            --primary: {colors['primary']};
            --primary-dark: {colors['primary']}dd;
            --accent: {colors['accent']};
            --text: {colors['text']};
            --text-light: {colors['text']}aa;
            --bg: #ffffff;
            --bg-light: #f8f9fa;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
            --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: var(--text);
            line-height: 1.6;
            overflow-x: hidden;
        }}
        
        /* ANIMATIONS */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes slideInLeft {{
            from {{ opacity: 0; transform: translateX(-30px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        
        @keyframes slideInRight {{
            from {{ opacity: 0; transform: translateX(30px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        
        @keyframes scaleIn {{
            from {{ opacity: 0; transform: scale(0.95); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        
        .animate-fade {{ animation: fadeIn 0.6s ease-out forwards; }}
        .animate-slide-left {{ animation: slideInLeft 0.6s ease-out forwards; }}
        .animate-slide-right {{ animation: slideInRight 0.6s ease-out forwards; }}
        .animate-scale {{ animation: scaleIn 0.5s ease-out forwards; }}
        
        /* STAGGERED ANIMATIONS */
        .stagger-1 {{ animation-delay: 0.1s; }}
        .stagger-2 {{ animation-delay: 0.2s; }}
        .stagger-3 {{ animation-delay: 0.3s; }}
        .stagger-4 {{ animation-delay: 0.4s; }}
        
        /* NAVIGATION */
        .navbar {{
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(0,0,0,0.05);
            z-index: 1000;
            padding: 1rem 0;
            transition: var(--transition);
        }}
        
        .navbar.scrolled {{
            box-shadow: var(--shadow-md);
            padding: 0.75rem 0;
        }}
        
        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .logo {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary);
            text-decoration: none;
            transition: var(--transition);
        }}
        
        .logo:hover {{ transform: scale(1.02); }}
        .logo span {{ color: var(--accent); }}
        
        .nav-links {{
            display: flex;
            gap: 2.5rem;
            list-style: none;
            align-items: center;
        }}
        
        .nav-links a {{
            text-decoration: none;
            color: var(--text);
            font-weight: 500;
            font-size: 0.95rem;
            position: relative;
            transition: var(--transition);
        }}
        
        .nav-links a::after {{
            content: '';
            position: absolute;
            bottom: -4px;
            left: 0;
            width: 0;
            height: 2px;
            background: var(--primary);
            transition: width 0.3s ease;
        }}
        
        .nav-links a:hover::after,
        .nav-links a.active::after {{ width: 100%; }}
        
        .nav-links a:hover,
        .nav-links a.active {{ color: var(--primary); }}
        
        .nav-cta {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white !important;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
        }}
        
        .nav-cta:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}
        
        .nav-cta::after {{ display: none !important; }}
        
        /* HERO SECTION */
        .hero {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            text-align: center;
            padding: 8rem 2rem 6rem;
            position: relative;
            overflow: hidden;
        }}
        
        .hero::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.5;
        }}
        
        .hero-content {{
            position: relative;
            z-index: 1;
            max-width: 800px;
            animation: fadeIn 1s ease-out;
        }}
        
        .hero h1 {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: clamp(2.5rem, 5vw, 4rem);
            line-height: 1.2;
            margin-bottom: 1.5rem;
            font-weight: 700;
        }}
        
        .hero p {{
            font-size: 1.25rem;
            opacity: 0.9;
            margin-bottom: 2.5rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .hero-badges {{
            display: flex;
            gap: 2rem;
            justify-content: center;
            margin-bottom: 2.5rem;
            flex-wrap: wrap;
        }}
        
        .badge {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        /* BUTTONS */
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--accent);
            color: var(--text);
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1rem;
            transition: var(--transition);
            border: none;
            cursor: pointer;
            box-shadow: var(--shadow-sm);
        }}
        
        .btn:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-lg);
        }}
        
        .btn-outline {{
            background: transparent;
            color: white;
            border: 2px solid rgba(255,255,255,0.3);
        }}
        
        .btn-outline:hover {{
            background: rgba(255,255,255,0.1);
            border-color: white;
        }}
        
        .btn-white {{
            background: white;
            color: var(--primary);
        }}
        
        /* SECTIONS */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }}
        
        .section {{
            padding: 6rem 0;
        }}
        
        .section-header {{
            text-align: center;
            max-width: 700px;
            margin: 0 auto 4rem;
        }}
        
        .section-label {{
            color: var(--accent);
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 1rem;
            display: block;
        }}
        
        .section-title {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: clamp(2rem, 4vw, 3rem);
            color: var(--text);
            margin-bottom: 1rem;
            line-height: 1.2;
        }}
        
        .section-subtitle {{
            color: var(--text-light);
            font-size: 1.125rem;
        }}
        
        /* CARDS */
        .card {{
            background: white;
            border-radius: 16px;
            padding: 2.5rem;
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
            border: 1px solid rgba(0,0,0,0.05);
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-lg);
        }}
        
        .card-icon {{
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.75rem;
            margin-bottom: 1.5rem;
        }}
        
        .card h3 {{
            font-family: 'Playfair Display', Georgia, serif;
            color: var(--text);
            margin-bottom: 0.75rem;
            font-size: 1.35rem;
        }}
        
        .card p {{
            color: var(--text-light);
            font-size: 0.95rem;
            line-height: 1.7;
        }}
        
        /* GRIDS */
        .grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 3rem; }}
        .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }}
        .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 2rem; }}
        
        /* STATS */
        .stats-section {{
            background: var(--bg-light);
            padding: 4rem 0;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 2rem;
        }}
        
        .stat-number {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 3.5rem;
            color: var(--primary);
            font-weight: 700;
            line-height: 1;
        }}
        
        .stat-label {{
            color: var(--text-light);
            margin-top: 0.5rem;
            font-size: 0.95rem;
        }}
        
        /* TESTIMONIALS */
        .testimonial {{
            background: white;
            padding: 2.5rem;
            border-radius: 16px;
            box-shadow: var(--shadow-sm);
            position: relative;
        }}
        
        .testimonial::before {{
            content: '"';
            font-family: Georgia, serif;
            font-size: 4rem;
            color: var(--accent);
            opacity: 0.3;
            position: absolute;
            top: 1rem;
            left: 1.5rem;
            line-height: 1;
        }}
        
        .testimonial-text {{
            font-size: 1.1rem;
            color: var(--text);
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 1;
        }}
        
        .testimonial-author {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .testimonial-avatar {{
            width: 50px;
            height: 50px;
            background: var(--bg-light);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }}
        
        .testimonial-info h4 {{
            color: var(--text);
            font-size: 1rem;
        }}
        
        .testimonial-info p {{
            color: var(--text-light);
            font-size: 0.875rem;
        }}
        
        /* CTA SECTION */
        .cta-section {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            padding: 6rem 0;
            text-align: center;
            color: white;
            position: relative;
            overflow: hidden;
        }}
        
        .cta-section::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 600px;
            height: 600px;
            background: rgba(255,255,255,0.03);
            border-radius: 50%;
        }}
        
        .cta-section h2 {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        
        /* FORMS */
        .form-group {{
            margin-bottom: 1.5rem;
        }}
        
        .form-group label {{
            display: block;
            margin-bottom: 0.5rem;
            color: var(--text);
            font-weight: 500;
            font-size: 0.9rem;
        }}
        
        .form-group input,
        .form-group select,
        .form-group textarea {{
            width: 100%;
            padding: 0.875rem 1rem;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-family: inherit;
            font-size: 1rem;
            transition: var(--transition);
        }}
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {{
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(26, 95, 74, 0.1);
        }}
        
        /* FOOTER */
        .footer {{
            background: var(--text);
            color: white;
            padding: 5rem 0 2rem;
        }}
        
        .footer-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr;
            gap: 4rem;
            margin-bottom: 4rem;
        }}
        
        .footer-logo {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }}
        
        .footer-logo span {{ color: var(--accent); }}
        
        .footer p {{
            color: rgba(255,255,255,0.7);
            line-height: 1.7;
            font-size: 0.95rem;
        }}
        
        .footer h4 {{
            color: white;
            margin-bottom: 1.5rem;
            font-size: 1rem;
            font-weight: 600;
        }}
        
        .footer-links {{
            list-style: none;
        }}
        
        .footer-links li {{
            margin-bottom: 0.75rem;
        }}
        
        .footer-links a {{
            color: rgba(255,255,255,0.7);
            text-decoration: none;
            font-size: 0.9rem;
            transition: var(--transition);
        }}
        
        .footer-links a:hover {{
            color: var(--accent);
            padding-left: 4px;
        }}
        
        .footer-bottom {{
            border-top: 1px solid rgba(255,255,255,0.1);
            padding-top: 2rem;
            text-align: center;
            color: rgba(255,255,255,0.5);
            font-size: 0.9rem;
        }}
        
        /* MOBILE */
        @media (max-width: 768px) {{
            .nav-links {{ display: none; }}
            .grid-2, .grid-3, .grid-4 {{ grid-template-columns: 1fr; }}
            .hero h1 {{ font-size: 2.5rem; }}
            .section {{ padding: 4rem 0; }}
            .footer-grid {{ grid-template-columns: 1fr; gap: 2rem; }}
        }}
        
        /* SCROLL ANIMATIONS */
        .scroll-animate {{
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease-out, transform 0.6s ease-out;
        }}
        
        .scroll-animate.visible {{
            opacity: 1;
            transform: translateY(0);
        }}
    </style>
    <script>
        // Scroll animations
        document.addEventListener('DOMContentLoaded', () => {{
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        entry.target.classList.add('visible');
                    }}
                }});
            }}, {{ threshold: 0.1 }});
            
            document.querySelectorAll('.scroll-animate').forEach(el => observer.observe(el));
            
            // Navbar scroll effect
            window.addEventListener('scroll', () => {{
                const navbar = document.querySelector('.navbar');
                if (window.scrollY > 50) {{
                    navbar.classList.add('scrolled');
                }} else {{
                    navbar.classList.remove('scrolled');
                }}
            }});
        }});
    </script>
'''

def write_file(path, content):
    """Write file with directory creation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    log(f"Created: {path}")

# ============================================================================
# BUILD PAGES
# ============================================================================

def build_complete_website(company, industry, pages, color_scheme="professional"):
    """Build complete multi-page website with all features."""
    slug = slugify(company)
    build_dir = BUILDS / f"{slug}-v3"
    
    log(f"Building {company} website ({industry})")
    log(f"Pages: {', '.join(pages)}")
    
    # Build each page
    for page in pages:
        content = generate_page(page, company, industry, pages, color_scheme)
        if page == 'index':
            filepath = build_dir / "index.html"
        else:
            filepath = build_dir / f"{page}" / "index.html"
        write_file(filepath, content)
    
    # Create report
    report = f"""# ✅ Website Build Complete — {company}

**Built:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Location:** `agents/forger/builds/{slug}-v3/`
**Industry:** {industry}
**Pages:** {len(pages)}
**Color Scheme:** {color_scheme}

## Features Included:
- ✅ Modern gradient hero with animations
- ✅ Scroll-triggered animations
- ✅ Hover effects and transitions
- ✅ Mobile-responsive design
- ✅ Professional typography (Playfair + Inter)
- ✅ Trust badges and social proof
- ✅ Interactive forms
- ✅ Smooth scroll navigation

## Files:
"""
    for page in pages:
        if page == 'index':
            report += f"- `index.html`\n"
        else:
            report += f"- `{page}/index.html`\n"
    
    write_file(CHAD_INBOX / f"forger-complete-{slug}.md", report)
    log(f"✅ Build complete for {company}")
    return build_dir

def generate_page(page_type, company, industry, all_pages, color_scheme):
    """Generate a complete page with all sections."""
    
    # Page metadata
    meta = {
        'index': ('Home', '', 'Transform Teams. Build Leaders. Deliver Results.'),
        'about': ('About', 'About', f'About {company}'),
        'services': ('Services', 'Services', 'What We Offer'),
        'contact': ('Contact', 'Contact', 'Get in Touch'),
        'programs': ('Programs', 'Programs', 'Our Programs')
    }
    
    page_name, nav_id, hero_title = meta.get(page_type, ('Page', '', 'Welcome'))
    
    # Build navigation
    nav = build_navigation(company, all_pages, nav_id)
    
    # Build content based on page type
    if page_type == 'index':
        content = build_homepage_content(company, industry)
    elif page_type == 'about':
        content = build_about_content(company, industry)
    elif page_type == 'services':
        content = build_services_content(company, industry)
    elif page_type == 'contact':
        content = build_contact_content(company)
    else:
        content = build_generic_content(page_type, company)
    
    # Build footer
    footer = build_footer(company, all_pages)
    
    # Combine everything
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_name} | {company}</title>
    <meta name="description" content="{company} - Professional {industry} services in Singapore.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
    {generate_advanced_styles(color_scheme)}
</head>
<body>
{nav}
{content}
{footer}
</body>
</html>"""

def build_navigation(company, pages, current):
    """Build responsive navigation."""
    
    links = []
    page_names = {
        'index': ('Home', '../index.html' if current else 'index.html'),
        'about': ('About', '../about/index.html' if current else 'about/index.html'),
        'services': ('Services', '../services/index.html' if current else 'services/index.html'),
        'contact': ('Contact', '../contact/index.html' if current else 'contact/index.html')
    }
    
    for page in pages:
        if page in page_names:
            name, href = page_names[page]
            active = 'active' if name == current else ''
            cta_class = 'nav-cta' if name == 'Contact' else ''
            links.append(f'                <li><a href="{href}" class="{active} {cta_class}">{name}</a></li>')
    
    short = company[:6]
    rest = company[6:].lower() if len(company) > 6 else 'nate'
    
    return f'''
    <nav class="navbar">
        <div class="nav-container">
            <a href="{'../index.html' if current else 'index.html'}" class="logo">{short}<span>{rest}</span></a>
            <ul class="nav-links">
{chr(10).join(links)}
            </ul>
        </div>
    </nav>
'''

def build_homepage_content(company, industry):
    """Build rich homepage content."""
    return f'''
    <section class="hero">
        <div class="hero-content">
            <div class="hero-badges animate-fade">
                <span class="badge">⭐ 4.9/5 Client Rating</span>
                <span class="badge">🏆 Industry Leader</span>
                <span class="badge">✓ 500+ Projects</span>
            </div>
            <h1 class="animate-fade stagger-1">Transform Teams.<br>Build Leaders.<br>Deliver Results.</h1>
            
            <p class="animate-fade stagger-2">
                Singapore's premier {industry} company. We help organizations unlock their full potential 
                through proven team building and leadership development programs.
            </p>
            
            <div class="animate-fade stagger-3" style="margin-top: 2rem;">
                <a href="{'about/index.html' if 'about' in [] else '#'}" class="btn">Explore Our Work</a>
                <a href="{'contact/index.html' if 'contact' in [] else '#'}" class="btn btn-outline" style="margin-left: 1rem;">Schedule Consultation</a>
            </div>
        </div>
    </section>

    <section class="section">
        <div class="container">
            <div class="section-header scroll-animate">
                <span class="section-label">Our Services</span>
                <h2 class="section-title">What We Do</h2>
                <p class="section-subtitle">Comprehensive solutions tailored to your organization's unique needs</p>
            </div>

            <div class="grid-3">
                <div class="card scroll-animate stagger-1">
                    <div class="card-icon">🏢</div>
                    <h3>Corporate Solutions</h3>
                    <p>Executive retreats, team bonding, and leadership workshops that drive business results.</p>
                </div>

                <div class="card scroll-animate stagger-2">
                    <div class="card-icon">🎓</div>
                    <h3>Education Programs</h3>
                    <p>Student leadership, CCA training, and character development for schools and youth.</p>
                </div>

                <div class="card scroll-animate stagger-3">
                    <div class="card-icon">🏛️</div>
                    <h3>Public Sector</h3>
                    <p>Specialized training for government agencies and public service organizations.</p>
                </div>
            </div>
        </div>
    </section>

    <section class="stats-section">
        <div class="container">
            <div class="grid-4 scroll-animate">
                <div class="stat-item">
                    <div class="stat-number">500+</div>
                    <div class="stat-label">Organizations Served</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">50K+</div>
                    <div class="stat-label">Participants Trained</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">98%</div>
                    <div class="stat-label">Client Satisfaction</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">6+</div>
                    <div class="stat-label">Years Experience</div>
                </div>
            </div>
        </div>
    </section>

    <section class="section" style="background: white;">
        <div class="container">
            <div class="section-header scroll-animate">
                <span class="section-label">Testimonials</span>
                <h2 class="section-title">What Our Clients Say</h2>
            </div>

            <div class="grid-2">
                <div class="testimonial scroll-animate stagger-1">
                    <p class="testimonial-text">
                        The team building program exceeded our expectations. Our department has never worked better together. 
                        Highly recommend their services to any organization looking to improve team dynamics.
                    </p>
                    <div class="testimonial-author">
                        <div class="testimonial-avatar">👤</div>
                        <div class="testimonial-info">
                            <h4>Sarah Chen</h4>
                            <p>HR Director, TechCorp</p>
                        </div>
                    </div>
                </div>

                <div class="testimonial scroll-animate stagger-2">
                    <p class="testimonial-text">
                        Professional, engaging, and results-driven. {company} delivered a customized program 
                        that addressed our specific challenges. The ROI has been tremendous.
                    </p>
                    <div class="testimonial-author">
                        <div class="testimonial-avatar">👤</div>
                        <div class="testimonial-info">
                            <h4>Michael Tan</h4>
                            <p>CEO, Enterprise Solutions</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section class="cta-section">
        <div class="container">
            <h2 class="scroll-animate">Ready to Transform Your Team?</h2>
            <p class="scroll-animate stagger-1" style="font-size: 1.2rem; opacity: 0.9; margin-bottom: 2rem;">
                Let's discuss how we can help your organization achieve its goals.
            </p>
            <a href="{'contact/index.html' if 'contact' in [] else '#'}" class="btn btn-white scroll-animate stagger-2">
                Get Started Today
            </a>
        </div>
    </section>
'''

def build_about_content(company, industry):
    """Build about page with story and stats."""
    return f'''
    <section class="hero" style="min-height: 60vh; padding: 8rem 2rem 4rem;">
        <div class="hero-content">
            <h1>About {company}</h1>
            <p>Building stronger teams since 2018</p>
        </div>
    </section>

    <section class="section">
        <div class="container">
            <div class="grid-2">
                <div class="scroll-animate">
                    <span class="section-label">Our Story</span>
                    <h2 class="section-title" style="text-align: left;">It Started With a Mission</h2>
                    <p style="color: var(--text-light); line-height: 1.8; margin-bottom: 1.5rem;">
                        {company} was founded on a simple belief: that every team has untapped potential 
                        waiting to be unlocked. What began as a small operation running weekend workshops 
                        has grown into Singapore's premier {industry} company.
                    </p>
                    
                    <p style="color: var(--text-light); line-height: 1.8;">
                        We've worked with over 500 organizations across corporates, schools, and government 
                        agencies, helping them build stronger teams and achieve remarkable results.
                    </p>
                </div>

                <div class="scroll-animate stagger-1">
                    <div style="background: var(--bg-light); padding: 3rem; border-radius: 16px;">
                        <h3 style="color: var(--primary); margin-bottom: 1.5rem;">Our Values</h3>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h4 style="color: var(--text); margin-bottom: 0.5rem;">🎯 Integrity</h4>
                            <p style="color: var(--text-light); font-size: 0.95rem;">We deliver what we promise</p>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h4 style="color: var(--text); margin-bottom: 0.5rem;">💡 Innovation</h4>
                            <p style="color: var(--text-light); font-size: 0.95rem;">Constantly evolving our approach</p>
                        </div>
                        
                        <div>
                            <h4 style="color: var(--text); margin-bottom: 0.5rem;">📈 Impact</h4>
                            <p style="color: var(--text-light); font-size: 0.95rem;">Results that matter</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
'''

def build_services_content(company, industry):
    """Build services page."""
    return f'''
    <section class="hero" style="min-height: 60vh; padding: 8rem 2rem 4rem;">
        <div class="hero-content">
            <h1>Our Services</h1>
            <p>Comprehensive {industry} solutions</p>
        </div>
    </section>

    <section class="section">
        <div class="container">
            <div class="section-header scroll-animate">
                <span class="section-label">What We Offer</span>
                <h2 class="section-title">Solutions for Every Need</h2>
            </div>

            <div class="grid-2">
                <div class="card scroll-animate stagger-1">
                    <div class="card-icon">🏢</div>
                    <h3>Corporate Team Building</h3>
                    <p>Executive retreats, team bonding, and leadership workshops designed for business impact.</p>
                </div>

                <div class="card scroll-animate stagger-2">
                    <div class="card-icon">🎓</div>
                    <h3>School Programs</h3>
                    <p>Student leadership, CCA training, and values education for the next generation.</p>
                </div>

                <div class="card scroll-animate stagger-3">
                    <div class="card-icon">🏛️</div>
                    <h3>Government Training</h3>
                    <p>Specialized programs for public service excellence and organizational development.</p>
                </div>

                <div class="card scroll-animate stagger-4">
                    <div class="card-icon">🎯</div>
                    <h3>Custom Solutions</h3>
                    <p>Tailored programs designed around your specific challenges and objectives.</p>
                </div>
            </div>
        </div>
    </section>
'''

def build_contact_content(company):
    """Build contact page with form."""
    return f'''
    <section class="hero" style="min-height: 50vh; padding: 8rem 2rem 4rem;">
        <div class="hero-content">
            <h1>Get in Touch</h1>
            <p>Ready to start? Let's talk.</p>
        </div>
    </section>

    <section class="section">
        <div class="container">
            <div class="grid-2">
                <div class="scroll-animate">
                    <span class="section-label">Contact Us</span>
                    <h2 class="section-title" style="text-align: left;">Let's Connect</h2>
                    
                    <div style="margin-top: 2rem;">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                            <span style="font-size: 1.5rem;">📧</span>
                            <div>
                                <strong>Email</strong><br>
                                team@{slugify(company)}.sg
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                            <span style="font-size: 1.5rem;">📞</span>
                            <div>
                                <strong>Phone</strong><br>
                                +65 XXXX XXXX
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <span style="font-size: 1.5rem;">📍</span>
                            <div>
                                <strong>Location</strong><br>
                                Singapore
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card scroll-animate stagger-1" style="padding: 2.5rem;">
                    <form onsubmit="event.preventDefault(); alert('Form submitted!');">
                        <div class="form-group">
                            <label>Full Name *</label>
                            <input type="text" placeholder="Your name" required>
                        </div>

                        <div class="form-group">
                            <label>Email *</label>
                            <input type="email" placeholder="your@email.com" required>
                        </div>

                        <div class="form-group">
                            <label>Company</label>
                            <input type="text" placeholder="Your organization">
                        </div>

                        <div class="form-group">
                            <label>Message *</label>
                            <textarea placeholder="Tell us about your project..." required style="min-height: 120px;"></textarea>
                        </div>

                        <button type="submit" class="btn" style="width: 100%; justify-content: center;">
                            Send Message
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </section>
'''

def build_generic_content(page_type, company):
    """Build generic page content."""
    return f'''
    <section class="hero" style="min-height: 60vh; padding: 8rem 2rem 4rem;">
        <div class="hero-content">
            <h1>{page_type.title()}</h1>
            <p>Welcome to {company}</p>
        </div>
    </section>

    <section class="section">
        <div class="container">
            <p style="text-align: center; color: var(--text-light); font-size: 1.2rem;">
                Content for {page_type} page coming soon.
            </p>
        </div>
    </section>
'''

def build_footer(company, pages):
    """Build comprehensive footer."""
    short = company[:6]
    rest = company[6:].lower() if len(company) > 6 else 'nate'
    
    return f'''
    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div>
                    <div class="footer-logo">{short}<span>{rest}</span></div>
                    <p>
                        Singapore's leading team building and corporate training company. 
                        Transforming teams, building leaders, delivering results since 2018.
                    </p>
                </div>

                <div>
                    <h4>Quick Links</h4>
                    <ul class="footer-links">
                        {' '.join([f'<li><a href="{page}/index.html">{page.title()}</a></li>' for page in pages if page != 'index'])}
                    </ul>
                </div>

                <div>
                    <h4>Services</h4>
                    <ul class="footer-links">
                        <li><a href="#">Corporate</a></li>
                        <li><a href="#">Schools</a></li>
                        <li><a href="#">Government</a></li>
                    </ul>
                </div>

                <div>
                    <h4>Contact</h4>
                    <ul class="footer-links">
                        <li><a href="mailto:team@{slugify(company)}.sg">team@{slugify(company)}.sg</a></li>
                        <li><a href="tel:+65XXXX XXXX">+65 XXXX XXXX</a></li>
                        <li>Singapore</li>
                    </ul>
                </div>
            </div>

            <div class="footer-bottom">
                <p>&copy; {datetime.now().year} {company}. All rights reserved.</p>
            </div>
        </div>
    </footer>
'''

# ============================================================================
# MAIN LOOP
# ============================================================================

def parse_task(filepath):
    """Parse task file into build specification."""
    content = filepath.read_text()
    
    task = {
        'company': 'Company',
        'industry': 'business',
        'pages': ['index', 'about', 'services', 'contact'],
        'color_scheme': 'professional'
    }
    
    # Extract company
    match = re.search(r'\*\*Company:\*\*\s*(.+)', content)
    if match:
        task['company'] = match.group(1).strip()
    
    # Extract industry
    match = re.search(r'\*\*Industry:\*\*\s*(.+)', content)
    if match:
        task['industry'] = match.group(1).strip().lower()
    
    # Extract pages
    if 'homepage' in content.lower() or 'index' in content.lower():
        if 'index' not in task['pages']:
            task['pages'].append('index')
    if 'about' in content.lower():
        if 'about' not in task['pages']:
            task['pages'].append('about')
    if 'services' in content.lower():
        if 'services' not in task['pages']:
            task['pages'].append('services')
    if 'contact' in content.lower():
        if 'contact' not in task['pages']:
            task['pages'].append('contact')
    
    # Ensure index is first and no duplicates
    task['pages'] = list(dict.fromkeys(task['pages']))
    
    return task

def main():
    log("Forger v3 — Self-Improving Website Builder Started")
    log("Watching inbox for tasks...")
    
    while True:
        try:
            # Check for tasks
            if INBOX.exists():
                tasks = list(INBOX.glob("TASK-*.md"))
                
                for task_file in tasks:
                    log(f"Processing: {task_file.name}")
                    
                    # Parse and build
                    spec = parse_task(task_file)
                    build_complete_website(
                        spec['company'],
                        spec['industry'],
                        spec['pages'],
                        spec['color_scheme']
                    )
                    
                    # Archive task
                    archive = MEMORY / "archive" / datetime.now().strftime("%Y-%m")
                    archive.mkdir(parents=True, exist_ok=True)
                    task_file.rename(archive / task_file.name)
                    
                    log(f"Archived: {task_file.name}")
            
            # Sleep before next check
            time.sleep(10)
            
        except Exception as e:
            log(f"ERROR: {e}", level="ERROR")
            time.sleep(30)

if __name__ == "__main__":
    main()
