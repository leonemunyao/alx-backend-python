## Messaging App

This is an app where users can hold conversations.

#### Testing its Functionality on Postman.


```bash
Messaging App Tests
    Authentication
        POST /login
        Refress Token
        Logout
    Conversations
        Create Conversation
        List Conversation
        Get Conversation
        Filter Conversation
    Messages
        Send Messages
        List Messages
        Update Messages
        Delete Messages
        Filter Messages
    Error Handling
        Unauthorized Tests
        Permission Tests  
```
#### Creating  a Test User.
* **Admin**
```bash
python manage.py createsuperuser
```
* **Basic User**
```bash
python manage.py shell
```
Then inside the Python Shell
```bash
from chats.models import User
user1 = User.objects.create_user(username='testuser3', email='testuser3@test.com', password='testpass123')
user2 = User.objects.create_user(username='testuser4', email='testuser4@test.com', password='testpass123')
```

#### Authentication testing.

* **Login/Get Token(POST)**
URL - `/api/token`
Body(raw JSON)
```bash
{
    "username": "testuser3",
    "password": "testpass123"
}
```

* **Refresh Token(POST)**
URL - `/api/token/refresh`
```bash
{
    "refresh": "{{refresh_token}}"
}
```

* **Logout(POST)**
URL - `/api/logout`
```bash
{
    "token": "{{refresh_token}}"
}
```

* **Create Conversations(POST)**
URL - `/api/conversations/`
```bash
{
    "title": "Test Conversation"
}
```

* **List User Conversations(GET)**
URL - `/api/conversations/`
Headers: `Authorization: Bearer {{access_token}}`
