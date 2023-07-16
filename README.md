### Run with
`uvicorn drf_signal_simplejwt.asgi:application --reload --host 0.0.0.0 --port 8000 --workers 9 --use-colors --log-level info`

### SU
```sh
Username: admin
Password: admin
```

### Location of token_blacklist_outstandingtoken, token_blacklist_blacklistedtoken
```
Under rest_framework_simplejwt -> token_blacklist -> models.py -> OutstandingToken, BlacklistedToken
```
**OutstandingToken**: Saves Refresh Token (`token`) mapped for which `user_id`. Also, `created_at` and `expires_at` datetime is stored. A field named `jti` is also there holding a unique UUID for each token. Which helps track and identify individual tokens during token validation and revocation.

**BlacklistedToken**: Has `token_id` which is a foreign key of OutstandingToken and a `blacklisted_at` datetime field. Whenever a refresh token is blacklisted. It is stored in this table.

