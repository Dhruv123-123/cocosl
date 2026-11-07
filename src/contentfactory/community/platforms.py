"""Read comments and post replies through official APIs only.

Instagram Graph API (version pinned in publish/_http.GRAPH_API_VERSION):
- GET /{ig-media-id}/comments?fields=id,text,username,timestamp,like_count,replies{...}
  Top-level comments, max 50 per page, reverse chronological; replies only via
  field expansion. Needs instagram_basic + instagram_manage_comments
  (+ pages_read_engagement) with Facebook Login, or instagram_business_basic +
  instagram_business_manage_comments with Instagram Login (IG_API_HOST=graph.instagram.com).
  https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-media/comments
  https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-comment
- POST /{ig-comment-id}/replies  message=...  -> {"id": ...}
  Only top-level comments can be replied to (a reply to a reply lands on the
  top-level comment); hidden comments and live-video comments can't be replied to.
  https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-comment/replies

YouTube Data API v3:
- GET /commentThreads?part=snippet,replies&videoId=...&maxResults=100&textFormat=plainText
  (1 quota unit). items[].snippet.{channelId, videoId, topLevelComment{id, snippet}},
  items[].replies.comments[] (may be incomplete). textOriginal is only returned
  to the comment's author, so we read textDisplay with textFormat=plainText.
  https://developers.google.com/youtube/v3/docs/commentThreads/list
  https://developers.google.com/youtube/v3/docs/comments
- POST /comments?part=snippet {"snippet": {"parentId", "textOriginal"}}
  (50 quota units). Requires the https://www.googleapis.com/auth/youtube.force-ssl scope.
  https://developers.google.com/youtube/v3/docs/comments/insert

Nothing here likes, hides, deletes or DMs. Adapters never touch the DB.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import httpx

from ..config import Settings
from ..publish.base import PublishError
from ..publish.instagram import InstagramPublisher
from ..publish.youtube import API as YT_API
from ..publish.youtube import YouTubePublisher

YT_FORCE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
IG_PAGE_SIZE = 50
YT_PAGE_SIZE = 100
REPLY_MAX_CHARS = {"instagram": 2200, "youtube": 10000}


@dataclass
class RemoteComment:
    remote_id: str
    author: str
    text: str
    created_at: str = ""
    like_count: int = 0
    parent_remote_id: str = ""
    own: bool = False              # written by the brand's own account
    raw: dict = field(default_factory=dict)


class CommentsClient:
    platform = "base"

    def fetch(self, remote_id: str, max_pages: int = 4) -> list[RemoteComment]:  # pragma: no cover
        raise NotImplementedError

    def reply(self, parent_remote_id: str, text: str) -> str:  # pragma: no cover
        raise NotImplementedError

    def missing_credentials(self) -> list[str]:  # pragma: no cover
        raise NotImplementedError


class InstagramComments(CommentsClient):
    platform = "instagram"
    FIELDS = ("id,text,username,timestamp,like_count,"
              "replies{id,text,username,timestamp,like_count}")

    def __init__(self, settings: Settings, own_usernames: set[str] | None = None,
                 transport: httpx.BaseTransport | None = None):
        self.pub = InstagramPublisher(settings, transport=transport)
        self.settings = settings
        own = {u.lower().lstrip("@") for u in (own_usernames or set()) if u}
        if settings.env("IG_USERNAME"):
            own.add(settings.env("IG_USERNAME").lower().lstrip("@"))
        self.own = own

    def missing_credentials(self) -> list[str]:
        return self.pub.missing_credentials()

    def _convert(self, item: dict, parent: str = "") -> RemoteComment:
        username = item.get("username") or (item.get("from") or {}).get("username") or ""
        return RemoteComment(
            remote_id=str(item.get("id", "")), author=username, text=item.get("text") or "",
            created_at=item.get("timestamp") or "", like_count=int(item.get("like_count") or 0),
            parent_remote_id=parent, own=username.lower() in self.own,
            raw={k: v for k, v in item.items() if k != "replies"})

    def fetch(self, remote_id: str, max_pages: int = 4) -> list[RemoteComment]:
        self.pub.ensure_credentials()
        out: list[RemoteComment] = []
        after = ""
        for _ in range(max_pages):
            params = {"fields": self.FIELDS, "limit": IG_PAGE_SIZE}
            if after:
                params["after"] = after
            body = self.pub._get(f"{remote_id}/comments", "comments", **params)
            for item in body.get("data") or []:
                top = self._convert(item)
                out.append(top)
                for rep in ((item.get("replies") or {}).get("data") or []):
                    out.append(self._convert(rep, parent=top.remote_id))
            paging = body.get("paging") or {}
            after = (paging.get("cursors") or {}).get("after", "")
            if not paging.get("next") or not after:
                break
        return out

    def reply(self, parent_remote_id: str, text: str) -> str:
        self.pub.ensure_credentials()
        body = self.pub._post(f"{parent_remote_id}/replies", "reply to comment", message=text)
        if not body.get("id"):
            raise PublishError("instagram: reply returned no id", retryable=False)
        return str(body["id"])


class YouTubeComments(CommentsClient):
    platform = "youtube"

    def __init__(self, settings: Settings, transport: httpx.BaseTransport | None = None):
        self.pub = YouTubePublisher(settings, transport=transport)
        self.settings = settings
        self.own_channel = settings.env("YT_CHANNEL_ID")

    def missing_credentials(self) -> list[str]:
        return self.pub.missing_credentials()

    def _convert(self, c: dict, video_channel: str, parent: str = "") -> RemoteComment:
        sn = c.get("snippet") or {}
        author_channel = (sn.get("authorChannelId") or {}).get("value", "")
        own = bool(author_channel) and author_channel in {video_channel, self.own_channel}
        return RemoteComment(
            remote_id=str(c.get("id", "")), author=sn.get("authorDisplayName") or "",
            text=sn.get("textDisplay") or sn.get("textOriginal") or "",
            created_at=sn.get("publishedAt") or "", like_count=int(sn.get("likeCount") or 0),
            parent_remote_id=parent or sn.get("parentId", ""), own=own,
            raw={"id": c.get("id"), "authorChannelId": author_channel, "videoChannel": video_channel,
                 "publishedAt": sn.get("publishedAt"), "moderationStatus": sn.get("moderationStatus")})

    def fetch(self, remote_id: str, max_pages: int = 4) -> list[RemoteComment]:
        self.pub.ensure_credentials()
        out: list[RemoteComment] = []
        token = ""
        for _ in range(max_pages):
            params = {"part": "snippet,replies", "videoId": remote_id, "maxResults": YT_PAGE_SIZE,
                      "textFormat": "plainText", "order": "time"}
            if token:
                params["pageToken"] = token
            body = self.pub.http.json("GET", f"{YT_API}/commentThreads", what="commentThreads.list",
                                      params=params, headers=self.pub._auth())
            for thread in body.get("items") or []:
                sn = thread.get("snippet") or {}
                channel = sn.get("channelId", "")
                top_raw = sn.get("topLevelComment") or {}
                top = self._convert(top_raw, channel)
                top.raw["canReply"] = sn.get("canReply", True)
                out.append(top)
                for rep in ((thread.get("replies") or {}).get("comments") or []):
                    out.append(self._convert(rep, channel, parent=top.remote_id))
            token = body.get("nextPageToken", "")
            if not token:
                break
        return out

    def reply(self, parent_remote_id: str, text: str) -> str:
        self.pub.ensure_credentials()
        try:
            body = self.pub.http.json("POST", f"{YT_API}/comments", what="comments.insert",
                                      params={"part": "snippet"}, headers=self.pub._auth(),
                                      json={"snippet": {"parentId": parent_remote_id, "textOriginal": text}})
        except PublishError as e:
            if "insufficient" in str(e).lower() or "HTTP 403" in str(e):
                raise PublishError(f"{e}. Replying needs the youtube.force-ssl scope: add {YT_FORCE_SSL_SCOPE} "
                                   "to the YouTube scopes and re-run `factory auth youtube`.",
                                   retryable=False) from None
            raise
        if not body.get("id"):
            raise PublishError("youtube: comments.insert returned no id", retryable=False)
        return str(body["id"])


SUPPORTED = ("instagram", "youtube")


def client_for(platform: str, settings: Settings, *, own_usernames: set[str] | None = None,
               transport: httpx.BaseTransport | None = None) -> CommentsClient:
    if platform == "instagram":
        return InstagramComments(settings, own_usernames, transport=transport)
    if platform == "youtube":
        return YouTubeComments(settings, transport=transport)
    raise ValueError(f"Comments aren't supported for '{platform}' yet (supported: {', '.join(SUPPORTED)})")
