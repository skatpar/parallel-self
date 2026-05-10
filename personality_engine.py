"""
Parallel Self — Personality Profiling Engine
=============================================
Extracts personality traits from questionnaire responses and text samples.
Uses VADER sentiment, lexical analysis, and rule-based trait scoring.
"""

import re
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.preprocessing import MinMaxScaler

# ── Trait Dimensions ──────────────────────────────────────────────────────────

TRAIT_NAMES = ["confidence", "aggression", "optimism", "risk_taking", "discipline"]

TRAIT_LABELS = {
    "confidence":  ("Hesitant", "Confident"),
    "aggression":  ("Passive", "Assertive"),
    "optimism":    ("Pessimistic", "Optimistic"),
    "risk_taking": ("Cautious", "Bold"),
    "discipline":  ("Flexible", "Disciplined"),
}

# ── Behavioral Questions ──────────────────────────────────────────────────────

QUESTIONS = [
    # Confidence (Q1-Q4)
    {
        "text": "You're in a meeting and disagree with a senior colleague. What do you do?",
        "options": [
            ("Stay silent and go along with it", 0.15),
            ("Mention it privately after the meeting", 0.40),
            ("Politely voice your disagreement in the meeting", 0.70),
            ("Directly challenge their point with evidence", 0.95),
        ],
        "trait": "confidence",
    },
    {
        "text": "A stranger compliments your work publicly. How do you react?",
        "options": [
            ("Feel awkward, deflect the compliment", 0.15),
            ("Say thanks but quickly change the subject", 0.40),
            ("Thank them and briefly explain your process", 0.70),
            ("Own it fully — 'Yeah, I put real effort into that'", 0.95),
        ],
        "trait": "confidence",
    },
    {
        "text": "You're asked to lead a project you've never done before. Your first thought?",
        "options": [
            ("I'm not qualified for this", 0.10),
            ("I'll try but I might need a lot of help", 0.35),
            ("I'll figure it out as I go", 0.65),
            ("Great — new challenge, let's go", 0.95),
        ],
        "trait": "confidence",
    },
    {
        "text": "How do you feel about presenting your ideas to a room of experts?",
        "options": [
            ("Terrified — I'd avoid it if possible", 0.10),
            ("Nervous but I'd prepare extensively", 0.35),
            ("A bit anxious but mostly excited", 0.65),
            ("Thrilled — I know my stuff", 0.95),
        ],
        "trait": "confidence",
    },
    # Aggression / Assertiveness (Q5-Q8)
    {
        "text": "Someone cuts in line in front of you. What do you do?",
        "options": [
            ("Nothing — not worth the conflict", 0.10),
            ("Give them a look but say nothing", 0.35),
            ("Politely tell them there's a line", 0.70),
            ("Firmly tell them to go to the back", 0.95),
        ],
        "trait": "aggression",
    },
    {
        "text": "A friend repeatedly cancels plans last minute. How do you handle it?",
        "options": [
            ("Keep rescheduling without saying anything", 0.10),
            ("Hint that it bothers you", 0.35),
            ("Have a direct conversation about it", 0.70),
            ("Tell them bluntly it's disrespectful", 0.95),
        ],
        "trait": "aggression",
    },
    {
        "text": "Your team is making a decision you strongly oppose. What do you do?",
        "options": [
            ("Go with the group consensus", 0.15),
            ("Express mild concern then back down", 0.35),
            ("Argue your case clearly and stand firm", 0.75),
            ("Refuse to proceed until your point is considered", 0.95),
        ],
        "trait": "aggression",
    },
    {
        "text": "Someone takes credit for your work. Your reaction?",
        "options": [
            ("Let it go — it's not that important", 0.10),
            ("Feel upset but don't say anything", 0.30),
            ("Privately correct the record", 0.65),
            ("Call it out immediately and publicly", 0.95),
        ],
        "trait": "aggression",
    },
    # Optimism (Q9-Q12)
    {
        "text": "You fail at something important. What's your internal monologue?",
        "options": [
            ("I knew this would happen. I always fail.", 0.10),
            ("This sucks. Maybe I'm not cut out for this.", 0.30),
            ("Setback, not failure. I'll adjust and try again.", 0.70),
            ("This is data. Now I know exactly what to fix.", 0.95),
        ],
        "trait": "optimism",
    },
    {
        "text": "You hear about a major industry disruption. First thought?",
        "options": [
            ("This could destroy everything I've built", 0.10),
            ("I'm worried but maybe it won't affect me directly", 0.35),
            ("Change is coming — time to adapt", 0.70),
            ("This is an opportunity. Early movers win.", 0.95),
        ],
        "trait": "optimism",
    },
    {
        "text": "When you think about the next 5 years of your life, you feel…",
        "options": [
            ("Anxious — too many unknowns", 0.15),
            ("Uncertain but hopeful", 0.40),
            ("Mostly excited with some realistic caution", 0.70),
            ("Unstoppable — the best is ahead", 0.95),
        ],
        "trait": "optimism",
    },
    {
        "text": "Monday morning. How do you feel?",
        "options": [
            ("Dread. Pure dread.", 0.10),
            ("Meh, just another week to survive", 0.30),
            ("Alright, let's get some things done", 0.65),
            ("Energized — new week, new wins", 0.95),
        ],
        "trait": "optimism",
    },
    # Risk-Taking (Q13-Q16)
    {
        "text": "You get a job offer that pays 2x but requires relocating to an unknown city. What do you do?",
        "options": [
            ("Decline — too much uncertainty", 0.10),
            ("Research extensively, probably decline", 0.35),
            ("Seriously consider it and likely go", 0.70),
            ("Accept immediately — life's too short", 0.95),
        ],
        "trait": "risk_taking",
    },
    {
        "text": "You have a business idea but it requires investing your savings. Your move?",
        "options": [
            ("Keep the savings — too risky", 0.10),
            ("Maybe invest a small portion to test", 0.40),
            ("Invest a significant chunk if the plan is solid", 0.70),
            ("All in. Calculated bets build empires.", 0.95),
        ],
        "trait": "risk_taking",
    },
    {
        "text": "A once-in-a-lifetime travel opportunity comes up, but timing is bad. You…",
        "options": [
            ("Pass — responsibilities first", 0.15),
            ("Feel torn but ultimately stay safe", 0.35),
            ("Find a way to make it work", 0.70),
            ("Book the ticket first, figure out the rest later", 0.95),
        ],
        "trait": "risk_taking",
    },
    {
        "text": "In a card game, you have a decent hand but could swap for an unknown one. You…",
        "options": [
            ("Keep what you have — safe play", 0.15),
            ("Hold but feel tempted", 0.35),
            ("Swap one card, keep the rest", 0.60),
            ("Swap the whole hand — fortune favors the bold", 0.95),
        ],
        "trait": "risk_taking",
    },
    # Discipline (Q17-Q20)
    {
        "text": "It's 6 AM. Your alarm goes off for a workout. What happens?",
        "options": [
            ("Snooze 5 times, skip the workout", 0.10),
            ("Lie in bed debating, maybe get up", 0.30),
            ("Get up after one snooze", 0.65),
            ("Already awake before the alarm", 0.95),
        ],
        "trait": "discipline",
    },
    {
        "text": "You set a personal deadline for a side project. The day comes and you're not done. You…",
        "options": [
            ("Abandon the project — too hard", 0.10),
            ("Push the deadline indefinitely", 0.30),
            ("Extend by one week with a concrete plan", 0.65),
            ("Stay up and finish it tonight", 0.95),
        ],
        "trait": "discipline",
    },
    {
        "text": "How do you handle a boring but necessary task?",
        "options": [
            ("Procrastinate until the last possible second", 0.10),
            ("Do it eventually, lots of breaks", 0.35),
            ("Schedule it and get it done on time", 0.70),
            ("Do it first thing — eat the frog", 0.95),
        ],
        "trait": "discipline",
    },
    {
        "text": "You're on a diet and someone offers you cake at a party. You…",
        "options": [
            ("Eat two slices — willpower is a myth", 0.10),
            ("Have one slice and feel guilty", 0.35),
            ("Take a small piece, enjoy it, move on", 0.60),
            ("Politely decline — commitment is commitment", 0.95),
        ],
        "trait": "discipline",
    },
]

# ── Lexical Markers ───────────────────────────────────────────────────────────

TRAIT_LEXICONS = {
    "confidence": {
        "positive": ["certain", "sure", "know", "can", "will", "capable", "strong",
                      "ready", "able", "determined", "believe", "achieve", "lead"],
        "negative": ["maybe", "perhaps", "unsure", "doubt", "can't", "afraid",
                      "worried", "hope", "possibly", "try", "might", "if only"],
    },
    "aggression": {
        "positive": ["demand", "insist", "confront", "challenge", "push", "fight",
                      "stand", "force", "refuse", "direct", "blunt", "firm"],
        "negative": ["please", "sorry", "apologize", "excuse", "gently", "quietly",
                      "avoid", "hope", "wish", "hesitate", "soft", "careful"],
    },
    "optimism": {
        "positive": ["great", "amazing", "opportunity", "grow", "improve", "win",
                      "bright", "excited", "love", "best", "wonderful", "thrive"],
        "negative": ["terrible", "awful", "fail", "lose", "worst", "hopeless",
                      "never", "disaster", "hate", "stuck", "miserable", "doomed"],
    },
    "risk_taking": {
        "positive": ["risk", "bold", "dare", "adventure", "leap", "chance",
                      "gamble", "spontaneous", "new", "explore", "unknown", "dive"],
        "negative": ["safe", "careful", "cautious", "plan", "secure", "stable",
                      "protect", "avoid", "risk-free", "steady", "conservative"],
    },
    "discipline": {
        "positive": ["schedule", "routine", "focus", "commit", "consistent",
                      "habit", "early", "organize", "prioritize", "finish", "daily"],
        "negative": ["procrastinate", "lazy", "skip", "later", "tomorrow",
                      "distract", "binge", "slack", "forget", "random", "chaotic"],
    },
}


# ── Analysis Functions ────────────────────────────────────────────────────────

def analyze_text_sample(text: str) -> dict:
    """Extract trait signals from a free-text writing sample."""
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    words = re.findall(r'\b\w+\b', text.lower())
    word_set = set(words)

    trait_scores = {}
    for trait, lexicon in TRAIT_LEXICONS.items():
        pos_hits = len(word_set & set(lexicon["positive"]))
        neg_hits = len(word_set & set(lexicon["negative"]))
        total = pos_hits + neg_hits
        if total > 0:
            trait_scores[trait] = pos_hits / total
        else:
            trait_scores[trait] = 0.5  # neutral

    # Adjust optimism with overall sentiment
    optimism_boost = (sentiment["compound"] + 1) / 2  # normalize -1..1 → 0..1
    trait_scores["optimism"] = 0.6 * trait_scores["optimism"] + 0.4 * optimism_boost

    return {
        "sentiment": sentiment,
        "trait_signals": trait_scores,
        "word_count": len(words),
        "avg_sentence_len": len(words) / max(text.count('.') + text.count('!') + text.count('?'), 1),
    }


def compute_profile(question_answers: dict, text_analysis: dict = None) -> dict:
    """
    Build a personality profile from questionnaire scores and optional text analysis.

    Parameters
    ----------
    question_answers : dict
        {trait_name: [score1, score2, ...]} from questionnaire
    text_analysis : dict or None
        Output of analyze_text_sample()

    Returns
    -------
    dict  {trait_name: float 0-100}
    """
    profile = {}
    for trait in TRAIT_NAMES:
        q_scores = question_answers.get(trait, [])
        q_mean = np.mean(q_scores) if q_scores else 0.5

        if text_analysis and trait in text_analysis.get("trait_signals", {}):
            text_score = text_analysis["trait_signals"][trait]
            combined = 0.75 * q_mean + 0.25 * text_score
        else:
            combined = q_mean

        profile[trait] = round(combined * 100, 1)

    return profile


def apply_modifications(base_profile: dict, modifications: dict) -> dict:
    """
    Apply slider modifications to create the parallel clone profile.

    Parameters
    ----------
    base_profile : dict   {trait: 0-100}
    modifications : dict  {trait: -50 to +50}

    Returns
    -------
    dict  {trait: 0-100 clamped}
    """
    clone_profile = {}
    for trait in TRAIT_NAMES:
        base_val = base_profile.get(trait, 50)
        mod_val = modifications.get(trait, 0)
        clone_profile[trait] = round(max(0, min(100, base_val + mod_val)), 1)
    return clone_profile


def compute_divergence(base: dict, clone: dict) -> dict:
    """Compute divergence metrics between base and clone profiles."""
    diffs = {t: abs(clone.get(t, 50) - base.get(t, 50)) for t in TRAIT_NAMES}
    total_divergence = np.mean(list(diffs.values()))
    max_trait = max(diffs, key=diffs.get)

    # Stability index: how far clone is from extreme values
    extremes = [abs(clone[t] - 50) for t in TRAIT_NAMES]
    stability = 100 - np.mean(extremes)

    return {
        "trait_diffs": diffs,
        "identity_divergence": round(total_divergence, 1),
        "clone_stability": round(stability, 1),
        "dominant_shift": max_trait,
    }


def get_personality_archetype(profile: dict):
    """Map a profile to a named archetype with description."""
    conf = profile.get("confidence", 50)
    agg = profile.get("aggression", 50)
    opt = profile.get("optimism", 50)
    risk = profile.get("risk_taking", 50)
    disc = profile.get("discipline", 50)

    # Dominant trait
    traits_sorted = sorted(profile.items(), key=lambda x: x[1], reverse=True)
    top_trait = traits_sorted[0][0]
    top_val = traits_sorted[0][1]

    if conf > 75 and agg > 70:
        return "⚡ The Commander", "Radiates authority. Speaks with conviction. Never backs down."
    elif opt > 75 and risk > 70:
        return "🚀 The Visionary", "Sees opportunity everywhere. Leaps before others even look."
    elif disc > 80 and conf > 60:
        return "🎯 The Architect", "Methodical, relentless, builds empires brick by brick."
    elif opt > 70 and conf > 65:
        return "☀️ The Catalyst", "Infectious energy. Makes everyone around them believe."
    elif agg > 70 and disc > 65:
        return "🔥 The Enforcer", "Gets things done. No excuses, no delays, no mercy on mediocrity."
    elif risk > 70 and agg > 60:
        return "🃏 The Maverick", "Unpredictable, bold, rewrites the rules of the game."
    elif disc > 70 and opt > 60:
        return "🏔️ The Stoic", "Calm, grounded, unshakeable. Progress through patience."
    elif conf < 40 and agg < 40:
        return "🌊 The Observer", "Thoughtful, cautious, sees what others miss from the sidelines."
    elif opt < 40:
        return "🌑 The Realist", "Clear-eyed, pragmatic. Prepares for the worst, earns the best."
    elif top_val > 70:
        label_map = {
            "confidence": ("💎 The Believer", "Self-assured core. Trusts their own judgment above all."),
            "aggression": ("⚔️ The Challenger", "Confronts problems head-on. Speaks truth to power."),
            "optimism": ("🌅 The Optimist", "Finds silver linings in storms. Relentlessly hopeful."),
            "risk_taking": ("🎲 The Gambler", "Thrives in uncertainty. Bets big, wins bigger."),
            "discipline": ("⏰ The Machine", "Routine is religion. Consistency is their superpower."),
        }
        return label_map.get(top_trait, ("🔮 The Enigma", "A unique blend that defies easy categorization."))
    else:
        return "⚖️ The Balanced", "Well-rounded, adaptable. Jack of all trades, master of composure."
