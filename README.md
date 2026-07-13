# Irvine Atlas · 尔湾生活全攻略

可扩展的尔湾生活地点数据库、响应式网页前端与公开活动聚合器。适合 UCI 学生、新居民和短期访客。

## 已实现

- 8 个核心生活区域，首批精选地点数据
- 地点中文/英文双语描述、标签、区域和类别筛选
- SQLite 持久化收藏
- 近期活动页面与可插拔抓取器架构
- FastAPI JSON API
- 手机/桌面响应式界面
- Windows 一键启动，端口冲突时自动递增

## 快速开始

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python start.py
```

Windows 也可双击 `start.bat`。

## 更新活动

```bash
python scrapers/update_events.py
```

抓取器只访问公开页面，不绕过登录、验证码或访问限制。网站结构变化时，应在 `scrapers/feeds.py` 中增加专用适配器。生产环境建议通过 GitHub Actions 定时执行，并将结果写入 JSON 或托管数据库。

## 数据扩展

地点初始数据位于 `data/places.json`。字段包括：`id`、中英文名称、区域、类别、地址、坐标、预算等级、标签、双语描述、官网、来源和更新时间。

## API

- `GET /api/places`
- `GET /api/events`
- `GET /api/meta`
- `POST /api/favorites`
- `DELETE /api/favorites/{item_type}/{item_id}`

## 后续路线

地图视图、用户自定义地点、照片、路线时间、停车信息、营业时间、活动去重、RSS/iCal/API 专用适配器和云端账户同步。
