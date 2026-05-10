"""
Parallel Self — Clone Response Engine
======================================
Generates simulated responses for both the "Real You" and "Parallel Clone"
based on personality profiles across different scenarios.
Uses rule-based response transformation with trait-weighted templates.
"""

import random

# ── Scenario Definitions ──────────────────────────────────────────────────────

SCENARIOS = {
    "job_interview": {
        "icon": "💼",
        "title": "Job Interview",
        "description": "The interviewer says: 'Tell me about a time you failed and what you learned.'",
        "context": "Professional setting, high stakes, being evaluated.",
    },
    "argument": {
        "icon": "⚡",
        "title": "Heated Argument",
        "description": "A colleague publicly blames you for a project delay that wasn't your fault.",
        "context": "Workplace conflict, reputation at stake, audience watching.",
    },
    "public_speaking": {
        "icon": "🎤",
        "title": "Public Speaking",
        "description": "You're about to present your idea to 200 people and your slides just crashed.",
        "context": "High pressure, large audience, technical failure.",
    },
    "relationship": {
        "icon": "💬",
        "title": "Relationship Conflict",
        "description": "Your partner says: 'You never prioritize us. Work always comes first.'",
        "context": "Emotional vulnerability, personal relationship, needs empathy and honesty.",
    },
    "negotiation": {
        "icon": "🤝",
        "title": "Salary Negotiation",
        "description": "HR offers you 20% below your expected salary. They say it's the 'final offer.'",
        "context": "Financial stakes, power dynamics, need to advocate for yourself.",
    },
    "rejection": {
        "icon": "🚫",
        "title": "Handling Rejection",
        "description": "You just got rejected from your dream opportunity. A friend asks 'How are you?'",
        "context": "Emotional moment, self-image challenged, needs resilience.",
    },
    "leadership": {
        "icon": "👑",
        "title": "Leadership Moment",
        "description": "Your team is demoralized after a major setback. They're looking to you for direction.",
        "context": "Leadership pressure, team morale, need to inspire.",
    },
    "boundary": {
        "icon": "🛡️",
        "title": "Setting Boundaries",
        "description": "Your boss asks you to work the weekend — again. You had plans.",
        "context": "Work-life balance, authority dynamics, personal limits.",
    },
}


# ── Response Templates ────────────────────────────────────────────────────────
# Each scenario has responses keyed by trait intensity levels:
#   low (0-35), mid (36-65), high (66-100)
# The engine blends across the dominant traits.

RESPONSE_BANK = {
    "job_interview": {
        "confidence": {
            "low": "Honestly, I… I've had a few setbacks. I'm not sure I handled them well. I tend to doubt myself after failures, but I try to learn from them. I hope that counts.",
            "mid": "I had a project that didn't meet expectations. It was tough, but I took time to analyze what went wrong and adjusted my approach. I grew from the experience.",
            "high": "I led an initiative that failed to hit its targets. I owned that failure publicly, dissected every decision I made, rebuilt the strategy, and the next version outperformed the original by 40%. Failure is just unfinished success.",
        },
        "aggression": {
            "low": "I prefer not to dwell on failures too much… I just try to quietly do better next time.",
            "mid": "I'm direct about my failures. I failed, I analyzed why, and I made concrete changes. That's the process.",
            "high": "Let me be blunt — I failed hard. And I'll tell you exactly why, because I've already torn that failure apart and rebuilt myself from it. I don't hide from it, I weaponize it.",
        },
        "optimism": {
            "low": "Failures have been… difficult. Sometimes I wonder if I'm on the right path. But I keep going because what else can you do?",
            "mid": "Every failure taught me something specific. I see them as part of the journey, even when they sting.",
            "high": "Honestly? My biggest failure was the best thing that happened to me. It forced me to level up in ways I never would have otherwise. I'm grateful for every setback.",
        },
        "risk_taking": {
            "low": "I try to avoid situations where failure is likely. I plan carefully. When I have failed, it was usually because of unforeseen factors.",
            "mid": "I took a calculated risk that didn't pan out. But I'd rather try and fail than wonder 'what if.'",
            "high": "I bet on a radical approach that everyone said was too risky. It blew up. And I'd do it again — because the next bet landed and it changed everything.",
        },
        "discipline": {
            "low": "I'll be honest, I sometimes struggle with follow-through. But I'm working on building better habits and systems.",
            "mid": "After that failure, I built a structured review process. Every week I track what worked and what didn't. Systematically improving.",
            "high": "I run post-mortems on every failure within 24 hours. I have a documented playbook of lessons learned. Every failure feeds my system. Nothing is wasted.",
        },
    },
    "argument": {
        "confidence": {
            "low": "I… I don't think that's entirely accurate, but maybe I did contribute to the delay somehow. I'll look into it.",
            "mid": "I appreciate the feedback, but I'd like to clarify my role in this. The timeline issues originated from factors outside my control, and I have documentation to show that.",
            "high": "Let me stop you right there. I have the receipts — every milestone I delivered was on time. Let's look at the actual timeline data before we assign blame.",
        },
        "aggression": {
            "low": "*stays quiet, feels hurt, plans to address it later via email*",
            "mid": "I'd prefer we discuss this with facts on the table rather than pointing fingers in front of the team.",
            "high": "No. You don't get to rewrite history in front of everyone. I'm going to correct the record right now, and I expect the same honesty from you.",
        },
        "optimism": {
            "low": "Great, another thing that's apparently my fault. This is becoming a pattern and I'm tired of it.",
            "mid": "This is frustrating, but let's focus on solving the problem rather than assigning blame. We can do a proper review after.",
            "high": "Look, the delay happened. Pointing fingers won't fix it. But we can absolutely recover this timeline — let me show you how.",
        },
        "risk_taking": {
            "low": "I'll accept the criticism for now to avoid escalation, then address it through proper channels.",
            "mid": "I'm going to address this now, even if it's uncomfortable. The truth matters more than keeping the peace.",
            "high": "I'll raise this with the leadership team directly. If the process is broken, let's fix it rather than sacrifice someone's reputation.",
        },
        "discipline": {
            "low": "I… I should have tracked things better. Let me figure out where things went off track.",
            "mid": "I've got my task logs and communication records. Let's schedule a review meeting to go through the actual timeline objectively.",
            "high": "I log every deliverable with timestamps. Here's the Gantt chart, here are the handoff dates. The data speaks for itself — the delay started upstream.",
        },
    },
    "public_speaking": {
        "confidence": {
            "low": "*freezes* I… uh… let me try to get the slides back. I'm sorry, just give me a moment… *visible panic*",
            "mid": "*takes a breath* Okay, technical difficulty. Let me walk you through the key points while we get this sorted. I know this material well enough.",
            "high": "*smiles* Well, looks like the slides decided to test my improvisation skills. Good news — I know this material cold. Let me take you through it, and I promise it'll be even better this way.",
        },
        "aggression": {
            "low": "*apologizes repeatedly* I'm so sorry about this, I should have had a backup...",
            "mid": "Slides are down, but the idea isn't. Let me give you the pitch directly — no filter, no pretty graphics. Just the core of what matters.",
            "high": "Forget the slides. You came here for the idea, not a slideshow. Let me give it to you raw and unfiltered. This is going to be more memorable anyway.",
        },
        "optimism": {
            "low": "This is a disaster… I'm sorry, I'll try to salvage what I can.",
            "mid": "Unexpected, but not a problem. Some of the best presentations I've seen were off-the-cuff. Let's make this one of them.",
            "high": "Actually, this might be a blessing in disguise. Now you get the real, passionate version instead of bullet points. Let's do this.",
        },
        "risk_taking": {
            "low": "*pulls out printed backup notes* I always carry a backup. Let me read from my notes while IT fixes the slides.",
            "mid": "I'll go off-script. It might be a bit rough, but I'd rather engage with you directly than stall.",
            "high": "New plan — interactive session. Forget the one-way presentation. Ask me anything about this idea. Let's make this a conversation.",
        },
        "discipline": {
            "low": "I... I should have tested the setup beforehand. Let me try to remember the key points...",
            "mid": "I rehearsed this enough times that I can do it from memory. Let me walk through each section systematically.",
            "high": "I always rehearse without slides as part of my prep. This is just Tuesday for me. Let me take you through all five sections, in order, from memory.",
        },
    },
    "relationship": {
        "confidence": {
            "low": "You're right... I'm sorry. I'm a mess. I don't know how to fix this. I'll try harder, I promise.",
            "mid": "I hear you, and I know there's truth in that. But I want you to know it's not because you don't matter — I've been struggling to balance everything. Let's figure this out together.",
            "high": "I hear you, and I take this seriously. But I need to be honest — I've been building something important, and I don't want to apologize for my ambition. What I do want is for us to design a life where both our needs are met. Let's talk solutions.",
        },
        "aggression": {
            "low": "I'm sorry... you're right. I'll cancel my work things this weekend.",
            "mid": "That's a fair point, but saying 'never' isn't accurate either. Let's talk about what specifically needs to change.",
            "high": "I'm not going to accept 'never' because that's not true and you know it. But your feelings are valid. Let's have an honest conversation without exaggeration.",
        },
        "optimism": {
            "low": "Maybe we're just not compatible with what we want from life...",
            "mid": "I know it doesn't feel great right now, but I believe we can find a balance. This is a rough patch, not a dead end.",
            "high": "This conversation is actually a good sign — it means we both care enough to fight for this. Let's use this energy to build something better.",
        },
        "risk_taking": {
            "low": "I'll adjust my schedule immediately. I don't want to risk losing you.",
            "mid": "How about we try something different — a weekly ritual that's just ours, non-negotiable, no matter what?",
            "high": "You know what, let's do something drastic. Let me take next month off. We'll travel, reconnect, reset. Life's too short for this pattern.",
        },
        "discipline": {
            "low": "You're right, I keep saying I'll change but I don't follow through. I don't blame you for being frustrated.",
            "mid": "I want to set specific times that are ours. Like a recurring commitment I treat as seriously as any work meeting.",
            "high": "Starting tomorrow, 7-9 PM is us-time. No phone, no laptop. I'm putting it in my calendar as a non-negotiable. And every Saturday morning is ours. Let me show you with actions.",
        },
    },
    "negotiation": {
        "confidence": {
            "low": "Oh... okay. I mean, I was hoping for more, but if that's the best you can do, I understand.",
            "mid": "I appreciate the offer, but I've done my research and my skills command a higher range. I'd like to discuss how we can get closer to my expectations.",
            "high": "I respect the offer, but let's be real — you reached out to me because of what I bring to the table. The market rate for my skill set is X, and I've consistently exceeded targets. Let's find a number that reflects that.",
        },
        "aggression": {
            "low": "I understand. Could we maybe revisit this in six months after I've proven myself?",
            "mid": "I don't accept that this is the final offer. Every number is negotiable when both sides see the value. Let me walk you through why.",
            "high": "'Final offer' is a negotiation tactic, and we both know it. I have competing offers on the table. Let's have an honest conversation about what it takes to close this today.",
        },
        "optimism": {
            "low": "I guess the market is tough right now. Maybe I should be grateful for the opportunity.",
            "mid": "I believe we can find a middle ground that works for both of us. This role is a great fit, and I think a fair comp reflects that mutual win.",
            "high": "I see this as the beginning of an incredible partnership. And the best partnerships start with fair terms. Let me explain why investing more in me now pays dividends for years.",
        },
        "risk_taking": {
            "low": "I'll accept the offer. I'd rather have the security of a confirmed position.",
            "mid": "I'm willing to walk away if we can't find a number that respects my value. But I'd prefer we find that number together.",
            "high": "I'll be transparent — I'd rather walk away from this than accept a number I'll resent. Pay me what I'm worth, and you'll get someone who gives 200%.",
        },
        "discipline": {
            "low": "I didn't really prepare specific numbers... let me get back to you?",
            "mid": "I've researched comp data from three sources. The median for this role at this level is X. Here's how I see the breakdown.",
            "high": "I've prepared a detailed compensation analysis: market data, my performance metrics, revenue I've generated, and a projection of my impact in this role. Here's the document.",
        },
    },
    "rejection": {
        "confidence": {
            "low": "Honestly? Not great. I keep wondering what I did wrong. Maybe I'm just not good enough for that level.",
            "mid": "It stings, I won't lie. But I know my worth isn't defined by one decision. I'll process it and come back stronger.",
            "high": "Disappointed, sure. But they missed out. I know what I bring. Someone else will see it, or I'll build something better on my own.",
        },
        "aggression": {
            "low": "I'm fine... *clearly not fine* ...let's talk about something else.",
            "mid": "I'm hurt, and I'm not going to pretend I'm not. But I've already started applying elsewhere. Sitting in sadness doesn't fix anything.",
            "high": "Pissed, honestly. But that anger is fuel. I'm channeling every bit of it into making my next move so good they'll regret passing on me.",
        },
        "optimism": {
            "low": "I feel like nothing ever works out. What's the point of trying so hard?",
            "mid": "It hurts now, but I believe something better is coming. Usually, rejections redirect you to where you're actually meant to be.",
            "high": "Best thing that could have happened. Seriously. This rejection just freed me up for something I haven't even imagined yet. I can feel it.",
        },
        "risk_taking": {
            "low": "I think I'll play it safer next time. Maybe I was reaching too high.",
            "mid": "I don't regret going for it. You miss 100% of the shots you don't take. I'll aim just as high next time.",
            "high": "Next time I'm aiming even higher. If you're going to get rejected anyway, might as well get rejected from the top.",
        },
        "discipline": {
            "low": "I need a few days off to recover from this. I just can't focus on anything right now.",
            "mid": "I'm giving myself today to feel it. Tomorrow, I'm back on the grind with a revised strategy.",
            "high": "I've already updated my portfolio, reached out to three new contacts, and scheduled time to analyze why I didn't get it. The grieving period is over — it lasted 30 minutes.",
        },
    },
    "leadership": {
        "confidence": {
            "low": "I know things look bad... I'm not sure what the right move is, but let's try to figure this out together?",
            "mid": "We took a hit. I won't sugarcoat it. But I've seen what this team can do, and I believe we can turn this around. Here's what I think we should focus on.",
            "high": "Listen up. We lost this battle, not the war. I've already mapped out our recovery plan. I've been in worse spots, and we came out on top. Follow my lead.",
        },
        "aggression": {
            "low": "I know everyone's frustrated. Please take some time, and we'll regroup when you're ready.",
            "mid": "We're not going to sit here feeling sorry for ourselves. The setback happened. Now — what are we going to do about it? I need solutions, not complaints.",
            "high": "Enough. We lost. It's done. Now I need every person in this room to bring me one thing: their best idea for the comeback. We meet in one hour. No excuses.",
        },
        "optimism": {
            "low": "I won't lie to you — this is bad, and I'm not sure things will get better quickly. But we'll do our best.",
            "mid": "Every great team has a chapter like this in their story. The question is whether this is the chapter where we gave up, or where we turned it around. I vote turnaround.",
            "high": "You know what the best part of a setback is? The comeback story. And ours is going to be legendary. I can already see it.",
        },
        "risk_taking": {
            "low": "Let's go back to what was working before and rebuild from a safe foundation.",
            "mid": "We could play it safe and recover slowly. Or we could use this moment to pivot and try the approach we've been too cautious to attempt. I say we go for it.",
            "high": "Forget recovery. This setback just gave us permission to tear up the playbook and try something nobody expects. Let's make them remember this moment.",
        },
        "discipline": {
            "low": "Take the rest of the day. We'll figure out a plan... eventually.",
            "mid": "Here's the plan: this week we stabilize, next week we strategize, week three we execute. I need everyone committed to this timeline.",
            "high": "I've already drafted the recovery plan. Daily standups at 9 AM starting tomorrow. Weekly milestones. Bi-weekly reviews. We're running this like a military operation until we're back on top.",
        },
    },
    "boundary": {
        "confidence": {
            "low": "I... had plans, but... I guess I can rearrange. When do you need me?",
            "mid": "I have personal commitments this weekend. I can finish the urgent items by Friday EOD, but the weekend is blocked.",
            "high": "I appreciate the urgency, but I've already committed this weekend. I protect my personal time because it makes me better at my job Monday through Friday. Let's find another way.",
        },
        "aggression": {
            "low": "*sighs internally* ...Sure, I can come in. What time?",
            "mid": "I'd like to help, but I need to be direct — this is the third weekend in a row. If this keeps happening, we need to discuss workload distribution.",
            "high": "No. I've worked the last three weekends. This is a staffing problem, not a dedication problem. I'll be available Monday at 8 AM sharp.",
        },
        "optimism": {
            "low": "This job is consuming my life... but I guess it's just how things are.",
            "mid": "I think we can find a solution that doesn't require weekend work. Let me propose a prioritization framework for these situations.",
            "high": "I love what we're building here, which is exactly why I need to recharge this weekend. A rested me delivers 10x. Trust the process.",
        },
        "risk_taking": {
            "low": "I'll come in. I can't afford to be seen as not a team player.",
            "mid": "I'm going to be honest about my boundaries, even if it's uncomfortable. My weekend is important to me.",
            "high": "I'll be honest — if weekend work becomes the norm, I'll need to reevaluate my position here. I'm too good at what I do to burn out.",
        },
        "discipline": {
            "low": "I mean, I didn't have specific plans, so... I guess I can come in.",
            "mid": "I have a structured personal schedule that I maintain for my wellbeing. I can give you Friday evening, but Saturday and Sunday are non-negotiable.",
            "high": "My weekend routine is strategic: Saturday for physical health, Sunday for mental recharge. This isn't laziness — it's performance optimization. I'll deliver everything needed by Friday 6 PM.",
        },
    },
}


# ── Response Generation ───────────────────────────────────────────────────────

def _get_intensity(value: float) -> str:
    """Convert 0-100 trait value to intensity level."""
    if value <= 35:
        return "low"
    elif value <= 65:
        return "mid"
    else:
        return "high"


def generate_response(profile: dict, scenario_key: str) -> str:
    """
    Generate a blended response based on personality profile for a scenario.

    Selects the response from the dominant trait and weaves in elements
    from secondary traits for a natural, multi-dimensional answer.
    """
    if scenario_key not in RESPONSE_BANK:
        return "Scenario not found."

    scenario_bank = RESPONSE_BANK[scenario_key]
    trait_responses = {}

    for trait in profile:
        if trait in scenario_bank:
            intensity = _get_intensity(profile[trait])
            trait_responses[trait] = scenario_bank[trait][intensity]

    if not trait_responses:
        return "Unable to generate response for this profile."

    # Sort traits by value — dominant first
    sorted_traits = sorted(profile.items(), key=lambda x: x[1], reverse=True)

    # Primary response from the most dominant trait
    primary_trait = sorted_traits[0][0]
    if primary_trait in trait_responses:
        primary = trait_responses[primary_trait]
    else:
        primary = list(trait_responses.values())[0]

    # If a secondary trait is also high (>60) and differs in intensity, blend
    secondary_notes = []
    for trait, val in sorted_traits[1:3]:
        if val > 55 and trait in trait_responses:
            sec_response = trait_responses[trait]
            if sec_response != primary:
                # Extract a distinctive phrase from secondary response
                sentences = [s.strip() for s in sec_response.replace('*', '').split('.') if len(s.strip()) > 20]
                if sentences:
                    secondary_notes.append(sentences[-1].strip())

    if secondary_notes:
        blended = primary.rstrip('.')
        addition = secondary_notes[0]
        if not addition.endswith('.'):
            addition += '.'
        blended += '. ' + addition
        return blended

    return primary


def generate_comparison(base_profile: dict, clone_profile: dict, scenario_key: str) -> dict:
    """Generate responses for both profiles and provide comparison analysis."""
    real_response = generate_response(base_profile, scenario_key)
    clone_response = generate_response(clone_profile, scenario_key)

    # Analyze differences
    base_dominant = max(base_profile, key=base_profile.get)
    clone_dominant = max(clone_profile, key=clone_profile.get)

    base_intensity = _get_intensity(base_profile[base_dominant])
    clone_intensity = _get_intensity(clone_profile[clone_dominant])

    # Generate analysis
    analysis_parts = []

    if base_dominant != clone_dominant:
        analysis_parts.append(
            f"**Dominant Trait Shift**: Your base self leads with *{base_dominant}* "
            f"while your clone leads with *{clone_dominant}*."
        )

    # Compare specific traits
    biggest_diff_trait = max(base_profile.keys(),
                            key=lambda t: abs(clone_profile.get(t, 50) - base_profile.get(t, 50)))
    diff_val = clone_profile[biggest_diff_trait] - base_profile[biggest_diff_trait]
    direction = "higher" if diff_val > 0 else "lower"
    analysis_parts.append(
        f"**Biggest Shift**: {biggest_diff_trait.replace('_', ' ').title()} is "
        f"{abs(diff_val):.0f} points {direction} in the clone."
    )

    if clone_profile.get("confidence", 50) > base_profile.get("confidence", 50) + 15:
        analysis_parts.append("📈 The clone shows noticeably more self-assurance in its language.")

    if clone_profile.get("aggression", 50) > base_profile.get("aggression", 50) + 15:
        analysis_parts.append("⚡ The clone is significantly more direct and confrontational.")

    if clone_profile.get("optimism", 50) > base_profile.get("optimism", 50) + 15:
        analysis_parts.append("☀️ The clone frames the situation more positively and sees more opportunity.")

    if not analysis_parts:
        analysis_parts.append("The profiles are quite similar — subtle shifts in tone rather than approach.")

    return {
        "real_response": real_response,
        "clone_response": clone_response,
        "analysis": "\n\n".join(analysis_parts),
        "scenario": SCENARIOS[scenario_key],
    }
