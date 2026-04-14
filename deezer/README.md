# Deezer

To get auth token:

1. Register an app: https://developers.deezer.com/myapps
2. Set redirect URL to http://localhost:8080/oauth/return
3. `uvx --from deezer-oauth-cli deezer-oauth APP_ID APP_SECRET`
4. Put it into `DEEZER_ACCESS_TOKEN` environment variable
