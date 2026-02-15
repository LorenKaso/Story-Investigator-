from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass
class Message:
    id: str
    sender: str
    receiver: str
    body: str
    raw_xml: str


def _localname(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _find_child_by_localname(element: ET.Element, name: str) -> ET.Element | None:
    for child in list(element):
        if _localname(child.tag).lower() == name.lower():
            return child
    return None


def _find_first_child_by_localnames(
    element: ET.Element, names: set[str]
) -> ET.Element | None:
    for child in list(element):
        if _localname(child.tag).lower() in names:
            return child
    return None


def load_story_xml(path: Path) -> list[Message]:
    try:
        content = path.read_text(encoding="utf-8-sig", errors="strict")
        root = ET.fromstring(content)
    except (ET.ParseError, OSError, UnicodeError) as exc:
        raise ValueError(f"Failed to parse story XML at {path}") from exc

    try:
        message_elements = root.findall(".//{*}message")
    except SyntaxError:
        message_elements = []

    if not message_elements:
        for pattern in (".//{*}Message", ".//{*}msg", ".//{*}messageEntry"):
            try:
                message_elements = root.findall(pattern)
            except SyntaxError:
                message_elements = []
            if message_elements:
                break

    if not message_elements:
        allowed = {"message", "msg", "messageentry"}
        message_elements = [
            elem
            for elem in root.iter()
            if _localname(elem.tag).lower() in allowed
        ]
    messages: list[Message] = []
    if message_elements:
        for message_el in message_elements:
            sender_el = _find_child_by_localname(message_el, "sender")
            receiver_el = _find_child_by_localname(message_el, "receiver")
            body_el = _find_child_by_localname(message_el, "body")

            messages.append(
                Message(
                    id=message_el.get("id", ""),
                    sender=sender_el.get("ref", "") if sender_el is not None else "",
                    receiver=receiver_el.get("ref", "") if receiver_el is not None else "",
                    body=(body_el.text or "") if body_el is not None else "",
                    raw_xml=ET.tostring(message_el, encoding="unicode"),
                )
            )
        return messages

    event_elements: list[ET.Element] = []
    for events_el in root.iter():
        if _localname(events_el.tag).lower() != "events":
            continue
        for child in list(events_el):
            if _localname(child.tag).lower() == "event":
                event_elements.append(child)

    if event_elements:
        for idx, event_el in enumerate(event_elements, start=1):
            sender_el = _find_first_child_by_localnames(event_el, {"sender", "from"})
            receiver_el = _find_first_child_by_localnames(event_el, {"receiver", "to"})
            body_el = _find_first_child_by_localnames(
                event_el, {"body", "text", "description", "content"}
            )

            sender = ""
            if sender_el is not None:
                sender = sender_el.get("ref", "") or (sender_el.text or "")

            receiver = ""
            if receiver_el is not None:
                receiver = receiver_el.get("ref", "") or (receiver_el.text or "")

            body = (body_el.text or "") if body_el is not None else ""

            messages.append(
                Message(
                    id=event_el.get("id", str(idx)),
                    sender=sender,
                    receiver=receiver,
                    body=body,
                    raw_xml=ET.tostring(event_el, encoding="unicode"),
                )
            )
        return messages

    root_name = _localname(root.tag)
    seen_localnames: list[str] = []
    seen_lookup: set[str] = set()
    for elem in root.iter():
        name = _localname(elem.tag)
        key = name.lower()
        if key not in seen_lookup:
            seen_lookup.add(key)
            seen_localnames.append(name)
        if len(seen_localnames) >= 30:
            break
    joined = ", ".join(seen_localnames)
    raise ValueError(
        "No messages found in story XML at "
        f"{path} (root={root_name}, seen_localnames=[{joined}])"
    )
