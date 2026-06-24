# Account Deactivate / Reactivate API

Welcome to the project! This is a Django REST Framework API that allows users to deactivate and reactivate their accounts, with a full, immutable audit trail logging every action.

This guide is written specifically to help you get this project running on your computer from absolutely zero, so you can co-present smoothly.

---

## 🛑 Step 1: Install Required Software (If you haven't already)

Before touching the code, you need two pieces of software installed on your computer.

### 1. Install Python
1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest version of Python for your operating system.
2. **CRITICAL STEP (Windows Users):** When you open the installer, at the very bottom of the first screen, check the box that says **"Add python.exe to PATH"** before you click Install. If you miss this, terminal commands won't work!
3. To verify it installed correctly, open your terminal (Command Prompt, PowerShell, or Mac Terminal) and type:
   ```bash
   python --version
   ```
   *(If it prints a version number like `Python 3.10.x`, you are good to go!)*

### 2. Install Postman
Since we will be presenting the API, you need a way to send requests to it visually.
1. Go to [postman.com/downloads](https://www.postman.com/downloads/) and download the Postman desktop app.
2. Install it and create a free account (or skip account creation if prompted).

---

## 🚀 Step 2: Set Up the Project

Now that you have Python, let's get the code running. 

1. **Open your Terminal** and navigate into the project folder using the `cd` command. 
   *(Example: `cd path/to/the/PRACTICAL/folder`)*
   
2. **Install the project dependencies** (Django and Django REST Framework). Run this command:
   ```bash
   pip install -r requirements.txt
   ```
   *(Wait for it to finish downloading everything).*

3. **Set up the Database**. This creates the local SQLite database file and all the necessary tables:
   ```bash
   python manage.py migrate
   ```

4. **Create an Admin User**. You need a user account to test the login and view the audit logs. Run this command and follow the prompts:
   ```bash
   python manage.py createsuperuser
   ```
   *(It will ask for a username, email, and password. Note: When typing the password, nothing will show on the screen. Just type it and hit enter).*

---

## 🏃 Step 3: Run the Server & Tests

### Start the Server
To make the API live on your machine, run:
```bash
python manage.py runserver
```
Leave this terminal window open! As long as this is running, your API is alive at `http://127.0.0.1:8000`.

### Run the Automated Tests
If you want to demonstrate the automated tests during the presentation, open a **second terminal window** (make sure you are in the project folder) and run:
```bash
python manage.py test accounts -v 2
```
This will run all 9 tests and verify the code is completely bug-free.

---

## 🧪 Step 4: How to Test in Postman (For the Presentation)

Here is your cheat sheet for presenting the API in Postman.

### 1. Get your Auth Token (Login)
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/api-token-auth/`
- **Body** (Select `raw` -> `JSON`):
  ```json
  {
      "username": "your_username_here",
      "password": "your_password_here"
  }
  ```
- Hit **Send**. Copy the `token` string from the response.

### 2. Deactivate the Account
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/account/deactivate/`
- **Headers** tab: 
  - Key: `Authorization`
  - Value: `Token PASTE_YOUR_TOKEN_HERE` *(Note the space after the word Token)*
- **Body** tab (`raw` -> `JSON`):
  ```json
  {
      "reason": "I am leaving the platform for a bit."
  }
  ```
- Hit **Send**. You should see `"is_active": false`.

### 3. Reactivate the Account
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/account/reactivate/`
- **Headers** tab: 
  - Key: `Authorization`
  - Value: `Token PASTE_YOUR_TOKEN_HERE`
- **Body** tab: Leave it completely empty (or `{}`).
- Hit **Send**. You should see `"is_active": true`.

### 4. Verify the Audit Log
Open your web browser and go to:
`http://127.0.0.1:8000/admin/`

Log in with your superuser credentials. Click on **Audit logs**. You will see a perfectly immutable, read-only record of the deactivate and reactivate actions you just performed!
