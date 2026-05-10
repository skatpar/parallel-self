import React, { useState, useMemo, useRef, useEffect } from "react";

// ============ DATA ============
const QUESTIONS = [
  {
    id: "q1",
    text: "When facing a difficult decision, your instinct is to:",
    options: [
      { v: "analyze", label: "Analyze every angle before acting" },
      { v: "gut", label: "Trust your gut and move fast" },
      { v: "consult", label: "Discuss it thoroughly with people you trust" },
      { v: "delay", label: "Sleep on it and decide tomorrow" },
    ],
  },
  {
    id: "q2",
    text: "In a heated disagreement, you usually:",
    options: [
      { v: "deescalate", label: "De-escalate and find middle ground" },
      { v: "hold", label: "Hold your position firmly" },
      { v: "withdraw", label: "Withdraw and process privately" },
      { v: "push", label: "Push back and defend your view" },
    ],
  },
  {
    id: "q3",
    text: "When opportunity comes with risk, you tend to:",
    options: [
      { v: "calculate", label: "Calculate odds carefully" },
      { v: "leap", label: "Take the leap immediately" },
      { v: "wait", label: "Wait for a safer version" },
      { v: "follow", label: "Go only if others go too" },
    ],
  },
  {
    id: "q4",
    text: "Your daily routine looks like:",
    options: [
      { v: "tight", label: "Tightly structured, every hour planned" },
      { v: "loose", label: "Loose framework, lots of flexibility" },
      { v: "mood", label: "Driven by mood and energy" },
      { v: "split", label: "Disciplined mornings, free evenings" },
    ],
  },
  {
    id: "q5",
    text: "When something fails, you most often:",
    options: [
      { v: "lesson", label: "Find the lesson and try again" },
      { v: "question", label: "Question whether to keep going" },
      { v: "blame", label: "Blame circumstances or others" },
      { v: "rebound", label: "Get back up immediately" },
    ],
  },
];

const SCENARIOS = [
  {
    id: "interview",
    title: "High-stakes interview",
    prompt: 'The interviewer asks: "Why should we hire you over someone with more experience?"',
  },
  {
    id: "salary",
    title: "Salary negotiation",
    prompt: 'They offer $80k. You wanted $95k. The recruiter says "this is our best offer."',
  },
  {
    id: "conflict",
    title: "Difficult conversation",
    prompt: "A close friend has been crossing your boundaries. They ask why you've been distant.",
  },
  {
    id: "pitch",
    title: "Pitching investors",
    prompt: 'An investor cuts you off: "I don\'t believe this market is real. Convince me."',
  },
];

const PRESETS = {
  Fierce: { confidence: 92, aggression: 78, optimism: 65, riskTaking: 80, discipline: 70 },
  Stoic: { confidence: 75, aggression: 30, optimism: 50, riskTaking: 40, discipline: 95 },
  Bold: { confidence: 88, aggression: 60, optimism: 85, riskTaking: 90, discipline: 60 },
  Focused: { confidence: 80, aggression: 50, optimism: 70, riskTaking: 55, discipline: 92 },
  Max: { confidence: 100, aggression: 90, optimism: 90, riskTaking: 95, discipline: 95 },
};

const TRAIT_KEYS = ["confidence", "aggression", "optimism", "riskTaking", "discipline"];
const TRAIT_LABELS = {
  confidence: "Confidence",
  aggression: "Aggression",
  optimism: "Optimism",
  riskTaking: "Risk-Taking",
  discipline: "Discipline",
};

// ============ THEME ============
const C = {
  bg: "#0A0A0B",
  card: "#101013",
  cardHi: "#16161A",
  border: "#1F1F23",
  borderHi: "#2A2A30",
  text: "#EFEDE7",
  textDim: "#9A9A9F",
  textMute: "#5C5C63",
  accent: "#D4FF3F", // Parallel You
  real: "#9BA1A6", // Real You
  warn: "#F97066",
};

const FONT_DISPLAY = "'Fraunces', 'Times New Roman', serif";
const FONT_SANS = "'Geist', system-ui, -apple-system, sans-serif";
const FONT_MONO = "'JetBrains Mono', 'SF Mono', Consolas, monospace";

// ============ HELPERS ============
function extractJSON(text) {
  const cleaned = text.replace(/```json\s*/gi, "").replace(/```\s*/g, "").trim();
  try {
    return JSON.parse(cleaned);
  } catch {
    const m = cleaned.match(/\{[\s\S]*\}/);
    if (m) return JSON.parse(m[0]);
    throw new Error("No JSON found");
  }
}

function callClaude(prompt) {
  return fetch("/api/claude", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  })
    .then((r) => r.json())
    .then((d) => d.text || "");
}

function divergence(base, clone) {
  if (!base || !clone) return 0;
  const sum = TRAIT_KEYS.reduce((s, k) => s + Math.abs(clone[k] - base[k]), 0);
  return Math.round((sum / (TRAIT_KEYS.length * 100)) * 100);
}
function stability(clone) {
  if (!clone) return 100;
  const mean = TRAIT_KEYS.reduce((s, k) => s + clone[k], 0) / TRAIT_KEYS.length;
  const variance = TRAIT_KEYS.reduce((s, k) => s + (clone[k] - mean) ** 2, 0) / TRAIT_KEYS.length;
  const std = Math.sqrt(variance);
  return Math.max(0, Math.min(100, Math.round(100 - std * 0.8)));
}

// ============ APP ============
export default function ParallelSelfDemo() {
  const [stage, setStage] = useState("profile");
  const [answers, setAnswers] = useState({});
  const [writing, setWriting] = useState("");
  const [profile, setProfile] = useState(null);
  const [clone, setClone] = useState(null);
  const [scenario, setScenario] = useState(null);
  const [responses, setResponses] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [loadingSim, setLoadingSim] = useState(false);

  const allAnswered = QUESTIONS.every((q) => answers[q.id]);
  const writingValid = writing.trim().length >= 30;

  // ---- Generate profile (Stage 1 -> 2) ----
  async function generateProfile() {
    setLoadingProfile(true);
    const prompt = `You are a personality analysis engine. Given these behavioral answers and a writing sample, classify the person into ONE archetype and estimate their trait scores.

ANSWERS:
${QUESTIONS.map((q) => {
  const opt = q.options.find((o) => o.v === answers[q.id]);
  return `- ${q.text} -> ${opt?.label}`;
}).join("\n")}

WRITING SAMPLE:
"${writing}"

Choose archetype from EXACTLY this list: The Stoic, The Strategist, The Maverick, The Diplomat, The Builder, The Explorer, The Guardian, The Connector, The Analyst, The Catalyst, The Dreamer, The Idealist.

Estimate scores (integer 0-100) for: confidence, aggression, optimism, riskTaking, discipline.

Also compute sentiment polarity (compound score -1 to 1, and positive/negative/neutral percentages 0-100 summing to 100) for the writing sample.

Respond ONLY with raw JSON, no markdown fences:
{"archetype":"...","summary":"one sentence describing this person","traits":{"confidence":N,"aggression":N,"optimism":N,"riskTaking":N,"discipline":N},"sentiment":{"compound":X,"positive":N,"negative":N,"neutral":N}}`;

    try {
      const txt = await callClaude(prompt);
      const data = extractJSON(txt);
      setProfile(data);
      setClone({ ...data.traits });
      setStage("modify");
    } catch (e) {
      // Fallback so demo always works
      const fb = {
        archetype: "The Strategist",
        summary: "A measured, analytical thinker who weighs options carefully before committing.",
        traits: { confidence: 62, aggression: 38, optimism: 58, riskTaking: 42, discipline: 71 },
        sentiment: { compound: 0.18, positive: 42, negative: 18, neutral: 40 },
      };
      setProfile(fb);
      setClone({ ...fb.traits });
      setStage("modify");
    } finally {
      setLoadingProfile(false);
    }
  }

  // ---- Run simulation (Stage 3) ----
  async function runSimulation() {
    if (!scenario || !profile || !clone) return;
    setLoadingSim(true);
    setResponses(null);
    const prompt = `You are simulating two versions of the same person responding to a high-stakes scenario.

REAL YOU TRAITS (0-100):
confidence:${profile.traits.confidence}, aggression:${profile.traits.aggression}, optimism:${profile.traits.optimism}, riskTaking:${profile.traits.riskTaking}, discipline:${profile.traits.discipline}
Archetype: ${profile.archetype}

PARALLEL YOU TRAITS (0-100):
confidence:${clone.confidence}, aggression:${clone.aggression}, optimism:${clone.optimism}, riskTaking:${clone.riskTaking}, discipline:${clone.discipline}

SCENARIO: ${scenario.title}
PROMPT: ${scenario.prompt}

Generate two distinct first-person responses (2-3 sentences each) that AUTHENTICALLY embody each trait profile. Real You should reflect more cautious or hesitant traits if that matches their scores. Parallel You should embody the modified, often bolder profile. Then write a 2-3 sentence behavioral analysis comparing them.

Respond ONLY with raw JSON, no markdown:
{"realYou":"...","parallelYou":"...","analysis":"..."}`;

    try {
      const txt = await callClaude(prompt);
      const data = extractJSON(txt);
      setResponses(data);
    } catch (e) {
      setResponses({
        realYou:
          "I'd probably take a moment, weigh my words carefully, and offer a measured response that doesn't overcommit. I want to be honest about my limitations while still showing interest.",
        parallelYou:
          "I'd lean in, hold eye contact, and reframe the question. The real question isn't whether I have the experience — it's whether you have the appetite for someone who'll move faster than the people you've already interviewed.",
        analysis:
          "Real You defers and softens; Parallel You owns the room and inverts the power dynamic. The trait shifts in confidence and aggression visibly transform passive participation into active framing.",
      });
    } finally {
      setLoadingSim(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: FONT_SANS }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400;1,9..144,600&family=Geist:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
        * { box-sizing: border-box; }
        input[type=range] { -webkit-appearance:none; appearance:none; height:2px; background:${C.borderHi}; outline:none; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance:none; appearance:none; width:14px; height:14px; background:${C.accent}; border-radius:50%; cursor:pointer; box-shadow:0 0 0 4px rgba(212,255,63,0.12); }
        input[type=range]::-moz-range-thumb { width:14px; height:14px; background:${C.accent}; border-radius:50%; cursor:pointer; border:none; box-shadow:0 0 0 4px rgba(212,255,63,0.12); }
        .ps-btn:hover { background:${C.accent} !important; color:#0A0A0B !important; }
        .ps-card { transition: border-color 0.2s, background 0.2s; }
        .ps-card:hover { border-color:${C.borderHi}; }
        .ps-opt { transition: all 0.15s; }
        .ps-opt:hover { border-color:${C.borderHi}; background:${C.cardHi}; }
        .ps-stage-dot { transition: all 0.3s; }
        @keyframes pulse { 0%,100% { opacity:0.6; } 50% { opacity:1; } }
        .ps-pulse { animation: pulse 1.4s ease-in-out infinite; }
        .ps-fade { animation: fadeIn 0.4s ease; }
        @keyframes fadeIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform:none; } }
        textarea:focus, input:focus { outline:none; }
      `}</style>

      <Header stage={stage} setStage={setStage} hasProfile={!!profile} hasClone={!!clone} />

      <main style={{ maxWidth: 1180, margin: "0 auto", padding: "32px 32px 80px" }}>
        {stage === "profile" && (
          <ProfileStage
            answers={answers}
            setAnswers={setAnswers}
            writing={writing}
            setWriting={setWriting}
            allAnswered={allAnswered}
            writingValid={writingValid}
            generateProfile={generateProfile}
            loading={loadingProfile}
          />
        )}
        {stage === "modify" && profile && clone && (
          <ModifyStage
            profile={profile}
            clone={clone}
            setClone={setClone}
            goNext={() => setStage("simulate")}
          />
        )}
        {stage === "simulate" && profile && clone && (
          <SimulateStage
            profile={profile}
            clone={clone}
            scenario={scenario}
            setScenario={setScenario}
            responses={responses}
            runSimulation={runSimulation}
            loading={loadingSim}
            goBack={() => setStage("modify")}
          />
        )}
      </main>
    </div>
  );
}

// ============ HEADER ============
function Header({ stage, setStage, hasProfile, hasClone }) {
  const stages = [
    { k: "profile", label: "Profile", n: "01" },
    { k: "modify", label: "Modify", n: "02" },
    { k: "simulate", label: "Simulate", n: "03" },
  ];
  const canGo = (k) => k === "profile" || (k === "modify" && hasProfile) || (k === "simulate" && hasClone);

  return (
    <header
      style={{
        borderBottom: `1px solid ${C.border}`,
        padding: "20px 32px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        position: "sticky",
        top: 0,
        background: "rgba(10,10,11,0.85)",
        backdropFilter: "blur(12px)",
        zIndex: 10,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: 4,
            background: C.accent,
            display: "grid",
            placeItems: "center",
            color: "#0A0A0B",
            fontFamily: FONT_MONO,
            fontWeight: 600,
            fontSize: 13,
          }}
        >
          //
        </div>
        <div>
          <div style={{ fontFamily: FONT_DISPLAY, fontSize: 18, letterSpacing: -0.3 }}>
            Parallel Self <em style={{ color: C.accent }}>AI</em>
          </div>
          <div style={{ fontFamily: FONT_MONO, fontSize: 10, color: C.textMute, letterSpacing: 1.2 }}>
            PERSONALITY CLONE LAB · v0.1
          </div>
        </div>
      </div>

      <nav style={{ display: "flex", gap: 4 }}>
        {stages.map((s, i) => {
          const active = stage === s.k;
          const enabled = canGo(s.k);
          return (
            <React.Fragment key={s.k}>
              <button
                onClick={() => enabled && setStage(s.k)}
                disabled={!enabled}
                style={{
                  background: active ? C.cardHi : "transparent",
                  border: `1px solid ${active ? C.borderHi : "transparent"}`,
                  color: active ? C.text : enabled ? C.textDim : C.textMute,
                  padding: "8px 14px",
                  borderRadius: 6,
                  fontSize: 12,
                  fontFamily: FONT_MONO,
                  letterSpacing: 0.5,
                  cursor: enabled ? "pointer" : "not-allowed",
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                }}
              >
                <span style={{ color: active ? C.accent : C.textMute, fontSize: 10 }}>{s.n}</span>
                {s.label.toUpperCase()}
              </button>
              {i < stages.length - 1 && (
                <span style={{ color: C.textMute, alignSelf: "center", fontFamily: FONT_MONO, fontSize: 11 }}>→</span>
              )}
            </React.Fragment>
          );
        })}
      </nav>
    </header>
  );
}

// ============ STAGE 1: PROFILE ============
function ProfileStage({ answers, setAnswers, writing, setWriting, allAnswered, writingValid, generateProfile, loading }) {
  const progress = (Object.keys(answers).length / QUESTIONS.length) * 100;
  const ready = allAnswered && writingValid;

  return (
    <div className="ps-fade">
      <SectionHead
        eyebrow="STAGE 01 / PROFILE"
        title={
          <>
            Extract your <em style={{ color: C.accent, fontStyle: "italic" }}>personality DNA</em>
          </>
        }
        sub="Answer five behavioral questions and drop in a writing sample. The engine will classify your archetype and estimate your trait baseline."
      />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: 32, marginTop: 32 }}>
        <div>
          {QUESTIONS.map((q, i) => (
            <div key={q.id} style={{ marginBottom: 28 }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 12 }}>
                <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.textMute }}>
                  Q{String(i + 1).padStart(2, "0")}
                </span>
                <h3 style={{ margin: 0, fontSize: 16, fontWeight: 400, color: C.text, fontFamily: FONT_DISPLAY }}>
                  {q.text}
                </h3>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                {q.options.map((o) => {
                  const sel = answers[q.id] === o.v;
                  return (
                    <button
                      key={o.v}
                      onClick={() => setAnswers({ ...answers, [q.id]: o.v })}
                      className="ps-opt"
                      style={{
                        textAlign: "left",
                        padding: "12px 14px",
                        borderRadius: 6,
                        border: `1px solid ${sel ? C.accent : C.border}`,
                        background: sel ? "rgba(212,255,63,0.06)" : C.card,
                        color: sel ? C.text : C.textDim,
                        fontSize: 13,
                        cursor: "pointer",
                        fontFamily: FONT_SANS,
                        lineHeight: 1.4,
                      }}
                    >
                      {o.label}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}

          <div style={{ marginTop: 36 }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 12 }}>
              <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.textMute }}>WS</span>
              <h3 style={{ margin: 0, fontSize: 16, fontWeight: 400, fontFamily: FONT_DISPLAY }}>
                Writing sample <span style={{ color: C.textMute, fontSize: 13 }}>— 30+ chars</span>
              </h3>
            </div>
            <textarea
              value={writing}
              onChange={(e) => setWriting(e.target.value)}
              placeholder="Write a short paragraph about a recent decision, frustration, or goal. The more authentic, the better the clone."
              style={{
                width: "100%",
                minHeight: 120,
                background: C.card,
                color: C.text,
                border: `1px solid ${writingValid ? C.borderHi : C.border}`,
                borderRadius: 6,
                padding: 14,
                fontFamily: FONT_SANS,
                fontSize: 13,
                resize: "vertical",
                lineHeight: 1.5,
              }}
            />
            <div style={{ marginTop: 6, fontFamily: FONT_MONO, fontSize: 10, color: C.textMute }}>
              {writing.length} chars · {writing.trim().split(/\s+/).filter(Boolean).length} words
            </div>
          </div>
        </div>

        {/* Right rail: progress card */}
        <aside>
          <div
            className="ps-card"
            style={{
              background: C.card,
              border: `1px solid ${C.border}`,
              borderRadius: 8,
              padding: 20,
              position: "sticky",
              top: 100,
            }}
          >
            <div style={{ fontFamily: FONT_MONO, fontSize: 10, letterSpacing: 1.2, color: C.textMute, marginBottom: 14 }}>
              EXTRACTION STATUS
            </div>

            <Stat label="Behavioral signals" value={`${Object.keys(answers).length} / ${QUESTIONS.length}`} />
            <Stat label="Writing sample" value={writingValid ? "READY" : "PENDING"} accent={writingValid} />
            <Stat label="Engine" value="LLM + LEXICON" mono />

            <div style={{ height: 1, background: C.border, margin: "20px 0" }} />

            <div style={{ marginBottom: 12 }}>
              <div style={{ height: 4, background: C.border, borderRadius: 999, overflow: "hidden" }}>
                <div
                  style={{
                    height: "100%",
                    width: `${progress}%`,
                    background: C.accent,
                    transition: "width 0.4s",
                  }}
                />
              </div>
              <div style={{ marginTop: 6, fontFamily: FONT_MONO, fontSize: 10, color: C.textMute }}>
                {Math.round(progress)}% PROFILED
              </div>
            </div>

            <button
              onClick={generateProfile}
              disabled={!ready || loading}
              className="ps-btn"
              style={{
                width: "100%",
                padding: "12px 16px",
                background: ready ? C.text : C.cardHi,
                color: ready ? C.bg : C.textMute,
                border: "none",
                borderRadius: 6,
                fontFamily: FONT_MONO,
                fontSize: 12,
                letterSpacing: 1,
                cursor: ready ? "pointer" : "not-allowed",
                fontWeight: 500,
                marginTop: 4,
              }}
            >
              {loading ? "ANALYZING…" : "EXTRACT PROFILE →"}
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}

// ============ STAGE 2: MODIFY ============
function ModifyStage({ profile, clone, setClone, goNext }) {
  const div = useMemo(() => divergence(profile.traits, clone), [profile, clone]);
  const stab = useMemo(() => stability(clone), [clone]);

  const setTrait = (k, v) => setClone({ ...clone, [k]: v });
  const applyPreset = (name) => setClone(PRESETS[name]);
  const reset = () => setClone({ ...profile.traits });

  // Re-classify cheaply on the fly based on dominant trait shifts
  const cloneArchetype = useMemo(() => {
    const dom = TRAIT_KEYS.reduce((a, b) => (clone[a] >= clone[b] ? a : b));
    const map = {
      confidence: "The Maverick",
      aggression: "The Catalyst",
      optimism: "The Idealist",
      riskTaking: "The Explorer",
      discipline: "The Stoic",
    };
    return clone[dom] >= 75 ? map[dom] : profile.archetype;
  }, [clone, profile.archetype]);

  return (
    <div className="ps-fade">
      <SectionHead
        eyebrow="STAGE 02 / MODIFY"
        title={
          <>
            Tune your <em style={{ color: C.accent, fontStyle: "italic" }}>parallel self</em>
          </>
        }
        sub="Adjust trait sliders or apply a preset. The engine tracks divergence from your baseline and re-classifies the archetype in real time."
      />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginTop: 32 }}>
        {/* Real You card */}
        <IdentityCard
          label="REAL YOU"
          archetype={profile.archetype}
          traits={profile.traits}
          color={C.real}
          accent={false}
          subtitle={profile.summary}
        />
        {/* Parallel You card */}
        <IdentityCard
          label="PARALLEL YOU"
          archetype={cloneArchetype}
          traits={clone}
          color={C.accent}
          accent
          subtitle={`Divergence ${div}% · Stability ${stab}%`}
        />
      </div>

      {/* Sliders */}
      <div
        className="ps-card"
        style={{
          background: C.card,
          border: `1px solid ${C.border}`,
          borderRadius: 8,
          padding: 28,
          marginTop: 24,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 20 }}>
          <div style={{ fontFamily: FONT_MONO, fontSize: 11, letterSpacing: 1.2, color: C.textMute }}>
            TRAIT MODIFICATION LAB
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            {Object.keys(PRESETS).map((p) => (
              <button
                key={p}
                onClick={() => applyPreset(p)}
                style={{
                  background: "transparent",
                  border: `1px solid ${C.border}`,
                  color: C.textDim,
                  padding: "5px 10px",
                  fontSize: 11,
                  fontFamily: FONT_MONO,
                  letterSpacing: 0.5,
                  borderRadius: 4,
                  cursor: "pointer",
                }}
                onMouseEnter={(e) => {
                  e.target.style.borderColor = C.accent;
                  e.target.style.color = C.accent;
                }}
                onMouseLeave={(e) => {
                  e.target.style.borderColor = C.border;
                  e.target.style.color = C.textDim;
                }}
              >
                {p.toUpperCase()}
              </button>
            ))}
            <button
              onClick={reset}
              style={{
                background: "transparent",
                border: `1px solid ${C.border}`,
                color: C.textMute,
                padding: "5px 10px",
                fontSize: 11,
                fontFamily: FONT_MONO,
                borderRadius: 4,
                cursor: "pointer",
              }}
            >
              RESET
            </button>
          </div>
        </div>

        {TRAIT_KEYS.map((k) => (
          <TraitSlider
            key={k}
            label={TRAIT_LABELS[k]}
            base={profile.traits[k]}
            value={clone[k]}
            onChange={(v) => setTrait(k, v)}
          />
        ))}
      </div>

      {/* Footer: divergence summary + advance */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: 24,
          padding: "20px 24px",
          background: C.card,
          border: `1px solid ${C.border}`,
          borderRadius: 8,
        }}
      >
        <div style={{ display: "flex", gap: 32 }}>
          <BigStat label="DIVERGENCE" value={`${div}%`} accent={div > 30} />
          <BigStat label="STABILITY" value={`${stab}%`} accent={false} />
          <BigStat label="ARCHETYPE" value={cloneArchetype.replace("The ", "").toUpperCase()} small />
        </div>
        <button
          onClick={goNext}
          className="ps-btn"
          style={{
            background: C.text,
            color: C.bg,
            padding: "12px 22px",
            border: "none",
            borderRadius: 6,
            fontFamily: FONT_MONO,
            fontSize: 12,
            letterSpacing: 1,
            cursor: "pointer",
            fontWeight: 500,
          }}
        >
          RUN SIMULATION →
        </button>
      </div>
    </div>
  );
}

function TraitSlider({ label, base, value, onChange }) {
  const delta = value - base;
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <span style={{ fontSize: 13, color: C.text, fontFamily: FONT_SANS }}>{label}</span>
        <span style={{ fontFamily: FONT_MONO, fontSize: 12, color: C.textDim }}>
          <span style={{ color: C.textMute }}>base {base}</span>
          <span style={{ margin: "0 8px", color: C.textMute }}>→</span>
          <span style={{ color: C.accent }}>{value}</span>
          {delta !== 0 && (
            <span style={{ marginLeft: 8, color: delta > 0 ? C.accent : C.warn, fontSize: 11 }}>
              {delta > 0 ? "+" : ""}
              {delta}
            </span>
          )}
        </span>
      </div>
      <div style={{ position: "relative", padding: "6px 0" }}>
        <input
          type="range"
          min={0}
          max={100}
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value))}
          style={{ width: "100%" }}
        />
        {/* baseline marker */}
        <div
          style={{
            position: "absolute",
            top: 4,
            bottom: 4,
            left: `calc(${base}% - 1px)`,
            width: 2,
            background: C.textMute,
            opacity: 0.5,
            pointerEvents: "none",
          }}
        />
      </div>
    </div>
  );
}

function IdentityCard({ label, archetype, traits, color, accent, subtitle }) {
  return (
    <div
      className="ps-card"
      style={{
        background: accent ? "linear-gradient(180deg, rgba(212,255,63,0.04), transparent)" : C.card,
        border: `1px solid ${accent ? "rgba(212,255,63,0.3)" : C.border}`,
        borderRadius: 8,
        padding: 24,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 10,
          letterSpacing: 1.4,
          color: color,
          marginBottom: 8,
        }}
      >
        ◉ {label}
      </div>
      <div
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 28,
          letterSpacing: -0.5,
          marginBottom: 4,
          color: C.text,
        }}
      >
        {archetype}
      </div>
      <div style={{ fontSize: 12, color: C.textMute, marginBottom: 18, fontStyle: "italic", fontFamily: FONT_DISPLAY }}>
        {subtitle}
      </div>

      <div style={{ display: "grid", gap: 6 }}>
        {TRAIT_KEYS.map((k) => (
          <div key={k} style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 11, color: C.textDim, width: 90, fontFamily: FONT_SANS }}>{TRAIT_LABELS[k]}</span>
            <div style={{ flex: 1, height: 4, background: C.border, borderRadius: 999, overflow: "hidden" }}>
              <div
                style={{
                  height: "100%",
                  width: `${traits[k]}%`,
                  background: color,
                  transition: "width 0.4s",
                }}
              />
            </div>
            <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.text, width: 28, textAlign: "right" }}>
              {traits[k]}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============ STAGE 3: SIMULATE ============
function SimulateStage({ profile, clone, scenario, setScenario, responses, runSimulation, loading, goBack }) {
  // ---- TTS / Avatar plumbing ----
  const [playingId, setPlayingId] = useState(null); // null | 'real' | 'parallel'
  const [ttsAvailable, setTtsAvailable] = useState(false);
  const sessionRef = useRef(0);
  const voicesRef = useRef([]);

  useEffect(() => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;
    setTtsAvailable(true);
    const loadVoices = () => {
      voicesRef.current = window.speechSynthesis.getVoices();
    };
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
    return () => {
      window.speechSynthesis.cancel();
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, []);

  function pickFemaleVoice() {
    const voices = voicesRef.current;
    if (!voices.length) return null;
    const en = voices.filter((v) => v.lang && v.lang.toLowerCase().startsWith("en"));
    const pool = en.length ? en : voices;
    // Common female voice names across macOS / iOS / Windows / Google, soft ones first
    const femalePatterns = [
      "samantha", "karen", "allison", "ava", "susan", "victoria", "kate", "serena", "zoe",
      "aria", "jenny", "eva", "michelle", "amelie", "fiona", "moira", "tessa", "veena", "nicky",
      "zira", "hazel", "heera",
      "female", "woman",
    ];
    for (const pat of femalePatterns) {
      const m = pool.find((v) => v.name && v.name.toLowerCase().includes(pat));
      if (m) return m;
    }
    // Last resort — Google US English defaults to female on Chrome
    const google = pool.find((v) => v.name && v.name.toLowerCase().includes("google") && v.lang.toLowerCase().includes("us"));
    return google || pool[0];
  }

  function speakOne({ text, id, token, onDone }) {
    if (!text || !window.speechSynthesis) {
      onDone && onDone();
      return;
    }
    const u = new SpeechSynthesisUtterance(text);
    const v = pickFemaleVoice();
    if (v) u.voice = v;
    // Default rate/pitch/volume — no modulation
    u.onstart = () => {
      if (sessionRef.current === token) setPlayingId(id);
    };
    u.onend = () => {
      if (sessionRef.current !== token) return;
      setPlayingId(null);
      onDone && onDone();
    };
    u.onerror = () => {
      if (sessionRef.current !== token) return;
      setPlayingId(null);
      onDone && onDone();
    };
    window.speechSynthesis.speak(u);
  }

  function playReal() {
    if (!responses?.realYou) return;
    const token = ++sessionRef.current;
    window.speechSynthesis.cancel();
    speakOne({ text: responses.realYou, id: "real", token });
  }

  function playParallel() {
    if (!responses?.parallelYou) return;
    const token = ++sessionRef.current;
    window.speechSynthesis.cancel();
    speakOne({ text: responses.parallelYou, id: "parallel", token });
  }

  function playBoth() {
    if (!responses?.realYou || !responses?.parallelYou) return;
    const token = ++sessionRef.current;
    window.speechSynthesis.cancel();
    speakOne({
      text: responses.realYou,
      id: "real",
      token,
      onDone: () => {
        if (sessionRef.current !== token) return;
        setTimeout(() => {
          if (sessionRef.current !== token) return;
          speakOne({ text: responses.parallelYou, id: "parallel", token });
        }, 350);
      },
    });
  }

  function stop() {
    ++sessionRef.current; // invalidate
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    setPlayingId(null);
  }

  return (
    <div className="ps-fade">
      <SectionHead
        eyebrow="STAGE 03 / SIMULATE"
        title={
          <>
            Watch them <em style={{ color: C.accent, fontStyle: "italic" }}>respond differently</em>
          </>
        }
        sub="Pick a high-stakes scenario. The engine generates how Real You and Parallel You would each respond, then analyzes the gap. Tap the avatars to hear each version speak."
      />

      <div style={{ marginTop: 32 }}>
        <div style={{ fontFamily: FONT_MONO, fontSize: 11, letterSpacing: 1.2, color: C.textMute, marginBottom: 12 }}>
          SCENARIO
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 10 }}>
          {SCENARIOS.map((s) => {
            const sel = scenario?.id === s.id;
            return (
              <button
                key={s.id}
                onClick={() => setScenario(s)}
                className="ps-opt"
                style={{
                  textAlign: "left",
                  padding: "14px 16px",
                  background: sel ? "rgba(212,255,63,0.06)" : C.card,
                  border: `1px solid ${sel ? C.accent : C.border}`,
                  borderRadius: 6,
                  cursor: "pointer",
                  color: C.text,
                  fontFamily: FONT_SANS,
                }}
              >
                <div style={{ fontFamily: FONT_DISPLAY, fontSize: 15, marginBottom: 4 }}>{s.title}</div>
                <div style={{ fontSize: 12, color: C.textDim, lineHeight: 1.4 }}>{s.prompt}</div>
              </button>
            );
          })}
        </div>

        <div style={{ display: "flex", gap: 10, marginTop: 20 }}>
          <button
            onClick={goBack}
            style={{
              background: "transparent",
              border: `1px solid ${C.border}`,
              color: C.textDim,
              padding: "10px 18px",
              borderRadius: 6,
              fontFamily: FONT_MONO,
              fontSize: 11,
              letterSpacing: 1,
              cursor: "pointer",
            }}
          >
            ← MODIFY
          </button>
          <button
            onClick={() => {
              stop();
              runSimulation();
            }}
            disabled={!scenario || loading}
            className="ps-btn"
            style={{
              flex: 1,
              background: scenario ? C.accent : C.cardHi,
              color: scenario ? C.bg : C.textMute,
              border: "none",
              padding: "10px 18px",
              borderRadius: 6,
              fontFamily: FONT_MONO,
              fontSize: 12,
              letterSpacing: 1,
              cursor: scenario ? "pointer" : "not-allowed",
              fontWeight: 600,
            }}
          >
            {loading ? "SIMULATING BOTH…" : "▶ RUN SIMULATION"}
          </button>
        </div>
      </div>

      {/* Responses */}
      {(loading || responses) && (
        <div style={{ marginTop: 32 }}>
          {/* Voice control bar */}
          {responses && ttsAvailable && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 12,
                marginBottom: 14,
                padding: "10px 14px",
                background: C.card,
                border: `1px solid ${C.border}`,
                borderRadius: 6,
              }}
            >
              <span style={{ fontFamily: FONT_MONO, fontSize: 10, letterSpacing: 1.4, color: C.textMute }}>
                ◇ VOICE PLAYBACK  ·  WEB SPEECH API
              </span>
              <div style={{ display: "flex", gap: 8 }}>
                <button
                  onClick={playingId ? stop : playBoth}
                  style={{
                    background: playingId ? C.cardHi : C.accent,
                    color: playingId ? C.text : C.bg,
                    border: "none",
                    padding: "6px 14px",
                    borderRadius: 4,
                    fontFamily: FONT_MONO,
                    fontSize: 10,
                    letterSpacing: 1.2,
                    cursor: "pointer",
                    fontWeight: 600,
                  }}
                >
                  {playingId ? "■ STOP" : "▶ PLAY BOTH"}
                </button>
              </div>
            </div>
          )}

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <ResponseCard
              label="REAL YOU"
              color={C.real}
              archetype={profile.archetype}
              text={responses?.realYou}
              loading={loading}
              playing={playingId === "real"}
              ttsAvailable={ttsAvailable}
              onPlay={playReal}
              onStop={stop}
            />
            <ResponseCard
              label="PARALLEL YOU"
              color={C.accent}
              accent
              archetype={
                TRAIT_KEYS.reduce((a, b) => (clone[a] >= clone[b] ? a : b)) +
                " dominant"
              }
              text={responses?.parallelYou}
              loading={loading}
              playing={playingId === "parallel"}
              ttsAvailable={ttsAvailable}
              onPlay={playParallel}
              onStop={stop}
            />
          </div>

          {/* Analysis */}
          <div
            style={{
              marginTop: 16,
              padding: 22,
              background: C.card,
              border: `1px solid ${C.border}`,
              borderRadius: 8,
            }}
          >
            <div
              style={{
                fontFamily: FONT_MONO,
                fontSize: 10,
                letterSpacing: 1.4,
                color: C.textMute,
                marginBottom: 10,
              }}
            >
              ◇ COMPARATIVE BEHAVIORAL ANALYSIS
            </div>
            {loading ? (
              <div className="ps-pulse" style={{ color: C.textMute, fontSize: 14, fontFamily: FONT_DISPLAY, fontStyle: "italic" }}>
                Generating analysis…
              </div>
            ) : (
              <div style={{ fontSize: 15, lineHeight: 1.6, fontFamily: FONT_DISPLAY, color: C.text }}>
                {responses?.analysis}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function ResponseCard({ label, color, accent, archetype, text, loading, playing, ttsAvailable, onPlay, onStop }) {
  return (
    <div
      style={{
        background: accent ? "linear-gradient(180deg, rgba(212,255,63,0.05), transparent)" : C.card,
        border: `1px solid ${accent ? "rgba(212,255,63,0.3)" : C.border}`,
        borderRadius: 8,
        padding: 22,
        minHeight: 240,
        position: "relative",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 14 }}>
        <span style={{ fontFamily: FONT_MONO, fontSize: 10, letterSpacing: 1.4, color }}>◉ {label}</span>
        <span style={{ fontFamily: FONT_MONO, fontSize: 10, color: C.textMute }}>{archetype}</span>
      </div>

      {/* Avatar row */}
      {!loading && text && (
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 14 }}>
          <SpeakingAvatar color={color} isPlaying={playing} accent={accent} />
          {ttsAvailable && (
            <button
              onClick={playing ? onStop : onPlay}
              style={{
                background: playing ? "rgba(212,255,63,0.12)" : "transparent",
                color: playing ? C.accent : color,
                border: `1px solid ${playing ? C.accent : C.border}`,
                padding: "6px 12px",
                borderRadius: 4,
                fontFamily: FONT_MONO,
                fontSize: 10,
                letterSpacing: 1.2,
                cursor: "pointer",
                fontWeight: 600,
              }}
            >
              {playing ? "■ STOP" : "▶ SPEAK"}
            </button>
          )}
          {playing && (
            <span style={{ fontFamily: FONT_MONO, fontSize: 9, letterSpacing: 1.2, color: C.accent }}>
              SPEAKING…
            </span>
          )}
        </div>
      )}

      {loading ? (
        <div className="ps-pulse" style={{ color: C.textMute, fontSize: 15, fontFamily: FONT_DISPLAY, fontStyle: "italic" }}>
          Composing response…
        </div>
      ) : (
        <div style={{ fontSize: 15, lineHeight: 1.55, fontFamily: FONT_DISPLAY, color: C.text }}>
          "{text}"
        </div>
      )}
    </div>
  );
}

function SpeakingAvatar({ color, isPlaying, accent }) {
  const [mouth, setMouth] = useState(2);
  const [pulse, setPulse] = useState({ r: 36, o: 0 });

  useEffect(() => {
    if (!isPlaying) {
      setMouth(2);
      setPulse({ r: 36, o: 0 });
      return;
    }
    // Mouth animation — randomized, gives natural lip-sync feel
    const mouthInt = setInterval(() => {
      setMouth(2 + Math.random() * 12);
    }, 95);
    // Pulse ring animation via rAF
    let raf;
    let r = 36, o = 0.5;
    const tick = () => {
      r += 0.45;
      o -= 0.014;
      if (r > 54 || o <= 0) { r = 36; o = 0.5; }
      setPulse({ r, o });
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => {
      clearInterval(mouthInt);
      cancelAnimationFrame(raf);
    };
  }, [isPlaying]);

  return (
    <svg viewBox="0 0 80 80" width="60" height="60" style={{ flexShrink: 0 }}>
      {/* Pulse ring (only when speaking) */}
      <circle cx="40" cy="40" r={pulse.r} fill="none" stroke={color} strokeWidth="1" opacity={pulse.o} />
      {/* Head */}
      <circle cx="40" cy="40" r="32" fill="none" stroke={color} strokeWidth="1.5" opacity={isPlaying ? 1 : 0.65} />
      {/* Inner glow when accent + speaking */}
      {accent && isPlaying && (
        <circle cx="40" cy="40" r="32" fill={color} opacity="0.06" />
      )}
      {/* Eyes */}
      <circle cx="30" cy="35" r="2.2" fill={color} />
      <circle cx="50" cy="35" r="2.2" fill={color} />
      {/* Mouth — animated rectangle */}
      <rect
        x={40 - 11}
        y={50 - mouth / 2}
        width="22"
        height={Math.max(2, mouth)}
        rx="1.5"
        fill={color}
      />
    </svg>
  );
}

// ============ SHARED ============
function SectionHead({ eyebrow, title, sub }) {
  return (
    <div>
      <div style={{ fontFamily: FONT_MONO, fontSize: 11, letterSpacing: 1.5, color: C.accent, marginBottom: 14 }}>
        {eyebrow}
      </div>
      <h1
        style={{
          margin: 0,
          fontFamily: FONT_DISPLAY,
          fontWeight: 400,
          fontSize: 44,
          letterSpacing: -1,
          lineHeight: 1.1,
          color: C.text,
        }}
      >
        {title}
      </h1>
      <p style={{ marginTop: 12, color: C.textDim, fontSize: 14, lineHeight: 1.6, maxWidth: 640 }}>{sub}</p>
    </div>
  );
}

function Stat({ label, value, accent, mono }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", padding: "8px 0" }}>
      <span style={{ fontSize: 11, color: C.textMute, fontFamily: FONT_SANS }}>{label}</span>
      <span style={{ fontFamily: FONT_MONO, fontSize: 12, color: accent ? C.accent : C.text }}>{value}</span>
    </div>
  );
}

function BigStat({ label, value, accent, small }) {
  return (
    <div>
      <div style={{ fontFamily: FONT_MONO, fontSize: 9, letterSpacing: 1.4, color: C.textMute, marginBottom: 4 }}>
        {label}
      </div>
      <div
        style={{
          fontFamily: small ? FONT_MONO : FONT_DISPLAY,
          fontSize: small ? 14 : 26,
          letterSpacing: small ? 0.5 : -0.5,
          color: accent ? C.accent : C.text,
        }}
      >
        {value}
      </div>
    </div>
  );
}
