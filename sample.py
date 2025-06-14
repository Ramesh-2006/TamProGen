# --[1] IMPORTS & SETUP --
import pandas as pd
import os
from dotenv import load_dotenv  
from groq import Groq 
import speech_recognition as sr
from collections import Counter 
from fuzzywuzzy import fuzz  # or use rapidfuzz for better performance

# --[2] LOAD DATA & API KEY --
load_dotenv()
GROQ_API_KEY = os.getenv("API_KEY")
client = Groq(api_key=GROQ_API_KEY)
data = pd.read_json('preprocessed_tamil_proverbs.json')

# --[3] VOICE INPUT FUNCTION --
def get_voice_input():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    print("🎙️ Speak your Tamil proverb...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        transcription = recognizer.recognize_google(audio, language="ta-IN")
        print(f"✅ Transcription: {transcription}")
        return transcription
    except sr.UnknownValueError:
        print("⚠️ Could not understand the audio.")
    except sr.RequestError:
        print("⚠️ API request error.")
    return ""

# --[4] FUZZY MATCHING FUNCTION --
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

    return best_match if best_score >= 70 else None

# --[5] AI-BASED EXPLANATION FUNCTION --
def generate_explanation(proverb_text):
    prompt = f"""You are a Tamil language expert. Explain the following Tamil proverb in detail.

Tamil Proverb: {proverb_text}

Provide your response in this format:
1. Transliteration
2. Meaning in Tamil(Full text must be in Tamil and briefly explain the meaning and it must be exact meaning of the proverb)
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

# --[6] FILTER FUNCTION --
def filter_proverbs(figurative_type="All", keyword=""):
    filtered_data = data

    if figurative_type != "All":
        filtered_data = filtered_data[filtered_data['Literal/Figurative'].str.lower() == figurative_type.lower()]

    if keyword.strip():
        mask = (
            filtered_data['Proverb (Tamil)'].str.contains(keyword, case=False, na=False) |
            filtered_data['Proverb (Transliteration)'].str.contains(keyword, case=False, na=False)
        )
        filtered_data = filtered_data[mask]

    return filtered_data

# --[7] MAIN CLI MENU --
def main():
    print("\n📜 Welcome to TamProGen — Tamil Proverb Generator & Analyzer\n")
    while True:
        print("\nChoose an option:")
        print("1. Type a Tamil proverb")
        print("2. Speak a Tamil proverb")
        print("3. Filter Proverbs")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            user_input = input("🔤 Enter a Tamil proverb or transliteration: ").strip()
            process_input(user_input)

        elif choice == "2":
            voice_input = get_voice_input()
            if voice_input:
                process_input(voice_input)

        elif choice == "3":
            figurative_type = input("🌀 Filter by type (All, Literal, Figurative): ").strip().capitalize()
            keyword = input("🔍 Enter keyword to search: ").strip()
            results = filter_proverbs(figurative_type, keyword)
            if not results.empty:
                print("\n✅ Matching Proverbs:")
                print(results[['Proverb (Tamil)', 'Meaning (English)', 'Literal/Figurative']])
            else:
                print("❌ No matching proverbs found.")

        elif choice == "4":
            print("👋 Exiting TamProGen. Vaazhga Tamil!")
            break
        else:
            print("⚠️ Invalid choice. Try again.")

# --[8] PROCESS INPUT (TYPED or VOICE) --
def process_input(user_input):
    print(f"🔍 You searched for: {user_input}")
    matched = search_proverb(user_input)

    if matched is not None:
        print("\n✅ Found in dataset!")
        print(f"📜 Proverb (Tamil): {matched['Proverb (Tamil)']}")
        print(f"🔡 Transliteration: {matched['Proverb (Transliteration)']}")
        print(f"📝 Meaning (Tamil): {matched['Meaning (Tamil)']}")
        print(f"🌍 Meaning (English): {matched['Meaning (English)']}")
        print(f"💬 Example Usage (Tamil): {matched['Example Usage (Tamil)']}")
        print(f"📘 Example Usage (English): {matched['Example Usage (English)']}")
        print(f"🎭 Type: {matched['Literal/Figurative']}")
    else:
        print("⚡ Not found in dataset. Generating explanation with AI...")
        explanation = generate_explanation(user_input)
        print("\n🔮 Generated Explanation\n")
        print(explanation)

# --[9] RUN --
if __name__ == "__main__":
    main()
