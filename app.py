import streamlit as st
import json
import google.generativeai as genai

# Page Config for FydeOS / PWA Desktop View
st.set_page_config(
    page_title="CG Vyapam FWLN26 Practice Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Practice UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 22px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
    .question-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .pattern-tag {
        background-color: #2563eb;
        color: #ffffff;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }
    .explanation-box-correct {
        background-color: #064e3b;
        border-left: 5px solid #10b981;
        padding: 14px 18px;
        border-radius: 6px;
        margin-top: 12px;
        color: #ecfdf5;
    }
    .explanation-box-wrong {
        background-color: #450a0a;
        border-left: 5px solid #ef4444;
        padding: 14px 18px;
        border-radius: 6px;
        margin-top: 12px;
        color: #fef2f2;
    }
    .explanation-box-neutral {
        background-color: #0f172a;
        border-left: 5px solid #3b82f6;
        padding: 14px 18px;
        border-radius: 6px;
        margin-top: 12px;
        color: #f8fafc;
    }
    .score-banner {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 10px;
        padding: 12px 20px;
        display: flex;
        justify-content: space-around;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- FULL OFFICIAL SYLLABUS DATA -----------------
SYLLABUS_TREE = {
    "Part 2: Chemistry [30 Marks]": {
        "Physical Chemistry (Class 11)": [
            "Class 11 - Ch 1: Some Basic Concepts of Chemistry (Mole Concept)",
            "Class 11 - Ch 5: States of Matter: Gases and Liquids",
            "Class 11 - Ch 6: Chemical Thermodynamics",
            "Class 11 - Ch 7: Equilibrium",
            "Class 11 - Ch 8: Redox Reactions (Basics for Electrochemistry & Titrations)"
        ],
        "Physical Chemistry (Class 12)": [
            "Class 12 - Ch 1: The Solid State",
            "Class 12 - Ch 2: Solutions",
            "Class 12 - Ch 3: Electrochemistry",
            "Class 12 - Ch 4: Chemical Kinetics",
            "Class 12 - Ch 5: Surface Chemistry"
        ],
        "Inorganic Chemistry (Class 11 & 12)": [
            "Class 11 - Ch 2: Structure of Atom",
            "Class 11 - Ch 3: Classification of Elements and Periodicity in Properties",
            "Class 11 - Ch 4: Chemical Bonding and Molecular Structure",
            "Class 12 - Ch 6: General Principles and Processes of Isolation of Elements (Metallurgy)",
            "Class 12 - Ch 8: The d- and f-Block Elements",
            "Class 12 - Ch 9: Coordination Compounds"
        ],
        "Organic & Biochemistry (Class 11 & 12)": [
            "Class 11 - Ch 12: Organic Chemistry – Some Basic Principles and Techniques (GOC)",
            "Class 11 - Ch 13: Hydrocarbons",
            "Class 12 - Ch 10: Haloalkanes and Haloarenes",
            "Class 12 - Ch 11: Alcohols, Phenols and Ethers",
            "Class 12 - Ch 12: Aldehydes, Ketones and Carboxylic Acids",
            "Class 12 - Ch 13: Amines",
            "Class 12 - Ch 14: Biomolecules",
            "Class 12 - Ch 15: Polymers",
            "Class 12 - Ch 16: Chemistry in Everyday Life"
        ]
    },
    "Part 2: Physics [10 Marks]": {
        "Mechanics (Class 11)": [
            "Class 11 - Ch 2: Units and Measurements",
            "Class 11 - Ch 3: Motion in a Straight Line",
            "Class 11 - Ch 4: Motion in a Plane",
            "Class 11 - Ch 5: Laws of Motion",
            "Class 11 - Ch 6: Work, Energy and Power",
            "Class 11 - Ch 7: System of Particles and Rotational Motion",
            "Class 11 - Ch 8: Gravitation",
            "Class 11 - Ch 9: Mechanical Properties of Solids",
            "Class 11 - Ch 10: Mechanical Properties of Fluids"
        ],
        "Heat, Thermodynamics & Waves (Class 11)": [
            "Class 11 - Ch 11: Thermal Properties of Matter",
            "Class 11 - Ch 12: Thermodynamics",
            "Class 11 - Ch 13: Kinetic Theory of Gases",
            "Class 11 - Ch 14: Oscillations",
            "Class 11 - Ch 15: Waves"
        ],
        "Electricity & Magnetism (Class 12)": [
            "Class 12 - Ch 1: Electric Charges and Fields",
            "Class 12 - Ch 2: Electrostatic Potential and Capacitance",
            "Class 12 - Ch 3: Current Electricity",
            "Class 12 - Ch 4: Moving Charges and Magnetism",
            "Class 12 - Ch 5: Magnetism and Matter",
            "Class 12 - Ch 6: Electromagnetic Induction",
            "Class 12 - Ch 7: Alternating Current",
            "Class 12 - Ch 8: Electromagnetic Waves"
        ],
        "Optics & Modern Physics (Class 12)": [
            "Class 12 - Ch 9: Ray Optics and Optical Instruments",
            "Class 12 - Ch 10: Wave Optics",
            "Class 12 - Ch 11: Dual Nature of Radiation and Matter",
            "Class 12 - Ch 12: Atoms",
            "Class 12 - Ch 13: Nuclei",
            "Class 12 - Ch 14: Semiconductor Electronics"
        ]
    },
    "Part 2: Biology [10 Marks]": {
        "Botany & Diversity (Class 11)": [
            "Class 11 - Ch 1: The Living World",
            "Class 11 - Ch 2: Biological Classification",
            "Class 11 - Ch 3: Plant Kingdom",
            "Class 11 - Ch 5: Morphology of Flowering Plants",
            "Class 11 - Ch 6: Anatomy of Flowering Plants",
            "Class 11 - Ch 13: Photosynthesis in Higher Plants",
            "Class 11 - Ch 14: Respiration in Plants",
            "Class 11 - Ch 15: Plant Growth and Development"
        ],
        "Cell Biology & Zoology / Physiology (Class 11)": [
            "Class 11 - Ch 8: Cell: The Unit of Life",
            "Class 11 - Ch 9: Biomolecules",
            "Class 11 - Ch 10: Cell Cycle and Cell Division",
            "Class 11 - Ch 4: Animal Kingdom",
            "Class 11 - Ch 7: Structural Organisation in Animals",
            "Class 11 - Ch 17: Breathing and Exchange of Gases",
            "Class 11 - Ch 18: Body Fluids and Circulation",
            "Class 11 - Ch 19: Excretory Products and their Elimination",
            "Class 11 - Ch 20: Locomotion and Movement",
            "Class 11 - Ch 21: Neural Control and Coordination",
            "Class 11 - Ch 22: Chemical Coordination and Integration"
        ],
        "Reproduction, Genetics & Evolution (Class 12)": [
            "Class 12 - Ch 1: Reproduction in Organisms",
            "Class 12 - Ch 2: Sexual Reproduction in Flowering Plants",
            "Class 12 - Ch 3: Human Reproduction",
            "Class 12 - Ch 4: Reproductive Health",
            "Class 12 - Ch 5: Principles of Inheritance and Variation",
            "Class 12 - Ch 6: Molecular Basis of Inheritance",
            "Class 12 - Ch 7: Evolution"
        ],
        "Biotech, Health & Ecology (Class 12)": [
            "Class 12 - Ch 8: Human Health and Disease",
            "Class 12 - Ch 9: Strategies for Enhancement in Food Production",
            "Class 12 - Ch 10: Microbes in Human Welfare",
            "Class 12 - Ch 11: Biotechnology – Principles and Processes",
            "Class 12 - Ch 12: Biotechnology and its Applications",
            "Class 12 - Ch 13: Organisms and Populations",
            "Class 12 - Ch 14: Ecosystem",
            "Class 12 - Ch 15: Biodiversity and Conservation",
            "Class 12 - Ch 16: Environmental Issues"
        ]
    },
    "Part 1: General Knowledge of India [10 Marks]": {
        "Indian GS Core": [
            "History of India",
            "Physical, Social & Economic Geography of India",
            "Constitution of India",
            "Indian Economy",
            "Social Science",
            "Science & Technology",
            "Indian Art, Literature & Culture",
            "Environment & Ecology",
            "Sports",
            "Current Affairs (National & International)"
        ]
    },
    "Part 1: General Knowledge of Chhattisgarh [10 Marks]": {
        "CG Special Topics": [
            "History of CG (Kakatiya Vansh, Kalchuri, Tribal Revolts)",
            "Geography, Climate, Physical Conditions, Demographics & Census",
            "Archaeological & Tourist Places",
            "Literature, Music, Dance, Art & Culture",
            "Special Traditions, Festivals & Rituals (Bastar Dussehra, Danteshwari)",
            "Economy of CG, Forests & Agriculture",
            "Administrative Setup, Local Governance & Panchayati Raj",
            "Industry, Energy, Water & Mineral Resources",
            "Current Affairs of Chhattisgarh"
        ]
    },
    "Part 1: Aptitude & Reasoning [10 Marks]": {
        "Aptitude Topics": [
            "Interpersonal Skills including Communication Skills",
            "Logical Reasoning & Analytical Ability",
            "Decision Making & Problem Solving",
            "General Mental Ability",
            "Basic Numeracy (General Mathematical Skills)",
            "Data Interpretation (Charts, Graphs, Tables, Data Sufficiency)"
        ]
    },
    "Part 1: Computer Knowledge [05 Marks]": {
        "Computer Modules": [
            "Computer Hardware & Software Architecture",
            "Operating Systems (OS)",
            "Internet Applications, Networking & Cybersecurity"
        ]
    },
    "Part 1: Hindi Language [05 Marks]": {
        "Hindi Vyakaran": [
            "Vowels, Consonants, Spelling (स्वर, व्यंजन, वर्तनी)",
            "Gender, Number, Tense (लिंग, वचन, काल)",
            "Noun, Pronoun, Adjective, Adverb, Case (संज्ञा, सर्वनाम, विशेषण, कारक)",
            "Compound Words (Samas - Construction & Types / समास)",
            "Sandhi (Vowel, Consonant, Visarga / संधि)",
            "Rasa & Alankar, Doha, Chhand, Sortha (रस, अलंकार, छंद)",
            "Grammatical Errors & Corrections",
            "Words, Vocabulary & One Word Substitution (विलोम, पर्यायवाची)",
            "Idioms & Proverbs (मुहावरे और लोकोक्तियाँ)"
        ]
    },
    "Part 1: Chhattisgarhi Language [05 Marks]": {
        "Chhattisgarhi Core": [
            "Janaula (Riddles / जनउला)",
            "Idioms (Muhavare / मुहावरे)",
            "Chhattisgarhi Grammar & Pronouns (छत्तीसगढ़ी व्याकरण)",
            "Hana (Proverbs) & Sayings (हाना एवं लोकोक्तियां)"
        ]
    },
    "Part 1: English Language [05 Marks]": {
        "English Grammar": [
            "Number, Gender, Articles",
            "Pronouns, Adjectives, Verbs, Adverbs",
            "Use of Some Important Conjunctions",
            "Use of Some Important Prepositions",
            "Active / Passive Voice",
            "Direct / Indirect Narration",
            "Synonyms & Antonyms",
            "One Word Substitution",
            "Spelling, Proverbs, Idioms and Phrases"
        ]
    }
}

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.markdown("### ⚙️ Practice Engine Control")
    
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    if api_key:
        st.success("🔑 API Key Connected", icon="✅")
        genai.configure(api_key=api_key)
    else:
        api_key = st.text_input("Enter Gemini API Key:", type="password")
        if api_key:
            genai.configure(api_key=api_key)
        else:
            st.error("Set GEMINI_API_KEY in Streamlit Secrets.")

    st.markdown("---")
    question_count = st.slider("Questions per Batch:", min_value=5, max_value=50, value=10, step=5)
    
    language_pref = st.selectbox(
        "Explanation Language:",
        ["English with Hinglish (Standard Technical Terms)", "Pure English", "Hindi / Chhattisgarhi"]
    )
    
    st.markdown("---")
    st.markdown("""
    **🎯 Target:** CG Vyapam FWLN26  
    **Mode:** Active Practice & Instant Explanation  
    **Standard:** NCERT Class 11-12 & CG Granth Academy
    """)

# ----------------- MAIN UI -----------------
st.markdown("""
<div class="main-header">
    <h2 style="margin:0; color:#f8fafc;">⚡ CG Vyapam FWLN26 Practice Engine</h2>
    <p style="margin:5px 0 0 0; color:#94a3b8;">Interactive Practice Mode • Instant Answer Reveal & NCERT Deep Explanation</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    selected_subject = st.selectbox("1. Select Subject / Part:", list(SYLLABUS_TREE.keys()))

with col2:
    sub_categories = SYLLABUS_TREE[selected_subject]
    selected_subcat = st.selectbox("2. Select Category / Unit:", list(sub_categories.keys()))

selected_chapter = st.selectbox("3. Select Chapter / Topic:", sub_categories[selected_subcat])

# ----------------- AI GENERATION ENGINE -----------------
def generate_questions(subject, chapter, count, lang):
    prompt = f"""
    You are an expert examiner and professor setting high-standard practice MCQs for CG Vyapam FWLN26 (Food & Drug Administration Lab Assistant / Namuna Sahayak).
    Generate strictly {count} challenging MCQs mapped strictly to:
    - Subject: {subject}
    - Specific Chapter/Topic: {chapter}
    - Language Style: {lang}

    STRICT 10 EXAM PATTERNS TO ROTATE ACROSS QUESTIONS:
    1. Multi-Statement Evaluation (Statements 1, 2, 3 -> Choose correct: Only 1 & 2, All, etc.)
    2. Match the Following (List-I with List-II)
    3. Assertion-Reason (A & R format)
    4. Chronological / Sequential Order Arrangement
    5. 'NOT Correct' / 'INCORRECT' identification
    6. Concept & Mechanism Depth (CBSE/NCERT Class 11-12 standard)
    7. Data / Table / Property Comparison
    8. Direct Standard PYQ Vyapam Standard
    9. Case / Application Based Practical Question
    10. Pair Identification (Correctly matched / Incorrectly matched)

    OUTPUT FORMAT REQUIREMENTS:
    Return ONLY a valid JSON array of objects. Do not include markdown ticks like ```json.
    Each object must have the following keys:
    - "id": integer (1 to {count})
    - "pattern": string (Name of the pattern used from the 10 patterns)
    - "question": string (The full question text including any statements/tables/lists)
    - "options": list of 4 strings (e.g. ["A) ...", "B) ...", "C) ...", "D) ..."])
    - "correct_answer": string (Single capital letter: "A", "B", "C", or "D")
    - "explanation": string (Step-by-step rigorous NCERT/Authentic explanation in Hinglish/English with key concepts, reactions/formulas, or historical facts)
    """

    model = genai.GenerativeModel("gemini-3.7-flash")
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    return response.text

# ----------------- GENERATE BUTTON -----------------
if st.button("🚀 Load Practice MCQs", use_container_width=True, type="primary"):
    if not api_key:
        st.error("Please connect your Gemini API Key first!")
    else:
        with st.spinner(f"Generating {question_count} practice questions for '{selected_chapter}'..."):
            try:
                raw_json = generate_questions(selected_subject, selected_chapter, question_count, language_pref)
                cleaned_json = raw_json.strip()
                if cleaned_json.startswith("```json"):
                    cleaned_json = cleaned_json[7:]
                if cleaned_json.endswith("```"):
                    cleaned_json = cleaned_json[:-3]
                
                questions = json.loads(cleaned_json)
                st.session_state["practice_questions"] = questions
                # Reset selections on new question load
                for q in questions:
                    if f"ans_q_{q['id']}" in st.session_state:
                        del st.session_state[f"ans_q_{q['id']}"]
                st.success(f"Loaded {len(questions)} Practice Questions!")
            except Exception as e:
                st.error(f"Error generating questions: {str(e)}")

# ----------------- INTERACTIVE PRACTICE RENDER -----------------
if "practice_questions" in st.session_state and st.session_state["practice_questions"]:
    questions = st.session_state["practice_questions"]
    
    # Calculate Live Stats
    attempted_count = 0
    correct_count = 0
    
    for q in questions:
        selected_val = st.session_state.get(f"ans_q_{q['id']}", None)
        if selected_val is not None:
            attempted_count += 1
            if selected_val.strip().startswith(q['correct_answer'].strip().upper()):
                correct_count += 1

    # Live Practice Status Bar
    st.markdown(f"""
    <div style="background: #1e293b; border: 1px solid #3b82f6; border-radius: 8px; padding: 12px 20px; margin: 20px 0;">
        <span style="font-size: 1rem; color: #94a3b8;">Practice Progress: </span>
        <strong style="color: #60a5fa; font-size: 1.1rem;">Attempted {attempted_count}/{len(questions)}</strong> | 
        <span style="font-size: 1rem; color: #94a3b8;"> Correct: </span>
        <strong style="color: #34d399; font-size: 1.1rem;">{correct_count}</strong> | 
        <span style="font-size: 1rem; color: #94a3b8;"> Accuracy: </span>
        <strong style="color: #fbbf24; font-size: 1.1rem;">{(correct_count/attempted_count*100) if attempted_count > 0 else 0:.1f}%</strong>
    </div>
    """, unsafe_allow_html=True)

    # Render Each Question with Instant Reveal
    for q in questions:
        st.markdown(f"""
        <div class="question-card">
            <span class="pattern-tag">Pattern: {q.get('pattern', 'Vyapam Standard')}</span>
            <p style="font-size: 1.05rem; font-weight: 600; color: #f8fafc; margin-top: 6px; line-height: 1.5;">
                Q{q['id']}. {q['question'].replace(chr(10), '<br>')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        user_choice = st.radio(
            f"Select Option for Q{q['id']}:",
            q['options'],
            index=None,
            key=f"ans_q_{q['id']}",
            label_visibility="collapsed"
        )

        correct_letter = q['correct_answer'].strip().upper()

        # Instant Evaluation Box
        if user_choice is not None:
            if user_choice.strip().startswith(correct_letter):
                st.markdown(f"""
                <div class="explanation-box-correct">
                    <strong>✅ Sahi Jawab! (Option {correct_letter})</strong><br><br>
                    <strong>📖 NCERT / Core Explanation:</strong><br>
                    {q['explanation']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="explanation-box-wrong">
                    <strong>❌ Galat Jawab! Sahi Option: {correct_letter}</strong><br><br>
                    <strong>📖 NCERT / Core Explanation:</strong><br>
                    {q['explanation']}
                </div>
                """, unsafe_allow_html=True)
        else:
            # Option to reveal without answering
            with st.expander("💡 Direct Answer & Explanation Dekhein (Bina Attempt Kiye)"):
                st.markdown(f"""
                <div class="explanation-box-neutral">
                    <strong>Correct Option: {correct_letter}</strong><br><br>
                    <strong>📖 NCERT / Core Explanation:</strong><br>
                    {q['explanation']}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color: #334155; margin: 25px 0;'>", unsafe_allow_html=True)
