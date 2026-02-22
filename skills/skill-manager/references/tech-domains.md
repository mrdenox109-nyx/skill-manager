# Tech Domains Reference

Reference mapping of platform detection signals, skill-to-domain assignments, and scoring rules.
Used as a fallback when the Python analysis script is unavailable.

## Platform Detection Signals

| Signal File(s) | Primary Platform | Languages |
|----------------|-----------------|-----------|
| `package.json` + `next.config.*` | Next.js (Web) | TypeScript, JavaScript |
| `package.json` + `vue` dep | Vue.js (Web) | TypeScript, JavaScript |
| `package.json` + `@angular/core` dep | Angular (Web) | TypeScript |
| `package.json` + `svelte` dep | Svelte (Web) | TypeScript, JavaScript |
| `package.json` + `react-native` dep | React Native (Mobile) | TypeScript, JavaScript |
| `package.json` + `expo` dep | Expo (Mobile) | TypeScript, JavaScript |
| `package.json` + `electron` dep | Electron (Desktop) | TypeScript, JavaScript |
| `package.json` + `remotion` dep | Media Processing | TypeScript |
| `Podfile` or `*.xcodeproj` | iOS/macOS Native | Swift, Objective-C |
| `Package.swift` | Swift Package | Swift |
| `Cargo.toml` | Rust | Rust |
| `go.mod` | Go | Go |
| `requirements.txt` / `pyproject.toml` | Python | Python |
| `Gemfile` | Ruby | Ruby |
| `composer.json` | PHP | PHP |
| `build.gradle` / `build.gradle.kts` | Android/JVM | Kotlin, Java |
| `pubspec.yaml` | Flutter | Dart |
| `Dockerfile` | Containerized | (varies) |
| `vercel.json` | Vercel Deployment | (varies) |
| `netlify.toml` | Netlify Deployment | (varies) |

## Skill Domain Assignments

### iOS/macOS Domain
Skills that are essential when iOS/macOS stack is detected:

```
mobile-ios-design          — iOS UI patterns, SwiftUI, HIG
asc-xcode-build            — Xcode build, archive, export
asc-metadata-sync          — App Store metadata management
asc-localize-metadata      — App Store localization
asc-subscription-localization — IAP display name localization
asc-ppp-pricing            — Territory-specific pricing
asc-shots-pipeline         — Screenshot automation
asc-notarization           — macOS notarization
app-store-optimization     — ASO toolkit
aso-full-audit             — Full ASO audit
aso-optimize               — Quick ASO metadata optimization
aso-competitor             — Competitive ASO intelligence
aso-prelaunch              — Pre-launch ASO checklist
aso                        — ASO toolkit (alias)
```

### Web/SaaS Domain
Skills that are essential when web framework is detected:

```
page-cro                   — Landing page conversion optimization
signup-flow-cro            — Signup/registration flow CRO
onboarding-cro             — Post-signup activation CRO
popup-cro                  — Popup/modal conversion optimization
form-cro                   — Form conversion optimization
copywriting                — Marketing copy creation
copy-editing               — Marketing copy editing
content-strategy           — Content planning and strategy
seo-audit                  — SEO audit and analysis
programmatic-seo           — Programmatic SEO implementation
schema-markup              — Structured data / schema.org
analytics-tracking         — GA4, GTM, event tracking setup
ab-test-setup              — A/B test design and implementation
email-sequence             — Drip campaigns, lifecycle emails
social-content             — Social media content creation
marketing-ideas            — Marketing strategy ideation
marketing-psychology       — Behavioral science for marketing
free-tool-strategy         — Engineering-as-marketing tools
launch-strategy            — Product launch planning
paid-ads                   — Paid advertising campaigns
referral-program           — Referral/affiliate programs
pricing-strategy           — Pricing model optimization
competitor-alternatives    — Competitor analysis pages
audit-website              — Website audit (SEO, perf, security)
```

### Payment Domain
Skills that are essential when payment processing is detected:

```
stripe-integration         — Stripe checkout, subscriptions, webhooks
paywall-upgrade-cro        — In-app paywall/upsell optimization
churn-prevention           — Churn reduction, dunning, save offers
```

### Media/AI Generation Domain
Skills that are essential when media processing is detected:

```
fal-audio                  — Audio generation via fal.ai
fal-generate               — Image generation via fal.ai
fal-image-edit             — Image editing via fal.ai
fal-platform               — fal.ai platform guide
fal-upscale                — Image upscaling via fal.ai
fal-workflow               — fal.ai workflow orchestration
remotion-best-practices    — Remotion video framework patterns
```

### Universal Domain (Never Disabled)
These skills provide cross-cutting value regardless of tech stack:

```
find-skills                — Discover and install new skills
skill-creator              — Create new skills
writing-skills             — Skill authoring guide
brainstorming              — Pre-implementation creative exploration
writing-plans              — Implementation planning
test-driven-development    — TDD workflow
dispatching-parallel-agents — Parallel task execution
subagent-driven-development — Multi-agent development
using-superpowers          — Skill discovery and usage
agentation                 — Agent coordination
skill-manager              — This skill (self-reference)
```

## Scoring Rules

### Base Scores by Relationship

| Relationship | Score | Tier |
|-------------|-------|------|
| Skill's domain matches detected platform exactly | 95 | essential |
| Skill is in a related domain (e.g., payment for web) | 70 | useful |
| Skill is cross-platform utility (e.g., marketing) | 50 | useful |
| Skill is for a completely different platform | 10 | irrelevant |
| Skill is universal | N/A | universal |

### Score Modifiers

| Condition | Modifier |
|-----------|----------|
| Dependency explicitly found in package.json/Podfile | +10 |
| Multiple stack signals reinforce relevance | +5 |
| Monorepo with matching sub-project | +15 |
| Only tangentially related to detected stack | -20 |

### Tier Thresholds

- **essential**: score >= 80
- **useful**: score >= 40 and score < 80
- **irrelevant**: score < 40
- **universal**: always universal, no score needed

### Disable Rule

Only skills in the **irrelevant** tier (score < 40) are added to the disabled list.
Skills in **useful** tier are kept active — they may still be invoked occasionally.

## Example Scenarios

### Next.js + Stripe Project
- Essential: All web/SaaS domain + payment domain
- Useful: media skills (might generate images)
- Irrelevant: All iOS/macOS domain (asc-*, mobile-ios-design)
- Universal: Always active

### iOS Swift App
- Essential: All iOS/macOS domain
- Useful: marketing-ideas, copywriting (app marketing), payment skills
- Irrelevant: Web-specific CRO (page-cro, signup-flow-cro), SEO (seo-audit, schema-markup, programmatic-seo), web tools (audit-website)
- Universal: Always active

### Rust CLI Tool
- Essential: (none specific — no Rust-specific skills installed)
- Useful: test-driven-development (universal), writing-plans (universal)
- Irrelevant: All iOS, most web marketing, all media, all payment
- Universal: Always active

### Flutter Mobile App
- Essential: mobile-ios-design (cross-mobile), payment skills (likely in-app purchases)
- Useful: marketing skills, ASO skills (if deploying to app stores)
- Irrelevant: Web-specific SEO, schema-markup
- Universal: Always active
