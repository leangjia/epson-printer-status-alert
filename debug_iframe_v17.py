# debug_iframe_v17.py
from DrissionPage import ChromiumPage

page = ChromiumPage("127.0.0.1:9222")
tab = page.tab

tab.get("https://10.85.10.251/PRESENTATION/ADVANCED/COMMON/TOP")
tab.wait(3)

# 点击【使用状态】
tab.ele('text:使用状态').click()
tab.wait(2)

print("\n🔍 正在进入 target_INFO frame...")
try:
    frame = page.get_frame('target_INFO', timeout=10)
    print("✅ 成功进入 frame")

    # 获取所有 dt 和 dd
    dt_list = frame.eles('tag:dt')
    dd_list = frame.eles('tag:dd')
    print(f"📄 找到 {len(dt_list)} 个 dt 标签")
    print(f"📄 找到 {len(dd_list)} 个 dd 标签")

    # 按索引配对
    data = {}
    for i, dt in enumerate(dt_list):
        label = dt.text.strip()
        if i < len(dd_list):
            dd = dd_list[i]
            div = dd.ele('tag:div')
            value = div.text.strip() if div else "无div"
        else:
            value = "无对应 dd"

        print(f"[{i}] {label} → {value}")
        data[label] = value

    # 测试提取关键字段
    print("\n📊 最终提取结果:")
    print("首次打印日期:", data.get("首次打印日期 :", "未找到"))
    print("总页数:", data.get("总页数 :", "未找到"))
    print("黑白总页数:", data.get("黑白总页数 :", "未找到"))
    print("彩色总页数:", data.get("彩色总页数 :", "未找到"))
    print("双面打印总页数:", data.get("双面打印总页数 :", "未找到"))
    print("单面打印总页数:", data.get("单面打印总页数 :", "未找到"))

except Exception as e:
    print(f"❌ 失败: {e}")