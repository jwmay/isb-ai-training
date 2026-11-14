from fractions import Fraction
import math
import random
from fpdf import FPDF
import streamlit as st

# --- PAGE CONFIGURATION & CHUNKY ARCADE CSS ---
st.set_page_config(
    page_title="🌟 Fun 5th Grade Fraction Adventure! 🍕", layout="wide"
)

st.markdown("""
    <style>
    /* Main App Background & Default Text */
    .stApp {
        background: #F0F4F8;
        font-family: 'Comic Sans MS', 'Chalkboard SE', 'Arial Rounded MT Bold', sans-serif;
        color: #1A365D;
    }
    
    /* Force Sidebar Background & Text Contrast */
    [data-testid="stSidebar"] {
        background-color: #FFFDF0;
        border-right: 3px solid #FFD166;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #1A365D !important;
        font-weight: bold;
    }
    
    /* High-Contrast Main Headers */
    h1, h2, h3 {
        color: #1A365D !important;
        font-weight: 900;
    }
    
    /* Standard Markdown Text */
    p, span, label, .stMarkdown {
        color: #1A365D !important;
        font-size: 18px;
    }
    
    /* Custom Card Containers for High Readability */
    .fun-card {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border: 4px solid #FFD166;
    }
    
    /* --- BIG CHUNKY ARCADE SLIDERS --- */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #FF6B6B !important;
        height: 32px !important;
        width: 32px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border: 3px solid #FFFFFF !important;
    }
    div[data-baseweb="slider"] div:has(> div[role="slider"]) {
        background-color: #4ECDC4 !important;
        height: 12px !important;
        border-radius: 6px !important;
    }
    
    /* Playful Buttons Styling */
    .stButton>button {
        background-color: #FF6B6B;
        color: white !important;
        font-size: 20px;
        font-weight: bold;
        border-radius: 18px;
        padding: 12px 28px;
        border: none;
        box-shadow: 0 5px #D9534F;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #FF5252;
        box-shadow: 0 2px #C9302C;
        transform: translateY(3px);
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if "score" not in st.session_state:
  st.session_state.score = 0
if "questions_answered" not in st.session_state:
  st.session_state.questions_answered = 0
if "quiz_question" not in st.session_state:
  st.session_state.quiz_question = None
  st.session_state.quiz_correct = None


# --- HELPER FUNCTIONS FOR SVG MANIPULATIVES ---
def draw_fraction_bar(num, den, color="#FF6B6B", label=""):
  width = 500
  height = 65
  total_units = max(1, math.ceil(num / den))
  total_blocks = total_units * den
  block_w = width / total_blocks

  svg = f'<svg width="100%" height="{height + 35}" viewBox="0 0 {width} {height + 35}" xmlns="http://www.w3.org/2000/svg">'
  for i in range(total_blocks):
    x = i * block_w
    fill = color if i < num else "#EDF2F7"
    stroke_w = 3 if (i % den == 0 and i > 0) else 1
    stroke_col = "#2D3748" if (i % den == 0 and i > 0) else "#CBD5E0"
    svg += f'<rect x="{x}" y="0" width="{block_w}" height="{height}" fill="{fill}" stroke="{stroke_col}" stroke-width="{stroke_w}" rx="10"/>'
    if block_w > 28:
      text_col = "white" if i < num else "#1A365D"
      svg += f'<text x="{x + block_w/2}" y="{height/2 + 7}" font-family="sans-serif" font-size="16" font-weight="bold" fill="{text_col}" text-anchor="middle">1/{den}</text>'

  for w in range(total_units):
    svg += f'<rect x="{w * (width/total_units)}" y="0" width="{width/total_units}" height="{height}" fill="none" stroke="#1A365D" stroke-width="4" rx="10"/>'

  if label:
    svg += f'<text x="5" y="{height + 28}" font-family="sans-serif" font-size="18" font-weight="bold" fill="#1A365D">{label}</text>'
  svg += "</svg>"
  return svg


def draw_fraction_circle(num, den, color="#4ECDC4"):
  size = 200
  cx, cy, r = size / 2, size / 2, (size / 2) - 10
  svg = f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">'
  if den == 1:
    fill = color if num >= 1 else "#EDF2F7"
    svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="#1A365D" stroke-width="4"/>'
  else:
    for i in range(den):
      start_angle = (i * 360 / den) - 90
      end_angle = ((i + 1) * 360 / den) - 90
      x1 = cx + r * math.cos(math.radians(start_angle))
      y1 = cy + r * math.sin(math.radians(start_angle))
      x2 = cx + r * math.cos(math.radians(end_angle))
      y2 = cy + r * math.sin(math.radians(end_angle))
      large_arc = 1 if (360 / den) > 180 else 0
      fill = color if i < num else "#EDF2F7"
      path = f"M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large_arc} 1 {x2} {y2} Z"
      svg += f'<path d="{path}" fill="{fill}" stroke="#1A365D" stroke-width="2.5"/>'
  svg += "</svg>"
  return svg


def draw_area_model(n1, d1, n2, d2):
  width, height = 320, 320
  cell_w = width / d1
  cell_h = height / d2
  svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'
  for r in range(d2):
    for c in range(d1):
      x = c * cell_w
      y = r * cell_h
      is_shaded_h = r < n2
      is_shaded_v = c < n1
      if is_shaded_h and is_shaded_v:
        fill = "#FF6B6B"
      elif is_shaded_v:
        fill = "#4ECDC4"
      elif is_shaded_h:
        fill = "#FFD166"
      else:
        fill = "#EDF2F7"
      svg += f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" fill="{fill}" stroke="#FFFFFF" stroke-width="3" rx="6"/>'
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
    q_text = f"🍕 What is **{n1}/{d1} + {n2}/{d2}**?"
  elif q_type == "compare":
    d1 = random.choice([3, 4, 5, 6, 8])
    d2 = random.choice([3, 4, 5, 6, 8])
    n1 = random.randint(1, d1 - 1)
    n2 = random.randint(1, d2 - 1)
    f1, f2 = Fraction(n1, d1), Fraction(n2, d2)
    ans = ">" if f1 > f2 else ("<" if f1 < f2 else "=")
    q_text = (
        f"⚖️ Which magic symbol fits best? **{n1}/{d1} [ ? ] {n2}/{d2}** (Type >,"
        " <, or =)"
    )
  else:
    d1, d2 = random.choice([3, 4, 5]), random.choice([3, 4, 5])
    n1, n2 = random.randint(1, d1 - 1), random.randint(1, d2 - 1)
    ans = Fraction(n1 * n2, d1 * d2)
    q_text = f"🎨 What is **{n1}/{d1} × {n2}/{d2}**?"

  st.session_state.quiz_question = q_text
  st.session_state.quiz_correct = str(ans)


# --- PDF WORKSHEET GENERATOR ---
def create_pdf_worksheet(num_problems, include_key):
  pdf = FPDF()
  pdf.add_page()
  pdf.set_font("Arial", "B", 16)
  pdf.cell(
      0, 10, "🌟 5th Grade Super Fun Fraction Practice Worksheet 🌟", 0, 1, "C"
  )
  pdf.set_font("Arial", "", 11)
  pdf.cell(
      0,
      8,
      "Explorer Name: ___________________________    Date: _______________",
      0,
      1,
      "L",
  )
  pdf.ln(5)

  problems = []
  answers = []

  for i in range(num_problems):
    p_type = random.choice(["add", "subtract", "multiply"])
    if p_type == "add":
      d = random.choice([3, 4, 6, 8])
      n1, n2 = random.randint(1, d - 1), random.randint(1, d - 1)
      problems.append(f"{i+1}.  {n1}/{d} + {n2}/{d} = _________")
      answers.append(f"{i+1}. {Fraction(n1, d) + Fraction(n2, d)}")
    elif p_type == "subtract":
      d = random.choice([3, 4, 6, 8])
      n1 = random.randint(2, d)
      n2 = random.randint(1, n1 - 1) if n1 > 1 else 1
      problems.append(f"{i+1}.  {n1}/{d} - {n2}/{d} = _________")
      answers.append(f"{i+1}. {Fraction(n1, d) - Fraction(n2, d)}")
    else:
      d1, d2 = random.choice([2, 3, 4]), random.choice([2, 3, 4])
      n1, n2 = random.randint(1, d1 - 1), random.randint(1, d2 - 1)
      problems.append(f"{i+1}.  {n1}/{d1} x {n2}/{d2} = _________")
      answers.append(f"{i+1}. {Fraction(n1*n2, d1*d2)}")

  pdf.set_font("Arial", "", 12)
  for prob in problems:
    pdf.cell(0, 12, prob, 0, 1)

  if include_key:
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "🔑 Secret Teacher Answer Key", 0, 1, "C")
    pdf.set_font("Arial", "", 11)
    for ans in answers:
      pdf.cell(0, 10, ans, 0, 1)

  return bytes(pdf.output())


# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown(
    "<h2>🚀 Fraction Quest</h2><p>Choose your exciting activity below!</p>",
    unsafe_allow_html=True,
)
mode = st.sidebar.radio(
    "",
    [
        "1. 🍕 Pizza & Bar Explorer",
        "2. ⚖️ Fraction Battle",
        "3. ➕ Super Addition",
        "4. 🎨 Magic Area Garden",
        "5. 🏆 Challenge Arena",
        "6. 📄 Printable Worksheets",
    ],
)

# ==========================================
# MODE 1: EXPLORE & EQUIVALENCE
# ==========================================
if mode == "1. 🍕 Pizza & Bar Explorer":
  st.markdown("<h1>🍕 Pizza & Fraction Bar Explorer</h1>", unsafe_allow_html=True)
  st.markdown("<div class='fun-card'>", unsafe_allow_html=True)
  st.write(
      "Welcome to the fraction diner! Grab the **big chunky sliders** below"
      " to cut delicious pizzas and bars into equal slices!"
  )

  col1, col2 = st.columns([1, 2])
  with col1:
    st.markdown("### 🎛️ Big Slicer Controls")
    den = st.slider(
        "Slices in 1 Whole (Denominator)", 1, 12, 4, key="m1_den"
    )
    num = st.slider("Yummy Shaded Slices (Numerator)", 0, den, 3, key="m1_num")

    st.metric(
        label="⭐ Fraction Value",
        value=f"{num/den:.3f}",
        delta=f"{(num/den)*100:.1f}% filled",
    )

  with col2:
    st.markdown(f"### 🎉 Showing: {num} out of {den} Slices")
    st.markdown(
        draw_fraction_bar(
            num, den, "#FF6B6B", f"Fraction Bar: {num}/{den} slices"
        ),
        unsafe_allow_html=True,
    )

    c_circle, c_eq = st.columns([1, 1.5])
    with c_circle:
      st.markdown(
          draw_fraction_circle(num, den, "#4ECDC4"), unsafe_allow_html=True
      )
    with c_eq:
      st.markdown("### ✨ Magic Equivalents")
      multiplier = st.slider(
          "Cut each slice into smaller pieces:", 1, 4, 2, key="m1_mult"
      )
      eq_num, eq_den = num * multiplier, den * multiplier
      st.markdown(
          draw_fraction_bar(
              eq_num,
              eq_den,
              "#FFD166",
              f"Equivalent: {num}/{den} = {eq_num}/{eq_den}!",
          ),
          unsafe_allow_html=True,
      )
  st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# MODE 2: COMPARE TWO FRACTIONS
# ==========================================
elif mode == "2. ⚖️ Fraction Battle":
  st.markdown("<h1>⚖️ Fraction Battle Arena</h1>", unsafe_allow_html=True)
  st.markdown("<div class='fun-card'>", unsafe_allow_html=True)
  st.write(
      "Use the big sliders to set two fraction treats side-by-side. Which one"
      " is bigger?"
  )

  c1, c2 = st.columns(2)
  with c1:
    st.markdown("### 🔵 Team Blue")
    den_a = st.slider("Denominator A", 1, 12, 3, key="da")
    num_a = st.slider("Numerator A", 0, den_a, 2, key="na")
    st.markdown(
        draw_fraction_bar(num_a, den_a, "#4ECDC4", f"Team Blue: {num_a}/{den_a}"),
        unsafe_allow_html=True,
    )

  with c2:
    st.markdown("### 🔴 Team Coral")
    den_b = st.slider("Denominator B", 1, 12, 5, key="db")
    num_b = st.slider("Numerator B", 0, den_b, 3, key="nb")
    st.markdown(
        draw_fraction_bar(
            num_b, den_b, "#FF6B6B", f"Team Coral: {num_b}/{den_b}"
        ),
        unsafe_allow_html=True,
    )

  st.divider()
  val_a = Fraction(num_a, den_a)
  val_b = Fraction(num_b, den_b)

  if val_a > val_b:
    symbol = ">"
    msg = f"🏆 **Team Blue ({num_a}/{den_a})** wins the battle!"
  elif val_a < val_b:
    symbol = "<"
    msg = f"🏆 **Team Coral ({num_b}/{den_b})** wins the battle!"
  else:
    symbol = "="
    msg = "🤝 It's a tie! Both fractions are completely equal!"

  st.markdown(
      f"<h2 style='text-align: center; color: #1A365D;'>{num_a}/{den_a} &nbsp;"
      f" {symbol} &nbsp; {num_b}/{den_b}</h2>",
      unsafe_allow_html=True,
  )
  st.success(msg)
  st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# MODE 3: ADD UNLIKE FRACTIONS
# ==========================================
elif mode == "3. ➕ Super Addition":
  st.markdown(
      "<h1>➕ Super Fraction Addition Combiner</h1>", unsafe_allow_html=True
  )
  st.markdown("<div class='fun-card'>", unsafe_allow_html=True)
  st.write(
      "Slide the controls to add pieces of different sizes using our magic"
      " common denominator machine!"
  )

  col1, col2 = st.columns(2)
  with col1:
    d1 = st.selectbox("First Pizza Cut Size", [2, 3, 4, 5, 6, 8, 10], index=0)
    n1 = st.slider("First Slices", 1, d1, 1, key="add_n1")
  with col2:
    d2 = st.selectbox("Second Pizza Cut Size", [2, 3, 4, 5, 6, 8, 10], index=1)
    n2 = st.slider("Second Slices", 1, d2, 1, key="add_n2")

  st.markdown("### Step 1: Your Original Pizzas")
  st.markdown(
      draw_fraction_bar(n1, d1, "#4ECDC4", f"Pizza 1: {n1}/{d1}"),
      unsafe_allow_html=True,
  )
  st.markdown(
      draw_fraction_bar(n2, d2, "#FF6B6B", f"Pizza 2: {n2}/{d2}"),
      unsafe_allow_html=True,
  )

  st.markdown("### Step 2: Slice into Matching Sizes")
  lcm = math.lcm(d1, d2)
  eq_n1 = n1 * (lcm // d1)
  eq_n2 = n2 * (lcm // d2)
  total_num = eq_n1 + eq_n2

  st.write(f"✨ Magic common slice size: **{lcm}ths**!")
  st.markdown(
      draw_fraction_bar(eq_n1, lcm, "#4ECDC4", f"{n1}/{d1} = {eq_n1}/{lcm}"),
      unsafe_allow_html=True,
  )
  st.markdown(
      draw_fraction_bar(eq_n2, lcm, "#FF6B6B", f"{n2}/{d2} = {eq_n2}/{lcm}"),
      unsafe_allow_html=True,
  )

  st.markdown("### Step 3: Combine Your Feast!")
  st.markdown(
      draw_fraction_bar(
          total_num,
          lcm,
          "#FFD166",
          f"Total Feast = {eq_n1}/{lcm} + {eq_n2}/{lcm} = {total_num}/{lcm}",
      ),
      unsafe_allow_html=True,
  )
  simplified = Fraction(total_num, lcm)
  st.success(
      f"🌟 **Super Result:** `{total_num}/{lcm}` (Simplified: "
      f"`{simplified.numerator}/{simplified.denominator}`)"
  )
  st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# MODE 4: MULTIPLY FRACTIONS (AREA GRID)
# ==========================================
elif mode == "4. 🎨 Magic Area Garden":
  st.markdown("<h1>🎨 Magic Area Garden Multiplier</h1>", unsafe_allow_html=True)
  st.markdown("<div class='fun-card'>", unsafe_allow_html=True)
  st.write(
      "Use the big chunky sliders to plant your garden width and height!"
      " The sparkling **Coral overlapping squares** show your harvest crop."
  )

  col1, col2 = st.columns([1, 2])
  with col1:
    d1 = st.slider("Garden Width Slices", 2, 6, 4, key="m_d1")
    n1 = st.slider("Planted Width Slices", 1, d1, 3, key="m_n1")
    d2 = st.slider("Garden Height Slices", 2, 6, 3, key="m_d2")
    n2 = st.slider("Planted Height Slices", 1, d2, 2, key="m_n2")

    num_product = n1 * n2
    den_product = d1 * d2
    prod_fraction = Fraction(num_product, den_product)

    st.metric(
        label="🌻 Harvest Crop Total",
        value=f"{num_product}/{den_product}",
        delta=(
            f"Simple: {prod_fraction.numerator}/{prod_fraction.denominator}"
        ),
    )

  with col2:
    st.markdown(
        f"### Garden Grid: {n1}/{d1} × {n2}/{d2} = {num_product}/{den_product}"
    )
    st.markdown(draw_area_model(n1, d1, n2, d2), unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #1A365D; font-size: 16px; font-weight: bold;'>🟦 Teal:"
        " Width &nbsp;|&nbsp; 🟨 Yellow: Height &nbsp;|&nbsp; 🟥 Coral: Overlap"
        " Harvest!</p>",
        unsafe_allow_html=True,
    )
  st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# MODE 5: CHALLENGE & QUIZ MODE
# ==========================================
elif mode == "5. 🏆 Challenge Arena":
  st.markdown("<h1>🏆 Fraction Challenge Arena</h1>", unsafe_allow_html=True)
  st.markdown("<div class='fun-card'>", unsafe_allow_html=True)
  st.write("Earn points, collect stellar scores, and become a fraction master!")

  col_score1, col_score2 = st.columns(2)
  with col_score1:
    st.metric("⭐ Your Score", st.session_state.score)
  with col_score2:
    st.metric("🎯 Quests Completed", st.session_state.questions_answered)

  if st.session_state.quiz_question is None:
    generate_new_question()

  st.markdown(
      f"<div style='background-color: #F7FAFC; padding: 20px; border-radius:"
      f" 15px; border: 2px dashed #CBD5E0; margin-bottom: 20px;'><h3"
      f" style='color: #1A365D !important;'>{st.session_state.quiz_question}</h3></div>",
      unsafe_allow_html=True,
  )

  user_ans = st.text_input("Type your awesome answer here (e.g. `3/4` or `>`):")

  col_btn1, col_btn2 = st.columns(2)
  with col_btn1:
    if st.button("🚀 Check My Answer!"):
      st.session_state.questions_answered += 1
      cleaned_user = user_ans.strip().replace(" ", "")
      cleaned_correct = str(st.session_state.quiz_correct).strip().replace(
          " ", ""
      )

      if cleaned_user == cleaned_correct:
        st.session_state.score += 1
        st.balloons()
        st.success("🎉 Woohoo! Spot on! You rock! 🌟")
      else:
        st.error(
            f"💡 Good try! The correct answer was **{cleaned_correct}**. Keep"
            " going!"
        )

  with col_btn2:
    if st.button("➡️ Next Quest!"):
      generate_new_question()
      st.rerun()
  st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# MODE 6: PDF WORKSHEET GENERATOR
# ==========================================
elif mode == "6. 📄 Printable Worksheets":
  st.markdown("<h1>📄 Printable Fraction Worksheet Factory</h1>", unsafe_allow_html=True)
  st.markdown("<div class='fun-card'>", unsafe_allow_html=True)
  st.write(
      "Teachers and students! Build a customized printable practice packet"
      " complete with a secret answer key!"
  )

  col_w1, col_w2 = st.columns(2)
  with col_w1:
    num_problems = st.slider(
        "Number of Quests on Sheet", min_value=5, max_value=20, value=10
    )
  with col_w2:
    include_key = st.checkbox(
        "Include Secret Teacher Answer Key Page 🔑", value=True
    )

  if st.button("✨ Magic Print Worksheet"):
    pdf_bytes = create_pdf_worksheet(num_problems, include_key)
    st.success("🎉 Your custom worksheet is ready for takeoff!")
    st.download_button(
        label="📥 Download Printable PDF",
        data=pdf_bytes,
        file_name="fun_fraction_practice_packet.pdf",
        mime="application/pdf",
    )
  st.markdown("</div>", unsafe_allow_html=True)
