from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Chat, Gig
import json

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.gig_id = self.scope['url_route']['kwargs']['gig_id']
        self.room_group_name = f'chat_{self.gig_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            print("DEBUG - Received:", data)  # Detailed logging
            
            # Convert gig_id to integer if it exists
            if 'gig_id' in data:
                try:
                    data['gig_id'] = int(data['gig_id'])
                except (ValueError, TypeError):
                    raise ValueError("gig_id must be a number")

            required_fields = {
                'message': str,
                'sender': str,
                'recipient': str,
                'gig_id': int
            }
            
            missing = [k for k in required_fields if k not in data]
            if missing:
                raise ValueError(f"Missing fields: {missing}. Received: {data}")

            # Debug print before DB operations
            print(f"Attempting to save message for gig {data['gig_id']}")

            # Get objects with explicit error handling
            try:
                gig = await self.get_gig(data['gig_id'])
                sender = await self.get_user(data['sender'])
                recipient = await self.get_user(data['recipient'])
            except Exception as e:
                raise ValueError(f"Error getting objects: {str(e)}")

            # Save with explicit commit
            try:
                chat_message = await database_sync_to_async(Chat.objects.create)(
                    gig=gig,
                    sender=sender,
                    recipient=recipient,
                    message=data['message']
                )
                print(f"SUCCESS - Saved message ID {chat_message.id}")
            except Exception as e:
                raise ValueError(f"DB save failed: {str(e)}")

            # Broadcast confirmation
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'status': 'saved',
                    'message_id': str(chat_message.id),
                    **{k: data[k] for k in required_fields}
                }
            )
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            await self.send(text_data=json.dumps({
                'error': error_msg,
                'received_data': data,  # Echo back
                'status': 'error'
            }))


    async def chat_message(self, event):
        timestamp = event.get('timestamp') or timezone.now().isoformat()
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
            'recipient': event['recipient'],
            'timestamp': timestamp,
            'message_id': event['message_id']
        }))

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def get_gig(self, gig_id):
        return Gig.objects.get(id=gig_id)

    @database_sync_to_async
    def create_chat_message(self, gig, sender, recipient, message):
        return Chat.objects.create(
            gig=gig,
            sender=sender,
            recipient=recipient,
            message=message
        )