import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\frontend\src\App.jsx"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# add import ActivateFlow
content = content.replace(
    "import AuthFlow from './AuthFlow'",
    "import AuthFlow from './AuthFlow'\nimport ActivateFlow from './ActivateFlow'",
)

# replace the !loggedIn block
old_block = """  if (!loggedIn) {
    return (
      <AuthFlow
        initialMode={authMode}
        onAuthenticated={(session) => {
          setRole(session.role || 'student')
          setLoggedIn(true)
        }}
      />
    )
  }"""

new_block = """  if (!loggedIn) {
    const params = new URLSearchParams(window.location.search)
    const token = params.get('activate_token')
    
    if (token) {
      return (
        <ActivateFlow 
          token={token} 
          onActivated={() => {
            window.location.href = '/portal'
          }} 
        />
      )
    }

    return (
      <AuthFlow
        initialMode={authMode}
        onAuthenticated={(session) => {
          setRole(session.role || 'student')
          setLoggedIn(true)
        }}
      />
    )
  }"""

content = content.replace(old_block, new_block)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
