
# 📊 AI-Powered SQL Assistant API

An interactive, production-ready AI Agent that translates natural language questions into safe, executable SQLite queries. Built with **FastAPI**, the **Anthropic Claude SDK**, and a clean, responsive front-end chat interface styled with **Tailwind CSS**.

---

## 🚀 Live Demo
* **Live Chat UI:** [Insert Netlify/Vercel URL Here]
* **API Documentation (Swagger UI):** [Insert Render URL Here]/docs

---

## ✨ Features

- **Autonomous Agentic Loop:** Implements a raw tool-calling architecture. Claude analyzes the database schema, writes a specific SQL query, triggers execution via local Python code, interprets the returned dataset, and writes a human-friendly answer.
- **Dual-Layer Security Guardrails (Defense-in-Depth):**
  - **Layer 1 (LLM Boundary):** System prompt restricts Claude to read-only queries.
  - **Layer 2 (Hard-Coded Regex Validation):** Python-based SQL parsing that intercepts and blocks queries containing destructive keywords (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, etc.), raising an HTTP 400 Bad Request.
- **Real-Time Token & Performance Monitoring:** Tracks input/output token usage per query loop and measures execution latency in milliseconds, outputting insights directly to the UI.
- **Interactive Chat UI:** Responsive chat interface built with Tailwind CSS, showing the plain-English explanation, the exact generated SQL query, execution speeds, and cost metrics.
- **Session-Based Conversation Memory:** Retains history to handle complex, multi-turn follow-up questions seamlessly.

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Uvicorn, Pydantic (Request/Response validation)
- **AI Core:** Anthropic Claude 3.5 Sonnet (via Tool-Calling API)
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API), Tailwind CSS

---

## 🗄️ Database Schema

The assistant interacts with a relational sales database with the following schema:

| Column | Data Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary Key |
| `region` | TEXT | North, South, East, West |
| `product_category` | TEXT | Electronics, Clothing |
| `quarter` | TEXT | Q1 2025, Q2 2025 |
| `revenue` | REAL | Sales revenue in dollars |
| `units_sold` | INTEGER | Number of items sold |

---

## ⚙️ Local Installation & Setup

### Prerequisites
- Python 3.10+ installed
- An Anthropic API Key ([Get one here](https://platform.claude.com/))

### Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/droy249/sql-assistant.git
   cd sql-assistant
   ```

2. **Set Up a Virtual Environment:**
   On Windows:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```
   On macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   On Windows (PowerShell):
   ```powershell
   setx ANTHROPIC_API_KEY "your-api-key-here"
   # Restart your terminal to apply setx!
   ```
   On macOS/Linux:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

5. **Run the Backend Server:**
   ```bash
   fastapi dev main.py
   ```
   Your backend is now running at `http://127.0.0.1:8000`. You can explore the interactive API docs at `http://127.0.0.1:8000/docs`.

6. **Launch the Frontend:**
   Double-click the `index.html` file to open it in any web browser, and start chatting with your database!

---

## 💡 What I Learned (Transferable Engineering Skills)
- **Custom Tool Integration:** Learned how to declare precise function schemas so LLMs can confidently choose, generate arguments for, and call backend infrastructure.
- **Web Security & CORS:** Successfully engineered and resolved Cross-Origin Resource Sharing (CORS) rules to enable isolated frontends to safely retrieve backend API payloads.
- **Defensive API Engineering:** Avoided third-party frameworks (like LangChain) to write a customized, lightweight agent loop from scratch, ensuring total control over error boundaries, cost-tracking, and input sanitation.
