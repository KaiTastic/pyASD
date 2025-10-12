# pyASDReader GUI 图形界面

用于查看和分析 ASD 光谱文件的图形用户界面。

## 主要功能

- **文件管理**
  - 打开单个 ASD 文件或浏览文件夹
  - 最近文件列表快速访问
  - 支持拖放（即将推出）

- **数据可视化**
  - 使用 matplotlib 的交互式光谱图
  - 支持多种数据类型：
    - 数字量 (DN)
    - 反射率（含一阶、二阶、三阶导数）
    - 白参考
    - 绝对反射率
    - Log(1/R)（含导数）
    - 辐射率（如果可用）
  - 缩放、平移等 matplotlib 工具
  - 可自定义网格和图例

- **元数据显示**
  - 完整的文件信息
  - 仪器详情
  - GPS 数据（如果可用）
  - 光谱参数
  - 可用数据类型

- **导出功能**
  - 导出数据为 CSV（可选择特定数据类型）
  - 导出元数据为文本文件
  - 导出图表为 PNG、SVG 或 PDF

## 安装

### 安装 GUI 依赖

```bash
# 安装 GUI 依赖
pip install -e ".[gui]"

# 或安装所有依赖
pip install -e ".[all]"
```

### 依赖项

- PyQt6 >= 6.4.0
- matplotlib >= 3.5.0
- numpy >= 1.20.0（基础包已要求）

## 使用方法

### 启动 GUI

```bash
# 从项目根目录
python main.py

# 或者指定要打开的文件
python main.py path/to/file.asd
```

### 使用界面

1. **打开文件**
   - 点击 "Open File..." 按钮或使用文件菜单 (Ctrl+O)
   - 或打开文件夹浏览多个文件 (Ctrl+Shift+O)

2. **查看数据**
   - 从下拉菜单选择数据类型
   - 图表自动更新
   - 使用 matplotlib 工具栏进行缩放/平移

3. **查看元数据**
   - 文件信息显示在左侧面板
   - 根据需要展开/折叠各部分

4. **导出数据**
   - 使用导出菜单保存数据或图表
   - 为 CSV 导出选择特定数据类型
   - 以各种格式导出图表

### 快捷键

- `Ctrl+O` - 打开文件
- `Ctrl+Shift+O` - 打开文件夹
- `Ctrl+W` - 关闭当前文件
- `Ctrl+Q` - 退出应用程序
- `F5` - 刷新图表

## 项目结构

```
gui/
├── __init__.py              # GUI 模块初始化
├── main_window.py           # 主应用程序窗口
├── widgets/                 # 自定义组件
│   ├── __init__.py
│   ├── plot_widget.py       # 光谱图组件
│   ├── metadata_widget.py   # 元数据显示组件
│   └── file_panel.py        # 文件管理面板
└── utils/                   # 工具模块
    ├── __init__.py
    └── export_utils.py      # 导出功能

main.py                      # 应用程序入口点
```

## 支持的文件版本

GUI 支持 pyASDReader 库支持的所有 ASD 文件版本（v1-v8）。

## 故障排除

### GUI 无法启动

- 确保已安装 PyQt6：`pip install PyQt6`
- 检查 Python 版本 >= 3.8

### 图表不显示

- 确保已安装 matplotlib：`pip install matplotlib`
- 尝试刷新图表 (F5)

### 数据类型显示"不可用"

- 某些数据类型需要特定文件版本
- 查看元数据了解文件版本
- 反射率需要参考数据 (v2+)
- 绝对反射率需要校准数据 (v7+)

## 开发

### 添加新功能

GUI 设计为模块化和可扩展的：

- **新图表类型**：添加到 `PlotWidget.PLOT_TYPES` 字典
- **新导出格式**：扩展 `ExportManager` 类
- **新组件**：在 `gui/widgets/` 目录创建

### 测试

```bash
# 测试导入
python -c "from gui.widgets import PlotWidget, MetadataWidget, FilePanel"

# 语法检查
python -m py_compile gui/**/*.py
```

## 许可证

与 pyASDReader 库相同（MIT 许可证）

## 致谢

基于 Kai Cao 的 pyASDReader 库构建。
