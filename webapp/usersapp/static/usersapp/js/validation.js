document.addEventListener('DOMContentLoaded', function() {
    // Элементы формы
    const password1 = document.querySelector('#id_password1');
    const password2 = document.querySelector('#id_password2');
    const username = document.querySelector('#id_username');
    const email = document.querySelector('#id_email');
    const form = document.querySelector('form');

    // Создаем контейнеры для подсказок
    const createHint = (field, text = '', isError = false) => {
        let hint = field.nextElementSibling;
        if (!hint || !hint.classList.contains('hint')) {
            hint = document.createElement('div');
            hint.className = 'hint';
            field.parentNode.insertBefore(hint, field.nextSibling);
        }
        hint.textContent = text;
        hint.style.color = isError ? '#e74c3c' : '#2ecc71';
        return hint;
    };

    // Валидация пароля
    password1.addEventListener('input', function() {
        const value = this.value;
        let hint = '';
        let isError = false;

        if (value.length < 8) {
            hint = 'Пароль слишком короткий (минимум 8 символов)';
            isError = true;
        } else if (/^\d+$/.test(value)) {
            hint = 'Пароль не может состоять только из цифр';
            isError = true;
        } else if (!/[A-Za-z]/.test(value)) {
            hint = 'Добавьте буквы для надежности';
            isError = true;
        }

        createHint(this, hint, isError);
    });

    // Проверка совпадения паролей
    password2.addEventListener('input', function() {
        const hint = createHint(this);
        if (password1.value !== this.value) {
            hint.textContent = 'Пароли не совпадают';
            hint.style.color = '#e74c3c';
        } else {
            hint.textContent = 'Пароли совпадают';
            hint.style.color = '#2ecc71';
        }
    });

    // Проверка уникальности email/username (после отправки формы)
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        let isError = false;

        // Проверка email через AJAX
        const emailCheck = await fetch('/check-email/', {
            method: 'POST',
            headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
            body: new URLSearchParams({ email: email.value })
        });
        const emailResult = await emailCheck.json();
        if (emailResult.exists) {
            createHint(email, 'Этот email уже занят', true);
            isError = true;
        }

        // Проверка username
        const usernameCheck = await fetch('/check-username/', {
            method: 'POST',
            headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
            body: new URLSearchParams({ username: username.value })
        });
        const usernameResult = await usernameCheck.json();
        if (usernameResult.exists) {
            createHint(username, 'Это имя пользователя уже занято', true);
            isError = true;
        }

        if (!isError) this.submit();
    });
});