import tkinter as tk
from tkinter import messagebox, Toplevel, Text, Scrollbar, ttk
import csv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
from tkinter import filedialog
import shutil

# 한글 폰트 설정
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

fileName = "가계부.csv"
if not os.path.exists(fileName):
    with open(fileName, "w", newline="", encoding="cp949") as f:
        pass  # 빈 파일 생성

def 종료_시_백업():
    if os.path.exists(fileName):
        backup_name = f"backup_{fileName}.csv"
        shutil.copy(fileName, backup_name)
        print(f"자동 백업 완료: {backup_name}")


# ✅ 저장 함수
def 저장하기():
    date = 날짜_entry.get()
    if not date:
        date = datetime.today().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("입력 오류", "날짜 형식은 YYYY-MM-DD이어야 합니다.")
            return

    type_ = 구분_var.get().strip()
    category = 항목_entry.get().strip()
    amount = 금액_entry.get().strip()
    note = 메모_entry.get().strip()

    if type_ not in ["수입", "지출"]:
        messagebox.showwarning("입력 오류", "구분은 '수입' 또는 '지출'만 가능합니다.")
        return

    if not category:
        messagebox.showwarning("입력 오류", "항목을 입력해주세요.")
        return

    if not amount.isdigit():
        messagebox.showwarning("입력 오류", "금액은 숫자만 입력 가능합니다.")
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
    win.geometry("700x400")
    
    # 정렬 기준 선택 Combobox
    정렬기준_label = tk.Label(win, text="정렬 기준 선택:")
    정렬기준_label.pack()

    정렬기준_combobox = ttk.Combobox(win, values=["날짜", "금액", "항목"])
    정렬기준_combobox.set("날짜")
    정렬기준_combobox.pack(pady=5)

    text = Text(win)
    text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    scrollbar = Scrollbar(win, command=text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text.config(yscrollcommand=scrollbar.set)

    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    def 정렬_및_출력():
        기준 = 정렬기준_combobox.get()
        if 기준 == "금액":
            정렬_df = df.sort_values(by="금액", ascending=False)
        elif 기준 == "항목":
            정렬_df = df.sort_values(by="항목")
        else:  # 날짜
            정렬_df = df.sort_values(by="날짜", ascending=True)

        정렬_df["금액"] = 정렬_df["금액"].apply(lambda x: f"{x:,}")
        text.delete("1.0", tk.END)
        text.insert(tk.END, 정렬_df.to_string(index=False))

    tk.Button(win, text="정렬 보기", command=정렬_및_출력).pack(pady=5)

    정렬_및_출력()  # 초기 출력

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
        검색결과 = df[df["항목"].astype(str).str.strip() == 검색어]

        if 검색결과.empty:
            messagebox.showinfo("검색 결과", f"'{검색어}' 항목에 해당하는 내역이 없습니다.")
            return

        win = Toplevel(root)
        win.title(f"항목 검색 결과 - {검색어}")
        win.geometry("700x400")
        
        tree = ttk.Treeview(win, columns=("날짜", "구분", "항목", "금액", "메모"), show="headings")
        for col in ("날짜", "구분", "항목", "금액", "메모"):
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(expand=True, fill="both")
        검색결과["금액"] = pd.to_numeric(검색결과["금액"], errors="coerce").fillna(0).astype(int)
        검색결과["금액"] = 검색결과["금액"].apply(lambda x: f"{x:,}")
        
        for i, row in 검색결과.iterrows():
            tree.insert("", "end", values=list(row))
        
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

def 초기화():
    if not os.path.exists(fileName):
        with open(fileName, "w", newline="", encoding="cp949") as f:
            writer = csv.writer(f)
            writer.writerow(["날짜", "구분", "항목", "금액", "메모"])
            
def 내역_관리():
    try:
        df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
        
        win = Toplevel(root)
        win.title("내역 수정 / 삭제")
        win.geometry("700x500")
        
        tree = ttk.Treeview(win, columns=("날짜", "구분", "항목", "금액", "메모"), show="headings")
        for col in ( "날짜", "구분", "항목", "금액", "메모"):
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # 데이터 삽입
        for i, row in df.iterrows():
            tree.insert("", "end", iid=i, values=list(row))
        
        tree.pack(expand=True, fill="both")
        
        # 수정 함수
        def 수정():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("선택 오류", "수정할 항목을 선택하세요")
                return
            
            i = int(selected[0])
            new_data = [수정_entry[col].get() for col in ("날짜", "구분", "항목", "금액", "메모")]
            df.loc[i] = new_data
            df.to_csv(fileName, index=False, header=False, encoding="cp949")
            messagebox.showinfo("완료", "수정되었습니다.")
            win.destroy()
            
        # 삭제 함수
        def 삭제():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("선택 오류", "삭제할 항목을 선택하세요.")
                return
        
            i = int(selected[0])
            df.drop(index=i, inplace=True)
            df.to_csv(fileName, index=False, header=False, encoding="cp949")
            messagebox.showinfo("완료", "삭제되었습니다.")
            win.destroy()
        
        # 선택된 값 입력창
        수정_frame = tk.Frame(win)
        수정_frame.pack(pady=10)

        수정_entry = {}
        for col in ("날짜", "구분", "항목", "금액", "메모"):
            tk.Label(수정_frame, text=col).pack()
            entry = tk.Entry(수정_frame)
            entry.pack()
            수정_entry[col] = entry

        def 선택_채우기(event):
            selected = tree.selection()
            if not selected:
                return
            values = tree.item(selected)["values"]
            for col, val in zip(("날짜", "구분", "항목", "금액", "메모"), values):
                수정_entry[col].delete(0, tk.END)
                수정_entry[col].insert(0, val)

        tree.bind("<<TreeviewSelect>>", 선택_채우기)

        # 버튼
        tk.Button(win, text="수정하기", command=수정).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(win, text="삭제하기", command=삭제).pack(side=tk.RIGHT, padx=20, pady=10)
        
    except Exception as e:
        messagebox.showerror("오류", f"내역 관리 중 오류 발생: {e}")

def 엑셀_내보내기():
    try:
        df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
        
        # 저장할 경로 선택
        path = asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel 파일", "*.xlsx")])
        if not path:
            return

        df.to_excel(path, index=False)
        messagebox.showinfo("성공", f"엑셀로 저장 완료!\n{path}")
    except Exception as e:
        messagebox.showerror("오류", f"엑셀 내보내기 실패: {e}")

def 데이터_초기화():
    if not os.path.exists(fileName):
        messagebox.showinfo("안내", "초기화할 파일이 존재하지 않습니다.")
        return

    result = messagebox.askyesno("⚠ 데이터 초기화", "정말로 모든 데이터를 삭제하시겠습니까?")
    if result:
        try:
            open(fileName, "w", encoding="cp949").close()
            messagebox.showinfo("초기화 완료", "모든 데이터가 삭제되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"초기화 중 오류 발생: {e}")

def 항목별_필터링():
    try:
        df = pd.read_csv(fileName, names=["날짜", "구분", "항목", "금액", "메모"], encoding="cp949")
        항목_목록 = df["항목"].dropna().unique().tolist()

        if not 항목_목록:
            messagebox.showinfo("알림", "항목 데이터가 없습니다.")
            return

        win = Toplevel(root)
        win.title("항목별 내역 필터링")
        win.geometry("700x450")

        tk.Label(win, text="항목 선택:").pack()
        항목_combo = ttk.Combobox(win, values=항목_목록)
        항목_combo.pack(pady=5)

        text = Text(win)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = Scrollbar(win, command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)

        df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)

        def 필터링_실행():
            선택항목 = 항목_combo.get().strip()
            필터결과 = df[df["항목"] == 선택항목]

            if 필터결과.empty:
                text.delete("1.0", tk.END)
                text.insert(tk.END, f"'{선택항목}' 항목에 해당하는 내역이 없습니다.")
            else:
                필터결과["금액"] = 필터결과["금액"].apply(lambda x: f"{x:,}")
                text.delete("1.0", tk.END)
                text.insert(tk.END, 필터결과.to_string(index=False))

        tk.Button(win, text="항목별 보기", command=필터링_실행).pack(pady=5)

    except Exception as e:
        messagebox.showerror("오류", f"항목별 필터링 중 오류 발생: {e}")

def 데이터_백업():
    try:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_가계부_{now}.csv"
        shutil.copy(fileName, backup_name)
        messagebox.showinfo("백업 완료", f"{backup_name} 로 백업되었습니다.")
    except Exception as e:
        messagebox.showerror("백업 오류", f"백업 중 오류 발생: {e}")

def 데이터_복원():
    try:
        path = filedialog.askopenfilename(title="복원할 백업 파일 선택", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        shutil.copy(path, fileName)
        messagebox.showinfo("복원 완료", f"{path} 의 내용으로 복원되었습니다.")
    except Exception as e:
        messagebox.showerror("복원 오류", f"복원 중 오류 발생: {e}")

# ✅ GUI 구성
root = tk.Tk()
root.title("미니 가계부")
root.geometry("1000x700")

root.protocol("WM_DELETE_WINDOW", lambda: [종료_시_백업(), root.destroy()])  # 창 닫을 때 백업

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

tab_input = ttk.Frame(notebook)
tab_view = ttk.Frame(notebook)
tab_stats = ttk.Frame(notebook)
tab_search = ttk.Frame(notebook)
tab_manage = ttk.Frame(notebook)

notebook.add(tab_input, text="📥 내역 입력")
notebook.add(tab_view, text="📋 전체 조회")
notebook.add(tab_stats, text="📊 통계 보기")
notebook.add(tab_search, text="🔍 검색")
notebook.add(tab_manage, text="🔍 내역 관리")

# 📥 내역 입력 탭
tk.Label(tab_input, text="날짜 (yyyy-mm-dd):").pack()
날짜_entry = tk.Entry(tab_input)
날짜_entry.pack()

tk.Label(tab_input, text="구분:").pack()
구분_var = tk.StringVar(value="지출")
tk.Radiobutton(tab_input, text="수입", variable=구분_var, value="수입").pack()
tk.Radiobutton(tab_input, text="지출", variable=구분_var, value="지출").pack()

# 자주 사용하는 항목 목록
항목_리스트 = ["식비", "교통", "월급", "쇼핑", "문화", "기타"]
tk.Label(tab_input, text="항목:").pack()
항목_entry = ttk.Combobox(tab_input, values=항목_리스트)
항목_entry.set("식비")
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
tk.Button(tab_view, text="📁 엑셀로 내보내기", command=엑셀_내보내기).pack(pady=10)
tk.Button(tab_view, text="🧹 CSV 데이터 초기화", command=데이터_초기화).pack(pady=10)

# 📊 통계 보기 탭
tk.Button(tab_stats, text="수입/지출 통계", command=통계_보기).pack(pady=10)
tk.Button(tab_stats, text="항목별 지출 그래프", command=지출_그래프).pack(pady=10)

tk.Label(tab_stats, text="월별 통계 (예: 2025-08)").pack()
월_entry = tk.Entry(tab_stats)
월_entry.pack()
tk.Button(tab_stats, text="월별 통계 보기", command=월별_통계).pack(pady=5)

tk.Button(tab_stats, text="📁 데이터 백업", command=데이터_백업).pack(pady=5)
tk.Button(tab_stats, text="📂 데이터 복원", command=데이터_복원).pack(pady=5)

# 🔍 검색 탭
tk.Label(tab_search, text="항목:").pack()
항목_리스트 = ["식비", "교통", "월급", "쇼핑", "문화", "기타"]
항목_entry = ttk.Combobox(tab_search, values=항목_리스트)
항목_entry.set("식비")
항목_entry.pack()
tk.Button(tab_search, text="항목 검색", command=항목_검색).pack(pady=5)

tk.Label(tab_search, text="🗓 시작 날짜 (yyyy-mm-dd)").pack()
시작날짜_entry = tk.Entry(tab_search)
시작날짜_entry.pack()
tk.Label(tab_search, text="종료 날짜 (yyyy-mm-dd)").pack()
종료날짜_entry = tk.Entry(tab_search)
종료날짜_entry.pack()
tk.Button(tab_search, text="날짜 범위 검색", command=날짜_검색).pack(pady=5)
tk.Button(tab_search, text="항목별 필터링", command=항목별_필터링).pack(pady=5)

tk.Label(tab_manage, text="내역 관리",).pack()
tk.Button(tab_manage, text="내역 수정/삭제", command=내역_관리).pack(pady=10)

# 실행 시작
if __name__ == "__main__":
    초기화()
    root.mainloop()