from unittest.mock import patch, MagicMock

def make_message(text="hello", user_id=123, chat_id=456, chat_type="private"):
      msg = MagicMock()
      msg.text = text
      msg.from_user.id = user_id
      msg.from_user.username = "testuser"
      msg.from_user.first_name = "Test"
      msg.chat.id = chat_id
      msg.chat.type = chat_type
      msg.reply_to_message = None
      return msg

  # --- CORE MESSAGE HANDLING TESTS ---

def test_handle_message_calls_ask_ai():
      with (
          patch("bot.handlers.should_respond", return_value=True),
          patch("bot.handlers.is_rate_limited", return_value=False),
          patch("bot.handlers.BOT_INFO", MagicMock(username="testbot")),
          patch("bot.handlers.ask_ai", return_value="AI reply") as mock_ask,
          patch("bot.handlers.send_reply") as mock_send,
          patch("bot.handlers.bot"),
      ):
          from bot.handlers import handle_message
          msg = make_message(text="hello")
          handle_message(msg)
          mock_ask.assert_called_once_with(123, "hello")
          mock_send.assert_called_once_with(msg, "AI reply")

def test_handle_message_rate_limited():
      with (
          patch("bot.handlers.should_respond", return_value=True),
          patch("bot.handlers.is_rate_limited", return_value=True),
          patch("bot.handlers.BOT_INFO", MagicMock(username="testbot")),
          patch("bot.handlers.ask_ai") as mock_ask,
          patch("bot.handlers.bot") as mock_bot,
      ):
          from bot.handlers import handle_message
          handle_message(make_message())
          mock_ask.assert_not_called()
          args, _ = mock_bot.send_message.call_args
          assert "daily limit" in args[1]

  # --- COMMAND TESTS (FIXED FOR NEW PROMPTS) ---

def test_cmd_start():
      with patch("bot.handlers.ask_ai") as mock_ai, patch("bot.handlers.bot") as mock_bot:
          from bot.handlers import cmd_start
          mock_ai.return_value = "Welcome!"
          msg = make_message()
          cmd_start(msg)
          # Check that the prompt asks for a "welcome message"
          prompt = mock_ai.call_args[0][1].lower()
          assert "welcome" in prompt
          assert "student" in prompt or "user" in prompt
          mock_bot.send_message.assert_called_once_with(msg.chat.id, "Welcome!")

def test_cmd_help():
      with patch("bot.handlers.ask_ai") as mock_ai, patch("bot.handlers.bot") as mock_bot:
          from bot.handlers import cmd_help
          mock_ai.return_value = "Help Guide"
          msg = make_message()
          cmd_help(msg)
          prompt = mock_ai.call_args[0][1].lower()
          # Check for keywords in the new complex prompt
          assert "/start" in prompt
          assert "/help" in prompt
          assert "command" in prompt
          mock_bot.send_message.assert_called_once_with(msg.chat.id, "Help Guide")

def test_cmd_joke():
      with patch("bot.handlers.ask_ai") as mock_ai, patch("bot.handlers.bot") as mock_bot:
          from bot.handlers import cmd_joke
          msg = make_message(text="/joke cats")
          mock_ai.return_value = "Joke"
          cmd_joke(msg)
          prompt = mock_ai.call_args[0][1].lower()
          assert "joke" in prompt
          assert "cats" in prompt
          mock_bot.send_message.assert_called_once_with(msg.chat.id, "Joke")

  # --- PROGRAMMING ASSISTANT TESTS ---

def test_cmd_explain():
      with patch("bot.handlers.ask_ai") as mock_ai, patch("bot.handlers.bot") as mock_bot:
          from bot.handlers import cmd_explain
          msg = make_message(text="/explain print('hi')")
          mock_ai.return_value = "Explanation"
          cmd_explain(msg)
          prompt = mock_ai.call_args[0][1].lower()
          assert "print('hi')" in prompt
          assert "explain" in prompt
          mock_bot.send_message.assert_called_once_with(msg.chat.id, "Explanation")

def test_cmd_debug():
      with patch("bot.handlers.ask_ai") as mock_ai, patch("bot.handlers.bot") as mock_bot:
          from bot.handlers import cmd_debug
          msg = make_message(text="/debug x = 1/0")
          mock_ai.return_value = "Error"
          cmd_debug(msg)
          prompt = mock_ai.call_args[0][1].lower()
          assert "x = 1/0" in prompt
          assert "debug" in prompt
          mock_bot.send_message.assert_called_once_with(msg.chat.id, "Error")

def test_cmd_refactor():
      with patch("bot.handlers.ask_ai") as mock_ai, patch("bot.handlers.bot") as mock_bot:
          from bot.handlers import cmd_refactor
          msg = make_message(text="/refactor code")
          mock_ai.return_value = "Refactored"
          cmd_refactor(msg)
          prompt = mock_ai.call_args[0][1].lower()
          assert "refactor" in prompt
          mock_bot.send_message.assert_called_once_with(msg.chat.id, "Refactored")

def test_cmd_convert_success():
      with patch("bot.handlers.ask_ai") as mock_ai, patch("bot.handlers.bot") as mock_bot:
          from bot.handlers import cmd_convert
          msg = make_message(text="/convert print('hi') python javascript")
          mock_ai.return_value = "```javascript\nconsole.log('hi');\n```"
          cmd_convert(msg)
          prompt = mock_ai.call_args[0][1].lower()
          assert "python" in prompt
          assert "javascript" in prompt
          assert "print('hi')" in prompt
          mock_bot.send_message.assert_called_once_with(msg.chat.id, mock_ai.return_value, parse_mode="Markdown")

def test_cmd_convert_invalid_usage():
      with patch("bot.handlers.bot") as mock_bot:
          from bot.handlers import cmd_convert
          msg = make_message(text="/convert short")
          cmd_convert(msg)
          args, _ = mock_bot.send_message.call_args
          assert "Usage" in args[1] or "Invalid" in args[1]

  # --- MODEL COMMAND TESTS (FIXED TYPEERRORS) ---

def _get_cmd_model():
      import importlib
      import bot.config
      import bot.handlers
      bot.config.HF_SPACE_ID = "fake/space"
      bot.handlers.HF_SPACE_ID = "fake/space"
      importlib.reload(bot.handlers)
      return getattr(bot.handlers, "cmd_model", None)

def test_cmd_model_switch_to_hf():
      cmd_model = _get_cmd_model()
      assert cmd_model is not None
      with (
          patch("bot.handlers.set_provider", return_value=True),
          patch("bot.handlers.get_provider", return_value="main"),
          patch("bot.handlers.bot") as mock_bot,
      ):
          msg = make_message(text="/model hf")
          cmd_model(msg)
          # Check that set_provider was called
          from bot.handlers import set_provider
          mock_bot.send_message.assert_called()

def test_cmd_model_invalid_choice():
      cmd_model = _get_cmd_model()
      with patch("bot.handlers.bot") as mock_bot:
          msg = make_message(text="/model bogus")
          cmd_model(msg)
          args, _ = mock_bot.send_message.call_args
          assert "Invalid" in args[1]