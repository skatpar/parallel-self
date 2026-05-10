# Parallel Self AI — Personality Clone Simulator

> *"Version_You.exe // Loading Fierce Mode…"*

An AI-powered personality profiling and clone simulation system. Create a digital replica of yourself, modify personality traits, and see how your **upgraded self** would respond to real-life scenarios.

---

## What Problem Does It Solve?

Instead of generic self-help advice, Parallel Self **shows** you how a stronger version of yourself would act — making personal growth visual, interactive, and measurable.

- **Low confidence** → See exactly what confident-you would say
- **Indecisiveness** → Watch your bold clone make decisions
- **Lack of assertiveness** → Compare your response with your fierce version
- **Difficulty imagining growth** → The gap between Real You and Parallel You becomes tangible

---

## How It Works

### 1. Personality Profiling (Stage 01)
- Answer 5 behavioral questions across trait dimensions
- Provide a free-text writing sample (30+ chars)
- Claude AI extracts your personality DNA — archetype classification + trait baseline

### 2. Clone Modification (Stage 02)
Adjust trait sliders to create your parallel self:

| Trait        | Low End     | High End    |
|-------------|-------------|-------------|
| Confidence  | Hesitant    | Confident   |
| Aggression  | Passive     | Assertive   |
| Optimism    | Pessimistic | Optimistic  |
| Risk-Taking | Cautious    | Bold        |
| Discipline  | Flexible    | Disciplined |

Quick presets: Fierce, Stoic, Bold, Focused, Max

Real-time divergence tracking and archetype re-classification.

### 3. Scenario Simulation (Stage 03)
Test both versions across 4 high-stakes scenarios:
- High-stakes interview
- Salary negotiation
- Difficult conversation
- Pitching investors

Each simulation generates:
- **Real You** response
- **Parallel You** response
- **Comparative behavioral analysis**
- **Voice playback** via Web Speech API

---

## Tech Stack

| Component        | Technology                              |
|------------------|-----------------------------------------|
| Frontend         | React 18 + Vite                         |
| Backend          | Express.js (API proxy)                  |
| AI Engine        | Claude API (Anthropic)                  |
| Voice Playback   | Web Speech API (browser-native TTS)     |
| Styling          | Inline CSS with custom dark theme       |
| Fonts            | Fraunces, Geist, JetBrains Mono         |

---

## Quick Start

```bash
# Install dependencies
npm install

# Add your Anthropic API key
cp .env.example .env
# Edit .env and add your key

# Run both frontend and backend
npm start
```

Then open `http://localhost:5173` in your browser.

- **Frontend** runs on port 5173 (Vite dev server)
- **Backend** runs on port 3001 (Express API proxy)

---

## Project Structure

```
parallel-self/
├── index.html          # HTML entry point
├── package.json        # Dependencies and scripts
├── vite.config.js      # Vite config with API proxy
├── server.js           # Express backend (Claude API proxy)
├── .env.example        # Environment variable template
├── .env                # Your API key (gitignored)
├── .gitignore
├── README.md
└── src/
    ├── main.jsx        # React entry point
    └── App.jsx         # Full app (profile/modify/simulate stages)
```

---

## UI Design

- **Dark mode** with minimal, editorial aesthetic
- **Accent color**: `#D4FF3F` (lime/chartreuse)
- Custom fonts: Fraunces (display), Geist (body), JetBrains Mono (data)
- Animated speaking avatars with lip-sync
- Identity Divergence Score and Clone Stability Index
- Smooth stage transitions with fade animations

---

## License

MIT — Built as an AI/ML portfolio project.
