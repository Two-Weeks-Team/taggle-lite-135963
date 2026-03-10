import os
import json
import re
import httpx
from typing import Any, Dict, List

_INFERENCE_URL = "https://inference.do-ai.run/v1/chat/completions"
_INFERENCE_KEY = os.getenv("DIGITALOCEAN_INFERENCE_KEY")
_MODEL = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")

def _extract_json(text: str) -> str:
    """Extract a JSON blob from possible markdown code fences or raw text."""
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()

async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {_INFERENCE_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _MODEL,
        "messages": messages,
        "max_completion_tokens": max_tokens,
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(_INFERENCE_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # OpenAI‑style response – extract the assistant's content
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            json_str = _extract_json(content)
            return json.loads(json_str)
    except Exception as exc:
        # Unified fallback – never propagate errors to the API layer
        return {"note": f"AI service is temporarily unavailable: {str(exc)}"}

async def generate_tags(url: str, max_tags: int = 3) -> Dict[str, Any]:
    """Ask the LLM to produce up to *max_tags* short tag strings for *url*.
    The response is expected to be a JSON object with a ``tags`` array.
    """
    user_msg = (
        f"Provide up to {max_tags} concise tags (no more than three words each) for the following URL: {url}. "
        "Return ONLY a JSON object with a key called 'tags', e.g., {\"tags\": [\"tag1\", \"tag2\"]}."
    )
    messages = [{"role": "user", "content": user_msg}]
    return await _call_inference(messages, max_tokens=512)

async def cluster_bookmarks(bookmark_ids: List[str], cluster_count: int = 2) -> Dict[str, Any]:
    """Ask the LLM to group *bookmark_ids* into *cluster_count* clusters.
    Expected return format: {"clusters": [{"id": "c1", "bookmarks": ["id1", "id2"]}, ...]}
    """
    ids_str = ", ".join(bookmark_ids)
    user_msg = (
        f"Cluster the following bookmark IDs into {cluster_count} groups: {ids_str}. "
        "Return ONLY a JSON object with a key called 'clusters', each element having an 'id' and a 'bookmarks' list."
    )
    messages = [{"role": "user", "content": user_msg}]
    return await _call_inference(messages, max_tokens=512)
