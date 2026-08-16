import os
import json
import streamlit as st
from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai import types

st.set_page_config(page_title="CG Vyapam MCQ Master", page_icon="🎯", layout="wide")

# 10 CG Vyapam Patterns Strictly Locked
class VyapamPatternEnum(str, Enum):
    P1 = "1. One-Liner MCQ (Direct Fact / Formula Based)"
    P2 = "2. True / False Pairing Question (Statement 1 & Statement 2)"
    P3 = "3. Match the Following (Column A vs Column B)"
    P4 = "4. Chronological / Logical Sequence Question"
    P5 = "5. 'Not Correct' / Galat Kathan Question"
    P6 = "6. Assertion (A) & Reason (R) Question"
    P7 = "7. Multi-Statement Question (Statements 1, 2, 3)"
    P8 = "8. Concept-Based / Application Question"
    P9 = "9. Analytical / Elimination-Based Question"
    P10 = "10. High-Yield PYQ Level Standard MCQ"

class MCQQuestion(BaseModel):
    id: int
    pattern_type: VyapamPatternEnum = Field(description="Must strictly be one of the 10 CG Vyapam patterns")
    question_text: str = Field(description="Question body strictly matching the assigned pattern structure")
    options: List[str] = Field(description="Exactly 4 options formatted as A) ..., B) ..., C) ..., D) ...")
    correct_option: str = Field(description="Exact string matching the right option, e.g., 'A) ...'")
    explanation: str = Field(description="Authentic Hindi/Hinglish explanation referencing CG Granth Academy / standard Vyapam facts")

class QuizResponse(BaseModel):
    subject: str
    chapter: str
    questions: List[MCQQuestion]

# Sidebar
with st.sidebar:
    st.header("⚙️ Exam Settings")
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            api_key = st.text_input("Gemini API Key:", type="password")
        else:
            st.success("🔑 API Key Auto-Connected!")
            
        num_q = st.select_slider("Kitne Questions Chahiye?", options=[10, 20, 30, 40, 50], value=20)
        st.markdown("---")
        st.caption("🔒 **Strict CG Vyapam 10-Pattern Engine Active**")

# Main Interface
st.title("🎯 CG Vyapam 50-MCQ Practice Engine")
st.write("Subject aur Chapter select karo, AI 10 patterns ka strict balanced set generate karega.")

col1, col2 = st.columns([1, 2])
with col1:
    subject = st.selectbox("Subject:", [
        "Chhattisgarh GS (इतिहास, भूगोल, जनजाति, पंचायती राज)",
        "Hindi Vyakaran (सामान्य हिन्दी)",
        "Computer Knowledge (कंप्यूटर ज्ञान)",
        "Indian GS (Polity, History, Geography, Science)",
        "Reasoning & General Aptitude"
    ])
with col2:
    chapter = st.text_input("Chapter / Topic Name:", placeholder="e.g., Kalchuri Vansh, Varnamala, MS Office, Bastar ke Vidroh...")

if st.button("🚀 Generate Vyapam Practice Test", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ Pehle Sidebar me Gemini API Key daalein!")
    elif not chapter.strip():
        st.warning("⚠️ Kripya Chapter ka naam likhein.")
    else:
        with st.spinner(f"Creating {num_q} standard Vyapam MCQs for '{chapter}'..."):
            try:
                client = genai.Client(api_key=api_key)
                
                system_prompt = f"""
                You are an official CG Vyapam (PEB) Examination Question Paper Setter.
                Generate {num_q} high-standard MCQs strictly on the topic: '{chapter}' for subject: '{subject}'.
                
                RULES:
                1. Strictly distribute questions across all 10 CG Vyapam patterns evenly.
                2. Authentic Sources Only: CG Hindi Granth Academy, CGPSC/Vyapam PYQs, NCERT, Pariksha Manthan.
                3. Language: Clear Hindi/Hinglish standard used in Vyapam exams with English terms in brackets for science/computer.
                4. Tone: Exam standard, non-repetitive, high factual accuracy.
                """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"Generate {num_q} MCQs for Chapter: {chapter} in Subject: {subject}",
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        response_schema=QuizResponse,
                        temperature=0.7
                    )
                )

                st.session_state['quiz_data'] = json.loads(response.text)
                st.session_state['user_answers'] = {}
                st.session_state['submitted'] = False
                st.success("✅ Test ready hai! Niche solve karein.")
            except Exception as e:
                st.error(f"Error: {e}")

# Quiz Display & Submission
if 'quiz_data' in st.session_state and st.session_state['quiz_data']:
    quiz = st.session_state['quiz_data']
    st.divider()
    st.subheader(f"📝 Topic: {quiz['chapter']} | Total Questions: {len(quiz['questions'])}")

    with st.form("exam_form"):
        for q in quiz['questions']:
            st.info(f"📌 **Pattern:** {q['pattern_type']}")
            st.write(f"**Q{q['id']}. {q['question_text']}**")
            
            user_choice = st.radio(
                f"Opt_{q['id']}",
                q['options'],
                index=None,
                key=f"q_{q['id']}",
                label_visibility="collapsed"
            )
            st.session_state['user_answers'][q['id']] = user_choice
            st.write("---")

        if st.form_submit_button("📊 Submit & View Result", type="primary", use_container_width=True):
            st.session_state['submitted'] = True

    if st.session_state.get('submitted', False):
        score = sum(1 for q in quiz['questions'] if st.session_state['user_answers'].get(q['id']) == q['correct_option'])
        total = len(quiz['questions'])
        
        st.balloons()
        st.metric(label="🎯 Final Score", value=f"{score} / {total}", delta=f"{(score/total)*100:.1f}% Accuracy")
        
        st.subheader("🔍 Solutions & Authentic Explanations:")
        for q in quiz['questions']:
            user_ans = st.session_state['user_answers'].get(q['id'])
            is_correct = (user_ans == q['correct_option'])
            
            with st.expander(f"Q{q['id']}: {q['question_text'][:80]}... {'✅ Right' if is_correct else '❌ Wrong'}"):
                st.write(f"**Aapka Answer:** {user_ans if user_ans else 'Not Attempted'}")
                st.write(f"**Sahi Answer:** {q['correct_option']}")
                st.info(f"💡 **Explanation:** {q['explanation']}")
