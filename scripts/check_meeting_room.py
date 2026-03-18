#!/usr/bin/env python3
"""
定时检查上海互联T6栋 16:00-18:00 会议室空闲情况
通过 CDP WebSocket 操作浏览器
"""
import json
import subprocess
import sys
import time
import urllib.request

CDP_PORT = 9222
TARGET_ID = "325E5FB4F7C77C48E0D3DCB9079B7F4E"

def cdp_get_targets():
    """获取浏览器标签页列表"""
    try:
        url = f"http://127.0.0.1:{CDP_PORT}/json"
        req = urllib.request.urlopen(url, timeout=5)
        return json.loads(req.read())
    except:
        return []

def run_js_via_cdp(js_code):
    """通过 CDP 执行 JS 并返回结果"""
    try:
        import websocket
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "websocket-client", "-q"])
        import websocket
    
    targets = cdp_get_targets()
    ws_url = None
    for t in targets:
        if t.get("id") == TARGET_ID:
            ws_url = t.get("webSocketDebuggerUrl")
            break
    
    if not ws_url:
        for t in targets:
            if t.get("type") == "page":
                ws_url = t.get("webSocketDebuggerUrl")
                break
    
    if not ws_url:
        return None, "No browser target found"
    
    ws = websocket.create_connection(ws_url, timeout=30)
    
    msg = {
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_code,
            "returnByValue": True,
            "awaitPromise": False
        }
    }
    ws.send(json.dumps(msg))
    
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == 1:
            ws.close()
            result = resp.get("result", {}).get("result", {})
            if result.get("type") == "string":
                return result.get("value"), None
            elif result.get("type") == "object":
                return json.dumps(result.get("value")), None
            else:
                return str(result), None
    
    ws.close()
    return None, "No response"

def get_pagination_count():
    """获取总页数"""
    js = """
    (() => {
        const pager = document.querySelector('[class*=pagination]');
        if (!pager) return '1';
        const items = pager.querySelectorAll('[class*=item]');
        if (items.length === 0) return '1';
        let maxPage = 1;
        items.forEach(item => {
            const text = item.textContent.trim();
            if (/^\\d+$/.test(text)) {
                maxPage = Math.max(maxPage, parseInt(text));
            }
        });
        return String(maxPage);
    })()
    """
    result, err = run_js_via_cdp(js)
    try:
        return int(result) if result and result.isdigit() else 1
    except:
        return 1

def go_to_page(page_num):
    """跳转到指定页"""
    js = f"""
    (() => {{
        const pager = document.querySelector('[class*=pagination]');
        if (!pager) return 'no_pager';
        const items = pager.querySelectorAll('[class*=item]');
        for (const item of items) {{
            if (item.textContent.trim() === '{page_num}') {{
                item.click();
                return 'clicked_page_{page_num}';
            }}
        }}
        return 'page_{page_num}_not_found';
    }})()
    """
    return run_js_via_cdp(js)

def check_page_rooms():
    """检查当前页会议室"""
    js = """
    (() => {
        const rooms = document.querySelectorAll('[class*=room-item]');
        if (rooms.length === 0) return JSON.stringify({error: 'no_rooms'});
        
        const headers = document.querySelectorAll('[class*=room-header-item]');
        const names = Array.from(headers).map(h => h.textContent.trim());
        
        const results = [];
        rooms.forEach((room, idx) => {
            const hourBlocks = room.querySelectorAll('[class*=hour-block]');
            if (hourBlocks.length < 18) return;
            
            const block16 = hourBlocks[15];
            const block16Rect = block16.getBoundingClientRect();
            const startY = block16Rect.y;
            const endY = startY + 120;
            
            const ordered = room.querySelectorAll('[class*=ordered-block]');
            let hasConflict = false;
            let conflictMeetings = [];
            
            ordered.forEach(o => {
                const r = o.getBoundingClientRect();
                if (r.y < endY && (r.y + r.height) > startY) {
                    hasConflict = true;
                    conflictMeetings.push(o.textContent.trim().substring(0, 15));
                }
            });
            
            results.push({
                name: names[idx] || 'Room' + idx,
                available: !hasConflict,
                conflicts: conflictMeetings
            });
        });
        
        return JSON.stringify({rooms: results, total: rooms.length});
    })()
    """
    return run_js_via_cdp(js)

def check_all_pages():
    """检查所有分页的会议室"""
    total_pages = get_pagination_count()
    print(f"  检测到共 {total_pages} 页会议室")
    
    all_results = []
    
    for page in range(1, total_pages + 1):
        if page > 1:
            print(f"  检查第 {page} 页...")
            go_to_page(page)
            time.sleep(1.2)
        
        result, err = check_page_rooms()
        if err:
            print(f"    ❌ 页面{page}检查失败: {err}")
            continue
        
        try:
            data = json.loads(result)
        except:
            print(f"    ❌ 页面{page}解析失败")
            continue
        
        for room in data.get('rooms', []):
            all_results.append(room)
    
    return all_results

def navigate_to_rooms():
    """导航到会议室页面"""
    js = "window.location.href = 'https://calendar.sankuai.com/rooms'; 'navigated';"
    return run_js_via_cdp(js)

def select_shanghai_t6():
    """选择上海互联T6栋"""
    js1 = """
    (() => {
        const cascader = document.querySelector('.building-pop___33XMv-wrapper');
        if (!cascader) return 'no_cascader';
        cascader.style.display = 'block';
        cascader.style.opacity = '1';
        cascader.style.zIndex = '9999';
        const lis = cascader.querySelectorAll('li');
        for (const li of lis) {
            if (li.textContent.trim() === '上海市') {
                li.click();
                return 'clicked_shanghai';
            }
        }
        return 'no_shanghai';
    })()
    """
    result, err = run_js_via_cdp(js1)
    if err:
        return None, err
    
    time.sleep(1)
    
    js2 = """
    (() => {
        const cascader = document.querySelector('.building-pop___33XMv-wrapper');
        if (!cascader) return 'no_cascader';
        const lis = cascader.querySelectorAll('li');
        for (const li of lis) {
            if (li.textContent.trim() === '上海/互联T6栋') {
                li.click();
                return 'clicked_t6';
            }
        }
        return 'no_t6';
    })()
    """
    return run_js_via_cdp(js2)

def check_current_building():
    """检查当前选中的大楼"""
    js = """
    (() => {
        const all = document.querySelectorAll('button');
        for (const b of all) {
            if (b.textContent.includes('/')) return b.textContent.trim();
        }
        return 'unknown';
    })()
    """
    return run_js_via_cdp(js)

def main():
    print(f"[{time.strftime('%H:%M:%S')}] 开始检查会议室...")
    
    building, err = check_current_building()
    if err:
        print(f"  ❌ 浏览器连接失败: {err}")
        return False, None
    
    print(f"  当前大楼: {building}")
    
    if building and '互联T6' not in building:
        print("  需要切换到上海互联T6栋...")
        navigate_to_rooms()
        time.sleep(3)
        result, err = select_shanghai_t6()
        print(f"  切换结果: {result}")
        time.sleep(2)
    
    # 检查所有页面
    all_rooms = check_all_pages()
    
    available_rooms = []
    for room in all_rooms:
        status = "✅ 空闲" if room['available'] else f"❌ 占用 ({', '.join(room['conflicts'])})"
        print(f"  {room['name']}: {status}")
        if room['available']:
            available_rooms.append(room)
    
    if available_rooms:
        print(f"\n  🎉 找到 {len(available_rooms)} 个空闲会议室!")
        return True, available_rooms
    else:
        print(f"\n  😔 暂无空闲会议室 (共 {len(all_rooms)} 间)")
        return False, None

if __name__ == "__main__":
    found, rooms = main()
    if found:
        print(json.dumps({"found": True, "rooms": rooms}, ensure_ascii=False))
    else:
        print(json.dumps({"found": False}, ensure_ascii=False))
