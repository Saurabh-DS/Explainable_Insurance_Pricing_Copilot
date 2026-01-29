# Explainable Insurance Pricing Copilot - Run All Script
# This script sets up the data, trains the model, builds the vector store, and runs the app.

echo "--- 🛠️ Installing Dependencies ---"
pip install -r requirements.txt

echo "`n--- 📝 Generating Guidelines ---"
python data_generation/generate_guidelines.py

echo "`n--- 📊 Generating Quotes Database ---"
python data_generation/generate_quotes.py

echo "`n--- 🤖 Training Pricing Model ---"
python pricing_model/train_model.py

echo "`n--- 📚 Building Vector Store (RAG) ---"
python rag/build_vector_store.py

echo "`n--- 🚀 Running App ---"
echo "Note: Ensure Ollama is running and Llama3 is pulled (ollama pull llama3)"
python app.py
