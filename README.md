# Seminar: Streaming Algorithms (Reservoir Sampling, Count-Min Sketch, HyperLogLog)

## 1) Data Stream là gì?

### 1.1 Khái niệm
**Data stream** là dữ liệu đến liên tục theo từng sự kiện (event), mỗi lần xử lý một phần tử, thay vì có toàn bộ dữ liệu ngay từ đầu.

Trong project:
- Mỗi dòng CSV = 1 event
- Trích một trường (`host`, `user_id`, `item_id`, ...) làm phần tử stream

### 1.2 Batch vs Streaming

| Tiêu chí | Batch Processing | Streaming Processing |
|---|---|---|
| Dữ liệu đầu vào | Có sẵn toàn bộ | Đến liên tục |
| Cách xử lý | Theo lô | Từng phần tử |
| Bộ nhớ | Thường lớn | Giới hạn, cố định |
| Độ trễ | Cao hơn | Thấp, gần realtime |

### 1.3 Vì sao cần Streaming Algorithms?
- Dữ liệu quá lớn, không thể giữ hết trong RAM
- Cần cập nhật kết quả nhanh theo thời gian thực
- Chấp nhận xấp xỉ để đổi lấy tốc độ và bộ nhớ thấp

### 1.4 Hạn chế cốt lõi
- **Memory limit:** không lưu toàn bộ stream
- **Time limit:** mỗi event phải xử lý rất nhanh, thường gần $O(1)$

---

## 2) Tạo data stream từ 2 file CSV

### 2.1 Ý tưởng
Đọc tuần tự:
1. File CSV thứ nhất
2. File CSV thứ hai  
Mỗi dòng đọc ra sẽ trích cột mục tiêu và `yield` ngay.

### 2.2 Minh họa generator

```python
def stream_items(file_paths, column_name):
    for path in file_paths:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for row in reader:
                yield row[column_name]
```

### 2.3 Ví dụ trực quan
- File A cho stream: `a, b, c`
- File B cho stream: `d, e`  
=> Stream liên tục: `a -> b -> c -> d -> e`

---

## 3) Giải thích 3 thuật toán

### A. Reservoir Sampling

#### Bài toán
Lấy ngẫu nhiên $k$ phần tử đại diện từ stream dài $N$ (thậm chí chưa biết trước $N$).

#### Ý tưởng
- Giữ một mảng kích thước $k$ (reservoir)
- $k$ phần tử đầu: cho vào luôn
- Với phần tử thứ $i > k$:
  - Random $j \in [1, i]$
  - Nếu $j \le k$, thay phần tử thứ $j$

#### Pseudocode
```text
reservoir = first k items
for i = k+1..N:
    j = random(1, i)
    if j <= k:
        reservoir[j] = item_i
```

#### Độ phức tạp
- Time/update: $O(1)$
- Memory: $O(k)$

#### Ưu / Nhược
- Ưu: đơn giản, nhẹ, tốt cho sampling
- Nhược: không chuyên cho frequency/distinct chính xác cao

---

### B. Count-Min Sketch (CMS)

#### Bài toán
Ước lượng tần suất xuất hiện của từng item trong stream lớn.

#### Ý tưởng
- Dùng bảng đếm 2D: `depth x width`
- Mỗi hàng có một hash function
- Update item: tăng đếm ở mỗi hàng tại cột hash tương ứng
- Query item: lấy **min** qua các hàng

#### Pseudocode
```text
init table[d][w] = 0
for each item x:
    for r in 1..d:
        c = hash_r(x) mod w
        table[r][c] += 1

estimate(x) = min_r table[r][hash_r(x) mod w]
```

#### Độ phức tạp
- Update: $O(d)$
- Query: $O(d)$
- Memory: $O(d \cdot w)$

Sai số thường theo tham số:

$$
w \approx \left\lceil \frac{e}{\epsilon}\right\rceil,\quad
d \approx \left\lceil \ln\frac{1}{\delta}\right\rceil
$$

#### Ưu / Nhược
- Ưu: tốt cho frequency/heavy hitters, memory nhỏ
- Nhược: có xu hướng **over-estimate** do collision

---

### C. HyperLogLog (HLL)

#### Bài toán
Ước lượng số lượng phần tử **distinct** trong stream rất lớn.

#### Ý tưởng
- Hash mỗi item thành chuỗi bit
- Dùng $m=2^p$ registers
- Một phần bit chọn register, phần còn lại đo số zero đầu tiên
- Tổng hợp các register để suy ra cardinality

#### Pseudocode
```text
init M[0..m-1] = 0
for each item x:
    h = hash(x)
    idx = first p bits
    w = remaining bits
    r = rank(first 1 in w)
    M[idx] = max(M[idx], r)

estimate = alpha_m * m^2 / sum(2^(-M[j]))
apply corrections if needed
```

#### Độ phức tạp
- Update: gần $O(1)$
- Memory: $O(m)$, rất thấp
- Sai số tương đối xấp xỉ:

$$
\text{RSE} \approx \frac{1.04}{\sqrt{m}}
$$

#### Ưu / Nhược
- Ưu: cực mạnh cho đếm distinct quy mô lớn
- Nhược: không dùng để ước lượng tần suất từng item

---

## 4) Benchmark thuật toán

### 4.1 Runtime

$$
\text{runtime} = t_{\text{end}} - t_{\text{start}}
$$

Đo tổng thời gian xử lý toàn bộ stream.

### 4.2 Memory usage
Đo peak memory khi chạy (ví dụ `tracemalloc`).

### 4.3 Estimation error

$$
\text{error\%} = \frac{|\hat{y} - y|}{y}\times 100
$$

- Reservoir/HLL: so với true distinct
- CMS: so với true frequency (thường trên top-k item)

### Vì sao quan trọng?
Streaming là bài toán đánh đổi **Speed – Memory – Accuracy**.  
Ba metric trên đo đúng 3 trục này.

---

## 5) Vẽ biểu đồ so sánh và cách đọc

### 5.1 Runtime chart
- Cột thấp hơn = nhanh hơn

### 5.2 Memory chart
- Cột thấp hơn = dùng RAM ít hơn

### 5.3 Error chart
- Cột thấp hơn = chính xác hơn

### Cách rút kết luận
- Nếu cần distinct chính xác với memory thấp -> HLL
- Nếu cần frequency item -> CMS
- Nếu cần sample đại diện -> Reservoir

---


## Bảng so sánh nhanh

| Thuật toán | Mục tiêu | Time/update | Memory | Ghi chú |
|---|---|---:|---:|---|
| Reservoir Sampling | Lấy mẫu ngẫu nhiên | $O(1)$ | $O(k)$ | Phụ thuộc chất lượng mẫu |
| Count-Min Sketch | Ước lượng tần suất | $O(d)$ | $O(d\cdot w)$ | Over-estimate do collision |
| HyperLogLog | Đếm distinct | $O(1)$ | $O(m)$ | Sai số nhỏ, ổn định |

---

## Cách chạy project

```bash
python run_experiment.py
```

Kết quả:
- In bảng benchmark (runtime, memory, error)
- Sinh 3 biểu đồ trong thư mục `plots/`: `runtime.png`, `memory.png`, `error.png`

---

## Cấu trúc project

```text
stream_bigdata/
├── data/
│   ├── data.csv
│   └── training.1600000.processed.noemoticon.csv
├── streaming_experiment/
│   ├── __init__.py
│   ├── benchmark.py
│   ├── count_min_sketch.py
│   ├── dataset_loader.py
│   ├── hyperloglog.py
│   ├── reservoir_sampling.py
│   └── visualize.py
├── requirements.txt
├── run_experiment.py
└── README.md
```
