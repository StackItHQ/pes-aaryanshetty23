[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/AHFn7Vbn)
# Superjoin Hiring Assignment

### Welcome to Superjoin's hiring assignment! 🚀

### Objective
Build a solution that enables real-time synchronization of data between a Google Sheet and a specified database (e.g., MySQL, PostgreSQL). The solution should detect changes in the Google Sheet and update the database accordingly, and vice versa.

### Problem Statement
Many businesses use Google Sheets for collaborative data management and databases for more robust and scalable data storage. However, keeping the data synchronised between Google Sheets and databases is often a manual and error-prone process. Your task is to develop a solution that automates this synchronisation, ensuring that changes in one are reflected in the other in real-time.

### Requirements:
1. Real-time Synchronisation
  - Implement a system that detects changes in Google Sheets and updates the database accordingly.
   - Similarly, detect changes in the database and update the Google Sheet.
  2.	CRUD Operations
   - Ensure the system supports Create, Read, Update, and Delete operations for both Google Sheets and the database.
   - Maintain data consistency across both platforms.
   
### Optional Challenges (This is not mandatory):
1. Conflict Handling
- Develop a strategy to handle conflicts that may arise when changes are made simultaneously in both Google Sheets and the database.
- Provide options for conflict resolution (e.g., last write wins, user-defined rules).
    
2. Scalability: 	
- Ensure the solution can handle large datasets and high-frequency updates without performance degradation.
- Optimize for scalability and efficiency.

## Submission ⏰
The timeline for this submission is: **Next 2 days**

Some things you might want to take care of:
- Make use of git and commit your steps!
- Use good coding practices.
- Write beautiful and readable code. Well-written code is nothing less than a work of art.
- Use semantic variable naming.
- Your code should be organized well in files and folders which is easy to figure out.
- If there is something happening in your code that is not very intuitive, add some comments.
- Add to this README at the bottom explaining your approach (brownie points 😋)
- Use ChatGPT4o/o1/Github Co-pilot, anything that accelerates how you work 💪🏽. 

Make sure you finish the assignment a little earlier than this so you have time to make any final changes.

Once you're done, make sure you **record a video** showing your project working. The video should **NOT** be longer than 120 seconds. While you record the video, tell us about your biggest blocker, and how you overcame it! Don't be shy, talk us through, we'd love that.

We have a checklist at the bottom of this README file, which you should update as your progress with your assignment. It will help us evaluate your project.

- [-] My code's working just fine! 🥳
- [-] I have recorded a video showing it working and embedded it in the README ▶️
- [-] I have tested all the normal working cases 😎
- [ ] I have even solved some edge cases (brownie points) 💪
- [-] I added my very planned-out approach to the problem at the end of this README 📜

## Got Questions❓
Feel free to check the discussions tab, you might get some help there. Check out that tab before reaching out to us. Also, did you know, the internet is a great place to explore? 😛

We're available at techhiring@superjoin.ai for all queries. 

All the best ✨.

## Developer's Section
## Approach and Project Details:

For this project, the primary goal was to develop a solution for real-time synchronization between Google Sheets and a MySQL database. Here's a detailed overview of the approach I took:

### 1. Setting Up Google Sheets API:
The first step was setting up Google Sheets API credentials. I created a service account in Google Cloud and shared the Google Sheet with the service account's email. This allowed the Python script to read from and write to the Google Sheet using the Google API.

### 2. MySQL Database Setup:
I created a MySQL database (`SuperjoinDB`) with an `EmployeeData` table to store employee records. The table includes columns for employee name, role, email, and salary, with the `id` column being auto-incremented.

### 3. Data Sync Logic:
The core of the project revolves around two main synchronization functions:
- **sync_sheet_to_db():** This function reads the data from Google Sheets and either inserts new rows or updates existing rows in the MySQL database based on the `employee_name` as the unique identifier. This ensures that no duplicates are created, and updates are handled correctly.
- **sync_db_to_sheet():** This function reads data from MySQL and updates the Google Sheet, starting from the second row to avoid overwriting the header.

### 4. Challenges Faced and Solutions:
- **Handling Duplicates and Updates:** Initially, the system was creating duplicate entries when rows in Google Sheets were updated. I solved this by implementing a check based on the `employee_name` field and comparing existing data with new data. If there was a change, the system updated the row; otherwise, it skipped it.
- **Google Sheets API Permissions:** Ensuring the service account had the correct permissions to access the Google Sheet was crucial. I had to configure the service account credentials and share the sheet with the correct email.

### 5. Continuous Synchronization:
To maintain real-time data synchronization, I implemented a `continuous_sync()` function that runs every 20 seconds, ensuring both Google Sheets and MySQL are kept in sync at all times.
