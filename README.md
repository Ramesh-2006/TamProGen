# 📜 Tamil Proverbs Exploration Dashboard

Welcome to the **Tamil Proverbs Visualizer**, a Streamlit-powered dashboard for exploring the depth, diversity, and beauty of Tamil proverbs! This tool lets you visualize, filter, and search proverbs based on their type, content, and frequency of usage.

---

## 🌟 Features

- 📂 View the complete dataset of Tamil proverbs
- 🌀 Pie chart showing the spread of Figurative vs Literal proverbs
- 🔠 Bar chart of the top 10 most common Tamil words used in proverbs
- 🎯 Sidebar filter to choose between All / Literal / Figurative
- 🔍 Keyword-based search for Tamil proverbs
- ✨ Proverb generator from a given keyword

---

## 🧠 Technologies Used

- **Python**
- **Streamlit** – for creating interactive dashboards
- **Pandas** – for data manipulation
- **Plotly Express** – for plotting pie and bar charts
- **Collections.Counter** – to get most common words

---

## 📁 File Structure

tamil-proverbs-dashboard/
├── app.py # Main Streamlit dashboard script
├── preprocessing.py # Script to clean and tokenize proverbs
├── preprocessed_tamil_proverbs.json # Preprocessed dataset
├── requirements.txt # Required packages
└── README.md # Project overview


##  📊 Sample Visualizations

A pie chart showing the Literal vs Figurative proverb distribution.

A bar chart showing the Top 10 most frequent Tamil words across proverbs.


##  🗂️ Dataset
The dataset is a curated and cleaned JSON file named preprocessed_tamil_proverbs.json, containing:

Proverb (Tamil)

Proverb (Transliteration)

Meaning (Tamil)

Meaning (English)

Example Usage (Tamil)

Example Usage (English)

Literal/Figurative

proverb_tokens (used for frequency analysis)

## ✨ Sample Use Case
Want to find a proverb that matches the keyword “அறம்”? Just enter it, and the dashboard will find the best match and show its meaning and example usage!

## 🙌 Credits
Crafted with 💚 by Ramesh M., a passionate Tamil speaker, poet, and aspiring data scientist, who dreams of blending ancient wisdom with modern tools.

## 📧 Contact
Have feedback or want to collaborate?

📮 Email: ramesh.m.j.2006@gmail.com