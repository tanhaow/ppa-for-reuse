# 多 Adapter 系统 - 快速参考指南

## 🚀 快速开始

### 5 分钟配置指南

#### 1. 为 Collection 设置 Adapter

```python
from ppa.archive.models import Collection

collection = Collection.objects.get(name='Your Collection')
collection.adapter_name = 'cookbook'  # 或 'scifi', 'feeding_america'
collection.save()
```

#### 2. 配置列表视图字段（可选）

**方法 A: 使用 Django Admin（推荐）**
```
1. 访问: http://localhost:8000/admin/archive/collection/
2. 编辑 collection
3. 在 "List View Fields" 中输入:
   [
     {"field": "cookbook_cook_time", "label": "Cook Time"},
     {"field": "cookbook_ingredients", "label": "Ingredients"}
   ]
4. 保存
```

**方法 B: 使用 Python**
```python
collection.list_view_fields = [
    {'field': 'cookbook_cook_time', 'label': 'Cook Time'},
    {'field': 'cookbook_ingredients', 'label': 'Ingredients'}
]
collection.save()
```

#### 3. 查看效果

```
访问: http://localhost:8000/archive/?collections=Your+Collection
```

---

## 📋 常用命令

### Collection 管理

```python
from ppa.archive.models import Collection

# 查看所有 collections
Collection.objects.all()

# 查看有 adapter 的 collections
Collection.objects.exclude(adapter_name='')

# 查看特定 adapter 的 collections
Collection.objects.filter(adapter_name='cookbook')

# 批量设置 adapter
Collection.objects.filter(
    name__startswith='Science Fiction'
).update(adapter_name='scifi')

# 复制字段配置
source = Collection.objects.get(name='Source Collection')
target = Collection.objects.get(name='Target Collection')
target.list_view_fields = source.list_view_fields
target.save()
```

### Adapter 操作

```python
from ppa.adapters.loader import get_adapter, get_adapters_for_work

# 加载 adapter
adapter = get_adapter('cookbook')
print(f"Name: {adapter.name}")
print(f"Fields: {list(adapter.field_map.keys())}")

# 获取 work 的 adapters
from ppa.archive.models import DigitizedWork
work = DigitizedWork.objects.first()
adapters = get_adapters_for_work(work)
print(f"Adapters: {[a.name for a in adapters]}")
```

### 验证配置

```python
from django.core.exceptions import ValidationError

collection = Collection.objects.first()
collection.adapter_name = 'cookbook'
collection.list_view_fields = [
    {'field': 'cookbook_cook_time', 'label': 'Cook Time'}
]

try:
    collection.full_clean()  # 验证
    collection.save()
    print("✓ Configuration valid")
except ValidationError as e:
    print(f"✗ Validation error: {e}")
```

---

## 🎯 常见任务

### 任务 1: 为新 Collection 配置 Adapter

```python
# 1. 创建或获取 collection
collection = Collection.objects.get(name='My New Collection')

# 2. 设置 adapter
collection.adapter_name = 'cookbook'

# 3. 使用默认字段（推荐）
# 不设置 list_view_fields，系统会使用 adapter 默认配置

# 4. 或配置自定义字段
collection.list_view_fields = [
    {'field': 'cookbook_cook_time', 'label': 'Cooking Time'},
    {'field': 'cookbook_ingredients', 'label': 'Main Ingredients'}
]

# 5. 保存
collection.save()
```

### 任务 2: 批量配置多个 Collections

```python
# 获取所有 sci-fi collections
scifi_collections = Collection.objects.filter(
    name__startswith='Science Fiction'
)

# 批量设置 adapter
scifi_collections.update(adapter_name='scifi')

# 为每个设置相同的字段配置
fields_config = [
    {'field': 'scifi_subgenre', 'label': 'Subgenre'},
    {'field': 'scifi_rating_score', 'label': 'Rating'}
]

for collection in scifi_collections:
    collection.list_view_fields = fields_config
    collection.save()

print(f"✓ Configured {scifi_collections.count()} collections")
```

### 任务 3: 预览字段配置

```python
from ppa.adapters.loader import get_adapter

collection = Collection.objects.get(name='Your Collection')

# 获取 adapter
adapter = get_adapter(collection.adapter_name)

# 获取字段配置
if collection.list_view_fields:
    fields = collection.list_view_fields
    print("Using custom fields:")
else:
    fields = adapter.display_fields.get('list_view', [])
    print("Using adapter defaults:")

# 显示字段
for i, field in enumerate(fields, 1):
    print(f"  {i}. {field['label']}: {field['field']}")
```

### 任务 4: 验证所有 Collections

```python
from django.core.exceptions import ValidationError

collections = Collection.objects.exclude(adapter_name='')
errors = []

for collection in collections:
    try:
        collection.full_clean()
    except ValidationError as e:
        errors.append({
            'collection': collection.name,
            'errors': e.message_dict
        })

if errors:
    print(f"✗ Found {len(errors)} collections with errors:")
    for error in errors:
        print(f"  - {error['collection']}: {error['errors']}")
else:
    print(f"✓ All {collections.count()} collections are valid")
```

---

## 🔧 Django Admin 操作

### 单个 Collection 配置

```
1. 访问: http://localhost:8000/admin/archive/collection/
2. 点击 collection 名称
3. 设置字段:
   - Adapter Name: cookbook
   - List View Fields: [JSON 配置]
4. 点击 "Save"
```

### 批量设置 Adapter

```
1. 在 Collection 列表中勾选多个 collections
2. Actions 下拉菜单 → "Set adapter for selected collections"
3. 点击 "Go"
4. 选择 adapter (cookbook, scifi, feeding_america)
5. 点击 "Apply"
```

### 批量复制字段配置

```
1. 勾选目标 collections（要复制到的）
2. Actions → "Copy field configuration to selected collections"
3. 点击 "Go"
4. 选择源 collection（从哪里复制）
5. 点击 "Copy Configuration"
```

### 预览字段配置

```
1. 勾选要预览的 collections
2. Actions → "Preview field configuration"
3. 点击 "Go"
4. 查看详细预览
```

---

## 📝 字段配置格式

### 基本格式

```json
[
  {
    "field": "adapter_field_name",
    "label": "Display Label"
  }
]
```

### 完整格式（带可选参数）

```json
[
  {
    "field": "cookbook_ingredients",
    "label": "Ingredients",
    "separator": " • "
  }
]
```

### 示例配置

**Cookbook:**
```json
[
  {"field": "cookbook_cook_time", "label": "Cook Time"},
  {"field": "cookbook_ingredients", "label": "Ingredients"}
]
```

**Sci-Fi:**
```json
[
  {"field": "scifi_subgenre", "label": "Subgenre"},
  {"field": "scifi_rating_score", "label": "Rating"},
  {"field": "scifi_genres", "label": "Genres"}
]
```

**Feeding America:**
```json
[
  {"field": "feeding_america_source_info", "label": "Source"},
  {"field": "feeding_america_dataset", "label": "Dataset"}
]
```

---

## ⚠️ 常见错误

### 错误 1: "Must be a JSON array (list)"

**原因:** 配置不是数组格式

**错误示例:**
```json
{"field": "cookbook_cook_time", "label": "Cook Time"}
```

**正确示例:**
```json
[
  {"field": "cookbook_cook_time", "label": "Cook Time"}
]
```

### 错误 2: "Missing required property 'field'"

**原因:** 缺少必需的 field 属性

**错误示例:**
```json
[
  {"label": "Cook Time"}
]
```

**正确示例:**
```json
[
  {"field": "cookbook_cook_time", "label": "Cook Time"}
]
```

### 错误 3: "Field should start with adapter prefix"

**原因:** 字段名缺少 adapter 前缀

**错误示例:**
```json
[
  {"field": "cook_time", "label": "Cook Time"}
]
```

**正确示例:**
```json
[
  {"field": "cookbook_cook_time", "label": "Cook Time"}
]
```

**例外:** 通用字段不需要前缀
```json
[
  {"field": "title", "label": "Title"},
  {"field": "author", "label": "Author"}
]
```

---

## 🎨 可用字段列表

### Cookbook Adapter

```
cookbook_cook_time       - 烹饪时间
cookbook_ingredients     - 食材列表
```

### Sci-Fi Adapter

```
scifi_subgenre          - 科幻子类型
scifi_rating_score      - 评分
scifi_rating_votes      - 评分人数
scifi_genres            - 类型列表
scifi_description       - 描述
scifi_goodreads_url     - Goodreads 链接
```

### Feeding America Adapter

```
feeding_america_source_info    - 来源信息
feeding_america_dataset        - 数据集名称
feeding_america_recipes        - 食谱信息
```

### 通用字段（所有 Adapters）

```
title                   - 标题
author                  - 作者
pub_date                - 出版日期
pub_place               - 出版地点
publisher               - 出版商
```

---

## 🔍 调试技巧

### 检查 Adapter 配置

```python
from ppa.adapters.loader import get_adapter

adapter = get_adapter('cookbook')
print(f"Name: {adapter.name}")
print(f"Display Name: {adapter.display_name}")
print(f"Fields: {list(adapter.field_map.keys())}")
print(f"List View Fields: {adapter.display_fields.get('list_view')}")
```

### 检查 Collection 配置

```python
collection = Collection.objects.get(name='Your Collection')
print(f"Name: {collection.name}")
print(f"Adapter: {collection.adapter_name}")
print(f"Custom Fields: {collection.list_view_fields}")
print(f"Works Count: {collection.digitizedwork_set.count()}")
```

### 检查 Work 的 Adapters

```python
from ppa.archive.models import DigitizedWork
from ppa.adapters.loader import get_adapters_for_work

work = DigitizedWork.objects.get(source_id='cookbook_001')
print(f"Title: {work.title}")
print(f"Collections: {[c.name for c in work.collections.all()]}")

adapters = get_adapters_for_work(work)
print(f"Adapters: {[a.name for a in adapters]}")

# 检查索引数据
from ppa.solr_factory import map_model_to_solr
index_data = map_model_to_solr(work)
print(f"Indexed Fields: {list(index_data.keys())}")
```

### 检查 Solr 索引

```bash
# 检查特定 work 的索引数据
curl "http://localhost:8983/solr/ppa/select?q=source_id:cookbook_001&fl=*"

# 检查字段是否存在
curl "http://localhost:8983/solr/ppa/schema/fields/cookbook_cook_time"

# 统计有特定字段的文档数量
curl "http://localhost:8983/solr/ppa/select?q=cookbook_cook_time:*&rows=0"
```

---

## 📊 系统状态检查

### 快速状态检查

```python
from ppa.archive.models import Collection, DigitizedWork
from ppa.adapters.loader import get_adapter

print("=== System Status ===")
print(f"Total Collections: {Collection.objects.count()}")
print(f"With Adapters: {Collection.objects.exclude(adapter_name='').count()}")
print(f"With Custom Fields: {Collection.objects.exclude(list_view_fields__isnull=True).count()}")
print(f"Total Works: {DigitizedWork.objects.count()}")

print("\n=== Adapters ===")
for name in ['cookbook', 'scifi', 'feeding_america']:
    adapter = get_adapter(name)
    if adapter:
        print(f"{name}: {len(adapter.field_map)} fields")

print("\n=== Collections by Adapter ===")
for name in ['cookbook', 'scifi', 'feeding_america', '']:
    count = Collection.objects.filter(adapter_name=name).count()
    label = name if name else '(none)'
    print(f"{label}: {count} collections")
```

---

## 🆘 获取帮助

### 文档

- [创建和使用 Adapters](creating-adapters.md)
- [配置列表视图字段](configuring-list-view-fields.md)
- [高级 Admin 功能](advanced-admin-features.md)
- [完整实施报告](../MULTI_ADAPTER_IMPLEMENTATION_REPORT.md)

### 常见问题

**Q: 列表视图不显示字段？**
A: 检查：1) Collection 有 adapter_name，2) 只选择了一个 collection，3) Solr 已索引数据

**Q: 如何重新索引数据？**
A: 运行 `python manage.py index --index work`

**Q: 如何查看可用的字段？**
A: 查看 adapter.yaml 文件中的 field_map 部分

**Q: 可以同时使用多个 adapters 吗？**
A: 可以！每个 collection 可以有自己的 adapter

**Q: 如何批量配置多个 collections？**
A: 使用 Django Admin 的批量操作功能

---

**最后更新:** 2026年3月11日
**版本:** 1.0.0
