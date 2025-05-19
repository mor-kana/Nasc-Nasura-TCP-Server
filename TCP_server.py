import pygame
import socket
import struct
import time
import json

# ===== ネットワーク設定 =====
# HOST = '100.125.131.3' # 受信側（Ubuntu, NGSH）の Tailscale IP に書き換え
HOST = '100.98.176.71' # 受信側（Ubuntu, MRKN）の Tailscale IP に書き換え
PORT = 5000

# ===== Pygame & ジョイスティック初期化 =====
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("ジョイスティックが見つかりません。")
    pygame.quit()
    exit()

joy = pygame.joystick.Joystick(0)
joy.init()
print(f"Joystick initialized: {joy.get_name()}")

# ===== ソケット接続 =====
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((HOST, PORT))
    print(f"Connected to server at {HOST}:{PORT}")
except Exception as e:
    print(f"接続失敗: {e}")
    pygame.quit()
    exit()

try:
    while True:
        pygame.event.pump()

        # 全ての軸を取得
        axes = [-joy.get_axis(i) for i in range(joy.get_numaxes())]
        # 全てのハット（十字キー）を取得
        hats = [joy.get_hat(i) for i in range(joy.get_numhats())]
        # 全てのボタン状態を取得 (0 or 1)
        buttons = [joy.get_button(i) for i in range(joy.get_numbuttons())]

        # 送信データ構造
        payload = {
            'axes': axes,
            'hats': hats,
            'buttons': buttons
        }
        # JSONにシリアライズ
        msg = json.dumps(payload).encode('utf-8')

        # 長さ(4バイトビッグエンディアン)＋データ本体を送信
        header = struct.pack('>L', len(msg))
        sock.sendall(header + msg)

        # デバッグ出力
        print(f"Sent axes={axes}, hats={hats}, buttons={buttons}")

        time.sleep(0.05)  # 50msごとに送信

except KeyboardInterrupt:
    print("Client exiting")

finally:
    sock.close()
    pygame.quit()
