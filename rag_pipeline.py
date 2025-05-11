# medical_rag_chatbot/rag_pipeline.py

import os
from dotenv import load_dotenv
import traceback
# import pickle # NO LONGER NEEDED FOR FAISS OBJECT ITSELF

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.output_parsers import StrOutputParser

from utils import get_qa_prompt_template

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file or environment variables.")

SCRIPT_DIR_RAG = os.path.dirname(os.path.abspath(__file__))
# FAISS_PICKLE_FILE_ABS = os.path.join(SCRIPT_DIR_RAG, "faiss_medical_book.pkl") # OLD
FAISS_INDEX_DIR_ABS = os.path.join(SCRIPT_DIR_RAG, "faiss_index_store") # NEW: Directory for FAISS save_local

EMBEDDING_MODEL = OpenAIEmbeddings(model="text-embedding-3-small")
LLM_MODEL = ChatOpenAI(temperature=0.1, model_name="gpt-3.5-turbo")

def load_and_process_pdf_to_faiss(pdf_file_path):
    print(f"Loading PDF from: {pdf_file_path}")
    loader = PyPDFLoader(pdf_file_path)
    documents = loader.load()

    if not documents:
        print("No documents loaded from PDF. Check PDF content and path.")
        return None
    print(f"Loaded {len(documents)} pages initially.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"Split into {len(split_docs)} chunks.")

    if not split_docs:
        print("No text chunks created after splitting. Check PDF content.")
        return None

    print(f"Attempting to create FAISS index from {len(split_docs)} documents...")
    try:
        vector_store = FAISS.from_documents(
            documents=split_docs,
            embedding=EMBEDDING_MODEL
        )
        print(f"FAISS index created successfully with {vector_store.index.ntotal} vectors.")

        # Save the FAISS index using its native save_local method
        os.makedirs(FAISS_INDEX_DIR_ABS, exist_ok=True) # Ensure directory exists
        vector_store.save_local(FAISS_INDEX_DIR_ABS) # Saves index.faiss and index.pkl
        print(f"FAISS index saved to directory: {FAISS_INDEX_DIR_ABS}")
        return vector_store
    except Exception as e:
        print(f"Error during FAISS index creation or saving: {e}")
        traceback.print_exc()
        return None


def load_existing_faiss_store():
    # Check if the main index file exists (FAISS saves index.faiss and index.pkl)
    index_file_path = os.path.join(FAISS_INDEX_DIR_ABS, "index.faiss")
    docstore_file_path = os.path.join(FAISS_INDEX_DIR_ABS, "index.pkl") # This is the Langchain docstore

    if os.path.exists(FAISS_INDEX_DIR_ABS) and os.path.exists(index_file_path) and os.path.exists(docstore_file_path):
        try:
            print(f"Loading existing FAISS index from directory: {FAISS_INDEX_DIR_ABS}")
            # FAISS.load_local requires the embedding function
            vector_store = FAISS.load_local(
                FAISS_INDEX_DIR_ABS,
                EMBEDDING_MODEL,
                allow_dangerous_deserialization=True # Required for loading pickled LangChain docstore
            )
            if vector_store and hasattr(vector_store, 'index') and vector_store.index.ntotal > 0:
                 print(f"Successfully loaded FAISS index with {vector_store.index.ntotal} vectors.")
                 return vector_store
            else:
                print("Loaded FAISS directory, but the store is invalid or empty.")
                # If loading seems to fail logically, consider cleaning up the directory
                # import shutil
                # if os.path.exists(FAISS_INDEX_DIR_ABS): shutil.rmtree(FAISS_INDEX_DIR_ABS)
                return None
        except Exception as e:
            print(f"Error loading existing FAISS index from directory: {e}")
            traceback.print_exc()
            # Attempt to remove potentially corrupted directory
            # import shutil
            # if os.path.exists(FAISS_INDEX_DIR_ABS):
            #     try:
            #         shutil.rmtree(FAISS_INDEX_DIR_ABS)
            #         print(f"Removed potentially corrupted FAISS index directory: {FAISS_INDEX_DIR_ABS}")
            #     except OSError as rm_err:
            #         print(f"Error removing FAISS index directory: {rm_err}")
            return None
    else:
        print(f"No existing FAISS index directory or essential files found at {FAISS_INDEX_DIR_ABS}.")
        return None


# --- query_rag_pipeline_faiss remains the same as your last FAISS version ---
def query_rag_pipeline_faiss(symptoms_query: str, vector_store: FAISS):
    if not vector_store:
        return "Error: Knowledge base (FAISS store) is not loaded. Please upload and process a PDF first."

    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    try:
        print(f"Retrieving top {retriever.search_kwargs['k']} documents from FAISS for query: {symptoms_query}")
        book_docs = retriever.invoke(symptoms_query)
        book_context = "\n\n---\n\n".join([f"Source Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(book_docs)])

        print("\n--- Retrieved Book Context (for LLM) START ---")
        print(book_context)
        print(f"--- Total length of book_context: {len(book_context)} chars ---")
        print("--- Retrieved Book Context (for LLM) END ---\n")

        if not book_context.strip():
            book_context = "No relevant information was found in the uploaded book for the user's symptoms."
            print("WARNING: Book context was empty or only whitespace after retrieval.")
    except Exception as e:
        print(f"Error retrieving from FAISS vector store: {e}")
        traceback.print_exc()
        book_context = "An error occurred while retrieving information from the book."

    ddg_search = DuckDuckGoSearchRun()
    try:
        web_search_query = f"treatment options and advice for managing symptoms: {symptoms_query} (include lifestyle, diet, medication classes, do's and don'ts, when to see a doctor)"
        print(f"Performing Web Search with query: {web_search_query}")
        web_search_results = ddg_search.run(web_search_query)
        if not web_search_results:
             web_search_results = "No specific information found on the web for these symptoms via DuckDuckGo."

        print("\n--- Web Search Results (for LLM) START ---")
        print(web_search_results)
        print(f"--- Total length of web_search_results: {len(web_search_results)} chars ---")
        print("--- Web Search Results (for LLM) END ---\n")

    except Exception as e:
        print(f"Error during DuckDuckGo search: {e}")
        traceback.print_exc()
        web_search_results = "An error occurred during web search."

    qa_prompt_template_obj = get_qa_prompt_template()
    chain = qa_prompt_template_obj | LLM_MODEL | StrOutputParser()

    print("Invoking LLM chain (LCEL) with FAISS context...")
    input_data = {
        "book_context": book_context,
        "web_search_results": web_search_results,
        "symptoms": symptoms_query
    }

    response_content = chain.invoke(input_data)
    print("LLM chain invocation complete.")
    return response_content

if __name__ == '__main__':
    print("Testing FAISS RAG Pipeline (save_local/load_local) with new prompt structure...")
    SCRIPT_DIR_RAG_MAIN = os.path.dirname(os.path.abspath(__file__))
    dummy_data_dir = os.path.join(SCRIPT_DIR_RAG_MAIN, "data")
    DUMMY_PDF_PATH = os.path.join(dummy_data_dir, "dummy_test_book_v3_meds_faiss_local.pdf")

    current_y_pos_for_test_pdf = 780
    def add_line_to_test_pdf(pdf_canvas_obj, text, indent=0):
        global current_y_pos_for_test_pdf
        pdf_canvas_obj.drawString(72 + indent, current_y_pos_for_test_pdf, text)
        current_y_pos_for_test_pdf -= 15
        if current_y_pos_for_test_pdf < 50:
            pdf_canvas_obj.showPage()
            pdf_canvas_obj.setFont("Helvetica", 10)
            current_y_pos_for_test_pdf = 780

    if not os.path.exists(dummy_data_dir): os.makedirs(dummy_data_dir)

    if True: # Always recreate dummy PDF for this test
        try:
            from reportlab.pdfgen import canvas
            pdf_canvas = canvas.Canvas(DUMMY_PDF_PATH)
            pdf_canvas.setFont("Helvetica", 10)
            current_y_pos_for_test_pdf = 780

            add_line_to_test_pdf(pdf_canvas, "Chapter: Common Cold & Flu (FAISS Test Local Save)")
            # ... (rest of your dummy PDF content) ...
            add_line_to_test_pdf(pdf_canvas, "Symptoms: Fever, cough, sore throat, runny nose, body aches, fatigue.", 10)
            add_line_to_test_pdf(pdf_canvas, "Pharmacological Information:", 10)
            add_line_to_test_pdf(pdf_canvas, "  - Drug Name: Acetaminophen (e.g., Tylenol)", 20)
            add_line_to_test_pdf(pdf_canvas, "    Purpose: Reduces fever and relieves minor aches and pains.", 30)
            # ... (add more dummy content as in your original test)
            pdf_canvas.save()
            print(f"Created DUMMY FAISS TEST PDF: {DUMMY_PDF_PATH}")
        except ImportError: exit("ReportLab not found. Please install it: pip install reportlab")
        except Exception as e: exit(f"Error creating dummy PDF: {e}")

    # Delete existing FAISS index directory for a fresh test run
    if os.path.exists(FAISS_INDEX_DIR_ABS):
        import shutil
        print(f"Deleting existing FAISS index directory for fresh test: {FAISS_INDEX_DIR_ABS}")
        shutil.rmtree(FAISS_INDEX_DIR_ABS)

    test_vs = load_and_process_pdf_to_faiss(DUMMY_PDF_PATH)
    if test_vs:
        print(f"FAISS Vector store created/loaded for DUMMY TEST PDF. Documents: {test_vs.index.ntotal}")

        symptoms = "fever, cough, body aches"
        print(f"\nQuerying for symptoms: {symptoms}")
        response_text = query_rag_pipeline_faiss(symptoms, test_vs)
        print("\nLLM Response Text:")
        print(response_text)

        print("\n--- Testing loading existing FAISS store after creation ---")
        # To properly test load_local, we should ensure the object in memory (test_vs) is not the one being used.
        # So, we can set test_vs to None or just call load_existing_faiss_store directly.
        del test_vs # Explicitly delete the in-memory object to ensure loading from disk
        loaded_vs = load_existing_faiss_store()
        if loaded_vs:
            symptoms_2 = "sore throat and runny nose"
            print(f"\nQuerying loaded store for symptoms: {symptoms_2}")
            response_text_2 = query_rag_pipeline_faiss(symptoms_2, loaded_vs)
            print("\nLLM Response Text from loaded store:")
            print(response_text_2)
        else:
            print("Failed to load FAISS store after it was created and saved.")
    else:
        print("Failed to create or load FAISS vector store during DUMMY TEST PDF testing.")