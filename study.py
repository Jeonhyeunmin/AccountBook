import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib
import test

matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

fileName = "가계부.csv"

# def get_date():
#     date = input("날짜 입력 (yyyy-mm-dd, Enter 시 오늘) : ")
#     if not date :
#       date = datetime.today().strftime("%Y-%m-%d")
#     print(date)
#     return date 

# def get_type():
#     while True:
#         type_ = input("수입 또는 지출 입력 (예 수입 / 지출) : ")
#         if type_ in ["수입", "지출"]:
#             return type_
#         print("수입 또는 지출만 입력 가능합니다. 다시 시도해주세요.")

# def get_category():
#     valid_categories = ["식비", "월급", "교통"]
#     while True:
#         category = input(f"항목 입력 (예 {' | '.join(valid_categories)}) : ")
#         if category in valid_categories:
#             return category
#         print(f"{', '.join(valid_categories)}만 입력 가능합니다. 다시 시도해주세요.")

# def get_amount():
#     while True:
#         amount = input("금액 입력 : ")
#         if amount:
#             return amount
#         print("금액을 입력해주세요.")

# def get_note():
#     return input("메모 (선택) : ")

# 📌 1. 내역 입력
def 입력():
  print("\n[내역입력]")
  date = test.get_date()
  type_ = test.get_type()
  category = test.get_category()
  amount = test.get_amount()
  note = test.get_note()
  row = [date, type_, category, amount, note]
  with open(fileName, "a", newline="", encoding="utf-8") as f:
      writer = csv.writer(f)
      writer.writerow(row)
  print("✅ 저장 완료!")

# 📌 2. 전체 내역 조회
def 출력():
  print("\n[전체 내역 조회]")
  try:
    df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
    print(df)
  except FileNotFoundError:
    print("❗ 가계부 파일이 존재하지 않습니다.")
    
# 📌 3. 통계 보기
def 통계():
    print("\n[수입/지출 통계]")
    try:
        df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
        df["금액"] = pd.to_numeric(df["금액"], errors="coerce")
        df["구분"] = df["구분"].str.strip()

        수입합계 = df[df["구분"] == "수입"]["금액"].sum()
        지출합계 = df[df["구분"] == "지출"]["금액"].sum()

        print(f"💰 총 수입: {수입합계} 원")
        print(f"💸 총 지출: {지출합계} 원")
        print(f"📊 잔액: {수입합계 - 지출합계} 원")

        항목별 = df[df["구분"] == "지출"].groupby("항목")["금액"].sum()
        print("\n📌 항목별 지출:")
        print(항목별)
    except Exception as e:
        print("❗ 통계 분석 중 오류:", e)

# 📌 4. 그래프 보기
def 그래프():
    print("\n[항목별 지출 그래프]")
    try:
        df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
        df["금액"] = pd.to_numeric(df["금액"], errors="coerce")
        df["구분"] = df["구분"].str.strip()

        지출 = df[df["구분"] == "지출"]
        항목별합계 = 지출.groupby("항목")["금액"].sum()

        if not 항목별합계.empty:
            항목별합계.plot(kind="bar", color="skyblue")
            plt.title("항목별 지출")
            plt.xlabel("항목")
            plt.ylabel("지출 금액")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.grid(True, axis='y')
            plt.show()
        else:
            print("📉 시각화할 지출 데이터가 없습니다.")
    except Exception as e:
        print("❗ 그래프 출력 중 오류:", e)
        
def 검색():
    print("\n[항목으로 검색하기]")
    try:
        keyword = input("검색할 항목 이름 입력 (예: 식비, 월급, 교통): ").strip()
        df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
        df["항목"] = df["항목"].astype(str).str.strip()

        result = df[df["항목"] == keyword]

        if result.empty:
            print("❗ 해당 항목의 내역이 없습니다.")
        else:
            print(result)
    except Exception as e:
        print("❗ 검색 중 오류:", e)

# 📌 메인 메뉴
def 메뉴():
    while True:
        print("\n📒 미니 가계부 메뉴")
        print("1. 내역 입력")
        print("2. 전체 조회")
        print("3. 통계 보기")
        print("4. 그래프 보기")
        print("5. 항목으로 검색")
        print("6. 종료")

        choice = input("메뉴 선택 (1~5): ").strip()
        if choice == "1":
            입력()
        elif choice == "2":
            출력()
        elif choice == "3":
            통계()
        elif choice == "4":
            그래프()
        elif choice == "5":
            검색()
        elif choice == "6":
            print("👋 프로그램을 종료합니다.")
            break
        else:
            print("❗ 잘못된 입력입니다. 다시 선택하세요.")

# 실행 시작
if __name__ == "__main__":
    메뉴()