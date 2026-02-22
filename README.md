# skill-manager

**Save ~4,000 tokens per conversation** by automatically disabling irrelevant Claude Code skills per project.

50+ installed skills? Most are noise for your current project. `skill-manager` detects your tech stack, scores every skill's relevance, and tells Claude to ignore the ones that don't belong — all through your project's `CLAUDE.md`.

## Install

```bash
npx skills add egebese/skill-manager -g -y
```

## Usage

```
/skill-manager
```

Or just say: *"manage skills"*, *"optimize skills"*, *"disable irrelevant skills"*, *"which skills do I need?"*

## Before & After

### Next.js + Stripe project

```
Stack: Next.js / TypeScript / React / Stripe / Tailwind CSS

53 skills analyzed:
  27 essential  (kept)    — page-cro, stripe-integration, analytics-tracking, ...
  10 universal  (kept)    — brainstorming, writing-plans, find-skills, ...
  16 irrelevant (disabled) — asc-xcode-build, mobile-ios-design, fal-audio, ...

16 skills disabled → ~1,200 tokens saved per conversation
```

### iOS Swift project

```
Stack: iOS/macOS Native / Swift / SwiftUI

53 skills analyzed:
   9 essential  (kept)    — mobile-ios-design, asc-xcode-build, app-store-optimization, ...
  13 useful     (kept)    — copywriting, marketing-ideas, stripe-integration, ...
  10 universal  (kept)    — brainstorming, writing-plans, find-skills, ...
  21 irrelevant (disabled) — seo-audit, schema-markup, programmatic-seo, page-cro, ...

21 skills disabled → ~1,600 tokens saved per conversation
```

### Rust CLI project

```
Stack: Rust

53 skills analyzed:
   0 essential
   0 useful
  10 universal  (kept)    — brainstorming, writing-plans, find-skills, ...
  43 irrelevant (disabled) — all iOS, web, marketing, media skills

43 skills disabled → ~3,200 tokens saved per conversation
```

## How It Works

**1. Detects** your tech stack from project files:
  - `package.json` → Node.js, Next.js, React, Vue, Stripe, Remotion, etc.
  - `*.xcodeproj` / `Podfile` / `Package.swift` → iOS/macOS
  - `Cargo.toml` → Rust | `go.mod` → Go | `pubspec.yaml` → Flutter
  - `build.gradle` → Android | `composer.json` → PHP | `Gemfile` → Ruby
  - Monorepo support: scans `packages/`, `apps/` subdirectories

**2. Discovers** all installed skills from every source:
  - `~/.agents/.skill-lock.json` (primary lock file)
  - `~/.agents/skills/` and `~/.claude/skills/` directories
  - Project-local `.claude/skills/` (always kept active)

**3. Scores** each skill 0–100 based on tech stack match:

| Tier | Score | Action |
|------|-------|--------|
| **essential** | 80–100 | Kept active — directly relevant |
| **useful** | 40–79 | Kept active — cross-platform utility |
| **irrelevant** | 0–39 | Disabled in CLAUDE.md |
| **universal** | always | Never disabled (brainstorming, TDD, find-skills, etc.) |

**4. Auto-categorizes unknown skills** by reading their `SKILL.md` description — your custom skills and newly installed skills are handled automatically, no hardcoded lists needed.

**5. Injects** a bounded section into `CLAUDE.md`:

```markdown
<!-- SKILL-MANAGER:START -->
## Disabled Skills
The following skills are not relevant and should be ignored:
- `asc-xcode-build` — No iOS/macOS stack detected
- `fal-audio` — No media processing signals
- ...
<!-- SKILL-MANAGER:END -->
```

**6. Generates** `.claude/skill-manager.json` with the full analysis for inspection and overrides.

## Overrides

Force-enable or force-disable specific skills by editing `.claude/skill-manager.json`:

```json
{
  "overrides": {
    "forceEnable": ["seo-audit"],
    "forceDisable": ["fal-audio"]
  }
}
```

Then re-run `/skill-manager` to apply.

## Re-enable All

Say *"re-enable all skills"* and the skill removes the CLAUDE.md section and deletes the config file.

## Supported Stacks

| Platform | Detection Signals |
|----------|------------------|
| **Next.js / React / Vue / Angular / Svelte** | package.json dependencies |
| **iOS / macOS** | *.xcodeproj, Podfile, Package.swift |
| **Android** | build.gradle, build.gradle.kts |
| **Flutter** | pubspec.yaml |
| **React Native / Expo** | package.json dependencies |
| **Rust** | Cargo.toml |
| **Go** | go.mod |
| **Python** | requirements.txt, pyproject.toml, setup.py |
| **Ruby** | Gemfile |
| **PHP** | composer.json |
| **Monorepo** | workspaces in package.json, packages/, apps/ dirs |

## Skill Domains

Skills are organized into domains for scoring:

- **iOS/macOS**: mobile-ios-design, asc-xcode-build, asc-metadata-sync, app-store-optimization, aso-*, ...
- **Web/SaaS**: page-cro, seo-audit, analytics-tracking, copywriting, content-strategy, ...
- **Payment**: stripe-integration, paywall-upgrade-cro, churn-prevention
- **Media**: fal-audio, fal-generate, fal-image-edit, remotion-best-practices, ...
- **Universal** (never disabled): find-skills, brainstorming, writing-plans, test-driven-development, skill-creator, ...

Skills not in any known domain are **auto-categorized** from their SKILL.md description using keyword matching — so your custom skills and third-party skills work out of the box.

## Why CLAUDE.md Injection?

Claude Code has no native `disabledSkills` setting. The only per-project mechanism is `CLAUDE.md`, which Claude reads at the start of every conversation. By injecting a clearly-marked section, we get:

- **Per-project** — each project gets its own disabled list
- **Reversible** — remove the section or say "re-enable all"
- **Idempotent** — re-running replaces the section, never duplicates
- **Non-destructive** — only touches content between `<!-- SKILL-MANAGER:START/END -->` markers

## Includes Python Analysis Script

For deterministic, fast analysis, the skill includes a zero-dependency Python 3.9+ script:

```bash
python3 ~/.agents/skills/skill-manager/scripts/analyze_project.py --analyze "$(pwd)"
```

Works without Python too — Claude follows the manual workflow instructions in SKILL.md.

## Requirements

- Claude Code with skills support
- Python 3.9+ (optional — manual fallback available)

## License

MIT
