import argparse
import requests
import re
from QueryScript import query


def parse_bark_keys(raw_keys):
    """
    解析 Bark API Key，支持逗号、空格、换行分隔多个 key。
    """
    return [key for key in re.split(r'[\s,]+', raw_keys.strip()) if key]


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
    parser.add_argument('--Synjones_Auth', required=True, help='Synjones_Auth')
    args = parser.parse_args()
    
    bark_keys = parse_bark_keys(args.bark_keys)
    if not bark_keys:
        parser.error('--bark-keys 不能为空')

    Synjones_Auth = args.Synjones_Auth
    print(f"Bark API Key 数量: {len(bark_keys)}")

    last = query("S2", "b429", Synjones_Auth=Synjones_Auth)
    print(f"Query result: {last}")  # 添加调试信息

    # 检查认证是否失效
    if last == "AUTH_FAILED":
        title = "⚠️ 认证失效提醒"
        desp = """**Synjones-Auth 认证已失效！**

认证信息已过期（401 Unauthorized）。

请按以下步骤更新认证信息：
1. 重新进行抓包获取新的 Synjones-Auth
2. 在 GitHub 仓库的 Settings → Secrets 中更新 SYNJONES_AUTH

---
*本消息由宿舍电量监控系统自动发送*"""
        send_bark(title, desp, bark_keys)
        print("已发送认证失效提醒")
        return
    
    if last is None:
        title = "❌ 脚本查询失败"
        desp = """**电量查询脚本执行失败！**

系统在查询宿舍电量时遇到错误，可能的原因：
- 网络连接问题
- 山大服务器异常
- 请求参数错误
- 其他未知错误

建议：
1. 检查 GitHub Actions 运行日志查看具体错误信息
2. 如果持续失败，可能需要检查脚本是否需要更新
3. 确认山大V卡通系统是否正常运行

---
*本消息由宿舍电量监控系统自动发送*"""
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
        
        # 使用Markdown格式的消息内容
        title = "宿舍电量提醒"
        desp = f"""**您好！**

您的宿舍电量不足，仅剩 **{last_value}** 度，请及时充值。

---
*本消息由宿舍电量监控系统自动发送*"""
        
        if last_value < 20: #last_value 为宿舍剩余电量，低于20度时发送推送提醒，可根据实际情况修改
            send_bark(title, desp, bark_keys)
        else:
            print(f"电量充足（{last_value}度），无需发送提醒")
    except ValueError as e:
        print(f"Error converting query result to float: {e}")

if __name__ == "__main__":
    main()
