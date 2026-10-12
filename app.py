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
    'Mô phỏng thuật toán BitTable F1 theo quy trình chạy tay '
    'và tự động lặp đến khi thuật toán kết thúc'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# 4. HÀM CƠ BẢN
# ============================================================

def binary(value, length):
    """Chuyển số nguyên sang chuỗi nhị phân đủ số bit."""
    return bin(int(value))[2:].zfill(length)


def popcount(value):
    """Đếm số bit 1."""
    return bin(int(value)).count("1")


def format_itemset(items):
    """Hiển thị itemset dạng {A, C, T}."""
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
    """AND các vector bit dọc."""

    if len(items) == 0:
        return 0

    result = vectors[items[0]]

    for item in items[1:]:
        result &= vectors[item]

    return result


def mid(value):
    """
    MID(E) = E & (E - 1)
    """
    return value & (value - 1)


def support_percent(support, total):
    if total == 0:
        return 0

    return support / total * 100


def sort_itemset(itemset, item_order):
    """
    Sắp xếp itemset theo thứ tự bit/item.
    """

    return tuple(
        sorted(
            itemset,
            key=lambda x: item_order.index(x)
        )
    )


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
# 6. DỮ LIỆU MẪU THEO SLIDE
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

        st.error(
            f"Không thể đọc file CSV: {e}"
        )

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

    selected_column = st.sidebar.selectbox(
        "Chọn cột chứa giao dịch",
        df_upload.columns
    )

    st.sidebar.caption(
        "Cột này phải chứa danh sách các item của từng giao dịch."
    )

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

            # Ví dụ:
            # ACTW -> A,C,T,W
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
    min_value=0.1,
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

    st.error(
        "Không tìm thấy item."
    )

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
# 12. THỨ TỰ ITEM
# ============================================================

item_order = all_items.copy()


# ============================================================
# 13. TẠO VECTOR DỌC
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
# 14. THÔNG TIN BÀI TOÁN
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
    f"MinSup count = ceil({N} × {minsup_percent:g} / 100) "
    f"= {min_sup_count}"
)


# ============================================================
# 15. HIỂN THỊ CSDL
# ============================================================

st.markdown(
    '<div class="section-title">'
    '4.1. Cơ sở dữ liệu & Ngưỡng phổ biến'
    '</div>',
    unsafe_allow_html=True
)

database_rows = []

for index, transaction in enumerate(transactions):

    tid = f"T{index + 1}"

    code = 0

    for item in transaction:

        if item in item_codes:

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


df_database = pd.DataFrame(
    database_rows
)

st.dataframe(
    df_database,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 16. BƯỚC 1 - VECTOR BIT DỌC
# ============================================================

st.markdown(
    '<div class="section-title">'
    '4.2. Bước 1: Khởi tạo Vector Bit dọc'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "Mỗi bit tương ứng với một giao dịch "
    "T1 → Tn."
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
# 17. XÁC ĐỊNH L1
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


frequent_levels = {}

if len(L1) > 0:

    frequent_levels[1] = L1


st.success(
    f"L₁ = {format_itemset([x[0] for x in L1])} "
    f"— {len(L1)} mục 1-phổ biến"
)


# ============================================================
# 18. HIỂN THỊ THÔNG TIN THUẬT TOÁN
# ============================================================

st.markdown(
    '<div class="section-title">'
    '4.3. Quy trình BitTable F1'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    """
Thuật toán sẽ tự động thực hiện:

L₁ → C₂ → L₂ → C₃ → L₃ → ... → Cₖ → Lₖ

Thuật toán chỉ dừng khi:
1. Không còn ứng viên để sinh cấp tiếp theo, hoặc
2. Cấp tiếp theo không còn tập phổ biến.
"""
)


# ============================================================
# 19. C2
# ============================================================

st.markdown(
    '<div class="section-title">'
    '4.4. Bước 2: Sinh C₂ và xác định L₂'
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

        conclusion = (
            f"Loại (< {min_sup_count})"
        )

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

        "Phép AND":
            and_expression,

        "Vector kết quả":
            binary(
                vector_result,
                N
            ) + "₂",

        "Popcount":
            support,

        "Support (%)":
            f"{support_percent(support, N):.1f}%",

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

if len(L2) > 0:

    frequent_levels[2] = L2

st.success(
    f"L₂ gồm {len(L2)} tập phổ biến."
)


# ============================================================
# 20. HÀM HIỂN THỊ MID
# ============================================================

def show_mid_table(level_items, level_name):

    mid_rows = []

    for itemset in level_items:

        code = itemset_code(
            itemset,
            item_codes
        )

        code_minus_one = code - 1

        mid_value = mid(code)

        mid_rows.append({

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

            "MID(E) = E & (E-1)":
                binary(
                    mid_value,
                    number_items
                ) + "₂"
        })

    st.subheader(
        f"MID của {level_name}"
    )

    st.latex(
        r"MID(E) = E \ \& \ (E-1)"
    )

    if len(mid_rows) > 0:

        st.dataframe(
            pd.DataFrame(mid_rows),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 21. HÀM SINH CẤP TIẾP THEO BẰNG MID
# ============================================================

def generate_candidates_by_mid(
    current_L,
    next_size
):

    # --------------------------------------------------------
    # Tính MID
    # --------------------------------------------------------

    mid_groups = {}

    mid_information = []

    for itemset in current_L:

        code = itemset_code(
            itemset,
            item_codes
        )

        mid_value = mid(code)

        if mid_value not in mid_groups:

            mid_groups[mid_value] = []

        mid_groups[mid_value].append(
            itemset
        )

        mid_information.append({

            "Tập E":
                format_itemset(itemset),

            "Mã E":
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

    # --------------------------------------------------------
    # Sinh candidate
    # --------------------------------------------------------

    candidate_details = []

    candidate_set = set()

    for mid_value, group in mid_groups.items():

        if len(group) < 2:
            continue

        for i in range(len(group)):

            for j in range(i + 1, len(group)):

                E1 = group[i]
                E2 = group[j]

                candidate = tuple(
                    sorted(
                        set(E1) | set(E2),
                        key=lambda x: item_order.index(x)
                    )
                )

                if len(candidate) != next_size:

                    continue

                candidate_set.add(
                    candidate
                )

                candidate_details.append({

                    "MID":
                        binary(
                            mid_value,
                            number_items
                        ) + "₂",

                    "E1":
                        format_itemset(E1),

                    "E2":
                        format_itemset(E2),

                    "Ứng viên":
                        format_itemset(candidate)
                })

    C_next = sorted(
        candidate_set,
        key=lambda x: tuple(
            item_order.index(i)
            for i in x
        )
    )

    return (
        C_next,
        mid_information,
        candidate_details
    )


# ============================================================
# 22. VÒNG LẶP TỔNG QUÁT
# ============================================================

current_L = L2
current_k = 2

while len(current_L) > 0:

    next_k = current_k + 1

    # --------------------------------------------------------
    # HIỂN THỊ MID CỦA CẤP HIỆN TẠI
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        f'4.{next_k + 2}. Bước: MID của L{current_k}'
        '</div>',
        unsafe_allow_html=True
    )

    show_mid_table(
        current_L,
        f"L{current_k}"
    )

    # --------------------------------------------------------
    # SINH C(k+1)
    # --------------------------------------------------------

    C_next, mid_information, candidate_details = \
        generate_candidates_by_mid(
            current_L,
            next_k
        )

    st.subheader(
        f"Sinh C{next_k} bằng MID"
    )

    if len(candidate_details) > 0:

        st.dataframe(
            pd.DataFrame(candidate_details),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            f"Không có cặp nào trong L{current_k} "
            f"có cùng MID để sinh C{next_k}."
        )

    # --------------------------------------------------------
    # KHÔNG CÒN ỨNG VIÊN
    # --------------------------------------------------------

    if len(C_next) == 0:

        st.warning(
            f"C{next_k} = ∅ "
            f"→ không thể sinh cấp tiếp theo. "
            f"Thuật toán kết thúc."
        )

        break

    # --------------------------------------------------------
    # ĐÁNH GIÁ C(k+1)
    # --------------------------------------------------------

    st.subheader(
        f"C{next_k} → L{next_k}"
    )

    next_L = []

    candidate_rows = []

    for candidate in C_next:

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

        percentage = support_percent(
            support,
            N
        )

        if support >= min_sup_count:

            conclusion = (
                f"Thuộc L{next_k}"
            )

            next_L.append(
                candidate
            )

        else:

            conclusion = (
                f"Loại (< {min_sup_count})"
            )

        candidate_rows.append({

            f"Ứng viên (C{next_k})":
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

            "Support (%)":
                f"{percentage:.1f}%",

            "Kết luận":
                conclusion
        })

    st.dataframe(
        pd.DataFrame(candidate_rows),
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # LƯU L(k+1)
    # --------------------------------------------------------

    st.success(
        f"L{next_k} gồm "
        f"{len(next_L)} tập phổ biến."
    )

    if len(next_L) > 0:

        frequent_levels[next_k] = next_L

    # --------------------------------------------------------
    # KHÔNG CÒN L(k+1)
    # --------------------------------------------------------

    if len(next_L) == 0:

        st.warning(
            f"L{next_k} = ∅ "
            f"→ không còn tập phổ biến. "
            f"Thuật toán kết thúc."
        )

        break

    # --------------------------------------------------------
    # TIẾP TỤC
    # --------------------------------------------------------

    current_L = next_L
    current_k = next_k


# ============================================================
# 23. TỔNG HỢP TẤT CẢ TẬP PHỔ BIẾN
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📊 Tổng hợp toàn bộ tập phổ biến'
    '</div>',
    unsafe_allow_html=True
)

all_frequent = []

for level, level_items in sorted(
    frequent_levels.items()
):

    for itemset in level_items:

        all_frequent.append(
            (level, itemset)
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
            f"L{level}",

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
# 24. THỐNG KÊ TỰ ĐỘNG
# ============================================================

st.header("📈 Thống kê")

stats_rows = []

for level, level_items in sorted(
    frequent_levels.items()
):

    stats_rows.append({

        "Mức":
            f"L{level}",

        "Số tập phổ biến":
            len(level_items)
    })


df_stats = pd.DataFrame(
    stats_rows
)

st.dataframe(
    df_stats,
    use_container_width=True,
    hide_index=True
)


total = sum(
    len(level_items)
    for level_items
    in frequent_levels.values()
)


st.metric(
    "🎯 TỔNG SỐ TẬP PHỔ BIẾN",
    total
)


# ============================================================
# 25. DANH SÁCH TOÀN BỘ TẬP PHỔ BIẾN
# ============================================================

st.header(
    "🎯 Danh sách toàn bộ tập phổ biến"
)

for level, level_items in sorted(
    frequent_levels.items()
):

    st.subheader(
        f"L{level} — {len(level_items)} tập"
    )

    if len(level_items) > 0:

        text = " , ".join(
            format_itemset(itemset)
            for itemset in level_items
        )

        st.code(text)


# ============================================================
# 26. KIỂM TRA KẾT QUẢ CHUẨN CỦA SLIDE
# ============================================================

if (
    data_source == "Dữ liệu mẫu theo slide"
    and abs(minsup_percent - 50) < 0.0001
):

    expected = {
        1: 5,
        2: 8,
        3: 5,
        4: 1
    }

    actual = {
        level: len(items)
        for level, items
        in frequent_levels.items()
    }

    if (
        actual.get(1, 0) == 5
        and actual.get(2, 0) == 8
        and actual.get(3, 0) == 5
        and actual.get(4, 0) == 1
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

            <b>L₅ = ∅ → Thuật toán dừng</b><br><br>

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
# 27. XUẤT KẾT QUẢ
# ============================================================

st.header(
    "📥 Xuất kết quả"
)

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
# 28. FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "BitTable F1 | "
    "L₁ → C₂/L₂ → MID/C₃/L₃ → "
    "MID/C₄/L₄ → ... → dừng khi không còn ứng viên/tập phổ biến"
)