# extract_printer_usage.py
from DrissionPage import ChromiumPage
import time


def extract_usage_status(frame):
    """从 frame 中提取打印机使用状态"""
    dt_list = frame.eles('tag:dt')
    dd_list = frame.eles('tag:dd')
    data = {}

    # 定义标签映射（去除冒号和空格）
    mapping = {
        "首次打印日期 :": "首次打印日期",
        "总页数 :": "总页数",
        "黑白总页数 :": "黑白总页数",
        "彩色总页数 :": "彩色总页数",
        "双面打印总页数 :": "双面打印总页数",
        "单面打印总页数 :": "单面打印总页数"
    }

    # 按索引配对 dt 和 dd
    for dt, dd in zip(dt_list, dd_list):
        label = dt.text.strip()
        if label in mapping:
            key = mapping[label]
            div = dd.ele('tag:div')
            data[key] = div.text.strip() if div else "获取失败"

    return data


def main():
    # 连接浏览器
    page = ChromiumPage("127.0.0.1:9222")
    tab = page.tab

    # 访问主页面
    main_url = "https://10.85.10.251/PRESENTATION/ADVANCED/COMMON/TOP"
    tab.get(main_url)
    print("✅ 已进入打印机主页面")
    time.sleep(3)

    # 点击【使用状态】
    tab.ele('text:使用状态').click()
    print("🖱️ 已点击【使用状态】")
    time.sleep(2)

    # 进入 target_INFO frame
    print("\n🔍 正在进入 target_INFO frame...")
    try:
        frame = page.get_frame('target_INFO', timeout=10)
        print("✅ 成功进入 frame")

        # 提取数据
        usage_data = extract_usage_status(frame)

        # 打印结果
        print("\n📊 打印机使用状态:")
        for key, value in usage_data.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"❌ 进入 frame 失败: {e}")


if __name__ == "__main__":
    main()