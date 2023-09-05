import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st


scopes = ["https://spreadsheets.google.com/feeds"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["cjson"], scopes)
client = gspread.authorize(credentials)
sheet_key = st.secrets["sheet_key"]
spreadsheet = client.open_by_key(sheet_key)
sheet_1 = spreadsheet.sheet1
sheet_pw = spreadsheet.worksheet("ACPW")


def get_password_dict():
    departments = sheet_pw.col_values(1)
    password = sheet_pw.col_values(2)
    password_dict = dict(zip(departments, password))

    departments.insert(0, "---您的單位---")
    return departments, password_dict


def get_data():
    data = sheet_1.get_all_values()
    return data


def get_departments_cols(data):
    departments_cols = [i+1 for i in range(len(data[1])) if data[1][i] != ""]
    departments_cols.insert(0, 0)
    return departments_cols


def get_department_rows(data, department):
    department_rows = []
    for i in range(len(data)):
      if department in data[i][3]:
        department_rows.append(i+1)
    return department_rows


def get_department_questions(data, department_rows):
    department_questions = []
    for i in department_rows:
        department_questions.append(data[i-1][2])
    return department_questions


def get_department_answers(data, department_rows, department_col):
    department_answers = []
    for i in department_rows:
        department_answers.append(data[i-1][department_col-1])
    return department_answers


def set_department_answers(data, department_rows, department_col, answers):
    for i in department_rows:
        data[i-1][department_col-1] = answers[department_rows.index(i)]
    return data


def update_answers(department_rows, department_col, answers):
    for row in department_rows:
        sheet_1.update_cell(row, department_col, answers[department_rows.index(row)])


def sended():
    st.session_state.data = set_department_answers(st.session_state.data, st.session_state.department_rows, st.session_state.department_col, st.session_state.answers)


def check_login(username_, password_, password_dict):
  if username_ not in password_dict.keys():
    return False
  if password_ == password_dict[username_]:
    return True
  else:
    return False


if "login" not in st.session_state:
  st.session_state.login = False
if 'department' not in st.session_state:
  st.session_state.department = "---您的單位---"
if 'departments' not in st.session_state:
  st.session_state.department = []
if 'data' not in st.session_state:
  st.session_state.data = []


def login_page():
    st.title("登入頁面")

    st.session_state.departments, password_dict  = get_password_dict()
    st.session_state.department = st.selectbox("請選擇您的單位", st.session_state.departments, index=0)
    password = st.text_input("請輸入密碼", type="password")
    login_button = st.button("登入")

    if login_button:
      if check_login(st.session_state.department, password, password_dict):
        st.success("Loading")
        st.session_state.data = get_data()
        st.session_state.login = True
        st.experimental_rerun()
      else:
        st.error("帳號或密碼錯誤")


def main_page():
    st.title("知識手冊第二階段審查意見表")
    departments_cols = get_departments_cols(st.session_state.data)
    department_col = dict(zip(st.session_state.departments, departments_cols))[st.session_state.department]
    st.session_state.department_col = department_col
    department_rows = get_department_rows(st.session_state.data, st.session_state.department)
    st.session_state.department_rows = department_rows
    department_questions = get_department_questions(st.session_state.data, department_rows)
    department_answers = get_department_answers(st.session_state.data, department_rows, department_col)
    answers = []

    if department_col != 0:
        with st.form("my_form"):
            for q in department_questions:
                st.session_state.q = st.text_area(q, value=dict(zip(department_questions, department_answers))[q], height=300)
                answers.append(st.session_state.q)
            st.session_state.answers = answers

            submitted = st.form_submit_button("提交") #, on_click=sended

            if submitted:
                update_answers(department_rows, department_col, answers)

                st.write("已收到您的答案，謝謝")


def main():
    st.set_page_config(page_title="知識手冊第二階段審查意見表", page_icon="⚡︎", layout="wide", initial_sidebar_state="collapsed")

    if not st.session_state.login:
        login_page()
    else:
        main_page()



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.write("出錯了，請重試")
        st.write(e)

