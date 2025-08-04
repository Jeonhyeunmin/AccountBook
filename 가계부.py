import tkinter as tk
from tkinter import messagebox, Toplevel, Text, Scrollbar, ttk
import csv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# 한글 폰트 설정
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

fileName = "가계부.csv"

# ✅ 저장 함수
def 저장하기():
    date = 날짜_entry.get()
    if not date:
        date = datetime.today().strftime("%Y-%m-%d")

    type_ = 구분_var.get()
    category = 항목_entry.get()
    amount = 금액_entry.get()
    note = 메모_entry.get()

    if type_ not in ["수입", "지출"]:
        messagebox.showwarning("입력 오류", "구분은 수입 또는 지출이어야 합니다.")
        return
    if not amount.isdigit():
        messagebox.showwarning("입력 오류", "금액은 숫자만 입력해야 합니다.")
        return

    row = [date, type_, category, amount, note]
    with open(fileName, "a", newline="", encoding="cp949") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    messagebox.showinfo("저장 완료", "내역이 저장되었습니다.")
    날짜_entry.delete(0, tk.END)
    항목_entry.delete(0, tk.END)
    금액_entry.delete(0, tk.END)
    메모_entry.delete(0, tk.END)

# ✅ 전체 조회
def 전체_조회():
    try:
        df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
    except FileNotFoundError:
        messagebox.showwarning("파일 없음", "가계부.csv 파일이 없습니다.")
        return

    win = Toplevel(root)
    win.title("전체 내역 조회")
    win.geometry("600x400")

    text = Text(win)
    text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = Scrollbar(win, command=text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text.config(yscrollcommand=scrollbar.set)

    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)
    df["금액"] = df["금액"].apply(lambda x: f"{x:,}")
    text.insert(tk.END, df.to_string(index=False))

# ✅ 통계 보기
def 통계_보기():
    try:
        df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
        df["금액"] = pd.to_numeric(df["금액"], errors="coerce")
        df["구분"] = df["구분"].astype(str).str.strip()

        수입 = df[df["구분"] == "수입"]["금액"].sum()
        지출 = df[df["구분"] == "지출"]["금액"].sum()
        잔액 = 수입 - 지출

        messagebox.showinfo("📊 수입/지출 통계",
            f"💰 총 수입: {수입:,.0f} 원\n💸 총 지출: {지출:,.0f} 원\n📌 잔액: {잔액:,.0f} 원")
    except Exception as e:
        messagebox.showerror("오류", f"통계 처리 중 오류 발생: {e}")

# ✅ 그래프 보기
def 지출_그래프():
    try:
        df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
        df["금액"] = pd.to_numeric(df["금액"], errors="coerce")
        df["구분"] = df["구분"].astype(str).str.strip()

        지출 = df[df["구분"] == "지출"]
        항목별합계 = 지출.groupby("항목")["금액"].sum()

        if 항목별합계.empty:
            messagebox.showinfo("알림", "지출 데이터가 없습니다.")
            return

        항목별합계.plot(kind="bar", color="skyblue")
        plt.title("항목별 지출 합계")
        plt.xlabel("항목")
        plt.ylabel("금액")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.grid(True, axis="y")
        plt.show()
    except Exception as e:
        messagebox.showerror("오류", f"그래프 출력 오류: {e}")

# ✅ 항목 검색
def 항목_검색():
    검색어 = 검색_entry.get().strip()
    if not 검색어:
        messagebox.showwarning("입력 오류", "검색할 항목명을 입력해주세요.")
        return
    try:
        df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
        결과 = df[df["항목"].astype(str).str.strip() == 검색어]

        if 결과.empty:
            messagebox.showinfo("검색 결과", f"'{검색어}' 항목에 해당하는 내역이 없습니다.")
            return

        win = Toplevel(root)
        win.title(f"항목 검색 결과 - {검색어}")
        win.geometry("600x400")

        text = Text(win)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = Scrollbar(win, command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)

        결과["금액"] = pd.to_numeric(결과["금액"], errors="coerce").fillna(0).astype(int)
        결과["금액"] = 결과["금액"].apply(lambda x: f"{x:,}")
        text.insert(tk.END, 결과.to_string(index=False))
    except Exception as e:
        messagebox.showerror("오류", f"검색 중 오류 발생: {e}")

# ✅ 날짜 검색
def 날짜_검색():
    start = 시작날짜_entry.get().strip()
    end = 종료날짜_entry.get().strip()
    if not start or not end:
        messagebox.showwarning("입력 오류", "시작과 종료 날짜를 모두 입력해주세요.")
        return
    try:
        df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
        df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
        df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0)

        start_date = pd.to_datetime(start)
        end_date = pd.to_datetime(end)

        result = df[(df["날짜"] >= start_date) & (df["날짜"] <= end_date)]

        if result.empty:
            messagebox.showinfo("검색 결과", f"{start} ~ {end} 사이의 내역이 없습니다.")
            return

        win = Toplevel(root)
        win.title(f"날짜 검색 결과: {start} ~ {end}")
        win.geometry("600x400")

        text = Text(win)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = Scrollbar(win, command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)

        result["금액"] = result["금액"].astype(int)
        result["금액"] = result["금액"].apply(lambda x: f"{x:,}")
        text.insert(tk.END, result.to_string(index=False))
    except Exception as e:
        messagebox.showerror("오류", f"날짜 검색 중 오류 발생: {e}")

# ✅ 월별 통계
def 월별_통계():
    month = 월_entry.get().strip()
    if not month or len(month) != 7:
        messagebox.showwarning("입력 오류", "형식에 맞게 'YYYY-MM' 형식으로 입력해주세요.")
        return
    try:
        df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
        df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
        df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0)
        df["연월"] = df["날짜"].dt.to_period("M").astype(str)
        해당월 = df[df["연월"] == month]

        if 해당월.empty:
            messagebox.showinfo("통계 없음", f"{month}에는 내역이 없습니다.")
            return

        수입 = 해당월[해당월["구분"] == "수입"]["금액"].sum()
        지출 = 해당월[해당월["구분"] == "지출"]["금액"].sum()
        잔액 = 수입 - 지출

        messagebox.showinfo(f"{month} 월별 통계",
            f"💰 수입: {수입:,.0f} 원\n💸 지출: {지출:,.0f} 원\n📌 잔액: {잔액:,.0f} 원")
    except Exception as e:
        messagebox.showerror("오류", f"월별 통계 계산 중 오류 발생: {e}")

# ✅ GUI 구성
root = tk.Tk()
root.title("미니 가계부")
root.geometry("1000x700")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

tab_input = ttk.Frame(notebook)
tab_view = ttk.Frame(notebook)
tab_stats = ttk.Frame(notebook)
tab_search = ttk.Frame(notebook)

notebook.add(tab_input, text="📥 내역 입력")
notebook.add(tab_view, text="📋 전체 조회")
notebook.add(tab_stats, text="📊 통계 보기")
notebook.add(tab_search, text="🔍 검색")

# 📥 내역 입력 탭
tk.Label(tab_input, text="날짜 (yyyy-mm-dd):").pack()
날짜_entry = tk.Entry(tab_input)
날짜_entry.pack()

tk.Label(tab_input, text="구분:").pack()
구분_var = tk.StringVar(value="지출")
tk.Radiobutton(tab_input, text="수입", variable=구분_var, value="수입").pack()
tk.Radiobutton(tab_input, text="지출", variable=구분_var, value="지출").pack()

tk.Label(tab_input, text="항목:").pack()
항목_entry = tk.Entry(tab_input)
항목_entry.pack()

tk.Label(tab_input, text="금액:").pack()
금액_entry = tk.Entry(tab_input)
금액_entry.pack()

tk.Label(tab_input, text="메모 (선택):").pack()
메모_entry = tk.Entry(tab_input)
메모_entry.pack()

tk.Button(tab_input, text="저장하기", command=저장하기).pack(pady=10)

# 📋 전체 조회 탭
tk.Button(tab_view, text="전체 내역 보기", command=전체_조회).pack(pady=20)

# 📊 통계 보기 탭
tk.Button(tab_stats, text="수입/지출 통계", command=통계_보기).pack(pady=10)
tk.Button(tab_stats, text="항목별 지출 그래프", command=지출_그래프).pack(pady=10)

tk.Label(tab_stats, text="월별 통계 (예: 2025-08)").pack()
월_entry = tk.Entry(tab_stats)
월_entry.pack()
tk.Button(tab_stats, text="월별 통계 보기", command=월별_통계).pack(pady=5)

# 🔍 검색 탭
tk.Label(tab_search, text="항목명 입력").pack()
검색_entry = tk.Entry(tab_search)
검색_entry.pack()
tk.Button(tab_search, text="항목 검색", command=항목_검색).pack(pady=5)

tk.Label(tab_search, text="🗓 시작 날짜 (yyyy-mm-dd)").pack()
시작날짜_entry = tk.Entry(tab_search)
시작날짜_entry.pack()
tk.Label(tab_search, text="종료 날짜 (yyyy-mm-dd)").pack()
종료날짜_entry = tk.Entry(tab_search)
종료날짜_entry.pack()
tk.Button(tab_search, text="날짜 범위 검색", command=날짜_검색).pack(pady=5)

root.mainloop()