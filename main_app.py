


# medical_rag_chatbot/main_app.py

import streamlit as st
import os
from dotenv import load_dotenv
import re
from datetime import datetime
import json
import traceback # Ensure traceback is imported for detailed error logging

# --- Define SCRIPT_DIR, ASSETS_DIR, DATA_DIR first for robustness ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# Make sure rag_pipeline and utils are found by adding SCRIPT_DIR to sys.path
import sys
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

try:
    # UPDATED TO FAISS FUNCTION NAMES
    from rag_pipeline import (
        load_and_process_pdf_to_faiss, # Assumes this is in your FAISS rag_pipeline.py
        query_rag_pipeline_faiss,      # Assumes this is in your FAISS rag_pipeline.py
        load_existing_faiss_store,     # Assumes this is in your FAISS rag_pipeline.py
        OPENAI_API_KEY
    )
except ImportError as e:
    st.error(
        f"Critical Error: Could not import FAISS-specific functions from 'rag_pipeline.py'. "
        f"Please ensure 'rag_pipeline.py' has been updated for FAISS (e.g., uses functions like 'load_and_process_pdf_to_faiss') "
        f"and 'utils.py' are in the same directory as 'main_app.py' ({SCRIPT_DIR}) "
        f"and all dependencies are installed. Specific error: {e}"
    )
    st.stop()

# --- Page Configuration ---
favicon_path = os.path.join(ASSETS_DIR, "favicon.png")
st.set_page_config(
    page_title="Tata MD AI Medical Advisor",
    page_icon=favicon_path if os.path.exists(favicon_path) else "🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Define Theme Colors (using your provided theme) ---
bg_color = "#141E30"
text_color_yellow = "#FFFACD"
text_color_blue = "#87CEFA"
primary_accent_pink = "#FF3CAC"
secondary_accent_blue = "#2B86C5"
secondary_accent_purple = "#784BA0"
dark_theme_bg_accent = "#243B55"
highlight_color_medication = "#FFB74D" # Orange for medication names
highlight_color_med_purpose = "#AED581" # Light Green for purpose
highlight_color_med_dosage = "#FFF176" # Light Yellow for dosage (use with caution)
highlight_color_med_notes = "#BCAAA4" # Light Brown/Grey for notes
highlight_color_positive_icon = "#66BB6A"
highlight_color_negative_icon = "#EF5350"
expander_header_bg_color = f"linear-gradient(135deg, rgba(255, 60, 172, 0.4) 0%, rgba(43, 134, 197, 0.5) 100%)"
expander_content_bg_color = f"rgba(43, 134, 197, 0.15)"
card_bg_color = f"rgba({int(secondary_accent_blue[1:3], 16)}, {int(secondary_accent_blue[3:5], 16)}, {int(secondary_accent_blue[5:7], 16)}, 0.4)"
card_border_color = f"rgba({int(primary_accent_pink[1:3], 16)}, {int(primary_accent_pink[3:5], 16)}, {int(primary_accent_pink[5:7], 16)}, 0.3)"
analysis_done_chat_bg = f"rgba({int(secondary_accent_blue[1:3], 16)}, {int(secondary_accent_blue[3:5], 16)}, {int(secondary_accent_blue[5:7], 16)}, 0.25)"


# --- Custom CSS (Your provided CSS) ---
st.markdown(f"""
<style>
    /* Base styles - Default text is Yellow */
    body, .stApp, .stChatInput, .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{
        background-color: {bg_color} !important;
        background-image: linear-gradient(to bottom right, {bg_color}, {dark_theme_bg_accent}) !important;
        color: {text_color_yellow} !important;
        font-family: 'Inter', sans-serif;
    }}
    p, li, span, div {{
        color: {text_color_yellow};
    }}
    a, a:visited {{
        color: {text_color_blue} !important;
        text-decoration: none;
    }}
    a:hover {{
        color: #5DADE2 !important; /* secondary_accent_blue_lighter */
        text-decoration: underline;
    }}

    .gradient-text {{
        background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 50%, {secondary_accent_blue} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
    }}

    .main-header {{ font-size: 3.0rem; font-weight: 700; margin-bottom: 0.5rem; text-align: center; }}
    .sub-header {{ font-size: 1.1rem; color: {text_color_blue} !important; opacity: 0.9; text-align: center; margin-bottom: 2rem; }}

    .section-header {{
        font-size: 2.0rem;
        color: {primary_accent_pink} !important;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        font-weight: 700;
        text-align: center;
        text-shadow: 0 0 8px rgba({int(primary_accent_pink[1:3],16)}, {int(primary_accent_pink[3:5],16)}, {int(primary_accent_pink[5:7],16)}, 0.3);
    }}

    .stChatMessage {{
        background: {card_bg_color};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 0.8rem;
        border: 1px solid {card_border_color};
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }}
     .stChatMessage p, .stChatMessage li, .stChatMessage span, .stChatMessage div {{
        color: {text_color_yellow} !important;
    }}

    div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message {{
        background: {analysis_done_chat_bg} !important;
        border: 1px solid {secondary_accent_blue} !important;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: -0.2rem -0.8rem; /* Adjust if it causes layout issues */
    }}
    div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message *,
    div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message p,
    div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message li,
    div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message span {{
        color: {text_color_yellow} !important;
    }}

    .highlight-disease {{
        color: {text_color_yellow} !important;
        font-weight: bold;
        font-size: 1.4em;
        display: block;
        text-align: center;
        margin-bottom: 0.75rem;
        padding: 0.3rem;
        border-radius: 5px;
    }}

    /* Medication specific styling from previous iteration */
    .medication-item {{
        background-color: rgba(43, 134, 197, 0.2); 
        border: 1px solid rgba(255, 60, 172, 0.3); 
        border-left: 5px solid {highlight_color_medication}; 
        padding: 12px 15px; 
        margin-bottom: 15px; 
        border-radius: 8px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
    }}
    .medication-item p {{ margin-bottom: 0.4rem !important; line-height: 1.5; }}
    .medication-item .med-drug-name strong {{ color: {highlight_color_medication} !important; font-size: 1.15em; display: block; margin-bottom: 0.3rem; }}
    .medication-item .med-purpose span {{ color: {highlight_color_med_purpose} !important; }}
    .medication-item .med-dosage span {{ color: {highlight_color_med_dosage} !important; font-style: italic; }}
    .medication-item .med-dosage em {{ font-size: 0.85em; opacity: 0.8; }}
    .medication-item .med-notes span {{ color: {highlight_color_med_notes} !important; }}


    .treatment-guidance-subheader {{
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 0.8rem;
        margin-bottom: 0.6rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid {card_border_color};
    }}
    .pharma-header {{ color: {text_color_blue} !important; }}
    .lifestyle-header {{ color: {text_color_blue} !important; }}
    .dietary-header {{ color: {text_color_yellow} !important; }}
    .dos-donts-header {{ color: {text_color_blue} !important; }}
    .redflags-header {{ color: {primary_accent_pink} !important; }}

    .symptoms-analyzed-box {{
        background-color: rgba(20, 30, 48, 0.6);
        border: 1px solid {secondary_accent_blue};
        border-radius: 8px;
        padding: 12px 15px;
        margin-bottom: 18px;
        font-size: 0.95em;
    }}
    .symptoms-analyzed-box b {{ color: {text_color_blue} !important; font-weight: 700; }}
    .symptom-item {{
        display: inline-block;
        background-color: {secondary_accent_blue};
        color: {text_color_yellow} !important;
        padding: 4px 10px;
        border-radius: 15px;
        margin: 4px;
        font-size: 0.9em;
        border: 1px solid {primary_accent_pink};
    }}

    .disclaimer-box {{
        background-color: rgba(36, 59, 85, 0.3);
        border: 1px dashed {primary_accent_pink};
        color: {text_color_blue} !important;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1.5rem;
        font-size: 0.85em;
    }}
    .disclaimer-box i b {{ color: {primary_accent_pink} !important; }}

    .stButton > button {{
        background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
        color: {text_color_yellow} !important;
        border: none;
        border-radius: 0.5rem;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }}
    .stButton > button:hover {{
        transform: translateY(-3px) scale(1.03);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.25);
        filter: brightness(1.1);
    }}

    div[data-testid="stFileUploader"] section {{
         background-color: {card_bg_color};
         border: 1px dashed {primary_accent_pink};
         border-radius: 0.5rem;
         padding: 1rem;
    }}
     div[data-testid="stFileUploader"] section small {{ color: {text_color_blue} !important; }}

    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
    }}

    .stChatInput > div > div > textarea {{
        background-color: {card_bg_color};
        border: 1px solid {card_border_color};
        border-radius: 0.5rem;
        color: {text_color_yellow} !important;
        padding: 1rem;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }}
    .stChatInput > div > div > textarea:focus {{
        border: 1px solid {primary_accent_pink};
        box-shadow: 0 0 0 3px rgba({int(primary_accent_pink[1:3],16)},{int(primary_accent_pink[3:5],16)},{int(primary_accent_pink[5:7],16)},0.25);
    }}

    section[data-testid="stSidebar"] > div:first-child {{
        background-color: {bg_color} !important;
        background-image: linear-gradient(to bottom right, {bg_color}, {dark_theme_bg_accent}) !important;
        border-right: 1px solid {card_border_color} !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] li,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-baseweb="input"] > div,
    section[data-testid="stSidebar"] {{
        color: {text_color_yellow} !important;
    }}
    section[data-testid="stSidebar"] a {{ color: {text_color_blue} !important; }}
    section[data-testid="stSidebar"] .stHeadingContainer h2 {{ 
        text-align: center;
        color: {primary_accent_pink} !important;
    }}
    section[data-testid="stSidebar"] .stImage {{
        margin-left: auto;
        margin-right: auto;
        display: block;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
        color: {text_color_yellow} !important;
    }}
    section[data-testid="stSidebar"] .stAlert {{
        border-radius: 0.5rem;
        border-left-width: 5px !important;
        background-color: rgba(0,0,0,0.3) !important;
        margin-left: 0.5rem;
        margin-right: 0.5rem;
    }}
    section[data-testid="stSidebar"] .stAlert p {{ color: {text_color_yellow} !important; }}
    section[data-testid="stSidebar"] .stAlert[data-baseweb="alert"][role="status"] {{ border-left-color: #4CAF50 !important; }} /* Success */
    section[data-testid="stSidebar"] .stAlert[data-baseweb="alert"][role="note"] {{ border-left-color: {secondary_accent_blue} !important; }} /* Info */
    section[data-testid="stSidebar"] .stAlert[data-baseweb="alert"][role="alert"] {{ border-left-color: #F44336 !important; }} /* Error / Warning */


    .streamlit-expanderHeader {{
        background: {expander_header_bg_color} !important;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 0.7rem !important;
        color: {text_color_yellow} !important;
        border: 1px solid {card_border_color} !important;
        padding: 0.9rem 1.2rem !important;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .streamlit-expanderContent {{
        background-color: {expander_content_bg_color} !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 0 0 0.7rem 0.7rem !important;
        border: 1px solid {card_border_color} !important;
        border-top: none !important;
        padding: 1.5rem;
    }}
    .streamlit-expanderContent p, .streamlit-expanderContent li, .streamlit-expanderContent span, .streamlit-expanderContent div {{
        color: {text_color_yellow} !important;
    }}
    .streamlit-expanderContent strong {{
        color: {text_color_blue} !important;
    }}
    .streamlit-expanderHeader > div > svg {{
        fill: {text_color_yellow} !important;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: rgba(20, 30, 48, 0.3); border-radius: 10px; }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
        border-radius: 10px;
        border: 2px solid rgba(20, 30, 48, 0.3);
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, {primary_accent_pink} 30%, {secondary_accent_purple} 100%);
        filter: brightness(1.2);
    }}

    .dos-list ul, .donts-list ul {{ list-style-type: none; padding-left: 0; }}
    .dos-list li::before {{ content: '👍'; color: {highlight_color_positive_icon}; font-weight: bold; display: inline-block; width: 1.5em; margin-left: -1.5em; }}
    .dos-list li {{ color: {text_color_yellow} !important; }}
    .donts-list li::before {{ content: '👎'; color: {highlight_color_negative_icon}; font-weight: bold; display: inline-block; width: 1.5em; margin-left: -1.5em; }}
    .donts-list li {{ color: {text_color_yellow} !important; }}
    .foods-eat-list ul, .foods-avoid-list ul {{ list-style-type: none; padding-left: 0; }}
    .foods-eat-list li::before {{ content: '✅ '; color: {highlight_color_positive_icon}; font-weight: bold; }}
    .foods-eat-list li {{ color: {text_color_yellow} !important; }}
    .foods-avoid-list li::before {{ content: '❌ '; color: {highlight_color_negative_icon}; font-weight: bold; }}
    .foods-avoid-list li {{ color: {text_color_yellow} !important; }}
    .foods-eat-list-title, .foods-avoid-list-title {{ color: {text_color_yellow} !important; }}
    .dos-list-title, .donts-list-title {{ color: {text_color_blue} !important; }}
</style>
""", unsafe_allow_html=True)


# --- Load Environment Variables ---
load_dotenv() 
if not OPENAI_API_KEY: 
    st.error("OpenAI API key not found. Please set it in your .env file or environment variables.")
    st.stop()

if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
if not os.path.exists(ASSETS_DIR): os.makedirs(ASSETS_DIR)

# --- Session State ---
if "vector_store_loaded" not in st.session_state: st.session_state.vector_store_loaded = False
if "vector_store" not in st.session_state: st.session_state.vector_store = None
if "processed_pdf_name" not in st.session_state: st.session_state.processed_pdf_name = None
if "kb_init_attempted_this_session" not in st.session_state: st.session_state.kb_init_attempted_this_session = False

if "messages" not in st.session_state:
    # This message will be updated by initialize_vector_store or subsequent actions
    st.session_state["messages"] = [{"role": "assistant", "content": "Initializing Medical Advisor..."}]


# --- Default "Not Found" Messages for Parser and Display Logic ---
DEFAULT_MSG_PREDICTED_DISEASE = "Not specified by AI or not clearly identified from the context."
DEFAULT_MSG_REASONING = "Reasoning not provided or an error occurred parsing the response."
DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK = "Information not available in provided context for specific medications. Please consult a healthcare professional for medication options."
DEFAULT_MSG_LIFESTYLE = "Specific lifestyle and home care guidance not found in the provided documents for the current query. Please consult a healthcare professional for personalized advice."
DEFAULT_MSG_DIETARY = "Specific dietary recommendations not found in the provided documents for the current query. Please consult a healthcare professional for personalized advice."
DEFAULT_MSG_DOS_DONTS = "Specific Do's & Don'ts not found in the provided documents for the current query. Please consult a healthcare professional for personalized advice."
DEFAULT_MSG_SEEK_HELP = "Always consult a doctor if symptoms are severe, worsen, or if you have any concerns."
DEFAULT_MSG_DISCLAIMER = """This information is for educational purposes only and not a substitute for professional medical advice, diagnosis, or treatment.
Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
Never disregard professional medical advice or delay in seeking it because of something you have read from this chatbot.
Medication details are illustrative and NOT a prescription; consult your doctor for any medication."""

# --- Helper Function to Parse LLM Response (ADAPTED FOR NEW PROMPT) ---
def parse_llm_response(response_text):
    parsed_data = {
        "predicted_disease": DEFAULT_MSG_PREDICTED_DISEASE,
        "reasoning": DEFAULT_MSG_REASONING,
        "pharmacological": DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK,
        "medications_list": [],
        "non_pharmacological_lifestyle": DEFAULT_MSG_LIFESTYLE,
        "dietary_recommendations": DEFAULT_MSG_DIETARY,
        "foods_to_eat": "", "foods_to_avoid": "",
        "general_dos_donts": DEFAULT_MSG_DOS_DONTS,
        "dos": "", "donts": "",
        "when_to_seek_help": DEFAULT_MSG_SEEK_HELP,
        "disclaimer": DEFAULT_MSG_DISCLAIMER
    }

    disease_match = re.search(r"\*\*Predicted Disease:\*\*\s*(.*?)(?=\n\s*\*\*Reasoning:\*\*|\n\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
    if disease_match and disease_match.group(1).strip(): parsed_data["predicted_disease"] = disease_match.group(1).strip()

    reasoning_match = re.search(r"\*\*Reasoning:\*\*\s*(.*?)(?=\n\s*\*\*Treatment Guidance:\*\*|\n\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
    if reasoning_match and reasoning_match.group(1).strip(): parsed_data["reasoning"] = reasoning_match.group(1).strip()

    disclaimer_match = re.search(r"\*\*Disclaimer:\*\*\s*(.*?)(?:\n\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
    if disclaimer_match and disclaimer_match.group(1).strip(): parsed_data["disclaimer"] = disclaimer_match.group(1).strip()

    treatment_guidance_block_match = re.search(r"\*\*Treatment Guidance:\*\*\s*(.*?)(?=\n\s*\*\*Disclaimer:\*\*|\n\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
    if treatment_guidance_block_match:
        treatment_text = treatment_guidance_block_match.group(1).strip()
        section_headers_raw = [r"Pharmacological \(Medications\):", r"Non-Pharmacological & Lifestyle:", r"Dietary Recommendations:", r"General Do's & Don'ts:", r"When to Seek Professional Help \(Red Flags\):"]
        all_next_headers_lookahead_parts = [r"^\s*\*\*" + re.escape(header_part) + r"\*\*" for header_part in section_headers_raw]
        combined_lookahead = r"(?:" + "|".join(all_next_headers_lookahead_parts) + r"|\n\n\n|\Z)"

        pharma_block_match = re.search(r"^\s*\*\*Pharmacological \(Medications\):\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if pharma_block_match and pharma_block_match.group(1).strip():
            pharma_content = pharma_block_match.group(1).strip()
            parsed_data["pharmacological"] = pharma_content
            med_items = re.findall(r"^\s*-\s*\*\*Drug Name:\*\*\s*(.*?)\n\s*-\s*\*\*Purpose:\*\*\s*(.*?)\n(?:\s*-\s*\*\*Common Dosage(?: \(Example Only - Emphasize to consult doctor\))?:\*\*\s*(.*?)\n)?(?:\s*-\s*\*\*Important Notes:\*\*\s*(.*?)(?=\n\s*-|\n\n\n|\Z))?", pharma_content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if med_items:
                parsed_data["medications_list"] = [{"drug_name": i[0].strip() or "N/A", "purpose": i[1].strip() or "N/A", "dosage": i[2].strip() if i[2] else "Consult doctor.", "notes": i[3].strip() if i[3] else "N/A"} for i in med_items]
            elif "consult a doctor" not in pharma_content.lower() and "information not available" not in pharma_content.lower(): pass
            else: parsed_data["pharmacological"] = DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK
        
        non_pharma_match = re.search(r"^\s*\*\*Non-Pharmacological & Lifestyle:\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if non_pharma_match and non_pharma_match.group(1).strip(): parsed_data["non_pharmacological_lifestyle"] = non_pharma_match.group(1).strip()

        diet_full_match = re.search(r"^\s*\*\*Dietary Recommendations:\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if diet_full_match and diet_full_match.group(1).strip():
            diet_text = diet_full_match.group(1).strip(); parsed_data["dietary_recommendations"] = diet_text
            eat_match = re.search(r"^\s*-\s*\*\*Foods to Eat:\*\*\s*(.*?)(?=\n\s*-\s*\*\*Foods to Avoid:\*\*|\n\n\n|\Z)", diet_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if eat_match and eat_match.group(1).strip(): parsed_data["foods_to_eat"] = "\n".join([li.strip("-* ").strip() for li in eat_match.group(1).strip().splitlines() if li.strip("-* ").strip()])
            avoid_match = re.search(r"^\s*-\s*\*\*Foods to Avoid:\*\*\s*(.*?)(?:\n\n\n|\Z)", diet_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if avoid_match and avoid_match.group(1).strip(): parsed_data["foods_to_avoid"] = "\n".join([li.strip("-* ").strip() for li in avoid_match.group(1).strip().splitlines() if li.strip("-* ").strip()])

        dos_donts_full_match = re.search(r"^\s*\*\*General Do's & Don'ts:\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if dos_donts_full_match and dos_donts_full_match.group(1).strip():
            dos_donts_text = dos_donts_full_match.group(1).strip(); parsed_data["general_dos_donts"] = dos_donts_text
            do_match = re.search(r"^\s*-\s*\*\*Do:\*\*\s*(.*?)(?=\n\s*-\s*\*\*Don't:\*\*|\n\n\n|\Z)", dos_donts_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if do_match and do_match.group(1).strip(): parsed_data["dos"] = "\n".join([li.strip("-* ").strip() for li in do_match.group(1).strip().splitlines() if li.strip("-* ").strip()])
            dont_match = re.search(r"^\s*-\s*\*\*Don't:\*\*\s*(.*?)(?:\n\n\n|\Z)", dos_donts_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if dont_match and dont_match.group(1).strip(): parsed_data["donts"] = "\n".join([li.strip("-* ").strip() for li in dont_match.group(1).strip().splitlines() if li.strip("-* ").strip()])

        seek_help_match = re.search(r"^\s*\*\*When to Seek Professional Help \(Red Flags\):\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if seek_help_match and seek_help_match.group(1).strip(): parsed_data["when_to_seek_help"] = seek_help_match.group(1).strip()
    return parsed_data

# --- Functions ---
def initialize_vector_store():
    """
    Initializes the vector store.
    1. Tries to load an existing FAISS store.
    2. If not found, tries to load and process 'Medical_book.pdf' from DATA_DIR.
    Updates session state for vector_store, vector_store_loaded, processed_pdf_name, and messages.
    Spinners and messages related to this process will appear in the sidebar.
    """
    # 1. Try to load an existing FAISS store
    # st.sidebar.info("Checking for existing knowledge base...") # Spinner is better
    with st.spinner("Checking for existing knowledge base..."): # Spinner in sidebar
        vs = load_existing_faiss_store()
        if vs:
            st.session_state.vector_store = vs
            st.session_state.vector_store_loaded = True
            st.session_state.processed_pdf_name = "Previously processed medical texts (FAISS)"
            st.session_state.messages = [{"role": "assistant", "content": "Welcome! Existing medical knowledge base (FAISS) active. How can I assist?"}]
            # Success message will be handled by the main sidebar logic after this function returns
            return

    # 2. If no existing store, try to load and process default PDF
    default_pdf_name = "Medical_book.pdf"
    default_pdf_path = os.path.join(DATA_DIR, default_pdf_name)

    if os.path.exists(default_pdf_path):
        # st.sidebar.info(f"Found '{default_pdf_name}'. Attempting to load...") # Spinner is better
        with st.spinner(f"Processing default KB: '{default_pdf_name}'... This may take a few moments."): # Spinner in sidebar
            try:
                processed_vs = load_and_process_pdf_to_faiss(default_pdf_path)
                if processed_vs:
                    st.session_state.vector_store = processed_vs
                    st.session_state.vector_store_loaded = True
                    st.session_state.processed_pdf_name = default_pdf_name
                    st.session_state.messages = [{"role": "assistant", "content": f"Welcome! Knowledge base from '{default_pdf_name}' (FAISS) is ready. How can I assist?"}]
                else: # Processing failed, but file existed
                    st.session_state.vector_store = None
                    st.session_state.vector_store_loaded = False
                    st.session_state.processed_pdf_name = None # Mark as failed to load default
                    st.session_state.messages = [{"role": "assistant", "content": f"Welcome! Could not process default PDF '{default_pdf_name}'. Please upload a medical reference PDF to begin."}]
            except Exception as e:
                st.session_state.vector_store = None
                st.session_state.vector_store_loaded = False
                st.session_state.processed_pdf_name = None # Mark as failed to load default
                st.session_state.messages = [{"role": "assistant", "content": f"Welcome! Error processing default PDF '{default_pdf_name}'. Please upload a medical reference PDF to begin."}]
                print(f"ERROR in initialize_vector_store processing default PDF '{default_pdf_name}': {traceback.format_exc()}")
    else:
        # Default PDF not found, and no existing store
        st.session_state.vector_store = None
        st.session_state.vector_store_loaded = False
        st.session_state.processed_pdf_name = None # Mark as default not found
        # Update message only if it's still the generic "Initializing..."
        if len(st.session_state.messages) == 1 and "Initializing" in st.session_state.messages[0]["content"]:
             st.session_state.messages = [{"role": "assistant", "content": "Welcome! Default 'Medical_book.pdf' not found. Please upload a medical reference PDF to begin."}]

# --- UI Layout ---
st.markdown(f"""<div style="text-align: center; padding-top: 2rem; padding-bottom: 1rem;"><h1 class='main-header'><span class='gradient-text'>Tata MD AI Medical Advisor</span></h1><p class='sub-header'>Leveraging medical literature to offer insights on symptoms. <br><em>This tool provides information for educational purposes only and is not a substitute for professional medical advice.</em></p></div>""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    logo_path = os.path.join(ASSETS_DIR, "tatmd.png")
    default_logo_url = "https://www.tatamd.com/images/logo_TATA%20MD.svg"
    if os.path.exists(logo_path): st.image(logo_path, width=180, use_container_width=False)
    else: st.markdown(f"""<div style="text-align: center; margin-bottom: 1rem;"><img src="{default_logo_url}" alt="TATA MD Logo" style="width: 180px; margin-bottom: 10px;" onerror="this.style.display='none'; this.parentElement.innerHTML+='<p style=\'color:{text_color_yellow};\'>TATA MD Logo</p>';"></div>""", unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align: center; color: {primary_accent_pink}; margin-bottom: 1rem;'>Knowledge Base</h2>", unsafe_allow_html=True)

    # Initialize KB on first run if not already attempted for this session
    if not st.session_state.kb_init_attempted_this_session:
        initialize_vector_store() # This function handles its own spinners and updates session state
        st.session_state.kb_init_attempted_this_session = True
        st.rerun() # Rerun to ensure messages and UI reflect the initialization immediately

    # Display current KB status based on session state
    if st.session_state.vector_store_loaded:
        st.success(f"Active KB: {st.session_state.processed_pdf_name or 'Loaded Successfully'}")
    elif st.session_state.processed_pdf_name is None and not st.session_state.vector_store_loaded:
        # This condition implies default PDF was either not found or failed to load
        default_pdf_name_check = "Medical_book.pdf"
        default_pdf_path_check = os.path.join(DATA_DIR, default_pdf_name_check)
        if not os.path.exists(default_pdf_path_check):
            st.warning(f"Default '{default_pdf_name_check}' not found in 'data/' folder. Please upload a PDF.")
        else: # Default PDF exists but failed to load
            st.error(f"Failed to load default KB '{default_pdf_name_check}'. Please upload a PDF or check the file.")
    else: # Catch-all for other unloaded states
        st.info("No active Knowledge Base. Please upload a PDF.")

    uploaded_file_sb = st.file_uploader("Upload New Medical Reference (PDF)", type="pdf", key="pdf_uploader_sidebar")
    if st.button("Process PDF & Build KB", key="process_button_sidebar", help="Upload and process a new PDF to create or update the knowledge base."):
        if uploaded_file_sb is not None:
            file_path = os.path.join(DATA_DIR, uploaded_file_sb.name)
            with open(file_path, "wb") as f: f.write(uploaded_file_sb.getbuffer())
            
            # Clear previous KB state before processing new one
            st.session_state.vector_store = None
            st.session_state.vector_store_loaded = False
            st.session_state.processed_pdf_name = None
            
            with st.spinner(f"Processing {uploaded_file_sb.name}... This may take a while."): # Spinner in sidebar
                processed_vs = load_and_process_pdf_to_faiss(file_path)
                if processed_vs:
                    st.session_state.vector_store = processed_vs
                    st.session_state.vector_store_loaded = True
                    st.session_state.processed_pdf_name = uploaded_file_sb.name
                    st.session_state.messages = [{"role": "assistant", "content": f"Knowledge base from '{uploaded_file_sb.name}' (FAISS) is ready. How can I assist?"}]
                else:
                    st.session_state.messages.append({"role": "assistant", "content": f"Failed to process '{uploaded_file_sb.name}'. Please try again or use a different PDF."})
                    # Error message displayed by the KB status logic on rerun
            st.rerun() # Rerun to reflect changes immediately
        else:
            st.warning("Please upload a PDF file first.")
            
    st.markdown("---"); st.markdown(f"<p style='font-size: 0.8em; text-align: center; opacity: 0.7; color: {text_color_blue} !important;'>Powered by Advanced AI</p>", unsafe_allow_html=True)

# --- Main Chat Interface ---
st.markdown("<div class='section-header'>Symptom Analysis & Guidance</div>", unsafe_allow_html=True)
chat_container = st.container()
with chat_container:
    for i, msg in enumerate(st.session_state.messages):
        is_structured_response = isinstance(msg["content"], dict) and "predicted_disease" in msg["content"]
        with st.chat_message(msg["role"], avatar="🧑‍⚕️" if msg["role"] == "assistant" else "👤"):
            if msg["role"] == "user": st.markdown(f"<div style='text-align: right; color: {text_color_yellow} !important; padding: 0.5rem;'>{msg['content']}</div>", unsafe_allow_html=True)
            elif is_structured_response:
                st.markdown("<div class='analysis-complete-message'>", unsafe_allow_html=True)
                data = msg["content"]
                symptoms_input_string = data.get("symptoms_input", "")
                if symptoms_input_string:
                    s_list = [s.strip() for s in re.split(r'[,\n]', symptoms_input_string) if s.strip()]
                    if not s_list and symptoms_input_string: s_list = [symptoms_input_string.strip()]
                    s_html = "".join([f"<div class='symptom-item'>{s}</div>" for s in s_list])
                    st.markdown(f"<div class='symptoms-analyzed-box'><b>Symptoms Analyzed:</b>{s_html}</div>", unsafe_allow_html=True)
                st.markdown(f"##### <span class='highlight-disease'>{data.get('predicted_disease', DEFAULT_MSG_PREDICTED_DISEASE)}</span>", unsafe_allow_html=True)
                r_content = data.get('reasoning', DEFAULT_MSG_REASONING).strip()
                if r_content and r_content != DEFAULT_MSG_REASONING and "not found" not in r_content.lower():
                    with st.expander("View Reasoning", expanded=False): st.markdown(r_content, unsafe_allow_html=True)
                else: st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_REASONING}</p>", unsafe_allow_html=True)
                st.markdown(f"<hr style='border-color: {card_border_color}; margin-top:1rem; margin-bottom:1rem;'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='color: {text_color_yellow}; text-align:center; margin-bottom:1rem;'>Treatment Guidance</h4>", unsafe_allow_html=True)
                with st.expander("💊 Pharmacological (Medications)", expanded=True):
                    st.markdown(f"<div class='treatment-guidance-subheader pharma-header'>Medications</div>", unsafe_allow_html=True)
                    med_list = data.get('medications_list', []); pharma_fb = data.get('pharmacological', DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK).strip()
                    if med_list:
                        for med in med_list:
                            med_h = "<div class='medication-item'>"
                            med_h += f"<p class='med-drug-name'><strong>{med.get('drug_name', 'N/A')}</strong></p>"
                            if med.get('purpose') and med.get('purpose') != 'N/A': med_h += f"<p class='med-purpose'>Purpose: <span>{med.get('purpose')}</span></p>"
                            d_txt = med.get('dosage', 'Consult doctor.')
                            if d_txt and d_txt not in ['N/A', 'Consult doctor.', 'Consult doctor for dosage.']: med_h += f"<p class='med-dosage'>Dosage Example: <span>{d_txt}</span> <em>(Not medical advice)</em></p>"
                            if med.get('notes') and med.get('notes') != 'N/A': med_h += f"<p class='med-notes'>Notes: <span>{med.get('notes')}</span></p>"
                            med_h += "</div>"; st.markdown(med_h, unsafe_allow_html=True)
                    elif pharma_fb and pharma_fb != DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK and "not available" not in pharma_fb.lower(): st.markdown(pharma_fb, unsafe_allow_html=True)
                    else: st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK}</p>", unsafe_allow_html=True)
                with st.expander("🌿 Non-Pharmacological & Lifestyle"):
                    st.markdown(f"<div class='treatment-guidance-subheader lifestyle-header'>Lifestyle & Home Care</div>", unsafe_allow_html=True)
                    c = data.get('non_pharmacological_lifestyle', DEFAULT_MSG_LIFESTYLE).strip()
                    if c and c != DEFAULT_MSG_LIFESTYLE and "not available" not in c.lower(): st.markdown(c, unsafe_allow_html=True)
                    else: st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_LIFESTYLE}</p>", unsafe_allow_html=True)
                with st.expander("🥗 Dietary Recommendations"):
                    st.markdown(f"<div class='treatment-guidance-subheader dietary-header'>Dietary Advice</div>", unsafe_allow_html=True)
                    e_items = data.get("foods_to_eat","").strip().splitlines(); a_items = data.get("foods_to_avoid","").strip().splitlines()
                    e_md = f"<strong class='foods-eat-list-title'>Foods to Eat:</strong><div class='foods-eat-list'><ul>" + "".join([f"<li>{i.strip()}</li>" for i in e_items if i.strip()]) + "</ul></div>" if any(i.strip() for i in e_items) else ""
                    a_md = f"<strong class='foods-avoid-list-title'>Foods to Avoid:</strong><div class='foods-avoid-list'><ul>" + "".join([f"<li>{i.strip()}</li>" for i in a_items if i.strip()]) + "</ul></div>" if any(i.strip() for i in a_items) else ""
                    if e_md or a_md:
                        if e_md: st.markdown(e_md, unsafe_allow_html=True)
                        if a_md: st.markdown(a_md, unsafe_allow_html=True)
                    else:
                        c = data.get('dietary_recommendations', DEFAULT_MSG_DIETARY).strip()
                        if c and c != DEFAULT_MSG_DIETARY and "not available" not in c.lower(): st.markdown(c, unsafe_allow_html=True)
                        else: st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_DIETARY}</p>", unsafe_allow_html=True)
                with st.expander("👍👎 General Do's & Don'ts"):
                    st.markdown(f"<div class='treatment-guidance-subheader dos-donts-header'>General Advice</div>", unsafe_allow_html=True)
                    d_items = data.get("dos","").strip().splitlines(); dn_items = data.get("donts","").strip().splitlines()
                    d_md = f"<strong class='dos-list-title'>Do:</strong><div class='dos-list'><ul>" + "".join([f"<li>{i.strip()}</li>" for i in d_items if i.strip()]) + "</ul></div>" if any(i.strip() for i in d_items) else ""
                    dn_md = f"<strong class='donts-list-title'>Don't:</strong><div class='donts-list'><ul>" + "".join([f"<li>{i.strip()}</li>" for i in dn_items if i.strip()]) + "</ul></div>" if any(i.strip() for i in dn_items) else ""
                    if d_md or dn_md:
                        if d_md: st.markdown(d_md, unsafe_allow_html=True)
                        if dn_md: st.markdown(dn_md, unsafe_allow_html=True)
                    else:
                        c = data.get('general_dos_donts', DEFAULT_MSG_DOS_DONTS).strip()
                        if c and c != DEFAULT_MSG_DOS_DONTS and "not available" not in c.lower(): st.markdown(c, unsafe_allow_html=True)
                        else: st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_DOS_DONTS}</p>", unsafe_allow_html=True)
                with st.expander("🚨 When to Seek Professional Help (Red Flags)", expanded=True):
                    st.markdown(f"<div class='treatment-guidance-subheader redflags-header'>Urgent Care / Red Flags</div>", unsafe_allow_html=True)
                    c = data.get('when_to_seek_help', DEFAULT_MSG_SEEK_HELP).strip()
                    if c and c != DEFAULT_MSG_SEEK_HELP and "always consult" not in c.lower(): st.error(c) # Use st.error for red flags to make them stand out
                    else: st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_SEEK_HELP}</p>", unsafe_allow_html=True)
                st.markdown(f"<hr style='border-color: {card_border_color}; margin-top:1.5rem; margin-bottom:1rem;'>", unsafe_allow_html=True)
                st.markdown("<div class='disclaimer-box'>" + f"<i><b>Disclaimer:</b> {data.get('disclaimer', DEFAULT_MSG_DISCLAIMER)}</i>" + "</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else: st.markdown(f"<div style='padding: 0.5rem; color: {text_color_yellow} !important;'>{str(msg['content'])}</div>", unsafe_allow_html=True)

if user_symptoms := st.chat_input("Describe symptoms (e.g., 'fever, persistent cough, body aches')...", key="symptom_input_main"):
    if not st.session_state.vector_store_loaded or st.session_state.vector_store is None:
        st.session_state.messages.append({"role": "user", "content": user_symptoms})
        st.session_state.messages.append({"role": "assistant", "content": "⚠️ Please ensure a medical reference PDF is successfully loaded first to enable symptom analysis. Check sidebar for KB status."})
    else:
        st.session_state.messages.append({"role": "user", "content": user_symptoms})
        with st.status("🧑‍⚕️ AI Advisor is thinking...", expanded=True) as status_ui:
            st.write("Reviewing symptoms against medical knowledge base...")
            try:
                raw_response = query_rag_pipeline_faiss(user_symptoms, st.session_state.vector_store) # Uses FAISS function
                st.write("Received response from AI, now parsing and formatting...")
                print(f"\n--- RAW LLM Response (from RAG pipeline) START ---\n{raw_response}\n--- RAW LLM Response (from RAG pipeline) END ---\n")
                parsed_response_data = parse_llm_response(raw_response)
                print(f"\n--- Parsed Response Data (for UI) START ---\n{json.dumps(parsed_response_data, indent=2)}\n--- Parsed Response Data (for UI) END ---\n")
                assistant_response_content = {"symptoms_input": user_symptoms, **parsed_response_data}
                st.session_state.messages.append({"role": "assistant", "content": assistant_response_content})
                status_ui.update(label="Guidance ready!", state="complete", expanded=False)
            except Exception as e:
                detailed_error_message = f"An error occurred during analysis: {str(e)}. Traceback: {traceback.format_exc()}"
                st.session_state.messages.append({"role": "assistant", "content": "Sorry, an unexpected error occurred while processing your request."})
                status_ui.update(label="Error processing request.", state="error", expanded=True)
                st.error("An internal error occurred. Please try again later or check logs.") # Show error in main app
                print(f"ERROR in Streamlit chat input processing: {detailed_error_message}")
    st.rerun()

st.markdown(f"""<div style="position: fixed; bottom: 0; left: 0; right: 0; background: rgba({int(bg_color[1:3], 16)}, {int(bg_color[3:5], 16)}, {int(bg_color[5:7], 16)}, 0.9); backdrop-filter: blur(5px); padding: 0.5rem; text-align: center; border-top: 1px solid {card_border_color}; z-index: 99;"><p style="margin: 0; font-size: 0.8rem; opacity: 0.7; color: {text_color_blue} !important;">Tata MD AI Medical Advisor © {datetime.now().year} - For Informational Purposes Only</p></div>""", unsafe_allow_html=True)

