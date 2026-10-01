# 🏥 ODASHA — AI-Powered Healthcare Assistant

> A full-stack healthcare management application that combines **FastAPI, React, SQLite, JWT Authentication, Role-Based Access Control (RBAC), Appointment Scheduling, Retrieval-Augmented Generation (RAG), and Generative AI** into a single platform.

---

## 📌 Overview

**ODASHA (AI Healthcare Assistant)** is a full-stack healthcare application designed to bring common healthcare-management workflows and AI-powered healthcare information into one platform.

The application provides separate experiences for:

- 👤 Patients
- 👨‍⚕️ Doctors
- 🛡️ Administrators

Patients can explore doctors, book appointments, view their appointments, and interact with an AI healthcare assistant.

Doctors can view their associated patients and appointments.

Administrators have access to management-level functionality for patients, doctors, departments, and appointments.

The AI assistant uses a **RAG pipeline** to retrieve relevant information from a healthcare knowledge base before generating a response. This helps the system provide answers based on the application's available healthcare information rather than relying only on the language model.

Retrieval is **lexical**: chunks are scored with BM25 against the question's tokens, with extra weight on the condition name at the top of each chunk. The knowledge base (`data/healthcare_knowledge.txt`) is read and indexed at startup, so editing that file is all that is needed to change what the assistant knows — there is no embedding model and no index rebuild step. A question with no real overlap with the knowledge base returns nothing, which lets the assistant say it lacks the information instead of inventing it.

> ⚠️ **Important:** This project is an educational/portfolio application. The AI assistant is intended for informational purposes and should not be considered a substitute for a qualified medical professional, diagnosis, or emergency medical care.

---

# 🚀 Features

## 🔐 Authentication & Security

- User registration
- User login
- JWT-based authentication
- Password hashing
- Protected frontend routes
- Backend authentication dependency
- Role-Based Access Control (RBAC)
- Patient / Doctor / Admin role separation
- Ownership-based access control
- Protected appointment creation
- Prevention of unauthorized patient access
- Prevention of unauthorized role-based operations

### Authentication Flow

```text
User
 │
 ├── Register
 │
 ▼
Password Hashing
 │
 ▼
SQLite User Record
 │
 ├── Login
 │
 ▼
JWT Access Token
 │
 ▼
Frontend localStorage
 │
 ▼
Protected API Requests
 │
 ▼
FastAPI Authentication
 │
 ▼
Role / Ownership Validation
