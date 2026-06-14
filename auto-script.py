import argparse
import requests
import re
from QueryScript import query

DEFAULT_LOW_POWER_THRESHOLD = 20.0


def parse_bark_keys(raw_keys):
    """
    解析 Bark API Key，支持逗号、空格、换行分隔多个 key。
    """
    return [key for key in re.split(r'[\s,]+', raw_keys.strip()) if key]


def parse_threshold(raw_threshold):
    """
    解析低电量提醒阈值。未传入或传入空字符串时使用默认值。
    """
    if raw_threshold is None or not raw_threshold.strip():
        return DEFAULT_LOW_POWER_THRESHOLD

    return float(raw_threshold)


def send_bark(title, desp, bark_keys):
    """
    使用 Bark 发送推送通知
    :param title: 消息标题
    :param desp: 消息内容
    :param bark_keys: Bark API Key 列表
    :return: 推送结果
    """
    results = []

    for bark_key in bark_keys:
        url = "https://api.day.app/push"
        data = {
            "device_key": bark_key,
            "title": title,
            "body": desp,
            "group": "宿舍电量监控",
            "isArchive": 1,
        }

        try:
            response = requests.post(url, json=data, timeout=15)
            response.raise_for_status()
            result = response.json()
            print(f"Bark 推送结果({bark_key[:5]}...): {result}")
            results.append(result)
        except requests.exceptions.RequestException as e:
            print(f"Bark 推送失败({bark_key[:5]}...): {e}")
            results.append(None)

    return results

def main():
    parser = argparse.ArgumentParser(description='Process some inputs.')
    parser.add_argument('--bark-keys', required=True, help='Bark API Key，多个 key 可用逗号、空格或换行分隔')
    parser.add_argument('--threshold', default=None, help=f'低电量提醒阈值，默认 {DEFAULT_LOW_POWER_THRESHOLD:g} 度')
    parser.add_argument('--Synjones_Auth', required=True, help='Synjones_Auth')
    args = parser.parse_args()
    
    bark_keys = parse_bark_keys(args.bark_keys)
    if not bark_keys:
        parser.error('--bark-keys 不能为空')

    try:
        low_power_threshold = parse_threshold(args.threshold)
    except ValueError:
        parser.error('--threshold 必须是数字')

    Synjones_Auth = args.Synjones_Auth
    print(f"Bark API Key 数量: {len(bark_keys)}")
    print(f"低电量提醒阈值: {low_power_threshold:g} 度")

    last = query("S2", "b429", Synjones_Auth=Synjones_Auth)
    print(f"Query result: {last}")  # 添加调试信息

    # 检查认证是否失效
    if last == "AUTH_FAILED":
        title = "⚠️ 认证失效提醒"
        desp = "Synjones-Auth 已失效，请重新抓包并更新 GitHub Secret: SYNJONES_AUTH。"
        send_bark(title, desp, bark_keys)
        print("已发送认证失效提醒")
        return
    
    if last is None:
        title = "❌ 脚本查询失败"
        desp = "宿舍电量查询失败，请检查 GitHub Actions 日志或山大V卡通服务状态。"
        send_bark(title, desp, bark_keys)
        print("查询失败，已发送脚本失效提醒")
        return

    try:
        # 从返回结果中提取数字（支持格式：'：16.00度' 或 '16.00'）
        match = re.search(r'(\d+\.?\d*)', last)
        if match:
            last_value = float(match.group(1))
        else:
            raise ValueError(f"无法从结果中提取数字: {last}")
        
        title = "宿舍电量提醒"
        desp = f"宿舍剩余电量 {last_value:g} 度，低于阈值 {low_power_threshold:g} 度，请及时充值。"
        
        if last_value < low_power_threshold:
            send_bark(title, desp, bark_keys)
        else:
            print(f"电量充足（{last_value}度），无需发送提醒")
    except ValueError as e:
        print(f"Error converting query result to float: {e}")

if __name__ == "__main__":
    main()
