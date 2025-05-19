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

// Валидация пароля
function validatePassword(password) {
    if (password.length < 8) {
        return { valid: false, message: 'Пароль слишком короткий (минимум 8 символов)' };
    }
    if (/^\d+$/.test(password)) {
        return { valid: false, message: 'Пароль не может состоять только из цифр' };
    }
    if (!/[A-Za-z]/.test(password)) {
        return { valid: false, message: 'Добавьте буквы для надежности' };
    }
    return { valid: true, message: 'Пароль надежный' };
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('register-form');
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');
    const username = document.getElementById('id_username');
    const email = document.getElementById('id_email');
    const captchaInput = document.querySelector('input[name="captcha_1"]');

    // Динамическая валидация пароля
    password1.addEventListener('input', function () {
        const validation = validatePassword(this.value);
        showHint(this, validation.message, !validation.valid);
    });

    // Проверка совпадения паролей
    password2.addEventListener('input', function () {
        if (this.value === '') {
            showHint(this, '');
            return;
        }
        if (password1.value === '') {
            showHint(this, 'Введите пароль выше', true);
            return;
        }
        if (this.value !== password1.value) {
            showHint(this, 'Пароли не совпадают', true);
        } else {
            showHint(this, 'Пароли совпадают');
        }
    });

    // AJAX-проверка username и email
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        let isValid = true;

        // Проверка email
        const emailResponse = await fetch('/check-email/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `email=${encodeURIComponent(email.value)}`
        });
        const emailData = await emailResponse.json();
        if (emailData.exists) {
            showHint(email, 'Этот email уже занят', true);
            isValid = false;
        }

        // Проверка username
        const usernameResponse = await fetch('/check-username/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username.value)}`
        });
        const usernameData = await usernameResponse.json();
        if (usernameData.exists) {
            showHint(username, 'Это имя пользователя уже занято', true);
            isValid = false;
        }

        // Проверка капчи
        if (captchaInput && captchaInput.value.trim().length === 0) {
            showHint(captchaInput, 'Капча введена неверно', true);
            isValid = false;
        }

        if (isValid) this.submit();
    });

    // Показываем ошибку капчи при загрузке, если она была до этого
    window.addEventListener('load', function () {
        const captchaInput = document.querySelector('input[name="captcha_1"]');
        if (captchaInput && captchaInput.dataset.error === 'true') {
            showHint(captchaInput, 'Капча введена неверно', true);
        }
    });
});

// Очистка ошибки капчи при вводе
const captchaInput = document.querySelector('input[name="captcha_1"]');
if (captchaInput) {
    captchaInput.addEventListener('input', function () {
        const hint = document.getElementById('captcha-hint');
        if (hint) hint.textContent = '';
    });
}