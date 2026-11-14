from fractions import Fraction
import io
import math
import random
from fpdf import FPDF
import streamlit as st

st.set_page_config(page_title="5th Grade Fraction Lab", layout="wide")

# --- INITIALIZE SESSION STATE ---
if "score" not in st.session_state:
  st.session_state.score = 0
if "questions_answered" not in st.session_state:
  st.session_state.questions_answered = 0
if "quiz_question" not in st.session_state:
  st.session_state.quiz_question = None
  st.session_state.quiz_options = []
  st.session_state.quiz_correct = None


# --- HELPER FUNCTIONS FOR SVG MANIPULATIVES ---
def draw_fraction_bar(num, den, color="#4F8BF9", label=""):
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
      svg += f'<text x="{x + block_w/2}" y="{height/2 + 5}" font-family="sans-serif" font-size="13" font-weight="bold" fill="{text_col}" text-anchor="middle">1/{den}</text>'

  for w in range(total_units):
    svg += f'<rect x="{w * (width/total_units)}" y="0" width="{width/total_units}" height="{height}" fill="none" stroke="#333333" stroke-width="2" rx="3"/>'

  if label:
    svg += f'<text x="0" y="{height + 18}" font-family="sans-serif" font-size="14" font-weight="bold" fill="#333">{label}</text>'
  svg += "</svg>"
  return svg


def draw_fraction_circle(num, den, color="#FF6B6B"):
  size = 180
  cx, cy, r = size / 2, size / 2, (size / 2) - 10
  svg = f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">'
  if den == 1:
    fill = color if num >= 1 else "#F0F2F6"
    svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="#333" stroke-width="2"/>'
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
      path = f"M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large_arc} 1 {x2} {y2} Z"
      svg += f'<path d="{path}" fill="{fill}" stroke="#333" stroke-width="1.5"/>'
  svg += "</svg>"
  return svg


def draw_area_model(n1, d1, n2, d2):
  width, height = 300, 300
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
        fill = "#9B5DE5"
      elif is_shaded_v:
        fill = "#4F8BF9"
      elif is_shaded_h:
        fill = "#FF6B6B"
      else:
        fill = "#F0F2F6"
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
    ans = ">" if f1 > f2 else ("<" if f1 < f2 else "=")
    q_text = f"Which symbol makes this true? **{n1}/{d1} [ ? ] {n2}/{d2}**"
  else:
    d1, d2 = random.choice([3, 4, 5]), random.choice([3, 4, 5])
    n1, n2 = random.randint(1, d1 - 1), random.randint(1, d2 - 1)
    ans = Fraction(n1 * n2, d1 * d2)
    q_text = f"What is **{n1}/{d1} × {n2}/{d2}**?"

  st.session_state.quiz_question = q_text
  st.session_state.quiz_correct = str(ans)


# --- PDF WORKSHEET GENERATOR ---
def create_pdf_worksheet(num_problems, include_key):
  pdf = FPDF()
  pdf.add_page()
  pdf.set_font("Arial", "B", 16)
  pdf.cell(0, 10, "5th Grade Fraction Practice Worksheet", 0, 1, "C")
  pdf.set_font("Arial", "", 11)
  pdf.cell(
      0,
      8,
      "Name: ___________________________    Date: _______________",
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
      answers.append(
          f"{i+1}. {Fraction(n1, d) + Fraction(n2, d)}"
          if d > 0
          else f"{i+1}. N/A"
      )
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
    pdf.cell(0, 10, "Teacher Answer Key", 0, 1, "C")
    pdf.set_font("Arial", "", 11)
    for ans in answers:
      pdf.cell(0, 10, ans, 0, 1)

  return pdf.output(dest="S").encode("latin1")


# --- APP NAVIGATION ---
st.title("🧮 5th Grade Fraction Manipulative Lab")
mode = st.sidebar.radio(
    "Choose a Learning Activity:",
    [
        "1. Explore & Equivalent Fractions",
        "2. Compare Two Fractions",
        "3. Add Fractions (Unlike Denominators)",
        "4. Multiply Fractions (Area Grid Model)",
        "5. 🏆 Challenge & Quiz Mode",
        "6. 📄 Printable Worksheet Generator",
    ],
)

# [MODES 1 through 5 omitted here for brevity, keeping existing code logic...]
if mode == "1. Explore & Equivalent Fractions":
  st.header("🔍 Explore a Fraction & Find Equivalents")
  den = st.slider(
      "Denominator (Total equal parts in 1 whole)", 1, 12, 4, key="m1_den"
  )
  num = st.slider("Numerator (Shaded parts)", 0, den, 3, key="m1_num")
  st.markdown(
      draw_fraction_bar(num, den, "#4F8BF9", f"{num} out of {den} equal parts"),
      unsafe_allow_html=True,
  )

elif mode == "2. Compare Two Fractions":
  st.header("⚖️ Compare Two Fractions")
  c1, c2 = st.columns(2)
  with c1:
    den_a = st.slider("Denominator A", 1, 12, 3, key="da")
    num_a = st.slider("Numerator A", 0, den_a, 2, key="na")
    st.markdown(
        draw_fraction_bar(num_a, den_a, "#4F8BF9", f"Fraction A: {num_a}/{den_a}"),
        unsafe_allow_html=True,
    )
  with c2:
    den_b = st.slider("Denominator B", 1, 12, 5, key="db")
    num_b = st.slider("Numerator B", 0, den_b, 3, key="nb")
    st.markdown(
        draw_fraction_bar(num_b, den_b, "#FF6B6B", f"Fraction B: {num_b}/{den_b}"),
        unsafe_allow_html=True,
    )

elif mode == "3. Add Fractions (Unlike Denominators)":
  st.header("➕ Adding Fractions with Unlike Denominators")
  d1 = st.selectbox("First Denominator", [2, 3, 4, 5, 6, 8, 10], index=0)
  n1 = st.slider("First Numerator", 1, d1, 1, key="add_n1")
  d2 = st.selectbox("Second Denominator", [2, 3, 4, 5, 6, 8, 10], index=1)
  n2 = st.slider("Second Numerator", 1, d2, 1, key="add_n2")
  lcm = math.lcm(d1, d2)
  total_num = (n1 * (lcm // d1)) + (n2 * (lcm // d2))
  st.markdown(
      draw_fraction_bar(
          total_num, lcm, "#9B5DE5", f"Total = {total_num}/{lcm}"
      ),
      unsafe_allow_html=True,
  )

elif mode == "4. Multiply Fractions (Area Grid Model)":
  st.header("✖️ Multiplying Fractions with an Area Grid")
  d1, n1 = 4, 3
  d2, n2 = 3, 2
  st.markdown(draw_area_model(n1, d1, n2, d2), unsafe_allow_html=True)

elif mode == "5. 🏆 Challenge & Quiz Mode":
  st.header("🏆 Fraction Challenge Arena")
  if st.session_state.quiz_question is None:
    generate_new_question()
  st.markdown(
      f"### Question:\n{st.session_state.quiz_question}", unsafe_allow_html=True
  )
  user_ans = st.text_input("Enter your answer:")
  if st.button("Submit"):
    if user_ans.strip() == str(st.session_state.quiz_correct).strip():
      st.success("🎉 Correct!")
    else:
      st.error(f"❌ Correct answer was: {st.session_state.quiz_correct}")
  if st.button("Next"):
    generate_new_question()
    st.rerun()

# ==========================================
# MODE 6: PDF WORKSHEET GENERATOR
# ==========================================
elif mode == "6. 📄 Printable Worksheet Generator":
  st.header("📄 Printable Fraction Worksheet Generator")
  st.write(
      "Create a custom printable PDF worksheet of fraction problems complete"
      " with an optional teacher answer key page!"
  )

  col_w1, col_w2 = st.columns(2)
  with col_w1:
    num_problems = st.slider(
        "Number of Problems on Sheet", min_value=5, max_value=20, value=10
    )
  with col_w2:
    include_key = st.checkbox("Include Teacher Answer Key Page", value=True)

  if st.button("🚀 Generate PDF Worksheet"):
    pdf_bytes = create_pdf_worksheet(num_problems, include_key)
    st.success("Worksheet successfully generated!")
    st.download_button(
        label="📥 Download PDF Worksheet",
        data=pdf_bytes,
        file_name="5th_grade_fraction_practice.pdf",
        mime="application/pdf",
    )
