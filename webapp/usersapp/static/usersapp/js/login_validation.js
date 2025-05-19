// Функция для отображения подсказок
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
    return hint;
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('login-form');

    if (!form) return;

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        const usernameInput = document.getElementById('id_username');
        const passwordInput = document.getElementById('id_password');
        const captchaInput = document.querySelector('input[name="captcha_1"]');
        const formData = new FormData(form);

        // Проверяем поля через Django API
        const response = await fetch('/check-login/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Accept': 'application/json'
            },
            body: new URLSearchParams(formData)
        });

        const data = await response.json();

        if (data.success) {
            form.submit();
        } else {
            if (data.errors.username) {
                showHint(usernameInput, data.errors.username, true);
            }
            if (data.errors.password) {
                showHint(passwordInput, data.errors.password, true);
            }
            if (data.errors.captcha) {
                showHint(captchaInput, data.errors.captcha, true);
            }
        }
    });
});