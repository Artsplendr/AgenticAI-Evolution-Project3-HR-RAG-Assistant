## HR RAG Assistant

A lightweight Retrieval-Augmented Generation (RAG) assistant focused on HR policies and procedures. It ingests HR markdown documents, builds a small local index, and answers employee questions with citations grounded in the policy content.

### Quick start
- Create and populate your environment file based on `.env.example`.
- Put your HR policy sources in `data/raw/` (sample files are included).
- Ingest data to build/update a local index:
  ```bash
  python scripts/ingest_hr_docs.py
  ```
- Ask a question:
  ```bash
  python scripts/ask_hr.py --question "How many PTO days do I get?"
  ```

### Project layout
| ENTRY POINTS | DATA | CORE LOGIC | INTERFACES |
|-------------|------|------------|------------|
| **app.py**<br>(Streamlit UI)<br><br>**scripts/**<br>• ingest_hr_docs.py<br>• ask_hr.py<br>• eval_hr.py (opt) | **data/raw/**<br>• hr_handbook.md<br>• remote_work_policy.md<br>• leave_policy.md<br>• benefits_overview.md<br>• onboarding_guide.md<br><br>**data/indexes/**<br>• hr_default/<br>&nbsp;&nbsp;• index.faiss<br>&nbsp;&nbsp;• chunks.jsonl<br>&nbsp;&nbsp;• meta.json | **src/hr_rag_assistant/**<br>• config.py<br>• types.py<br><br>**ingestion/**<br>• loaders.py<br>• cleaner.py<br>• chunker.py<br>• index_builder.py<br><br>**retrieval/**<br>• vectorstore.py<br>• retriever.py<br>• prompts.py<br><br>**generation/**<br>• answerer.py<br>• citations.py<br><br>agent.py (opt) | (see ENTRY POINTS) |
| **CONFIG & META** | **DOCUMENTATION** | **TESTS** | |
| .env<br>.env.example<br>pyproject.toml<br>README.md | **docs/**<br>• architecture.md<br>• hr_questions.md<br>• decisions.md | **tests/**<br>• test_chunker.py<br>• test_retriever.py<br>• test_smoke.py | |

### Notes
- `.env` is for local secrets and is git-ignored. Use `.env.example` for a safe template.
- The implementation is intentionally minimal to enable fast iteration. Replace stub logic with real embedding and vector search as needed.

