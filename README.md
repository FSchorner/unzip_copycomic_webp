# unzip_copycomic_webp

这是一个用于从 `book.size` + `book.copy` 还原 WebP 图片的 Python 脚本。

它适用于以下情形：

- `book.size` 中保存了每张图片的长度
- `book.copy` 是多个 WebP 文件按顺序拼接在一起的二进制文件
- 需要把它们拆分并还原为独立的 `.webp` 文件

---

## 功能说明

脚本会自动：

1. 读取同目录下的 `book.size`
2. 解析每张图片的大小
3. 读取 `book.copy` 中对应长度的数据
4. 校验 RIFF / WEBP 头部
5. 将每张图片保存到 `extracted/` 目录中

输出示例：

```text
extracted/
├── 0001.webp
├── 0002.webp
├── 0003.webp
└── ...
```

---

## 目录结构

```text
unzip_copycomic_webp/
├── unzip_webp.py
├── book.size
├── book.copy
├── extracted/
│   ├── 0001.webp
│   ├── 0002.webp
│   └── ...
└── README.md
```

---

## 运行方式

### 方法 1：双击运行

在 Windows 下，直接双击 `unzip_webp.py` 即可。

### 方法 2：命令行运行

```bash
python unzip_webp.py
```

如果你在某些环境下使用的是 Python 3：

```bash
python3 unzip_webp.py
```

---

## `book.size` 格式

`book.size` 的内容通常类似：

```text
856070#copy#102670#copy#120582#copy#...
```

也就是：

- 每个数字表示一张图片的大小（字节）
- `#copy#` 是分隔符
- 数字之间不能有多余空格或非数字字符

例如：

```text
1000#copy#2000#copy#1500
```

表示 3 张图片，大小分别为：

- 1000 bytes
- 2000 bytes
- 1500 bytes

---

## `book.copy` 格式

`book.copy` 是多个 WebP 文件按顺序拼接后的二进制文件。

脚本会：

- 先检查 `book.size` 中的总大小是否和 `book.copy` 的真实大小一致
- 再按每个大小读取数据
- 验证每段数据是否为有效的 RIFF / WEBP 文件

如果校验失败，脚本会直接报错并提示具体偏移位置。

---

## 输出说明

提取成功后，图片会保存在当前目录下的 `extracted` 文件夹中，文件名按顺序命名：

```text
0001.webp
0002.webp
0003.webp
```

---

## 兼容性

- 适用于 Windows
- 兼容 Python 3.12
- 自动尝试读取 UTF-8 / GB18030 编码的 `book.size`

---

## 常见问题

### 1. 报错：找不到 `book.size` 或 `book.copy`

请确认：

- 脚本和这两个文件位于同一目录
- 文件名拼写正确
- 没有误改扩展名

### 2. 报错：size 总和 != book.copy 文件大小

通常说明：

- `book.size` 和 `book.copy` 不是同一份数据
- 文件损坏或截断
- 分隔符格式错误

### 3. 报错：第 X 页不是 RIFF 文件

这通常表示：

- `book.copy` 并不是按标准格式拼接
- 某一段数据被破坏
- `book.size` 对应的长度不正确

---

## 声明

本脚本仅用于从本地文件中还原已知数据结构的图片，不涉及网络下载、加密破解或非法内容处理。

---

## 许可证

本项目未附带特别许可协议，默认按实际使用场景自行保留所有权利。
