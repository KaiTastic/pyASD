# pyASDReader GUI - 工具栏设计文档

## 概述

本文档详细说明了 pyASDReader GUI 应用程序主工具栏的设计和实现方案。工具栏将提供常用操作的快速访问，提升整体用户工作流程效率。

## 当前状态

应用程序目前已有：
- **菜单栏**：文件、导出、视图、帮助菜单
- **嵌入式控制栏**：
  - `MultiPlotControlBar` - 布局和同步控制（位于画布区域内）
  - `SubPlotControlBar` - 子图控制（单个图表控制）
  - `FileTreeControlBar` - 树操作（全选、清除、刷新、展开、折叠）
  - `SelectedFilesInfoBar` - 批量操作（对比、叠加、导出）
- **缺少主工具栏**，无法统一快速访问功能

## 设计目标

1. **可发现性**：通过可视化图标使功能易于发现
2. **效率**：减少常用操作的点击次数
3. **一致性**：遵循 Qt/PyQt6 工具栏最佳实践
4. **灵活性**：允许自定义和状态持久化
5. **可访问性**：支持键盘快捷键和工具提示
6. **专业性**：现代、简洁的外观，适合科学软件

## 工具栏架构

### 位置
- **位置**：MainWindow 顶部，菜单栏下方（默认）
- **可选位置**：底部、左侧、右侧（用户可配置）
- **可移动**：是，可以拖动到不同位置
- **可浮动**：是，可以分离为浮动窗口

### 结构

工具栏将组织为 **8 个逻辑区域**，用视觉分隔符分隔：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [文件] [视图] [绘图] [数据类型] [多文件] [同步] [显示] [设置]                │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 工具栏区域

### 1. 文件操作区域

**用途**：快速访问文件和文件夹操作

| 操作 | 图标 | 快捷键 | 描述 |
|------|------|--------|------|
| 打开文件 | 📂 | Ctrl+O | 打开单个 ASD 文件 |
| 打开文件夹 | 📁 | Ctrl+Shift+O | 浏览文件夹树 |
| 最近文件 | 📋 | - | 最近文件下拉列表（最多 10 个）|
| 快速导出 | 💾 | Ctrl+E | 下拉菜单：CSV/PNG/SVG/PDF |
| 关闭文件 | ✕ | Ctrl+W | 关闭当前文件 |

**实现说明**：
- 最近文件下拉列表使用 QMenu
- 快速导出显示格式选项子菜单
- 未加载文件时，操作被禁用

### 2. 视图与布局区域

**用途**：控制面板可见性和绘图布局

| 操作 | 图标 | 快捷键 | 描述 |
|------|------|--------|------|
| 布局选择器 | 🔲 | - | 下拉菜单：1×1, 1×2, 2×1, 2×2, 1×3, 3×1, 2×3 |
| 切换左侧面板 | ◀ | F9 | 显示/隐藏文件浏览器 |
| 切换右侧面板 | ▶ | F10 | 显示/隐藏属性面板 |
| 切换工具栏 | ⬍ | F11 | 显示/隐藏子图工具栏 |
| 全屏模式 | ⛶ | Alt+F11 | 最大化画布区域 |

**实现说明**：
- 布局选择器直接控制 `MultiPlotCanvas.set_layout_mode()`
- 面板切换使用 QSplitter 的 widget 可见性
- 状态保存在 QSettings 中

### 3. 绘图操作区域

**用途**：常用绘图操作

| 操作 | 图标 | 快捷键 | 描述 |
|------|------|--------|------|
| 刷新全部 | 🔄 | F5 | 重绘所有图表 |
| 清除全部 | 🗑️ | Ctrl+Delete | 清除所有子图 |
| 自动缩放 | 🔍 | Ctrl+0 | 重置缩放以适应数据 |
| 重置视图 | 🏠 | Home | 重置为默认视图 |
| 截图 | 📷 | Ctrl+Shift+S | 快速捕获到剪贴板 |

**实现说明**：
- 自动缩放对所有子图调用 `ax.autoscale()`
- 截图将当前视图复制到剪贴板
- 仅当存在图表时操作才启用

### 4. 数据类型选择器区域

**用途**：全局和定向数据类型切换

| 操作 | 图标 | 快捷键 | 描述 |
|------|------|--------|------|
| 数据类型下拉 | 📊 | - | 选择：DN、反射率、导数、Log(1/R) 等 |
| 应用到全部 | ⇒⇒ | Ctrl+Shift+A | 将选定类型应用到所有子图 |
| 应用到当前 | ⇒ | Ctrl+A | 应用到当前焦点子图 |

**实现说明**：
- 数据类型列表与 `SubPlotControlBar` 组合框匹配
- 应用到全部遍历所有子图
- 应用到当前仅针对焦点子图

### 5. 多文件操作区域

**用途**：对多个选定文件的操作

| 操作 | 图标 | 快捷键 | 描述 |
|------|------|--------|------|
| 对比 | ⚖️ | Ctrl+M | 并排加载选中的文件 |
| 叠加 | 📈 | Ctrl+Shift+M | 在一张图上绘制所有光谱 |
| 统计 | 📊 | Ctrl+T | 显示统计对比 |
| 批量导出 | 📦 | Ctrl+B | 导出多个文件 |

**实现说明**：
- 仅当选中 2 个以上文件时启用
- 对比触发自动布局选择
- 叠加打开 `OverlayPlotDialog`
- 批量导出打开 `BatchExportDialog`

### 6. 同步控制区域

**用途**：子图间的同步设置

| 操作 | 图标 | 快捷键 | 描述 |
|------|------|--------|------|
| 同步缩放 | 🔗 | - | 切换缩放同步 |
| 同步光标 | ➕ | - | 切换光标同步 |
| 同步平移 | ✋ | - | 切换平移同步 |
| 全部锁定 | 🔒 | Ctrl+L | 锁定所有子图交互 |

**实现说明**：
- 可选中的 QAction（切换按钮）
- 状态与 `MultiPlotControlBar` 同步
- 全部锁定禁用所有子图交互

### 7. 显示选项区域

**用途**：视觉显示偏好设置

| 操作 | 图标 | 快捷键 | 描述 |
|------|------|--------|------|
| 网格 | ⊞ | Ctrl+G | 切换所有图表上的网格 |
| 图例 | 📝 | Ctrl+Shift+L | 切换图例可见性 |
| 主题 | 🎨 | - | 下拉菜单：浅色/深色/系统 |
| 工具栏大小 | 📏 | - | 下拉菜单：小/中/大 |

**实现说明**：
- 网格/图例应用于所有当前和未来的图表
- 主题更改整个应用程序的外观
- 工具栏大小调整图标尺寸（16/24/32px）

### 8. 设置与帮助区域

**用途**：配置和帮助

| 操作 | 图标 | 快捷键 | 描述 |
|------|------|--------|------|
| 快速帮助 | ❓ | F1 | 显示键盘快捷键 |
| 设置 | ⚙️ | - | 打开首选项对话框 |
| 关于 | ℹ️ | - | 显示关于对话框 |

**实现说明**：
- 快速帮助显示包含快捷键参考的弹出窗口
- 设置对话框用于持久化首选项
- 关于重用现有对话框

## 实现方案

### 阶段 1：核心基础设施

**需要创建的文件**：

1. **`gui/widgets/main_toolbar.py`**
   - `MainToolBar` 类（继承 QToolBar）
   - 区域创建方法
   - 操作定义
   - 信号/槽连接

2. **`gui/utils/icon_manager.py`**
   - 图标资源管理
   - 主题支持（浅色/深色）
   - 图标不可用时的回退机制

3. **`gui/widgets/preferences_dialog.py`**
   - 设置配置 UI
   - 工具栏自定义选项

**需要修改的文件**：

1. **`gui/main_window.py`**
   - 在 `init_ui()` 中添加工具栏实例化
   - 连接工具栏信号到现有槽
   - 将工具栏添加到窗口布局

2. **`gui/widgets/multi_plot_canvas.py`**
   - 暴露工具栏操作的方法
   - 添加状态变化的信号发射

### 阶段 2：操作实现

**核心操作**：
```python
class MainToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("主工具栏", parent)
        self._create_file_section()
        self._create_view_section()
        self._create_plot_section()
        self._create_datatype_section()
        self._create_multifile_section()
        self._create_sync_section()
        self._create_display_section()
        self._create_settings_section()

    def _create_file_section(self):
        # 打开文件操作
        self.open_file_action = QAction(
            QIcon("icons/open_file.png"),
            "打开文件",
            self
        )
        self.open_file_action.setShortcut("Ctrl+O")
        self.open_file_action.setToolTip("打开 ASD 文件 (Ctrl+O)")
        self.open_file_action.setStatusTip("打开单个 ASD 文件")
        self.addAction(self.open_file_action)

        # ... 更多操作
        self.addSeparator()  # 区域分隔符
```

### 阶段 3：状态管理

**持久化设置**：
```python
# 保存工具栏状态
settings = QSettings("pyASDReader", "GUI")
settings.setValue("toolbar/position", self.toolbar.orientation())
settings.setValue("toolbar/visible", self.toolbar.isVisible())
settings.setValue("toolbar/icon_size", self.toolbar.iconSize())
settings.setValue("toolbar/movable", self.toolbar.isMovable())

# 恢复工具栏状态
orientation = settings.value("toolbar/position", Qt.Horizontal)
visible = settings.value("toolbar/visible", True, type=bool)
icon_size = settings.value("toolbar/icon_size", QSize(24, 24))
```

### 阶段 4：图标资源

**图标策略**：
1. **首选**：尽可能使用 Qt 标准图标
2. **次选**：包含自定义图标集（SVG 格式）
3. **回退**：使用 Unicode 字符/emoji 配合样式文本

**图标来源**：
- Qt 标准图标（`QStyle.StandardPixmap`）
- Material Design Icons
- Font Awesome（通过字体或 SVG）
- 专门操作的自定义 SVG 图标

**图标管理器示例**：
```python
class IconManager:
    @staticmethod
    def get_icon(name, theme="light"):
        # 尝试 Qt 标准图标
        if hasattr(QStyle.StandardPixmap, f"SP_{name}"):
            return qApp.style().standardIcon(
                getattr(QStyle.StandardPixmap, f"SP_{name}")
            )

        # 尝试自定义图标文件
        icon_path = f"gui/resources/icons/{theme}/{name}.svg"
        if os.path.exists(icon_path):
            return QIcon(icon_path)

        # 回退到文本
        return QIcon()
```

## 与现有代码的集成

### 连接到主窗口

```python
# 在 main_window.py 中
def init_ui(self):
    # ... 现有代码 ...

    # 创建工具栏
    self.main_toolbar = MainToolBar(self)
    self.addToolBar(Qt.TopToolBarArea, self.main_toolbar)

    # 连接信号
    self.main_toolbar.open_file_requested.connect(
        self.file_panel.open_file_dialog
    )
    self.main_toolbar.layout_changed.connect(
        self.multi_plot_canvas.set_layout_mode
    )
    self.main_toolbar.data_type_apply_all.connect(
        self._apply_data_type_to_all
    )
    # ... 更多连接 ...
```

### 与 MultiPlotCanvas 集成

```python
# MultiPlotCanvas 中的新方法
def apply_data_type_to_all(self, data_type: str):
    """将数据类型应用到所有子图"""
    for subplot in self.subplots:
        if subplot.current_file:
            subplot.load_data(subplot.current_file, data_type)

def toggle_grid_all(self, enabled: bool):
    """切换所有子图的网格"""
    for subplot in self.subplots:
        subplot.ax.grid(enabled)
        subplot.canvas.draw()
```

## 自定义功能

### 用户可配置选项

1. **工具栏可见性**：显示/隐藏整个工具栏
2. **区域可见性**：显示/隐藏单个区域
3. **图标大小**：小（16px）、中（24px）、大（32px）
4. **位置**：顶部、底部、左侧、右侧、浮动
5. **样式**：仅图标、仅文本、图标+文本
6. **主题**：浅色、深色、系统

### 首选项对话框

```
┌─ 工具栏首选项 ─────────────────────────┐
│                                        │
│ ☑ 显示工具栏                           │
│                                        │
│ 位置: [顶部 ▼]                         │
│ 图标大小: [中等 (24px) ▼]              │
│ 样式: [图标+文本 ▼]                    │
│ 主题: [系统 ▼]                         │
│                                        │
│ 可见区域:                              │
│ ☑ 文件操作                             │
│ ☑ 视图与布局                           │
│ ☑ 绘图操作                             │
│ ☑ 数据类型选择器                       │
│ ☑ 多文件操作                           │
│ ☑ 同步控制                             │
│ ☑ 显示选项                             │
│ ☑ 设置与帮助                           │
│                                        │
│        [恢复默认] [确定] [取消]        │
└────────────────────────────────────────┘
```

## 测试策略

### 单元测试
- 测试每个操作的启用/禁用逻辑
- 测试信号发射
- 测试状态持久化

### 集成测试
- 测试工具栏与主窗口的集成
- 测试实际文件操作的操作执行
- 测试布局模式切换

### 用户测试
- 验证键盘快捷键正确工作
- 验证工具提示正确显示
- 测试工具栏拖放/停靠行为
- 验证浅色/深色主题中的图标可见性

## 可访问性

### 键盘导航
- 所有操作都可通过键盘快捷键访问
- Tab 键在工具栏项目间导航
- Enter/空格键激活操作

### 屏幕阅读器
- 为屏幕阅读器提供适当的工具提示文本
- 状态栏集成的状态提示
- 所有操作的可访问名称

### 高对比度
- 图标设计在高对比度模式下工作
- 文本标签保持可见
- 焦点指示器清晰可见

## 未来增强

### 阶段 2 功能
1. **自定义操作构建器**：允许用户创建自定义工具栏按钮
2. **宏录制**：记录和重放操作序列
3. **手势支持**：触控/触控板手势操作
4. **上下文感知工具栏**：根据活动面板更改工具栏

### 高级功能
1. **插件支持**：允许插件添加工具栏项目
2. **工作区配置文件**：保存/加载工具栏配置
3. **快速命令面板**：Ctrl+P 风格命令搜索
4. **工具栏组**：为不同工作流创建多个工具栏

## 设计参考

### 类似应用程序的灵感
- **QGIS**：具有清晰区域的模块化工具栏
- **MATLAB**：数据类型选择器和绘图控制
- **OriginPro**：科学绘图工具栏设计
- **ImageJ**：多窗口协调工具

### Qt 最佳实践
- 对所有工具栏项目使用 QAction
- 为互斥操作实现 QActionGroup
- 使用 QToolButton 进行下拉菜单
- 遵循 Qt 样式指南进行图标设计

## 总结

此工具栏设计提供：
- **快速访问**：一键访问 40 多个常用操作
- **视觉清晰**：带有工具提示和键盘快捷键的图标
- **灵活性**：可自定义位置、大小和可见性
- **集成**：与现有 UI 组件无缝集成
- **可扩展性**：易于添加新操作和区域

该实现遵循 PyQt6 最佳实践，并与现有代码库架构保持一致。

## 附录：快捷键参考表

### 文件操作
- `Ctrl+O` - 打开文件
- `Ctrl+Shift+O` - 打开文件夹
- `Ctrl+E` - 快速导出
- `Ctrl+W` - 关闭文件
- `Ctrl+Q` - 退出应用

### 视图控制
- `F9` - 切换左侧面板
- `F10` - 切换右侧面板
- `F11` - 切换子图工具栏
- `Alt+F11` - 全屏模式

### 绘图操作
- `F5` - 刷新全部
- `Ctrl+Delete` - 清除全部
- `Ctrl+0` - 自动缩放
- `Home` - 重置视图
- `Ctrl+Shift+S` - 截图

### 数据类型
- `Ctrl+A` - 应用到当前
- `Ctrl+Shift+A` - 应用到全部

### 多文件操作
- `Ctrl+M` - 对比模式
- `Ctrl+Shift+M` - 叠加模式
- `Ctrl+T` - 统计视图
- `Ctrl+B` - 批量导出

### 同步控制
- `Ctrl+L` - 全部锁定/解锁

### 显示选项
- `Ctrl+G` - 切换网格
- `Ctrl+Shift+L` - 切换图例

### 帮助
- `F1` - 快速帮助
