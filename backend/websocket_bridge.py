#!/usr/bin/env python3
"""
WebSocket到TCP的桥接器
将WebSocket连接转换为TCP连接，实现浏览器与TCP服务器的通信
"""

import asyncio
import websockets
import json
import logging
import time
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketBridge:
    """WebSocket到TCP桥接器"""
    def __init__(self, ws_host='0.0.0.0', ws_port=8080, tcp_host='localhost', tcp_port=6000):
        self.ws_host = ws_host
        self.ws_port = ws_port
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.connections = {}  # websocket_id -> tcp_connection_info
        
    async def start_bridge(self):
        """启动桥接器"""
        logger.info(f'WebSocket桥接器启动在 ws://{self.ws_host}:{self.ws_port}')
        logger.info(f'桥接到TCP服务器 {self.tcp_host}:{self.tcp_port}')
        
        async with websockets.serve(
            self.handle_websocket,
            self.ws_host,
            self.ws_port,
            ping_interval=30,
            ping_timeout=10
        ):
            await asyncio.Future()  # 运行 forever
            
    async def handle_websocket(self, websocket, path):
        """处理WebSocket连接"""
        ws_id = f"ws_{id(websocket)}"
        logger.info(f"新的WebSocket连接: {ws_id}")
        
        try:
            # 连接到TCP服务器
            tcp_reader, tcp_writer = await asyncio.open_connection(
                self.tcp_host, self.tcp_port
            )
            
            logger.info(f"WebSocket {ws_id} 连接到TCP服务器成功")
            
            # 存储连接信息
            self.connections[ws_id] = {
                'websocket': websocket,
                'tcp_reader': tcp_reader,
                'tcp_writer': tcp_writer,
                'connected_at': datetime.now().isoformat()
            }
            
            # 启动双向消息转发
            await asyncio.gather(
                self.websocket_to_tcp(ws_id, websocket, tcp_writer),
                self.tcp_to_websocket(ws_id, tcp_reader, websocket)
            )
            
        except Exception as e:
            logger.error(f"WebSocket连接错误: {e}")
        finally:
            # 清理连接
            await self.cleanup_connection(ws_id)
            
    async def websocket_to_tcp(self, ws_id, websocket, tcp_writer):
        """WebSocket到TCP的消息转发"""
        try:
            async for message in websocket:
                try:
                    # 解析WebSocket消息
                    ws_data = json.loads(message)
                    logger.info(f"收到WebSocket消息: {ws_data.get('type', 'unknown')}")
                    
                    # 转换消息格式并发送到TCP服务器
                    tcp_message = self.convert_websocket_to_tcp(ws_data)
                    tcp_message_str = json.dumps(tcp_message) + '\n'
                    
                    tcp_writer.write(tcp_message_str.encode())
                    await tcp_writer.drain()
                    
                    logger.info(f"消息从WebSocket转发到TCP: {tcp_message.get('type', 'unknown')}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"WebSocket消息JSON解析错误: {e}")
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    }))
                except Exception as e:
                    logger.error(f"WebSocket到TCP转发错误: {e}")
                    break
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket连接关闭: {ws_id}")
        except Exception as e:
            logger.error(f"WebSocket到TCP转发异常: {e}")
            
    async def tcp_to_websocket(self, ws_id, tcp_reader, websocket):
        """TCP到WebSocket的消息转发"""
        try:
            while True:
                # 读取TCP消息（按行读取）
                data = await tcp_reader.readline()
                if not data:
                    break
                    
                try:
                    # 解析TCP消息
                    tcp_message_str = data.decode().strip()
                    if not tcp_message_str:
                        continue
                        
                    tcp_data = json.loads(tcp_message_str)
                    logger.info(f"收到TCP消息: {tcp_data.get('type', 'unknown')}")
                    
                    # 转换消息格式并发送到WebSocket
                    ws_message = self.convert_tcp_to_websocket(tcp_data)
                    
                    await websocket.send(json.dumps(ws_message))
                    logger.info(f"消息从TCP转发到WebSocket: {ws_message.get('type', 'unknown')}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"TCP消息JSON解析错误: {e}")
                except Exception as e:
                    logger.error(f"TCP到WebSocket转发错误: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"TCP到WebSocket转发异常: {e}")
            
    def convert_websocket_to_tcp(self, ws_data):
        """转换WebSocket消息格式到TCP格式"""
        # WebSocket消息格式: {type, data}
        # TCP消息格式: {type, data, timestamp}
        
        return {
            'type': ws_data.get('type'),
            'data': ws_data.get('data', {}),
            'timestamp': datetime.now().isoformat()
        }
        
    def convert_tcp_to_websocket(self, tcp_data):
        """转换TCP消息格式到WebSocket格式"""
        # TCP消息格式: {type, data, timestamp}
        # WebSocket消息格式: {type, data}
        
        return {
            'type': tcp_data.get('type'),
            'data': tcp_data.get('data', {})
        }
        
    async def cleanup_connection(self, ws_id):
        """清理连接"""
        if ws_id in self.connections:
            conn_info = self.connections[ws_id]
            
            # 关闭TCP连接
            try:
                if 'tcp_writer' in conn_info:
                    conn_info['tcp_writer'].close()
                    await conn_info['tcp_writer'].wait_closed()
            except Exception as e:
                logger.error(f"关闭TCP连接错误: {e}")
                
            # 从连接列表中移除
            del self.connections[ws_id]
            logger.info(f"连接已清理: {ws_id}")

async def main():
    """主函数"""
    # 从环境变量读取配置
    import os
    
    ws_host = os.environ.get('WS_HOST', '0.0.0.0')
    ws_port = int(os.environ.get('WS_PORT', '8080'))
    tcp_host = os.environ.get('TCP_HOST', 'localhost')
    tcp_port = int(os.environ.get('TCP_PORT', '6000'))
    
    bridge = WebSocketBridge(ws_host, ws_port, tcp_host, tcp_port)
    
    try:
        await bridge.start_bridge()
    except KeyboardInterrupt:
        logger.info("桥接器已停止")
    except Exception as e:
        logger.error(f"桥接器运行错误: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("桥接器已停止")