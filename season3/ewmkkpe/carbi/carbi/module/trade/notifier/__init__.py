# -*- coding: utf-8 -*-
import requests


def notify_slack(url, content):
  payload = {
    'text': _build_slack_text(content),
  }
  requests.post(url, json=payload)


def _build_slack_text(content):
  title = content.title
  texts = [
    title,
    "```",
    content.text,
    "```",
  ]
  return "\n".join(texts)
