from fractions import Fraction
import math
import streamlit as st

st.set_page_config(page_title="5th Grade Fraction Lab", layout="wide")


# --- HELPER FUNCTIONS FOR SVG MANIPULATIVES ---
def draw_fraction_bar(num, den, color="#4F8BF9", label=""):
  """Generates an SVG horizontal fraction bar divided into `den` parts with `num` shaded."""
  width = 500
  height = 60
  # Handle improper fractions by scaling the bar width if num > den
  total_units = max(1, math.ceil(num / den))
  total_blocks = total_units * den
  block_w = width / total_blocks

  svg = f'<svg width="100%" height="{height + 25}" viewBox="0 0 {width} {height + 25}" xmlns="http://www.w3.org/2000/svg">'

  for i in range(total_blocks):
    x = i * block_w
    fill = color if i < num else "#F0F2F6"
    stroke_w = (
        3 if (i % den == 0 and i > 0) else 1
    )  # Thicker line at whole-number boundaries
    stroke_col = "#1E1E1E" if (i % den == 0 and i > 0) else "#FFFFFF"

    svg += f'<rect x="{x}" y="0" width="{block_w}" height="{height}" fill="{fill}" stroke="{stroke_col}" stroke-width="{stroke_w}" rx="3"/>'

    # Add unit fraction text inside blocks if they are wide enough
    if block_w > 28:
      text_col = "white" if i < num else "#555555"
      svg += (
          f'<text x="{x + block_w/2}" y="{height/2 + 5}" font-family="sans-serif"'
          f' font-size="13" font-weight="bold" fill="{text_col}"'
          f' text-anchor="middle">1/{den}</text>'
      )

  # Outer border for each whole
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


# --- APP HEADER & NAVIGATION ---
st.title("🧮 5th Grade Fraction Manipulative Lab")
st.markdown(
    "Explore how fractions work visually using **Fraction Bars** and **Area"
    " Models**."
)

mode = st.sidebar.radio(
    "Choose a Learning Activity:",
    [
        "1. Explore & Equivalent Fractions",
        "2. Compare Two Fractions",
        "3. Add Fractions (Unlike Denominators)",
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
        "Denominator (Total equal parts in 1 whole)",
        min_value=1,
        max_value=12,
        value=4,
    )
    num = st.slider(
        "Numerator (Number of shaded parts)", min_value=0, max_value=den, value=3
    )

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
          "Split each piece into how many smaller pieces?", 1, 4, 2
      )
      eq_num, eq_den = num * multiplier, den * multiplier
      st.markdown(
          draw_fraction_bar(
              eq_num,
              eq_den,
              "#2EC4B6",
              f"{num}/{den} = {eq_num}/{eq_den} (multiplied by"
              f" {multiplier}/{multiplier})",
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
  # Comparison Result
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

  # Toggle to reveal common denominator grid
  if st.checkbox("Show Common Denominator Pieces to Compare"):
    lcm = math.lcm(den_a, den_b)
    new_num_a = num_a * (lcm // den_a)
    new_num_b = num_b * (lcm // den_b)
    st.write(f"Both bars cut into **{lcm}ths**:")
    st.markdown(
        draw_fraction_bar(
            new_num_a, lcm, "#4F8BF9", f"{num_a}/{den_a} = {new_num_a}/{lcm}"
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        draw_fraction_bar(
            new_num_b, lcm, "#FF6B6B", f"{num_b}/{den_b} = {new_num_b}/{lcm}"
        ),
        unsafe_allow_html=True,
    )

# ==========================================
# MODE 3: ADD UNLIKE FRACTIONS
# ==========================================
elif mode == "3. Add Fractions (Unlike Denominators)":
  st.header("➕ Adding Fractions with Unlike Denominators")
  st.write(
      "To add fractions with different-sized pieces, we first cut them into"
      " **same-sized pieces** (a common denominator)."
  )

  col1, col2 = st.columns(2)
  with col1:
    d1 = st.selectbox("First Denominator", [2, 3, 4, 5, 6, 8, 10], index=0)
    n1 = st.slider("First Numerator", 1, d1, 1, key="add_n1")
  with col2:
    d2 = st.selectbox("Second Denominator", [2, 3, 4, 5, 6, 8, 10], index=1)
    n2 = st.slider("Second Numerator", 1, d2, 1, key="add_n2")

  st.subheader("Step 1: Look at the original pieces")
  st.markdown(
      draw_fraction_bar(n1, d1, "#4F8BF9", f"First Fraction: {n1}/{d1}"),
      unsafe_allow_html=True,
  )
  st.markdown(
      draw_fraction_bar(n2, d2, "#FF6B6B", f"Second Fraction: {n2}/{d2}"),
      unsafe_allow_html=True,
  )

  st.subheader("Step 2: Find a Common Denominator")
  lcm = math.lcm(d1, d2)
  eq_n1 = n1 * (lcm // d1)
  eq_n2 = n2 * (lcm // d2)

  st.write(
      f"The smallest common piece size for **{d1}ths** and **{d2}ths** is"
      f" **{lcm}ths**."
  )
  st.markdown(
      draw_fraction_bar(
          eq_n1, lcm, "#4F8BF9", f"{n1}/{d1} becomes {eq_n1}/{lcm}"
      ),
      unsafe_allow_html=True,
  )
  st.markdown(
      draw_fraction_bar(
          eq_n2, lcm, "#FF6B6B", f"{n2}/{d2} becomes {eq_n2}/{lcm}"
      ),
      unsafe_allow_html=True,
  )

  st.subheader("Step 3: Combine the Pieces!")
  total_num = eq_n1 + eq_n2
  st.markdown(
      draw_fraction_bar(
          total_num,
          lcm,
          "#9B5DE5",
          f"Total: {eq_n1}/{lcm} + {eq_n2}/{lcm} = {total_num}/{lcm}",
      ),
      unsafe_allow_html=True,
  )

  # Simplify / Mixed number conversion
  simplified = Fraction(total_num, lcm)
  whole = total_num // lcm
  rem = total_num % lcm

  result_text = f"**Sum:** `{total_num}/{lcm}`"
  if whole > 0 and rem > 0:
    result_text += f"  |  **Mixed Number:** `{whole} and {rem}/{lcm}`"
  elif whole > 0 and rem == 0:
    result_text += f"  |  **Whole Number:** `{whole}`"
  if simplified.denominator != lcm:
    result_text += (
        f"  |  **Simplified:** `{simplified.numerator}/{simplified.denominator}`"
    )

  st.success(result_text)
