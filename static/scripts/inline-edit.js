function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    const editableElements = document.querySelectorAll('.editable');

    editableElements.forEach(element => {
        element.addEventListener('click', makeEditable);
    });

    function makeEditable(event) {
        console.log('edit has been called');
        const element = event.target;
        const currentValue = element.textContent.trim();
        const field = element.dataset.field;
        const requestId = element.dataset.requestId;

        // Create input element
        const input = document.createElement('input');
        input.type = field === 'date_exchange' ? 'date' : 'text';
        input.value = field === 'date_exchange' ? formatDateForInput(currentValue) : currentValue;
        input.className = 'inline-edit-input';

        // Replace content with input
        element.textContent = '';
        element.appendChild(input);
        input.focus();

        // Handle save on Enter or blur
        input.addEventListener('blur', () => saveEdit(element, input, field, requestId, currentValue));
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                saveEdit(element, input, field, requestId, currentValue);
            }
            if (e.key === 'Escape') {
                cancelEdit(element, currentValue);
            }
        });
    }

    function saveEdit(element, input, field, requestId, originalValue) {
        const newValue = input.value.trim();

        if (newValue === '' || newValue === originalValue) {
            cancelEdit(element, originalValue);
            return;
        }

        // Show loading state
        element.textContent = 'Сохранение...';
        element.classList.add('saving');

        // Send AJAX request
        fetch(`/requests/${requestId}/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                field: field,
                value: newValue
            })
        })
        .then(response => response.json())
        .then(data => {
            element.classList.remove('saving');
            if (data.success) {
                const displayValue = field === 'date_exchange' ? formatDateForDisplay(newValue) : newValue;
                element.textContent = displayValue;
                element.classList.add('updated');
                setTimeout(() => element.classList.remove('updated'), 2000);
            } else {
                element.textContent = originalValue;
                alert('Ошибка при сохранении: ' + (data.error || 'Неизвестная ошибка'));
            }
        })
        .catch(error => {
            element.classList.remove('saving');
            element.textContent = originalValue;
            alert('Ошибка сети при сохранении');
        });
    }

    function cancelEdit(element, originalValue) {
        element.textContent = originalValue;
    }

    function formatDateForInput(dateString) {
        // Convert "25.08.2025" to "2025-08-25"
        const parts = dateString.split('.');
        if (parts.length === 3) {
            return `${parts[2]}-${parts[1]}-${parts[0]}`;
        }
        return dateString;
    }

    function formatDateForDisplay(isoDate) {
        // Convert "2025-08-25" to "25.08.2025"
        const date = new Date(isoDate);
        return date.toLocaleDateString('ru-RU');
    }

    // Delete button functionality
    const deleteButtons = document.querySelectorAll('.delete-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.stopPropagation(); // Prevent triggering edit mode

            if (!confirm('Вы уверены, что хотите удалить эту заявку?')) {
                return;
            }

            const card = button.closest('.request-card');
            const requestId = card.dataset.requestId;

            console.log('Deleting request ID:', requestId); // Debug log

            // Send delete request
            fetch(`/requests/${requestId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the card from DOM
                    card.style.opacity = '0.5';
                    setTimeout(() => card.remove(), 300);
                } else {
                    alert('Ошибка при удалении: ' + (data.error || 'Неизвестная ошибка'));
                }
            })
            .catch(error => {
                console.error('Delete error:', error);
                alert('Ошибка сети при удалении');
            });
        });
    });
});
