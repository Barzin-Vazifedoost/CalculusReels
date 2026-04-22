#!/usr/bin/env python3
"""
Generate calculus reel videos: Gemini designs the animation → Manim renders → TTS narrates.

Pipeline:
  1. Gemini generates a structured animation plan (JSON) tailored to each topic
  2. The plan is mapped to Manim animation primitives
  3. Manim renders the sketch-style animation
  4. Gemini writes a narration script
  5. gTTS converts narration to audio
  6. ffmpeg combines animation + audio into final MP4

Usage:
  python scripts/generate_reels.py --id 1            # generate one reel
  python scripts/generate_reels.py --id 1 --preview   # animation only, skip AI
  python scripts/generate_reels.py                     # generate all 20
  python scripts/generate_reels.py --force             # regenerate everything

Requirements:
  pip install manim google-genai gtts
  brew install cairo pango ffmpeg
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
import textwrap
from pathlib import Path

# ── Paths ──
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = PROJECT_ROOT / "public"
VIDEO_DIR = PUBLIC_DIR / "videos"
AUDIO_DIR = PUBLIC_DIR / "audio"
PLANS_DIR = PROJECT_ROOT / "scripts" / "plans"
ENV_FILE = PROJECT_ROOT / ".env"


def load_api_key():
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip()
    return None


# ═══════════════════════════════════════════════════════════════════
#  TOPIC DEFINITIONS
# ═══════════════════════════════════════════════════════════════════

TOPICS = [
    {"id": 1,  "title": "Introduction to Limits",          "topic": "Limits",       "color": "#3B82F6", "formula": r"\lim_{x \to a} f(x) = L", "description": "the concept of limits — how a function approaches a value as x gets closer to a point"},
    {"id": 2,  "title": "Derivative Rules",                "topic": "Derivatives",  "color": "#8B5CF6", "formula": r"\frac{d}{dx}[x^n] = nx^{n-1}", "description": "the power rule, product rule, and quotient rule for taking derivatives"},
    {"id": 3,  "title": "Chain Rule Explained",            "topic": "Derivatives",  "color": "#8B5CF6", "formula": r"\frac{d}{dx}[f(g(x))] = f'(g(x)) \cdot g'(x)", "description": "the chain rule — how to differentiate composite functions step by step"},
    {"id": 4,  "title": "Integration Basics",              "topic": "Integration",  "color": "#10B981", "formula": r"\int f(x)\,dx = F(x) + C", "description": "the fundamental idea of integration — antiderivatives and the area under a curve"},
    {"id": 5,  "title": "U-Substitution Method",           "topic": "Integration",  "color": "#10B981", "formula": r"\int f(g(x)) \cdot g'(x)\,dx = \int f(u)\,du", "description": "u-substitution — the reverse chain rule for solving integrals"},
    {"id": 6,  "title": "L'Hôpital's Rule",               "topic": "Limits",       "color": "#3B82F6", "formula": r"\lim_{x \to a} \frac{f(x)}{g(x)} = \lim_{x \to a} \frac{f'(x)}{g'(x)}", "description": "L'Hôpital's rule for evaluating indeterminate forms like 0/0"},
    {"id": 7,  "title": "Implicit Differentiation",        "topic": "Derivatives",  "color": "#8B5CF6", "formula": r"\frac{d}{dx}[F(x,y)] = 0 \Rightarrow \frac{dy}{dx}", "description": "implicit differentiation — finding dy/dx when y isn't explicitly solved"},
    {"id": 8,  "title": "Related Rates",                   "topic": "Applications", "color": "#F59E0B", "formula": r"\frac{dA}{dt} = \frac{dA}{dr} \cdot \frac{dr}{dt}", "description": "related rates — connecting how different quantities change with respect to time"},
    {"id": 9,  "title": "Fundamental Theorem of Calculus",  "topic": "Integration",  "color": "#10B981", "formula": r"\int_a^b f(x)\,dx = F(b) - F(a)", "description": "the Fundamental Theorem of Calculus — the deep connection between derivatives and integrals"},
    {"id": 10, "title": "Integration by Parts",            "topic": "Integration",  "color": "#10B981", "formula": r"\int u\,dv = uv - \int v\,du", "description": "integration by parts — the product rule in reverse for integrals"},
    {"id": 11, "title": "Optimization Problems",           "topic": "Applications", "color": "#F59E0B", "formula": r"f'(x) = 0 \Rightarrow \text{critical points}", "description": "optimization — finding maximum and minimum values using calculus"},
    {"id": 12, "title": "Mean Value Theorem",              "topic": "Theorems",     "color": "#EC4899", "formula": r"f'(c) = \frac{f(b) - f(a)}{b - a}", "description": "the Mean Value Theorem — there's always a point where the instantaneous rate equals the average rate"},
    {"id": 13, "title": "Partial Fractions",               "topic": "Integration",  "color": "#10B981", "formula": r"\frac{P(x)}{Q(x)} = \frac{A}{x-a} + \frac{B}{x-b}", "description": "partial fraction decomposition — breaking rational functions into simpler pieces"},
    {"id": 14, "title": "Trigonometric Substitution",      "topic": "Integration",  "color": "#10B981", "formula": r"x = a\sin\theta", "description": "trigonometric substitution — using trig identities to simplify complex integrals"},
    {"id": 15, "title": "Infinite Series Introduction",    "topic": "Series",       "color": "#EF4444", "formula": r"\sum_{n=1}^{\infty} a_n", "description": "infinite series — adding up infinitely many terms and whether they converge"},
    {"id": 16, "title": "Newton's Method",                 "topic": "Applications", "color": "#F59E0B", "formula": r"x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}", "description": "Newton's method — iteratively approximating roots using tangent lines"},
    {"id": 17, "title": "Parametric Equations",            "topic": "Applications", "color": "#F59E0B", "formula": r"\frac{dy}{dx} = \frac{dy/dt}{dx/dt}", "description": "parametric equations — describing curves with x(t) and y(t)"},
    {"id": 18, "title": "Area Between Curves",             "topic": "Integration",  "color": "#10B981", "formula": r"A = \int_a^b [f(x) - g(x)]\,dx", "description": "finding the area between two curves using definite integrals"},
    {"id": 19, "title": "Improper Integrals",              "topic": "Integration",  "color": "#10B981", "formula": r"\int_a^{\infty} f(x)\,dx = \lim_{t \to \infty} \int_a^t f(x)\,dx", "description": "improper integrals — handling integrals with infinite bounds using limits"},
    {"id": 20, "title": "Taylor Series",                   "topic": "Series",       "color": "#EF4444", "formula": r"f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x-a)^n", "description": "Taylor series — representing any smooth function as an infinite polynomial"},
]


# ═══════════════════════════════════════════════════════════════════
#  ANIMATION PRIMITIVES — the building blocks Gemini can choose from
# ═══════════════════════════════════════════════════════════════════

PRIMITIVES_DESCRIPTION = """
You have these animation primitives (building blocks) to design a Manim scene.
Each primitive is a step in the animation sequence.

PRIMITIVES:
1. "show_title" — Write the topic title at the top with an underline
   params: { "text": "...", "color": "#hex" }

2. "show_formula" — Display a formula in monospace font
   params: { "text": "unicode formula string", "color": "#hex", "position": "center"|"below_title"|"top_right" }

3. "show_text" — Show explanatory text
   params: { "text": "...", "color": "#hex"|"white", "position": "center"|"below"|"top", "font_size": 28 }

4. "draw_axes" — Draw a coordinate system
   params: { "x_range": [-3, 3], "y_range": [-2, 4], "position": "center"|"bottom" }

5. "plot_function" — Plot a function on the axes (must follow draw_axes)
   params: { "expression": "python math expression using x", "color": "#hex", "label": "f(x)" }
   Available functions: x**2, x**3, sin(x), cos(x), exp(x), log(x), 1/x, sqrt(x), abs(x)
   Can combine: 0.5*x**2 - 1, sin(x) + 0.5*x, x**3 - 3*x

6. "plot_second_function" — Plot a second function for comparison
   params: { "expression": "python math expression", "color": "#hex", "label": "g(x)" }

7. "animate_tangent" — Show a tangent line sliding along a curve
   params: { "x_values": [list of x positions to move through], "color": "yellow" }

8. "shade_area" — Shade the area under a curve between two x values
   params: { "x_start": -1, "x_end": 2, "color": "#hex", "opacity": 0.3 }

9. "shade_between" — Shade area between two curves
   params: { "x_start": -1, "x_end": 2, "color": "#hex", "opacity": 0.3 }

10. "show_vertical_line" — Draw a vertical dashed line at x
    params: { "x": 2, "color": "#hex" }

11. "show_horizontal_line" — Draw a horizontal dashed line at y
    params: { "y": 1, "color": "#hex" }

12. "show_dot" — Place a highlighted dot at a point
    params: { "x": 1, "y": 2, "color": "yellow", "label": "optional label" }

13. "show_secant_to_tangent" — Animate a secant line becoming a tangent
    params: { "x_point": 1, "dx_values": [2.0, 1.0, 0.5, 0.1], "color": "yellow" }

14. "show_riemann_sum" — Show Riemann rectangles under a curve
    params: { "x_start": 0, "x_end": 3, "n_values": [4, 8, 16, 32], "color": "#hex" }

15. "show_arrow_annotation" — Draw an arrow with a label between two points
    params: { "from": [x1, y1], "to": [x2, y2], "label": "text", "color": "#hex" }

16. "animate_parameter" — Animate a value changing (like approaching a limit)
    params: { "label": "x →", "values": [3, 2.5, 2.1, 2.01, 2.001], "color": "#hex" }

17. "show_iteration" — Show iterative steps (for Newton's method etc.)
    params: { "points": [[x1,y1], [x2,y2], ...], "color": "#hex", "labels": ["x₀", "x₁", ...] }

18. "draw_shape" — Draw a geometric shape
    params: { "shape": "circle"|"rectangle"|"triangle", "color": "#hex", "position": "center" }

19. "transform_equation" — Show one equation transforming into another
    params: { "from_text": "equation 1", "to_text": "equation 2", "color": "#hex" }

20. "fade_out_all" — Clear the screen with a fade
    params: {}

21. "wait" — Pause for dramatic effect
    params: { "duration": 1.0 }

22. "draw_number_line" — Draw a horizontal number line with labeled points
    params: { "points": [0, 1, 2, 3], "highlight": 2, "color": "#hex", "labels": ["0", "1", "2", "3"] }

23. "animate_trace" — Animate a dot tracing along the plotted curve
    params: { "x_start": -2, "x_end": 2, "color": "yellow", "duration": 3.0 }

24. "highlight_flash" — Flash/pulse a mobject to draw attention (uses the last created text/formula)
    params: { "color": "yellow", "count": 2 }

25. "show_brace" — Show a brace annotation between two x-values on the axes
    params: { "x_start": 1, "x_end": 3, "label": "Δx", "color": "#hex", "direction": "down" }

26. "morph_function" — Smoothly morph the plotted curve into a new function
    params: { "expression": "new python math expression", "color": "#hex", "label": "new label" }

27. "show_table" — Display a small table of x/y values
    params: { "headers": ["x", "f(x)"], "rows": [[1, 1], [2, 4], [3, 9]], "color": "#hex" }

28. "draw_arrow" — Draw a labeled arrow between two screen positions
    params: { "start": [x1, y1], "end": [x2, y2], "label": "text", "color": "#hex" }

29. "fade_out_last" — Fade out the most recently added elements (last N mobjects)
    params: { "count": 3 }
"""


# ═══════════════════════════════════════════════════════════════════
#  GEMINI: Generate animation plan
# ═══════════════════════════════════════════════════════════════════

def generate_animation_plan(topic, api_key):
    """Ask Gemini to design a tailored animation sequence."""
    from google import genai

    client = genai.Client(api_key=api_key)

    prompt = f"""You are designing a ~30 second Manim animation for a calculus educational video.

Topic: {topic['title']}
Description: {topic['description']}
Key formula: {topic['formula']}
Theme color: {topic['color']}

{PRIMITIVES_DESCRIPTION}

Design a compelling, educational animation sequence for this topic.
Think about what visual would BEST explain this concept:
- For limits: show a function approaching a value, animate x getting closer
- For derivatives: show tangent lines, slopes changing, secant→tangent
- For integration: shade areas, show Riemann sums converging
- For series: show partial sums accumulating
- For theorems: illustrate the geometric meaning
- For applications: show the real-world scenario

Rules:
- Use 10-16 primitives total to fill ~30 seconds
- Always start with "show_title"
- Include "wait" primitives (0.5-1.5s) between major visual beats for pacing
- Include at least one graph/visual (not just text)
- Use the topic's color (${topic['color']}) as the primary accent
- Make it tell a STORY — build understanding step by step
- Show the concept BEFORE revealing the formula (build anticipation)
- End with the key formula as a takeaway

Return ONLY a JSON array of primitives. No explanation, no markdown, just the JSON.
Example format:
[
  {{"primitive": "show_title", "params": {{"text": "...", "color": "#hex"}}}},
  {{"primitive": "draw_axes", "params": {{"x_range": [-3, 3], "y_range": [-2, 4], "position": "bottom"}}}},
  ...
]"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    # Parse JSON from response
    text = response.text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    try:
        plan = json.loads(text)
        if not isinstance(plan, list):
            raise ValueError("Expected a JSON array")
        return plan
    except (json.JSONDecodeError, ValueError) as e:
        print(f"    Warning: Could not parse Gemini plan ({e}), using fallback")
        return None


# ═══════════════════════════════════════════════════════════════════
#  FALLBACK PLANS — hand-crafted per topic type (when no API key)
# ═══════════════════════════════════════════════════════════════════

def get_fallback_plan(topic):
    """Return a hand-crafted animation plan based on topic type."""
    color = topic["color"]
    title = topic["title"]
    tid = topic["id"]

    # Base: title + formula
    base = [
        {"primitive": "show_title", "params": {"text": title, "color": color}},
    ]

    plans = {
        # ── LIMITS (~30s) ──
        1: base + [
            {"primitive": "show_text", "params": {"text": "What happens as x gets closer to a?", "color": "white", "position": "below_title", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-1, 5], "y_range": [-1, 4], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "0.5*(x-2)**2 + 1", "color": color, "label": "f(x)"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_vertical_line", "params": {"x": 2, "color": "#FFFFFF"}},
            {"primitive": "show_brace", "params": {"x_start": 1, "x_end": 2, "label": "approaching", "color": color, "direction": "down"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "animate_parameter", "params": {"label": "x →", "values": [4, 3.5, 3, 2.5, 2.1, 2.01, 2.001], "color": color}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "show_dot", "params": {"x": 2, "y": 1, "color": "yellow", "label": "L = 1"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "lim x→a f(x) = L", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── DERIVATIVES (~30s) ──
        2: base + [
            {"primitive": "show_text", "params": {"text": "How fast is f(x) changing?", "color": "white", "position": "below_title", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-2, 3], "y_range": [-1, 5], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "x**2", "color": color, "label": "f(x) = x²"}},
            {"primitive": "animate_trace", "params": {"x_start": -1.5, "x_end": 2.5, "color": "yellow", "duration": 2.0}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "show_secant_to_tangent", "params": {"x_point": 1, "dx_values": [2.0, 1.5, 1.0, 0.5, 0.1, 0.01], "color": "yellow"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "animate_tangent", "params": {"x_values": [-1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2], "color": "yellow"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_formula", "params": {"text": "d/dx [xⁿ] = nxⁿ⁻¹", "color": color, "position": "top_right"}},
            {"primitive": "highlight_flash", "params": {"color": "yellow", "count": 2}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "plot_second_function", "params": {"expression": "2*x", "color": "#FBBF24", "label": "f'(x) = 2x"}},
            {"primitive": "show_text", "params": {"text": "The derivative IS the slope!", "color": "white", "position": "below", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── CHAIN RULE (~30s) ──
        3: base + [
            {"primitive": "show_text", "params": {"text": "What if f is inside another function?", "color": "white", "position": "below_title", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "y = sin(x²)", "color": "white", "position": "center"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "transform_equation", "params": {"from_text": "outer: sin(u)    inner: u = x²", "to_text": "dy/dx = cos(u) · 2x", "color": color}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-3, 3], "y_range": [-2, 4], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "sin(x**2)", "color": color, "label": "sin(x²)"}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "animate_tangent", "params": {"x_values": [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2], "color": "yellow"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_formula", "params": {"text": "d/dx [f(g(x))] = f'(g(x))·g'(x)", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── INTEGRATION BASICS (~30s) ──
        4: base + [
            {"primitive": "show_text", "params": {"text": "How do we find the area under a curve?", "color": "white", "position": "below_title", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-1, 4], "y_range": [-1, 5], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "0.5*x**2", "color": color, "label": "f(x) = ½x²"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_brace", "params": {"x_start": 0.5, "x_end": 3, "label": "Δx", "color": color, "direction": "down"}},
            {"primitive": "show_riemann_sum", "params": {"x_start": 0.5, "x_end": 3, "n_values": [3, 6, 12, 24, 48], "color": color}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "shade_area", "params": {"x_start": 0.5, "x_end": 3, "color": color, "opacity": 0.3}},
            {"primitive": "show_text", "params": {"text": "Infinite rectangles = exact area!", "color": "white", "position": "below", "font_size": 24}},
            {"primitive": "highlight_flash", "params": {"color": "yellow", "count": 2}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "∫ f(x)dx = F(x) + C", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── U-SUBSTITUTION (~30s) ──
        5: base + [
            {"primitive": "show_text", "params": {"text": "The reverse chain rule", "color": "white", "position": "below_title", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "∫ 2x · cos(x²) dx", "color": "white", "position": "center"}},
            {"primitive": "wait", "params": {"duration": 1.2}},
            {"primitive": "transform_equation", "params": {"from_text": "Let u = x²,  du = 2x dx", "to_text": "∫ cos(u) du", "color": color}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "transform_equation", "params": {"from_text": "∫ cos(u) du = sin(u) + C", "to_text": "= sin(x²) + C", "color": color}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "draw_axes", "params": {"x_range": [-3, 3], "y_range": [-2, 2], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "sin(x**2)", "color": color, "label": "F(x) = sin(x²)"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_formula", "params": {"text": "∫ f(g(x))·g'(x)dx = ∫ f(u)du", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── L'HOPITAL (~30s) ──
        6: base + [
            {"primitive": "show_formula", "params": {"text": "lim x→0  sin(x)/x = ?", "color": "white", "position": "center"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
            {"primitive": "draw_axes", "params": {"x_range": [-4, 4], "y_range": [-1, 2], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "sin(x)", "color": color, "label": "sin(x)"}},
            {"primitive": "plot_second_function", "params": {"expression": "x", "color": "#FBBF24", "label": "x"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_dot", "params": {"x": 0, "y": 0, "color": "red", "label": "0/0 !"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_text", "params": {"text": "Indeterminate! Try derivatives...", "color": "white", "position": "below", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "transform_equation", "params": {"from_text": "lim sin(x)/x → lim cos(x)/1", "to_text": "= cos(0)/1 = 1", "color": color}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "lim f/g = lim f'/g'", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── IMPLICIT DIFF (~30s) ──
        7: base + [
            {"primitive": "show_text", "params": {"text": "What if y isn't solved explicitly?", "color": "white", "position": "below_title", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "x² + y² = 25", "color": "white", "position": "center"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-6, 6], "y_range": [-6, 6], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "(25 - x**2)**0.5 if abs(x) < 5 else 0", "color": color, "label": "circle"}},
            {"primitive": "plot_second_function", "params": {"expression": "-(25 - x**2)**0.5 if abs(x) < 5 else 0", "color": color, "label": ""}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "animate_tangent", "params": {"x_values": [-4, -3, -1, 0, 1, 3, 4], "color": "yellow"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "transform_equation", "params": {"from_text": "2x + 2y·(dy/dx) = 0", "to_text": "dy/dx = −x/y", "color": color}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── RELATED RATES (~30s) ──
        8: base + [
            {"primitive": "show_text", "params": {"text": "If one thing changes, what else changes?", "color": "white", "position": "below_title", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_shape", "params": {"shape": "circle", "color": color, "position": "center"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_formula", "params": {"text": "A = πr²", "color": "white", "position": "center"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_text", "params": {"text": "r grows → A grows FASTER", "color": color, "position": "below", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "transform_equation", "params": {"from_text": "Differentiate both sides with respect to t", "to_text": "dA/dt = 2πr · dr/dt", "color": color}},
            {"primitive": "wait", "params": {"duration": 1.2}},
            {"primitive": "show_formula", "params": {"text": "dA/dt = dA/dr · dr/dt", "color": color, "position": "top_right"}},
            {"primitive": "show_text", "params": {"text": "The chain rule connects the rates!", "color": "white", "position": "below", "font_size": 22}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── FTC (~30s) ──
        9: base + [
            {"primitive": "show_text", "params": {"text": "The most important theorem in calculus", "color": "white", "position": "below_title", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.2}},
            {"primitive": "draw_axes", "params": {"x_range": [-1, 5], "y_range": [-1, 4], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "0.3*x**2", "color": color, "label": "f(x)"}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "show_dot", "params": {"x": 1, "y": 0, "color": "yellow", "label": "a"}},
            {"primitive": "show_dot", "params": {"x": 3.5, "y": 0, "color": "yellow", "label": "b"}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "shade_area", "params": {"x_start": 1, "x_end": 3.5, "color": color, "opacity": 0.3}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_text", "params": {"text": "Area = antiderivative at b minus at a", "color": "white", "position": "below", "font_size": 22}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "∫ₐᵇ f(x)dx = F(b) − F(a)", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_text", "params": {"text": "Derivatives ↔ Integrals are inverses!", "color": color, "position": "below", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── INTEGRATION BY PARTS (~30s) ──
        10: base + [
            {"primitive": "show_text", "params": {"text": "The product rule... in reverse", "color": "white", "position": "below_title", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "∫ x · eˣ dx = ?", "color": "white", "position": "center"}},
            {"primitive": "wait", "params": {"duration": 1.2}},
            {"primitive": "show_text", "params": {"text": "Pick:  u = x     dv = eˣ dx", "color": color, "position": "below_title", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "transform_equation", "params": {"from_text": "du = dx     v = eˣ", "to_text": "= x·eˣ − ∫ eˣ dx = x·eˣ − eˣ + C", "color": color}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-2, 3], "y_range": [-2, 8], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "x*exp(x)", "color": color, "label": "x·eˣ"}},
            {"primitive": "shade_area", "params": {"x_start": 0, "x_end": 2, "color": color, "opacity": 0.3}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_formula", "params": {"text": "∫ u dv = uv − ∫ v du", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── OPTIMIZATION (~30s) ──
        11: base + [
            {"primitive": "show_text", "params": {"text": "Finding the peak — where is the maximum?", "color": "white", "position": "below_title", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-2, 4], "y_range": [-3, 5], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "-(x-1)**2 + 4", "color": color, "label": "f(x)"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "animate_tangent", "params": {"x_values": [-1, -0.5, 0, 0.5, 0.8, 1, 1.2, 1.5, 2, 2.5, 3], "color": "yellow"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_text", "params": {"text": "Slope = 0 at the top!", "color": "white", "position": "below", "font_size": 24}},
            {"primitive": "show_dot", "params": {"x": 1, "y": 4, "color": "yellow", "label": "maximum"}},
            {"primitive": "show_horizontal_line", "params": {"y": 4, "color": "#FFFFFF"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "f'(x) = 0 → critical points", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── MVT (~30s) ──
        12: base + [
            {"primitive": "show_text", "params": {"text": "Somewhere the slope matches the average", "color": "white", "position": "below_title", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-1, 5], "y_range": [-1, 5], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "0.2*x**3 - 0.5*x**2 + 2", "color": color, "label": "f(x)"}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "show_dot", "params": {"x": 0.5, "y": 0, "color": color, "label": "a"}},
            {"primitive": "show_dot", "params": {"x": 4, "y": 0, "color": color, "label": "b"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_secant_to_tangent", "params": {"x_point": 2.2, "dx_values": [3.5, 2.5, 1.5, 0.5, 0.1, 0.01], "color": "yellow"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_text", "params": {"text": "There exists c where tangent ∥ secant", "color": "white", "position": "below", "font_size": 22}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "f'(c) = [f(b)−f(a)] / (b−a)", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── PARTIAL FRACTIONS (~30s) ──
        13: base + [
            {"primitive": "show_text", "params": {"text": "Break it apart to integrate it", "color": "white", "position": "below_title", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "∫ 1/[(x−1)(x+2)] dx", "color": "white", "position": "center"}},
            {"primitive": "wait", "params": {"duration": 1.2}},
            {"primitive": "transform_equation", "params": {"from_text": "1/[(x−1)(x+2)]", "to_text": "A/(x−1) + B/(x+2)", "color": color}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-4, 4], "y_range": [-3, 3], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "1/((x-1.01)*(x+2.01))", "color": color, "label": "f(x)"}},
            {"primitive": "show_vertical_line", "params": {"x": 1, "color": "#EF4444"}},
            {"primitive": "show_vertical_line", "params": {"x": -2, "color": "#EF4444"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_text", "params": {"text": "A = 1/3, B = −1/3", "color": color, "position": "below", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "= (1/3)ln|x−1| − (1/3)ln|x+2| + C", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── TRIG SUB (~30s) ──
        14: base + [
            {"primitive": "show_text", "params": {"text": "Use trig to kill the square root", "color": "white", "position": "below_title", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "∫ √(a² − x²) dx", "color": "white", "position": "center"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_shape", "params": {"shape": "triangle", "color": color, "position": "center"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_text", "params": {"text": "Let x = a sinθ", "color": color, "position": "below_title", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "transform_equation", "params": {"from_text": "√(a²−a²sin²θ) = a cosθ", "to_text": "∫ a² cos²θ dθ", "color": color}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_text", "params": {"text": "The square root disappears!", "color": "white", "position": "below", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_formula", "params": {"text": "x = a sinθ, x = a tanθ, x = a secθ", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── SERIES (~30s) ──
        15: base + [
            {"primitive": "show_text", "params": {"text": "Can you add up INFINITELY many numbers?", "color": "white", "position": "below_title", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.2}},
            {"primitive": "show_formula", "params": {"text": "1 + ½ + ¼ + ⅛ + ...", "color": "white", "position": "center"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [0, 10], "y_range": [0, 3], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "2*(1 - 0.5**x)", "color": color, "label": "partial sums"}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "show_horizontal_line", "params": {"y": 2, "color": "#FFFFFF"}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "animate_parameter", "params": {"label": "S =", "values": [1, 1.5, 1.75, 1.875, 1.9375, 1.96875, 1.984], "color": color}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_text", "params": {"text": "It converges to 2!", "color": color, "position": "below", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "Σ aₙ converges if partial sums approach L", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── NEWTON'S METHOD (~30s) ──
        16: base + [
            {"primitive": "show_text", "params": {"text": "Guess, improve, repeat — find the root", "color": "white", "position": "below_title", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-1, 4], "y_range": [-4, 8], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "x**2 - 3", "color": color, "label": "f(x) = x²−3"}},
            {"primitive": "show_horizontal_line", "params": {"y": 0, "color": "#FFFFFF"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_text", "params": {"text": "Where does f(x) = 0?", "color": "white", "position": "below", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_iteration", "params": {"points": [[3, 6], [2, 1], [1.75, 0.0625]], "color": "yellow", "labels": ["x₀=3", "x₁=2", "x₂=1.75"]}},
            {"primitive": "draw_arrow", "params": {"start": [1.75, 0.0625], "end": [1.732, 0], "label": "converging!", "color": "#10B981"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_dot", "params": {"x": 1.732, "y": 0, "color": "yellow", "label": "→ √3 ≈ 1.732"}},
            {"primitive": "highlight_flash", "params": {"color": "yellow", "count": 2}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "xₙ₊₁ = xₙ − f(xₙ)/f'(xₙ)", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── PARAMETRIC (~30s) ──
        17: base + [
            {"primitive": "show_text", "params": {"text": "Describe a curve with TWO functions of t", "color": "white", "position": "below_title", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "x(t) = cos(t),  y(t) = sin(t)", "color": "white", "position": "center"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-3, 3], "y_range": [-3, 3], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "sin(x)*2", "color": color, "label": "parametric path"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "animate_tangent", "params": {"x_values": [-2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5], "color": "yellow"}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_text", "params": {"text": "Slope = (dy/dt) ÷ (dx/dt)", "color": "white", "position": "below", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_formula", "params": {"text": "dy/dx = (dy/dt)/(dx/dt)", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── AREA BETWEEN CURVES (~30s) ──
        18: base + [
            {"primitive": "show_text", "params": {"text": "What's the area BETWEEN two curves?", "color": "white", "position": "below_title", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-1, 5], "y_range": [-1, 5], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "-0.5*x**2 + 3*x", "color": color, "label": "f(x)"}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "plot_second_function", "params": {"expression": "x", "color": "#FBBF24", "label": "g(x)"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_text", "params": {"text": "Subtract: top − bottom", "color": "white", "position": "below", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "shade_between", "params": {"x_start": 0, "x_end": 4, "color": color, "opacity": 0.3}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "A = ∫ₐᵇ [f(x) − g(x)] dx", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── IMPROPER INTEGRALS (~30s) ──
        19: base + [
            {"primitive": "show_text", "params": {"text": "Can you integrate to INFINITY?", "color": "white", "position": "below_title", "font_size": 26}},
            {"primitive": "wait", "params": {"duration": 1.2}},
            {"primitive": "draw_axes", "params": {"x_range": [0, 8], "y_range": [-0.5, 3], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "1/x**2 if x > 0.3 else 10", "color": color, "label": "f(x) = 1/x²"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "shade_area", "params": {"x_start": 1, "x_end": 3, "color": color, "opacity": 0.2}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "shade_area", "params": {"x_start": 1, "x_end": 5, "color": color, "opacity": 0.2}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "shade_area", "params": {"x_start": 1, "x_end": 7, "color": color, "opacity": 0.3}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_text", "params": {"text": "The area is FINITE — it converges!", "color": "white", "position": "below", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_formula", "params": {"text": "∫₁∞ 1/x² dx = 1", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
        # ── TAYLOR SERIES (~30s) ──
        20: base + [
            {"primitive": "show_text", "params": {"text": "Any function as an infinite polynomial", "color": "white", "position": "below_title", "font_size": 24}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "draw_axes", "params": {"x_range": [-4, 4], "y_range": [-2, 6], "position": "bottom"}},
            {"primitive": "plot_function", "params": {"expression": "exp(x)", "color": "white", "label": "eˣ (actual)"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "plot_second_function", "params": {"expression": "1 + x", "color": "#EF4444", "label": "1 term"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "plot_second_function", "params": {"expression": "1 + x + 0.5*x**2", "color": "#F59E0B", "label": "2 terms"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "plot_second_function", "params": {"expression": "1 + x + 0.5*x**2 + x**3/6", "color": "#10B981", "label": "3 terms"}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "plot_second_function", "params": {"expression": "1 + x + 0.5*x**2 + x**3/6 + x**4/24", "color": "#3B82F6", "label": "4 terms"}},
            {"primitive": "wait", "params": {"duration": 0.5}},
            {"primitive": "show_table", "params": {"headers": ["terms", "f(1) approx"], "rows": [["1", "2.00"], ["2", "2.50"], ["3", "2.67"], ["4", "2.71"]], "color": color}},
            {"primitive": "wait", "params": {"duration": 1.0}},
            {"primitive": "show_text", "params": {"text": "More terms → closer to eˣ!", "color": "white", "position": "below", "font_size": 24}},
            {"primitive": "highlight_flash", "params": {"color": "yellow", "count": 2}},
            {"primitive": "wait", "params": {"duration": 0.8}},
            {"primitive": "show_formula", "params": {"text": "f(x) = Σ fⁿ(a)/n! · (x−a)ⁿ", "color": color, "position": "top_right"}},
            {"primitive": "wait", "params": {"duration": 1.5}},
        ],
    }

    return plans.get(tid, base + [
        {"primitive": "draw_axes", "params": {"x_range": [-3, 3], "y_range": [-2, 4], "position": "bottom"}},
        {"primitive": "plot_function", "params": {"expression": "x**2", "color": color, "label": "f(x)"}},
        {"primitive": "animate_tangent", "params": {"x_values": [-2, -1, 0, 1, 2], "color": "yellow"}},
    ])


# ═══════════════════════════════════════════════════════════════════
#  MANIM CODE GENERATOR — converts plan → Python Manim code
# ═══════════════════════════════════════════════════════════════════

def plan_to_manim_code(plan, topic):
    """Convert a primitive-based plan into a complete Manim Python script."""
    color = topic["color"]
    lines = []

    # Track state
    has_axes = False
    has_function = False
    func_expr = "x**2"
    func_count = 0

    # ── Scene config ──
    lines.append('''
        # ── Zone-based layout tracking ──
        # Each zone holds at most ONE active element. Placing a new element
        # in a zone automatically fades out the previous occupant.
        _zone = {}          # zone_name → mobject
        _extras = []        # non-zoned elements (dots, arrows, etc.)

        def _set_zone(name, mob):
            """Place mob in a zone, fading out previous occupant."""
            if name in _zone and _zone[name] is not None:
                self.play(FadeOut(_zone[name]), run_time=0.2)
            _zone[name] = mob

        def _clear_zone(name):
            if name in _zone and _zone[name] is not None:
                self.play(FadeOut(_zone[name]), run_time=0.2)
                _zone[name] = None

        def _clear_zones(*names):
            to_fade = [_zone[n] for n in names if n in _zone and _zone[n] is not None]
            if to_fade:
                self.play(*[FadeOut(m) for m in to_fade], run_time=0.25)
            for n in names:
                _zone[n] = None
        ''')

    for step in plan:
        p = step["primitive"]
        params = step.get("params", {})

        if p == "show_title":
            text = params.get("text", topic["title"]).replace('"', '\\"')
            c = params.get("color", color)
            lines.append(f'''
        title = Text("{text}", font_size=36, color=WHITE, font="sans-serif")
        title.to_edge(UP, buff=0.5)
        underline = Line(
            title.get_left() + DOWN*0.2, title.get_right() + DOWN*0.2,
            color="{c}", stroke_width=2, stroke_opacity=0.6
        )
        title_group = VGroup(title, underline)
        self.play(FadeIn(title, shift=DOWN*0.15), run_time=0.8, rate_func=smooth)
        self.play(Create(underline), run_time=0.3, rate_func=smooth)
        _zone["title"] = title_group
        self.wait(0.2)''')

        elif p == "show_formula":
            text = params.get("text", "f(x)").replace('"', '\\"')
            c = params.get("color", color)
            pos = params.get("position", "center")
            zone_name = {"center": "center", "below_title": "subtitle", "top_right": "formula_tr"}.get(pos, "center")
            pos_code = {
                "center": ".move_to(ORIGIN)",
                "below_title": ".next_to(title, DOWN, buff=0.4)" if "title" in "\n".join(lines) else ".move_to(UP*2)",
                "top_right": ".to_corner(UR, buff=0.3).scale(0.75)",
            }.get(pos, ".move_to(ORIGIN)")
            lines.append(f'''
        _clear_zone("{zone_name}")
        formula_{func_count} = Text("{text}", font_size=26, font="monospace", color="{c}")
        formula_{func_count}{pos_code}
        self.play(Write(formula_{func_count}), run_time=1.0, rate_func=smooth)
        _set_zone("{zone_name}", formula_{func_count})
        self.wait(0.3)''')
            func_count += 1

        elif p == "show_text":
            text = params.get("text", "").replace('"', '\\"')
            c = params.get("color", "white")
            c = "WHITE" if c == "white" else f'"{c}"'
            fs = params.get("font_size", 28)
            pos = params.get("position", "center")
            zone_name = {"center": "center", "below_title": "subtitle", "below": "caption", "top": "subtitle"}.get(pos, "center")
            pos_code = ".move_to(ORIGIN)"
            shift_dir = "UP*0.15"
            if pos == "below_title" and "title" in "\n".join(lines):
                pos_code = ".next_to(title, DOWN, buff=0.35)"
                shift_dir = "DOWN*0.1"
            elif pos == "below":
                pos_code = ".to_edge(DOWN, buff=0.4)"
                shift_dir = "UP*0.1"
            elif pos == "top":
                pos_code = ".to_edge(UP, buff=1.0)"
                shift_dir = "DOWN*0.1"
            lines.append(f'''
        _clear_zone("{zone_name}")
        text_{func_count} = Text("{text}", font_size={min(fs, 26)}, color={c})
        text_{func_count}{pos_code}
        self.play(FadeIn(text_{func_count}, shift={shift_dir}), run_time=0.6, rate_func=smooth)
        _set_zone("{zone_name}", text_{func_count})
        self.wait(0.3)''')
            func_count += 1

        elif p == "draw_axes":
            has_axes = True
            xr = params.get("x_range", [-3, 3])
            yr = params.get("y_range", [-2, 4])
            pos = params.get("position", "bottom")
            buff = "0.5" if pos == "bottom" else "0.3"
            edge = "DOWN" if pos == "bottom" else "ORIGIN"
            lines.append(f'''
        # Clear center zone before drawing graph area
        _clear_zones("center", "subtitle")
        axes = Axes(
            x_range=[{xr[0]}, {xr[1]}, 1], y_range=[{yr[0]}, {yr[1]}, 1],
            x_length=5.5, y_length=3,
            axis_config={{"color": WHITE, "stroke_width": 1.5, "stroke_opacity": 0.3, "include_ticks": True, "tick_size": 0.05}},
            tips=False,
        )
        axes.to_edge({edge}, buff={buff})
        self.play(Create(axes), run_time=0.7, rate_func=smooth)''')

        elif p == "plot_function":
            has_function = True
            expr = params.get("expression", "x**2")
            func_expr = expr
            c = params.get("color", color)
            label = params.get("label", "f(x)").replace('"', '\\"')
            lines.append(f'''
        def f(x):
            try:
                from math import sin, cos, exp, log, sqrt, pi
                val = {expr}
                return max(-10, min(10, val))
            except:
                return 0
        curve = axes.plot(f, color="{c}", stroke_width=2.5, use_smoothing=True)
        self.play(Create(curve, rate_func=smooth), run_time=1.5)
        self.wait(0.15)''')

        elif p == "plot_second_function":
            expr2 = params.get("expression", "x")
            c2 = params.get("color", "#FBBF24")
            label2 = params.get("label", "g(x)").replace('"', '\\"')
            lines.append(f'''
        def g_{func_count}(x):
            try:
                from math import sin, cos, exp, log, sqrt, pi
                val = {expr2}
                return max(-10, min(10, val))
            except:
                return 0
        curve2_{func_count} = axes.plot(g_{func_count}, color="{c2}", stroke_width=2, stroke_opacity=0.85, use_smoothing=True)
        self.play(Create(curve2_{func_count}, rate_func=smooth), run_time=1.0)
        self.wait(0.15)''')
            func_count += 1

        elif p == "animate_tangent":
            x_vals = params.get("x_values", [-1, 0, 1, 2])
            tc = params.get("color", "yellow")
            tc_manim = "YELLOW" if tc == "yellow" else f'"{tc}"'
            lines.append(f'''
        def f_prime(x):
            h = 0.001
            return (f(x+h) - f(x-h)) / (2*h)
        def get_tan(xv):
            y = f(xv); s = f_prime(xv)
            span = 1.2
            x1, x2 = xv - span, xv + span
            return Line(
                axes.c2p(x1, y + s*(x1-xv)),
                axes.c2p(x2, y + s*(x2-xv)),
                color={tc_manim}, stroke_width=2, stroke_opacity=0.9
            )
        xv = {x_vals[0]}
        dot_t = Dot(axes.c2p(xv, f(xv)), color={tc_manim}, radius=0.07)
        dot_t.set_z_index(5)
        tan_t = get_tan(xv)
        self.play(GrowFromCenter(dot_t), Create(tan_t), run_time=0.6, rate_func=smooth)
        for xv in {x_vals[1:]}:
            nd = Dot(axes.c2p(xv, f(xv)), color={tc_manim}, radius=0.07)
            nd.set_z_index(5)
            nt = get_tan(xv)
            self.play(
                Transform(dot_t, nd), Transform(tan_t, nt),
                run_time=0.5, rate_func=smooth
            )
            self.wait(0.1)''')

        elif p == "shade_area":
            xs = params.get("x_start", 0)
            xe = params.get("x_end", 2)
            c = params.get("color", color)
            op = params.get("opacity", 0.3)
            lines.append(f'''
        area = axes.get_area(curve, x_range=[{xs}, {xe}], color="{c}", opacity={op})
        area.set_z_index(-1)
        self.play(FadeIn(area, rate_func=smooth), run_time=1.2)
        self.wait(0.3)''')

        elif p == "shade_between":
            xs = params.get("x_start", 0)
            xe = params.get("x_end", 2)
            c = params.get("color", color)
            op = params.get("opacity", 0.3)
            lines.append(f'''
        try:
            between_area = axes.get_area(curve, x_range=[{xs}, {xe}], color="{c}", opacity={op})
            between_area.set_z_index(-1)
            self.play(FadeIn(between_area, rate_func=smooth), run_time=1.2)
        except:
            pass
        self.wait(0.3)''')

        elif p == "show_vertical_line":
            x = params.get("x", 0)
            c = params.get("color", "#FFFFFF")
            lines.append(f'''
        vl = DashedLine(axes.c2p({x}, axes.y_range[0]), axes.c2p({x}, axes.y_range[1]), color="{c}", stroke_width=1.2, stroke_opacity=0.5, dash_length=0.08)
        self.play(Create(vl, rate_func=smooth), run_time=0.5)''')

        elif p == "show_horizontal_line":
            y = params.get("y", 0)
            c = params.get("color", "#FFFFFF")
            lines.append(f'''
        hl = DashedLine(axes.c2p(axes.x_range[0], {y}), axes.c2p(axes.x_range[1], {y}), color="{c}", stroke_width=1.2, stroke_opacity=0.5, dash_length=0.08)
        self.play(Create(hl, rate_func=smooth), run_time=0.5)''')

        elif p == "show_dot":
            x = params.get("x", 0)
            y = params.get("y", 0)
            c = params.get("color", "yellow")
            c_manim = "YELLOW" if c == "yellow" else ("RED" if c == "red" else f'"{c}"')
            label = params.get("label", "")
            label_code = ""
            if label:
                label = label.replace('"', '\\"')
                label_code = f'''
        _clear_zone("dot_label")
        dot_label_{func_count} = Text("{label}", font_size=14, color={c_manim}).next_to(dot_{func_count}, UR, buff=0.1)
        self.play(FadeIn(dot_label_{func_count}, shift=UP*0.08), run_time=0.3, rate_func=smooth)
        _zone["dot_label"] = dot_label_{func_count}'''
            lines.append(f'''
        dot_{func_count} = Dot(axes.c2p({x}, {y}), color={c_manim}, radius=0.06)
        dot_{func_count}.set_z_index(5)
        self.play(GrowFromCenter(dot_{func_count}), run_time=0.35, rate_func=smooth){label_code}''')
            func_count += 1

        elif p == "show_riemann_sum":
            xs = params.get("x_start", 0)
            xe = params.get("x_end", 3)
            ns = params.get("n_values", [4, 8, 16])
            c = params.get("color", color)
            lines.append(f'''
        prev_rects = None
        for n in {ns}:
            rects = axes.get_riemann_rectangles(
                curve, x_range=[{xs}, {xe}], dx=(({xe}-{xs})/n),
                color="{c}", fill_opacity=0.25, stroke_width=0.8
            )
            rects.set_z_index(-1)
            if prev_rects:
                self.play(Transform(prev_rects, rects, rate_func=smooth), run_time=0.7)
            else:
                self.play(FadeIn(rects, rate_func=smooth), run_time=0.8)
                prev_rects = rects
            self.wait(0.2)''')

        elif p == "animate_parameter":
            label = params.get("label", "x →").replace('"', '\\"')
            values = params.get("values", [3, 2, 1.5, 1.1])
            c = params.get("color", color)
            lines.append(f'''
        _clear_zone("param")
        param_text = Text("{label} {values[0]}", font_size=20, font="monospace", color="{c}").to_corner(DR, buff=0.3)
        self.play(FadeIn(param_text, shift=LEFT*0.15), run_time=0.3, rate_func=smooth)
        for v in {values[1:]}:
            new_text = Text(f"{label} {{v}}", font_size=20, font="monospace", color="{c}").to_corner(DR, buff=0.3)
            self.play(FadeOut(param_text, shift=UP*0.08), run_time=0.12)
            self.play(FadeIn(new_text, shift=UP*0.08), run_time=0.12)
            param_text = new_text
            self.wait(0.1)
        _zone["param"] = param_text''')

        elif p == "transform_equation":
            fr = params.get("from_text", "a = b").replace('"', '\\"')
            to = params.get("to_text", "c = d").replace('"', '\\"')
            c = params.get("color", color)
            lines.append(f'''
        _clear_zone("center")
        eq_from_{func_count} = Text("{fr}", font_size=22, font="monospace", color="{c}")
        eq_from_{func_count}.move_to(ORIGIN)
        self.play(FadeIn(eq_from_{func_count}, shift=UP*0.1), run_time=0.7, rate_func=smooth)
        _zone["center"] = eq_from_{func_count}
        self.wait(0.5)
        eq_to_{func_count} = Text("{to}", font_size=22, font="monospace", color="{c}")
        eq_to_{func_count}.move_to(ORIGIN)
        self.play(FadeOut(eq_from_{func_count}, shift=UP*0.15), run_time=0.3, rate_func=smooth)
        self.play(FadeIn(eq_to_{func_count}, shift=UP*0.15), run_time=0.5, rate_func=smooth)
        _zone["center"] = eq_to_{func_count}
        self.wait(0.3)''')
            func_count += 1

        elif p == "draw_shape":
            shape = params.get("shape", "circle")
            c = params.get("color", color)
            if shape == "circle":
                lines.append(f'''
        shape = Circle(radius=1.2, color="{c}", stroke_width=2.5).move_to(ORIGIN)
        self.play(Create(shape, rate_func=smooth), run_time=1.2)
        self.wait(0.2)''')
            elif shape == "triangle":
                lines.append(f'''
        shape = Triangle(color="{c}", stroke_width=2.5).scale(1.3).move_to(ORIGIN)
        self.play(Create(shape, rate_func=smooth), run_time=1.2)
        self.wait(0.2)''')
            elif shape == "rectangle":
                lines.append(f'''
        shape = Rectangle(width=2.5, height=1.8, color="{c}", stroke_width=2.5).move_to(ORIGIN)
        self.play(Create(shape, rate_func=smooth), run_time=1.2)
        self.wait(0.2)''')

        elif p == "show_iteration":
            points = params.get("points", [[2, 4], [1.5, 1]])
            c = params.get("color", "yellow")
            c_manim = "YELLOW" if c == "yellow" else f'"{c}"'
            labels = params.get("labels", [f"x{i}" for i in range(len(points))])
            for i, (pt, lbl) in enumerate(zip(points, labels)):
                lbl = lbl.replace('"', '\\"')
                lines.append(f'''
        iter_dot_{i} = Dot(axes.c2p({pt[0]}, {pt[1]}), color={c_manim}, radius=0.08)
        iter_dot_{i}.set_z_index(5)
        iter_lbl_{i} = Text("{lbl}", font_size=14, color={c_manim}).next_to(iter_dot_{i}, DOWN, buff=0.12)
        self.play(GrowFromCenter(iter_dot_{i}), FadeIn(iter_lbl_{i}, shift=DOWN*0.1), run_time=0.5, rate_func=smooth)''')
                if i < len(points) - 1:
                    npt = points[i + 1]
                    lines.append(f'''
        iter_arrow_{i} = Arrow(axes.c2p({pt[0]}, {pt[1]}), axes.c2p({npt[0]}, {npt[1]}), color={c_manim}, stroke_width=1.5, buff=0.12, max_tip_length_to_length_ratio=0.15)
        self.play(Create(iter_arrow_{i}, rate_func=smooth), run_time=0.5)''')

        elif p == "show_secant_to_tangent":
            xp = params.get("x_point", 1)
            dxs = params.get("dx_values", [2.0, 1.0, 0.5, 0.1])
            c = params.get("color", "yellow")
            c_manim = "YELLOW" if c == "yellow" else f'"{c}"'
            lines.append(f'''
        xp = {xp}
        sec_dot = Dot(axes.c2p(xp, f(xp)), color={c_manim}, radius=0.07)
        sec_dot.set_z_index(5)
        self.play(GrowFromCenter(sec_dot), run_time=0.3, rate_func=smooth)
        prev_sec = None
        for dx in {dxs}:
            p1 = axes.c2p(xp, f(xp))
            p2 = axes.c2p(xp+dx, f(xp+dx))
            sec = Line(p1, p2, color={c_manim}, stroke_width=2, stroke_opacity=0.85).scale(2.5)
            if prev_sec:
                self.play(Transform(prev_sec, sec, rate_func=smooth), run_time=0.6)
            else:
                self.play(Create(sec, rate_func=smooth), run_time=0.6)
                prev_sec = sec
            self.wait(0.15)''')

        elif p == "draw_number_line":
            pts = params.get("points", [0, 1, 2, 3])
            hl = params.get("highlight", None)
            c = params.get("color", color)
            lbls = params.get("labels", [str(x) for x in pts])
            lines.append(f'''
        nl = NumberLine(x_range=[{min(pts)-1}, {max(pts)+1}, 1], length=8, color=WHITE,
                        include_numbers=False, stroke_width=2).shift(DOWN*0.5)
        self.play(Create(nl), run_time=0.8)
        for pt, lbl in zip({pts}, {lbls}):
            d = Dot(nl.n2p(pt), color="{c}", radius=0.08)
            t = Text(str(lbl), font_size=16, color=WHITE).next_to(d, DOWN, buff=0.15)
            self.play(Create(d), FadeIn(t), run_time=0.3)''')
            if hl is not None:
                lines.append(f'''
        hl_dot = Dot(nl.n2p({hl}), color=YELLOW, radius=0.15)
        self.play(Create(hl_dot), run_time=0.5)
        self.play(hl_dot.animate.scale(1.5), run_time=0.3)
        self.play(hl_dot.animate.scale(1/1.5), run_time=0.3)''')

        elif p == "animate_trace":
            xs = params.get("x_start", -2)
            xe = params.get("x_end", 2)
            tc = params.get("color", "yellow")
            tc_manim = "YELLOW" if tc == "yellow" else f'"{tc}"'
            dur = params.get("duration", 3.0)
            lines.append(f'''
        trace_dot = Dot(axes.c2p({xs}, f({xs})), color={tc_manim}, radius=0.1)
        trace_path = TracedPath(trace_dot.get_center, stroke_color={tc_manim}, stroke_width=3, stroke_opacity=0.7)
        self.add(trace_path)
        self.play(Create(trace_dot), run_time=0.3)
        self.play(MoveAlongPath(trace_dot, axes.plot(f, x_range=[{xs}, {xe}]), rate_func=smooth), run_time={dur})
        self.wait(0.3)''')

        elif p == "highlight_flash":
            hc = params.get("color", "yellow")
            hc_manim = "YELLOW" if hc == "yellow" else f'"{hc}"'
            cnt = params.get("count", 2)
            lines.append(f'''
        if self.mobjects:
            _target = self.mobjects[-1]
            _orig_color = _target.get_color() if hasattr(_target, 'get_color') else WHITE
            for _ in range({cnt}):
                self.play(_target.animate.scale(1.08), run_time=0.15, rate_func=smooth)
                self.play(_target.animate.scale(1/1.08), run_time=0.15, rate_func=smooth)''')

        elif p == "show_brace":
            bxs = params.get("x_start", 1)
            bxe = params.get("x_end", 3)
            blbl = params.get("label", "Δx").replace('"', '\\"')
            bc = params.get("color", color)
            bdir = params.get("direction", "down")
            bdir_vec = "DOWN" if bdir == "down" else "UP"
            lines.append(f'''
        brace_line_{func_count} = Line(axes.c2p({bxs}, 0), axes.c2p({bxe}, 0))
        brace_{func_count} = Brace(brace_line_{func_count}, {bdir_vec}, color="{bc}")
        brace_lbl_{func_count} = Text("{blbl}", font_size=20, color="{bc}")
        brace_lbl_{func_count}.next_to(brace_{func_count}, {bdir_vec}, buff=0.1)
        self.play(Create(brace_{func_count}), FadeIn(brace_lbl_{func_count}), run_time=0.8)
        self.wait(0.3)''')
            func_count += 1

        elif p == "morph_function":
            new_expr = params.get("expression", "x**2")
            mc = params.get("color", color)
            mlabel = params.get("label", "f(x)").replace('"', '\\"')
            lines.append(f'''
        def f_new_{func_count}(x):
            try:
                from math import sin, cos, exp, log, sqrt, pi
                val = {new_expr}
                return max(-10, min(10, val))
            except:
                return 0
        new_curve_{func_count} = axes.plot(f_new_{func_count}, color="{mc}", stroke_width=3)
        new_label_{func_count} = Text("{mlabel}", font_size=18, color="{mc}").next_to(new_curve_{func_count}, UR, buff=0.1)
        self.play(Transform(curve, new_curve_{func_count}), FadeIn(new_label_{func_count}), run_time=1.5)
        f = f_new_{func_count}
        self.wait(0.3)''')
            func_count += 1

        elif p == "show_table":
            headers = params.get("headers", ["x", "f(x)"])
            rows = params.get("rows", [[1, 1], [2, 4]])
            tc = params.get("color", color)
            # Build table text
            header_str = "  |  ".join(str(h) for h in headers)
            row_strs = []
            for row in rows:
                row_strs.append("  |  ".join(str(v) for v in row))
            all_rows = [header_str, "─" * len(header_str)] + row_strs
            table_text = "\\n".join(all_rows)
            lines.append(f'''
        table_{func_count} = Text("{table_text}", font_size=20, font="monospace", color="{tc}").scale(0.8)
        self.play(FadeIn(table_{func_count}), run_time=1.0)
        self.wait(0.5)''')
            func_count += 1

        elif p == "draw_arrow":
            astart = params.get("start", [0, 0])
            aend = params.get("end", [1, 1])
            albl = params.get("label", "").replace('"', '\\"')
            ac = params.get("color", color)
            lines.append(f'''
        arrow_{func_count} = Arrow(
            axes.c2p({astart[0]}, {astart[1]}), axes.c2p({aend[0]}, {aend[1]}),
            color="{ac}", stroke_width=2.5, buff=0.1)
        self.play(Create(arrow_{func_count}), run_time=0.6)''')
            if albl:
                lines.append(f'''
        arrow_lbl_{func_count} = Text("{albl}", font_size=18, color="{ac}").next_to(arrow_{func_count}, UP, buff=0.1)
        self.play(FadeIn(arrow_lbl_{func_count}), run_time=0.3)''')
            func_count += 1

        elif p == "fade_out_last":
            cnt = params.get("count", 3)
            lines.append(f'''
        _to_remove = self.mobjects[-{cnt}:] if len(self.mobjects) >= {cnt} else self.mobjects[:]
        if _to_remove:
            self.play(*[FadeOut(m) for m in _to_remove], run_time=0.4, rate_func=smooth)''')

        elif p == "fade_out_all":
            lines.append('''
        self.play(*[FadeOut(m, shift=DOWN*0.1) for m in self.mobjects], run_time=0.5, rate_func=smooth)
        _zone.clear()''')

        elif p == "wait":
            dur = params.get("duration", 1.0)
            lines.append(f'''
        self.wait({dur})''')

    # Add final wait
    lines.append('''
        self.wait(2.0)''')

    # Assemble full script
    body = "\n".join(lines)
    script = f'''from manim import *

# ── Vertical (9:16) reel format ──
config.frame_rate = 30
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16

class ReelScene(Scene):
    def construct(self):
        self.camera.background_color = "#0a0a0a"
{body}
'''
    return script


# ═══════════════════════════════════════════════════════════════════
#  RENDERING + PIPELINE (unchanged from before)
# ═══════════════════════════════════════════════════════════════════

def render_animation(plan, topic, output_path, quality="low"):
    """Convert plan to Manim code and render."""
    script_content = plan_to_manim_code(plan, topic)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script_content)
        script_path = f.name

    try:
        quality_flag = {"low": "-ql", "medium": "-qm", "high": "-qh"}.get(quality, "-ql")
        cmd = [
            "manim", "render", quality_flag, "--format", "mp4",
            "--media_dir", str(PROJECT_ROOT / "media"),
            script_path, "ReelScene",
        ]

        print(f"    Rendering Manim animation ({quality})...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        if result.returncode != 0:
            print(f"    Manim error: {result.stderr[-500:]}", file=sys.stderr)
            # Save the failing script for debugging
            debug_path = PLANS_DIR / f"debug-{topic['id']}.py"
            os.makedirs(PLANS_DIR, exist_ok=True)
            with open(debug_path, "w") as dbg:
                dbg.write(script_content)
            print(f"    Debug script saved: {debug_path}")
            return False

        # Find output
        media_dir = PROJECT_ROOT / "media" / "videos"
        for mp4 in media_dir.rglob("ReelScene.mp4"):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            os.rename(str(mp4), str(output_path))
            print(f"    Animation saved: {output_path}")
            return True

        print("    Could not find rendered MP4", file=sys.stderr)
        return False
    finally:
        os.unlink(script_path)


def generate_narration(topic, api_key):
    """Use Gemini to write narration script."""
    from google import genai
    client = genai.Client(api_key=api_key)

    prompt = f"""Write a short narration (60-90 seconds spoken) about {topic['description']}.

For a calculus video aimed at university students (Calc 1ZB3, McMaster).

Rules:
- Hook that grabs attention in the first sentence
- Explain with intuition, not just formulas
- One clear example
- Memorable takeaway at the end
- Conversational, enthusiastic tone (like 3Blue1Brown)
- NO stage directions, just spoken words
- Under 200 words

Topic: {topic['title']}
Formula: {topic['formula']}"""

    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text.strip()


def generate_tts(text, output_path):
    from gtts import gTTS
    print(f"    Generating TTS audio...")
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(str(output_path))
    return True


def combine_video_audio(video_path, audio_path, output_path):
    print(f"    Combining video + audio...")
    a_dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
        capture_output=True, text=True).stdout.strip() or "0")
    v_dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True, text=True).stdout.strip() or "0")

    cmd = ["ffmpeg", "-y"]
    if v_dur < a_dur:
        cmd += ["-stream_loop", "-1"]
    cmd += ["-i", str(video_path), "-i", str(audio_path),
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "128k",
            "-shortest", "-pix_fmt", "yuv420p", str(output_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ffmpeg error: {result.stderr[-300:]}", file=sys.stderr)
        return False
    print(f"    Final video: {output_path}")
    return True


def extract_audio(video_path, audio_output_path):
    return subprocess.run(
        ["ffmpeg", "-y", "-i", str(video_path), "-vn", "-acodec", "libmp3lame", "-b:a", "128k", str(audio_output_path)],
        capture_output=True, text=True).returncode == 0


# ═══════════════════════════════════════════════════════════════════
#  MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════

def generate_reel(topic, api_key=None, preview_only=False, quality="low", force=False):
    reel_id = topic["id"]
    title = topic["title"]

    video_output = VIDEO_DIR / f"reel-{reel_id}.mp4"
    audio_output = AUDIO_DIR / f"reel-{reel_id}.mp3"
    temp_animation = VIDEO_DIR / f"_animation-{reel_id}.mp4"
    temp_tts = VIDEO_DIR / f"_tts-{reel_id}.mp3"
    plan_file = PLANS_DIR / f"plan-{reel_id}.json"

    if not force and video_output.exists() and audio_output.exists():
        print(f"  [{reel_id}/20] Skipping (already exists): {title}")
        return True

    print(f"\n  [{reel_id}/20] Generating: {title}")
    os.makedirs(VIDEO_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(PLANS_DIR, exist_ok=True)

    # Step 1: Get animation plan (Gemini or fallback)
    plan = None
    if api_key and not preview_only:
        try:
            print(f"    Asking Gemini to design animation...")
            plan = generate_animation_plan(topic, api_key)
            if plan:
                plan_file.write_text(json.dumps(plan, indent=2))
                print(f"    Gemini plan: {len(plan)} steps → {plan_file.name}")
        except Exception as e:
            print(f"    Gemini plan error: {e}")

    if not plan:
        plan = get_fallback_plan(topic)
        plan_file.write_text(json.dumps(plan, indent=2))
        print(f"    Using fallback plan: {len(plan)} steps")

    # Step 2: Render Manim animation from plan
    if not render_animation(plan, topic, temp_animation, quality):
        return False

    if preview_only:
        os.rename(str(temp_animation), str(video_output))
        print(f"  [{reel_id}/20] Preview done (no audio)")
        return True

    # Step 3: Generate narration
    if api_key:
        try:
            narration = generate_narration(topic, api_key)
            print(f"    Narration: {len(narration.split())} words")
        except Exception as e:
            print(f"    Narration error: {e}")
            narration = f"Welcome to {title}. {topic['description']}. Let's explore this step by step."
    else:
        narration = f"Welcome to {title}. {topic['description']}. Let's explore this concept step by step."

    transcript_dir = PUBLIC_DIR / "transcripts"
    os.makedirs(transcript_dir, exist_ok=True)
    (transcript_dir / f"reel-{reel_id}.txt").write_text(narration)

    # Step 4: TTS
    if not generate_tts(narration, temp_tts):
        return False

    # Step 5: Combine
    if not combine_video_audio(temp_animation, temp_tts, video_output):
        return False

    # Step 6: Extract audio for web player
    extract_audio(video_output, audio_output)

    # Cleanup
    for f in [temp_animation, temp_tts]:
        if os.path.exists(f):
            os.unlink(f)

    print(f"  [{reel_id}/20] Complete!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate CalculusReels videos (Gemini + Manim)")
    parser.add_argument("--id", type=int, help="Generate only this topic ID")
    parser.add_argument("--force", action="store_true", help="Regenerate even if exists")
    parser.add_argument("--preview", action="store_true", help="Animation only, no AI narration")
    parser.add_argument("--quality", choices=["low", "medium", "high"], default="low")
    args = parser.parse_args()

    api_key = load_api_key()
    if not api_key and not args.preview:
        print("Warning: No GEMINI_API_KEY — using fallback plans + placeholder narration.\n")

    topics = TOPICS
    if args.id:
        topics = [t for t in TOPICS if t["id"] == args.id]
        if not topics:
            print(f"No topic with id={args.id}")
            sys.exit(1)

    print(f"Generating {len(topics)} reel(s)...\n")
    ok, fail = 0, 0
    for topic in topics:
        if generate_reel(topic, api_key=api_key, preview_only=args.preview, quality=args.quality, force=args.force):
            ok += 1
        else:
            fail += 1

    print(f"\nDone: {ok} succeeded, {fail} failed")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
