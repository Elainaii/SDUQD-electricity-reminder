import argparse
import requests
import re
from QueryScript import query

def send_serverchan(title, desp, sendkey):
    """
    使用Server酱发送推送通知
    :param title: 消息标题
    :param desp: 消息内容（支持Markdown）
    :param sendkey: Server酱的SendKey
    :return: 推送结果
    """
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    
    # 使用POST请求发送，避免GET请求的长度限制
    data = {
        "title": title,
        "desp": desp
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()
        print(f"推送结果: {result}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"推送失败: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Process some inputs.')
    parser.add_argument('--sendkey', required=True, help='Server酱SendKey')
    parser.add_argument('--Synjones_Auth', required=True, help='Synjones_Auth')
    args = parser.parse_args()
    
    sendkey = args.sendkey
    Synjones_Auth = args.Synjones_Auth
    print(f"SendKey: {sendkey[:5]}...")  # 只显示部分SendKey

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
        send_serverchan(title, desp, sendkey)
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
        send_serverchan(title, desp, sendkey)
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
            send_serverchan(title, desp, sendkey)
        else:
            print(f"电量充足（{last_value}度），无需发送提醒")
    except ValueError as e:
        print(f"Error converting query result to float: {e}")

if __name__ == "__main__":
    main()