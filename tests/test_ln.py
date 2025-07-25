import unittest
from unittest.mock import patch, MagicMock
from mtool.ln.post import spice_up_text

class TestSpiceUpText(unittest.TestCase):
    @patch('mtool.ln.post.OpenAI')
    def test_spice_up_text(self, mock_openai):
        # Mock the client and the chat completions create method
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "This is a spiced up a post."
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        # Call the function
        result = spice_up_text("This is a test.")

        # Assert the result
        self.assertEqual(result, "This is a spiced up a post.")

        # Assert that the API was called with the correct parameters
        mock_client.chat.completions.create.assert_called_once_with(
            extra_headers={
                "HTTP-Referer": "https://github.com/search?q=repo%3AInfiniThink-Dev%2Fmtool",
                "X-Title": "mtool",
            },
            model="qwen/qwen3-235b-a22b-2507:free",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional LinkedIn writer. Given a brief summary of technical work, generate a 1-3 sentence LinkedIn post that:\n- Highlights the value of the work\n- Is easy to read\n- Sounds confident but not arrogant\n- Can include 1–2 emojis or light hashtags"
                },
                {
                    "role": "user",
                    "content": "Summary: \"This is a test.\""
                }
            ]
        )

if __name__ == '__main__':
    unittest.main()
