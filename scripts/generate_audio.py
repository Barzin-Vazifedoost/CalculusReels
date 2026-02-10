"""
Generate audio overviews for each calculus topic using NotebookLM.

Prerequisites:
  pip install -r requirements.txt
  playwright install chromium
  notebooklm login          # one-time browser OAuth

Usage:
  python generate_audio.py              # generate all missing
  python generate_audio.py --force      # regenerate everything
  python generate_audio.py --id 3       # regenerate a single topic
"""

"""
Generate audio overviews for each calculus topic using Google Cloud Text-to-Speech.

Prerequisites:
  pip install -r requirements.txt
  # Set up Google Cloud authentication (one of these options):
  export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
  # OR use gcloud auth: gcloud auth application-default login

Usage:
  python generate_audio.py              # generate all missing
  python generate_audio.py --force      # regenerate everything  
  python generate_audio.py --id 3       # regenerate a single topic
"""

import os
import sys
import argparse
from google.cloud import texttospeech

# Educational content for each calculus topic
TOPICS = [
    (1, "Introduction to Limits", """
    Limits are the foundation of calculus. A limit describes the value that a function approaches as the input approaches some value. 
    For example, as x approaches 2, the function f(x) = x squared approaches 4. 
    Limits help us understand continuity and are essential for defining derivatives and integrals.
    We use limit notation: limit as x approaches a of f(x) equals L.
    """),
    
    (2, "Derivative Rules", """
    Derivatives measure the rate of change of a function. The power rule states that the derivative of x to the n equals n times x to the n minus 1.
    The product rule: the derivative of u times v equals u prime times v plus u times v prime.
    The quotient rule: the derivative of u over v equals u prime times v minus u times v prime, all divided by v squared.
    These rules are fundamental tools for finding derivatives of complex functions.
    """),
    
    (3, "Chain Rule Explained", """
    The chain rule is used to find the derivative of composite functions. If we have a function g inside another function f, 
    the derivative of f of g of x equals f prime of g of x times g prime of x.
    Think of it as peeling layers of an onion - we differentiate the outer function first, then multiply by the derivative of the inner function.
    This is essential for functions like sine of x squared or e to the power of 3x.
    """),
    
    (4, "Integration Basics", """
    Integration is the reverse process of differentiation. The integral of a function represents the area under its curve.
    The fundamental theorem of calculus connects derivatives and integrals: the integral from a to b of f prime of x dx equals f of b minus f of a.
    Basic integration rules include: the integral of x to the n equals x to the n plus 1 divided by n plus 1, plus a constant C.
    Always remember to add the constant of integration for indefinite integrals.
    """),
    
    (5, "U-Substitution Method", """
    U-substitution is a technique for solving complex integrals by making a substitution to simplify the integrand.
    We let u equal some part of the function, then find du in terms of dx.
    For example, to integrate x times e to the x squared, we let u equal x squared, so du equals 2x dx.
    This transforms difficult integrals into simpler ones that we can solve using basic integration rules.
    """),
    
    (6, "L'Hopital's Rule", """
    L'Hopital's rule helps us evaluate limits that give indeterminate forms like 0 over 0 or infinity over infinity.
    The rule states: if limit of f over g gives an indeterminate form, then this limit equals the limit of f prime over g prime, 
    provided this new limit exists.
    For example, limit as x approaches 0 of sine x over x equals limit of cosine x over 1, which equals 1.
    This is a powerful tool for evaluating challenging limits.
    """),
    
    (7, "Implicit Differentiation", """
    Implicit differentiation is used when we cannot easily solve for y in terms of x.
    Instead of having y equals some function of x, we have equations like x squared plus y squared equals 25.
    We differentiate both sides with respect to x, treating y as a function of x and using the chain rule.
    This gives us dy/dx in terms of both x and y, allowing us to find slopes of curves defined implicitly.
    """),
    
    (8, "Related Rates", """
    Related rates problems involve finding how fast one quantity changes based on how fast related quantities change.
    The key steps are: identify the relationship between variables, differentiate with respect to time,
    and substitute known values to solve for the unknown rate.
    For example, if a balloon is being inflated, we can relate the rate of change of volume to the rate of change of radius.
    These problems connect calculus to real-world applications.
    """),
    
    (9, "Optimization Problems", """
    Optimization uses calculus to find maximum and minimum values of functions.
    The process involves: setting up the objective function, finding its derivative, setting the derivative equal to zero,
    and checking critical points and endpoints.
    The second derivative test helps determine if critical points are maxima or minima.
    Applications include finding maximum profit, minimum cost, or optimal dimensions for containers.
    """),
    
    (10, "Integration by Parts", """
    Integration by parts is based on the product rule for derivatives. The formula is:
    integral of u dv equals u times v minus integral of v du.
    We choose u and dv strategically using the LIATE rule: Logarithmic, Inverse trigonometric, Algebraic, Trigonometric, Exponential.
    This method is essential for integrating products of different types of functions,
    like x times e to the x or x times logarithm of x.
    """),
    
    (11, "Trigonometric Integration", """
    Integrating trigonometric functions requires special techniques and identities.
    For powers of sine and cosine, we use substitution or half-angle formulas.
    The integral of tangent x equals negative natural log of cosine x.
    Trigonometric substitution helps with integrals involving square roots of quadratic expressions.
    These methods are crucial for solving many physics and engineering problems.
    """),
    
    (12, "Partial Fractions", """
    Partial fraction decomposition breaks complex rational functions into simpler fractions that are easier to integrate.
    For example, 1 over (x minus 1)(x plus 2) can be written as A over (x minus 1) plus B over (x plus 2).
    We solve for constants A and B, then integrate each simple fraction separately.
    This technique is essential for integrating rational functions with factorizable denominators.
    """),
    
    (13, "Area Between Curves", """
    To find the area between two curves f(x) and g(x) from x equals a to x equals b,
    we integrate the absolute value of their difference: integral from a to b of absolute value of f(x) minus g(x) dx.
    We need to identify which function is on top in each interval and split the integral at intersection points.
    This concept extends to finding areas in polar coordinates and volumes of solids of revolution.
    """),
    
    (14, "Volume by Cross Sections", """
    We can find volumes by integrating cross-sectional areas. If each cross-section perpendicular to the x-axis has area A(x),
    then the volume from x equals a to x equals b is the integral from a to b of A(x) dx.
    Common cross-sections include squares, semicircles, and equilateral triangles.
    This method, along with disk and washer methods, provides powerful tools for calculating volumes.
    """),
    
    (15, "Arc Length and Surface Area", """
    The arc length of a curve y equals f(x) from x equals a to x equals b is:
    integral from a to b of square root of 1 plus (dy/dx) squared dx.
    Surface area of revolution around the x-axis is: 2 pi times integral of y times square root of 1 plus (dy/dx) squared dx.
    These formulas come from approximating curves with small line segments and surfaces with small bands.
    """),
    
    (16, "Sequences and Series", """
    A sequence is an ordered list of numbers, while a series is the sum of a sequence's terms.
    Convergence tests help determine if infinite series sum to finite values.
    The ratio test, root test, and comparison tests are fundamental tools.
    Geometric series with ratio r converge to a over (1 minus r) when absolute value of r is less than 1.
    Series are essential for understanding functions as infinite polynomials.
    """),
    
    (17, "Taylor and Maclaurin Series", """
    Taylor series represent functions as infinite polynomials around a point a:
    f(x) equals sum from n equals 0 to infinity of f to the n derivative at a times (x minus a) to the n over n factorial.
    Maclaurin series are Taylor series centered at zero.
    Common series include e to the x, sine x, and cosine x.
    These series allow us to approximate transcendental functions using polynomials.
    """),
    
    (18, "Parametric Equations", """
    Parametric equations express x and y coordinates as functions of a parameter t.
    To find dy/dx for parametric curves, we use: dy/dx equals (dy/dt) divided by (dx/dt).
    Arc length for parametric curves uses: integral of square root of (dx/dt) squared plus (dy/dt) squared dt.
    Parametric equations are essential for describing motion, cycloids, and other complex curves.
    """),
    
    (19, "Polar Coordinates", """
    Polar coordinates express points using radius r and angle theta instead of x and y.
    The conversion formulas are: x equals r cosine theta, y equals r sine theta.
    Area in polar coordinates: A equals one half times integral of r squared d theta.
    Arc length: integral of square root of r squared plus (dr/d theta) squared d theta.
    Polar form is natural for circular and spiral patterns.
    """),
    
    (20, "Vector Calculus Intro", """
    Vector calculus extends single-variable calculus to vector fields and multivariable functions.
    Gradient, divergence, and curl are fundamental vector operators.
    Line integrals compute work done by force fields along curves.
    Green's theorem relates line integrals around closed curves to double integrals over regions.
    This forms the foundation for advanced topics in physics and engineering.
    """)
]
    (9,  "Fundamental Theorem of Calculus", "https://www.youtube.com/watch?v=HfACrKJ_Y2w"),
    (10, "Integration by Parts",           "https://www.youtube.com/watch?v=2I-_SV8cwsw"),
    (11, "Optimization Problems",          "https://www.youtube.com/watch?v=WUvTyaaNkzM"),
    (12, "Mean Value Theorem",             "https://www.youtube.com/watch?v=SJe21zF5xNM"),
    (13, "Partial Fractions",              "https://www.youtube.com/watch?v=YQW_adN0jKw"),
    (14, "Trigonometric Substitution",     "https://www.youtube.com/watch?v=8GPkwvZcGvs"),
    (15, "Infinite Series Introduction",   "https://www.youtube.com/watch?v=Tj8p_mpICa8"),
    (16, "Newton's Method",                "https://www.youtube.com/watch?v=1uN8cBGVpfs"),
    (17, "Parametric Equations",           "https://www.youtube.com/watch?v=GNcFjFmqEc8"),
    (18, "Area Between Curves",            "https://www.youtube.com/watch?v=x_TkJcMZm6s"),
    (19, "Improper Integrals",             "https://www.youtube.com/watch?v=fWOGfzC3IeY"),
    (20, "Taylor Series",                  "https://www.youtube.com/watch?v=3d6DsjIBzJ4"),
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "audio")

AUDIO_INSTRUCTIONS = (
    "Create an engaging, educational audio discussion about this calculus topic. "
    "Assume the listener is a university student taking Calculus 1 (Calc 1ZB3 at McMaster). "
    "Keep it concise, clear, and focused on building intuition. "
    "Use examples where helpful."
)


async def generate_one(client, reel_id: int, title: str, url: str) -> bool:
    """Generate audio for a single topic. Returns True on success."""
    output_path = os.path.join(OUTPUT_DIR, f"reel-{reel_id}.mp3")

    try:
        print(f"  [{reel_id}/20] Creating notebook for: {title}")
        nb = await client.notebooks.create(f"CalculusReels - {title}")

        print(f"  [{reel_id}/20] Adding YouTube source...")
        await client.sources.add_url(nb.id, url, wait=True)

        print(f"  [{reel_id}/20] Generating audio overview (this takes a few minutes)...")
        status = await client.artifacts.generate_audio(
            nb.id, instructions=AUDIO_INSTRUCTIONS
        )
        await client.artifacts.wait_for_completion(nb.id, status.task_id)

        print(f"  [{reel_id}/20] Downloading audio...")
        await client.artifacts.download_audio(nb.id, output_path)

        print(f"  [{reel_id}/20] Done -> {output_path}")
        return True

    except Exception as e:
        print(f"  [{reel_id}/20] FAILED: {e}", file=sys.stderr)
        return False


async def main():
    parser = argparse.ArgumentParser(description="Generate NotebookLM audio for CalculusReels")
    parser.add_argument("--force", action="store_true", help="Regenerate all, even if file exists")
    parser.add_argument("--id", type=int, help="Generate only this topic ID")
    parser.add_argument("--delay", type=int, default=30, help="Seconds between topics (rate limit protection)")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Filter topics
    topics = TOPICS
    if args.id:
        topics = [(tid, t, u) for tid, t, u in TOPICS if tid == args.id]
        if not topics:
            print(f"No topic with id={args.id}")
            sys.exit(1)

    # Import here so the script shows a helpful error if not installed
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        print("notebooklm-py is not installed. Run:")
        print("  pip install -r requirements.txt")
        print("  playwright install chromium")
        print("  notebooklm login")
        sys.exit(1)

    print(f"Generating audio for {len(topics)} topic(s)...\n")
    successes, failures = 0, 0

    async with await NotebookLMClient.from_storage() as client:
        for i, (reel_id, title, url) in enumerate(topics):
            output_path = os.path.join(OUTPUT_DIR, f"reel-{reel_id}.mp3")

            if not args.force and os.path.exists(output_path):
                print(f"  [{reel_id}/20] Skipping (already exists): {output_path}")
                successes += 1
                continue

            ok = await generate_one(client, reel_id, title, url)
            if ok:
                successes += 1
            else:
                failures += 1

            # Rate limit protection between topics
            if i < len(topics) - 1:
                print(f"  Waiting {args.delay}s before next topic...")
                await asyncio.sleep(args.delay)

    print(f"\nDone: {successes} succeeded, {failures} failed")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
