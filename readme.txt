It's test task for Hammer Systems company.
The app is a simplified referral system with the ability to authenticate using a special sms code.
The app homepage: https://hammer-kpa.herokuapp.com

API:
1)
    Descriptions: returns phone number and secret code for authenticate
    HTTP method: GET
    path: /user-api/login/{phone number}
    Parameter content type: JSON
    Parameters: phone_number
    Response: phone_number, code

2)
    Descriptions: activates phone in the database and return unique token
    HTTP method: POST
    path: /user-api/login/auth
    Parameter content type: JSON
    Parameters: phone_number, code
    Response: token

3)
    Descriptions: gets personal data by token
    HTTP method: POST
    path: /user-api/profile
    Parameter content type: JSON
    Parameters: token
    Response: phone_number, personal referral code, referral_code, partners
    
4)
    Descriptions: sets foreign referral code
    HTTP method: POST
    path: /user-api/change-ref-code
    Parameter content type: JSON
    Parameters: token, referral code
    Response: message


