#!/usr/bin/env python3
"""
TCP Socket服务器
用于处理实时通信，替代Socket.IO
"""

import asyncio
import json
import logging
import time
from collections import defaultdict
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientConnection:
    """客户端连接管理"""
    def __init__(self, reader, writer, client_id):
        self.reader = reader
        self.writer = writer
        self.client_id = client_id
        self.user_id = None
        self.username = None
        self.rooms = set()
        self.authenticated = False
        self.last_activity = time.time()
        
    async def send_message(self, message_type, data):
        """发送消息给客户端"""
        try:
            message = {
                'type': message_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            message_str = json.dumps(message) + '\n'
            self.writer.write(message_str.encode())
            await self.writer.drain()
            logger.info(f"Sent to client {self.client_id}: {message_type}")
        except Exception as e:
            logger.error(f"Error sending message to client {self.client_id}: {e}")
            
    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity = time.time()

class TCPServer:
    """TCP Socket服务器"""
    def __init__(self, host='0.0.0.0', port=6000):
        self.host = host
        self.port = port
        self.clients = {}  # client_id -> ClientConnection
        self.rooms = defaultdict(set)  # room_name -> set of client_ids
        self.online_users = set()
        self.client_counter = 0
        
    async def start_server(self):
        """启动服务器"""
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        logger.info(f'TCP服务器启动在 {self.host}:{self.port}')
        
        async with server:
            await server.serve_forever()
            
    async def handle_client(self, reader, writer):
        """处理客户端连接"""
        self.client_counter += 1
        client_id = f"client_{self.client_counter}"
        client = ClientConnection(reader, writer, client_id)
        self.clients[client_id] = client
        
        addr = writer.get_extra_info('peername')
        logger.info(f'客户端连接: {addr}, ID: {client_id}')
        
        try:
            # 发送连接确认
            await client.send_message('connected', {
                'client_id': client_id,
                'message': 'Connected to TCP server'
            })
            
            # 处理客户端消息
            while True:
                data = await reader.readline()
                if not data:
                    break
                    
                message_str = data.decode().strip()
                if not message_str:
                    continue
                    
                try:
                    message = json.loads(message_str)
                    await self.process_message(client, message)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误 from {client_id}: {e}")
                    await client.send_message('error', {'message': 'Invalid JSON format'})
                    
        except asyncio.CancelledError:
            logger.info(f"Client {client_id} connection cancelled")
        except Exception as e:
            logger.error(f"处理客户端 {client_id} 时发生错误: {e}")
        finally:
            # 清理客户端连接
            await self.remove_client(client_id)
            writer.close()
            await writer.wait_closed()
            logger.info(f'客户端断开连接: {addr}')
            
    async def process_message(self, client, message):
        """处理客户端消息"""
        client.update_activity()
        
        message_type = message.get('type')
        data = message.get('data', {})
        
        logger.info(f"收到消息 from {client.client_id}: {message_type}")
        
        if message_type == 'authenticate':
            await self.handle_authenticate(client, data)
        elif message_type == 'join_room':
            await self.handle_join_room(client, data)
        elif message_type == 'leave_room':
            await self.handle_leave_room(client, data)
        elif message_type == 'send_message':
            await self.handle_send_message(client, data)
        elif message_type == 'typing':
            await self.handle_typing(client, data)
        elif message_type == 'stop_typing':
            await self.handle_stop_typing(client, data)
        elif message_type == 'get_online_count':
            await self.handle_get_online_count(client)
        else:
            logger.warning(f"未知消息类型: {message_type}")
            
    async def handle_authenticate(self, client, data):
        """处理用户认证"""
        user_id = data.get('user_id')
        username = data.get('username')
        
        if not user_id:
            await client.send_message('auth_error', {'message': 'User ID required'})
            return
            
        client.user_id = user_id
        client.username = username
        client.authenticated = True
        self.online_users.add(user_id)
        
        logger.info(f"用户认证成功: {username} (ID: {user_id})")
        
        # 发送认证成功消息
        await client.send_message('auth_success', {
            'user_id': user_id,
            'username': username,
            'message': 'Authentication successful'
        })
        
        # 广播用户上线
        await self.broadcast_to_all('user_online', {
            'user_id': user_id,
            'username': username,
            'online_count': len(self.online_users)
        })
        
    async def handle_join_room(self, client, data):
        """处理加入房间"""
        if not client.authenticated:
            await client.send_message('error', {'message': 'Authentication required'})
            return
            
        room_name = data.get('room_name')
        if not room_name:
            await client.send_message('error', {'message': 'Room name required'})
            return
            
        # 离开当前房间
        if client.rooms:
            for old_room in list(client.rooms):
                await self.leave_room(client, old_room)
                
        # 加入新房间
        await self.join_room(client, room_name)
        
    async def handle_leave_room(self, client, data):
        """处理离开房间"""
        room_name = data.get('room_name')
        if room_name:
            await self.leave_room(client, room_name)
        else:
            # 离开所有房间
            for room in list(client.rooms):
                await self.leave_room(client, room)
                
    async def handle_send_message(self, client, data):
        """处理发送消息"""
        if not client.authenticated:
            await client.send_message('error', {'message': 'Authentication required'})
            return
            
        room_name = data.get('room_name')
        message_content = data.get('message')
        
        if not room_name or not message_content:
            await client.send_message('error', {'message': 'Room name and message required'})
            return
            
        if room_name not in client.rooms:
            await client.send_message('error', {'message': 'Not in room'})
            return
            
        # 广播消息到房间
        message_data = {
            'room_name': room_name,
            'user_id': client.user_id,
            'username': client.username,
            'message': message_content,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast_to_room(room_name, 'new_message', message_data)
        
    async def handle_typing(self, client, data):
        """处理输入状态"""
        if not client.authenticated:
            return
            
        room_name = data.get('room_name')
        if room_name and room_name in client.rooms:
            typing_data = {
                'room_name': room_name,
                'user_id': client.user_id,
                'username': client.username,
                'is_typing': True
            }
            
            # 广播给房间内的其他用户
            await self.broadcast_to_room_except(room_name, 'user_typing', typing_data, client.client_id)
            
    async def handle_stop_typing(self, client, data):
        """处理停止输入"""
        if not client.authenticated:
            return
            
        room_name = data.get('room_name')
        if room_name and room_name in client.rooms:
            typing_data = {
                'room_name': room_name,
                'user_id': client.user_id,
                'username': client.username,
                'is_typing': False
            }
            
            await self.broadcast_to_room_except(room_name, 'user_stop_typing', typing_data, client.client_id)
            
    async def handle_get_online_count(self, client):
        """处理获取在线用户数"""
        await client.send_message('online_count', {
            'count': len(self.online_users)
        })
        
    async def join_room(self, client, room_name):
        """加入房间"""
        client.rooms.add(room_name)
        self.rooms[room_name].add(client.client_id)
        
        logger.info(f"用户 {client.username} 加入房间 {room_name}")
        
        # 发送加入成功消息
        await client.send_message('room_joined', {
            'room_name': room_name,
            'message': f'Joined room {room_name}'
        })
        
        # 广播给房间内的其他用户
        join_data = {
            'room_name': room_name,
            'user_id': client.user_id,
            'username': client.username,
            'message': f'{client.username} joined the room'
        }
        
        await self.broadcast_to_room_except(room_name, 'user_joined', join_data, client.client_id)
        
    async def leave_room(self, client, room_name):
        """离开房间"""
        if room_name in client.rooms:
            client.rooms.remove(room_name)
            self.rooms[room_name].discard(client.client_id)
            
            # 如果房间为空，删除房间
            if not self.rooms[room_name]:
                del self.rooms[room_name]
                
            logger.info(f"用户 {client.username} 离开房间 {room_name}")
            
            # 广播给房间内的其他用户
            leave_data = {
                'room_name': room_name,
                'user_id': client.user_id,
                'username': client.username,
                'message': f'{client.username} left the room'
            }
            
            await self.broadcast_to_room_except(room_name, 'user_left', leave_data, client.client_id)
            
    async def broadcast_to_room(self, room_name, message_type, data):
        """广播消息到房间"""
        if room_name in self.rooms:
            for client_id in self.rooms[room_name]:
                if client_id in self.clients:
                    await self.clients[client_id].send_message(message_type, data)
                    
    async def broadcast_to_room_except(self, room_name, message_type, data, except_client_id):
        """广播消息到房间（排除指定客户端）"""
        if room_name in self.rooms:
            for client_id in self.rooms[room_name]:
                if client_id != except_client_id and client_id in self.clients:
                    await self.clients[client_id].send_message(message_type, data)
                    
    async def broadcast_to_all(self, message_type, data):
        """广播消息给所有客户端"""
        for client in self.clients.values():
            await client.send_message(message_type, data)
            
    async def remove_client(self, client_id):
        """移除客户端"""
        if client_id in self.clients:
            client = self.clients[client_id]
            
            # 离开所有房间
            for room in list(client.rooms):
                await self.leave_room(client, room)
                
            # 从在线用户中移除
            if client.user_id:
                self.online_users.discard(client.user_id)
                
                # 广播用户下线
                await self.broadcast_to_all('user_offline', {
                    'user_id': client.user_id,
                    'username': client.username,
                    'online_count': len(self.online_users)
                })
                
            del self.clients[client_id]
            
async def main():
    """主函数"""
    server = TCPServer()
    await server.start_server()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务器已停止")