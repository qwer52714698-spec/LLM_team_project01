# streamlit_app.py
import time
import random
import json

import streamlit as st
from openai import OpenAI

import prompt
import tarot_data
from function_tools import (
    get_current_time,
    draw_tarot_cards,
    tools_,
)

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(layout="centered")
st.title("👉 고민될 땐, 타로챗봇")

MODEL_MAIN = "gpt-4o-mini"
MODEL_STREAM = "gpt-4.1"
MODEL_OPENING = "gpt-4.1-nano-2025-04-14"

client = OpenAI()

# --------------------------------------------------
# OpenAI 호출
# --------------------------------------------------
def call_ai(messages, tools=None, stream=False, model=MODEL_MAIN):
    return client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        stream=stream,
    )

# --------------------------------------------------
# 세션 초기화
# --------------------------------------------------
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": prompt.streamlit_prompt_01}]
    st.session_state.setdefault("phase", "start")        # 상태: start => reading
    st.session_state.setdefault("input_disabled", False) # 채팅 입력창 활성/비활성

# --------------------------------------------------
# 채팅 메시지 렌더링
# --------------------------------------------------
def render_messages():
    for msg in st.session_state.messages:
        role = msg["role"]

        if role in ("user", "assistant"):
            with st.chat_message(role):
                st.markdown(msg["content"])

        elif role == "function":
            st.markdown(msg["content"])
            render_tarot_images(msg)

# --------------------------------------------------
# 카드 이미지 렌더링
# --------------------------------------------------
def render_tarot_images(message):
    if "image_ids" not in message:
        return

    card_ids = message["image_ids"].split(",")
    cols = st.columns(3)

    for i, col in enumerate(cols):
        card = tarot_data.TAROT_CARDS[int(card_ids[i])]
        col.image(card["image_url"], width="content")
        col.markdown(
            f"**{i}. {card['name']}**  \n{card['keywords']}",
            text_alignment="center",
        )

# --------------------------------------------------
# 오프닝 멘트
# --------------------------------------------------
def opening_hook():
    if st.session_state.phase != "start": # 시작때, 한번 만!
        return

    st.session_state.phase = "reading"

    with st.chat_message("assistant"):
        stream = call_ai(
            st.session_state.messages,
            stream=True,
            model=MODEL_OPENING,
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})

# --------------------------------------------------
# Tool Dispatcher
# --------------------------------------------------
def handle_tool_calls(tool_calls):
    for call in tool_calls:
        name = call.function.name
        args = json.loads(call.function.arguments)

        # Tool 사용시
        if name == "draw_tarot_cards":
            handle_draw_tarot(call, args)

# --------------------------------------------------
# 카드 오픈 연출 처리
# --------------------------------------------------
def handle_draw_tarot(call, args):
    placeholder = st.empty()
    for i in range(10):
        placeholder.markdown(f"에너지가 모이고 있어요{'.' * i}", text_alignment="center")
        time.sleep(0.5)

    # 타로 카드 아이디 3개 가져오기
    card_ids = draw_tarot_cards(card_ids=args["card_ids"])

    # 카드 정렬 후 배치
    cols = st.columns(3)
    slots = [col.empty() for col in cols]
    content = "사용자가 선택한 카드는 "

    for i, slot in enumerate(slots):
        progress = slot.progress(0)
        for p in range(100):
            time.sleep(random.uniform(0, 0.05))
            progress.progress(p + 1)
        progress.empty()

        # 카드 뒷면 출력
        with slot.container():
            card = tarot_data.TAROT_CARDS[int(card_ids[i])]
            st.image("assets/cards/back.jpg", width="content")
            content += f"{card['name']} "

    st.session_state.messages.append({
        "role": "function",
        "tool_call_id": call.id,
        "name": call.function.name,
        "content": content,
        "image_ids": ",".join(map(str, card_ids)),
    })

    placeholder.markdown("### 잠시 숨을 고르고 리딩을 시작합니다.", text_alignment="center")
    time.sleep(random.randint(3, 5))

    # 실제 카드 오픈(앞면)
    for i, slot in enumerate(slots):
        with slot.container():
            card = tarot_data.TAROT_CARDS[int(card_ids[i])]
            st.image(card["image_url"], width="content")
            st.markdown(
                f"**{card['id']}. {card['name']}**  \n{card['keywords']}",
                text_alignment="center",
            )
            time.sleep(1)

# --------------------------------------------------
# 메인 루프
# --------------------------------------------------
def run():
    init_session()
    render_messages()
    opening_hook()

    if user_input := st.chat_input("질문을 입력하세요"):
        
        # user 입력 처리
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # tool 사용 유무
        response = call_ai(
            st.session_state.messages,
            tools=tools_,
        )
        response = response.choices[0].message

        if response.tool_calls:
            handle_tool_calls(response.tool_calls)

        # assistant 입력 처리
        with st.chat_message("assistant"):
            stream = call_ai(
                st.session_state.messages,
                stream=True,
                model=MODEL_STREAM,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --------------------------------------------------
if __name__ == "__main__":
    run()
