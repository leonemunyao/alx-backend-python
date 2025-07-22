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

---

## Creating the Request Logging Middleware

Implementing the `RequestLoggingMiddleware` class in `middleware.py`.

Then configuring the Middleware in `settings.py` as follows....
```python
MIDDLEWARE = [
    .....
    'chats.middleware.RequestLoggingMiddleware',
    .....
]
```

**Understanding the Implementation**

* `__int__` method takes get_response as a parameter, sets up logging configuration and creates a logger that writes to `requests.log`
* `__call__` methos called every request, extracts user information, logs the timestamp, user and request path and continues processing the request by calling `get_reponse(request)`
* Middleware order: Placed after `AuthenticationMiddleware` in the `settings.py` so we have access to `request.user`

**Testing the Middleware**

