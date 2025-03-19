import streamlit as st
import sqlite3
import cv2
import os
from pytube import YouTube

# Database setup
def init_db():
    conn = sqlite3.connect("football_stats.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            stats TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    return conn

# Login system
def login(username, password):
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return c.fetchone()

# Register new user
def register(username, password):
    conn = init_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Analyze video
def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    duration = total_frames / fps

    # Placeholder stats
    stats = {
        "duration": duration,
        "total_frames": total_frames,
        "fps": fps,
        "possession": {"team_a": 50, "team_b": 50},
        "shots": {"team_a": 10, "team_b": 8},
        "passes": {"team_a": 300, "team_b": 280},
        "corners": {"team_a": 5, "team_b": 3},
        "fouls": {"team_a": 12, "team_b": 10},
        "offsides": {"team_a": 2, "team_b": 1},
        "cards": {"yellow": {"team_a": 2, "team_b": 1}, "red": {"team_a": 0, "team_b": 0}},
    }

    cap.release()
    os.remove(video_path)  # Delete video to save space
    return stats

# Streamlit app
def main():
    st.title("Football Match Analyzer")
    st.sidebar.title("Menu")
    menu = ["HOME", "OVERVIEW", "SETTINGS", "STATS", "VIDEOS"]
    choice = st.sidebar.selectbox("Select Option", menu)

    if choice == "HOME":
        st.write("Welcome to the Football Match Analyzer!")
        st.write("Upload a video or provide a link to analyze.")

        youtube_url = st.text_input("Enter YouTube Link")
        uploaded_file = st.file_uploader("Or upload a video", type=["mp4"])

        if st.button("Analyze"):
            if youtube_url:
                try:
                    yt = YouTube(youtube_url)
                    video = yt.streams.filter(file_extension="mp4").first()
                    video_path = video.download()
                except Exception as e:
                    st.error(f"Error: {e}")
            elif uploaded_file:
                video_path = "uploaded_video.mp4"
                with open(video_path, "wb") as f:
                    f.write(uploaded_file.read())
            else:
                st.error("Please provide a video link or upload a file.")

            stats = analyze_video(video_path)
            st.write("Analysis Results:")
            st.json(stats)

    elif choice == "STATS":
        st.write("Match Statistics")
        # Fetch and display stats from the database
