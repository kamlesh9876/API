# Code Explanation API

> A lightweight FastAPI service that analyzes source code and returns beginner-friendly explanations, syntax trees, and simple suggestions. Ideal for learning tools, code-review helpers, or embedding in developer tooling.

---

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95-green)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)]()

## 🚀 Features
- Explain a code snippet in plain English.
- Return an abstract syntax tree (AST) or simplified structure.
- Support for multiple languages (starting with Python; easy to extend).
- JSON API, OpenAPI docs and interactive Swagger UI.
- Ready for Docker and CI.

---

## 🔧 Tech stack
- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- (Optional) tree-sitter / astor for richer parsing

---

## 📦 Quickstart — Local (dev)

1. Clone repo
```bash
git clone https://github.com/<your-username>/code-explain-api.git
cd code-explain-api
