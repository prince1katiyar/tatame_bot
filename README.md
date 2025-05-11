🦠 1. Dengue Fever
High fever

Severe headache

Pain behind the eyes

Muscle and joint pain ("breakbone fever")

Skin rash

😷 2. COVID-19
Fever or chills

Cough

Shortness of breath

Loss of taste or smell

Fatigue

🤧 3. Common Cold
Runny or stuffy nose

Sneezing

Sore throat

Mild headache

Cough

🧠 4. Migraine
Intense headache (often one-sided)

Nausea or vomiting

Sensitivity to light and sound

Visual disturbances (aura)

Dizziness

❤️ 5. Heart Attack (Myocardial Infarction)
Chest pain or pressure

Pain radiating to left arm, jaw, or back

Shortness of breath

Cold sweat

Nausea







## Setup and Installation (Local)

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd medical_rag_chatbot
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    *   Create a `.env` file in the project root directory (`medical_rag_chatbot/.env`).
    *   Add your OpenAI API key to this file:
        ```
        OPENAI_API_KEY="your_openai_api_key_here"
        ```
    *   An `.env.example` file can be included in the repository as a template.

5.  **Run the Application:**
    ```bash
    streamlit run main_app.py
    ```
    The application should open in your default web browser.

## Deployment to Streamlit Community Cloud

1.  **Push to GitHub:** Ensure all your code (excluding `.env`, `faiss_index_store/`, and other ignored files) is pushed to a public GitHub repository.
2.  **Sign Up/Log In:** Go to [share.streamlit.io](https://share.streamlit.io/) and connect your GitHub account.
3.  **Deploy New App:**
    *   Click "New app".
    *   Select your repository, branch (e.g., `main`), and the main file path (e.g., `main_app.py`).
    *   **Advanced Settings -> Secrets:** Add your `OPENAI_API_KEY` as a secret:
        ```
        OPENAI_API_KEY="your_actual_openai_api_key_here"
        ```
4.  **Deploy!** Streamlit Cloud will build and deploy your application. You will receive a public URL to share.

**Note on FAISS Index Persistence on Streamlit Cloud:**
The FAISS index (`faiss_index_store/`) is saved to the app's ephemeral filesystem on Streamlit Community Cloud. This means if the app restarts (due to inactivity, updates, etc.), the index may be lost, and users might need to re-upload and process the PDF. For persistent storage, consider integrating cloud storage (e.g., S3) for the FAISS index or using a hosted vector database service.

## Key Technologies Used

*   **Python**
*   **Streamlit:** For the web application interface.
*   **LangChain:** Framework for building LLM applications.
*   **OpenAI GPT Models:** For language understanding and generation.
*   **FAISS:** For efficient similarity search in the vector store.
*   **DuckDuckGo Search:** For real-time web search augmentation.
*   **PyPDF:** For loading and parsing PDF documents.
*   **HTML/CSS:** For custom UI styling.

## Future Enhancements (Ideas)

*   Integrate persistent storage for the FAISS index (e.g., S3).
*   Allow users to manage multiple uploaded PDFs/knowledge bases.
*   Implement user authentication.
*   Add more sophisticated error handling and logging.
*   Incorporate LLM fine-tuning for more specialized medical advice (requires significant data and expertise).
*   Option to use different LLMs or embedding models.
*   Evaluation framework for response quality.

## Contributing

Contributions, issues, and feature requests are welcome. Please open an issue to discuss any major changes.