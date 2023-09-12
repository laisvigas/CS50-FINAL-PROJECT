CLASS DIARY MANAGEMENT SYSTEM (DIÁRIO DE CLASSE)

Description:

CS50 Final Project - Diary and Class Management System

Introduction

Welcome to the CS50 Final Project - a Diary and Class Management System. This web-based application is designed to help teachers and educators efficiently manage student records and grades in an organized and user-friendly manner. The system provides features for user registration, authentication, student data management, and grade recording across multiple units.

Files and Their Functions:

- app.py: This is the main application file containing the Flask web application. It defines the routes and logic for user registration, login, adding students, and managing grades. It also initializes the SQLite database and handles user sessions.
- templates/: This directory contains all the HTML templates used for rendering the web pages. Notable templates include:
- index.html: The login page for users to authenticate.
- cadastro.html: The registration page where users can create new accounts.
- pagina_inicial.html: The main dashboard page displaying user-specific information and a motivational quote.
- cadastrar_aluno.html: The page for adding and managing student records.
- adicionar_notas.html, adicionar_notas_uni2.html, adicionar_notas_uni3.html: Pages for adding and updating student grades in different units.
- media.html: The page displaying the calculated average grades for each student.
- diario_classe.db: The SQLite database file where user account information, student records, and grades are stored. It is created and initialized when the application is run for the first time.
- forms.py: This file defines Flask-WTF forms used for user registration and student grade input. It includes form validation and error handling logic.
- motivational_phrases: A list of motivational quotes used in the application to provide positive messages to users. These quotes are randomly displayed on the dashboard.

Design Choices:

Database Structure: The database design includes tables for user accounts, student records, and multiple units for grade tracking (notas, notas2, notas3). This structure allows for flexibility in managing student data and grades across different units.
Flask: Flask was chosen as the web framework due to its simplicity and flexibility. It provides easy routing, session management, and integration with HTML templates.
Progressive Difficulty: The application gradually increases the complexity of exercises by starting with basic functionality and progressively introducing advanced features. This approach aims to provide a positive learning experience and reduce potential frustration among users.
Motivational Messages: Randomly displaying motivational messages on the dashboard adds a personal touch to the application, helping users stay motivated and engaged.

Conclusion:
The CS50 Final Project - Diary and Class Management System is a valuable tool for educators to manage student records and grades effectively. The project's structure, files, and design choices have been carefully considered to provide a user-friendly and motivating experience.