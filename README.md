# Rule-Engine-With-AST
A simple rule-based engine that allows users to create, combine, and evaluate rules on given data. Built using Flask for the backend, and HTML, CSS, and JavaScript for the frontend. Data is stored in an SQLite database.
# Test Cases
Create rules based on logical expressions (e.g., age > 30 AND salary > 20000)

Combine existing rules using logical operators

Evaluate rules against provided data

# Bouns Features:-
Can give name to rule for easy understanding and reterving 

Added view all rules which return all the rules which are created with id and name which makes it eaiser for testing


# Local Setup (Without Docker)
# 1.Clone the Repository:

git clone (https://github.com/shyamraj2p/Rule-Engine-With-AST.git)

cd Rule-Engine-With-AST
# 2.Install Python Dependencies:

pip install -r requirements.txt

# 3.Run the Application: Start the Flask server.

python api.py

# 4.Access the Web Interface: Open a browser and go to

http://127.0.0.1:5000/

# Docker Setup
1)You can also run the application using Docker. Here's how:

2)Build the Docker Image:- docker build -t Rule-Engine-With-AST .

3)Run the Docker Container:- docker run -p 5000:5000 Rule-Engine-With-AST

4)Access the Application:

Open a browser and go to:- http://127.0.0.1:5000/

# Preview of Application
<img width="946" alt="application1 pre" src="https://github.com/user-attachments/assets/a15f0d28-7840-46b7-bfaa-0d46dc51402f">



# Dependencies
To run this project, you will need to install the following dependencies:

Flask: Python web framework

SQLite3: Lightweight database for storing rules

Jinja2: Template rendering for Flask

Docker (optional): For containerizing and deploying the application



