from datetime import datetime
import pytz
import random
import streamlit as st

tools_ = [
  {
    "type": "function",
    "function": {
      "name": "get_current_time",
      "description": "해당 타임존의 날짜와 시간을 반환합니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "timezone": {
            "type": "string",
            "description": "타임존 문자열 (예: Asia/Seoul)"
          }
        },
        "required": [
          "timezone"
        ]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "draw_tarot_cards",
      "description": "타로 카드 숫자 아이디 3개를 리턴합니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "card_ids": {
            "type": "string",
            "description": "0~21 (총 22개) 숫자 중 랜덤으로 3개 (예: 7, 4, 20)"
          }
        },
        "required": [
          "card_ids"
        ]
      }
    }
  }
]

def get_current_time(timezone: str = 'Asia/Seoul'):
    tz = pytz.timezone(timezone)
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    return f"{now} {timezone}"

def draw_tarot_cards(card_ids: str):
    card_ids = card_ids.split(',')
    return random.sample(card_ids, 3)
  
def reading():
  pass
  

    