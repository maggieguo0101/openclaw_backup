#!/usr/bin/env python3
"""
微信公众号草稿箱工具
功能：获取 access_token、上传封面图片、新增草稿
用法：
    # 新增草稿（纯文字，无封面）
    python3 wechat_draft.py add --title "文章标题" --content "<p>正文HTML</p>" --author "作者"

    # 新增草稿（带封面图片）
    python3 wechat_draft.py add --title "文章标题" --content "<p>正文HTML</p>" --cover /path/to/cover.jpg

    # 查看草稿列表
    python3 wechat_draft.py list

配置：在 wechat_config.json 中填写 appid 和 appsecret
"""

import json
import os
import sys
import argparse
import requests
import time
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).parent
CONFIG_FILE = WORKSPACE / "wechat_config.json"
TOKEN_CACHE_FILE = WORKSPACE / ".wechat_token_cache.json"

BASE_URL = "https://api.weixin.qq.com"


def load_config() -> dict:
    """加载公众号配置"""
    if not CONFIG_FILE.exists():
        default = {"appid": "", "appsecret": ""}
        CONFIG_FILE.write_text(json.dumps(default, indent=2, ensure_ascii=False))
        print(f"❌ 请先填写配置文件：{CONFIG_FILE}")
        print("   需要填入：appid 和 appsecret")
        sys.exit(1)
    cfg = json.loads(CONFIG_FILE.read_text())
    if not cfg.get("appid") or not cfg.get("appsecret"):
        print(f"❌ 配置不完整，请填写 {CONFIG_FILE} 中的 appid 和 appsecret")
        sys.exit(1)
    return cfg


def get_access_token(appid: str, appsecret: str) -> str:
    """获取 access_token，优先用缓存（有效期2小时）"""
    # 检查缓存
    if TOKEN_CACHE_FILE.exists():
        cache = json.loads(TOKEN_CACHE_FILE.read_text())
        if cache.get("expires_at", 0) > time.time() + 300:  # 提前5分钟刷新
            return cache["access_token"]

    # 重新获取
    url = f"{BASE_URL}/cgi-bin/token"
    resp = requests.get(url, params={
        "grant_type": "client_credential",
        "appid": appid,
        "secret": appsecret,
    }, timeout=10)
    data = resp.json()
    if "errcode" in data and data["errcode"] != 0:
        print(f"❌ 获取 access_token 失败：{data}")
        sys.exit(1)

    token = data["access_token"]
    expires_in = data.get("expires_in", 7200)
    cache = {"access_token": token, "expires_at": time.time() + expires_in}
    TOKEN_CACHE_FILE.write_text(json.dumps(cache))
    print(f"✅ access_token 已更新，有效期 {expires_in//60} 分钟")
    return token


def upload_image(token: str, image_path: str) -> str:
    """上传永久素材（封面图），返回 media_id"""
    url = f"{BASE_URL}/cgi-bin/material/add_material"
    path = Path(image_path)
    if not path.exists():
        print(f"❌ 图片文件不存在：{image_path}")
        sys.exit(1)

    # 判断类型
    suffix = path.suffix.lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}
    mime = mime_map.get(suffix, "image/jpeg")

    with open(path, "rb") as f:
        resp = requests.post(
            url,
            params={"access_token": token, "type": "image"},
            files={"media": (path.name, f, mime)},
            timeout=30,
        )
    data = resp.json()
    if "media_id" not in data:
        print(f"❌ 上传封面图失败：{data}")
        sys.exit(1)
    print(f"✅ 封面图上传成功，media_id：{data['media_id']}")
    return data["media_id"]


def upload_content_image(token: str, image_path: str) -> str:
    """上传正文内图片，返回可用 URL（临时素材接口）"""
    url = f"{BASE_URL}/cgi-bin/media/uploadimg"
    path = Path(image_path)
    with open(path, "rb") as f:
        resp = requests.post(
            url,
            params={"access_token": token},
            files={"media": (path.name, f, "image/jpeg")},
            timeout=30,
        )
    data = resp.json()
    if "url" not in data:
        print(f"❌ 上传正文图片失败：{data}")
        sys.exit(1)
    return data["url"]


def add_draft(token: str, title: str, content: str,
              author: str = "", digest: str = "",
              thumb_media_id: str = "",
              content_source_url: str = "",
              need_open_comment: int = 0) -> str:
    """新增草稿，返回 media_id"""
    url = f"{BASE_URL}/cgi-bin/draft/add"

    article = {
        "title": title,
        "content": content,
        "author": author,
        "digest": digest,
        "content_source_url": content_source_url,
        "need_open_comment": need_open_comment,
    }
    if thumb_media_id:
        article["thumb_media_id"] = thumb_media_id

    payload = {"articles": [article]}
    resp = requests.post(
        url,
        params={"access_token": token},
        json=payload,
        timeout=30,
    )
    data = resp.json()
    if "media_id" not in data:
        print(f"❌ 新增草稿失败：{data}")
        sys.exit(1)
    return data["media_id"]


def list_drafts(token: str, offset: int = 0, count: int = 10) -> None:
    """获取草稿列表"""
    url = f"{BASE_URL}/cgi-bin/draft/batchget"
    resp = requests.post(
        url,
        params={"access_token": token},
        json={"offset": offset, "count": count, "no_content": 1},
        timeout=10,
    )
    data = resp.json()
    if "item" not in data:
        print(f"草稿箱为空或出错：{data}")
        return
    print(f"\n共 {data.get('total_count', '?')} 篇草稿，显示前 {count} 篇：\n")
    for item in data["item"]:
        content = item.get("content", {})
        articles = content.get("news_item", [{}])
        first = articles[0] if articles else {}
        print(f"  📄 {first.get('title', '无标题')}")
        print(f"     media_id: {item.get('media_id')}")
        update_time = item.get("update_time", 0)
        if update_time:
            import datetime
            dt = datetime.datetime.fromtimestamp(update_time)
            print(f"     更新时间: {dt.strftime('%Y-%m-%d %H:%M')}")
        print()


def publish_draft(token: str, media_id: str) -> None:
    """发布草稿（提交发布，注意：不会推送通知给粉丝）"""
    url = f"{BASE_URL}/cgi-bin/freepublish/submit"
    resp = requests.post(
        url,
        params={"access_token": token},
        json={"media_id": media_id},
        timeout=10,
    )
    data = resp.json()
    if data.get("errcode", 0) == 0:
        print(f"✅ 发布成功！publish_id：{data.get('publish_id')}")
    else:
        print(f"❌ 发布失败：{data}")


# ── CLI ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="微信公众号草稿箱工具")
    sub = parser.add_subparsers(dest="cmd")

    # add 子命令
    p_add = sub.add_parser("add", help="新增草稿")
    p_add.add_argument("--title", required=True, help="文章标题")
    p_add.add_argument("--content", help="正文 HTML（或用 --content-file 指定文件）")
    p_add.add_argument("--content-file", help="从文件读取正文 HTML")
    p_add.add_argument("--author", default="", help="作者名")
    p_add.add_argument("--digest", default="", help="摘要（不填自动截取前54字）")
    p_add.add_argument("--cover", help="封面图片路径（本地文件）")
    p_add.add_argument("--source-url", default="", help="阅读原文链接")
    p_add.add_argument("--open-comment", action="store_true", help="开启评论")

    # list 子命令
    p_list = sub.add_parser("list", help="查看草稿列表")
    p_list.add_argument("--count", type=int, default=10, help="显示数量")

    # publish 子命令
    p_pub = sub.add_parser("publish", help="发布草稿（不推送通知）")
    p_pub.add_argument("--media-id", required=True, help="草稿 media_id")

    # token 子命令
    sub.add_parser("token", help="刷新并显示 access_token")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    cfg = load_config()
    token = get_access_token(cfg["appid"], cfg["appsecret"])

    if args.cmd == "token":
        print(f"access_token: {token}")

    elif args.cmd == "list":
        list_drafts(token, count=args.count)

    elif args.cmd == "publish":
        publish_draft(token, args.media_id)

    elif args.cmd == "add":
        # 读取正文
        if args.content_file:
            content = Path(args.content_file).read_text(encoding="utf-8")
        elif args.content:
            content = args.content
        else:
            print("❌ 请通过 --content 或 --content-file 提供正文")
            sys.exit(1)

        # 上传封面
        thumb_media_id = ""
        if args.cover:
            thumb_media_id = upload_image(token, args.cover)

        # 新增草稿
        media_id = add_draft(
            token=token,
            title=args.title,
            content=content,
            author=args.author,
            digest=args.digest,
            thumb_media_id=thumb_media_id,
            content_source_url=args.source_url,
            need_open_comment=1 if args.open_comment else 0,
        )
        print(f"\n✅ 草稿已保存到草稿箱！")
        print(f"   media_id：{media_id}")
        print(f"   标题：{args.title}")
        print(f"\n💡 在公众号后台「草稿箱」中可查看和编辑")
        print(f"   如需发布（不推送通知），运行：")
        print(f"   python3 wechat_draft.py publish --media-id {media_id}")


if __name__ == "__main__":
    main()
