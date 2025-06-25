Smart Office Light Automator
This is a Streamlit-based web application designed to automate and optimize office lighting based on daylight data. It evaluates brightness needs using lux values, calculates energy consumption and associated costs, and generates a natural language lighting schedule using the GROQ LLM API.

Features
Upload CSV files containing time and lux data

Automatically determine brightness percentage based on daylight intensity

Calculate energy consumption in kilowatt-hours (kWh)

Estimate total cost based on energy usage

Match the current time to suggest appropriate brightness levels

Generate a natural language lighting schedule using the GROQ API

Simple web interface for visualization and interaction

Requirements
Python 3.8 or higher

Install required packages using:

bash
Copy
Edit
pip install -r requirements.txt
Input CSV Format
Your CSV file should have the following structure:

csv
Copy
Edit
time,lux
06:00,80
06:30,120
07:00,400
...
time: Time in 24-hour format (HH:MM)

lux: Numeric value representing daylight intensity

Getting Started
Clone the Repository

bash
Copy
Edit
git clone https://github.com/your-username/smart-light-dashboard.git
cd smart-light-dashboard
Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Run the Application

bash
Copy
Edit
streamlit run app.py
Use the Application

Upload your CSV file with time and lux columns

Enter your GROQ API key

View brightness suggestions, energy use, and generated schedules

Agents Overview
The application uses a modular agent-based architecture:

Data Reader: Processes and standardizes CSV input

Brightness Evaluator: Determines brightness percentage based on lux

Energy Consumption Agent: Calculates energy usage in kWh

Cost Calculator Agent: Computes cost based on energy consumption

GROQ LLM Scheduler: Generates a readable, time-based brightness schedule

GROQ API Integration
To use the schedule generation feature, you must provide a valid GROQ API key. This key is used to call the GROQ API endpoint with structured brightness data to generate human-readable output.

License
This project is open-source and available under the MIT License.

Author
Developed by Killing Data
(Sarthak Kulkarni, Ansh Ranjan, Akash Gulge)