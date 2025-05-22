document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('login-form');
    if (!form) return;

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch('/login/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData
            });

            if (response.redirected) {
                window.location.href = response.url;
                return;
            }

            const data = await response.json();

            if (data.success) {
                form.submit();
            } else {
                document.querySelectorAll('.hint').forEach(h => h.remove());

                if (data.errors) {
                    for (const [field, error] of Object.entries(data.errors)) {
                        const input = document.getElementById(`id_${field}`);
                        if (input) {
                            showHint(input, error, true);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error:', error);
            const usernameInput = document.getElementById('id_username');
            showHint(usernameInput, 'Произошла ошибка при отправке формы', true);
        }
    });

    function showHint(element, message, isError = false) {
        const hintId = `${element.id}-hint`;
        let hint = document.getElementById(hintId);
        if (!hint) {
            hint = document.createElement('div');
            hint.id = hintId;
            hint.className = 'hint';
            element.parentNode.appendChild(hint);
        }
        hint.textContent = message;
        hint.style.color = isError ? '#e74c3c' : '#2ecc71';
    }
});