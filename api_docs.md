**Send code**
----
  Sends sms with secure code and checks whether the limit has been exceeded. Returns whether the user with this phone number is registered.

* **URL:**
  /api/auth/code/

* **Method:**
    `POST`
  
* **URL Params:**
    None
    
* **Data Params:**

    phone: [string]
     
* **Success Response:**

    **Code 201:**
    
    **Content:** 
  ```javascript
  { 
    is_new: true
  }
  ```
 
* **Error Response:**

    **Code 400:**
    
    **Content:** 
    ```javascript
    {
      phone: ["Invalid phone number."]
    }
    ```
    
    **Code 429:**
    
    **Content:** 
    ```javascript
    {
      detail: "Request was throttled."
    }
    ```
    
    
**Confirm code, user exists**
----
  Sign in user by phone and code. The user with this phone must be registered in the system.

* **URL:**
  /api/auth/users/

* **Method:**
  `POST`
  
*  **URL Params:**
    None
    
* **Data Params:**

    phone: [string]
    
    code: [alphanumeric]
     
* **Success Response:**

    **Code 201:**
    
    **Content:** 
    ```javascript
    {
      user_id: 1, 
      token: "sadfsdfw22342342dfgaa" 
    }
    ```
 
* **Error Response:**

    **Code 400:**
    
    **Content:** 
    ```javascript
    {
      code: ["Code is invalid."],
      phone: ["Invalid phone number."]
    }
    ```
                  
    **Code 404:**
    
    **Content:** 
    ```javascript
    {
      detail: "Not found."
    }
    ```
    
    **Code 429:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Request was throttled."
    }
    ```
    

**Confirm code, new user**
----
  Sign up user by phone and code. The user must not be registered in the system. This kind of requests requires additional data. The user is automatically added to the users contact which contain the user's phone number.

* **URL:**
  /api/auth/users/

* **Method:**
  `POST`
  
*  **URL Params:**
    None
    
* **Data Params:**

    phone: [string]
    
    code: [alphanumeric]
    
    is_new: true
    
    name: [string]
    
    avatar: [file]
     
* **Success Response:**

    **Code 201:**
    
    **Content:** 
    ```javascript
    { 
      user_id: 1, 
      token: "sadfsdfw22342342dfgaa"
    }
    ```
 
* **Error Response:**

    **Code 400:** 
    
    **Content:** 
    ```javascript
    {
      code: ["Code is invalid."],
      phone: ["Invalid phone number.", "user with this phone already exists."],
      name: ["This field is required."],
      avatar: ["This field is required."]
    }
    ```
                  
    **Code 429:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Request was throttled."
    }
    ```
                  
                  
**Get own account**
----
  Get full info about own account.

* **URL**
  /api/account/

* **Method:**
  `GET`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**
    None
     
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    {
      id: 1, 
      name: "fff", 
      phone: "+79250741413",
      created: "2222333",
      hidden_phone: false, 
      avatar: "http://localhost:8000/path.png"
    }
    ```
 
* **Error Response:**

    **Code 401:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
    
    
**Update own account**
----
  Partly update own settings.

* **URL**
  /api/account/

* **Method:**
  `PATCH`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**

    **Optional:**
    
    name: [string]
    
    hidden_phone: [bool]
    
    avatar: [file]
     
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    {
      id: 1, 
      name: "fff", 
      phone: "+79250741413",
      created: "2222333",
      hidden_phone: false, 
      avatar: "http://localhost:8000/path.png"
    }
    ```
 
* **Error Response:**

    **Code 400:** 
    
    **Content:** 
    ```javascript
    {
      avatar: ["Upload a valid image. The file you uploaded was either not an image or a corrupted image."], 
      name: ["This field may not be blank"]
    }
    ```
    
    **Code 401:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
    
    
**Get users**
----
  Get users info by their ids. Representation of each user depends on the relationship between this user and the viewer and user settings.

* **URL**
  /api/users/?user_ids=:id&user_ids=:id

* **Method:**
  `GET`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**

   user_ids: [array]
    
* **Data Params:**
  None
     
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    [
        {
            id: 1, 
            name: "fff", 
            phone: "+79250741413",
            avatar: "http://localhost:8000/path1.png"
        },
        {
            id: 2, 
            name: "aaa", 
            avatar: "http://localhost:8000/path2.png"
        }
    ]
    ```
 
* **Error Response:**

    **Code 400:** 
    
    **Content:** 
    ```javascript
    {
      user_ids: ["This list may not be empty", "A valid integer is required."]
    }
    ```
    
    **Code 401:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
    
    
**Get user**
----
  Does the same things as "Get users" method, but only for single user.

* **URL**
  /api/users/:id

* **Method:**
  `GET`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**
  None
     
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    {
      id: 1, 
      name: "fff", 
      phone: "+79250741413",
      avatar: "http://localhost:8000/path1.png"
    }
    ```
 
* **Error Response:**

    **Code 401:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
    
    **Code 404:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Not found."
    }
    ```
    
    
**Get blacklist**
----
  Returns a list of users that have been blocked by this user.

* **URL**
  /api/blacklist/

* **Method:**
  `GET`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**
  None
     
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    [
        {
            id: 1, 
            name: "fff", 
            phone: "+79250741413",
            avatar: "http://localhost:8000/path1.png"
        },
        {
            id: 2, 
            name: "aaa", 
            avatar: "http://localhost:8000/path2.png"
        }
    ]
    ```
 
* **Error Response:**

    **Code 401:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
    
    
**Add to blacklist**
----
  Adds user to blacklist by id. The user must exist. Returns resulting blacklist.

* **URL**
  /api/blacklist/

* **Method:**
  `PUT`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**

    user_id: [integer]
     
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    [
        {
            id: 1, 
            name: "fff", 
            phone: "+79250741413",
            avatar: "http://localhost:8000/path1.png"
        },
        {
            id: 2, 
            name: "aaa", 
            avatar: "http://localhost:8000/path2.png"
        }
    ]
    ```
   
 
* **Error Response:**

    **Code 400:**
    
    **Content:** 
    ```javascript
    {
      user_id: ["User with this id does not exist.", "Can not do it with yourself."]
    }
    ```
    
    **Code 401:** 
    
    **Content:**
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
    
    
**Remove from blacklist**
----
  Removes user from blacklist by id. The user must exist. Returns resulting blacklist.

* **URL**
  /api/blacklist/

* **Method:**
  `DELETE`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**

    user_id: [integer]
     
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    [
        {
            id: 1, 
            name: "fff", 
            phone: "+79250741413",
            avatar: "http://localhost:8000/path1.png"
        },
        {
            id: 2, 
            name: "aaa", 
            avatar: "http://localhost:8000/path2.png"
        }
    ]
    ```
 
* **Error Response:**

    **Code 400:**
    
    **Content:** 
    ```javascript
    {
      user_id: ["User with this id does not exist.", "Can not do it with yourself."]
    }
    ```
    
    **Code 401:** 
    
    **Content:**
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
    
    
**Get contacts**
----
  Returns a list of users from user contacts.

* **URL**
  /api/contacts/

* **Method:**
  `GET`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**
    None
     
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    [
        {
            id: 1, 
            name: "fff", 
            phone: "+79250741413",
            avatar: "http://localhost:8000/path1.png"
        },
        {
            id: 2, 
            name: "aaa", 
            phone: "+79250741412",
            avatar: "http://localhost:8000/path2.png"
        }
    ]
    ```
 
* **Error Response:**

    **Code 401:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
    
    
**Add to contacts**
----
  Imports a list of user contacts. Contact contains name and phone number. If user with such phone does not exist, contact is still saved for future use. Returns list of users added to the contacts.

* **URL**
  /api/contacts/

* **Method:**
  `PUT`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**

    names: [array]
    
    phones: [array]
    
    the first name and the first phone from the lists form a first contact and so on.
     
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    [
        {
            id: 1, 
            name: "fff", 
            phone: "+79250741413",
            avatar: "http://localhost:8000/path1.png"
        },
        {
            id: 2, 
            name: "aaa", 
            phone: "+79250741412",
            avatar: "http://localhost:8000/path2.png"
        }
    ]
    ```
 
* **Error Response:**

    **Code 400:**
    
    **Content:** 
    ```javascript
    {
      phones: ["Phone list contains duplicates.", "The phones list contains user phone."],
      non_field_errors: ["The number of phones must be equal to the number of names."]
    }
    ```
                   
    **Code 401:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
    
    
**Remove from contacts**
----
  Delete user contacts by phone numbers. Returns resulting contact list.

* **URL**
  /api/contacts/

* **Method:**
  `DELETE`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**

    phones: [array]
     
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    [
        {
            id: 1, 
            name: "fff", 
            phone: "+79250741413",
            avatar: "http://localhost:8000/path1.png"
        },
        {
            id: 2, 
            name: "aaa", 
            phone: "+79250741412",
            avatar: "http://localhost:8000/path2.png"
        }
    ]
    ```
 
* **Error Response:**

    **Code 400:**
    
    **Content:** 
    ```javascript
    {
      phones: ["Invalid phone number.", "This list may not be empty."]
    }
    ```
    
    **Code 401:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
