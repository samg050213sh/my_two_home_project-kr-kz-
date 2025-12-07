"""
Map of Two Homes: Taraz ↔ Seoul
My personal journey from Kazakhstan to Korea

"""

import streamlit as st
import pandas as pd
import plotly.express as px
#import plotly.graph_objects as go
try:
    from wordcloud import WordCloud
    HAS_WORDCLOUD = True
except Exception:
    HAS_WORDCLOUD = False
import matplotlib.pyplot as plt
import json
#import os
#import numpy as np
#i markered the places because of errors in loading some libraries on streamlit cloud


# PAGE SETUP

st.set_page_config(
    page_title="My Two Homes: Taraz & Seoul",
    page_icon="🏠",
    layout="wide"
)


# LOAD DATA

@st.cache_data
def load_dishes():
    return pd.read_csv('data/dishes.csv')

@st.cache_data  
def load_words():
    return pd.read_csv('data/words.csv')

@st.cache_data
def load_memories():
    with open('data/memories.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('memories', [])


dishes_df = load_dishes()
words_df = load_words()
memories_list = load_memories()


# SIDEBAR - NAVIGATION

st.sidebar.title("🌍 Navigation")
page = st.sidebar.radio(
    "Choose Section:",
    ["🏠 Home", "🍽 Food Journey", "🗣 Language Map", "📖 My Memories", "📊 My Stats"]
)

# Sidebar

st.sidebar.markdown("---")
st.sidebar.markdown("**Quick Stats:**")
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Dishes", len(dishes_df))
with col2:
    st.metric("Memories", len(memories_list))


# PAGE 1: HOME

if page == "🏠 Home":
    st.title("🏠 My Two Homes: Taraz & Seoul")
    st.markdown("### My Cultural Journey: 2022-2025")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🇰🇿 Taraz, Kazakhstan")
        st.markdown("""
        - My hometown where I grew up
        - Left at 17 years old in 2022  
        - Memories: family, school, childhood friends
        - What I miss: hospitality, wide spaces, home food
        """)
    
    with col2:
        st.subheader("🇰🇷 Seoul, Korea")  
        st.markdown("""
        - My new home since 2022
        - Current: SeoulTech University student
        - Studying: Computer Science
        - What I gained: independence, new perspectives
        """)
    
    # Map
    st.markdown("### 🗺️ My Journey Map")
    
    map_data = pd.DataFrame({
        'lat': [42.9, 37.5665],
        'lon': [71.3667, 126.9780],
        'city': ['Taraz', 'Seoul'],
        'country': ['Kazakhstan', 'Korea'],
        'size': [20, 20]
    })
    
    fig = px.scatter_geo(map_data,
                        lat='lat',
                        lon='lon',
                        hover_name='city',
                        size='size',
                        projection='natural earth',
                        title='From Taraz to Seoul: My Path')
    
    fig.update_traces(marker=dict(color=['#00A86B', '#CD2E3A']))
    st.plotly_chart(fig, use_container_width=True)


# PAGE 2: FOOD JOURNEY  

elif page == "🍽 Food Journey":
    st.title("🍽 My Food Journey")
    st.markdown("### From Taraz Kitchen to Seoul Street Food")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        country = st.selectbox("Country", ["All"] + list(dishes_df['country'].unique()))
    with col2:
        sort_by = st.selectbox("Sort by", ["Nostalgia", "Frequency", "Name"])
    
    # Filter data
    filtered_dishes = dishes_df.copy()
    if country != "All":
        filtered_dishes = filtered_dishes[filtered_dishes['country'] == country]
    
    # Sort
    if sort_by == "Nostalgia":
        filtered_dishes = filtered_dishes.sort_values('nostalgia_index', ascending=False)
    elif sort_by == "Frequency":
        filtered_dishes = filtered_dishes.sort_values('frequency', ascending=False)
    else:
        filtered_dishes = filtered_dishes.sort_values('name')
    
    # Visualization
    fig = px.scatter(filtered_dishes,
                    x='frequency',
                    y='nostalgia_index',
                    size='ingredients_difficulty',
                    color='country',
                    hover_name='name',
                    hover_data=['story'],
                    color_discrete_map={'Kazakhstan': '#00A86B', 'Korea': '#CD2E3A'},
                    title='Food Nostalgia vs Frequency')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Dishes list WITH PHOTOS
    st.markdown("### 🍜 My Food Gallery")
    
    has_photos = 'image_path' in dishes_df.columns or 'image' in dishes_df.columns
    photo_column = 'image_path' if 'image_path' in dishes_df.columns else 'image'
    
    if has_photos:
        st.info(f" finded {photo_column}")
 
    dishes_list = filtered_dishes.to_dict('records')
    
    for i in range(0, len(dishes_list), 2): #columns of 2
        cols = st.columns(2)
        
        for j in range(2):
            if i + j < len(dishes_list):
                dish = dishes_list[i + j]
                with cols[j]:
                    with st.container():
                        country_flag = "🇰🇿" if dish['country'] == 'Kazakhstan' else "🇰🇷"

                        st.markdown(f"#### {country_flag} {dish['name']}")
                        
                        # fhoto
                        if has_photos and photo_column in dish and pd.notna(dish[photo_column]):
                            photo_file = dish[photo_column]
                            try:
                                if isinstance(photo_file, str):
                                    photo_file = photo_file.strip()
                                    if ',' in photo_file:
                                        photo_file = photo_file.split(',')[0]
                                    
                                    st.image(f"images/{photo_file}",
                                            caption=dish['name'],
                                            use_container_width=True)
                            except Exception as e:
                                st.warning(f"Could not load: {photo_file}")
                                st.info(f"Ошибка: {e}")

                        col_metrics1, col_metrics2 = st.columns(2)
                        with col_metrics1:
                            nostalgia = dish['nostalgia_index']
                            color = "green" if nostalgia >= 8 else "orange" if nostalgia >= 5 else "red"
                            st.markdown(f"<span style='color:{color};'>Nostalgia: **{nostalgia}/10**</span>", 
                                      unsafe_allow_html=True)
                        
                        with col_metrics2:
                            frequency = dish['frequency']
                            stars = "⭐" * min(frequency, 5)
                            st.markdown(f"Frequency: **{stars}**")
                        
                        # Story expander
                        with st.expander("📖 Read Story & Details"):
                            st.write(dish['story'])
                            st.markdown(f"**Difficulty:** {dish['ingredients_difficulty']}/10")


# PAGE 3: LANGUAGE MAP

elif page == "🗣 Language Map":
    st.title("🗣 My Language Journey")
    
    # Word clouds
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🇰🇿 Kazakh Words")
        kazakh_words = ' '.join(words_df[words_df['language'] == 'Kazakh']['word'].tolist() * 3)
        if kazakh_words:
            wordcloud = WordCloud(width=400, height=300, background_color='white').generate(kazakh_words)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
    
    with col2:
        st.subheader("🇰🇷 Korean Words")
        korean_words = ' '.join(words_df[words_df['language'] == 'Korean']['word'].tolist() * 3)
        if korean_words:
            wordcloud = WordCloud(width=400, height=300, background_color='white').generate(korean_words)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
    
    # Words list
    st.markdown("### Meaningful Words")
    for _, word in words_df.iterrows():
        with st.expander(f"{word['word']} ({word['language']}) - {word['meaning']}"):
            st.write(f"**Emotional weight:** {word['emotional_weight']}/10")
            st.write(f"**Year:** {word['year_learned']}")
            st.write(f"**Story:** {word['context']}")


# PAGE 4: MEMORIES

elif page == "📖 My Memories":
    st.title("📖 My Memory Book")

    col1, col2 = st.columns(2)
    with col1:
        year_filter = st.selectbox("Year", ["All"] + sorted(set(m['date'][:4] for m in memories_list), reverse=True))
    with col2:
        emotion_filter = st.selectbox("Emotion", ["All"] + sorted(set(m['emotion'] for m in memories_list)))

    filtered_memories = memories_list.copy()
    if year_filter != "All":
        filtered_memories = [m for m in filtered_memories if m['date'].startswith(year_filter)]
    if emotion_filter != "All":
        filtered_memories = [m for m in filtered_memories if m['emotion'] == emotion_filter]
    
    
    for memory in filtered_memories:
        with st.container():
            st.subheader(f"📝 {memory['title']}")
            st.caption(f"📅 {memory['date']} | 📍 {memory['location']} | 🇰🇿🇰🇷 {memory['country']}")

            if 'image_path' in memory and memory['image_path']:
                try:
                    img_path = memory['image_path']
                    
                    #check if file exists because code at starts gives errors
                    import os
                    if os.path.exists(img_path):
                        st.image(img_path, 
                                 caption=memory.get('title', 'Memory'),
                                 width=400)
                    else:
                        alt_path = f"images/{os.path.basename(img_path)}"
                        if os.path.exists(alt_path):
                            st.image(alt_path,
                                    caption=memory.get('title', 'Memory'),
                                    width=400)
                        else:
                            st.warning(f"Image not found: {img_path}")
                            st.info(f"📷 Photo: {os.path.basename(img_path)}")
                except Exception as e:
                    st.error(f"Error loading image: {e}")
            else:
                st.info("📷 No photo for this memory")

            st.write(memory['story'])

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Emotion:** {memory['emotion']}")
            with col2:
                tags_html = " ".join([f"`{tag}`" for tag in memory['tags']])
                st.markdown(f"**Tags:** {tags_html}")
            
            st.divider()


# PAGE 5: STATS

else:
    st.title("📊 My Journey Stats")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Items", len(dishes_df) + len(words_df) + len(memories_list))
    with col2:
        st.metric("Kazakhstan Items", len(dishes_df[dishes_df['country'] == 'Kazakhstan']) +len([w for w in words_df['language'] if w == 'Kazakh']))
    with col3:
        st.metric("Korea Items", len(dishes_df[dishes_df['country'] == 'Korea']) + 
                 len([w for w in words_df['language'] if w == 'Korean']))
    with col4:
        st.metric("Memories", len(memories_list))

    if memories_list:
        emotions = [m['emotion'] for m in memories_list]
        emotion_counts = pd.Series(emotions).value_counts()
        
        fig = px.pie(values=emotion_counts.values,
                    names=emotion_counts.index,
                    title='Emotions in My Memories')
        st.plotly_chart(fig, use_container_width=True)


# FOOTER

st.markdown("---")
st.caption("Created with ❤️ from Taraz to Seoul | Shynaiym's personal cultural journey project")