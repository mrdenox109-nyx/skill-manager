#!/usr/bin/env python3
"""
Skill Manager — Project Analysis Script

Detects project tech stack and scores installed Claude Code skills by relevance.
Python 3.9+, zero external dependencies.

Usage:
    python3 analyze_project.py --detect-stack /path/to/project
    python3 analyze_project.py --analyze /path/to/project
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Universal skills — never disabled regardless of project type
# ---------------------------------------------------------------------------
UNIVERSAL_SKILLS = frozenset({
    "find-skills",
    "skill-creator",
    "writing-skills",
    "brainstorming",
    "writing-plans",
    "test-driven-development",
    "dispatching-parallel-agents",
    "subagent-driven-development",
    "using-superpowers",
    "agentation",
    "skill-manager",
})

# ---------------------------------------------------------------------------
# Domain definitions: which skills belong to which tech domain
# ---------------------------------------------------------------------------
IOS_MACOS_SKILLS = frozenset({
    "mobile-ios-design",
    "asc-xcode-build",
    "asc-metadata-sync",
    "asc-localize-metadata",
    "asc-subscription-localization",
    "asc-ppp-pricing",
    "asc-shots-pipeline",
    "asc-notarization",
    "app-store-optimization",
    "aso-full-audit",
    "aso-optimize",
    "aso-competitor",
    "aso-prelaunch",
    "aso",
})

WEB_SAAS_SKILLS = frozenset({
    "page-cro",
    "signup-flow-cro",
    "onboarding-cro",
    "popup-cro",
    "form-cro",
    "copywriting",
    "copy-editing",
    "content-strategy",
    "seo-audit",
    "programmatic-seo",
    "schema-markup",
    "analytics-tracking",
    "ab-test-setup",
    "email-sequence",
    "social-content",
    "marketing-ideas",
    "marketing-psychology",
    "free-tool-strategy",
    "launch-strategy",
    "paid-ads",
    "referral-program",
    "pricing-strategy",
    "competitor-alternatives",
    "audit-website",
})

PAYMENT_SKILLS = frozenset({
    "stripe-integration",
    "paywall-upgrade-cro",
    "churn-prevention",
})

MEDIA_SKILLS = frozenset({
    "fal-audio",
    "fal-generate",
    "fal-image-edit",
    "fal-platform",
    "fal-upscale",
    "fal-workflow",
    "remotion-best-practices",
})

# Marketing subset that gets "useful" instead of "irrelevant" in non-web projects
MARKETING_CROSS_PLATFORM = frozenset({
    "copywriting",
    "copy-editing",
    "marketing-ideas",
    "marketing-psychology",
    "content-strategy",
    "email-sequence",
    "social-content",
    "launch-strategy",
    "pricing-strategy",
    "competitor-alternatives",
})

# ---------------------------------------------------------------------------
# Stack detection
# ---------------------------------------------------------------------------

def detect_stack(project_path: str) -> dict:
    """Detect the project's tech stack from files and dependencies."""
    root = Path(project_path)
    stack = {
        "primary": "",
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "signals": {},
        "dependencies": [],
    }

    languages = set()
    frameworks = set()
    platforms = set()
    deps = set()

    # --- File-based signals ---
    signal_checks = {
        "package.json": root / "package.json",
        "tsconfig.json": root / "tsconfig.json",
        "Podfile": root / "Podfile",
        "Package.swift": root / "Package.swift",
        "Cargo.toml": root / "Cargo.toml",
        "go.mod": root / "go.mod",
        "requirements.txt": root / "requirements.txt",
        "pyproject.toml": root / "pyproject.toml",
        "setup.py": root / "setup.py",
        "Gemfile": root / "Gemfile",
        "composer.json": root / "composer.json",
        "build.gradle": root / "build.gradle",
        "build.gradle.kts": root / "build.gradle.kts",
        "pubspec.yaml": root / "pubspec.yaml",
        "Dockerfile": root / "Dockerfile",
        "docker-compose.yml": root / "docker-compose.yml",
        "vercel.json": root / "vercel.json",
        "netlify.toml": root / "netlify.toml",
    }

    for name, path in signal_checks.items():
        stack["signals"][name] = path.exists()

    # Check for .xcodeproj directories
    xcodeproj_dirs = list(root.glob("*.xcodeproj"))
    stack["signals"]["*.xcodeproj"] = len(xcodeproj_dirs) > 0

    # --- Parse package.json ---
    pkg_path = root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            all_deps = {}
            for key in ("dependencies", "devDependencies", "peerDependencies"):
                all_deps.update(pkg.get(key, {}))
            deps.update(all_deps.keys())

            languages.add("JavaScript")
            if stack["signals"].get("tsconfig.json"):
                languages.add("TypeScript")

            # Framework detection from deps
            framework_map = {
                "next": ("Next.js", "Web"),
                "react": ("React", "Web"),
                "vue": ("Vue.js", "Web"),
                "@angular/core": ("Angular", "Web"),
                "svelte": ("Svelte", "Web"),
                "@sveltejs/kit": ("SvelteKit", "Web"),
                "nuxt": ("Nuxt.js", "Web"),
                "gatsby": ("Gatsby", "Web"),
                "astro": ("Astro", "Web"),
                "express": ("Express", "Web"),
                "fastify": ("Fastify", "Web"),
                "hono": ("Hono", "Web"),
                "react-native": ("React Native", "Mobile"),
                "expo": ("Expo", "Mobile"),
                "electron": ("Electron", "Desktop"),
                "tauri": ("Tauri", "Desktop"),
                "remotion": ("Remotion", "Media"),
                "stripe": ("Stripe", "Payment"),
                "@stripe/stripe-js": ("Stripe", "Payment"),
                "tailwindcss": ("Tailwind CSS", None),
                "@prisma/client": ("Prisma", None),
                "drizzle-orm": ("Drizzle", None),
            }

            for dep, (fw, platform) in framework_map.items():
                if dep in all_deps:
                    frameworks.add(fw)
                    if platform:
                        platforms.add(platform)

            # Check for workspace (monorepo)
            if "workspaces" in pkg:
                platforms.add("Monorepo")

        except (json.JSONDecodeError, OSError):
            pass

    # --- iOS/macOS signals ---
    if stack["signals"].get("Podfile") or stack["signals"].get("*.xcodeproj"):
        languages.add("Swift")
        platforms.add("iOS")
        platforms.add("macOS")

    if stack["signals"].get("Package.swift"):
        languages.add("Swift")
        if not platforms & {"iOS", "macOS"}:
            platforms.add("Swift Package")

    # --- Other languages ---
    if stack["signals"].get("Cargo.toml"):
        languages.add("Rust")
        platforms.add("Native")

    if stack["signals"].get("go.mod"):
        languages.add("Go")
        platforms.add("Native")

    if any(stack["signals"].get(f) for f in ("requirements.txt", "pyproject.toml", "setup.py")):
        languages.add("Python")

    if stack["signals"].get("Gemfile"):
        languages.add("Ruby")
        platforms.add("Web")

    if stack["signals"].get("composer.json"):
        languages.add("PHP")
        platforms.add("Web")

    if stack["signals"].get("build.gradle") or stack["signals"].get("build.gradle.kts"):
        languages.add("Kotlin")
        languages.add("Java")
        platforms.add("Android")

    if stack["signals"].get("pubspec.yaml"):
        languages.add("Dart")
        platforms.add("Flutter")
        platforms.add("Mobile")

    # --- Monorepo: scan subdirectories ---
    for subdir_name in ("packages", "apps", "projects"):
        subdir = root / subdir_name
        if subdir.is_dir():
            platforms.add("Monorepo")
            for child in subdir.iterdir():
                if child.is_dir() and (child / "package.json").exists():
                    sub_stack = detect_stack(str(child))
                    languages.update(sub_stack.get("languages", []))
                    frameworks.update(sub_stack.get("frameworks", []))
                    platforms.update(sub_stack.get("platforms", []))
                    deps.update(sub_stack.get("dependencies", []))

    # --- Determine primary ---
    primary = ""
    if "Next.js" in frameworks:
        primary = "Next.js"
    elif "React Native" in frameworks or "Expo" in frameworks:
        primary = "React Native"
    elif "iOS" in platforms:
        primary = "iOS/macOS Native"
    elif "Android" in platforms:
        primary = "Android"
    elif "Flutter" in platforms:
        primary = "Flutter"
    elif "Electron" in frameworks or "Tauri" in frameworks:
        primary = "Desktop"
    elif frameworks & {"React", "Vue.js", "Angular", "Svelte", "SvelteKit", "Nuxt.js", "Astro", "Gatsby"}:
        primary = next(iter(frameworks & {"React", "Vue.js", "Angular", "Svelte", "SvelteKit", "Nuxt.js", "Astro", "Gatsby"}))
    elif frameworks & {"Express", "Fastify", "Hono"}:
        primary = "Node.js Server"
    elif "Rust" in languages:
        primary = "Rust"
    elif "Go" in languages:
        primary = "Go"
    elif "Python" in languages:
        primary = "Python"
    elif "Ruby" in languages:
        primary = "Ruby"
    elif "PHP" in languages:
        primary = "PHP"
    elif languages:
        primary = next(iter(languages))
    else:
        primary = "Unknown"

    stack["primary"] = primary
    stack["languages"] = sorted(languages)
    stack["frameworks"] = sorted(frameworks)
    stack["platforms"] = sorted(platforms)
    stack["dependencies"] = sorted(deps)

    return stack


# ---------------------------------------------------------------------------
# Keywords used to auto-categorize unknown skills from their SKILL.md description
# ---------------------------------------------------------------------------
KEYWORD_DOMAINS = {
    "ios": "ios",
    "macos": "ios",
    "xcode": "ios",
    "swiftui": "ios",
    "swift": "ios",
    "app store": "ios",
    "apple": "ios",
    "aso": "ios",
    "android": "android",
    "kotlin": "android",
    "gradle": "android",
    "flutter": "mobile",
    "dart": "mobile",
    "react native": "mobile",
    "mobile": "mobile",
    "web": "web",
    "seo": "web",
    "landing page": "web",
    "conversion": "web",
    "cro": "web",
    "marketing": "web",
    "email": "web",
    "copywriting": "web",
    "analytics": "web",
    "stripe": "payment",
    "payment": "payment",
    "subscription": "payment",
    "checkout": "payment",
    "churn": "payment",
    "image generat": "media",
    "video generat": "media",
    "audio generat": "media",
    "fal.ai": "media",
    "remotion": "media",
    "media": "media",
}

# ---------------------------------------------------------------------------
# Skill reading — multi-source discovery
# ---------------------------------------------------------------------------

def _parse_skill_md_frontmatter(skill_md_path: Path) -> dict:
    """Extract name and description from SKILL.md YAML frontmatter."""
    result = {"name": "", "description": ""}
    try:
        text = skill_md_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return result

    # Match YAML frontmatter between --- markers
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return result

    for line in match.group(1).splitlines():
        if line.startswith("name:"):
            result["name"] = line.split(":", 1)[1].strip().strip("\"'")
        elif line.startswith("description:"):
            result["description"] = line.split(":", 1)[1].strip().strip("\"'")

    return result


def _infer_domain_from_description(description: str) -> str | None:
    """Guess a skill's domain from its SKILL.md description using keyword matching."""
    desc_lower = description.lower()
    # Count hits per domain
    domain_hits: dict[str, int] = {}
    for keyword, domain in KEYWORD_DOMAINS.items():
        if keyword in desc_lower:
            domain_hits[domain] = domain_hits.get(domain, 0) + 1

    if not domain_hits:
        return None
    # Return domain with most keyword hits
    return max(domain_hits, key=lambda d: domain_hits[d])


def read_installed_skills(project_path: str | None = None) -> dict:
    """Discover all installed skills from multiple sources.

    Sources (in priority order):
    1. ~/.agents/.skill-lock.json  — primary lock file (has metadata)
    2. ~/.agents/skills/           — directory listing (catches skills not in lock)
    3. ~/.claude/skills/           — symlinked global skills (may have unique ones)
    4. <project>/.claude/skills/   — project-local skills (marked as local)
    """
    home = Path.home()
    skills: dict[str, dict] = {}

    # --- Source 1: Lock file ---
    lock_path = home / ".agents" / ".skill-lock.json"
    if lock_path.exists():
        try:
            data = json.loads(lock_path.read_text(encoding="utf-8"))
            for name, info in data.get("skills", {}).items():
                skills[name] = {
                    "source": info.get("source", "unknown"),
                    "sourceType": "lock-file",
                    "description": "",
                    "local": False,
                }
        except (json.JSONDecodeError, OSError):
            pass

    # --- Source 2: ~/.agents/skills/ directory ---
    agents_skills_dir = home / ".agents" / "skills"
    if agents_skills_dir.is_dir():
        for child in agents_skills_dir.iterdir():
            if child.is_dir() and child.name not in skills:
                skill_md = child / "SKILL.md"
                fm = _parse_skill_md_frontmatter(skill_md) if skill_md.exists() else {}
                skills[child.name] = {
                    "source": "agents-dir",
                    "sourceType": "directory",
                    "description": fm.get("description", ""),
                    "local": False,
                }

    # --- Source 3: ~/.claude/skills/ directory ---
    claude_skills_dir = home / ".claude" / "skills"
    if claude_skills_dir.is_dir():
        for child in claude_skills_dir.iterdir():
            if child.is_dir() and child.name not in skills:
                skill_md = child / "SKILL.md"
                fm = _parse_skill_md_frontmatter(skill_md) if skill_md.exists() else {}
                skills[child.name] = {
                    "source": "claude-skills-dir",
                    "sourceType": "directory",
                    "description": fm.get("description", ""),
                    "local": False,
                }

    # --- Source 4: Project-local skills ---
    if project_path:
        project_skills_dir = Path(project_path) / ".claude" / "skills"
        if project_skills_dir.is_dir():
            for child in project_skills_dir.iterdir():
                if child.is_dir() and child.name not in skills:
                    skill_md = child / "SKILL.md"
                    fm = _parse_skill_md_frontmatter(skill_md) if skill_md.exists() else {}
                    skills[child.name] = {
                        "source": "project-local",
                        "sourceType": "project",
                        "description": fm.get("description", ""),
                        "local": True,
                    }

    # --- Backfill descriptions for lock-file skills that had none ---
    for name, info in skills.items():
        if info["description"]:
            continue
        # Try reading SKILL.md from both directories
        for base in (agents_skills_dir, claude_skills_dir):
            skill_md = base / name / "SKILL.md"
            if skill_md.exists():
                fm = _parse_skill_md_frontmatter(skill_md)
                if fm.get("description"):
                    info["description"] = fm["description"]
                    break

    return skills


# ---------------------------------------------------------------------------
# Relevance scoring
# ---------------------------------------------------------------------------

def score_skills(stack: dict, installed_skills: dict, overrides: dict | None = None) -> dict:
    """Score each installed skill based on detected tech stack."""
    if overrides is None:
        overrides = {"forceEnable": [], "forceDisable": []}

    force_enable = set(overrides.get("forceEnable", []))
    force_disable = set(overrides.get("forceDisable", []))

    platforms = set(stack.get("platforms", []))
    frameworks = set(stack.get("frameworks", []))
    deps = set(stack.get("dependencies", []))

    is_ios = bool(platforms & {"iOS", "macOS"})
    is_web = bool(platforms & {"Web"}) or bool(
        frameworks & {"Next.js", "React", "Vue.js", "Angular", "Svelte", "SvelteKit",
                       "Nuxt.js", "Astro", "Gatsby", "Express", "Fastify", "Hono"}
    )
    is_mobile = bool(platforms & {"Mobile", "iOS", "Android", "Flutter"}) or bool(
        frameworks & {"React Native", "Expo"}
    )
    is_android = bool(platforms & {"Android"})
    is_flutter = bool(platforms & {"Flutter"})
    has_stripe = "Stripe" in frameworks or "stripe" in deps or "@stripe/stripe-js" in deps
    has_media = "Remotion" in frameworks or bool(
        deps & {"remotion", "@remotion/cli", "fal-ai", "@fal-ai/client"}
    )
    is_empty = stack.get("primary", "") == "Unknown"

    results = {}

    for skill_name in installed_skills:
        # Universal skills
        if skill_name in UNIVERSAL_SKILLS:
            results[skill_name] = {
                "tier": "universal",
                "score": 100,
                "reason": "Universal skill — always active",
            }
            continue

        # Project-local skills — never disabled
        if installed_skills.get(skill_name, {}).get("local"):
            results[skill_name] = {
                "tier": "universal",
                "score": 100,
                "reason": "Project-local skill — always active",
            }
            continue

        score = 0
        reason = ""

        # --- iOS/macOS domain ---
        if skill_name in IOS_MACOS_SKILLS:
            if is_ios:
                score = 95
                reason = "iOS/macOS stack detected"
            elif is_flutter and skill_name in ("app-store-optimization", "aso-full-audit",
                                                 "aso-optimize", "aso-competitor", "aso-prelaunch", "aso"):
                score = 70
                reason = "Flutter deploys to App Store"
            elif is_mobile and skill_name in ("app-store-optimization", "aso-full-audit",
                                                "aso-optimize", "aso-competitor", "aso-prelaunch", "aso"):
                score = 60
                reason = "Mobile app may target App Store"
            else:
                score = 10
                reason = "No iOS/macOS stack detected"

        # --- Web/SaaS domain ---
        elif skill_name in WEB_SAAS_SKILLS:
            if is_web:
                score = 90
                reason = "Web stack detected"
            elif skill_name in MARKETING_CROSS_PLATFORM:
                score = 50
                reason = "Cross-platform marketing utility"
            else:
                score = 20
                reason = "No web stack detected"

        # --- Payment domain ---
        elif skill_name in PAYMENT_SKILLS:
            if has_stripe:
                score = 95
                reason = "Stripe dependency detected"
            elif is_web or is_mobile:
                score = 55
                reason = "Web/mobile projects often use payments"
            else:
                score = 25
                reason = "No payment signals detected"

        # --- Media domain ---
        elif skill_name in MEDIA_SKILLS:
            if has_media:
                score = 90
                reason = "Media processing dependency detected"
            elif skill_name == "remotion-best-practices" and "remotion" in deps:
                score = 95
                reason = "Remotion dependency found"
            else:
                score = 10
                reason = "No media processing signals"

        # --- Unknown skill: try auto-categorize from SKILL.md description ---
        else:
            desc = installed_skills.get(skill_name, {}).get("description", "")
            inferred = _infer_domain_from_description(desc) if desc else None

            if installed_skills.get(skill_name, {}).get("local"):
                # Project-local skills are always kept active
                score = 100
                reason = "Project-local skill — always active"
            elif inferred == "ios":
                score = 95 if is_ios else 10
                reason = f"Auto-categorized as iOS (from description){' — iOS stack detected' if is_ios else ' — no iOS stack detected'}"
            elif inferred == "android":
                score = 95 if is_android else 10
                reason = f"Auto-categorized as Android (from description){' — Android stack detected' if is_android else ' — no Android stack detected'}"
            elif inferred == "mobile":
                score = 80 if is_mobile else 30
                reason = f"Auto-categorized as mobile (from description){' — mobile stack detected' if is_mobile else ' — no mobile stack detected'}"
            elif inferred == "web":
                score = 90 if is_web else 50
                reason = f"Auto-categorized as web (from description){' — web stack detected' if is_web else ' — cross-platform utility'}"
            elif inferred == "payment":
                score = 95 if has_stripe else (55 if (is_web or is_mobile) else 25)
                reason = f"Auto-categorized as payment (from description)"
            elif inferred == "media":
                score = 90 if has_media else 10
                reason = f"Auto-categorized as media (from description){' — media stack detected' if has_media else ' — no media signals'}"
            else:
                score = 50
                reason = "Unknown domain — keeping active"

        # --- Empty project: keep everything ---
        if is_empty:
            score = max(score, 50)
            reason = "No stack detected — keeping active"

        # --- Apply overrides ---
        if skill_name in force_enable:
            score = 95
            reason = f"Force-enabled via override (original: {reason})"
        elif skill_name in force_disable:
            score = 5
            reason = f"Force-disabled via override (original: {reason})"

        # --- Assign tier ---
        if score >= 80:
            tier = "essential"
        elif score >= 40:
            tier = "useful"
        else:
            tier = "irrelevant"

        results[skill_name] = {
            "tier": tier,
            "score": score,
            "reason": reason,
        }

    return results


# ---------------------------------------------------------------------------
# Full analysis
# ---------------------------------------------------------------------------

def analyze(project_path: str) -> dict:
    """Run the full analysis: detect stack, read skills, score, produce output."""
    stack = detect_stack(project_path)
    installed = read_installed_skills(project_path)

    # Read existing overrides
    overrides = {"forceEnable": [], "forceDisable": []}
    config_path = Path(project_path) / ".claude" / "skill-manager.json"
    if config_path.exists():
        try:
            existing = json.loads(config_path.read_text(encoding="utf-8"))
            overrides = existing.get("overrides", overrides)
        except (json.JSONDecodeError, OSError):
            pass

    scored = score_skills(stack, installed, overrides)

    disabled = sorted(
        name for name, info in scored.items() if info["tier"] == "irrelevant"
    )
    enabled = sorted(
        name for name, info in scored.items() if info["tier"] in ("essential", "useful")
    )
    universal = sorted(
        name for name, info in scored.items() if info["tier"] == "universal"
    )

    stats = {
        "total": len(scored),
        "essential": sum(1 for v in scored.values() if v["tier"] == "essential"),
        "useful": sum(1 for v in scored.values() if v["tier"] == "useful"),
        "irrelevant": sum(1 for v in scored.values() if v["tier"] == "irrelevant"),
        "universal": sum(1 for v in scored.values() if v["tier"] == "universal"),
    }

    # Remove dependencies list from stack output (too verbose)
    stack_output = {k: v for k, v in stack.items() if k != "dependencies"}

    return {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "detectedStack": stack_output,
        "skills": scored,
        "disabled": disabled,
        "enabled": enabled,
        "universal": universal,
        "overrides": overrides,
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Skill Manager — Detect project stack and score skill relevance"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--detect-stack",
        metavar="PATH",
        help="Detect tech stack and output JSON",
    )
    group.add_argument(
        "--analyze",
        metavar="PATH",
        help="Full analysis: detect stack + score all skills",
    )

    args = parser.parse_args()

    if args.detect_stack:
        path = os.path.abspath(args.detect_stack)
        if not os.path.isdir(path):
            print(json.dumps({"error": f"Not a directory: {path}"}), file=sys.stderr)
            sys.exit(1)
        result = detect_stack(path)
        print(json.dumps(result, indent=2))

    elif args.analyze:
        path = os.path.abspath(args.analyze)
        if not os.path.isdir(path):
            print(json.dumps({"error": f"Not a directory: {path}"}), file=sys.stderr)
            sys.exit(1)
        result = analyze(path)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
