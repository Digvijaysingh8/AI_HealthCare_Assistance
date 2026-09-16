# AI Healthcare Appointment & Patient Assistance Platform

An AI-powered healthcare assistant designed to help patients manage appointments, retrieve healthcare information, and handle routine healthcare-related queries through a conversational interface.

The platform combines **FastAPI, PostgreSQL, Redis, LangChain, LangGraph, LLMs, and Retrieval-Augmented Generation (RAG)** to provide an intelligent and scalable backend.

## 🚀 Features

- Patient management
- Doctor and department information
- Appointment booking and management
- View upcoming appointments
- Reschedule or cancel appointments
- AI-powered conversational assistance
- Healthcare information retrieval using RAG
- Context-aware responses using LLMs
- Conversation workflow orchestration with LangGraph
- PostgreSQL for persistent data storage
- Redis for caching and temporary state
- REST APIs using FastAPI
- Human-assistance routing for requests requiring staff intervention

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │     Web Dashboard    │
                    │   / User Interface   │
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
       │ PostgreSQL  │  │    Redis    │  │ AI Agent     │
       │             │  │             │  │  LangGraph   │
       │ Patients    │  │ Cache/State │  │              │
       │ Doctors     │  │             │  │ LangChain    │
       │ Appointments│  │             │  │ LLM + RAG    │
       └─────────────┘  └─────────────┘  └──────────────┘
