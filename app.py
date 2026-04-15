import streamlit as st
import pandas as pd
from collections import Counter
import numpy as np

st.set_page_config(page_title="Super-AI Total Predictor", layout="wide")

st.title("🛡️ Super-AI: Predict + Avoid List")
st.write("🎯 आने वाले + ❌ न आने वाले नंबर")

# Master Configurations
master_patterns = [0, -18, -16, -26, -32, -1, -4, -11, -15, -10, -51, -50, 15, 5, -5, -55, 1, 10, 11, 51, 55, -40]
shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

uploaded_file = st.sidebar.file_uploader("Upload Data File", type=['csv', 'xlsx'])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.sidebar.write(f"📊 Loaded {len(df)} rows")
    
    # Auto-detect shift columns
    available_shifts = [col for col in shifts if col in df.columns]
    
    if not available_shifts:
        st.error("❌ शिफ्ट कॉलम्स नहीं मिले। कृपया `DS`, `FD`, `GD`, `GL`, `DB`, `SG` चेक करें।")
        st.stop()
    
    # Convert to numeric & clean
    for col in available_shifts:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df_clean = df[available_shifts].dropna()
    
    if len(df_clean) < 2:
        st.error("❌ कम से कम 2 दिन का डेटा चाहिए।")
        st.stop()

    today_row = df_clean.iloc[-1]
    yesterday_row = df_clean.iloc[-2] if len(df_clean) > 1 else None
    
    today_nums = {col: int(today_row[col]) for col in available_shifts}
    yesterday_nums = {col: int(yesterday_row[col]) for col in available_shifts} if yesterday_row is not None else {}
    
    # === POSITIVE SCORES (जैसा पहले था) ===
    positive_scores = np.zeros(100)
    
    # A. Master Pattern Score
    for val in today_nums.values():
        for p in master_patterns:
            res = int((val + p) % 100)
            positive_scores[res] += 1

    # B. History Transition (Weight: 3)
    for s_name, s_val in today_nums.items():
        history_hits = df_clean[df_clean[s_name] == s_val].index
        next_vals = []
        for idx in history_hits:
            if idx + 1 < len(df_clean):
                v_next = df_clean.iloc[idx + 1][s_name]
                if not pd.isna(v_next):
                    next_vals.append(int(v_next))
        if next_vals:
            top_next = [n for n, c in Counter(next_vals).most_common(3)]
            for tn in top_next:
                positive_scores[tn] += 3

    # === NEW: NEGATIVE SCORES (AVOID LIST) ===
    negative_scores = np.zeros(100)
    
    # 1. Cold Numbers (बहुत कम आए हों) - Weight: -4
    all_numbers = []
    for col in available_shifts:
        all_numbers.extend(df_clean[col].dropna().astype(int).tolist())
    
    number_freq = Counter(all_numbers)
    for num in range(100):
        freq = number_freq.get(num, 0)
        if freq < 2:  # बहुत कम आए
            negative_scores[num] -= 4

    # 2. Anti-Patterns (जो patterns से दूर हैं) - Weight: -2
    anti_patterns = [25, 33, 42, 67, 88, 99]  # opposite of master patterns
    for val in today_nums.values():
        for ap in anti_patterns:
            res = int((val + ap) % 100)
            negative_scores[res] -= 2

    # 3. Recent Avoid (पिछले 7 दिन में बार-बार न आए) - Weight: -3
    recent_7d = df_clean.tail(7)
    recent_cold = []
    for num in range(100):
        recent_count = 0
        for col in available_shifts:
            recent_count += recent_7d[col].dropna().astype(int).eq(num).sum()
        if recent_count == 0:
            recent_cold.append(num)
    
    for num in recent_cold[:20]:  # Top 20 cold
        negative_scores[num] -= 3

    # 4. Forbidden Zones (pattern clusters से बाहर) - Weight: -1
    hot_zones = [0,1,5,10,11,15,50,51,55]
    for num in range(100):
        if num not in hot_zones:
            negative_scores[num] -= 1

    # === FINAL COMBINED SCORES ===
    final_scores = positive_scores + negative_scores
    
    # === DISPLAY RESULTS ===
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("🎯 आने वाले Top 10")
        predict_results = []
        for num in range(100):
            if final_scores[num] > 0:
                predict_results.append({
                    "Number": f"{num:02d}",
                    "Score": f"+{final_scores[num]:.1f}",
                    "Conf": f"{min(95, final_scores[num]*6):.0f}%"
                })
        
        predict_df = pd.DataFrame(predict_results).sort_values("Score", key=lambda x: x.str.extract('(d+)').astype(float), ascending=False)
        st.dataframe(predict_df.head(10), use_container_width=True)
        
        top_hit = predict_df.iloc[0]['Number'] if len(predict_df) > 0 else "N/A"
        st.markdown(f"""
        <div style='background: linear-gradient(45deg, #4CAF50, #45a049); 
                    color: white; padding: 20px; border-radius: 15px; text-align: center;'>
            <h2>🎯 #1 Prediction: {top_hit}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.header("❌ न आने वाले Top 20")
        avoid_results = []
        for num in range(100):
            if final_scores[num] < -1:
                avoid_results.append({
                    "Number": f"{num:02d}",
                    "Avoid Score": f"{final_scores[num]:.1f}",
                    "Risk": f"{min(95, abs(final_scores[num])*4):.0f}%"
                })
        
        avoid_df = pd.DataFrame(avoid_results).sort_values("Avoid Score")
        st.dataframe(avoid_df.head(20), use_container_width=True)
        
        top_avoid = avoid_df.iloc[0]['Number'] if len(avoid_df) > 0 else "N/A"
        st.markdown(f"""
        <div style='background: linear-gradient(45deg, #f44336, #d32f2f); 
                    color: white; padding: 20px; border-radius: 15px; text-align: center;'>
            <h2>🚫 #1 Avoid: {top_avoid}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📊 Complete Score Heatmap (सभी 100 नंबर)")
    score_df = pd.DataFrame({
        "Number": [f"{i:02d}" for i in range(100)],
        "Final Score": [round(final_scores[i], 1) for i in range(100)]
    }).sort_values("Final Score", ascending=False)
    
    st.dataframe(score_df, use_container_width=True)

else:
    st.info("👈 Sidebar में फ़ाइल अपलोड करें।")
