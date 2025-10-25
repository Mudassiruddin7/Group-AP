# ChatGPT-Style Interface Guide

## Overview
The F2 Portfolio AI now features a ChatGPT-style conversational interface with efficient token usage and intelligent query routing.

## Key Features

### 1. **Smart Conversation Flow**
- Maintains chat history with context-aware responses
- Automatically limits context to last 10 messages for efficiency
- Clean, intuitive message display with user/assistant avatars

### 2. **Intelligent Query Classification**
The AI automatically detects three types of queries:

#### General Chat
- **Triggers**: Simple greetings like "hi", "hello", "hey"
- **Behavior**: Warm, conversational responses without portfolio generation
- **Example**: 
  - User: "hi"
  - AI: "Hello! I'm F2 Portfolio AI, your investment advisor assistant..."

#### Research Queries
- **Triggers**: Keywords like "research", "tell me about", "what is", "explain"
- **Behavior**: Detailed educational responses about stocks, concepts, or strategies
- **Token Limit**: 600 tokens for efficient responses (300-400 words)
- **Example**:
  - User: "research about Tesla stock"
  - AI: Provides company fundamentals, market position, and investment considerations

#### Portfolio Requests
- **Triggers**: Age mentions, risk keywords, investment terms
- **Behavior**: Full portfolio optimization with visualizations
- **Example**:
  - User: "I'm 20 with medium risk"
  - AI: Generates complete portfolio with metrics and charts

### 3. **Token Optimization**
To minimize API costs while maintaining quality:

- **Chat responses**: 200 tokens max (2-3 sentences)
- **Research responses**: 600 tokens max (300-400 words)
- **Portfolio explanations**: 1000 tokens (detailed but focused)
- **Context pruning**: Only last 5 messages for chat, 3 for research, 10 for portfolio

### 4. **Visual Enhancements**

#### Message Display
- User messages: Avatar 👤, light gray background
- AI messages: Avatar 🤖, white background
- Smooth transitions and hover effects

#### Portfolio Metrics
Displayed as compact cards:
- 📈 Expected Return
- 📊 Volatility (Risk)
- ⚡ Sharpe Ratio
- 🎯 Number of Holdings

#### Charts
Collapsed by default to save space:
- Allocation pie chart
- Sector distribution bar chart

### 5. **User Controls**
- **Clear Chat**: Button to reset conversation history
- **Message Persistence**: All messages stay visible in conversation
- **Expandable Charts**: Toggle portfolio visualizations on demand

## Usage Examples

### Example 1: Casual Greeting
```
User: hi
AI: Hello! I'm F2 Portfolio AI, your friendly investment advisor assistant. 
I'm here to help you navigate the world of investments. How can I assist 
you today?
```

### Example 2: Age-Based Portfolio
```
User: im 20 what about u?
AI: [Detects age 20 → Generates medium risk, 15-year horizon portfolio]
Great to connect with you! At 20, with a 15-year investment horizon, 
you're in an excellent position to build long-term wealth...

📈 Return: 52.3% | 📊 Volatility: 14.9% | ⚡ Sharpe: 3.24 | 🎯 Holdings: 4
[Expandable charts showing allocation]
```

### Example 3: Research Query
```
User: research about Apple stock
AI: Apple Inc. (AAPL) is one of the world's most valuable companies, 
known for its innovative consumer electronics, software, and services...
[300-400 word detailed analysis]

💡 Note: This is general educational information. Consult a licensed 
financial advisor for specific investment decisions.
```

### Example 4: Follow-up Question
```
User: what's the sharpe ratio?
AI: The Sharpe Ratio is a financial metric that measures risk-adjusted 
returns. It's calculated by subtracting the risk-free rate from the 
expected return and dividing by volatility. A higher ratio indicates 
better return per unit of risk taken.
```

## Technical Implementation

### Context Management
```python
# Only send last 10 messages to save tokens
recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
```

### Message Structure
```python
{
    "role": "user" | "assistant",
    "content": "message text",
    "has_portfolio": True | False  # For visualization tracking
}
```

### Intent Classification
```python
# In agent_cerebras.py
query_intent = _classify_query_intent(user_query, chat_history)
# Returns: "general_chat" | "research" | "portfolio_request"
```

## Performance Metrics

### Token Usage Comparison
| Query Type | Old Usage | New Usage | Savings |
|------------|-----------|-----------|---------|
| Chat | ~300 tokens | ~200 tokens | 33% ↓ |
| Research | ~800 tokens | ~600 tokens | 25% ↓ |
| Portfolio | ~1200 tokens | ~1000 tokens | 17% ↓ |

### Response Times
- Chat: < 2 seconds
- Research: 2-4 seconds
- Portfolio: 5-8 seconds (includes optimization)

## Best Practices

### For Users
1. **Be specific**: "I'm 30, need low risk for 5 years" works better than vague requests
2. **Use keywords**: Start with "research" for informational queries
3. **Ask follow-ups**: The AI remembers context from previous messages
4. **Clear when needed**: Use the Clear Chat button to start fresh topics

### For Developers
1. **Monitor token usage**: Check Cerebras dashboard for API consumption
2. **Adjust max_tokens**: Modify in agent_cerebras.py if responses are too short/long
3. **Context window**: Increase history limit (currently 10) if more context is needed
4. **Add streaming**: Implement token-by-token streaming for better UX (future enhancement)

## Troubleshooting

### Issue: AI not detecting age
**Solution**: Be explicit with age mentions
- ✅ "I'm 25", "im 30", "age 40"
- ❌ "quarter century old", "almost thirty"

### Issue: Portfolio generated for simple questions
**Solution**: Avoid investment keywords in casual questions
- ✅ "hello, how are you?"
- ❌ "hi, i have some risk questions" (triggers portfolio)

### Issue: Chat history growing too large
**Solution**: Click "Clear Chat" button or refresh the page

## Future Enhancements
- [ ] Real-time streaming responses (token-by-token display)
- [ ] Voice input/output integration
- [ ] Multi-turn portfolio refinement
- [ ] Export chat history as PDF
- [ ] Sentiment analysis of user queries
- [ ] RAG (Retrieval Augmented Generation) with live market data

## API Reference

### Key Functions

#### `show_ai_chat()`
Main chat interface in `app.py`. Handles message display and user input.

#### `process_query(user_query, chat_history)`
Core agent method in `agent_cerebras.py`. Routes queries and generates responses.

#### `_classify_query_intent(user_query, chat_history)`
Determines if query is chat, research, or portfolio request.

#### `_handle_general_chat(user_query, chat_history)`
Processes conversational queries with 200 token limit.

#### `_handle_research_query(user_query, chat_history)`
Processes research queries with 600 token limit.

## Configuration

### Modify Token Limits
Edit `agent_cerebras.py`:
```python
# For chat responses
max_tokens=200  # Increase if responses too brief

# For research
max_tokens=600  # Increase for more detailed answers

# For portfolio explanations
max_tokens=1000  # Increase for longer explanations
```

### Modify Context Window
Edit `app.py`:
```python
# Currently sends last 10 messages
recent_history = st.session_state.chat_history[-10:]

# Change to 20 for more context (uses more tokens):
recent_history = st.session_state.chat_history[-20:]
```

## Credits
- **AI Model**: Cerebras Llama 3.3 70B
- **Interface**: Streamlit 1.32+
- **Optimization**: PyPortfolioOpt 1.5+
- **Data**: 27 stocks, 9 sectors, 35K+ price records

---

**Note**: This interface is optimized for educational use. For production deployment, implement rate limiting, error handling, and cost monitoring.
