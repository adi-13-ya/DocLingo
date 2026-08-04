# Changelog

All notable changes to the DocLingo project will be documented in this file.

## [Unreleased] - 2026-08-04

### 🎨 Project Reorganization

#### Added
- **LICENSE** - MIT License for the project
- **CONTRIBUTING.md** - Contribution guidelines for developers
- **CHANGELOG.md** - This changelog file
- **.env.example** - Template for environment configuration
- **docs/** folder - Centralized location for all documentation
  - README.md - Documentation index
  - All phase implementation docs
  - Architecture and structure documentation
- **diagrams/** folder - PlantUML architecture diagrams
  - README.md - Diagram viewing instructions
  - RAG component, pipeline, and sequence diagrams
- **.github/** folder - GitHub templates
  - ISSUE_TEMPLATE.md - Issue reporting template
  - PULL_REQUEST_TEMPLATE.md - PR template
  - README.md - Template documentation

#### Changed
- Reorganized project structure for better maintainability
- Moved all documentation files to `docs/` folder
- Moved all PlantUML diagrams to `diagrams/` folder
- Updated .gitignore to exclude temporary files

#### Removed
- **filestruct.txt** - Temporary file structure documentation
- **patch.py** - Temporary patch file
- **working.md** - Temporary working notes

### 📦 Repository Updates
- Changed remote repository from `doclingo-multilingual-document-model` to `DocLingo`
- Repository URL: https://github.com/adi-13-ya/DocLingo.git
- Both `main` and `fix` branches pushed and synced

### 🛡️ .gitignore Improvements
- Properly excludes `.env` and sensitive files
- Ignores `venv/` and Python cache files
- Excludes temporary and log files
- Protects against accidental commits of secrets

### 📁 New Project Structure

```
DocLingo/
├── .github/              # GitHub templates
├── docs/                 # Documentation
├── diagrams/             # Architecture diagrams
├── answer_engine/        # Answer generation
├── confidence_engine/    # Confidence scoring
├── decision_engine/      # Adaptive decisions
├── document_processor/   # PDF processing
├── feedback_manager/     # Feedback learning
├── language_manager/     # Multilingual support
├── query_engine/         # Query processing (14 engines)
├── retrieval_engine/     # FAISS retrieval
├── safety_engine/        # Safety & governance
├── vector_store/         # Vector operations
├── utils/                # Utilities
├── app.py                # Streamlit UI
├── main.py               # Main pipeline
├── LICENSE               # MIT License
├── CONTRIBUTING.md       # Contribution guide
├── README.md             # Main documentation
└── .env.example          # Config template
```

## Version History

### v1.0 - Initial Release
- Intelligent document Q&A system
- 20+ language support
- FAISS semantic search
- Safety and governance features
- Feedback-driven learning
- 14 specialized query engines

---

**Format**: Based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
**Versioning**: [Semantic Versioning](https://semver.org/)
