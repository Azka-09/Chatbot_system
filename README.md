# 🤖 Mini GPT

A ChatGPT-style assistant built with **Streamlit** and **LangChain**, featuring a premium royal-blue / deep-navy interface and an API-key-first welcome screen.

## Features

- **API-key-first welcome screen**: the chat stays hidden until your OpenAI key is entered and verified.
- **Key verification**: the key is checked against OpenAI with a loading spinner and friendly error messages.
- **Secure handling**: the key lives only in the Streamlit session. It is never written to disk, put in URLs, or shown in error messages.
- **Polished chat workspace**: rounded message bubbles, timestamps, a typing indicator, and a pinned input bar.
- **Chat history**: create new chats, switch between them, or clear them all.
- **Suggested prompts** on an empty conversation.
- **Settings**: choose the model (`gpt-4.1-mini` or `gpt-4.1`) and edit the assistant instructions.
- **Update or disconnect your key** anytime from the sidebar.
- **Responsive and accessible**: works on desktop and mobile, with scrollable code blocks and support for the reduced-motion setting.

## Project structure

```
.
├── app.py             # The whole application (UI, styling, chat logic)
├── requirements.txt   # Python dependencies
└── README.md
```

## Requirements

- Python 3.9 or newer
- An [OpenAI API key](https://platform.openai.com/api-keys) with billing enabled

## Getting started

1. **(Optional) create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**

   ```bash
   streamlit run app.py
   ```

4. Open the URL shown in the terminal (usually http://localhost:8501), paste your API key, and click **Connect and Continue**.

## Usage

| Action | How |
| --- | --- |
| Start chatting | Type in the input bar, or click a suggested prompt |
| New conversation | Sidebar → **New chat** |
| Switch conversation | Click it under **Chat history** |
| Change model or instructions | Sidebar → **Settings** |
| Update your key | Sidebar → **API key** → enter the new key → **Update key** |
| Sign out | Sidebar → **API key** → **Disconnect** |

## Security notes

- The key is kept in `st.session_state` for the current browser session only.
- Refreshing the page or closing the tab ends the session, so you will be asked for the key again.
- Never commit a real API key to the repository.
- Error messages are deliberately generic so they cannot leak key fragments.

## Troubleshooting

- **"That API key wasn't accepted"**: check for typos or extra spaces, and confirm the key is active.
- **Rate limit or quota error**: check your billing and usage limits in the OpenAI dashboard.
- **"Couldn't reach OpenAI"**: check your internet connection or proxy settings.
- **Key rejected although it is valid**: verification calls the model-list endpoint, so keys restricted to specific endpoints may fail the check.
- **Styles look off after upgrading Streamlit**: the custom CSS targets Streamlit's internal element IDs, which can change between versions.

## Tech stack

- [Streamlit](https://streamlit.io/): UI framework
- [LangChain](https://python.langchain.com/) (`langchain-core`, `langchain-openai`): message handling and model calls
- [OpenAI Python SDK](https://github.com/openai/openai-python): key verification and error types
