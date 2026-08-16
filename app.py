import os
import json
import streamlit as st
from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai import types

# Modern Wide UI Configuration
st.set_page_config(
    page_title="CG Vyapam FWLN26 Practice Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark-Mode Modern Glassmorphism CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    .main-title {
        font-size: 28px;
        font-weight: 700;
        color: #60a5fa;
        margin-bottom: 6px;
    }
    
    .main-subtitle {
        font-size: 14px;
        color: #9ca3af;
    }
    
    .q-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    .badge-pattern {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #93c5fd;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 10 CG Vyapam Question Patterns Strictly Enforced
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
    question_text: str = Field(description="Question body in clear CBSE English + technical Hinglish terms matching the pattern")
    options: List[str] = Field(description="Exactly 4 options: A) ..., B) ..., C) ..., D) ...")
    correct_option: str = Field(description="Exact string matching one of the options")
    explanation: str = Field(description="Authentic explanation referencing NCERT / Standard Granth Academy facts")

class QuizResponse(BaseModel):
    subject: str
    chapter: str
    questions: List[MCQQuestion]

# Official Syllabus Mapped Strictly to NCERT Units
FULL_SYLLABUS = {
    "🧪 Chemistry (Class 11 & 12 NCERT) [30 Marks]": [
        "Some Basic Concepts of Chemistry (Mole Concept)",
        "Structure of Atom",
        "Classification of Elements & Periodicity",
        "Chemical Bonding and Molecular Structure",
        "Chemical Thermodynamics & Energetics",
        "Equilibrium (Physical, Chemical & Ionic)",
        "Redox Reactions",
        "Organic Chemistry: Basic Principles & Mechanisms",
        "Hydrocarbons (Alkanes, Alkenes, Alkynes, Arenes)",
        "Solutions & Colligative Properties",
        "Electrochemistry",
        "Chemical Kinetics",
        "d- and f-Block Elements (Transition Metals)",
        "Coordination Compounds",
        "Haloalkanes and Haloarenes",
        "Alcohols, Phenols and Ethers",
        "Aldehydes, Ketones and Carboxylic Acids",
        "Amines (Organic Nitrogen Compounds)",
        "Biomolecules (Carbs, Proteins, Nucleic Acids, Lipids)",
        "Polymers & Chemistry in Everyday Life"
    ],
    "⚡ Physics (Class 11 & 12 NCERT) [10 Marks]": [
        "Units and Measurements",
        "Kinematics (Motion in 1D & 2D)",
        "Laws of Motion & Friction",
        "Work, Energy and Power",
        "Rotational Motion & System of Particles",
        "Gravitation",
        "Mechanical Properties of Solids & Fluids",
        "Thermodynamics & Kinetic Theory of Gases",
        "Oscillations & Waves (Sound)",
        "Electrostatics & Capacitance",
        "Current Electricity & Circuits",
        "Magnetism, Moving Charges & Matter",
        "Electromagnetic Induction & Alternating Current",
        "Optics (Ray Optics & Wave Optics)",
        "Modern Physics (Dual Nature, Atoms, Nuclei)",
        "Semiconductor Devices & Digital Electronics"
    ],
    "🌿 Biology (Class 11 & 12 NCERT) [10 Marks]": [
        "The Living World & Biological Classification",
        "Plant Kingdom & Animal Kingdom",
        "Morphology & Anatomy of Flowering Plants",
        "Structural Organisation in Animals (Tissues)",
        "Cell: Structure and Functions",
        "Biomolecules & Enzymes",
        "Cell Cycle and Cell Division",
        "Plant Physiology (Photosynthesis, Respiration, Growth)",
        "Human Physiology: Digestion & Respiration",
        "Human Physiology: Body Fluids & Circulation",
        "Human Physiology: Excretion & Locomotion",
        "Human Physiology: Neural & Endocrine Coordination",
        "Reproduction in Plants and Humans",
        "Genetics: Principles of Inheritance & Molecular Basis",
        "Evolution",
        "Human Health, Disease & Immunity",
        "Biotechnology: Principles and Applications",
        "Ecology, Ecosystem & Environmental Issues"
    ],
    "🏛️ Chhattisgarh GK [10 Marks]": [
        "CG History: Ancient Dynasties (Nal, Sharabhpuriya, Pandu)",
        "CG History: Kalchuri Dynasty (Ratanpur & Raipur)",
        "CG History: Bastar Dynasties & Kakatiya Vansh",
        "Maratha Rule, Suba System & British Treaties",
        "Tribal Revolts of Bastar (Tarapur, Mediya, Bhoomkal)",
        "Freedom Movement in CG (1857 & National Movement)",
        "CG Geography: Physical Divisions, Rivers & Waterfalls",
        "CG Climate, Soils, Agriculture & Forests",
        "Mineral, Energy & Water Resources of CG",
        "CG Tribes, Ghotul System & Customs",
        "Folk Literature, Dance, Music, Arts & Festivals",
        "Administrative Setup, Urban Bodies & Panchayati Raj",
        "Economic Survey of CG & Budget Facts"
    ],
    "🇮🇳 General Knowledge of India [10 Marks]": [
        "Indian History: Ancient & Medieval India",
        "Indian National Movement & Modern History",
        "Physical, Social & Economic Geography of India",
        "Indian Constitution: Fundamental Rights & Duties",
        "Union Executive, Parliament & Judiciary",
        "Indian Economy, Budget & Banking",
        "Science & Technology & Environmental Ecology",
        "National & International Current Affairs"
    ],
    "🧠 Aptitude & Logical Reasoning [10 Marks]": [
        "Number Series & Alphabet Coding-Decoding",
        "Blood Relations & Direction Sense Test",
        "Syllogism, Venn Diagrams & Logical Deductions",
        "Basic Numeracy: Percentages, Profit & Loss",
        "Basic Numeracy: Ratio, Proportion & Averages",
        "Time, Work, Speed & Distance",
        "Data Interpretation (Bar Graphs, Tables, Pie Charts)",
        "Communication & Interpersonal Decision Making"
    ],
    "💻 Computer Knowledge [05 Marks]": [
        "Computer Hardware Architecture (CPU, Memory, Storage)",
        "Input, Output & Peripheral Devices",
        "Operating Systems (Windows, Linux, Command Line)",
        "MS Office Suite: MS Word & MS Excel Functions",
        "Internet Protocols, Search Engines & Browsers",
        "Cyber Security, Viruses, Firewalls & Cryptography"
    ],
    "📖 General Hindi (सामान्य हिन्दी) [05 Marks]": [
        "वर्ण विचार (स्वर, व्यंजन एवं वर्तनी शुद्धि)",
        "संधि एवं संधि विच्छेद (स्वर, व्यंजन, विसर्ग)",
        "समास रचना एवं उनके भेद",
        "संज्ञा, सर्वनाम, विशेषण, क्रिया एवं कारक",
        "तत्सम, तद्भव, देशज, विदेशज, उपसर्ग एवं प्रत्यय",
        "रस, अलंकार, दोहा, छंद एवं सोरठा",
        "पर्यायवाची, विलोम, अनेकार्थी एवं एक शब्द",
        "मुहावरे एवं लोकोक्तियां"
    ],
    "🗣️ Chhattisgarhi Language [05 Marks]": [
        "छत्तीसगढ़ी व्याकरण (संज्ञा, सर्वनाम, कारक, क्रिया)",
        "छत्तीसगढ़ी जनउला (पहेलियां / Riddles)",
        "छत्तीसगढ़ी हाना (लोकोक्तियां / Proverbs)",
        "छत्तीसगढ़ी मुहावरे एवं प्रचलित लोकोक्तियां"
    ],
    "🔤 English Language [05 Marks]": [
        "Articles, Determiners & Prepositions",
        "Tenses & Subject-Verb Agreement",
        "Active and Passive Voice",
        "Direct and Indirect Speech (Narration)",
        "Vocabulary: Synonyms, Antonyms & One Word Substitution",
        "Idioms, Phrases & Spelling Correction"
    ]
}

# Sidebar Navigation & Settings
with st.sidebar:
    st.markdown("### ⚙️ Engine Control")
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Gemini API Key:", type="password")
    else:
        st.success("🔑 API Key Connected")
    
    num_q = st.select_slider("Question Count:", options=[10, 20, 30, 40, 50], value=20)
    lang_pref = st.selectbox("Preferred Language:", [
        "English with Hinglish (Standard CBSE/Vyapam)",
        "Bilingual (Hindi + English)",
        "Pure English",
        "Pure Hindi (हिंदी)"
    ])
    st.markdown("---")
    st.markdown("🎯 **Target Exam:** CG Vyapam FWLN26")
    st.caption("Mapped strictly to NCERT Class 11-12 & Official Syllabus")

# Main Header Container
st.markdown("""
<div class='main-header'>
    <div class='main-title'>⚡ CG Vyapam FWLN26 Practice Engine</div>
    <div class='main-subtitle'>Strict NCERT Chapter-wise Mapping • 10 Exam Pattern Allocation • Authentic Granth Academy & PYQ Standard</div>
</div>
""", unsafe_allow_html=True)

# Select Subject & Chapter
col1, col2 = st.columns([1, 1])
with col1:
    selected_subject = st.selectbox("1. Select Subject / Stream:", list(FULL_SYLLABUS.keys()))

with col2:
    chapter_options = FULL_SYLLABUS[selected_subject] + ["+ Custom Topic (Manual Entry)"]
    selected_chapter = st.selectbox("2. Select NCERT Unit / Chapter:", chapter_options)

if selected_chapter == "+ Custom Topic (Manual Entry)":
    final_chapter = st.text_input("Enter Topic Name:", placeholder="e.g., Optical Isomerism, Danteshwari Temple...")
else:
    final_chapter = selected_chapter

# Test Generation Button
if st.button("🚀 Launch 10-Pattern Test Set", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ Gemini API Key is required!")
    elif not final_chapter or not final_chapter.strip():
        st.warning("⚠️ Please select a valid chapter.")
    else:
        with st.spinner(f"Generating {num_q} standard Vyapam MCQs for '{final_chapter}'..."):
            try:
                client = genai.Client(api_key=api_key)
                
                system_prompt = f"""
                You are the official Chief Question Setter for the CG Vyapam FWLN26 Recruitment Examination.
                Generate {num_q} high-standard examination MCQs strictly for:
                - Subject: '{selected_subject}'
                - Chapter / Unit: '{final_chapter}'
                - Language Style: '{lang_pref}'
                
                MANDATORY RULES:
                1. STRICT PATTERN MIX: Distribute questions evenly across all 10 CG Vyapam patterns (One-liner, Multi-statement, Match following, Chronological sequence, Not correct, Assertion-Reason, Concept application, Elimination, PYQ standard).
                2. STRICT NCERT & GRANTH ACADEMY STANDARDS: For Chemistry, Physics, and Biology, adhere strictly to CBSE NCERT Class 11-12 curriculum with exact scientific terminology. For CG GK, adhere to CG Granth Academy.
                3. Avoid repetitive facts. Ensure options are authentic with strong distractors.
                """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"Generate {num_q} MCQs on {final_chapter} ({selected_subject})",
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        response_schema=QuizResponse,
                        temperature=0.4
                    )
                )

                st.session_state['quiz_data'] = json.loads(response.text)
                st.session_state['user_answers'] = {}
                st.session_state['submitted'] = False
                st.success("✅ Test loaded successfully! Complete the questions below.")
            except Exception as e:
                st.error(f"Error generating test: {e}")

# Interactive Quiz Section
if 'quiz_data' in st.session_state and st.session_state['quiz_data']:
    quiz = st.session_state['quiz_data']
    st.markdown("---")
    st.subheader(f"📝 Chapter: {quiz['chapter']} ({len(quiz['questions'])} Questions)")

    with st.form("exam_form"):
        for q in quiz['questions']:
            st.markdown(f"<div class='badge-pattern'>Type: {q['pattern_type']}</div>", unsafe_allow_html=True)
            st.markdown(f"**Q{q['id']}. {q['question_text']}**")
            
            user_choice = st.radio(
                f"Option selection for Q{q['id']}",
                q['options'],
                index=None,
                key=f"q_{q['id']}",
                label_visibility="collapsed"
            )
            st.session_state['user_answers'][q['id']] = user_choice
            st.markdown("<br>", unsafe_allow_html=True)

        if st.form_submit_button("📊 Submit Test & Generate Scorecard", type="primary", use_container_width=True):
            st.session_state['submitted'] = True

    # Performance Evaluation & Explanations
    if st.session_state.get('submitted', False):
        score = sum(1 for q in quiz['questions'] if st.session_state['user_answers'].get(q['id']) == q['correct_option'])
        total = len(quiz['questions'])
        accuracy = (score / total) * 100
        
        st.balloons()
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label="🎯 Final Score", value=f"{score} / {total}")
        with col_m2:
            st.metric(label="📈 Accuracy Rate", value=f"{accuracy:.1f}%")
        
        st.markdown("### 🔍 Detailed Solutions & Conceptual Explanations")
        for q in quiz['questions']:
            user_ans = st.session_state['user_answers'].get(q['id'])
            is_correct = (user_ans == q['correct_option'])
            status_text = "✅ Correct" if is_correct else "❌ Incorrect"
            
            with st.expander(f"Q{q['id']}: {q['question_text'][:80]}... [{status_text}]"):
                st.write(f"**Your Choice:** {user_ans if user_ans else 'Not Attempted'}")
                st.write(f"**Correct Answer:** {q['correct_option']}")
                st.info(f"💡 **NCERT / Authentic Explanation:** {q['explanation']}")
