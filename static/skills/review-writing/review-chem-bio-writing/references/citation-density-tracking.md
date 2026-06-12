# 引用密度量化追踪脚本

## 用途

每次综述扩张后运行，识别低密度节（引用偏少、文字偏多），指导下轮迭代方向。

## 追踪指标

| 指标 | 大综述目标 | 巨型综述目标 |
|------|:---------:|:-----------:|
| 字/cite | ≤120 | ≤250 |
| 每节最少引用 | ≥20 | ≥40 |
| 语料库利用率 | ≥30% | ≥50% |

## 快捷追踪命令

```bash
cd /opt/data/reviews/<project>/
python3 -c "
import re, glob
u=set()
for f in sorted(glob.glob('sections/*.md')):
 if '00-outline' in f: continue
 with open(f) as c: c=c.read()
 n=len(set(re.findall(r'10\.\d{4,}/[^\s\)\]]+',c)))
 u.update(re.findall(r'10\.\d{4,}/[^\s\)\]]+',c))
 cn=len(re.findall(r'[\u4e00-\u9fff]',c))
 print(f'{f.split(\"/\")[-1][:35]:<35} {cn:>5}字 {n:>3}cite ({cn//max(n,1):>3}字/cite)')
print(f'\n总计：{sum(1 for _ in open(\"data/final_corpus.json\"))}篇语料')
"
```

## 判断逻辑

```
字/cite > 120（大综述）或 > 250（巨型） → 文字偏多引用偏少
  下轮只加证据段落，不扩展叙述
字/cite < 60（大综述）或 < 120（巨型） → 引用密度已达标
  可以开始加叙述深度

单节引用 < 20（大综述）或 < 40（巨型） → 后腿节
  优先从 corpus 检索该节主题下高引未引论文注入
```

## DOI 匹配注意事项

Corpus 中的 DOI 格式为 `https://doi.org/10.XXXX/XXXXXX`（带前缀）。
正文中提取的 DOI 格式为 `10.XXXX/XXXXXX`（无前缀）。
在写 automated check 脚本时记得做归一化处理：

```python
def normalize(d):
    d = d.strip().lower()
    for prefix in ['https://doi.org/', 'http://doi.org/', 'doi.org/', 'doi:']:
        if d.startswith(prefix): d = d[len(prefix):]
    return d
```
