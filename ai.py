import logging
from collections import defaultdict, deque

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL, SHOP_NAME
from faq import faq_as_text

log = logging.getLogger(__name__)

ORDER_MARKER = "[ORDER]"

SYSTEM_PROMPT = f"""Ты — вежливый консультант интернет-магазина «{SHOP_NAME}».
Магазин продаёт автооптику (фары, фонари, ПТФ) и кузовные детали (бамперы, капоты, крылья,
двери, зеркала, решётки) для китайских автомобилей.

Правила:
- Отвечай кратко (до 5–6 предложений), по-русски, или на языке клиента.
- Опирайся на FAQ ниже. Не выдумывай цены, наличие и сроки — говори, что их уточнит менеджер.
- Не отвечай на темы, не связанные с магазином и автозапчастями; мягко возвращай к теме.
- Если клиент хочет купить, заказать, узнать цену или наличие конкретной детали —
  в самом конце ответа добавь отдельной строкой маркер {ORDER_MARKER}.
- Для подбора детали полезен VIN-код, марка, модель, год.

FAQ магазина:
{faq_as_text()}
"""

client = genai.Client(api_key=GEMINI_API_KEY)

# Короткая история диалога на пользователя (в памяти, сбрасывается при рестарте)
_history: dict[int, deque] = defaultdict(lambda: deque(maxlen=10))


async def ask(user_id: int, text: str) -> tuple[str, bool]:
    """Возвращает (ответ, хочет_ли_клиент_оформить_заказ)."""
    history = _history[user_id]
    history.append(types.Content(role="user", parts=[types.Part(text=text)]))
    try:
        response = await client.aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=list(history),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.4,
                max_output_tokens=800,
                # Не держим клиента дольше ~30 с, если Gemini завис
                http_options=types.HttpOptions(
                    timeout=30000, retry_options=types.HttpRetryOptions(attempts=2)
                ),
            ),
        )
        answer = (response.text or "").strip()
    except Exception:
        log.exception("Gemini error")
        history.pop()
        return "Извините, сейчас не могу ответить. Попробуйте позже или оформите заявку — менеджер свяжется с вами.", True

    wants_order = ORDER_MARKER in answer
    answer = answer.replace(ORDER_MARKER, "").strip() or "Оформите заявку — менеджер всё уточнит."
    history.append(types.Content(role="model", parts=[types.Part(text=answer)]))
    return answer, wants_order
