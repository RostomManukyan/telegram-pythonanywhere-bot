import os
import json
from datetime import datetime
from bot.clients import bot, BOT_INFO, store
from bot.config import COMMIT_SHA, HF_SPACE_ID, HOSTING_LABEL, MODEL, RATE_LIMIT
from bot.ai import ask_ai
from bot.helpers import is_allowed, keep_typing, send_reply, should_respond
from bot.history import clear_history
from bot.preferences import get_provider, set_provider
from bot.rate_limit import is_rate_limited

# Verbose console logging for local dev and teaching. Enabled by
# BOT_VERBOSE_LOG=1 (run_local.py sets this automatically). Prints one
# line per inbound/outbound message so kids and teachers can see the
# conversation flow in their terminal while the bot is running.
VERBOSE_LOG = os.environ.get("BOT_VERBOSE_LOG", "").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)


def _log(message, direction: str, text: str) -> None:
    """Print a one-line trace of a message in verbose mode.

    direction is "in" (user → bot) or "out" (bot → user). Text is
    truncated to 500 characters so long AI replies don't flood the
    terminal. Newlines are collapsed for single-line readability.
    """
    if not VERBOSE_LOG:
        return
    user = message.from_user
    user_name = (
        f"@{user.username}" if user.username else (user.first_name or f"user:{user.id}")
    )
    bot_name = f"@{BOT_INFO.username}"
    snippet = (text or "").replace("\n", " ").replace("\r", " ")
    if len(snippet) > 500:
        snippet = snippet[:500] + "..."
    if direction == "in":
        sender, receiver = user_name, bot_name
    else:
        sender, receiver = bot_name, user_name
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {sender} → {receiver}: {snippet}", flush=True)


from bot.ai import ask_ai

from bot.ai import ask_ai  # make sure correct import

#____ /start _____
@bot.message_handler(commands=["start"], func=is_allowed)
def cmd_start(message):
    prompt = """
      Generate a professional and welcoming "First Contact" message for a Telegram Programming Assistant bot.

      Tone: Senior Software Engineer, helpful, and efficient.
      
      Include:
      - A warm welcome (e.g., "System initialized. Ready to code.")
      - A brief description: "I am your AI pair-programmer. I can help you debug, refactor, explain, or write code."
      - A mention of /help for the full command list.
      Keep it concise and use Markdown (bolding/emojis) to make it readable on a mobile screen.
      """


    response = ask_ai(message.from_user.id, prompt)

    bot.send_message(message.chat.id, response)

#______ /help _______
@bot.message_handler(commands=["help"], func=is_allowed)
def cmd_help(message):
    prompt = """
      Generate a structured "Command Reference" guide for a Programming Assistant bot.

      The guide must list these commands clearly using Markdown:
      - /start - Initialize the session
      - /help - Show this menu
      - /coin - give heads or tails
      - /joke <topic> - give joke
      - /quote - give an simple quote
      - /fact - give an simple fact
      - /compliment - say a compliment
      - /roll - give number in range (1-6)
      - /magic8 - say yes/no (result is random)
      - /explain <code/topic> - Deep dive into how something works
      - /debug <code/error> - Find bugs and suggest fixes
      - /refactor <code/topic> - Improve code quality and efficiency
      - /convert <lang1> to <lang2> <code/topic> - Translate code between languages
      - /reset - Clear conversation history and start fresh
      - /about - Learn about this AI assistant
      - /model - Switch between AI providers (main/hf)
      - /remember <key> <note> - Save a technical snippet or concept
      - /recall <key> - Retrieve a saved note
      - /notes - List all saved technical notes
      - /forget <key> - Delete a saved note

      Requirements:
      - Use a "Command | Description" format.
      - Use code blocks for the commands (e.g., `/debug`).
      - Keep descriptions very short (one sentence max).
      - Group them logically (e.g., "Coding Tools", "Memory/Notes", "System").
      """

    response = ask_ai(message.from_user.id, prompt)

    bot.send_message(message.chat.id, response)

#____ /reset _______
@bot.message_handler(commands=["reset"], func=is_allowed)
def cmd_reset(message):
    clear_history(message.from_user.id)
    bot.send_message(message.chat.id, "Conversation cleared. Starting fresh!")

#_____ /joke ________
@bot.message_handler(commands=["joke"], func=is_allowed)
def cmd_joke(message):
    name = message.text.split(maxsplit=1)[1] if " " in message.text else "any you want"
    reply = ask_ai(message.from_user.id, f"Tell me short, clean joke with topic {name}.")
    bot.send_message(message.chat.id, reply)

#_____ /quote _______
@bot.message_handler(commands=["quote"], func=is_allowed)
def cmd_quote(message):
    prompt="Act as a profound philosopher and poet. Your task is to write a single, original, and highly impactful motivational sentence."
    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

#______ /fact _____
@bot.message_handler(commands=["fact"], func=is_allowed)
def cmd_fact(message):
    prompt="Tell me short, clean fact"
    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

#______ /compliment ______
@bot.message_handler(commands=["compliment"], func=is_allowed)
def cmd_compliment(message):
    prompt="Tell me short, clean complimend"
    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

#______ /roll _________
@bot.message_handler(commands=["roll"], func=is_allowed)
def cmd_roll(message):
    from random import randint as r
    num=r(1,6)
    bot.send_message(
    message.chat.id,
    f"Your number is {num}",
 )

#______ /coin _______
@bot.message_handler(commands=["coin"], func=is_allowed)
def cmd_coin(message):
    from random import randint as r
    num=r(0,1)
    if num==0:
        res="heads"
    else:
        res="tails"
    bot.send_message(
    message.chat.id,
    f"It came up {res}",
 )

#_______ /magic8 ______
@bot.message_handler(commands=["magic8"], func=is_allowed)
def cmd_magic8(message):
    from random import randint as r
    num=r(0,1)
    if num==0:
        res="yes"
    else:
        res="no"
    bot.send_message(
    message.chat.id,
    f"Magic 8 ball say {res}",
 )



#_________ /explain ___________
@bot.message_handler(commands=["explain"], func=is_allowed)
def cmd_explain(message):
      """Explains a snippet of code in detail."""
      # Usage: /explain <code snippet>
      parts = message.text.split(maxsplit=1)
      if len(parts) < 2:
          bot.send_message(message.chat.id, "Usage: /explain <code>")
          return

      code = parts[1]
      prompt = f"Act as a senior software engineer. Explain this code snippet step-by-step for a beginner:\n\n{code}"
      reply = ask_ai(message.from_user.id, prompt)
      bot.send_message(message.chat.id, reply, parse_mode="Markdown")

#____________ /debug ______________
@bot.message_handler(commands=["debug"], func=is_allowed)
def cmd_debug(message):
      """Helps find bugs in code."""
      # Usage: /debug <code>
      parts = message.text.split(maxsplit=1)
      if len(parts) < 2:
          bot.send_message(message.chat.id, "Usage: /debug <code>")
          return

      code = parts[1]
      prompt = f"Act as a debugging expert. Find the potential bugs or logical errors in this code and suggest a fix:\n\n{code}"
      reply = ask_ai(message.from_user.id, prompt)
      bot.send_message(message.chat.id, reply, parse_mode="Markdown")

#_________ /refactor _____________
@bot.message_handler(commands=["refactor"], func=is_allowed)
def cmd_refactor(message):
      """Suggests cleaner/more efficient ways to write code."""
      parts = message.text.split(maxsplit=1)
      if len(parts) < 2:
          bot.send_message(message.chat.id, "Usage: /refactor <code>")
          return

      code = parts[1]
      prompt = f"Act as a clean code expert. Refactor this code to be more efficient, readable, and follow best practices (like DRY or SOLID):\n\n{code}"
      reply = ask_ai(message.from_user.id, prompt)
      bot.send_message(message.chat.id, reply, parse_mode="Markdown")

#_________ /convert __________
@bot.message_handler(commands=["convert"], func=is_allowed)
def cmd_convert(message):
      """
      Usage: /convert <code> <from_lang> <to_lang>
      Example: /convert print("hello") python javascript
      """
      # Split the message into parts
      # parts[0] is "/convert"
      parts = message.text.split()

      # We need at least: command + code + from_lang + to_lang (4 parts minimum)
      if len(parts) < 4:
          bot.send_message(
              message.chat.id,
              "⚠️  **Invalid Usage.**\n\n"
              "**Format:** `/convert <code> <from_lang> <to_lang>`\n"
              "**Example:** `/convert print('hi') python javascript`",
              parse_mode="Markdown"
          )
          return

      # The last two elements are the languages
      to_lang = parts[-1]
      from_lang = parts[-2]

      # Everything between the command and the two languages is the code
      # We reconstruct the code by joining the middle parts
      # This handles code that contains spaces correctly
      code_parts = parts[1:-2]
      code = " ".join(code_parts)

      prompt = (
          f"Convert the following code from {from_lang} to {to_lang}. "
          "Return ONLY the resulting code block wrapped in triple backticks with the language name. "
          "Do not include any explanations or conversational text.\n\n"
          f"{code}"
      )

      try:
          reply = ask_ai(message.from_user.id, prompt)
          bot.send_message(message.chat.id, reply, parse_mode="Markdown")
      except Exception as e:
          print(f"Error in cmd_convert: {e}")
          bot.send_message(message.chat.id, "❌ An error occurred during conversion.")


#______ /remember _______
@bot.message_handler(commands=["remember"], func=is_allowed)
def cmd_remember(message):
    parts = message.text.split(maxsplit=2)

    if len(parts) < 3:
        bot.send_message(
            message.chat.id,
            "Usage: /remember <key> <note>"
        )
        return

    key = parts[1]
    note = parts[2]

    notes = store.get(f"notes:{message.from_user.id}")

    if notes:
        notes = json.loads(notes)
    else:
        notes = {}

    notes[key] = note

    store.set(
        f"notes:{message.from_user.id}",
        json.dumps(notes)
    )

    bot.send_message(
        message.chat.id,
        f"Saved note under key '{key}'"
    )

#_______ /recall ________
@bot.message_handler(commands=["recall"], func=is_allowed)
def cmd_recall(message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        bot.send_message(
            message.chat.id,
            "Usage: /recall <key>"
        )
        return

    key = parts[1]

    notes = store.get(f"notes:{message.from_user.id}")

    if notes:
        notes = json.loads(notes)
    else:
        notes = {}

    if key in notes:
        bot.send_message(
            message.chat.id,
            f"{key}: {notes[key]}"
        )
    else:
        bot.send_message(
            message.chat.id,
            f"No note found with key '{key}'"
        )

#_________ /notes _________
@bot.message_handler(commands=["notes"], func=is_allowed)
def cmd_notes(message):
    notes = store.get(f"notes:{message.from_user.id}")

    if not notes:
        bot.send_message(
            message.chat.id,
            "No notes saved."
        )
        return

    notes = json.loads(notes)

    if not notes:
        bot.send_message(
            message.chat.id,
            "No notes saved."
        )
        return

    keys = "\n".join(notes.keys())

    bot.send_message(
        message.chat.id,
        f"Saved keys:\n{keys}"
    )

#_________ /forget ____________
@bot.message_handler(commands=["forget"], func=is_allowed)
def cmd_forget(message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        bot.send_message(
            message.chat.id,
            "Usage: /forget <key>"
        )
        return

    key = parts[1]

    notes = store.get(f"notes:{message.from_user.id}")

    if not notes:
        bot.send_message(
            message.chat.id,
            "No notes saved."
        )
        return

    notes = json.loads(notes)

    if key not in notes:
        bot.send_message(
            message.chat.id,
            f"No note found with key '{key}'."
        )
        return

    del notes[key]

    store.set(
        f"notes:{message.from_user.id}",
        json.dumps(notes)
    )

    bot.send_message(
        message.chat.id,
        f"Forgot note '{key}'."
    )

#_______ /roast _________
@bot.message_handler(commands=["roast"], func=is_allowed)
def cmd_roast(message):
    name = message.text.split(maxsplit=1)[1] if " " in message.text else "you"
    reply = ask_ai(message.from_user.id, f"Write a short, playful, friendly roast of {name}.")
    bot.send_message(message.chat.id, reply)

  # ______ /about ________
@bot.message_handler(commands=["about"], func=is_allowed)
def cmd_about(message):
      prompt = """
        Generate an "About" message for a high-end AI Programming Assistant.

        Include:
        - The Mission: To act as a 24/7 pair-programmer for developers of all levels.
        - The Tech: Mention it uses advanced Large Language Models (LLMs) to understand complex logic and syntax.
        - The Philosophy: Focus on clean code, security, and learning rather than just "copy-pasting."
        - A closing encouraging line (e.g., "Happy coding! 🚀").

        Tone: Sophisticated, tech-forward, and reliable.
        Format: Use Markdown for a clean, professional look. Keep it under 150 words.
        """

      response = ask_ai(message.from_user.id, prompt)
      bot.send_message(message.chat.id, response)

  # <--- MAKE SURE THERE ARE NO SPACES BEFORE THE LINE BELOW --->
@bot.message_handler(commands=["model"], func=is_allowed)
def cmd_model(message):
      parts = (message.text or "").split(maxsplit=1)
      if len(parts) == 1:
          current = get_provider(message.from_user.id)
          bot.send_message(
              message.chat.id,
              f"Current provider: {current}\n\n"
              "Options:\n"
              "/model main — Cerebras (fast, multilingual, with memory)\n"
              "/model hf — ArmGPT (Armenian only, slow, no memory)",
          )
          return
      choice = parts[1].strip().lower()
      if choice not in ("main", "hf"):
          bot.send_message(
              message.chat.id, "Invalid choice. Use: /model main or /model hf"
          )
          return
      if not set_provider(message.from_user.id, choice):
          bot.send_message(
              message.chat.id, "Could not save preference. Try again later."
          )
          return
      if choice == "hf":
          bot.send_message(
              message.chat.id,
              "Switched to hf (ArmGPT).\n\n"
              "Note: this is a tiny base completion model trained only on Armenian text. "
              "It will continue whatever you write rather than answer questions, "
              "and it does not understand English. Replies take ~30-60s and there is no memory.",
          )
      else:
          bot.send_message(message.chat.id, "Switched to Main Provider.")

@bot.message_handler(content_types=["text"], func=is_allowed)
def handle_message(message):
    if not should_respond(message):
        return
    text = (message.text or "").replace(f"@{BOT_INFO.username}", "").strip()
    if not text:
        # Edited messages, forwards, or stickers-with-empty-caption can
        # arrive with no usable text. Don't burn rate-limit / AI calls on them.
        return
    _log(message, "in", text)
    if is_rate_limited(message.from_user.id):
        limit_msg = f"You've reached the daily limit of {RATE_LIMIT} messages. Try again tomorrow."
        bot.send_message(message.chat.id, limit_msg)
        _log(message, "out", f"[rate limited] {limit_msg}")
        return
    try:
        with keep_typing(message.chat.id):
            reply = ask_ai(message.from_user.id, text)
        send_reply(message, reply)
        _log(message, "out", reply)
    except Exception as e:
        print(f"Error in handle_message: {e}")
        bot.send_message(message.chat.id, "Something went wrong. Please try again.")
        _log(message, "out", f"[error] {e}")
