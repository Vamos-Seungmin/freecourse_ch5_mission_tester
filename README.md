
## Prerequisite
- You need to install python 3.12 on your computer...
- Install poerty on your computer... (check [here](https://python-poetry.org/docs/#installing-with-the-official-installer))

## CMD

```bash
# set dependencies 
poetry install
```

```bash
# set playwright
poetry run playwright install
```


```bash
# DO TEST!
poetry run python app.py
```

---

### COMMAND HISTORY

What I did is...

```bash
poetry env remove python3.10
poetry env use python3.12
```


```bash
poetry add playwright

poetry run playwright install

poetry add google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```