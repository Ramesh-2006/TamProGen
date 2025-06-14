import json
import pandas as pd
import re
import random

# Load JSON file
with open('proverbs.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
df = pd.DataFrame(data)

# Remove duplicates based on Tamil Proverbs
df = df.drop_duplicates(subset=['Proverb (Tamil)'], keep='first')

# Strip whitespaces from all strings
df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

# Clean Tamil text (keep only Tamil letters and spaces)
def clean_text(text):
    return re.sub(r'[^\u0B80-\u0BFF\s]', '', text).strip()

df['Proverb (Tamil)'] = df['Proverb (Tamil)'].apply(clean_text)

# Normalize transliteration to lowercase
df['Proverb (Transliteration)'] = df['Proverb (Transliteration)'].str.lower()

# Re-drop duplicates (safety)
df = df.drop_duplicates(subset=['Proverb (Tamil)'], keep='first')

# Tokenize Tamil proverbs
df['proverb_tokens'] = df['Proverb (Tamil)'].apply(lambda x: re.findall(r'\S+', x))

# Tamil stopwords (expand if needed)
stopwords = ['உம்', 'என்று', 'தான்', 'இன்', 'ஆக', 'இந்த']
df['proverb_tokens'] = df['proverb_tokens'].apply(lambda x: [word for word in x if word not in stopwords])

# Tamil spelling variation normalization
tamil_variation_dict = {
    "வேண்டாம்": "வேண்டா", "வேணுமா": "வேண்டுமா", "பறந்து": "பற", "பறக்க": "பற",
    "பாடல்": "பாட்டு", "கேட்க": "கேட்ப", "கேட்கின்றது": "கேட்பது", "செல்லும்": "செல்ல",
    "செல்லாது": "செல்லா", "சென்றான்": "சென்ற", "சென்றது": "சென்று", "வந்தான்": "வந்து",
    "வந்தது": "வந்து", "வந்தாயா": "வந்தியா", "பேசும்": "பேச", "பேசாமல்": "பேசாதே",
    "போனான்": "போய்", "போனது": "போய்", "போனாய்": "போயியா", "நடந்தது": "நடந்து",
    "நடந்தான்": "நடந்து", "தெரியாது": "தெரியா", "தெரியும்": "தெரிய",
    "நினைக்கிறது": "நினைக்க", "நினைத்தான்": "நினைத்து", "எதுவும்": "ஒன்றும்",
    "எதற்காக": "எதுக்கு", "உள்ளது": "உள்ள", "உள்ளவன்": "உள்ள", "நல்லது": "நல்ல",
    "மோசமானது": "மோசம்", "கெட்டது": "கெட்ட", "சிறந்தது": "சிறந்த", "பெரியது": "பெரிய",
    "சின்னது": "சின்ன", "அழகு": "அழகான", "மிகவும்": "நெருக்கமான", "உடனே": "உடன்",
    "வாழ்கின்றான்": "வாழ", "வாழ்ந்தான்": "வாழ"
}
def normalize_tamil_word(word):
    return tamil_variation_dict.get(word, word)

df['proverb_tokens'] = df['proverb_tokens'].apply(lambda x: [normalize_tamil_word(word) for word in x])

# Synonym normalization
synonym_dict = {
    "அறிவு": "ஞானம்", "ஞானம்": "அறிவு", "கல்வி": "அறிவு", "தெரிவு": "புத்தி",
    "புத்தி": "தெரிவு", "மதிப்பு": "கௌரவம்", "கௌரவம்": "மதிப்பு",
    "புகழ்": "புகழ்ச்சி", "புகழ்ச்சி": "புகழ்", "கிரியை": "கடமை", "கடமை": "கிரியை",
    "சொத்து": "செல்வம்", "செல்வம்": "சொத்து", "பொருள்": "வளம்", "வளம்": "பொருள்",
    "தினை": "பசுமை", "பசுமை": "தினை", "இன்பம்": "மகிழ்ச்சி", "மகிழ்ச்சி": "இன்பம்",
    "ஆனந்தம்": "மகிழ்ச்சி", "பெருமிதம்": "ஆனந்தம்", "மனம்": "உள்ளம்", "உள்ளம்": "மனம்",
    "சிந்தனை": "யோசனை", "யோசனை": "சிந்தனை", "திறன்": "வல்லமை", "வல்லமை": "திறன்",
    "சக்தி": "ஆற்றல்", "ஆற்றல்": "சக்தி", "வெற்றி": "ஜெயம்", "ஜெயம்": "வெற்றி",
    "வாழ்வு": "உயர்வு", "உயர்வு": "வாழ்வு", "அழகு": "கனிவு", "கனிவு": "அழகு",
    "கண்ணோமி": "அழகு", "சிரிப்பு": "அழகு", "பழி": "நிந்தனை", "நிந்தனை": "பழி",
    "குற்றம்": "பாவம்", "பாவம்": "குற்றம்", "தேவை": "அவசியம்", "அவசியம்": "தேவை",
    "பிடிப்பு": "நோக்கம்", "நோக்கம்": "பிடிப்பு", "நட்பு": "சிநேகம்", "சிநேகம்": "நட்பு",
    "உற்றார்": "உற்றவன்", "உற்றவன்": "உற்றார்", "கண்கள்": "கண்ணு", "கண்ணு": "கண்கள்",
    "விழி": "பார்வை", "பார்வை": "விழி", "நெருப்பு": "அக்னி", "அக்னி": "நெருப்பு",
    "வெப்பம்": "காட்டு", "காட்டு": "வெப்பம்", "பசி": "சோறு", "சோறு": "பசி",
    "உணவு": "அன்னம்", "அன்னம்": "உணவு", "பூனை": "சிறுபுலி", "சிறுபுலி": "பூனை",
    "சிங்கம்": "வானரம்", "வானரம்": "சிங்கம்", "மரம்": "தோப்பு", "தோப்பு": "மரம்",
    "காலம்": "நேரம்", "நேரம்": "காலம்", "வயது": "இளமை", "இளமை": "வயது"
}
def normalize_synonyms(word):
    return synonym_dict.get(word, word)

df['proverb_tokens'] = df['proverb_tokens'].apply(lambda words: [normalize_synonyms(word) for word in words])

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(tokenizer=lambda x: x, lowercase=False)
X_tfidf = vectorizer.fit_transform(df['proverb_tokens'])

# TF-IDF as DataFrame (optional)
tfidf_df = pd.DataFrame(X_tfidf.toarray(), columns=vectorizer.get_feature_names_out())
print("TF-IDF Shape:", tfidf_df.shape)

# Synonym replacement for data augmentation
def replace_with_synonym(proverb):
    words = proverb.split()
    return " ".join([synonym_dict.get(word, word) for word in words])

df['synonym_replaced_proverb'] = df['Proverb (Tamil)'].apply(replace_with_synonym)

# Add character-level typo (noise)
def add_typo(proverb):
    chars = list(proverb)
    if len(chars) > 3:
        idx = random.randint(0, len(chars) - 1)
        chars[idx] = ''  # Remove a character
    return ''.join(chars)

df['noisy_proverb'] = df['Proverb (Tamil)'].apply(add_typo)

# Save to file
df.to_json('preprocessed_tamil_proverbs.json', orient='records', force_ascii=False)

print("✅ Preprocessing completed. File saved as 'preprocessed_tamil_proverbs.json'")
