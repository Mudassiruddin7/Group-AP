# Quick Start Guide - ChatGPT Interface

## Launch the App

```bash
streamlit run app.py
```

Navigate to: **http://localhost:8502**

---

## 🎯 Example Conversations

### Conversation 1: Casual Introduction
```
👤 You: hi

🤖 AI: Hello! I'm F2 Portfolio AI, your friendly investment advisor 
      assistant. I'm here to help you navigate the world of investments 
      and achieve your financial goals. How can I assist you today?
```
**Result**: Quick greeting, no portfolio generation (saves tokens)

---

### Conversation 2: Age-Based Portfolio
```
👤 You: im 20 what about u?

🤖 AI: Great to connect with you! At 20, with a 15-year investment 
      horizon, you're in an excellent position to build long-term wealth.
      Your medium risk profile allows us to focus on growth while still 
      being mindful of potential market fluctuations.

      This portfolio is tailored to your needs, with a mix of stocks 
      that provide a balance of growth and stability. For example, 
      Apple (AAPL) gives you exposure to the tech sector...

      📈 Return: 52.3%
      📊 Volatility: 14.9%
      ⚡ Sharpe: 3.24
      🎯 Holdings: 4

      [📊 View Portfolio Charts ▼]
```
**Result**: Detected age 20 → Generated 15-year portfolio automatically

---

### Conversation 3: Research Query
```
👤 You: research about Apple stock

🤖 AI: Apple Inc. (AAPL) is one of the world's most valuable companies,
      known for its innovative consumer electronics, software, and 
      services.

      Company Fundamentals:
      • Market Cap: ~$3 trillion
      • Sector: Technology / Consumer Electronics
      • Key Products: iPhone, iPad, Mac, Apple Watch, AirPods

      Investment Considerations:
      • Strong brand loyalty and ecosystem
      • Consistent innovation and product development
      • High profit margins and cash flow generation

      Risks:
      • Heavy dependence on iPhone sales (~50% of revenue)
      • Market saturation in developed countries
      • Regulatory scrutiny on App Store practices

      💡 Note: This is general educational information. For specific 
      investment decisions, please consult a licensed financial advisor.
```
**Result**: Educational research response, no portfolio generated

---

### Conversation 4: Explicit Portfolio Request
```
👤 You: I want a medium risk portfolio for 10 years

🤖 AI: Great to connect with you. With a 10-year horizon and a medium 
      risk tolerance, you're in an excellent position to build long-term 
      wealth while balancing growth and preservation...

      Your medium risk portfolio is carefully constructed with stocks 
      like Netflix (NFLX) for entertainment sector exposure, and 
      Cal-Maine (CALM) for agricultural stability...

      📈 Return: 52.3%
      📊 Volatility: 14.9%
      ⚡ Sharpe: 3.24
      🎯 Holdings: 4

      [📊 View Portfolio Charts ▼]
```
**Result**: Full portfolio optimization with visualizations

---

### Conversation 5: Follow-up Question
```
👤 You: what's the sharpe ratio?

🤖 AI: The Sharpe Ratio is a financial metric that measures risk-adjusted
      returns. It's calculated by subtracting the risk-free rate from 
      the expected return and dividing by volatility. A higher ratio 
      indicates better return per unit of risk taken.
```
**Result**: Quick educational response using conversation context

---

## 🎨 Interface Features

### Message Display
- **User messages**: 👤 avatar, light gray background
- **AI messages**: 🤖 avatar, white background
- **Smooth scrolling**: Auto-scroll to latest message

### Portfolio Metrics (When Generated)
Displayed as 4 compact cards:
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 📈 Return    │ 📊 Volatility│ ⚡ Sharpe    │ 🎯 Holdings  │
│   52.3%      │   14.9%      │   3.24       │   4          │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

### Charts (Collapsible)
Click "📊 View Portfolio Charts" to expand:
- **Left**: Allocation pie chart (% per stock)
- **Right**: Sector distribution bar chart

---

## 🗑️ Clear Chat Feature

Located in top-right corner of AI Chat tab:

```
┌────────────────────────────────────────────────────────┐
│ 💬 Chat with F2 Portfolio AI        [🗑️ Clear Chat] │
├────────────────────────────────────────────────────────┤
│ Ask about investments, research companies, or get      │
│ personalized portfolio recommendations                 │
└────────────────────────────────────────────────────────┘
```

**Click to**: Reset conversation and start fresh

---

## 💡 Pro Tips

### 1. **For Fast Responses**
Keep queries simple:
- ✅ "hi"
- ✅ "what is diversification?"
- ✅ "explain the Sharpe ratio"

### 2. **For Portfolio Generation**
Mention age or risk:
- ✅ "im 30"
- ✅ "medium risk, 10 years"
- ✅ "conservative portfolio for retirement"

### 3. **For Research**
Start with "research":
- ✅ "research about Tesla"
- ✅ "research sector allocation"
- ✅ "research dividend stocks"

### 4. **Multi-Turn Conversations**
The AI remembers context:
```
👤 You: im 25
🤖 AI: [generates portfolio]

👤 You: make it more aggressive
🤖 AI: [generates high-risk portfolio, remembers age 25]
```

---

## 🔧 Customization

### Want Longer Responses?
Edit `agent_cerebras.py`:

```python
# Line ~463 (Chat responses)
max_tokens=200  # Change to 300 for longer chat

# Line ~510 (Research)
max_tokens=600  # Change to 800 for more detail
```

### Want More Context History?
Edit `app.py`:

```python
# Line ~117
recent_history = st.session_state.chat_history[-10:]
# Change -10 to -20 for more context (uses more tokens)
```

---

## 📊 Token Usage Monitor

Watch the terminal output when running queries:

```bash
INFO:agent_cerebras:Handling general chat query
INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions
# Token usage automatically logged by Cerebras SDK
```

Check your Cerebras dashboard for detailed usage:
- https://cloud.cerebras.ai/dashboard

---

## ⚠️ Important Notes

1. **This is educational software** - Not financial advice
2. **API costs apply** - Monitor Cerebras usage
3. **Chat history** - Cleared on page refresh
4. **Portfolio data** - Based on historical prices (not live)

---

## 🆘 Troubleshooting

### AI Not Responding
1. Check terminal for errors
2. Verify Cerebras API key in `.env`
3. Ensure internet connection

### Portfolio Not Generating
1. Mention age or risk explicitly
2. Try: "I'm 30 with medium risk"
3. Avoid vague requests

### Charts Not Showing
1. Generate a portfolio first
2. Click "📊 View Portfolio Charts" expander
3. Refresh page if stuck

---

## 📚 Additional Resources

- **Full Documentation**: `CHAT_INTERFACE_GUIDE.md`
- **Enhancement Summary**: `CHATGPT_ENHANCEMENT_SUMMARY.md`
- **Architecture**: `ARCHITECTURE.md`
- **Code Tests**: `test_chat_interface.py`

---

## 🚀 Quick Test

Run the test script:
```bash
python test_chat_interface.py
```

Expected output:
```
✅ TEST 1: Greeting → Chat Response
✅ TEST 2: Age mention → Portfolio
✅ TEST 3: Research → Detailed analysis
✅ TEST 4: Portfolio → Medium risk
✅ TEST 5: Follow-up → Sharpe explanation

✅ CHAT INTERFACE TEST COMPLETE
Total messages: 10
```

---

**Ready to go!** Launch the app and start chatting with F2 Portfolio AI! 🎉
