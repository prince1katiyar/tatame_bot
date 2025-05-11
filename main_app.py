# # medical_rag_chatbot/main_app.py

# import streamlit as st
# import os
# from dotenv import load_dotenv
# import re
# from datetime import datetime
# import json
# # Removed import sqlite3 as it was just for displaying version
# # import sqlite3
# # import streamlit as st # Streamlit already imported

# # st.write(f"SQLite version: {sqlite3.sqlite_version}") # Not needed for FAISS

# # --- Define SCRIPT_DIR, ASSETS_DIR, DATA_DIR first for robustness ---
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
# DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# # Make sure rag_pipeline and utils are found by adding SCRIPT_DIR to sys.path
# import sys
# if SCRIPT_DIR not in sys.path:
#     sys.path.append(SCRIPT_DIR)

# try:
#     # UPDATED TO FAISS FUNCTION NAMES
#     from rag_pipeline import (
#         load_and_process_pdf_to_faiss,
#         query_rag_pipeline_faiss,
#         load_existing_faiss_store,
#         OPENAI_API_KEY
#     )
# except ImportError as e:
#     st.error(
#         f"Critical Error: Could not import FAISS-specific functions from 'rag_pipeline.py'. "
#         f"Please ensure 'rag_pipeline.py' has been updated for FAISS and 'utils.py' are in the same directory "
#         f"as 'main_app.py' ({SCRIPT_DIR}) and all dependencies are installed. Specific error: {e}"
#     )
#     st.stop()

# # --- Page Configuration ---
# favicon_path = os.path.join(ASSETS_DIR, "favicon.png")
# st.set_page_config(
#     page_title="TATA md AI Medical Advisor",
#     page_icon=favicon_path if os.path.exists(favicon_path) else "🩺",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # --- Define Theme Colors (using your provided theme) ---
# bg_color = "#141E30"
# text_color_yellow = "#FFFACD"
# text_color_blue = "#87CEFA"
# primary_accent_pink = "#FF3CAC"
# secondary_accent_blue = "#2B86C5"
# secondary_accent_purple = "#784BA0"
# dark_theme_bg_accent = "#243B55"
# highlight_color_medication = "#FFB74D" # Orange for medication names
# highlight_color_med_purpose = "#AED581" # Light Green for purpose
# highlight_color_med_dosage = "#FFF176" # Light Yellow for dosage (use with caution)
# highlight_color_med_notes = "#BCAAA4" # Light Brown/Grey for notes
# highlight_color_positive_icon = "#66BB6A"
# highlight_color_negative_icon = "#EF5350"
# expander_header_bg_color = f"linear-gradient(135deg, rgba(255, 60, 172, 0.4) 0%, rgba(43, 134, 197, 0.5) 100%)"
# expander_content_bg_color = f"rgba(43, 134, 197, 0.15)"
# card_bg_color = f"rgba({int(secondary_accent_blue[1:3], 16)}, {int(secondary_accent_blue[3:5], 16)}, {int(secondary_accent_blue[5:7], 16)}, 0.4)"
# card_border_color = f"rgba({int(primary_accent_pink[1:3], 16)}, {int(primary_accent_pink[3:5], 16)}, {int(primary_accent_pink[5:7], 16)}, 0.3)"
# analysis_done_chat_bg = f"rgba({int(secondary_accent_blue[1:3], 16)}, {int(secondary_accent_blue[3:5], 16)}, {int(secondary_accent_blue[5:7], 16)}, 0.25)"


# # --- Custom CSS (Your provided CSS) ---
# st.markdown(f"""
# <style>
#     /* Base styles - Default text is Yellow */
#     body, .stApp, .stChatInput, .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{
#         background-color: {bg_color} !important;
#         background-image: linear-gradient(to bottom right, {bg_color}, {dark_theme_bg_accent}) !important;
#         color: {text_color_yellow} !important;
#         font-family: 'Inter', sans-serif;
#     }}
#     p, li, span, div {{
#         color: {text_color_yellow};
#     }}
#     a, a:visited {{
#         color: {text_color_blue} !important;
#         text-decoration: none;
#     }}
#     a:hover {{
#         color: #5DADE2 !important; /* secondary_accent_blue_lighter */
#         text-decoration: underline;
#     }}

#     .gradient-text {{
#         background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 50%, {secondary_accent_blue} 100%);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         background-clip: text;
#         font-weight: 800;
#     }}

#     .main-header {{ font-size: 3.0rem; font-weight: 700; margin-bottom: 0.5rem; text-align: center; }}
#     .sub-header {{ font-size: 1.1rem; color: {text_color_blue} !important; opacity: 0.9; text-align: center; margin-bottom: 2rem; }}

#     .section-header {{
#         font-size: 2.0rem;
#         color: {primary_accent_pink} !important;
#         margin-top: 2.5rem;
#         margin-bottom: 1.5rem;
#         font-weight: 700;
#         text-align: center;
#         text-shadow: 0 0 8px rgba({int(primary_accent_pink[1:3],16)}, {int(primary_accent_pink[3:5],16)}, {int(primary_accent_pink[5:7],16)}, 0.3);
#     }}

#     .stChatMessage {{
#         background: {card_bg_color};
#         backdrop-filter: blur(10px);
#         -webkit-backdrop-filter: blur(10px);
#         border-radius: 0.8rem;
#         border: 1px solid {card_border_color};
#         padding: 1.2rem 1.8rem;
#         margin-bottom: 1.2rem;
#         box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
#     }}
#      .stChatMessage p, .stChatMessage li, .stChatMessage span, .stChatMessage div {{
#         color: {text_color_yellow} !important;
#     }}

#     div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message {{
#         background: {analysis_done_chat_bg} !important;
#         border: 1px solid {secondary_accent_blue} !important;
#         padding: 1rem;
#         border-radius: 0.5rem;
#         margin: -0.2rem -0.8rem;
#     }}
#     div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message *,
#     div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message p,
#     div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message li,
#     div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message span {{
#         color: {text_color_yellow} !important;
#     }}

#     .highlight-disease {{
#         color: {text_color_yellow} !important;
#         font-weight: bold;
#         font-size: 1.4em;
#         display: block;
#         text-align: center;
#         margin-bottom: 0.75rem;
#         padding: 0.3rem;
#         border-radius: 5px;
#     }}

#     /* Medication specific styling */
#     .medication-item {{
#         border-left: 3px solid {highlight_color_medication};
#         padding-left: 10px;
#         margin-bottom: 15px;
#     }}
#     .medication-item .med-drug-name strong {{ color: {highlight_color_medication} !important; font-size: 1.1em; }}
#     .medication-item .med-purpose span {{ color: {highlight_color_med_purpose} !important; }}
#     .medication-item .med-dosage span {{ color: {highlight_color_med_dosage} !important; font-style: italic; }}
#     .medication-item .med-notes span {{ color: {highlight_color_med_notes} !important; }}
#     .medication-item p {{ margin-bottom: 0.3rem !important; }}


#     .treatment-guidance-subheader {{
#         font-size: 1.2rem;
#         font-weight: bold;
#         margin-top: 0.8rem;
#         margin-bottom: 0.6rem;
#         padding-bottom: 0.4rem;
#         border-bottom: 1px solid {card_border_color};
#     }}
#     .pharma-header {{ color: {text_color_blue} !important; }}
#     .lifestyle-header {{ color: {text_color_blue} !important; }}
#     .dietary-header {{ color: {text_color_yellow} !important; }}
#     .dos-donts-header {{ color: {text_color_blue} !important; }}
#     .redflags-header {{ color: {primary_accent_pink} !important; }}

#     .symptoms-analyzed-box {{
#         background-color: rgba(20, 30, 48, 0.6);
#         border: 1px solid {secondary_accent_blue};
#         border-radius: 8px;
#         padding: 12px 15px;
#         margin-bottom: 18px;
#         font-size: 0.95em;
#     }}
#     .symptoms-analyzed-box b {{ color: {text_color_blue} !important; font-weight: 700; }}
#     .symptom-item {{
#         display: inline-block;
#         background-color: {secondary_accent_blue};
#         color: {text_color_yellow} !important;
#         padding: 4px 10px;
#         border-radius: 15px;
#         margin: 4px;
#         font-size: 0.9em;
#         border: 1px solid {primary_accent_pink};
#     }}

#     .disclaimer-box {{
#         background-color: rgba(36, 59, 85, 0.3);
#         border: 1px dashed {primary_accent_pink};
#         color: {text_color_blue} !important;
#         padding: 1rem;
#         border-radius: 0.5rem;
#         margin-top: 1.5rem;
#         font-size: 0.85em;
#     }}
#     .disclaimer-box i b {{ color: {primary_accent_pink} !important; }}

#     .stButton > button {{
#         background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
#         color: {text_color_yellow} !important;
#         border: none;
#         border-radius: 0.5rem;
#         padding: 0.7rem 1.5rem;
#         font-weight: 600;
#         transition: all 0.3s ease;
#         box-shadow: 0 2px 5px rgba(0,0,0,0.2);
#     }}
#     .stButton > button:hover {{
#         transform: translateY(-3px) scale(1.03);
#         box-shadow: 0 12px 25px rgba(0, 0, 0, 0.25);
#         filter: brightness(1.1);
#     }}

#     div[data-testid="stFileUploader"] section {{
#          background-color: {card_bg_color};
#          border: 1px dashed {primary_accent_pink};
#          border-radius: 0.5rem;
#          padding: 1rem;
#     }}
#      div[data-testid="stFileUploader"] section small {{ color: {text_color_blue} !important; }}

#     .stProgress > div > div > div {{
#         background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
#     }}

#     .stChatInput > div > div > textarea {{
#         background-color: {card_bg_color};
#         border: 1px solid {card_border_color};
#         border-radius: 0.5rem;
#         color: {text_color_yellow} !important;
#         padding: 1rem;
#         box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
#     }}
#     .stChatInput > div > div > textarea:focus {{
#         border: 1px solid {primary_accent_pink};
#         box-shadow: 0 0 0 3px rgba({int(primary_accent_pink[1:3],16)},{int(primary_accent_pink[3:5],16)},{int(primary_accent_pink[5:7],16)},0.25);
#     }}

#     section[data-testid="stSidebar"] > div:first-child {{
#         background-color: {bg_color} !important;
#         background-image: linear-gradient(to bottom right, {bg_color}, {dark_theme_bg_accent}) !important;
#         border-right: 1px solid {card_border_color} !important;
#     }}
#     section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
#     section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] li,
#     section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] span,
#     section[data-testid="stSidebar"] label,
#     section[data-testid="stSidebar"] div[data-baseweb="input"] > div,
#     section[data-testid="stSidebar"] {{
#         color: {text_color_yellow} !important;
#     }}
#     section[data-testid="stSidebar"] a {{ color: {text_color_blue} !important; }}
#     section[data-testid="stSidebar"] .stHeadingContainer h2 {{ /* Changed from h2 to general heading for flexibility */
#         text-align: center;
#         color: {primary_accent_pink} !important;
#     }}
#     section[data-testid="stSidebar"] .stImage {{
#         margin-left: auto;
#         margin-right: auto;
#         display: block;
#     }}
#     section[data-testid="stSidebar"] .stButton > button {{
#         background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
#         color: {text_color_yellow} !important;
#     }}
#     section[data-testid="stSidebar"] .stAlert {{
#         border-radius: 0.5rem;
#         border-left-width: 5px !important;
#         background-color: rgba(0,0,0,0.3) !important;
#         margin-left: 0.5rem;
#         margin-right: 0.5rem;
#     }}
#     section[data-testid="stSidebar"] .stAlert p {{ color: {text_color_yellow} !important; }}
#     section[data-testid="stSidebar"] .stAlert[data-baseweb="alert"][role="status"] {{ border-left-color: #4CAF50 !important; }}
#     section[data-testid="stSidebar"] .stAlert[data-baseweb="alert"][role="note"] {{ border-left-color: {secondary_accent_blue} !important; }}
#     section[data-testid="stSidebar"] .stAlert[data-baseweb="alert"][role="alert"] {{ border-left-color: #F44336 !important; }}

#     .streamlit-expanderHeader {{
#         background: {expander_header_bg_color} !important;
#         backdrop-filter: blur(8px);
#         -webkit-backdrop-filter: blur(8px);
#         border-radius: 0.7rem !important;
#         color: {text_color_yellow} !important;
#         border: 1px solid {card_border_color} !important;
#         padding: 0.9rem 1.2rem !important;
#         font-weight: 600;
#         box-shadow: 0 2px 10px rgba(0,0,0,0.1);
#     }}
#     .streamlit-expanderContent {{
#         background-color: {expander_content_bg_color} !important;
#         backdrop-filter: blur(12px);
#         -webkit-backdrop-filter: blur(12px);
#         border-radius: 0 0 0.7rem 0.7rem !important;
#         border: 1px solid {card_border_color} !important;
#         border-top: none !important;
#         padding: 1.5rem;
#     }}
#     .streamlit-expanderContent p, .streamlit-expanderContent li, .streamlit-expanderContent span, .streamlit-expanderContent div {{
#         color: {text_color_yellow} !important;
#     }}
#     .streamlit-expanderContent strong {{
#         color: {text_color_blue} !important;
#     }}
#     .streamlit-expanderHeader > div > svg {{
#         fill: {text_color_yellow} !important;
#     }}

#     #MainMenu {{visibility: hidden;}}
#     footer {{visibility: hidden;}}

#     ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
#     ::-webkit-scrollbar-track {{ background: rgba(20, 30, 48, 0.3); border-radius: 10px; }}
#     ::-webkit-scrollbar-thumb {{
#         background: linear-gradient(180deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
#         border-radius: 10px;
#         border: 2px solid rgba(20, 30, 48, 0.3);
#     }}
#     ::-webkit-scrollbar-thumb:hover {{
#         background: linear-gradient(180deg, {primary_accent_pink} 30%, {secondary_accent_purple} 100%);
#         filter: brightness(1.2);
#     }}

#     .dos-list ul, .donts-list ul {{ list-style-type: none; padding-left: 0; }}
#     .dos-list li::before {{ content: '👍'; color: {highlight_color_positive_icon}; font-weight: bold; display: inline-block; width: 1.5em; margin-left: -1.5em; }}
#     .dos-list li {{ color: {text_color_yellow} !important; }}
#     .donts-list li::before {{ content: '👎'; color: {highlight_color_negative_icon}; font-weight: bold; display: inline-block; width: 1.5em; margin-left: -1.5em; }}
#     .donts-list li {{ color: {text_color_yellow} !important; }}
#     .foods-eat-list ul, .foods-avoid-list ul {{ list-style-type: none; padding-left: 0; }}
#     .foods-eat-list li::before {{ content: '✅ '; color: {highlight_color_positive_icon}; font-weight: bold; }}
#     .foods-eat-list li {{ color: {text_color_yellow} !important; }}
#     .foods-avoid-list li::before {{ content: '❌ '; color: {highlight_color_negative_icon}; font-weight: bold; }}
#     .foods-avoid-list li {{ color: {text_color_yellow} !important; }}
#     .foods-eat-list-title, .foods-avoid-list-title {{ color: {text_color_yellow} !important; }}
#     .dos-list-title, .donts-list-title {{ color: {text_color_blue} !important; }}
# </style>
# """, unsafe_allow_html=True)


# # --- Load Environment Variables ---
# load_dotenv() # Ensure this is called early
# if not OPENAI_API_KEY: # Check after load_dotenv and import from rag_pipeline
#     st.error("OpenAI API key not found. Please set it in your .env file or environment variables.")
#     st.stop()

# if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
# if not os.path.exists(ASSETS_DIR): os.makedirs(ASSETS_DIR)

# # --- Session State ---
# if "vector_store_loaded" not in st.session_state: st.session_state.vector_store_loaded = False
# if "vector_store" not in st.session_state: st.session_state.vector_store = None
# if "processed_pdf_name" not in st.session_state: st.session_state.processed_pdf_name = None
# if "messages" not in st.session_state:
#     st.session_state["messages"] = [{"role": "assistant", "content": "Welcome! Please upload a medical reference PDF to begin."}]

# # --- Default "Not Found" Messages for Parser and Display Logic ---
# DEFAULT_MSG_PREDICTED_DISEASE = "Not specified by AI or not clearly identified from the context."
# DEFAULT_MSG_REASONING = "Reasoning not provided or an error occurred parsing the response."
# DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK = "Information not available in provided context for specific medications. Please consult a healthcare professional for medication options."
# DEFAULT_MSG_LIFESTYLE = "Specific lifestyle and home care guidance not found in the provided documents for the current query. Please consult a healthcare professional for personalized advice."
# DEFAULT_MSG_DIETARY = "Specific dietary recommendations not found in the provided documents for the current query. Please consult a healthcare professional for personalized advice."
# DEFAULT_MSG_DOS_DONTS = "Specific Do's & Don'ts not found in the provided documents for the current query. Please consult a healthcare professional for personalized advice."
# DEFAULT_MSG_SEEK_HELP = "Always consult a doctor if symptoms are severe, worsen, or if you have any concerns."
# DEFAULT_MSG_DISCLAIMER = """This information is for educational purposes only and not a substitute for professional medical advice, diagnosis, or treatment.
# Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
# Never disregard professional medical advice or delay in seeking it because of something you have read from this chatbot.
# Medication details are illustrative and NOT a prescription; consult your doctor for any medication."""

# # --- Helper Function to Parse LLM Response (ADAPTED FOR NEW PROMPT) ---
# # This function is complex due to regex parsing. Consider if your LLM supports JSON mode for more robust parsing.
# def parse_llm_response(response_text):
#     # Initialize with defaults
#     parsed_data = {
#         "predicted_disease": DEFAULT_MSG_PREDICTED_DISEASE,
#         "reasoning": DEFAULT_MSG_REASONING,
#         "pharmacological": DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK,
#         "medications_list": [],
#         "non_pharmacological_lifestyle": DEFAULT_MSG_LIFESTYLE,
#         "dietary_recommendations": DEFAULT_MSG_DIETARY,
#         "foods_to_eat": "", "foods_to_avoid": "",
#         "general_dos_donts": DEFAULT_MSG_DOS_DONTS,
#         "dos": "", "donts": "",
#         "when_to_seek_help": DEFAULT_MSG_SEEK_HELP,
#         "disclaimer": DEFAULT_MSG_DISCLAIMER
#     }

#     # Extract Main Sections
#     disease_match = re.search(r"\*\*Predicted Disease:\*\*\s*(.*?)(?=\n\s*\*\*Reasoning:\*\*|\n\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
#     if disease_match and disease_match.group(1).strip(): parsed_data["predicted_disease"] = disease_match.group(1).strip()

#     reasoning_match = re.search(r"\*\*Reasoning:\*\*\s*(.*?)(?=\n\s*\*\*Treatment Guidance:\*\*|\n\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
#     if reasoning_match and reasoning_match.group(1).strip(): parsed_data["reasoning"] = reasoning_match.group(1).strip()

#     disclaimer_match = re.search(r"\*\*Disclaimer:\*\*\s*(.*?)(?:\n\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
#     if disclaimer_match and disclaimer_match.group(1).strip(): parsed_data["disclaimer"] = disclaimer_match.group(1).strip()

#     treatment_guidance_block_match = re.search(r"\*\*Treatment Guidance:\*\*\s*(.*?)(?=\n\s*\*\*Disclaimer:\*\*|\n\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
#     if treatment_guidance_block_match:
#         treatment_text = treatment_guidance_block_match.group(1).strip()
        
#         section_headers_raw = [
#             r"Pharmacological \(Medications\):",
#             r"Non-Pharmacological & Lifestyle:",
#             r"Dietary Recommendations:",
#             r"General Do's & Don'ts:",
#             r"When to Seek Professional Help \(Red Flags\):"
#         ]
#         all_next_headers_lookahead_parts = [r"^\s*\*\*" + re.escape(header_part) + r"\*\*" for header_part in section_headers_raw]
#         combined_lookahead = r"(?:" + "|".join(all_next_headers_lookahead_parts) + r"|\n\n\n|\Z)"

#         # Pharmacological (Medications)
#         pharma_block_match = re.search(r"^\s*\*\*Pharmacological \(Medications\):\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
#         if pharma_block_match and pharma_block_match.group(1).strip():
#             pharma_content = pharma_block_match.group(1).strip()
#             parsed_data["pharmacological"] = pharma_content
#             med_items = re.findall(
#                 r"^\s*-\s*\*\*Drug Name:\*\*\s*(.*?)\n"
#                 r"\s*-\s*\*\*Purpose:\*\*\s*(.*?)\n"
#                 r"(?:\s*-\s*\*\*Common Dosage(?: \(Example Only - Emphasize to consult doctor\))?:\*\*\s*(.*?)\n)?"
#                 r"(?:\s*-\s*\*\*Important Notes:\*\*\s*(.*?)(?=\n\s*-|\n\n\n|\Z))?",
#                 pharma_content, re.DOTALL | re.IGNORECASE | re.MULTILINE
#             )
#             if med_items:
#                 parsed_data["medications_list"] = [
#                     {"drug_name": i[0].strip() or "N/A", "purpose": i[1].strip() or "N/A", 
#                      "dosage": i[2].strip() or "Consult doctor.", "notes": i[3].strip() or "N/A"} for i in med_items
#                 ]
#             elif "consult a doctor" not in pharma_content.lower() and "information not available" not in pharma_content.lower():
#                 pass # Keep full pharma_content
#             else:
#                 parsed_data["pharmacological"] = DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK
        
#         # Non-Pharmacological & Lifestyle
#         non_pharma_match = re.search(r"^\s*\*\*Non-Pharmacological & Lifestyle:\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
#         if non_pharma_match and non_pharma_match.group(1).strip(): parsed_data["non_pharmacological_lifestyle"] = non_pharma_match.group(1).strip()

#         # Dietary Recommendations
#         diet_full_match = re.search(r"^\s*\*\*Dietary Recommendations:\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
#         if diet_full_match and diet_full_match.group(1).strip():
#             diet_text = diet_full_match.group(1).strip()
#             parsed_data["dietary_recommendations"] = diet_text
#             eat_match = re.search(r"^\s*-\s*\*\*Foods to Eat:\*\*\s*(.*?)(?=\n\s*-\s*\*\*Foods to Avoid:\*\*|\n\n\n|\Z)", diet_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
#             if eat_match and eat_match.group(1).strip(): parsed_data["foods_to_eat"] = "\n".join([li.strip("-* ").strip() for li in eat_match.group(1).strip().splitlines() if li.strip("-* ").strip()])
#             avoid_match = re.search(r"^\s*-\s*\*\*Foods to Avoid:\*\*\s*(.*?)(?:\n\n\n|\Z)", diet_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
#             if avoid_match and avoid_match.group(1).strip(): parsed_data["foods_to_avoid"] = "\n".join([li.strip("-* ").strip() for li in avoid_match.group(1).strip().splitlines() if li.strip("-* ").strip()])

#         # General Do's & Don'ts
#         dos_donts_full_match = re.search(r"^\s*\*\*General Do's & Don'ts:\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
#         if dos_donts_full_match and dos_donts_full_match.group(1).strip():
#             dos_donts_text = dos_donts_full_match.group(1).strip()
#             parsed_data["general_dos_donts"] = dos_donts_text
#             do_match = re.search(r"^\s*-\s*\*\*Do:\*\*\s*(.*?)(?=\n\s*-\s*\*\*Don't:\*\*|\n\n\n|\Z)", dos_donts_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
#             if do_match and do_match.group(1).strip(): parsed_data["dos"] = "\n".join([li.strip("-* ").strip() for li in do_match.group(1).strip().splitlines() if li.strip("-* ").strip()])
#             dont_match = re.search(r"^\s*-\s*\*\*Don't:\*\*\s*(.*?)(?:\n\n\n|\Z)", dos_donts_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
#             if dont_match and dont_match.group(1).strip(): parsed_data["donts"] = "\n".join([li.strip("-* ").strip() for li in dont_match.group(1).strip().splitlines() if li.strip("-* ").strip()])

#         # When to Seek Professional Help
#         seek_help_match = re.search(r"^\s*\*\*When to Seek Professional Help \(Red Flags\):\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
#         if seek_help_match and seek_help_match.group(1).strip(): parsed_data["when_to_seek_help"] = seek_help_match.group(1).strip()
    
#     return parsed_data


# # --- Functions ---
# def initialize_vector_store():
#     # UPDATED TO FAISS
#     vs = load_existing_faiss_store()
#     if vs:
#         st.session_state.vector_store = vs
#         st.session_state.vector_store_loaded = True
#         st.session_state.processed_pdf_name = "Previously processed medical texts (FAISS)"
#         if len(st.session_state.messages) == 1 and "Welcome!" in st.session_state.messages[0]["content"]:
#             st.session_state.messages[0] = {"role": "assistant", "content": "Welcome! Medical knowledge base (FAISS) active. How can I assist?"}


# # --- UI Layout ---
# st.markdown(f"""
# <div style="text-align: center; padding-top: 2rem; padding-bottom: 1rem;">
#     <h1 class='main-header'><span class='gradient-text'>TATA md AI Medical Advisor</span></h1>
#     <p class='sub-header'>
#         Leveraging medical literature to offer insights on symptoms. <br>
#         <em>This tool provides information for educational purposes only and is not a substitute for professional medical advice.</em>
#     </p>
# </div>
# """, unsafe_allow_html=True)

# # --- Sidebar ---
# with st.sidebar:
#     logo_path = os.path.join(ASSETS_DIR, "tatmd.png") # Make sure this image exists
#     default_logo_url = "https://www.tatamd.com/images/logo_TATA%20MD.svg"

#     if os.path.exists(logo_path):
#         st.image(logo_path, width=180, use_container_width=False) # Set use_container_width=False for fixed width
#     else:
#         st.markdown(f"""
#             <div style="text-align: center; margin-bottom: 1rem;">
#                 <img src="{default_logo_url}" alt="TATA MD Logo" style="width: 180px; margin-bottom: 10px;"
#                      onerror="this.style.display='none'; this.parentElement.innerHTML+='<p style=\'color:{text_color_yellow};\'>TATA MD Logo</p>';">
#             </div>
#         """, unsafe_allow_html=True)

#     st.markdown(f"<h2 style='text-align: center; color: {primary_accent_pink}; margin-bottom: 1rem;'>Knowledge Base</h2>", unsafe_allow_html=True)

#     if not st.session_state.vector_store_loaded and st.session_state.vector_store is None:
#         with st.spinner("Checking for existing knowledge base..."):
#             initialize_vector_store()

#     if st.session_state.vector_store_loaded:
#         st.success(f"Active KB: {st.session_state.processed_pdf_name or 'Loaded'}")
#     else:
#         st.info("Upload a PDF to activate the Knowledge Base.")

#     uploaded_file_sb = st.file_uploader("Upload Medical Reference (PDF)", type="pdf", key="pdf_uploader_sidebar")

#     if st.button("Process PDF & Build KB", key="process_button_sidebar", help="Upload and process a new PDF to create or update the knowledge base."):
#         if uploaded_file_sb is not None:
#             file_path = os.path.join(DATA_DIR, uploaded_file_sb.name)
#             with open(file_path, "wb") as f: f.write(uploaded_file_sb.getbuffer())

#             with st.spinner(f"Processing {uploaded_file_sb.name}... This may take a while."):
#                 st.session_state.vector_store = None
#                 st.session_state.vector_store_loaded = False
#                 st.session_state.processed_pdf_name = None
                
#                 # UPDATED TO FAISS
#                 processed_vs = load_and_process_pdf_to_faiss(file_path)

#                 if processed_vs:
#                     st.session_state.vector_store = processed_vs
#                     st.session_state.vector_store_loaded = True
#                     st.session_state.processed_pdf_name = uploaded_file_sb.name
#                     st.session_state.messages = [{"role": "assistant", "content": f"Knowledge base from '{uploaded_file_sb.name}' (FAISS) is ready. How can I assist?"}]
#                 else:
#                     st.session_state.messages = [{"role": "assistant", "content": f"Failed to process '{uploaded_file_sb.name}'. Please try again or use a different PDF."}]
#                     st.error(f"Failed to process '{uploaded_file_sb.name}'.")
#             st.rerun()
#         else:
#             st.warning("Please upload a PDF file first.")

#     st.markdown("---")
#     st.markdown(f"<p style='font-size: 0.8em; text-align: center; opacity: 0.7; color: {text_color_blue} !important;'>Powered by Advanced AI</p>", unsafe_allow_html=True)


# # --- Main Chat Interface ---
# st.markdown("<div class='section-header'>Symptom Analysis & Guidance</div>", unsafe_allow_html=True)

# chat_container = st.container() # Use st.container to manage chat messages if needed
# with chat_container:
#     for i, msg in enumerate(st.session_state.messages):
#         is_structured_response = isinstance(msg["content"], dict) and "predicted_disease" in msg["content"]

#         with st.chat_message(msg["role"], avatar="🧑‍⚕️" if msg["role"] == "assistant" else "👤"):
#             if msg["role"] == "user":
#                 # User messages can be simpler, or you can style them too
#                 st.markdown(f"<div style='text-align: right; color: {text_color_yellow} !important; padding: 0.5rem;'>{msg['content']}</div>", unsafe_allow_html=True)

#             elif is_structured_response:
#                 st.markdown("<div class='analysis-complete-message'>", unsafe_allow_html=True) # Wrapper for structured response
#                 data = msg["content"]

#                 symptoms_input_string = data.get("symptoms_input", "")
#                 if symptoms_input_string:
#                     symptom_list = [s.strip() for s in re.split(r'[,\n]', symptoms_input_string) if s.strip()]
#                     if not symptom_list and symptoms_input_string: symptom_list = [symptoms_input_string.strip()]
#                     symptoms_html_items = "".join([f"<div class='symptom-item'>{symptom}</div>" for symptom in symptom_list])
#                     st.markdown(f"<div class='symptoms-analyzed-box'><b>Symptoms Analyzed:</b>{symptoms_html_items}</div>", unsafe_allow_html=True)


#                 st.markdown(f"##### <span class='highlight-disease'>{data.get('predicted_disease', DEFAULT_MSG_PREDICTED_DISEASE)}</span>", unsafe_allow_html=True)
                
#                 reasoning_content = data.get('reasoning', DEFAULT_MSG_REASONING).strip()
#                 if reasoning_content and reasoning_content != DEFAULT_MSG_REASONING and "not found" not in reasoning_content.lower():
#                     with st.expander("View Reasoning", expanded=False):
#                         st.markdown(reasoning_content, unsafe_allow_html=True)
#                 else:
#                     st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_REASONING}</p>", unsafe_allow_html=True)
                
#                 st.markdown(f"<hr style='border-color: {card_border_color}; margin-top:1rem; margin-bottom:1rem;'>", unsafe_allow_html=True)
#                 st.markdown(f"<h4 style='color: {text_color_yellow}; text-align:center; margin-bottom:1rem;'>Treatment Guidance</h4>", unsafe_allow_html=True)

#                 # Pharmacological (Medications)
#                 with st.expander("💊 Pharmacological (Medications)", expanded=True):
#                     st.markdown(f"<div class='treatment-guidance-subheader pharma-header'>Medications</div>", unsafe_allow_html=True)
#                     medications_list = data.get('medications_list', [])
#                     pharmacological_text_fallback = data.get('pharmacological', DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK).strip()
#                     if medications_list:
#                         for med in medications_list:
#                             med_html = "<div class='medication-item'>"
#                             med_html += f"<p class='med-drug-name'><strong>{med.get('drug_name', 'N/A')}</strong></p>"
#                             if med.get('purpose') and med.get('purpose') != 'N/A': med_html += f"<p class='med-purpose'>Purpose: <span>{med.get('purpose')}</span></p>"
#                             if med.get('dosage') and med.get('dosage') not in ['N/A', 'Consult doctor.','Consult doctor for dosage.']: med_html += f"<p class='med-dosage'>Dosage Example: <span>{med.get('dosage')}</span> <em>(Not medical advice)</em></p>"
#                             if med.get('notes') and med.get('notes') != 'N/A': med_html += f"<p class='med-notes'>Notes: <span>{med.get('notes')}</span></p>"
#                             med_html += "</div>"
#                             st.markdown(med_html, unsafe_allow_html=True)
#                     elif pharmacological_text_fallback and pharmacological_text_fallback != DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK and "not available" not in pharmacological_text_fallback.lower():
#                         st.markdown(pharmacological_text_fallback, unsafe_allow_html=True)
#                     else:
#                         st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK}</p>", unsafe_allow_html=True)
                
#                 # Non-Pharmacological & Lifestyle
#                 with st.expander("🌿 Non-Pharmacological & Lifestyle"):
#                     st.markdown(f"<div class='treatment-guidance-subheader lifestyle-header'>Lifestyle & Home Care</div>", unsafe_allow_html=True)
#                     content = data.get('non_pharmacological_lifestyle', DEFAULT_MSG_LIFESTYLE).strip()
#                     if content and content != DEFAULT_MSG_LIFESTYLE and "not available" not in content.lower(): st.markdown(content, unsafe_allow_html=True)
#                     else: st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_LIFESTYLE}</p>", unsafe_allow_html=True)

#                 # Dietary Recommendations
#                 with st.expander("🥗 Dietary Recommendations"):
#                     st.markdown(f"<div class='treatment-guidance-subheader dietary-header'>Dietary Advice</div>", unsafe_allow_html=True)
#                     eat_items = data.get("foods_to_eat","").strip().splitlines()
#                     avoid_items = data.get("foods_to_avoid","").strip().splitlines()
#                     eat_md = f"<strong class='foods-eat-list-title'>Foods to Eat:</strong><div class='foods-eat-list'><ul>" + "".join([f"<li>{i.strip()}</li>" for i in eat_items if i.strip()]) + "</ul></div>" if any(i.strip() for i in eat_items) else ""
#                     avoid_md = f"<strong class='foods-avoid-list-title'>Foods to Avoid:</strong><div class='foods-avoid-list'><ul>" + "".join([f"<li>{i.strip()}</li>" for i in avoid_items if i.strip()]) + "</ul></div>" if any(i.strip() for i in avoid_items) else ""
#                     if eat_md or avoid_md:
#                         if eat_md: st.markdown(eat_md, unsafe_allow_html=True)
#                         if avoid_md: st.markdown(avoid_md, unsafe_allow_html=True)
#                     else:
#                         content = data.get('dietary_recommendations', DEFAULT_MSG_DIETARY).strip()
#                         if content and content != DEFAULT_MSG_DIETARY and "not available" not in content.lower(): st.markdown(content, unsafe_allow_html=True)
#                         else: st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_DIETARY}</p>", unsafe_allow_html=True)
                
#                 # General Do's & Don'ts
#                 with st.expander("👍👎 General Do's & Don'ts"):
#                     st.markdown(f"<div class='treatment-guidance-subheader dos-donts-header'>General Advice</div>", unsafe_allow_html=True)
#                     dos_items = data.get("dos","").strip().splitlines()
#                     donts_items = data.get("donts","").strip().splitlines()
#                     dos_md = f"<strong class='dos-list-title'>Do:</strong><div class='dos-list'><ul>" + "".join([f"<li>{i.strip()}</li>" for i in dos_items if i.strip()]) + "</ul></div>" if any(i.strip() for i in dos_items) else ""
#                     donts_md = f"<strong class='donts-list-title'>Don't:</strong><div class='donts-list'><ul>" + "".join([f"<li>{i.strip()}</li>" for i in donts_items if i.strip()]) + "</ul></div>" if any(i.strip() for i in donts_items) else ""
#                     if dos_md or donts_md:
#                         if dos_md: st.markdown(dos_md, unsafe_allow_html=True)
#                         if donts_md: st.markdown(donts_md, unsafe_allow_html=True)
#                     else:
#                         content = data.get('general_dos_donts', DEFAULT_MSG_DOS_DONTS).strip()
#                         if content and content != DEFAULT_MSG_DOS_DONTS and "not available" not in content.lower(): st.markdown(content, unsafe_allow_html=True)
#                         else: st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_DOS_DONTS}</p>", unsafe_allow_html=True)

#                 # Red Flags
#                 with st.expander("🚨 When to Seek Professional Help (Red Flags)", expanded=True):
#                     st.markdown(f"<div class='treatment-guidance-subheader redflags-header'>Urgent Care / Red Flags</div>", unsafe_allow_html=True)
#                     content = data.get('when_to_seek_help', DEFAULT_MSG_SEEK_HELP).strip()
#                     if content and content != DEFAULT_MSG_SEEK_HELP and "always consult" not in content.lower(): st.error(content)
#                     else: st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_SEEK_HELP}</p>", unsafe_allow_html=True)

#                 st.markdown(f"<hr style='border-color: {card_border_color}; margin-top:1.5rem; margin-bottom:1rem;'>", unsafe_allow_html=True)
#                 st.markdown("<div class='disclaimer-box'>" + f"<i><b>Disclaimer:</b> {data.get('disclaimer', DEFAULT_MSG_DISCLAIMER)}</i>" + "</div>", unsafe_allow_html=True)
#                 st.markdown("</div>", unsafe_allow_html=True) # Close .analysis-complete-message

#             else: # Simple string content for assistant (e.g., initial greeting, error messages)
#                 st.markdown(f"<div style='padding: 0.5rem; color: {text_color_yellow} !important;'>{str(msg['content'])}</div>", unsafe_allow_html=True)


# # --- Chat Input ---
# if user_symptoms := st.chat_input("Describe symptoms (e.g., 'fever, persistent cough, body aches')...", key="symptom_input_main"):
#     if not st.session_state.vector_store_loaded or st.session_state.vector_store is None:
#         st.session_state.messages.append({"role": "user", "content": user_symptoms}) # Add user msg even if KB not ready
#         st.session_state.messages.append({"role": "assistant", "content": "⚠️ Please upload and process a medical reference PDF first to enable symptom analysis."})
#     else:
#         st.session_state.messages.append({"role": "user", "content": user_symptoms})

#         with st.status("🧑‍⚕️ AI Advisor is thinking...", expanded=True) as status_ui:
#             st.write("Reviewing symptoms against medical knowledge base...")
#             try:
#                 # UPDATED TO FAISS
#                 raw_response = query_rag_pipeline_faiss(user_symptoms, st.session_state.vector_store)

#                 st.write("Received response from AI, now parsing and formatting...") # More feedback
#                 print(f"\n--- RAW LLM Response (from RAG pipeline) START ---\n{raw_response}\n--- RAW LLM Response (from RAG pipeline) END ---\n")

#                 parsed_response_data = parse_llm_response(raw_response)
#                 print(f"\n--- Parsed Response Data (for UI) START ---\n{json.dumps(parsed_response_data, indent=2)}\n--- Parsed Response Data (for UI) END ---\n")

#                 assistant_response_content = {"symptoms_input": user_symptoms, **parsed_response_data}
#                 st.session_state.messages.append({"role": "assistant", "content": assistant_response_content})
#                 status_ui.update(label="Guidance ready!", state="complete", expanded=False)
#             except Exception as e:
#                 detailed_error_message = f"An error occurred during analysis: {str(e)}. Traceback: {traceback.format_exc()}"
#                 st.session_state.messages.append({"role": "assistant", "content": "Sorry, an unexpected error occurred while processing your request."})
#                 status_ui.update(label="Error processing request.", state="error", expanded=True)
#                 st.error("An internal error occurred. Please try again later or check logs.") # User-facing error
#                 print(f"ERROR in Streamlit chat input processing: {detailed_error_message}") # Detailed log for developer
#     st.rerun()

# # --- Footer ---
# st.markdown(f"""
# <div style="position: fixed; bottom: 0; left: 0; right: 0; background: rgba({int(bg_color[1:3], 16)}, {int(bg_color[3:5], 16)}, {int(bg_color[5:7], 16)}, 0.9); backdrop-filter: blur(5px); padding: 0.5rem; text-align: center; border-top: 1px solid {card_border_color}; z-index: 99;">
#     <p style="margin: 0; font-size: 0.8rem; opacity: 0.7; color: {text_color_blue} !important;">
#         TATA md AI Medical Advisor © {datetime.now().year} - For Informational Purposes Only
#     </p>
# </div>
# """, unsafe_allow_html=True)




# medical_rag_chatbot/main_app.py

import streamlit as st
import os
from dotenv import load_dotenv
import re
from datetime import datetime
import json
import traceback
import shutil # For potentially cleaning up index directory

# --- Define SCRIPT_DIR, ASSETS_DIR, DATA_DIR first for robustness ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# Make sure rag_pipeline and utils are found by adding SCRIPT_DIR to sys.path
import sys
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

try:
    from rag_pipeline import (
        load_and_process_pdf_to_faiss,
        query_rag_pipeline_faiss,
        load_existing_faiss_store,
        OPENAI_API_KEY,
        FAISS_INDEX_DIR_ABS # Import the path to the FAISS index directory
    )
except ImportError as e:
    st.error(
        f"Critical Error: Could not import FAISS-specific functions or constants from 'rag_pipeline.py'. "
        f"Please ensure 'rag_pipeline.py' is correctly set up for FAISS. Specific error: {e}"
    )
    st.stop()

# --- Page Configuration (remains the same) ---
favicon_path = os.path.join(ASSETS_DIR, "favicon.png")
st.set_page_config(
    page_title="TATA md AI Medical Advisor",
    page_icon=favicon_path if os.path.exists(favicon_path) else "🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Theme Colors and CSS (remains the same as your extensive CSS block) ---
# For brevity, I'll assume your large CSS block from the previous message is here.
# Make sure it's included.
bg_color = "#141E30"; text_color_yellow = "#FFFACD"; text_color_blue = "#87CEFA"; primary_accent_pink = "#FF3CAC"
secondary_accent_blue = "#2B86C5"; secondary_accent_purple = "#784BA0"; dark_theme_bg_accent = "#243B55"
highlight_color_medication = "#FFB74D"; highlight_color_med_purpose = "#AED581"; highlight_color_med_dosage = "#FFF176"
highlight_color_med_notes = "#BCAAA4"; highlight_color_positive_icon = "#66BB6A"; highlight_color_negative_icon = "#EF5350"
expander_header_bg_color = f"linear-gradient(135deg, rgba(255, 60, 172, 0.4) 0%, rgba(43, 134, 197, 0.5) 100%)"
expander_content_bg_color = f"rgba(43, 134, 197, 0.15)"; card_bg_color = f"rgba({int(secondary_accent_blue[1:3], 16)}, {int(secondary_accent_blue[3:5], 16)}, {int(secondary_accent_blue[5:7], 16)}, 0.4)"
card_border_color = f"rgba({int(primary_accent_pink[1:3], 16)}, {int(primary_accent_pink[3:5], 16)}, {int(primary_accent_pink[5:7], 16)}, 0.3)"
analysis_done_chat_bg = f"rgba({int(secondary_accent_blue[1:3], 16)}, {int(secondary_accent_blue[3:5], 16)}, {int(secondary_accent_blue[5:7], 16)}, 0.25)"
st.markdown(f"""<style> ... YOUR EXTENSIVE CSS HERE ... </style>""", unsafe_allow_html=True) # Placeholder for your CSS

# --- Load Environment Variables ---
load_dotenv()
if not OPENAI_API_KEY:
    st.error("OpenAI API key not found. Please set it in your .env file or environment variables.")
    st.stop()

if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
if not os.path.exists(ASSETS_DIR): os.makedirs(ASSETS_DIR)

# --- Constants for Default Book ---
DEFAULT_PDF_NAME = "Medical_book.pdf" # Name of your default PDF
DEFAULT_PDF_PATH = os.path.join(DATA_DIR, DEFAULT_PDF_NAME)
DEFAULT_KB_DISPLAY_NAME = "General Medical Reference (Default)"

# --- Session State ---
if "vector_store_loaded" not in st.session_state: st.session_state.vector_store_loaded = False
if "vector_store" not in st.session_state: st.session_state.vector_store = None
if "processed_pdf_name" not in st.session_state: st.session_state.processed_pdf_name = None
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": f"Welcome! Loading the {DEFAULT_KB_DISPLAY_NAME}. How can I assist?"}]
if "kb_source_is_default" not in st.session_state: # Track if current KB is default
    st.session_state.kb_source_is_default = False

# --- Default Messages (remains the same) ---
# ... (Your DEFAULT_MSG_... constants here) ...
DEFAULT_MSG_PREDICTED_DISEASE = "Not specified by AI or not clearly identified from the context."
DEFAULT_MSG_REASONING = "Reasoning not provided or an error occurred parsing the response."
DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK = "Information not available for specific medications. Consult a healthcare professional."
DEFAULT_MSG_LIFESTYLE = "Specific lifestyle guidance not found. Consult a healthcare professional."
DEFAULT_MSG_DIETARY = "Specific dietary recommendations not found. Consult a healthcare professional."
DEFAULT_MSG_DOS_DONTS = "Specific Do's & Don'ts not found. Consult a healthcare professional."
DEFAULT_MSG_SEEK_HELP = "Always consult a doctor if symptoms are severe, worsen, or if you have any concerns."
DEFAULT_MSG_DISCLAIMER = "This information is for educational purposes only..."


# --- Helper Function to Parse LLM Response (remains the same) ---
def parse_llm_response(response_text):
    # ... (Your existing parse_llm_response function here) ...
    parsed_data = {
        "predicted_disease": DEFAULT_MSG_PREDICTED_DISEASE, "reasoning": DEFAULT_MSG_REASONING,
        "pharmacological": DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK, "medications_list": [],
        "non_pharmacological_lifestyle": DEFAULT_MSG_LIFESTYLE, "dietary_recommendations": DEFAULT_MSG_DIETARY,
        "foods_to_eat": "", "foods_to_avoid": "", "general_dos_donts": DEFAULT_MSG_DOS_DONTS,
        "dos": "", "donts": "", "when_to_seek_help": DEFAULT_MSG_SEEK_HELP, "disclaimer": DEFAULT_MSG_DISCLAIMER
    }
    # Simplified regex for brevity, use your full robust parser here
    disease_match = re.search(r"\*\*Predicted Disease:\*\*\s*(.*?)(?=\n\s*\*\*Reasoning:\*\*|\Z)", response_text, re.DOTALL | re.IGNORECASE)
    if disease_match and disease_match.group(1).strip(): parsed_data["predicted_disease"] = disease_match.group(1).strip()
    # ... (Continue with your full parsing logic for all sections) ...
    # Ensure your parser correctly populates "medications_list"
    treatment_guidance_block_match = re.search(r"\*\*Treatment Guidance:\*\*\s*(.*?)(?=\n\s*\*\*Disclaimer:\*\*|\Z)", response_text, re.DOTALL | re.IGNORECASE)
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
    return parsed_data


# --- Core Functions ---
def process_and_load_pdf(pdf_path, display_name, is_default=False):
    """Processes a PDF and loads it into the FAISS vector store."""
    with st.spinner(f"Processing {display_name}... This may take a few minutes."):
        # Clear previous index if processing a new PDF (default or uploaded)
        # This ensures we don't mix indexes.
        if os.path.exists(FAISS_INDEX_DIR_ABS):
            try:
                shutil.rmtree(FAISS_INDEX_DIR_ABS)
                print(f"Cleared existing FAISS index directory: {FAISS_INDEX_DIR_ABS}")
            except Exception as e:
                st.error(f"Could not clear previous index: {e}")
                # Decide if you want to proceed or stop
        
        vs = load_and_process_pdf_to_faiss(pdf_path)
        if vs:
            st.session_state.vector_store = vs
            st.session_state.vector_store_loaded = True
            st.session_state.processed_pdf_name = display_name
            st.session_state.kb_source_is_default = is_default
            st.session_state.messages = [{"role": "assistant", "content": f"Knowledge base from '{display_name}' is ready. How can I assist?"}]
            st.success(f"Knowledge base built from '{display_name}'!")
            return True
        else:
            st.session_state.messages = [{"role": "assistant", "content": f"Failed to process '{display_name}'. Please try again."}]
            st.error(f"Failed to process '{display_name}'.")
            return False

def initialize_default_kb():
    """Tries to load an existing FAISS store or process the default PDF."""
    vs = load_existing_faiss_store()
    if vs:
        st.session_state.vector_store = vs
        st.session_state.vector_store_loaded = True
        # We don't know for sure if the loaded index is from the default PDF.
        # For simplicity, we'll assume if an index exists, it's usable.
        # A more robust system would store metadata about the index source.
        st.session_state.processed_pdf_name = st.session_state.get("processed_pdf_name", DEFAULT_KB_DISPLAY_NAME) # Keep existing name if available
        st.session_state.kb_source_is_default = st.session_state.get("kb_source_is_default", True) # Assume default if not set
        st.sidebar.success(f"Active KB: {st.session_state.processed_pdf_name}")
        if len(st.session_state.messages) == 1 and "Welcome!" in st.session_state.messages[0]["content"]:
             st.session_state.messages[0] = {"role": "assistant", "content": f"Welcome! Knowledge base '{st.session_state.processed_pdf_name}' active."}

    elif os.path.exists(DEFAULT_PDF_PATH):
        st.sidebar.info(f"No existing knowledge base found. Processing '{DEFAULT_KB_DISPLAY_NAME}'...")
        process_and_load_pdf(DEFAULT_PDF_PATH, DEFAULT_KB_DISPLAY_NAME, is_default=True)
    else:
        st.sidebar.warning(f"Default PDF '{DEFAULT_PDF_NAME}' not found in '{DATA_DIR}'. Please upload a PDF.")
        st.session_state.messages[0] = {"role": "assistant", "content": f"Welcome! Default knowledge base not found. Please upload a medical PDF."}

# --- UI Layout ---
# ... (Your main header markdown) ...
st.markdown(f"""<div style="text-align: center; padding-top: 2rem; padding-bottom: 1rem;"><h1 class='main-header'><span class='gradient-text'>TATA md AI Medical Advisor</span></h1><p class='sub-header'>Leveraging medical literature to offer insights on symptoms. <br><em>This tool provides information for educational purposes only and is not a substitute for professional medical advice.</em></p></div>""", unsafe_allow_html=True)


# --- Sidebar ---
with st.sidebar:
    # ... (Your logo display logic) ...
    logo_path = os.path.join(ASSETS_DIR, "tatmd.png"); default_logo_url = "https://www.tatamd.com/images/logo_TATA%20MD.svg"
    if os.path.exists(logo_path): st.image(logo_path, width=180, use_container_width=False)
    else: st.markdown(f"""<div style='text-align: center; margin-bottom: 1rem;'><img src="{default_logo_url}" alt="TATA MD Logo" style="width: 180px; margin-bottom: 10px;" onerror="this.style.display='none'; this.parentElement.innerHTML+='<p style=\'color:{text_color_yellow};\'>TATA MD Logo</p>';"></div>""", unsafe_allow_html=True)

    st.markdown(f"<h2 style='text-align: center; color: {primary_accent_pink}; margin-bottom: 1rem;'>Knowledge Base</h2>", unsafe_allow_html=True)

    # Initialize default KB if no vector store is loaded yet
    if not st.session_state.vector_store_loaded:
        initialize_default_kb()
    elif st.session_state.vector_store_loaded: # If already loaded, just show status
         st.success(f"Active KB: {st.session_state.processed_pdf_name or 'Unknown'}")


    st.markdown("---")
    st.markdown("<p style='font-weight: bold; color: #FFB74D;'>Upload Custom PDF:</p>", unsafe_allow_html=True)
    uploaded_file_sb = st.file_uploader("Select a medical PDF to build a new knowledge base.", type="pdf", key="pdf_uploader_sidebar")

    if st.button("Process Uploaded PDF", key="process_uploaded_button", help="Process the uploaded PDF. This will replace the current knowledge base."):
        if uploaded_file_sb is not None:
            # Save uploaded file temporarily
            temp_pdf_path = os.path.join(DATA_DIR, uploaded_file_sb.name)
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file_sb.getbuffer())
            
            process_and_load_pdf(temp_pdf_path, uploaded_file_sb.name, is_default=False)
            
            # Clean up the temporarily saved uploaded PDF after processing
            if os.path.exists(temp_pdf_path):
                try:
                    os.remove(temp_pdf_path)
                except Exception as e:
                    print(f"Could not remove temporary uploaded file {temp_pdf_path}: {e}")
            st.rerun() # Rerun to reflect new KB
        else:
            st.warning("Please upload a PDF file first.")

    if st.session_state.vector_store_loaded and not st.session_state.kb_source_is_default:
        if st.button("Switch to Default KB", key="switch_to_default_kb"):
            if os.path.exists(DEFAULT_PDF_PATH):
                st.info(f"Switching to '{DEFAULT_KB_DISPLAY_NAME}'...")
                process_and_load_pdf(DEFAULT_PDF_PATH, DEFAULT_KB_DISPLAY_NAME, is_default=True)
                st.rerun()
            else:
                st.error(f"Default PDF '{DEFAULT_PDF_NAME}' not found. Cannot switch.")
    
    st.markdown("---")
    st.markdown(f"<p style='font-size: 0.8em; text-align: center; opacity: 0.7; color: {text_color_blue} !important;'>Powered by Advanced AI</p>", unsafe_allow_html=True)


# --- Main Chat Interface ---
# ... (Your main chat interface markdown header) ...
st.markdown("<div class='section-header'>Symptom Analysis & Guidance</div>", unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    for i, msg in enumerate(st.session_state.messages):
        is_structured_response = isinstance(msg["content"], dict) and "predicted_disease" in msg["content"]
        with st.chat_message(msg["role"], avatar="🧑‍⚕️" if msg["role"] == "assistant" else "👤"):
            # ... (Your existing detailed display logic for user and structured assistant messages) ...
            # This part of your code for displaying messages is quite extensive and seems correct
            # based on previous versions. I'll put a placeholder here for brevity.
            # Ensure it uses data.get('medications_list', []) and iterates for multiple medication boxes.
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
                    elif pharma_fb and pharma_fb != DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK and "not available" not in pharma_fb.lower(): st.markdown(pharma_fb, unsafe_allow_html=True) # Changed from medication-item wrap to direct markdown
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
                    if c and c != DEFAULT_MSG_SEEK_HELP and "always consult" not in c.lower(): st.error(c)
                    else: st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_SEEK_HELP}</p>", unsafe_allow_html=True)
                st.markdown(f"<hr style='border-color: {card_border_color}; margin-top:1.5rem; margin-bottom:1rem;'>", unsafe_allow_html=True)
                st.markdown("<div class='disclaimer-box'>" + f"<i><b>Disclaimer:</b> {data.get('disclaimer', DEFAULT_MSG_DISCLAIMER)}</i>" + "</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else: st.markdown(f"<div style='padding: 0.5rem; color: {text_color_yellow} !important;'>{str(msg['content'])}</div>", unsafe_allow_html=True)


# --- Chat Input ---
if user_symptoms := st.chat_input("Describe symptoms (e.g., 'fever, persistent cough, body aches')...", key="symptom_input_main"):
    if not st.session_state.vector_store_loaded or st.session_state.vector_store is None:
        st.session_state.messages.append({"role": "user", "content": user_symptoms})
        st.session_state.messages.append({"role": "assistant", "content": "⚠️ The Knowledge Base is not active. Please upload a PDF or ensure the default PDF is processed."})
    else:
        st.session_state.messages.append({"role": "user", "content": user_symptoms})
        with st.status("🧑‍⚕️ AI Advisor is thinking...", expanded=True) as status_ui:
            st.write("Reviewing symptoms against medical knowledge base...")
            try:
                raw_response = query_rag_pipeline_faiss(user_symptoms, st.session_state.vector_store)
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
                st.error("An internal error occurred. Please try again later or check logs.")
                print(f"ERROR in Streamlit chat input processing: {detailed_error_message}")
    st.rerun()

# --- Footer (remains the same) ---
# ... (Your footer markdown) ...
st.markdown(f"""<div style="position: fixed; bottom: 0; left: 0; right: 0; background: rgba({int(bg_color[1:3], 16)}, {int(bg_color[3:5], 16)}, {int(bg_color[5:7], 16)}, 0.9); backdrop-filter: blur(5px); padding: 0.5rem; text-align: center; border-top: 1px solid {card_border_color}; z-index: 99;"><p style="margin: 0; font-size: 0.8rem; opacity: 0.7; color: {text_color_blue} !important;">TATA md AI Medical Advisor © {datetime.now().year} - For Informational Purposes Only</p></div>""", unsafe_allow_html=True)