document.addEventListener('DOMContentLoaded', () => {
    // Only run if we are on the home page (where these elements exist)
    const translateBtn = document.getElementById('translate-btn');
    if (!translateBtn) return;

    const clearBtn = document.getElementById('clear-btn');
    const inputTextArea = document.getElementById('english-input');
    const exampleBtns = document.querySelectorAll('.example-btn');
    
    const englishOutput = document.getElementById('english-output');
    const frenchOutput = document.getElementById('french-output');
    const loadingDiv = document.getElementById('loading');
    
    const unknownWordsContainer = document.getElementById('unknown-words-container');
    const unknownWordsList = document.getElementById('unknown-words-list');
    
    const statusMessage = document.getElementById('status-message');
    const timeMessage = document.getElementById('time-message');

    // Handle Example Clicks
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            inputTextArea.value = btn.innerText;
            // Optionally auto-translate: translate();
        });
    });

    // Handle Clear Button
    clearBtn.addEventListener('click', () => {
        inputTextArea.value = '';
        englishOutput.innerText = '...';
        frenchOutput.innerText = '...';
        frenchOutput.style.display = 'block';
        loadingDiv.classList.add('hidden');
        unknownWordsContainer.classList.add('hidden');
        statusMessage.innerText = 'Awaiting input...';
        statusMessage.style.color = '#2ecc71';
        timeMessage.innerText = '';
        inputTextArea.focus();
    });

    // Handle Translate Button
    translateBtn.addEventListener('click', translate);

    async function translate() {
        const sentence = inputTextArea.value.trim();
        
        if (!sentence) {
            alert('Please enter an English sentence.');
            return;
        }

        // UI Reset for new translation
        englishOutput.innerText = sentence;
        frenchOutput.style.display = 'none';
        loadingDiv.classList.remove('hidden');
        unknownWordsContainer.classList.add('hidden');
        statusMessage.innerText = 'Processing...';
        statusMessage.style.color = '#f39c12'; // Warning/processing orange
        timeMessage.innerText = '';

        try {
            const response = await fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ sentence: sentence })
            });

            const data = await response.json();

            loadingDiv.classList.add('hidden');
            frenchOutput.style.display = 'block';

            if (!response.ok) {
                frenchOutput.innerText = 'Error: ' + data.error;
                statusMessage.innerText = 'Translation Failed';
                statusMessage.style.color = '#e74c3c'; // Red
                return;
            }

            // Success or Partial Success
            frenchOutput.innerText = data.translation || '(No translation output)';
            
            if (data.status) {
                statusMessage.innerText = 'Translation Successful';
                statusMessage.style.color = '#2ecc71'; // Green
            } else {
                statusMessage.innerText = 'Translation Completed with Unknown Words';
                statusMessage.style.color = '#e74c3c'; // Red
                
                // Show unknown words
                unknownWordsList.innerHTML = '';
                data.unknown_words.forEach(word => {
                    const li = document.createElement('li');
                    li.innerText = word;
                    unknownWordsList.appendChild(li);
                });
                unknownWordsContainer.classList.remove('hidden');
            }

            if (data.time_ms !== undefined) {
                timeMessage.innerText = `Translation took ${data.time_ms} ms`;
            }

        } catch (error) {
            loadingDiv.classList.add('hidden');
            frenchOutput.style.display = 'block';
            frenchOutput.innerText = 'Network error occurred.';
            statusMessage.innerText = 'Translation Failed';
            statusMessage.style.color = '#e74c3c'; // Red
            console.error('Translation error:', error);
        }
    }
});
