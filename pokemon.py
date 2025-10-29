#!/usr/bin/env python3
import asyncio
import os
import logging

from joycontrol import logging_default as log, utils
from joycontrol.controller import Controller
from joycontrol.controller_state import button_push
from joycontrol.command_line_interface import CLI
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server

async def main():
    # === 用户配置区 ===
    reconnect_bt_addr = "C8:48:05:51:07:0F"  # ← 在此填入你的 Switch 蓝牙地址
    interval = 1.0                            # 每隔 1 秒按一次 A
    controller = Controller.PRO_CONTROLLER
    # =================

    # 初始化手柄协议
    spi_flash = FlashMemory()
    factory = controller_protocol_factory(controller, spi_flash=spi_flash, reconnect=reconnect_bt_addr)

    # 启动 HID server
    transport, protocol = await create_hid_server(
        factory,
        reconnect_bt_addr=reconnect_bt_addr,
        ctl_psm=17,
        itr_psm=19,
        capture_file=None,
        device_id=None,
        interactive=False
    )

    controller_state = protocol.get_controller_state()
    await controller_state.connect()  # 等待连接完成
    print("✅ 已连接到 Switch，开始自动按 A ...（Ctrl+C 停止）")

    try:
        while True:
            await button_push(controller_state, 'a')
            await CLI.
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        print("\n🛑 用户中止，断开连接。")
    finally:
        await transport.close()

if __name__ == "__main__":
    if os.geteuid() != 0:
        raise PermissionError("⚠️ 请使用 sudo 运行本程序！")

    log.configure(console_level=logging.INFO)
    asyncio.run(main())
