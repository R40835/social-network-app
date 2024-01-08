# Real-Time Social Networking Web App
# Overview
A fully-featured real-time web application built using Django, PostgreSQL, Redis, and Agora SDK. The app provides a comprehensive social networking experience with features accessible on both phones and desktops.

# Key Features
1. User Management:
- User profiles with customisable details and profile photos.
- User account recovery using email.
- User search.
- Friend requests, friend management, and online status real-time tracking.
- Ability to add, remove, and see friends' profiles.

2. Content Management:
- Post uploads with or without photos.
- Real-time feed showcasing all user posts.
- Post editing and deletion.
- Post likes and comments.
- Comment editing.
- Ability to see post likers.

3. Direct Messages and Group Chats:
- One-to-one direct messages.
- Group chat functionality with room creation.
- Instant messaging with real-time updates.

4. Video Calls:
- One-to-one video calls using Agora SDK.
- Mute and stop video features during calls.
- Calls history.

5. Notifications:
- Direct messages and room messages real-time notifications.
- Post likes and comments real-time notifications.
- Friend requests real-time notifications.
- Friend requests acceptance real-time notifications.
- Calls real-time notifications.
- Missed calls real-time notifications.

# App Setup
1. Install the dependencies listed in the requirements.txt file using the following command:
```
pip install -r requirements.txt
```
2. Create a postgres database and user for the app.
3. Setup a redis server and run it, windows users can download the zip file containing the server from the following link:
https://github.com/zkteco-home/redis-windows/releases/tag/7.0.11
4. Create an agora account for free then get your app ID and Certificate. Please use the following link to sign up:
https://www.agora.io/en/blog/how-to-get-started-with-agora/
5. Using python generate a secret key as follows:
```
>>> import secrets
>>> secrets.token_hex(60)
```
6. Create a .env file in the project root for the environment variables, and assign the appropriate values to the corresponding variables:
```
DEBUG=...
SECRET_KEY=...
DATABASE_USER=...
DATABASE_PASSWORD=...
DATABASE_NAME=...
EMAIL_HOST=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
EMAIL_PORT=...
EMAIL_USE_TLS=...
EMAIL_USE_SSL=...
AGORA_APP_ID=...
AGORA_APP_CERTIFICATE=...
```
- Note: Do not use quotes!
7. Make migrations using the following command: 
```
python manage.py makemigrations
```
8. Migrate using the following command: 
```
python manage.py migrate
```
9. Run the server using the following command: 
```
python manage.py runserver
```

# Technology Stack
- Django for backend development.
- PostgreSQL for data storage.
- Redis for caching and real-time features.
- Agora SDK for video call functionality.

# Contributing
Contributions to the Social Network App are welcome! If you have any ideas, bug fixes, or improvements, please submit a pull request. Make sure to follow the established coding style and guidelines.

# License
This project is licensed under the MIT License. See the LICENSE file for more information.

# Contact
For any questions or inquiries, please reach out to meraghnir93@gmail.com
