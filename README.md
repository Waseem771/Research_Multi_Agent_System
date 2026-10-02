# 🔬 Beginner's Guide: Multi-Agent Research System

Welcome! If you are new to Python or Artificial Intelligence, you are in the right place. 
This project uses **Streamlit** (to make the website UI) and **CrewAI** (to control the AI agents).

## 🚀 How to Run This Project on Your Computer

### Step 1: Install Python
Make sure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/). 

### Step 2: Open your Terminal
Open your computer's terminal (or Command Prompt / PowerShell on Windows). Use the `cd` command to navigate to the folder where you saved this project.

### Step 3: Install the Required Libraries
We need to download the tools this project uses. Run this command:
```bash
pip install -r requirements.txt
```

### Step 4: Run the App
Once everything is installed, type this command to start your website:
```bash
streamlit run app.py
```
Your browser will automatically open a new tab showing your app!

---

## 📁 Understanding the Folders
- **`app.py`**: This is the front door. It draws the website you see on your screen.
- **`config.py`**: This securely handles your API passwords (keys).
- **`coordinator.py`**: This is the manager. It assigns tasks to the agents.
- **`agents/`**: This folder contains the personalities for our 5 AI workers.
- **`tools/`**: This folder contains special abilities (like searching Google) that we give to the agents.
