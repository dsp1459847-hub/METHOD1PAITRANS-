import streamlit as st

st.set_page_config(page_title="Satta Pattern Predictor", layout="wide")

st.title("🎰 Master Pattern Prediction Tool")
st.write("आज के नंबर डालें और अगले 24-48 घंटों की भविष्यवाणी पाएं।")

# मास्टर पैटर्न लिस्ट
day1_patterns = [-16, 0, -4, -11, -32, -40]
day2_patterns = [0, -18, -26, -1, 15]
all_patterns = [0, -18, -16, -26, -32, -1, -4, -11, -15, -10, -51, -50, 15, 5, -5, -55, 1, 10, 11, 51, 55, -40]

# इनपुट सेक्शन
st.sidebar.header("आज के नंबर (Input)")
inputs = {}
shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']
for shift in shifts:
    inputs[shift] = st.sidebar.number_input(f"{shift} का नंबर", min_value=0, max_value=99, value=0)

if st.sidebar.button("Predict Numbers"):
    col1, col2 = st.columns(2)
    
    base_numbers = [v for v in inputs.values() if v >= 0]
    
    with col1:
        st.header("📅 Day 1 (Next 24h)")
        preds_d1 = []
        for n in base_numbers:
            for p in day1_patterns:
                preds_d1.append((n + p) % 100)
        
        unique_d1 = sorted(list(set(preds_d1)))
        st.success(f"संभावित नंबर: {', '.join(map(str, unique_d1))}")
        
        # High Confidence
        counts = {x: preds_d1.count(x) for x in unique_d1}
        high_conf = [num for num, count in counts.items() if count > 1]
        st.warning(f"🔥 High Confidence: {', '.join(map(str, high_conf))}")

    with col2:
        st.header("📅 Day 2 (Next 48h)")
        preds_d2 = []
        for n in base_numbers:
            for p in day2_patterns:
                preds_d2.append((n + p) % 100)
        
        unique_d2 = sorted(list(set(preds_d2)))
        st.info(f"संभावित नंबर: {', '.join(map(str, unique_d2))}")
        
        counts_d2 = {x: preds_d2.count(x) for x in unique_d2}
        high_conf_d2 = [num for num, count in counts_d2.items() if count > 1]
        st.error(f"🔥 High Confidence: {', '.join(map(str, high_conf_d2))}")

    st.divider()
    st.header("📊 All Pattern Results (Full Table)")
    full_data = []
    for shift, val in inputs.items():
        row = {"Shift": shift, "Today": val}
        for p in all_patterns:
            row[f"P({p})"] = (val + p) % 100
        full_data.append(row)
    st.dataframe(full_data)

st.write("---")
st.caption("नोट: यह टूल केवल डेटा विश्लेषण पर आधारित है।")
      
