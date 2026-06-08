# pip install streamlit python-dotenv langchain-groq pdfplumber streamlit-mic-recorder SpeechRecognition pydub

import os
import io
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import pdfplumber
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from pydub import AudioSegment

load_dotenv()

st.set_page_config(
    page_title="Mock Interview Bot",
    page_icon="🎯",
    layout="centered"
)

st.title("🎯 Mock Interview Bot")
st.write("Upload your resume and practice your interview!")

st.divider()

# ── SESSION STATE ──────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "target_role" not in st.session_state:
    st.session_state.target_role = ""

if "experience_level" not in st.session_state:
    st.session_state.experience_level = ""

if "bot_should_greet" not in st.session_state:
    st.session_state.bot_should_greet = False

if "end_interview" not in st.session_state:
    st.session_state.end_interview = False

if "mic_key" not in st.session_state:
    st.session_state.mic_key = 0

# ── SIDEBAR ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📄 Setup Your Interview")

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    target_role = st.text_input("Target Role", placeholder="e.g. Data Analyst, AI Engineer")

    experience_level = st.selectbox(
        "Experience Level",
        ["Fresher", "1-3 years", "3+ years"]
    )

    start_button = st.button("Start Interview 🚀")

    if start_button:
        if not uploaded_file:
            st.warning("Please upload your resume first!")
        elif not target_role:
            st.warning("Please enter your target role!")
        else:
            with pdfplumber.open(uploaded_file) as pdf:
                resume_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        resume_text += text

            st.session_state.resume_text = resume_text
            st.session_state.target_role = target_role
            st.session_state.experience_level = experience_level
            st.session_state.interview_started = True
            st.session_state.chat_history = []
            st.session_state.bot_should_greet = True
            st.session_state.end_interview = False
            st.rerun()

    if st.session_state.interview_started:
        st.divider()
        end_button = st.button("🛑 End Interview & Get Report")
        if end_button:
            st.session_state.chat_history.append({
                "role": "user",
                "content": "End the interview now and give me the full detailed report."
            })
            st.session_state.end_interview = True
            st.rerun()

# ── SYSTEM PROMPT ──────────────────────────────────────────────────
def build_system_prompt():
    return f"""
You are an elite AI Interview Coach and Career Mentor conducting a realistic mock interview.

Candidate Profile:
- Resume: {st.session_state.resume_text}
- Target Role: {st.session_state.target_role}
- Experience Level: {st.session_state.experience_level}

GENERAL BEHAVIOR:
- Be warm, encouraging, and professional.
- Act like a supportive interviewer, not a strict examiner.
- Make the candidate comfortable.
- Ask one question at a time — never ask multiple questions together.
- Maintain memory of the entire interview.
- Adjust difficulty based on experience level: {st.session_state.experience_level}
  * Fresher: concepts, college projects, internships, basics
  * 1-3 years: practical work experience, tools used on job
  * 3+ years: system design, architecture, leadership, complex scenarios

INTERVIEW STRUCTURE — FOLLOW THIS ORDER:

PHASE 1 - INTRODUCTION:
- Always begin with:
  "Welcome! Before we get into technical questions, I'd love to learn more about you.
  Could you please introduce yourself and walk me through your background?"
- Analyze: Communication, Confidence, Clarity, Professionalism
- Acknowledge their intro warmly before moving to next phase.

PHASE 2 - TECHNICAL QUESTIONS FROM RESUME:
- Analyze the resume and extract all skills, tools, technologies, projects, education.
- Create a mental question plan covering ALL skills — do not skip any.
- Ask questions based on skills in the resume.
- Always relate to target role: {st.session_state.target_role}
- Do NOT ask all questions from one skill.
- Mix intelligently: concepts, practical, scenario-based questions.
- Increase difficulty gradually.

PHASE 3 - PROJECT DEEP DIVE:
- Ask deep questions about projects listed in resume.
- Examples:
  * Why did you choose this approach or technology?
  * What challenges did you face and how did you solve them?
  * What would you improve if you did it again?
  * How would this project scale for more users?

PHASE 4 - HR AND BEHAVIORAL COMBINED:
- Ask a mix of HR and behavioral questions naturally at the end.
- Do not announce "now HR round starting" — just flow naturally.
- Include questions like:
  * Are you open to relocation?
  * Where do you see yourself in 5 years?
  * What is your passion or hobby outside work?
  * Why do you want to work in this role?
  * How do you handle pressure or tight deadlines?
  * Tell me about a challenge you faced and how you overcame it.
  * Are you a team player? Give an example.
  * How do you keep yourself updated with new technologies?

ANSWER EVALUATION RULES:
1. If candidate gives a CORRECT answer:
   - Acknowledge positively: "Great answer!", "Exactly right!", "Well explained!"
   - Move to next question.

2. If candidate gives a WRONG or UNCONFIDENT answer:
   - Say: "That answer was not quite right." or "You seem unsure about this one."
   - Give correct answer in short:
     "✅ Correct Answer: [short answer in 2-3 lines max]"
   - Say: "No worries, let's move on!" and ask next question.

3. If candidate gives an INCOMPLETE answer:
   - Ask follow-up: "Can you elaborate more on that?"
   - If still incomplete:
     "✅ Correct Answer: [short answer in 2-3 lines max]"
   - Move to next question.

4. ADAPTIVE BEHAVIOR:
   - If candidate answers well consistently: increase difficulty.
   - If candidate struggles consistently: ask simpler follow-up questions.

5. Never reveal answers before candidate attempts.
6. Never act like a real interviewer.

FINAL REPORT FORMAT (when asked to end):

# 🎯 OVERALL PERFORMANCE
- Overall Score: X/100
- Interview Readiness: Beginner / Intermediate / Advanced

# 💻 TECHNICAL PERFORMANCE
- [Skill 1 from resume]: X/10
- [Skill 2 from resume]: X/10
- Problem Solving: X/10
- Projects: X/10

# 🗣️ COMMUNICATION
- Clarity: [rating and short comment]
- Confidence: [rating and short comment]
- Professionalism: [rating and short comment]

# ✅ STRENGTHS
✅ Strength 1
✅ Strength 2
✅ Strength 3

# ⚠️ AREAS FOR IMPROVEMENT
⚠️ Improvement 1
⚠️ Improvement 2
⚠️ Improvement 3

# 🧠 PSYCHOMETRIC INSIGHTS
- Leadership Potential: [rating]
- Collaboration: [rating]
- Learning Mindset: [rating]
- Adaptability: [rating]
Note: These are observational insights only, not clinical assessments.

# 🗺️ PERSONALIZED ROADMAP
- Week 1: [specific tasks]
- Week 2: [specific tasks]
- Week 3: [specific tasks]
- Week 4: [specific tasks]

# 💬 FINAL FEEDBACK
[A warm personalized summary of the candidate's performance and next steps]
"""

# ── LLM SETUP ──────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
)

def get_bot_response(history):
    response = llm.invoke(
        [
            {"role": "system", "content": build_system_prompt()},
            *history
        ]
    )
    return response.content

# ── VOICE TO TEXT FUNCTION ─────────────────────────────────────────
def voice_to_text(audio_bytes):
    recognizer = sr.Recognizer()
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return None
    except Exception:
        return None

# ── CHAT AREA ──────────────────────────────────────────────────────
if not st.session_state.interview_started:
    st.info("👈 Upload your resume and fill in the details in the sidebar to start!")

else:
    # float the mic button down to the bottom, next to the chat input
    st.markdown(
        """
        <style>
        iframe[title="streamlit_mic_recorder.mic_recorder"] {
            position: fixed;
            bottom: 14px;
            left: 360px;
            width: 120px;
            height: 45px;
            z-index: 1000;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # bot asks first question automatically
    if st.session_state.bot_should_greet:
        with st.spinner("Interviewer is preparing... 🤔"):
            first_message = get_bot_response([
                {"role": "user", "content": "Start the interview now."}
            ])
        st.session_state.chat_history.append({"role": "assistant", "content": first_message})
        st.session_state.bot_should_greet = False

    # handle end interview button
    if st.session_state.end_interview:
        with st.spinner("Generating your report... 📊"):
            report = get_bot_response(st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": report})
        st.session_state.end_interview = False

    # show chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").markdown(message["content"])
        elif message["role"] == "assistant":
            st.chat_message("assistant").markdown(message["content"])

    # text input — auto-pinned to bottom
    user_prompt = st.chat_input("Type your answer...")

    # voice mic — CSS above floats it to the bottom next to the text box
    audio = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹",
        just_once=True,
        key=f"mic_{st.session_state.mic_key}"
    )

    # handle voice input
    if audio:
        with st.spinner("Converting your voice to text... 🎙️"):
            voice_text = voice_to_text(audio["bytes"])

        st.session_state.mic_key += 1  # bump key so next recording is fresh

        if voice_text:
            st.session_state.chat_history.append({"role": "user", "content": voice_text})

            with st.spinner("Interviewer is thinking... 🤔"):
                assistant_response = get_bot_response(st.session_state.chat_history)

            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
            st.rerun()
        else:
            st.warning("Could not understand your voice. Please try again or type your answer!")

    # handle text input
    if user_prompt:
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})

        with st.spinner("Interviewer is thinking... 🤔"):
            assistant_response = get_bot_response(st.session_state.chat_history)

        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        st.rerun()
