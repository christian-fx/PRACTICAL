# 🎤 Live Presentation Script: Account State API

Use this document as your "cheat sheet" during your online meeting. It assumes your audience knows nothing and walks them through the entire flow visually.

---

## 🛑 Pre-Meeting Setup (Do this 10 mins before the meeting)

1. Open your terminal in VS Code (or your command prompt) and navigate to the project folder.
2. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
3. Open **Postman**.
4. Open your **Web Browser** and have `http://127.0.0.1:8000/admin/` open in a tab.
5. *Now you are ready to hit "Share Screen".*

---

## 🎬 Act 1: Creating a User
*Tell the audience: "First, let's create a brand new user so we have someone to test with."*

1. Open a **new terminal tab** (leave the server running in the first one).
2. Type the following command and hit Enter:
   ```bash
   python manage.py createsuperuser
   ```
3. **Username**: Type `demo_user`
4. **Email**: Leave blank and hit Enter.
5. **Password**: Type `DemoPassword123!` (Note: the password won't show on screen while you type it. Just type and hit enter).
6. **Password (again)**: Type `DemoPassword123!` again.
7. *Say: "Great, we now have a user in the database."*

---

## 🎬 Act 2: Logging in via Postman (Getting the Token)
*Tell the audience: "Now, our user needs to log into the mobile app or website. When they log in, the server gives them a secure token. Let's simulate that login."*

1. Switch to **Postman**.
2. Click the **+** button to create a new Request.
3. Change the method from `GET` to **`POST`**.
4. Set the URL to: `http://127.0.0.1:8000/api-token-auth/`
5. Go to the **Body** tab.
6. Select **raw** and change the dropdown from "Text" to **JSON**.
7. Paste this into the box:
   ```json
   {
       "username": "demo_user",
       "password": "DemoPassword123!"
   }
   ```
8. Click the blue **Send** button.
9. *Show the audience the bottom window.* You will see:
   ```json
   {
       "token": "SOME_LONG_RANDOM_STRING_HERE"
   }
   ```
10. **Highlight and Copy** that token value. 

---

## 🎬 Act 3: Deactivating the Account
*Tell the audience: "Now the user decides they want to leave the platform. They must provide a reason. Let's call the deactivate endpoint."*

1. Open a **new Request tab** in Postman.
2. Change the method to **`POST`**.
3. Set the URL to: `http://127.0.0.1:8000/account/deactivate/`
4. Go to the **Headers** tab.
   - Under Key, type: `Authorization`
   - Under Value, type: `Token ` (with a space) and **paste the token you copied earlier**. 
   *(Example: `Token 9466f4...`)*
5. Go to the **Body** tab.
6. Select **raw** and change the dropdown to **JSON**.
7. Paste this into the box:
   ```json
   {
       "reason": "I am spending too much time on this app."
   }
   ```
8. Click **Send**.
9. *Show the audience the response.* Point out two things:
   - `"is_active": false` (The account is now turned off).
   - `"deactivated_at"` now has a timestamp.

---

## 🎬 Act 4: Proving the Audit Log Works
*Tell the audience: "For security and compliance, every time someone changes their account state, we log it permanently. Let's look at the admin dashboard."*

1. Switch to your **Web Browser**.
2. Go to `http://127.0.0.1:8000/admin/`.
3. Log in with the `demo_user` and `DemoPassword123!`.
4. Click on **Audit logs** under the Accounts section.
5. Click on the very top entry.
6. *Point out to the audience:*
   - You can see **who** did it (`demo_user`).
   - You can see the **Action** (`DEACTIVATE`).
   - You can see the **Reason** ("I am spending too much time on this app.").
   - Notice that there is **no Save or Delete button** at the bottom. Tell them: *"This log is strictly read-only to ensure data integrity. Even administrators cannot alter history."*

---

## 🎬 Act 5: Reactivating the Account
*Tell the audience: "A week later, the user changes their mind and wants to come back. Because they still have their token on their phone, they can reactivate themselves."*

1. Switch back to **Postman**.
2. Open a **new Request tab**.
3. Change the method to **`POST`**.
4. Set the URL to: `http://127.0.0.1:8000/account/reactivate/`
5. Go to the **Headers** tab.
   - Under Key, type: `Authorization`
   - Under Value, type: `Token ` and **paste your token again**.
6. Note: No body is required for reactivation.
7. Click **Send**.
8. *Show the audience the response.* Point out:
   - `"is_active": true` (They are back online).
   - `"deactivation_reason": ""` (The old reason has been cleared out).

---

## 🎬 Act 6: The Final Proof (Automated Tests)
*Tell the audience: "Finally, doing things manually is great, but software changes over time. To make sure this feature never breaks in the future, I wrote an automated test suite."*

1. Switch back to your **Terminal** (where you created the user).
2. Type this command and hit Enter:
   ```bash
   python manage.py test accounts -v 2
   ```
3. Let the audience watch the terminal quickly run through all 9 tests.
4. *Say: "As you can see, all 9 tests passed flawlessly, verifying everything from missing tokens, to length requirements, to data integrity."*

**"And that concludes the demonstration. Are there any questions?"**
