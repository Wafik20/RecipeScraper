import httpx
import json
from typing import Dict
from urllib.parse import quote
import jmespath
import scraper as scraper
import re

INSTAGRAM_DOCUMENT_ID = "8845758582119845"  # contst id for post documents instagram.com

def scrape_post(url_or_shortcode: str) -> Dict:
    """Scrape single Instagram post data"""
    if "http" in url_or_shortcode:
        match = re.search(r"/(p|reel)/([^/?]+)", url_or_shortcode) # get either a reel or post
        shortcode =  match.group(2) if match else url_or_shortcode  # Return extracted shortcode or original input
    else:
        shortcode = url_or_shortcode
    print(f"scraping instagram post: {shortcode}")

    variables = quote(
        json.dumps(
            {
                "shortcode": shortcode,
                "fetch_tagged_user_count": None,
                "hoisted_comment_id": None,
                "hoisted_reply_id": None,
            },
            separators=(",", ":"),
        )
    )
    body = f"variables={variables}&doc_id={INSTAGRAM_DOCUMENT_ID}"
    url = "https://www.instagram.com/graphql/query"

    result = httpx.post(
        url=url,
        headers={"content-type": "application/x-www-form-urlencoded"},
        data=body,
    )
    data = json.loads(result.content)
    return data["data"]["xdt_shortcode_media"]


def parse_post(data: Dict) -> Dict:
    # Extract post owner
    post_owner = data.get("owner", {}).get("username", "")

    result = jmespath.search(
        f"""{{
        id: id,
        shortcode: shortcode,
        owner: owner.username,
        dimensions: dimensions,
        src: display_url,
        src_attached: edge_sidecar_to_children.edges[].node.display_url,
        has_audio: has_audio,
        video_url: video_url,
        views: video_view_count,
        plays: video_play_count,
        likes: edge_media_preview_like.count,
        location: location.name,
        taken_at: taken_at_timestamp,
        related: edge_web_media_to_related_media.edges[].node.shortcode,
        type: product_type,
        video_duration: video_duration,
        music: clips_music_attribution_info,
        is_video: is_video,
        tagged_users: edge_media_to_tagged_user.edges[].node.user.username,
        captions: edge_media_to_caption.edges[].node.text,
        related_profiles: edge_related_profiles.edges[].node.username,
        comments_count: edge_media_to_parent_comment.count,
        comments_disabled: comments_disabled,
        comments_next_page: edge_media_to_parent_comment.page_info.end_cursor,
        owner_comments: edge_media_to_parent_comment.edges[?node.owner.username == '{post_owner}'].node.{{ 
            id: id, 
            text: text, 
            created_at: created_at, 
            owner: owner.username 
        }}
    }}""",
        data,
    )

    return result

def get_instagram_post(url_or_shortcode: str) -> Dict:
    scraped_post = scrape_post(url_or_shortcode)
    parsed_post = parse_post(scraped_post)
    return json.dumps(parsed_post, ensure_ascii=False) # return JSON string