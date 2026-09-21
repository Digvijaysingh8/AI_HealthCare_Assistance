# AI Healthcare Appointment & Patient Assistance Platform

An AI-powered healthcare assistant designed to help patients manage appointments, retrieve healthcare information, and handle routine healthcare-related queries through a conversational interface.

The platform combines **FastAPI, SQLite, SQLModel, Redis, LangChain, LangGraph, LLMs, and Retrieval-Augmented Generation (RAG)** to provide an intelligent and scalable healthcare assistance system.

## 🚀 Features

- Patient management
- Doctor and department information
- Appointment booking and management
- View upcoming appointments
- Reschedule or cancel appointments
- AI-powered conversational assistance
- Healthcare information retrieval using RAG
- Context-aware responses using LLMs
- AI workflow orchestration with LangGraph
- SQLite database for persistent data storage
- Redis for caching and temporary state
- REST APIs using FastAPI
- Human-assistance routing for requests requiring staff intervention

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │     Web Dashboard    │
                    │    User Interface    │
                    └──────────┬───────────┘
                               │
                               │ REST API
                               ▼
                    ┌──────────────────────┐
                    │        FastAPI       │
                    │      Backend API     │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
       │   SQLite   │  │    Redis    │  │  AI Agent    │
       │             │  │             │  │  LangGraph   │
       │ Patients    │  │ Cache/State │  │              │
       │ Doctors     │  │             │  │ LangChain    │
       │ Appointments│  │             │  │ LLM + RAG    │
       └─────────────┘  └─────────────┘  └──────────────┘
