**Response json format**
----
* **Success:**
    ```javascript
    {
      data: {
              id: 1,
              name: "hello",
              foo: "bar"
            }
    }
    ```
    
* **Error:**
    ```javascript
    {
      error: {
               status_code: 404,
               type: "USER_NOT_FOUND",
               description: "Some info."
             }
    }
    ```
    

**Send code**
----
  Sends sms with secret code and checks whether the maximum number of attempts has been exceeded. Code expires after some time, now five minutes. Returns whether the user with this phone number is registered. This method does not create a user. After sending a new code, previous codes become invalid.

* **URL:**
  /api/auth/code/

* **Method:**
    `POST`
  
* **URL Params:**
    None
    
* **Data Params:**

    phone: [string]
    
    Phone number must be in the international format, i.e. must start with '+' and country code.
    Russia example: +79250741413.
    All other api methods with phone in request or response also only support this format.
 
     
* **Success Response:**

    **Code 201:**
    
    **Content:** 
    ```javascript
    {
      is_new: true
    }
    ```
 
* **Error Response:**

    "INVALID_PHONE_NUMBER" - if phone number has incorrect format. 
    
    
**Confirm code, user exists**
----
  Sign in user by phone and code and checks whether the maximum number of attempts has been exceeded. The user with this phone must be registered in the system. If user does not exist, secret code remains valid until user sign up. In debug mode code '00000' always valid. Methods generates new token for user, after that previous user tokens become invalid, to prevent multi-device support.

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

    "INVALID_PHONE_NUMBER" - if phone number has incorrect format. 
    
    "INVALID_PHONE_CODE" - if code validation error occurred.
    
    "CONFIRM_ATTEMPTS_EXCEEDED" - if the user has exhausted the number of attempts.
    
    "USER_NOT_FOUND" - if user with such phone number does not registered in the system.
    
    
**Confirm code, new user**
----
  Sign up user by phone and code and checks whether the maximum number of attempts has been exceeded. The user must not be registered in the system. This kind of requests requires additional data. The user is automatically added to the users contact which contain the user's phone number. In debug mode code '00000' always valid.

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
    
    **Optional:**
    
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

    "INVALID_PHONE_NUMBER" - if phone number has incorrect format. 
    
    "INVALID_PHONE_CODE" - if code validation error occurred.
    
    "CONFIRM_ATTEMPTS_EXCEEDED" - if the user has exhausted the number of attempts.
    
    "USER_ALREADY_EXISTS" - if user with such phone number already registered .
    
    "INVALID_REQUEST_DATA" - if any request field has incorrect value.
                  
                  
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
      created_at: "2016-10-22T18:22:45.121940Z",
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
    
    name: [string] Cannot be blank.
    
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
      created_at: "2016-10-22T18:22:45.121940Z",
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
    
    
**Delete own account**
----
  Permanently delete account with all settings and relationships.

* **URL**
  /api/account/

* **Method:**
  `DELETE`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**
    None
         
* **Success Response:**

    **Code 204:**
    
    **Content:** `` 
    
* **Error Response:**

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
  /api/users/?users=:id&users=:id

* **Method:**
  `GET`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**

     users: [array]
    
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
      users: ["This list may not be empty", "A valid integer is required."]
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
      detail: "User does not exist."
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
  Adds user to blacklist by id. Returns resulting blacklist.

* **URL**
  /api/blacklist/

* **Method:**
  `PUT`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**

    user: [integer]
     
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
      user: ["User with this id does not exist.", "Can not do it with yourself."]
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
  Removes user from blacklist by id. Returns resulting blacklist.

* **URL**
  /api/blacklist/

* **Method:**
  `DELETE`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**

    user: [integer]
     
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
      user: ["User with this id does not exist.", "Can not do it with yourself."]
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
  Imports a list of user contacts. Contact contains name and phone number. If user with such phone does not exist, contact is still saved for future use. If any name from list longer than 255 chars, method returns error, therefore client should remove this contact from list before sending the request. Returns list of users added to the contacts.

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
    
    The first name and the first phone from the lists form a first contact and so on.
     
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
    
    
**New meeting**
----
  Creates new meeting with users by their ids, also notifies users about that. User who makes the request (creator) becomes king of meeting. If meeting is created with non-existing users or with users who blocked creator, these users are not added to the members. Meeting can contain a single user - creator, therefore "users" param is optional.

* **URL**
  /api/meetings/

* **Method:**
  `POST`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**

    title: [string]
    
    logo: [file]
    
    destination_lat: [float]
    
    destination_lon: [float]
    
    **Optional:**
    
    description: [string]
    
    users: [array]
    
    "users" param can contain creator or not, it doesn't matter. 
    
    end_at: [datetime]
    
    
* **Success Response:**

    **Code 201:**
    
    **Content:** 
    ```javascript
    {
        id: 1, 
        title: "fff", 
        description: null,
        logo: "http://localhost:8000/path1.png"
        end_at: null,
        created_at: "2016-10-22T18:22:45.121940Z",
        completed: false,
        king: 5,
        users: [
            5,
            6
        ],
        destination: {
            lat: 2.233,
            lon: 44.334,
        }
    }
    ```
 
* **Error Response:**

    **Code 400:**
    
    **Content:** 
    ```javascript
    {
      users: ["A valid integer is required."],
      title: ["This field may not be blank.", "This field is required."],
      description: ["This field may not be blank."],
      logo: ["No file was submitted.", "Upload a valid image. The file you uploaded was either not an image or a corrupted image."],
      end_at: [ "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."]
    }
    ```
    
    **Code 401:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
    
    
**Get meetings**
----
  Get info about user meetings. Meetings may be filtered by completed status.

* **URL**
  /api/meetings/

* **Method:**
  `GET`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    
    **Optional:**
    
    completed: [boolean]
    
    If "completed" param is true, response will be contain completed meetings. Else only uncompleted. Default value is false.
    
* **Data Params:**
    None
    
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    [
        {
            id: 228, 
            title: "fff", 
            description: null,
            logo: "http://localhost:8000/path1.png"
            end_at: "2016-10-22T18:23:45.121940Z",
            created_at: "2016-10-22T18:22:45.121940Z",
            completed: true,
            king: 6,
            users: [
                5,
                6
            ],
            destination: {
                lat: 2.233,
                lon: 44.334,
            }
        },
        {
            id: 32, 
            title: "fff", 
            description: "sss",
            logo: "http://localhost:8000/path1.png"
            end_at: null,
            created_at: "2016-10-22T18:22:45.121940Z",
            completed: false,
            king: 7,
            users: [
                7,
                8
            ],
            destination: {
                lat: 2.233,
                lon: 44.334,
            }
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
    
    
**Get meeting**
----
  Get info about single meeting. The user must be in this meeting.

* **URL**
  /api/meetings/:id/

* **Method:**
  `GET`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**
    None
    
* **Success Response:**

    **Code 204:**
    
    **Content:** 
    ```javascript
    {
        id: 228, 
        title: "fff", 
        description: null,
        logo: "http://localhost:8000/path1.png"
        end_at: "2016-10-22T18:23:45.121940Z",
        created_at: "2016-10-22T18:22:45.121940Z",
        completed: false,
        king: 6,
        users: [
            5,
            6
        ],
        destination: {
            lat: 2.233,
            lon: 44.334,
        }
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
      detail: "Meeting does not exist."
    }
    ```
    
    
**Meeting invite user**
----
  Invites one user to the meeting, meeting must be uncompleted. Any user in the meeting can send invitation. If user blocked invitation sender, this user is not added to the meeting. Returns updated meeting info.

* **URL**
  /api/meetings/:id/users/

* **Method:**
  `PUT`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**

    user: [integer]
    
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    {
        id: 1, 
        title: "fff", 
        description: "sss",
        logo: "http://localhost:8000/path1.png"
        end_at: "2016-10-22T18:55:45.121940Z",
        created_at: "2016-10-22T18:22:45.121940Z",
        completed: false,
        king: 5,
        users: [
            5,
            6
        ],
        destination: {
            lat: 2.233,
            lon: 44.334,
        }
    }
    ```
 
* **Error Response:**

    **Code 400:**
    
    **Content:** 
    ```javascript
    {
      user: ["A valid integer is required.", "User with this id does not exist.", "Can not do it with yourself."],
    }
    ```
    
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
      detail: "Meeting does not exist."
    }
    ```
    
    
**Meeting exclude user**
----
  Excludes one user from meeting. Only king of meeting can do this shit. Meeting must be uncompleted. Can't exclude yourself, see "Meeting leave" method. Returns updated meeting info. In future the user can be invited.

* **URL**
  /api/meetings/:id/users/

* **Method:**
  `DELETE`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**

    user: [integer]
    
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    {
        id: 1, 
        title: "fff", 
        description: "sss",
        logo: "http://localhost:8000/path1.png"
        end_at: null,
        created_at: "2016-10-22T18:22:45.121940Z",
        completed: false,
        king: 6,
        users: [
            5,
            6,
            7
        ],
        destination: {
            lat: 2.233,
            lon: 44.334,
        }
    }
    ```
 
* **Error Response:**

    **Code 400:**
    
    **Content:** 
    ```javascript
    {
      user: ["A valid integer is required.", "User with this id does not exist.", "Can not do it with yourself."],
    }
    ```
    
    **Code 401:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
    
    **Code 403:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Only king of meeting have permission to perform this action."
    }
    ```
    
    **Code 404:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Meeting does not exist."
    }
    ```
    
    
**Meeting leave**
----
  Leaves from meeting. Meeting can be completed or uncompleted. If the user was the king of the meeting new king will be chosen randomly. In future the user can be invited.

* **URL**
  /api/meetings/:id/

* **Method:**
  `DELETE`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**
    None
    
* **Success Response:**

    **Code 204:**
    
    **Content:** 
    ```javascript
    {}
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
      detail: "Meeting does not exist."
    }
    ```
    
    
**Meeting update**
----
  Update info about meeting. User must be a king of meeting and meeting must be uncompleted. At the moment "completed" is the only editable field. Returns updated info about meeting.

* **URL**
  /api/meetings/:id/

* **Method:**
  `PATCH`
  
*  **Headers:** 

     Authorization: `"Token aasfsdfsfsdfsfdf234aa"`
   
*  **URL Params:**
    None
    
* **Data Params:**

    completed: [true]
    
    If "completed" param is specified, it must be true.
    
* **Success Response:**

    **Code 200:**
    
    **Content:** 
    ```javascript
    {
        id: 1, 
        title: "fff", 
        description: "sss",
        logo: "http://localhost:8000/path1.png"
        end_at: null,
        created_at: "2016-10-22T18:22:45.121940Z",
        completed: false,
        king: 6,
        users: [
            5,
            6,
            7
        ],
        destination: {
            lat: 2.233,
            lon: 44.334,
        }
    }
    ```
 
* **Error Response:**

    **Code 400:** 
    
    **Content:** 
    ```javascript
    {
      completed: ["completed must be True or not specified."]
    }
    ```
    
    **Code 401:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Invalid token."
    }
    ```
    
    **Code 403:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Only king of meeting have permission to perform this action."
    }
    ```
    
    **Code 404:** 
    
    **Content:** 
    ```javascript
    {
      detail: "Meeting does not exist."
    }
    ```
