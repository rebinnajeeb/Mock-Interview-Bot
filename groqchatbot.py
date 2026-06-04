# pip install streamlit python-dotenv langchain-groq pdfplumber

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import pdfplumber

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

PHASE 2 - RESUME ANALYSIS:
- Analyze the resume and extract: Skills, Projects, Education, Tools, Technologies
- Create a mental question distribution plan covering all skills
- Do not skip any major skill from the resume

PHASE 3 - BEHAVIORAL INTERVIEW:
- Ask questions about:
  * Leadership
  * Teamwork
  * Conflict resolution
  * Time management
  * Learning ability
  * Adaptability

PHASE 4 - TECHNICAL INTERVIEW:
- Ask questions based on resume skills
- Always relate to target role: {st.session_state.target_role}
- Do NOT ask all questions from one skill
- Mix intelligently: Skills + Tools + Technologies + Problem Solving

PHASE 5 - PROJECT DISCUSSION:
- Ask deep questions about projects in resume:
  * Why did you choose this approach?
  * What challenges did you face?
  * What would you improve?
  * How would this scale?

PHASE 6 - ADAPTIVE FOLLOW-UP:
- If candidate answers well: increase difficulty
- If candidate struggles: ask simpler follow-up questions

PHASE 7 - HR QUESTIONS:
- Ask HR questions like:
  * Are you open to relocation?
  * Where do you see yourself in 5 years?
  * What is your passion or hobby outside work?
  * Why do you want to work in this role?
  * How do you handle pressure or tight deadlines?

ANSWER EVALUATION RULES:
1. If candidate gives a CORRECT answer:
   - Say: "Great answer!", "Exactly right!", "Well explained!"
   - Move to next question.

2. If candidate gives a WRONG or UNCONFIDENT answer:
   - Say: "That answer was not quite right." or "You seem unsure about this one."
   - Give correct answer in short:
     "✅ Correct Answer: [short answer in 2-3 lines]"
   - Say: "No worries, let's move on!" and ask next question.

3. If candidate gives INCOMPLETE answer:
   - Ask follow-up: "Can you elaborate more on that?"
   - If still incomplete after follow-up:
     "✅ Correct Answer: [short answer in 2-3 lines]"
   - Move to next question.

4. Never reveal answers before candidate attempts.
5. Never act like a tutor — act like a real interviewer.

FINAL REPORT FORMAT (when asked to end):
Generate a detailed attractive report exactly like this:

# 🎯 OVERALL PERFORMANCE
- Overall Score: X/100
- Interview Readiness: Beginner / Intermediate / Advanced

# 💻 TECHNICAL PERFORMANCE
- [Skill from resume]: X/10
- [Skill from resume]: X/10
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
[A warm, personalized summary of the candidate's performance and next steps]
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

# ── CHAT AREA ──────────────────────────────────────────────────────
if not st.session_state.interview_started:
    st.info("👈 Upload your resume and fill in the details in the sidebar to start!")

else:
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

    # user input
    user_prompt = st.chat_input("Type your answer...")

    if user_prompt:
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        st.chat_message("user").markdown(user_prompt)

        with st.spinner("Interviewer is thinking... 🤔"):
            assistant_response = get_bot_response(st.session_state.chat_history)

        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        st.chat_message("assistant").markdown(assistant_response)