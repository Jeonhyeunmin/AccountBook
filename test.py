import csv
from datetime import datetime

def get_date():
    date = input("날짜 입력 (yyyy-mm-dd, Enter 시 오늘) : ")
    if not date :
      date = datetime.today().strftime("%Y-%m-%d")
    print(date)
    return date 

def get_type():
    while True:
        type_ = input("수입 또는 지출 입력 (예 수입 / 지출) : ")
        if type_ in ["수입", "지출"]:
            return type_
        print("수입 또는 지출만 입력 가능합니다. 다시 시도해주세요.")

def get_category():
    valid_categories = ["식비", "월급", "교통"]
    while True:
        category = input(f"항목 입력 (예 {' | '.join(valid_categories)}) : ")
        if category in valid_categories:
            return category
        print(f"{', '.join(valid_categories)}만 입력 가능합니다. 다시 시도해주세요.")

def get_amount():
    while True:
        amount = input("금액 입력 : ")
        if amount:
            return amount
        print("금액을 입력해주세요.")

def get_note():
    return input("메모 (선택) : ")