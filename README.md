# 🧠 PARALLEL SELF — AI Personality Clone Simulator

> *"Version_You.exe // Loading Fierce Mode…"*

An AI-powered personality profiling and clone simulation system. Create a digital replica of yourself, modify personality traits, and see how your **upgraded self** would respond to real-life scenarios.

---

## 🎯 What Problem Does It Solve?

Instead of generic self-help advice, Parallel Self **shows** you how a stronger version of yourself would act — making personal growth visual, interactive, and measurable.

- **Low confidence** → See exactly what confident-you would say
- **Indecisiveness** → Watch your bold clone make decisions
- **Lack of assertiveness** → Compare your response with your fierce version
- **Difficulty imagining growth** → The gap between Real You and Parallel You becomes tangible

---

## 🧬 How It Works

### 1. Personality Profiling
- Answer 20 behavioral questions across 5 trait dimensions
- Optional: provide a free-text writing sample
- AI extracts personality DNA using **VADER sentiment analysis** and **lexical trait scoring**

### 2. Clone Generation
Adjust trait sliders to create your parallel self:

| Trait        | Low End     | High End    |
|-------------|-------------|-------------|
| Confidence  | Hesitant    | Confident   |
| Aggression  | Passive     | Assertive   |
| Optimism    | Pessimistic | Optimistic  |
| Risk-Taking | Cautious    | Bold        |
| Discipline  | Flexible    | Disciplined |

Quick presets: 🔥 Fierce, 🧊 Stoic, 🚀 Bold, 🎯 Focused, ⚡ Max

### 3. Scenario Simulation
Test both versions across 8 real-life scenarios:
- 💼 Job Interview
- ⚡ Heated Argument
- 🎤 Public Speaking
- 💬 Relationship Conflict
- 🤝 Salary Negotiation
- 🚫 Handling Rejection
- 👑 Leadership Moment
- 🛡️ Setting Boundaries

Each simulation generates:
- **Real You** response
- **Parallel You** response
- **Comparative analysis**

### 4. Identity Dashboard
- Side-by-side trait comparison bars
- Identity Divergence Score
- Clone Stability Index
- Text sample sentiment analysis
- Exportable profile JSON

---

## 🛠 Tech Stack

| Component           | Technology                        |
|--------------------|-----------------------------------|
| UI Framework       | Streamlit (Cyberpunk custom CSS)  |
| Sentiment Analysis | VADER (vaderSentiment)            |
| ML/Clustering      | scikit-learn                      |
| Text Analysis      | Lexical trait scoring + NLP       |
| Response Engine    | Rule-based trait-weighted system  |

**No heavy deep learning required** — runs on any machine.

---

## 📊 AI Techniques (Viva-Ready)

- **NLP Feature Extraction** — Lexical marker analysis from writing samples
- **Personality Trait Clustering** — Multi-dimensional behavioral profiling
- **Sentiment Polarity Scoring** — VADER compound + dimensional scores
- **Behavioral Simulation Modeling** — Trait-intensity response mapping
- **Parameter-Controlled Response Generation** — Slider-driven personality modification

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## 📁 Project Structure

```
parallel-self/
├── app.py                  # Main Streamlit application (UI + routing)
├── personality_engine.py   # Personality profiling, trait analysis, archetypes
├── clone_engine.py         # Response generation, scenario simulation
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🎨 UI Design

- **Dark mode** with cyberpunk aesthetics
- **Neon cyan / magenta / green** accent system
- Custom fonts: Orbitron (headers), Rajdhani (body), Share Tech Mono (data)
- Terminal-style boot sequences
- Glowing trait bars and metrics
- "Clone Stability Index" and "Identity Divergence Score"

---

## 📝 License

MIT — Built as an AI/ML portfolio project.
