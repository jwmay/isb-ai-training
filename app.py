from fractions import Fraction
import math
import random
import streamlit as st

st.set_page_config(page_title="5th Grade Fraction Lab", layout="wide")


# --- INITIALIZE SESSION STATE FOR QUIZ ---
if "score" not in st.session_state:
  st.session_state.score = 0
if "questions_answered" not in st.session_state:
  st.session_state.questions_answered = 0
if "quiz_question" not in st.session_state:
  st.session_state.quiz_question = None
  st.session_state.quiz_options = []
  st.session_state.quiz_correct = None
  st.session_state.quiz_feedback = ""


# --- HELPER FUNCTIONS FOR SVG MANIPULATIVES ---
def draw_fraction_bar(num, den, color="#4F8BF9", label=""):
  """Generates an SVG horizontal fraction bar divided into `den` parts with `num` shaded."""
  width = 500
  height = 60
  total_units = max(1, math.ceil(num / den))
  total_blocks = total_units * den
  block_w = width / total_blocks

  svg = f'<svg width="100%" height="{height + 25}" viewBox="0 0 {width} {height + 25}" xmlns="http://www.w3.org/2000/svg">'

  for i in range(total_blocks):
    x = i * block_w
    fill = color if i < num else "#F0F2F6"
    stroke_w = 3 if (i % den == 0 and i > 0) else 1
    stroke_col = "#1E1E1E" if (i % den == 0 and i > 0) else "#FFFFFF"

    svg += f'<rect x="{x}" y="0" width="{block_w}" height="{height}" fill="{fill}" stroke="{stroke_col}" stroke-width="{stroke_w}" rx="3"/>'

    if block_w > 28:
      text_col = "white" if i < num else "#555555"
      svg += (
          f'<text x="{x + block_w/2}" y="{height/2 + 5}" font-family="sans-serif"'
          f' font-size="13" font-weight="bold" fill="{text_col}"'
          f' text-anchor="middle">1/{den}</text>'
      )

  for w in range(total_units):
    svg += (
        f'<rect x="{w * (width/total_units)}" y="0"'
        f' width="{width/total_units}" height="{height}" fill="none"'
        ' stroke="#333333" stroke-width="2" rx="3"/>'
    )

  if label:
    svg += (
        f'<text x="0" y="{height + 18}" font-family="sans-serif"'
        f' font-size="14" font-weight="bold" fill="#333">{label}</text>'
    )

  svg += "</svg>"
  return svg


def draw_fraction_circle(num, den, color="#FF6B6B"):
  """Generates an SVG fraction circle (pie model) for fractions <= 1."""
  size = 180
  cx, cy, r = size / 2, size / 2, (size / 2) - 10
  svg = (
      f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}"'
      ' xmlns="http://www.w3.org/2000/svg">'
  )

  if den == 1:
    fill = color if num >= 1 else "#F0F2F6"
    svg += (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="#333"'
        ' stroke-width="2"/>'
    )
  else:
    for i in range(den):
      start_angle = (i * 360 / den) - 90
      end_angle = ((i + 1) * 360 / den) - 90

      x1 = cx + r * math.cos(math.radians(start_angle))
      y1 = cy + r * math.sin(math.radians(start_angle))
      x2 = cx + r * math.cos(math.radians(end_angle))
      y2 = cy + r * math.sin(math.radians(end_angle))

      large_arc = 1 if (360 / den) > 180 else 0
      fill = color if i < num else "#F0F2F6"

      path = (
          f"M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large_arc} 1 {x2} {y2} Z"
      )
      svg += (
          f'<path d="{path}" fill="{fill}" stroke="#333"'
          ' stroke-width="1.5"/>'
      )

  svg += "</svg>"
  return svg


def draw_area_model(n1, d1, n2, d2):
  """Generates an SVG 2D grid showing fraction multiplication overlap."""
  width, height = 300, 300
  cell_w = width / d1
  cell_h = height / d2

  svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'

  # Background grid cells
  for r in range(d2):
    for c in range(d1):
      x = c * cell_w
      y = r * cell_h

      is_shaded_h = r < n2
      is_shaded_v = c < n1

      if is_shaded_h and is_shaded_v:
        fill = "#9B5DE5"  # Overlap color (Product)
      elif is_shaded_v:
        fill = "#4F8BF9"  # Fraction 1 color
      elif is_shaded_h:
        fill = "#FF6B6B"  # Fraction 2 color
      else:
        fill = "#F0F2F6"  # Unshaded

      svg += f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" fill="{fill}" stroke="#FFFFFF" stroke-width="2" rx="2"/>'

  svg += "</svg>"
  return svg


def generate_new_question():
  q_types = ["add", "compare", "multiply"]
  q_type = random.choice(q_types)

  if q_type == "add":
    d1 = random.choice([2, 3, 4, 6])
    d2 = random.choice([2, 3, 4, 6])
    n1 = random.randint(1, d1 - 1 if d1 > 1 else 1)
    n2 = random.randint(1, d2 - 1 if d2 > 1 else 1)
    ans = Fraction(n1, d1) + Fraction(n2, d2)
    q_text = f"What is **{n1}/{d1} + {n2}/{d2}**?"
  elif q_type == "compare":
    d1 = random.choice([3, 4, 5, 6, 8])
    d2 = random.choice([3, 4, 5, 6, 8])
    n1 = random.randint(1, d1 - 1)
    n2 = random.randint(1, d2 - 1)
    f1, f2 = Fraction(n1, d1), Fraction(n2, d2)
    if f1 > f2:
      ans = f"{n1}/{d1} > {n2}/{d2}"
    elif f1 < f2:
      ans = f"{n1}/{d1} < {n2}/{d2}"
    else:
      ans = f"{n1}/{d1} = {n2}/{d2}"
    q_text = (
        f"Which symbol makes this true? **{n1}/{d1} [ ? ] {n2}/{d2}** (Choose"
        " >, <, or =)"
    )
  else:
    d1, d2 = random.choice([3, 4, 5]), random.choice([3, 4, 5])
    n1, n2 = random.randint(1, d1 - 1), random.randint(1, d2 - 1)
    ans = Fraction(n1 * n2, d1 * d2)
    q_text = f"What is **{n1}/{d1} × {n2}/{d2}**?"

  st.session_state.quiz_question = q_text
  st.session_state.quiz_correct = str(ans)
  st.session_state.quiz_feedback = ""


# --- APP HEADER & NAVIGATION ---
st.title("🧮 5th Grade Fraction Manipulative Lab")
st.markdown(
    "Explore how fractions work visually using **Fraction Bars**, **Area"
    " Models**, and test your skills in **Challenge Mode**!"
)

mode = st.sidebar.radio(
    "Choose a Learning Activity:",
    [
        "1. Explore & Equivalent Fractions",
        "2. Compare Two Fractions",
        "3. Add Fractions (Unlike Denominators)",
        "4. Multiply Fractions (Area Grid Model)",
        "5. 🏆 Challenge & Quiz Mode",
    ],
)

# ==========================================
# MODE 1: EXPLORE & EQUIVALENCE
# ==========================================
if mode == "1. Explore & Equivalent Fractions":
  st.header("🔍 Explore a Fraction & Find Equivalents")
  st.write(
      "Adjust the numerator and denominator to see how the pieces change size."
  )

  col1, col2 = st.columns([1, 2])
  with col1:
    den = st.slider(
        "Denominator (Total equal parts in 1 whole)", 1, 12, 4, key="m1_den"
    )
    num = st.slider("Numerator (Shaded parts)", 0, den, 3, key="m1_num")

    st.metric(
        label="Decimal & Percentage Value",
        value=f"{num/den:.3f}",
        delta=f"{(num/den)*100:.1f}%",
    )

  with col2:
    st.subheader(f"Visualizing {num}/{den}")
    st.markdown(
        draw_fraction_bar(
            num, den, "#4F8BF9", f"{num} out of {den} equal parts"
        ),
        unsafe_allow_html=True,
    )

    c_circle, c_eq = st.columns([1, 1.5])
    with c_circle:
      st.markdown(
          draw_fraction_circle(num, den, "#4F8BF9"), unsafe_allow_html=True
      )
    with c_eq:
      st.write("**Equivalent Fractions (Same Amount, Different Cut Sizes):**")
      multiplier = st.slider(
          "Split each piece into how many smaller pieces?", 1, 4, 2, key="m1_mult"
      )
      eq_num, eq_den = num * multiplier, den * multiplier
      st.markdown(
          draw_fraction_bar(
              eq_num,
              eq_den,
              "#2EC4B6",
              f"{num}/{den} = {eq_num}/{eq_den}",
          ),
          unsafe_allow_html=True,
      )

# ==========================================
# MODE 2: COMPARE TWO FRACTIONS
# ==========================================
elif mode == "2. Compare Two Fractions":
  st.header("⚖️ Compare Two Fractions")
  st.write(
      "Line up two fraction bars to see which one takes up more space."
  )

  c1, c2 = st.columns(2)
  with c1:
    st.subheader("Fraction A (Blue)")
    den_a = st.slider("Denominator A", 1, 12, 3, key="da")
    num_a = st.slider("Numerator A", 0, den_a, 2, key="na")
    st.markdown(
        draw_fraction_bar(num_a, den_a, "#4F8BF9", f"Fraction A: {num_a}/{den_a}"),
        unsafe_allow_html=True,
    )

  with c2:
    st.subheader("Fraction B (Coral)")
    den_b = st.slider("Denominator B", 1, 12, 5, key="db")
    num_b = st.slider("Numerator B", 0, den_b, 3, key="nb")
    st.markdown(
        draw_fraction_bar(num_b, den_b, "#FF6B6B", f"Fraction B: {num_b}/{den_b}"),
        unsafe_allow_html=True,
    )

  st.divider()
  val_a = Fraction(num_a, den_a)
  val_b = Fraction(num_b, den_b)

  if val_a > val_b:
    symbol = ">"
    msg = f"**{num_a}/{den_a}** is greater than **{num_b}/{den_b}**"
  elif val_a < val_b:
    symbol = "<"
    msg = f"**{num_a}/{den_a}** is less than **{num_b}/{den_b}**"
  else:
    symbol = "="
    msg = f"**{num_a}/{den_a}** is equal to **{num_b}/{den_b}**!"

  st.markdown(
      f"<h2 style='text-align: center;'>{num_a}/{den_a} &nbsp; {symbol} &nbsp;"
      f" {num_b}/{den_b}</h2>",
      unsafe_allow_html=True,
  )
  st.info(f"💡 **Why?** {msg}")

# ==========================================
# MODE 3: ADD UNLIKE FRACTIONS
# ==========================================
elif mode == "3. Add Fractions (Unlike Denominators)":
  st.header("➕ Adding Fractions with Unlike Denominators")
  st.write(
      "To add fractions with different piece sizes, convert them into"
      " **same-sized pieces** (common denominator)."
  )

  col1, col2 = st.columns(2)
  with col1:
    d1 = st.selectbox("First Denominator", [2, 3, 4, 5, 6, 8, 10], index=0)
    n1 = st.slider("First Numerator", 1, d1, 1, key="add_n1")
  with col2:
    d2 = st.selectbox("Second Denominator", [2, 3, 4, 5, 6, 8, 10], index=1)
    n2 = st.slider("Second Numerator", 1, d2, 1, key="add_n2")

  st.subheader("Step 1: Original Pieces")
  st.markdown(
      draw_fraction_bar(n1, d1, "#4F8BF9", f"{n1}/{d1}"), unsafe_allow_html=True
  )
  st.markdown(
      draw_fraction_bar(n2, d2, "#FF6B6B", f"{n2}/{d2}"), unsafe_allow_html=True
  )

  st.subheader("Step 2: Common Denominator Grid")
  lcm = math.lcm(d1, d2)
  eq_n1 = n1 * (lcm // d1)
  eq_n2 = n2 * (lcm // d2)
  total_num = eq_n1 + eq_n2

  st.write(f"Common denominator is **{lcm}**:")
  st.markdown(
      draw_fraction_bar(eq_n1, lcm, "#4F8BF9", f"{eq_n1}/{lcm}"),
      unsafe_allow_html=True,
  )
  st.markdown(
      draw_fraction_bar(eq_n2, lcm, "#FF6B6B", f"{eq_n2}/{lcm}"),
      unsafe_allow_html=True,
  )

  st.subheader("Step 3: Combined Sum")
  st.markdown(
      draw_fraction_bar(
          total_num, lcm, "#9B5DE5", f"Total = {total_num}/{lcm}"
      ),
      unsafe_allow_html=True,
  )
  simplified = Fraction(total_num, lcm)
  st.success(
      f"**Result:** `{total_num}/{lcm}` (Simplified:"
      f" `{simplified.numerator}/{simplified.denominator}`)"
  )

# ==========================================
# MODE 4: MULTIPLY FRACTIONS (AREA GRID)
# ==========================================
elif mode == "4. Multiply Fractions (Area Grid Model)":
  st.header("✖️ Multiplying Fractions with an Area Grid")
  st.write(
      "When multiplying fractions like $\\frac{2}{3} \\times \\frac{3}{4}$,"
      " imagine a square garden. One fraction is shaded horizontally (Blue),"
      " and the other vertically (Coral). The **purple overlapping squares**"
      " show the product!"
  )

  col1, col2 = st.columns([1, 2])
  with col1:
    d1 = st.slider("Width Denominator", 2, 6, 4, key="m_d1")
    n1 = st.slider("Width Numerator", 1, d1, 3, key="m_n1")
    d2 = st.slider("Height Denominator", 2, 6, 3, key="m_d2")
    n2 = st.slider("Height Numerator", 1, d2, 2, key="m_n2")

    num_product = n1 * n2
    den_product = d1 * d2
    prod_fraction = Fraction(num_product, den_product)

    st.metric(
        label="Multiplication Result",
        value=f"{num_product}/{den_product}",
        delta=(
            f"Simplified: {prod_fraction.numerator}/{prod_fraction.denominator}"
        ),
    )

  with col2:
    st.subheader(
        f"Area Grid: {n1}/{d1} × {n2}/{d2} = {num_product}/{den_product}"
    )
    st.markdown(draw_area_model(n1, d1, n2, d2), unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #666; font-size: 14px;'>🟦 Blue: Width fraction &nbsp;|&nbsp;"
        " 🟥 Coral: Height fraction &nbsp;|&nbsp; 🟪 Purple: Overlapping"
        " product</p>",
        unsafe_allow_html=True,
    )

# ==========================================
# MODE 5: CHALLENGE & QUIZ MODE
# ==========================================
elif mode == "5. 🏆 Challenge & Quiz Mode":
  st.header("🏆 Fraction Challenge Arena")
  st.write("Test your visual fraction skills! Solve problems to earn points.")

  col_score1, col_score2 = st.columns(2)
  with col_score1:
    st.metric("Score", st.session_state.score)
  with col_score2:
    st.metric("Questions Answered", st.session_state.questions_answered)

  if st.session_state.quiz_question is None:
    generate_new_question()

  st.markdown(
      f"### Question:\n{st.session_state.quiz_question}", unsafe_allow_html=True
  )

  user_ans = st.text_input(
      "Enter your answer (e.g. `3/4`, `>`, or `5/12`):", key="user_input_quiz"
  )

  col_btn1, col_btn2 = st.columns(2)
  with col_btn1:
    if st.button("Submit Answer"):
      st.session_state.questions_answered += 1
      # Clean string formatting for comparison
      cleaned_user = user_ans.strip().replace(" ", "")
      cleaned_correct = str(st.session_state.quiz_correct).strip().replace(
          " ", ""
      )

      if cleaned_user == cleaned_correct:
        st.session_state.score += 1
        st.success(
            "🎉 **Correct! Great job!** Click next to tackle another one."
        )
      else:
        st.error(
            f"❌ Not quite! The correct answer was **{cleaned_correct}**."
        )

  with col_btn2:
    if st.button("Next Question ➡️"):
      generate_new_question()
      st.rerun()
