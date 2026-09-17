# AI-Powered Multi-Agent Supply Chain Risk, Demand Forecasting and Decision Intelligent System

## 📌 Project Overview

This project presents an AI-powered intelligent supply chain management system that combines multiple specialized AI agents to support demand forecasting, supplier risk assessment, inventory optimization, workforce planning, risk propagation analysis, and intelligent decision-making.

The system integrates Machine Learning, Multi-Agent AI, Optimization, Graph Analytics, Generative AI, and What-If Simulation to provide data-driven decision support for modern supply chain operations.

## 🎯 Objectives

- Predict future product demand using Machine Learning.
- Assess and rank suppliers based on risk and performance.
- Optimize inventory levels, safety stock, and reorder points.
- Predict workforce requirements and potential shortages.
- Analyze how supply chain disruptions propagate across dependencies.
- Generate intelligent recommendations using a Decision Intelligence Engine.
- Provide natural-language explanations using Generative AI.
- Simulate potential supply chain disruption scenarios using What-If Analysis.

## 🧠 AI Agents

### 1. Demand Forecasting Agent
Predicts future product demand using historical sales and relevant supply chain factors.

### 2. Supplier Risk Agent
Evaluates supplier reliability, quality, cost, lead time, and other risk factors to calculate supplier risk and ranking.

### 3. Inventory Agent
Determines safety stock, reorder point, and inventory requirements using statistical and optimization techniques.

### 4. Workforce Intelligence Agent
Analyzes workforce requirements and predicts possible labor shortages or excess capacity.

### 5. Risk Propagation Agent
Uses dependency graphs to analyze how a disruption at one supply chain node can affect connected nodes.

### 6. Decision Intelligence Agent
Combines outputs from different agents and generates data-driven operational recommendations.

## 🤖 Generative AI

A Generative AI assistant is integrated into the system to explain predictions, risks, simulations, and recommendations in natural language.

The Generative AI layer receives structured outputs from the Machine Learning and Decision Intelligence components and converts them into understandable explanations for users.

## 🔬 Technologies

### Machine Learning
- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost

### AI & Optimization
- Multi-Agent AI
- LangGraph
- NetworkX
- SciPy
- Generative AI / LLM

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL

### Frontend
- React.js
- Tailwind CSS
- Recharts
- React Flow

### Development Tools
- Jupyter Notebook
- Visual Studio Code
- Git
- GitHub
- Postman
- Docker

## 📊 Machine Learning Techniques

| Module | Techniques |
|---|---|
| Demand Forecasting | Linear Regression, Random Forest, XGBoost |
| Supplier Risk | Random Forest / XGBoost Classification |
| Supplier Ranking | Multi-Criteria Decision Making |
| Inventory Optimization | Safety Stock, ROP, EOQ, Optimization |
| Workforce Intelligence | Regression and Classification |
| Risk Propagation | Dependency Graph and Risk Scoring |
| Decision Intelligence | Multi-Criteria Decision Making and Optimization |

## 🏗️ System Architecture

```text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │ React Frontend  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ FastAPI Backend │
                  └────────┬────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Multi-Agent Layer   │
                └──────────┬──────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
 Demand Agent       Supplier Agent      Inventory Agent
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
       Workforce       Risk Agent   Decision Engine
         Agent              │             │
             └──────────────┼─────────────┘
                            ▼
                     PostgreSQL Database
                            │
                            ▼
                    Generative AI Layer
                            │
                            ▼
                 Explanation & Recommendation
                 