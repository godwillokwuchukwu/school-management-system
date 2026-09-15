import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\frontend\src\App.jsx"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

chatbot_component = """
function AIChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState([{ sender: 'ai', text: 'Hi! I am your AI Assistant. How can I help you today?' }])
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (!prompt.trim()) return
    
    const userMessage = { sender: 'user', text: prompt }
    setMessages((prev) => [...prev, userMessage])
    setPrompt('')
    setLoading(true)
    
    try {
      const data = await api.aiChatbot(userMessage.text)
      setMessages((prev) => [...prev, { sender: 'ai', text: data.response }])
    } catch (err) {
      setMessages((prev) => [...prev, { sender: 'ai', text: 'Error connecting to the assistant.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <button 
        className="primary-button" 
        style={{ position: 'fixed', bottom: '2rem', right: '2rem', zIndex: 9999, borderRadius: '50px', padding: '1rem' }}
        onClick={() => setIsOpen(true)}
        aria-label="Open AI Assistant"
      >
        <Icon name="messages" /> Ask AI
      </button>

      {isOpen && (
        <div className="modal-backdrop" style={{ zIndex: 10000 }}>
          <section className="modal" style={{ width: '400px', height: '500px', display: 'flex', flexDirection: 'column' }}>
            <button className="modal-close" onClick={() => setIsOpen(false)} aria-label="Close">
              <Icon name="close" />
            </button>
            <p className="eyebrow">RIVERSIDE ACADEMY</p>
            <h2>AI Assistant</h2>
            
            <div style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem', border: '1px solid #ddd', padding: '1rem', borderRadius: '4px' }}>
              {messages.map((m, i) => (
                <div key={i} style={{ marginBottom: '1rem', textAlign: m.sender === 'user' ? 'right' : 'left' }}>
                  <span style={{ 
                    display: 'inline-block',
                    padding: '0.5rem 1rem', 
                    borderRadius: '20px', 
                    background: m.sender === 'user' ? '#000' : '#f0f0f0',
                    color: m.sender === 'user' ? '#fff' : '#000',
                  }}>
                    {m.text}
                  </span>
                </div>
              ))}
              {loading && <div style={{ textAlign: 'left' }}><span style={{ display: 'inline-block', padding: '0.5rem', background: '#f0f0f0', borderRadius: '20px' }}>...</span></div>}
            </div>

            <form onSubmit={submit} style={{ display: 'flex', gap: '0.5rem' }}>
              <input 
                type="text" 
                value={prompt} 
                onChange={e => setPrompt(e.target.value)} 
                placeholder="Ask a question..." 
                style={{ flex: 1, padding: '0.5rem' }} 
              />
              <button className="primary-button" disabled={loading}>Send</button>
            </form>
          </section>
        </div>
      )}
    </>
  )
}
"""

content = content.replace(
    "export default App", chatbot_component + "\nexport default App"
)

# Render the widget inside App component
content = content.replace(
    "      {api.isAuthenticated() ? (",
    "      <AIChatbotWidget />\n      {api.isAuthenticated() ? (",
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
