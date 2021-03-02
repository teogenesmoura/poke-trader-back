## Poketrader back

#### Register user

```
POST /auth/register
username: str
password: str
email: str

```

#### Login

```
POST /auth/login/
username: str
password: str  
```

#### Logout

```
Authorization-Headers: Token Bearer
POST /auth/logout/
```

### Create History for a user

```
Authorization-Headers: Token Bearer
POST /history/
name: str
type: str
```

### Get History for a user

```
Authorization-Headers: Token Bearer
GET /user/history/
```

### Create an Entry
```
Authorization-Headers: Token Bearer
POST /history/<history_id>/entry
{
    "history_id": "9",
    "host": {
        "ids": ["1","2","3"]
    },
    "opponent": {
        "ids": ["4","5","6"]
    }
}
```
