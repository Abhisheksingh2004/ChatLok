let currentFile = null;

const fileInput = document.getElementById('fileInput');
const fileDropZone = document.getElementById('fileDropZone');
const fileUploadContainer = document.getElementById('fileUploadContainer');
const chatSection = document.getElementById('chatSection');
const fileName = document.getElementById('fileName');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const loadingIndicator = document.getElementById('loadingIndicator');

document.addEventListener('DOMContentLoaded', initializeApp);

async function initializeApp() {
  try {
    const response = await fetch('/get_chat_history');
    const result = await response.json();
    if (result.success) {
      (result.chat_history || []).forEach(msg => addMessage(msg.type, msg.content));
      if (result.has_file && result.filename) {
        currentFile = { name: result.filename };
        fileName.textContent = result.filename;
        fileUploadContainer.style.display = 'none';
        chatSection.style.display = 'block';
        questionInput.focus();

        // Show memory stats
        updateMemoryStats();
      }
    }
  } catch (error) {
    console.error('Error loading chat history:', error);
  }
}

async function updateMemoryStats() {
  try {
    const response = await fetch('/get_memory_stats');
    const result = await response.json();
    if (result.success && result.stats) {
      const memoryStats = document.getElementById('memoryStats');
      const messageCount = document.getElementById('messageCount');
      messageCount.textContent = result.stats.message_count || 0;
      memoryStats.style.display = 'block';
    }
  } catch (error) {
    console.error('Error loading memory stats:', error);
  }
}

// No click handler needed for fileDropZone (input covers it)

fileInput.addEventListener('change', e => {
  if (e.target.files.length > 0) {
    handleFileUpload(e.target.files[0]);
    fileInput.value = '';
  }
});

questionInput.addEventListener('input', function () {
  this.style.height = 'auto';
  this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

questionInput.addEventListener('keydown', function (e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendQuestion();
  }
});

async function handleFileUpload(file) {
  currentFile = file;
  showLoading(true);
  const formData = new FormData();
  formData.append('file', file);
  try {
    const response = await fetch('/upload', { method: 'POST', body: formData });
    const result = await response.json();
    if (result.success) {
      fileName.textContent = result.filename;
      fileUploadContainer.style.display = 'none';
      chatSection.style.display = 'block';
      questionInput.focus();
      addMessage('system', `File "${result.filename}" uploaded successfully! You can now ask questions about it.`);
    } else {
      alert('Error uploading file: ' + result.error);
    }
  } catch (error) {
    alert('Error uploading file: ' + error.message);
  } finally {
    showLoading(false);
    fileInput.value = '';
  }
}

async function sendQuestion() {
  const question = questionInput.value.trim();
  if (!question) return;
  addMessage('user', question);
  questionInput.value = '';
  questionInput.style.height = 'auto';
  showLoading(true);
  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const result = await response.json();
    addMessage(result.answer ? 'assistant' : 'error', result.answer || result.error || 'An error occurred');

    // Update memory stats after each message
    updateMemoryStats();
  } catch (error) {
    addMessage('error', 'Error: ' + error.message);
  } finally {
    showLoading(false);
  }
}

function addMessage(type, content) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${type}-message`;
  const formattedContent = formatTextContent(content);
  let innerHTML;
  if (type === 'user') {
    innerHTML = `<div class="message-content"><div class="message-text">${content}</div></div>`;
  } else if (type === 'assistant') {
    innerHTML = `<div class="message-content"><div class="message-text">${formattedContent}</div></div>`;
  } else if (type === 'system') {
    innerHTML = `<div class="message-content"><div class="message-text">${content}</div></div>`;
  } else {
    innerHTML = `<div class="message-content"><div class="message-text">❌ ${content}</div></div>`;
  }
  messageDiv.innerHTML = innerHTML;
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatTextContent(text) {
  if (!text) return text;
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
    .replace(/^(\d+\.\s.*$)/gm, '<div class="list-item">$1</div>')
    .replace(/^[-•]\s(.*)$/gm, '<div class="list-item">• $1</div>')
    .replace(/^([A-Z][^:]*:)$/gm, '<div class="section-header">$1</div>');
}

function showLoading(show) {
  loadingIndicator.style.display = show ? 'flex' : 'none';
  sendBtn.disabled = show;
}

function changeFile() {
  fileUploadContainer.style.display = 'block';
  fileUploadContainer.style = ''; // <-- Reset all inline styles!
  chatSection.style.display = 'none';
  chatMessages.innerHTML = '';
  currentFile = null;
}

async function clearChatOnly(event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  setTimeout(async () => {
    if (confirm('Are you sure you want to clear the chat history? (File will remain loaded)')) {
      try {
        const response = await fetch('/clear_chat_only', { method: 'POST' });
        const result = await response.json();
        if (result.success) {
          chatMessages.innerHTML = '';
          if (currentFile) {
            addMessage('system', `Chat history cleared. File "${currentFile.name}" is still loaded and ready for questions.`);
          }
        } else {
          addMessage('error', 'Failed to clear chat history: ' + (result.error || 'Unknown error'));
        }
      } catch (error) {
        addMessage('error', 'Error clearing chat: ' + error.message);
      }
    }
  }, 10);
}

function clearChat(event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  setTimeout(() => {
    if (confirm('Are you sure you want to clear the chat and remove the current file?')) {
      fetch('/clear', { method: 'POST' });
      fileUploadContainer.style.display = 'block';
      fileUploadContainer.style = ''; 
      chatSection.style.display = 'none';
      chatMessages.innerHTML = '';
      currentFile = null;
    }
  }, 10);
}
