import json
import asyncio

from channels.generic.http import AsyncHttpConsumer
from channels.db import database_sync_to_async

from .models import Post


class SSEConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        await self.send_headers(headers=[
            (b"Cache-Control", b"no-cache"),
            (b"Content-Type", b"text/event-stream"),
            (b"Transfer-Encoding", b"chunked"),
        ])

        while True:
            # Retrieve new data since the last check
            payload_data = await self.query_new_posts()
            # If there's new data, construct and send SSE payload
            payload = f"data: {json.dumps(payload_data)}\n\n"

            if payload_data["is_new"]:
                await self.send_body(payload.encode("utf-8"), more_body=True)
            else:
                payload_data = {"is_new": False}
                payload = f"data: {json.dumps(payload_data)}\n\n"
                await self.send_body(payload.encode("utf-8"), more_body=True)

            await asyncio.sleep(5)
            await self.set_posts_not_new(payload_data)

    @staticmethod
    @database_sync_to_async
    def query_new_posts():
        """
        Querying the DB for new posts and returning the posts data if existing.
        """
        new_posts = Post.objects.filter(is_new=True).order_by("-date_created")

        if len(new_posts) > 0:
            data = {
                index: {
                    "post_id": f"{post.pk}",
                    "description": f"{post.description}",
                    "photo": f"{post.photo.url}" if post.photo else None,  
                    "likes": f"{post.likes}",
                    "comments": f"{post.comments.count()}",
                    "date_created": f"{post.date_created.strftime("%d/%m/%Y at %H:%M")}", 
                    "user_id": f"{post.user.pk}",
                    "name": f"{post.user.first_name} {post.user.last_name}",
                    "profile_photo": f"{post.user.profile_photo.url}" if post.user.profile_photo else "/media/app/default-user.png",
                }
                for index, post in enumerate(new_posts)
            }
            data["is_new"] = True
            return data 
        return {"is_new": False}
    
    @staticmethod
    @database_sync_to_async
    def set_posts_not_new(data):
        """
        Setting new posts as not new after sending them to client.
        """
        if len(data) > 1:
            del data["is_new"]
            post_ids = [data[post]["post_id"] for post in data]
            Post.objects.filter(pk__in=post_ids).update(is_new=False)

