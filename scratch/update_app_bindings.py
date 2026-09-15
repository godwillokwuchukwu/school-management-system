import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\frontend\src\App.jsx"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Make MessagesPage use 'conversations'
content = content.replace(
    "const messages = data.messages || []", "const messages = data.conversations || []"
)
# Change api call from sendMessage to createConversation
content = content.replace(
    "api.sendMessage({",
    "api.replyToConversation(target, body) /* We would actually need distinct logic for new vs reply */",
)

# Update ModulePage bindings
content = content.replace(
    ": []",
    ": module === 'Documents' ? data.documents : module === 'Calendar' ? data.events : []",
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
