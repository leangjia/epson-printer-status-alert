# printer_monitor.py
from DrissionPage import ChromiumPage, ChromiumOptions
import time
import openpyxl
from datetime import datetime
import requests

# ==================== 配置区 ====================
PRINTER_IP = "10.85.10.251"
EXCEL_FILE = "打印机使用状态记录.xlsx"
WECHAT_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的企业微信webhook-key"
GOTIFY_URL = "http://10.85.30.24:8385/message?token=A5gkYdBfPJs56z1"


# ==============================================

def extract_usage_status(frame):
    """从 frame 中提取关键数据"""
    dt_list = frame.eles('tag:dt')
    dd_list = frame.eles('tag:dd')
    data = {}

    mapping = {
        "首次打印日期 :": "首次打印日期",
        "总页数 :": "总页数",
        "黑白总页数 :": "黑白总页数",
        "彩色总页数 :": "彩色总页数",
        "双面打印总页数 :": "双面打印总页数",
        "单面打印总页数 :": "单面打印总页数"
    }

    for dt, dd in zip(dt_list, dd_list):
        label = dt.text.strip()
        if label in mapping:
            key = mapping[label]
            div = dd.ele('tag:div')
            data[key] = div.text.strip() if div else "获取失败"

    return data


def write_to_excel(data):
    """写入 Excel，追加一行"""
    try:
        try:
            wb = openpyxl.load_workbook(EXCEL_FILE)
        except FileNotFoundError:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "打印记录"
            headers = ["采集时间", "首次打印日期", "总页数", "黑白总页数", "彩色总页数", "双面打印", "单面打印"]
            ws.append(headers)

        ws = wb.active
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("首次打印日期", ""),
            data.get("总页数", ""),
            data.get("黑白总页数", ""),
            data.get("彩色总页数", ""),
            data.get("双面打印总页数", ""),
            data.get("单面打印总页数", "")
        ]
        ws.append(row)
        wb.save(EXCEL_FILE)
        print(f"✅ 数据已写入 Excel: {EXCEL_FILE}")
    except Exception as e:
        print(f"❌ 写入 Excel 失败: {e}")


def send_wechat_alert(data):
    """发送企业微信通知"""
    if not WECHAT_WEBHOOK or "你的key" in WECHAT_WEBHOOK:
        print("⚠️ 企业微信 webhook 未配置，跳过")
        return

    sj = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = data.get("总页数", "未知")
    black_white = data.get("黑白总页数", "未知")
    color = data.get("彩色总页数", "未知")

    msg = f"""
【打印机状态】
采集时间：{sj}
总页数: {total}
黑白: {black_white}  彩色: {color}
""".strip()

    payload = {
        "msgtype": "text",
        "text": {"content": msg}
    }

    try:
        requests.post(WECHAT_WEBHOOK, json=payload, timeout=5)
        print("✅ 企业微信通知已发送")
    except Exception as e:
        print(f"❌ 企业微信发送失败: {e}")


def send_gotify_alert(data):
    """发送 Gotify 通知"""
    if not GOTIFY_URL or "你的gotify" in GOTIFY_URL:
        print("⚠️ Gotify URL 未配置，跳过")
        return

    sj = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = data.get("总页数", "未知")
    color = data.get("彩色总页数", "未知")

    msg = f"🖨️ 打印机状态\n总页数: {total}\n彩色: {color}\n采集时间：{sj}"

    try:
        requests.post(GOTIFY_URL, data={"title": "打印机监控", "message": msg, "priority": 5}, timeout=5)
        print("✅ Gotify 通知已发送")
    except Exception as e:
        print(f"❌ Gotify 发送失败: {e}")


def main():
    # === 设置浏览器选项，自动忽略证书错误 ===
    co = ChromiumOptions()
    co.set_argument('--ignore-certificate-errors')
    co.set_argument('--allow-running-insecure-content')
    # 可选：隐藏浏览器窗口（无头模式）
    # co.set_headless(True)

    # ✅ 修复：直接传入 co，而不是 options=co
    page = ChromiumPage(co)

    print("✅ 浏览器已启动（忽略证书错误）")

    try:
        # 访问打印机主页面
        page.get(f"https://10.85.10.251/PRESENTATION/ADVANCED/COMMON/TOP")
        print("✅ 已进入打印机主页面")
        time.sleep(3)

        # 点击【使用状态】
        tab = page.tab
        tab.ele('text:使用状态').click()
        print("🖱️ 已点击【使用状态】")
        time.sleep(2)

        # 进入 target_INFO frame
        print("\n🔍 正在进入 target_INFO frame...")
        frame = page.get_frame('target_INFO', timeout=10)
        print("✅ 成功进入 frame")

        # 提取数据
        usage_data = extract_usage_status(frame)
        print("\n📊 提取到数据:", usage_data)

        # 写入 Excel
        write_to_excel(usage_data)

        # 发送通知
        send_wechat_alert(usage_data)
        send_gotify_alert(usage_data)

    except Exception as e:
        print(f"❌ 操作失败: {e}")
    finally:
        page.quit()  # 关闭浏览器
        print("🟢 浏览器已关闭")

if __name__ == "__main__":
    main()