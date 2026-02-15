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


def load_story_xml(path: Path) -> list[Message]:
    tree = ET.parse(path)
    root = tree.getroot()
    messages: list[Message] = []

    for message_el in root.findall("message"):
        message_id = message_el.get("id", "")

        sender_el = message_el.find("sender")
        receiver_el = message_el.find("receiver")
        body_el = message_el.find("body")

        sender = sender_el.get("ref", "") if sender_el is not None else ""
        receiver = receiver_el.get("ref", "") if receiver_el is not None else ""
        body = (body_el.text or "") if body_el is not None else ""
        raw_xml = ET.tostring(message_el, encoding="unicode")

        messages.append(
            Message(
                id=message_id,
                sender=sender,
                receiver=receiver,
                body=body,
                raw_xml=raw_xml,
            )
        )

    return messages
