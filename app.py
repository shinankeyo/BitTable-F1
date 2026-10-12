import streamlit as st
import pandas as pd
import math
from itertools import combinations


# ============================================================
# 1. CẤU HÌNH STREAMLIT
# ============================================================

st.set_page_config(
    page_title="BitTable F1 - Khai thác tập phổ biến",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# 2. CSS
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 5px;
}

.sub-title {
    color: #666;
    font-size: 16px;
    margin-bottom: 25px;
}

.section-title {
    font-size: 25px;
    font-weight: 700;
    margin-top: 25px;
}

.result-box {
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #ddd;
    margin-top: 10px;
    margin-bottom: 15px;
}

.success-box {
    padding: 18px;
    border-radius: 10px;
    background-color: #e8f5e9;
    border: 1px solid #81c784;
}

.warning-box {
    padding: 18px;
    border-radius: 10px;
    background-color: #fff8e1;
    border: 1px solid #ffcc80;
}

.step-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #f5f7fa;
    border-left: 5px solid #4a90e2;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. TIÊU ĐỀ
# ============================================================

st.markdown(
    '<div class="main-title">📊 BitTable F1 – Khai thác tập phổ biến</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Mô phỏng bài toán theo quy trình chạy tay BitTable F1'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# 4. HÀM XỬ LÝ
# ============================================================

def binary(value, length):
    """
    Chuyển số nguyên sang nhị phân với đủ số bit.
    """
    return bin(int(value))[2:].zfill(length)


def popcount(value):
    """
    Đếm số bit 1.
    """
    return bin(int(value)).count("1")


def format_itemset(items):
    """
    {A, C, T}
    """
    return "{" + ", ".join(items) + "}"


def itemset_code(items, item_codes):
    """
    Mã bit của itemset bằng phép OR.

    Ví dụ:

    A = 10000
    C = 01000
    T = 00010

    ACT = 11010
    """

    value = 0

    for item in items:
        value |= item_codes[item]

    return value


def vector_and(items, vectors):
    """
    AND các vector dọc.
    """

    result = vectors[items[0]]

    for item in items[1:]:
        result &= vectors[item]

    return result


def mid(value):
    """
    MID = E & (E - 1)
    """

    return value & (value - 1)


def support_percent(support, total):
    return support / total * 100


# ============================================================
# 5. SIDEBAR - CHỌN DỮ LIỆU
# ============================================================

st.sidebar.header("⚙️ CẤU HÌNH DỮ LIỆU")

data_source = st.sidebar.radio(
    "Nguồn dữ liệu",
    [
        "Dữ liệu mẫu theo slide",
        "Upload file CSV"
    ]
)


# ============================================================
# 6. DỮ LIỆU MẪU
# ============================================================

sample_transactions = [
    ["A", "C", "T", "W"],
    ["C", "D", "W"],
    ["A", "C", "T", "W"],
    ["A", "C", "D", "W"],
    ["A", "C", "D", "T", "W"],
    ["C", "D", "T"]
]


# ============================================================
# 7. ĐỌC DỮ LIỆU
# ============================================================

transactions = []


if data_source == "Dữ liệu mẫu theo slide":

    transactions = sample_transactions.copy()

else:

    uploaded_file = st.sidebar.file_uploader(
        "📁 Chọn file CSV",
        type=["csv"]
    )

    if uploaded_file is None:

        st.info(
            "👈 Hãy upload file CSV ở thanh bên trái."
        )

        st.stop()

    try:

        df_upload = pd.read_csv(uploaded_file)

    except Exception as e:

        st.error(f"Không thể đọc file CSV: {e}")

        st.stop()


    st.sidebar.success(
        f"Đã đọc file: {uploaded_file.name}"
    )

    st.sidebar.write(
        f"Số dòng: {len(df_upload)}"
    )

    st.sidebar.write(
        f"Số cột: {len(df_upload.columns)}"
    )


    # --------------------------------------------------------
    # Chọn cột giao dịch
    # --------------------------------------------------------

    selected_column = st.sidebar.selectbox(
        "Chọn cột chứa giao dịch",
        df_upload.columns
    )


    st.sidebar.caption(
        "Cột này phải chứa danh sách các item của từng giao dịch."
    )


    # --------------------------------------------------------
    # Cách đọc dữ liệu
    # --------------------------------------------------------

    input_format = st.sidebar.radio(
        "Định dạng item trong cột",
        [
            "Các item viết liền nhau",
            "Các item cách nhau bằng dấu phẩy"
        ]
    )


    for value in df_upload[selected_column].dropna():

        text = str(value).strip()

        # Xóa ký hiệu tập hợp
        text = (
            text
            .replace("{", "")
            .replace("}", "")
            .replace("[", "")
            .replace("]", "")
            .strip()
        )


        if input_format == "Các item cách nhau bằng dấu phẩy":

            items = [
                x.strip()
                for x in text.split(",")
                if x.strip()
            ]

        else:

            # Ví dụ ACTW -> A,C,T,W
            items = list(
                text.replace(" ", "")
            )


        if len(items) > 0:

            transactions.append(items)


# ============================================================
# 8. KIỂM TRA DỮ LIỆU
# ============================================================

if len(transactions) == 0:

    st.error(
        "Không có giao dịch hợp lệ trong dữ liệu."
    )

    st.stop()


# ============================================================
# 9. MINIMUM SUPPORT
# ============================================================

st.sidebar.header("📌 THAM SỐ")

minsup_percent = st.sidebar.number_input(
    "MinSup (%)",
    min_value=1.0,
    max_value=100.0,
    value=50.0,
    step=1.0
)


N = len(transactions)

min_sup_raw = N * minsup_percent / 100

min_sup_count = math.ceil(min_sup_raw)


# ============================================================
# 10. XÁC ĐỊNH TOÀN BỘ ITEM
# ============================================================

all_items = sorted(
    set(
        item
        for transaction in transactions
        for item in transaction
    )
)


if len(all_items) == 0:

    st.error("Không tìm thấy item.")

    st.stop()


# ============================================================
# 11. MÃ BIT CHO ITEM
# ============================================================

item_codes = {}

number_items = len(all_items)

for index, item in enumerate(all_items):

    position = number_items - 1 - index

    item_codes[item] = 1 << position


# ============================================================
# 12. TẠO VECTOR DỌC
# ============================================================

vectors = {}

for item in all_items:

    value = 0

    for tid, transaction in enumerate(transactions):

        if item in transaction:

            position = N - 1 - tid

            value |= 1 << position

    vectors[item] = value


# ============================================================
# 13. THÔNG TIN BÀI TOÁN
# ============================================================

st.header("📌 Thông tin bài toán")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Số giao dịch",
        N
    )

with col2:
    st.metric(
        "Số item",
        len(all_items)
    )

with col3:
    st.metric(
        "MinSup",
        f"{minsup_percent:g}%"
    )

with col4:
    st.metric(
        "MinSup count",
        min_sup_count
    )


st.info(
    f"MinSup count = ceil({N} × {minsup_percent:g}%) "
    f"= {min_sup_count}"
)


# ============================================================
# 14. HIỂN THỊ CSDL
# ============================================================

st.markdown(
    '<div class="section-title">'
    '4.1. Cơ sở dữ liệu mẫu & Ngưỡng phổ biến'
    '</div>',
    unsafe_allow_html=True
)


database_rows = []


for index, transaction in enumerate(transactions):

    tid = f"T{index + 1}"

    code = 0

    for item in transaction:

        code |= item_codes[item]


    database_rows.append({
        "Giao dịch (TID)": tid,

        "Tập mục mua":
            format_itemset(transaction),

        "Biểu diễn Bit":
            binary(code, number_items) + "₂",

        "Giá trị nguyên":
            code
    })


df_database = pd.DataFrame(database_rows)


st.dataframe(
    df_database,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 15. BƯỚC 1 - VECTOR DỌC
# ============================================================

st.markdown(
    '<div class="section-title">'
    '4.2. Bước 1: Khởi tạo Vector Bit dọc'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    """
    Đọc CSDL để xây dựng vector bit dọc cho từng item.
    Mỗi bit tương ứng với một giao dịch T₁ → Tₙ.
    """
)


vector_rows = []


for item in all_items:

    code = item_codes[item]

    vector = vectors[item]

    support = popcount(vector)

    percentage = support_percent(
        support,
        N
    )


    result = (
        "Thuộc L₁"
        if support >= min_sup_count
        else "Loại"
    )


    vector_rows.append({

        "Mục":
            item,

        "Mã nhị phân":
            binary(code, number_items) + "₂",

        "Vector Bit dọc":
            binary(vector, N) + "₂",

        "Độ hỗ trợ (sup)":
            support,

        "Tỷ lệ (%)":
            f"{percentage:.1f}%",

        "Kết luận":
            result
    })


df_vectors = pd.DataFrame(
    vector_rows
)


st.dataframe(
    df_vectors,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 16. L1
# ============================================================

L1 = []


for item in all_items:

    support = popcount(
        vectors[item]
    )

    if support >= min_sup_count:

        L1.append(
            (item,)
        )


st.success(
    f"L₁ = {format_itemset([x[0] for x in L1])}"
    f" — {len(L1)} mục 1-phổ biến"
)


# ============================================================
# 17. BƯỚC 2 - C2
# ============================================================

st.markdown(
    '<div class="section-title">'
    '4.3. Bước 2: Sinh ứng viên C₂ và xác định L₂'
    '</div>',
    unsafe_allow_html=True
)


C2 = list(
    combinations(
        [x[0] for x in L1],
        2
    )
)


c2_rows = []

L2 = []


for candidate in C2:

    code = itemset_code(
        candidate,
        item_codes
    )


    vector_result = vector_and(
        candidate,
        vectors
    )


    support = popcount(
        vector_result
    )


    if support >= min_sup_count:

        conclusion = "Thuộc L₂"

        L2.append(candidate)

    else:

        conclusion = f"Loại (< {min_sup_count})"


    # Chuỗi phép AND
    and_expression = " AND ".join(
        [
            binary(
                vectors[item],
                N
            )
            for item in candidate
        ]
    )


    c2_rows.append({

        "Ứng viên (C₂)":
            format_itemset(candidate),

        "Mã bit":
            binary(code, number_items) + "₂",

        "Phép toán Bitwise AND":
            and_expression,

        "Vector kết quả":
            binary(
                vector_result,
                N
            ) + "₂",

        "Popcount":
            support,

        "Kết luận":
            conclusion
    })


df_c2 = pd.DataFrame(
    c2_rows
)


st.dataframe(
    df_c2,
    use_container_width=True,
    hide_index=True
)


st.success(
    f"L₂ gồm {len(L2)} tập phổ biến."
)


# ============================================================
# 18. BƯỚC 3 - MID CỦA L2
# ============================================================

st.markdown(
    '<div class="section-title">'
    '4.4. Bước 3: Sinh ứng viên C₃ bằng mặt nạ MID'
    '</div>',
    unsafe_allow_html=True
)


st.latex(
    r"MID(E) = E \ \& \ (E-1)"
)


mid_l2_rows = []


for itemset in L2:

    code = itemset_code(
        itemset,
        item_codes
    )

    code_minus_one = code - 1

    mid_value = mid(code)


    mid_l2_rows.append({

        "Tập E":
            format_itemset(itemset),

        "Mã bit E":
            binary(
                code,
                number_items
            ) + "₂",

        "E - 1":
            binary(
                code_minus_one,
                number_items
            ) + "₂",

        "MID(E)":
            binary(
                mid_value,
                number_items
            ) + "₂"
    })


df_mid_l2 = pd.DataFrame(
    mid_l2_rows
)


st.dataframe(
    df_mid_l2,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 19. SINH C3 BẰNG MID
# ============================================================

C3 = []

seen_c3 = set()


for i in range(len(L2)):

    for j in range(i + 1, len(L2)):

        E1 = L2[i]

        E2 = L2[j]


        code_E1 = itemset_code(
            E1,
            item_codes
        )


        code_E2 = itemset_code(
            E2,
            item_codes
        )


        MID_E1 = mid(code_E1)

        MID_E2 = mid(code_E2)


        # Chỉ ghép khi cùng MID
        if MID_E1 != MID_E2:
            continue


        candidate = tuple(
            sorted(
                set(E1) | set(E2),
                key=lambda x:
                    all_items.index(x)
            )
        )


        if len(candidate) != 3:
            continue


        if candidate not in seen_c3:

            seen_c3.add(
                candidate
            )

            C3.append(
                candidate
            )


# ============================================================
# 20. ĐÁNH GIÁ C3
# ============================================================

c3_rows = []

L3 = []


for candidate in C3:

    code = itemset_code(
        candidate,
        item_codes
    )


    vector_result = vector_and(
        candidate,
        vectors
    )


    support = popcount(
        vector_result
    )


    if support >= min_sup_count:

        conclusion = "Thuộc L₃"

        L3.append(candidate)

    else:

        conclusion = f"Loại (< {min_sup_count})"


    c3_rows.append({

        "Ứng viên (C₃)":
            format_itemset(candidate),

        "Mã bit":
            binary(
                code,
                number_items
            ) + "₂",

        "Vector kết quả":
            binary(
                vector_result,
                N
            ) + "₂",

        "Popcount":
            support,

        "Tỷ lệ":
            f"{support_percent(support, N):.1f}%",

        "Kết luận":
            conclusion
    })


df_c3 = pd.DataFrame(
    c3_rows
)


st.dataframe(
    df_c3,
    use_container_width=True,
    hide_index=True
)


st.success(
    f"L₃ gồm {len(L3)} tập phổ biến."
)


# ============================================================
# 21. BƯỚC 4 - MID CỦA L3
# ============================================================

st.markdown(
    '<div class="section-title">'
    '4.5. Bước 4: Sinh ứng viên C₄ và xác định L₄'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    """
    Ghép các tập trong L₃ có cùng 2 mục tiền tố.
    Sử dụng MID để xác định các nhóm có thể ghép.
    """
)


mid_l3_rows = []


for itemset in L3:

    code = itemset_code(
        itemset,
        item_codes
    )


    mid_value = mid(code)


    mid_l3_rows.append({

        "Tập E":
            format_itemset(itemset),

        "Mã bit E":
            binary(
                code,
                number_items
            ) + "₂",

        "MID(E)":
            binary(
                mid_value,
                number_items
            ) + "₂"
    })


df_mid_l3 = pd.DataFrame(
    mid_l3_rows
)


st.dataframe(
    df_mid_l3,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 22. SINH C4
# ============================================================

C4 = []

seen_c4 = set()


for i in range(len(L3)):

    for j in range(i + 1, len(L3)):

        E1 = L3[i]

        E2 = L3[j]


        code_E1 = itemset_code(
            E1,
            item_codes
        )


        code_E2 = itemset_code(
            E2,
            item_codes
        )


        MID_E1 = mid(code_E1)

        MID_E2 = mid(code_E2)


        if MID_E1 != MID_E2:
            continue


        candidate = tuple(
            sorted(
                set(E1) | set(E2),
                key=lambda x:
                    all_items.index(x)
            )
        )


        if len(candidate) != 4:
            continue


        if candidate not in seen_c4:

            seen_c4.add(
                candidate
            )

            C4.append(
                candidate
            )


# ============================================================
# 23. ĐÁNH GIÁ C4
# ============================================================

c4_rows = []

L4 = []


for candidate in C4:

    code = itemset_code(
        candidate,
        item_codes
    )


    vector_result = vector_and(
        candidate,
        vectors
    )


    support = popcount(
        vector_result
    )


    if support >= min_sup_count:

        conclusion = "Thuộc L₄"

        L4.append(candidate)

    else:

        conclusion = f"Loại (< {min_sup_count})"


    c4_rows.append({

        "Ứng viên (C₄)":
            format_itemset(candidate),

        "Mã bit":
            binary(
                code,
                number_items
            ) + "₂",

        "Vector kết quả":
            binary(
                vector_result,
                N
            ) + "₂",

        "Popcount":
            support,

        "Tỷ lệ":
            f"{support_percent(support, N):.1f}%",

        "Kết luận":
            conclusion
    })


if len(c4_rows) > 0:

    df_c4 = pd.DataFrame(
        c4_rows
    )

    st.dataframe(
        df_c4,
        use_container_width=True,
        hide_index=True
    )


st.success(
    f"L₄ gồm {len(L4)} tập phổ biến."
)


# ============================================================
# 24. KIỂM TRA C5
# ============================================================

st.subheader("Kiểm tra cấp C₅")


C5 = []


for i in range(len(L4)):

    for j in range(i + 1, len(L4)):

        E1 = L4[i]

        E2 = L4[j]


        code_E1 = itemset_code(
            E1,
            item_codes
        )


        code_E2 = itemset_code(
            E2,
            item_codes
        )


        if mid(code_E1) == mid(code_E2):

            candidate = tuple(
                sorted(
                    set(E1) | set(E2),
                    key=lambda x:
                        all_items.index(x)
                )
            )


            if len(candidate) == 5:

                C5.append(
                    candidate
                )


if len(C5) == 0:

    st.warning(
        "Không còn tổ hợp hợp lệ để sinh cấp 5 → thuật toán kết thúc."
    )


# ============================================================
# 25. TỔNG HỢP 19 TẬP
# ============================================================

st.markdown(
    '<div class="section-title">'
    '4.6. Bảng tổng hợp kết quả'
    '</div>',
    unsafe_allow_html=True
)


all_frequent = []


for itemset in L1:

    all_frequent.append(
        ("L1", itemset)
    )


for itemset in L2:

    all_frequent.append(
        ("L2", itemset)
    )


for itemset in L3:

    all_frequent.append(
        ("L3", itemset)
    )


for itemset in L4:

    all_frequent.append(
        ("L4", itemset)
    )


final_rows = []


for level, itemset in all_frequent:

    vector_result = vector_and(
        itemset,
        vectors
    )


    support = popcount(
        vector_result
    )


    final_rows.append({

        "Kích thước":
            level,

        "Tập phổ biến":
            format_itemset(itemset),

        "Mã bit":
            binary(
                itemset_code(
                    itemset,
                    item_codes
                ),
                number_items
            ) + "₂",

        "Vector":
            binary(
                vector_result,
                N
            ) + "₂",

        "Support":
            support,

        "Support (%)":
            f"{support_percent(support, N):.1f}%"
    })


df_final = pd.DataFrame(
    final_rows
)


st.dataframe(
    df_final,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 26. THỐNG KÊ
# ============================================================

count_L1 = len(L1)

count_L2 = len(L2)

count_L3 = len(L3)

count_L4 = len(L4)

total = (
    count_L1
    + count_L2
    + count_L3
    + count_L4
)


c1, c2, c3, c4, c5 = st.columns(5)


with c1:
    st.metric(
        "L₁",
        count_L1
    )


with c2:
    st.metric(
        "L₂",
        count_L2
    )


with c3:
    st.metric(
        "L₃",
        count_L3
    )


with c4:
    st.metric(
        "L₄",
        count_L4
    )


with c5:
    st.metric(
        "TỔNG",
        total
    )


# ============================================================
# 27. KẾT QUẢ 19 TẬP - DẠNG DỄ NHÌN
# ============================================================

st.header("🎯 Danh sách toàn bộ tập phổ biến")


for level_name, level_items in [
    ("L₁", L1),
    ("L₂", L2),
    ("L₃", L3),
    ("L₄", L4)
]:

    st.subheader(
        f"{level_name} — {len(level_items)} tập"
    )


    if len(level_items) > 0:

        text = " , ".join(
            format_itemset(itemset)
            for itemset in level_items
        )

        st.code(text)


# ============================================================
# 28. KIỂM TRA KẾT QUẢ CHUẨN CỦA SLIDE
# ============================================================

if (
    data_source == "Dữ liệu mẫu theo slide"
    and abs(minsup_percent - 50) < 0.0001
):

    if (
        len(L1) == 5
        and len(L2) == 8
        and len(L3) == 5
        and len(L4) == 1
        and total == 19
    ):

        st.markdown(
            """
            <div class="success-box">

            <h2>✅ KẾT QUẢ KHỚP VỚI SLIDE</h2>

            <b>L₁ = 5</b><br>
            <b>L₂ = 8</b><br>
            <b>L₃ = 5</b><br>
            <b>L₄ = 1</b><br><br>

            <b>5 + 8 + 5 + 1 = 19 tập phổ biến</b>

            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.error(
            "Kết quả không khớp với bài toán chuẩn."
        )


# ============================================================
# 29. DOWNLOAD KẾT QUẢ
# ============================================================

st.header("📥 Xuất kết quả")


csv_result = df_final.to_csv(
    index=False,
    encoding="utf-8-sig"
)


st.download_button(
    label="⬇️ Tải bảng kết quả CSV",
    data=csv_result,
    file_name="BitTable_F1_result.csv",
    mime="text/csv"
)


# ============================================================
# 30. FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "BitTable F1 | L₁ → C₂/L₂ → MID/C₃/L₃ → MID/C₄/L₄ → C₅"
)