# Code Citations

## License: MIT
https://github.com/maxc0d3r/google-workspace-manager/tree/d2a4e561ae8278455cd5b0c03283a413ebeaff54/gwm/auth/authenticator.py

```
:
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh
```


## License: unknown
https://github.com/ilteriskeskin/ilteriskeskin.github.io/tree/02b0e9d8fbac2051a31a4f69f80598b4b9884492/posts/python-gmail-api/index.html

```
))
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service
```


## License: unknown
https://github.com/josferde5/ST2PAI1/tree/cee75a02a5505f9281a7a51bcdd682d7e45d116a/email_module.py

```
creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def
```

