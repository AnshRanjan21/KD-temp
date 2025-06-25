import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ===== Agent Functions =====
def load_daylight_data(df):
    df.columns = df.columns.str.strip().str.lower()
    return df[['time', 'lux']]

def evaluate_brightness(lux):
    if lux > 500:
        return 10
    elif lux > 300:
        return 40
    else:
        return 80

def calculate_energy_kwh(brightness_percent, hours=1, watt=40):
    return round((brightness_percent / 100) * watt * hours / 1000, 4)

def calculate_cost(kwh, rate=0.15):
    return round(kwh * rate, 4)

def call_groq_scheduler(dataframe, groq_api_key):
    prompts = [
        f"Time: {row['time']}, Daylight: {row['lux']} lux, Brightness: {row['brightness']}%"
        for _, row in dataframe.iterrows()
    ]
    full_prompt = (
        "You are an intelligent office lighting assistant. Based on the data below, "
        "generate a natural-language schedule describing when and why lights change brightness:\n\n"
        + "\n".join(prompts)
        + "\n\nFormat:\nHour: Brightness % - Reason"
    )

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": full_prompt}],
            "temperature": 0.3,
        },
    )
    try:
        output = response.json()
        return output['choices'][0]['message']['content'] if 'choices' in output else "⚠️ GROQ did not return a valid response."
    except Exception as e:
        return f"❌ GROQ request failed: {e}"

def get_nearest_time_brightness(df):
    try:
        now = datetime.now().replace(second=0, microsecond=0)
        df['parsed_time'] = pd.to_datetime(df['time'], format="%H:%M", errors='coerce').dt.time
        df = df.dropna(subset=['parsed_time'])
        df['datetime_obj'] = df['parsed_time'].apply(lambda t: datetime.combine(now.date(), t))
        df['time_diff'] = df['datetime_obj'].apply(lambda t: abs((now - t).total_seconds()))
        nearest_row = df.loc[df['time_diff'].idxmin()]
        return nearest_row['time'], nearest_row['brightness']
    except Exception:
        return None, None

# ===== Main UI =====
def main():
    st.set_page_config(page_title="💡 Smart Office Light Dashboard", layout="wide")

    st.markdown("""
        <style>
            body { background-color: #F6FBF9; }
            h1 { color: #2E8B57; font-size: 2.5rem; }
            .big-font { font-size: 1.2rem !important; }
            .stTextInput, .stFileUploader, .stNumberInput { border-radius: 10px !important; }
            .metric { font-size: 1.3rem !important; font-weight: 600; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>💡 Smart Office Light Automator</h1>", unsafe_allow_html=True)

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2933/2933245.png", width=90)
        st.markdown("### 📥 Upload CSV & API Key")
        uploaded_file = st.file_uploader("Upload Daylight Data (CSV)", type=["csv"])
        groq_api_key = st.text_input("Enter your GROQ API Key", type="password")
        st.info("📄 Format: `time` and `lux` (e.g., 06:00, 200)", icon="ℹ️")
        st.markdown("---")
        st.caption("⚙️ Designed for Smart Lighting Optimization")

    if not uploaded_file or not groq_api_key:
        st.markdown("### 🚀 Welcome!")
        st.markdown("""
        This assistant automates **office lighting** based on **real-time daylight** to improve **efficiency** and lower **energy costs**.

        **To begin:**
        1. 📤 Upload your daylight sensor data (CSV)
        2. 🔐 Enter your GROQ API key

        👇 Dashboard will unlock once inputs are valid.
        """)
        return

    # ===== Main Logic After Input =====
    df = pd.read_csv(uploaded_file)
    df = load_daylight_data(df)
    df['brightness'] = df['lux'].apply(evaluate_brightness)
    df['energy_kwh'] = df['brightness'].apply(calculate_energy_kwh)
    df['cost'] = df['energy_kwh'].apply(calculate_cost)

    time_match, brightness_match = get_nearest_time_brightness(df)

    st.markdown("### 🕒 Current Lighting Status")
    col_input, col_time = st.columns([1, 3])
    with col_input:
        manual_input = st.number_input("💡 Brightness Override [%] (Optional)", min_value=0, max_value=100, step=10)

    with col_time:
        if manual_input != 0:
            st.info(f"Manual override active ➜ Brightness set to **{manual_input}%**")
        elif time_match:
            st.success(f"Auto-set ➜ Time: **{time_match}** | Brightness: **{brightness_match}%** (Now: {datetime.now().strftime('%H:%M')})")
        else:
            st.error("⛔ Could not match brightness with current time.")

    col1, col2, col3 = st.columns(3)
    col1.metric("🔁 Adjustments", f"{len(df)} readings")
    col2.metric("⚡ Energy Used", f"{df['energy_kwh'].sum():.4f} kWh")
    col3.metric("💸 Total Cost", f"${df['cost'].sum():.4f}")

    st.markdown("### 📊 Data Overview")
    st.dataframe(df.style.background_gradient(cmap='Greens'), use_container_width=True)

    with st.expander("📅 Smart Schedule from GROQ"):
        with st.spinner("🔄 Generating schedule..."):
            schedule = call_groq_scheduler(df, groq_api_key)

        # Beautify the schedule display
        def format_schedule(text):
            # Split lines, assuming each line format: "Hour: Brightness % - Reason"
            lines = text.split('\n')
            formatted_lines = []
            for line in lines:
                if ":" in line and "-" in line:
                    hour_part = line.split(":")[0].strip()
                    rest = line[len(hour_part)+1:].strip()
                    brightness_part = rest.split("-")[0].strip()
                    reason_part = rest[len(brightness_part)+1:].strip()
                    formatted_line = (
                        f"<p style='font-family: monospace; font-size: 1rem; margin: 4px 0;'>"
                        f"<span style='color:#2E8B57; font-weight: 700;'>{hour_part}:</span> "
                        f"<span style='color:#FFA500; font-weight: 600;'>{brightness_part}</span> - "
                        f"<span style='color:#555;'>{reason_part}</span>"
                        f"</p>"
                    )
                    formatted_lines.append(formatted_line)
                else:
                    # Just plain text lines or errors
                    formatted_lines.append(f"<p style='color:#d9534f; font-style: italic;'>{line}</p>")
            return "".join(formatted_lines)

        st.markdown(
            f"""
            <div style="
                background: #f0fdf4;
                border: 2px solid #2E8B57;
                border-radius: 12px;
                padding: 15px 20px;
                max-height: 400px;
                overflow-y: auto;
                box-shadow: 0 4px 10px rgba(46, 139, 87, 0.2);
            ">
                {format_schedule(schedule)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption("Made with ❤️ by Killing Data ⚡ (Sarthak, Ansh, Akash)")

if __name__ == "__main__":
    main()
