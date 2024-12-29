## Relatives

- Notion 
  - 학습자료: [크래프톤 정글 프리코스 - Chapter 5](https://www.notion.so/kraftonjungle/Chapter-5-1-1654c6f37f8c80359416d6baf45ac415?pvs=25)
  - 코칭가이드: [크래프톤 정글 프리코스 - Chapter 5 코칭 가이드](https://www.notion.so/kraftonjungle/Chapter-5-16b4c6f37f8c8048ab8bf2952cb3006e)
- Google Form: [Day5 오늘의 설문](https://docs.google.com/forms/d/e/1FAIpQLSflM2Vu2846cuC_f4pQTXBQIxywIHR8IANMDgU_mWBR7ILC5Q/viewform?usp=sharing)
- Google Spreadsheet [Day 5 오늘의 설문(응답)](https://docs.google.com/spreadsheets/d/1g-zaVqayul-D3O0Fz_ESuTEMTMSnJ2K4LMLGTwAsAAU/edit?usp=sharing)


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