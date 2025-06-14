# --[1] IMPORTS & SETUP --
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv  
from groq import Groq 
import speech_recognition as sr
import plotly.express as px 
from collections import Counter 
from fuzzywuzzy import fuzz  # or use rapidfuzz for better performance

# --[2] PAGE CONFIG --
st.set_page_config(
    page_title="TamProGen — Tamil Proverb Generator & Analyzer",
    layout="wide",
    page_icon="📜"
)

# --[3] LOAD DATA & API KEY --
load_dotenv()
GROQ_API_KEY = os.getenv("API_KEY")
client = Groq(api_key=GROQ_API_KEY)

data = pd.read_json('preprocessed_tamil_proverbs.json')

# --[4] VOICE INPUT FUNCTION --
def get_voice_input():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("🎙️ Speak your Tamil proverb...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        transcription = recognizer.recognize_google(audio, language="ta-IN")
        st.success(f"✅ Transcription: {transcription}")
        return transcription
    except sr.UnknownValueError:
        st.error("⚠️ Could not understand the audio.")
    except sr.RequestError:
        st.error("⚠️ API request error.")
    return ""

# --[5] FUZZY MATCHING FUNCTION --
def search_proverb(user_input):
    best_score = 0
    best_match = None

    for _, row in data.iterrows():
        tamil_score = fuzz.partial_ratio(user_input.lower(), row['Proverb (Tamil)'].lower())
        translit_score = fuzz.partial_ratio(user_input.lower(), row['Proverb (Transliteration)'].lower())
        score = max(tamil_score, translit_score)

        if score > best_score:
            best_score = score
            best_match = row

    return best_match if best_score >= 70 else None  # adjust threshold as needed

# --[6] AI-BASED EXPLANATION FUNCTION --
def generate_explanation(proverb_text):
    prompt = f"""You are a Tamil language expert. Explain the following Tamil proverb in detail.

Tamil Proverb: {proverb_text}

Provide your response in this format:
1. Transliteration
2. Meaning in Tamil(Full text must be in Tamil and briefly explain the meaning)
3. Meaning in English
4. Example Usage in Tamil
5. Example Usage in English
6. Literal or Figurative (choose and explain briefly)"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# --[7] APP TITLE --
st.markdown("""
<div style='text-align:center; font-family: Georgia, serif; font-size: 3rem; color: #6B4226;'>
    📜 <strong>TamProGen</strong> — Tamil Proverb Generator & Analyzer
</div>
<hr style='border: 1px solid #D2B48C; margin-bottom: 30px;'>
""", unsafe_allow_html=True)

# --[8] SIDEBAR NAVIGATION --
st.sidebar.title("Navigate TamProGen")
app_mode = st.sidebar.radio("Choose Section", ["Proverb Generator", "Filter Proverbs", "Visual Explorer"])

# --[9] PROVERB GENERATOR --
if app_mode == "Proverb Generator":
    st.header("Proverb Generator")

    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input("Enter a Tamil proverb or transliteration:", label_visibility="collapsed", key="proverb_input")

    with col2:
        if st.button("🎙️", help="Speak your proverb out loud"):
            voice_input = get_voice_input()
            if voice_input:
                st.info(f"🎧 You said: **{voice_input}**")
                user_input = voice_input

    if user_input:
        st.write(f"🔍 You searched for: **{user_input}**")
        matched = search_proverb(user_input)

        if matched is not None:
            st.success("✅ Found in dataset!")
            st.markdown(f"**📜 Proverb (Tamil):** {matched['Proverb (Tamil)']}")
            st.markdown(f"**🔡 Transliteration:** {matched['Proverb (Transliteration)']}")
            st.markdown(f"**📝 Meaning (Tamil):** {matched['Meaning (Tamil)']}")
            st.markdown(f"**🌍 Meaning (English):** {matched['Meaning (English)']}")
            st.markdown(f"**💬 Example Usage (Tamil):** {matched['Example Usage (Tamil)']}")
            st.markdown(f"**📘 Example Usage (English):** {matched['Example Usage (English)']}")
            st.markdown(f"**🎭 Type:** {matched['Literal/Figurative']}")

            # ✅ NEW: Button to Generate AI Explanation (even if found)
            if st.button("🪄 Generate AI Explanation"):
                explanation = generate_explanation(user_input)
                st.markdown("### 🔮 Generated Explanation")
                st.markdown(explanation)

        else:
            st.warning("⚡ Not found in dataset. Generating explanation with AI...")
            explanation = generate_explanation(user_input)
            st.markdown("### 🔮 Generated Explanation")
            st.markdown(explanation)

# --[10] VISUAL EXPLORER --
elif app_mode == "Visual Explorer":
    st.header("Tamil Proverbs – Visual Analysis")

    with st.expander("View Full Dataset"):
        st.dataframe(data)

    fig_pie = px.pie(
        data_frame=data,
        names='Literal/Figurative',
        title='Distribution of Figurative vs Literal Proverbs',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    all_tokens = [token for sublist in data['proverb_tokens'] for token in sublist]
    token_counts = Counter(all_tokens)
    top_tokens = dict(token_counts.most_common(10))

    fig_bar = px.bar(
        x=list(top_tokens.keys()),
        y=list(top_tokens.values()),
        labels={'x': 'Word', 'y': 'Frequency'},
        title="Top 10 Most Frequent Words in Proverbs",
        color=list(top_tokens.values()),
        color_continuous_scale='blues'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --[11] FILTER PROVERBS --
elif app_mode == "Filter Proverbs":
    st.header("Filter Proverbs")

    figurative_filter = st.selectbox("Choose Type", ["All", "Literal", "Figurative"])
    keyword = st.text_input("Enter keyword to filter proverbs:")

    if st.button("🔘 Apply Filter"):
        filtered_data = data

        if figurative_filter != "All":
            filtered_data = filtered_data[filtered_data['Literal/Figurative'].str.lower() == figurative_filter.lower()]

        if keyword.strip():
            mask = (
                filtered_data['Proverb (Tamil)'].str.contains(keyword, case=False, na=False) |
                filtered_data['Proverb (Transliteration)'].str.contains(keyword, case=False, na=False)
            )
            filtered_data = filtered_data[mask]

        if not filtered_data.empty:
            st.markdown(f"### Proverbs Filtered by: Type = {figurative_filter}, Keyword = '{keyword}'")
            st.dataframe(filtered_data[['Proverb (Tamil)', 'Meaning (English)', 'Literal/Figurative']])
        else:
            st.warning("No matching proverbs found.")
