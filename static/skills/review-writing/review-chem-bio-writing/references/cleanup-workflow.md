# 综述终稿清理工作流

交付前必须执行以下清洗步骤：

## 1. 机械清洗（用Python脚本执行）

```python
import re

with open('draft.md', 'r', encoding='utf-8') as f:
    t = f.read()

# 清除C/E/L/T行首标记
t = re.sub(r'^[CLT][：:]\s*', '', t, flags=re.MULTILINE)
# 清除加粗C/E/L/T全段
t = re.sub(r'\*\*[CLT][：:].*?\*\*', '', t)
# 清除剩余孤立C/L/T字符
t = re.sub(r'(?<=\s)[CLT][：:](?=\s)', '', t)
# 清除"关键观察""数据来源""解读"
for p in ['关键观察', '数据来源', '解读', '*注：']:
    t = t.replace(p, '')
# 清除AI填充词
for p in ['需要指出的是', '值得注意的是', '不可忽视的是', '毋庸置疑']:
    t = t.replace(p, '')
# 压缩空行
t = re.sub(r'\n{4,}', '\n\n\n', t)
# 清除行末空格
t = re.sub(r' +\n', '\n', t)
# 消除双空格
t = re.sub(r'  +', ' ', t)

with open('draft_clean.md', 'w', encoding='utf-8') as f:
    f.write(t)
```

## 2. 验证清单

- [ ] 无 `**C：**` `**L：**` `**T：**` 残留
- [ ] 无 `^C：` `^L：` `^T：` 行首标记
- [ ] 无 `(C：` `C：` 等孤立字符
- [ ] 无 "值得注意的是""需要指出的是"等填充词
- [ ] 无 "图X-X建议"等制作笔记
- [ ] 所有引用格式统一为 (Author, Year, *Journal*, DOI:)
- [ ] 输出为纯md文件，不编译PDF
