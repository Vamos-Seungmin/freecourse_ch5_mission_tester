from dataclasses import dataclass
import os
import time
from playwright.sync_api import sync_playwright

# Google Sheets imports
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from google.oauth2 import service_account

# https://docs.google.com/spreadsheets/d/1g-zaVqayul-D3O0Fz_ESuTEMTMSnJ2K4LMLGTwAsAAU/edit?usp=sharing
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1g-zaVqayul-D3O0Fz_ESuTEMTMSnJ2K4LMLGTwAsAAU"

아이피주소_시트범위 = "'sheet1'!B2:B"
점수_시트범위 = "'sheet1'!D2:D"

SERVICE_ACCOUNT_FILE = 'service-account-key.json'  # Google Cloud Console에서 다운로드한 서비스 계정 키 파일


@dataclass
class TestData:
    ip: str
    name: str


@dataclass
class TestResult:
    ip: str
    name: str
    is_success: bool


def get_google_sheets_service() -> Resource:
    """
    Returns an authorized Sheets API service instance using service account credentials.
    Requires a service account key JSON file.
    """
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=SCOPES
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        return service
        
    except Exception as e:
        print(f"Error creating sheets service: {e}")
        raise


def write_results_to_sheets(service: Resource, results: list[TestResult]) -> None:
    """
    Writes test results to Google Sheets.
    Each result is written to column D.
    """
    # True/False 값을 문자열로 변환하여 각각 하나의 셀에 기록
    values = [[result.is_success] for result in results]

    body = {"values": values}

    # 디버깅을 위한 출력
    print(f"Writing values: {values}")
    print(f"To range: {점수_시트범위}")

    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=점수_시트범위,
        valueInputOption="RAW",
        body=body,
    ).execute()


# def fetch_ips_from_sheets():
#     """
#     Fetches a list of IPs from a Google Sheets range.
#     Returns a list of IPs (strings).
#     """
#     service = get_google_sheets_service()  # Sheets API 서비스 초기화
#     try:
#         result = (
#             service.spreadsheets()
#             .values()
#             .get(spreadsheetId=SPREADSHEET_ID, range=아이피주소_시트범위)
#             .execute()
#         )  # 지정된 범위에서 데이터 가져오기
#         rows = result.get("values", [])  # 가져온 데이터에서 값을 추출
#         ips = [row[0] for row in rows if row]  # 각 행의 첫 번째 값을 IP로 간주
#         return ips
#     except Exception as e:
#         print(f"Error fetching IPs from Google Sheets: {e}")
#         return []


def fetch_ips_and_names_from_sheets() -> list[TestData]:
    """
    Fetches lists of IPs and names from Google Sheets ranges.
    Returns a list of TestData objects.
    """
    service = get_google_sheets_service()
    try:
        result = (
            service.spreadsheets()
            .values()
            .batchGet(
                spreadsheetId=SPREADSHEET_ID, ranges=["'sheet1'!B2:B", "'sheet1'!C2:C"]
            )
            .execute()
        )
        value_ranges = result.get("valueRanges", [])

        # 각 range의 values를 추출
        ips = [row[0] for row in value_ranges[0].get("values", []) if row]
        names = [row[0] for row in value_ranges[1].get("values", []) if row]

        # IP와 이름을 TestData 객체로 묶기
        test_data = [TestData(ip=ip, name=name) for ip, name in zip(ips, names)]

        return test_data
    except Exception as e:
        print(f"Error fetching data from Google Sheets: {e}")
        return ([], [])  # 빈 리스트 튜플 반환


def test_webpages(test_data_list: list[TestData]) -> list[TestResult]:
    """
    Uses Playwright to test each IP-based webpage.
    Returns a list of rows for each IP: [ip, success_boolean, page_title_or_error].
    """
    # 함수 정의: IP 주소 목록을 입력으로 받아 각 웹 페이지를 테스트하고 결과를 반환

    results: list[TestResult] = []
    # 테스트 결과를 저장할 빈 리스트 생성. 각 결과는 [IP, 성공 여부, 페이지 제목 또는 오류 메시지] 형태.

    with sync_playwright() as p:
        # Playwright의 실행 컨텍스트를 열기 위해 `sync_playwright`를 사용.

        # Chromium 브라우저를 헤드리스 모드(브라우저 창 없이 백그라운드 실행)로 실행.

        # 브라우저의 새 페이지(탭) 생성.

        for test_data in test_data_list:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            # 입력으로 받은 IP 주소 목록을 순회하며 각각 테스트.

            parsed_ip = test_data.ip.replace("http://", "")
            url = f"http://{parsed_ip}"
            # 현재 IP 주소를 기반으로 URL 생성.

            status = False
            # 기본 상태는 실패(`False`), 추가 정보는 빈 문자열로 초기화.

            try:
                page.goto(url, timeout=5000)  # 10초 타임아웃 설정
                # 해당 URL로 이동. 페이지가 로드되지 않으면 10초 후 타임아웃 발생.

                # time.sleep(1)
                # 페이지가 완전히 로드되도록 잠시 대기. (필요에 따라 생략 가능)

                # 5. 페이지 이동 기다리기
                page.wait_for_load_state("load")

                # 현재 페이지의 제목(title)을 가져옴.
                page_title = page.title()
                print(f"[page_title] {page_title}")

                # 텍스트 찾기
                text_to_search = "나홀로 링크 메모장!"
                if page.locator(f"text={text_to_search}").is_visible():
                    print(f"[page.locator] {page.locator(f'text={text_to_search}')}")
                    print(f"{text_to_search} 텍스트를 찾았습니다.")

                # 포스팅 박스 열기 찾기
                if (page.locator("text=포스팅 박스 열기")).is_visible():
                    page.locator("text=포스팅 박스 열기").click()
                    time.sleep(1)
                else:
                    print("음슴?")

                # 2. 첫 번째 input 태그 찾기 및 값 설정
                first_input = page.locator("input").nth(0)  # 첫 번째 <input> 태그 선택
                first_input.fill("https://jungle.krafton.com/")  # URL 값을 입력

                # 3. 두 번째 input 태그 찾기 및 값 설정
                second_input = page.locator("textarea").nth(
                    0
                )  # 두 번째 <input> 태그 선택
                second_input.fill(
                    f"{test_data.name}님, Day4 과제 제출 완료!"
                )  # 메시지 값을 입력
                
                # 4. "기사저장" 버튼 클릭
                button = page.locator(
                    "text=기사저장"
                )  # '기사저장' 텍스트를 가진 버튼 선택
                try:
                    # Alert 확인 및 텍스트 검증
                    def handle_dialog(dialog):
                        nonlocal status
                        alert_text = dialog.message
                        print(f"Alert 텍스트: {alert_text}")
                        if alert_text == "포스팅 성공!":
                            print("Alert 텍스트가 예상과 일치합니다!")
                            status = True
                        else:
                            print("Alert 텍스트가 예상과 다릅니다.")
                        dialog.accept()

                    page.on("dialog", handle_dialog)  # Alert 이벤트 핸들러 등록
                    button.click()  # 버튼 클릭
                    page.wait_for_timeout(2000)  # 1000ms(1초) 대기
                except TimeoutError:
                    print("기사저장 버튼을 누른 후 Alert가 뜨지 않았습니다.")

            except Exception as e:
                print(f"[ERROR] {e}")
                

            test_result = TestResult(
                ip=test_data.ip,
                name=test_data.name,
                is_success=True if status else False,
            )

            # 현재 IP 주소에 대한 테스트 결과를 리스트에 추가.
            results.append(test_result)
            browser.close()
            # 브라우저를 닫아 리소스 해제.

    return results
    # 모든 IP에 대한 테스트 결과 리스트 반환.


def main():
    service = get_google_sheets_service()
    test_data_list: list[TestData] = fetch_ips_and_names_from_sheets()
    test_results: list[TestResult] = test_webpages(test_data_list)
    write_results_to_sheets(service, test_results)


if __name__ == "__main__":
    main()
