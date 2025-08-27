document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('registerForm');
  if (!form) return;

  const f = form.elements;
  const username = f.username;
  const email = f.email;
  const telegram = f.telegram;
  const password = f.password;
  const confirm = f.confirm;

  // Helpers
  const clearValidity = (el) => el && el.setCustomValidity('');
  const setError = (el, msg) => el && el.setCustomValidity(msg);

  const hasLetter = (s) => /[A-Za-zА-Яа-я]/.test(s);
  const hasDigit = (s) => /\d/.test(s);

  // Live clearing of messages
  [username, email, telegram, password, confirm].forEach((el) => {
    if (!el) return;
    el.addEventListener('input', () => clearValidity(el));
  });

  // Optional: keep confirm validity synced with password
  password.addEventListener('input', () => {
    if (confirm.value) {
      clearValidity(confirm);
      if (confirm.value !== password.value) {
        setError(confirm, 'Пароли должны совпадать');
      }
    }
  });

  confirm.addEventListener('input', () => {
    clearValidity(confirm);
    if (confirm.value !== password.value) {
      setError(confirm, 'Пароли должны совпадать');
    }
  });

  function validateForm() {
    let ok = true;

    // Username: required, min 3 chars
    clearValidity(username);
    if (!username.value.trim()) {
      setError(username, 'Введите имя пользователя');
      ok = false;
    } else if (username.value.trim().length < 3) {
      setError(username, 'Минимум 3 символа');
      ok = false;
    }

    // Email: rely on built-in email type + presence
    clearValidity(email);
    if (!email.value.trim() || !email.checkValidity()) {
      setError(email, 'Введите корректную почту');
      ok = false;
    }

    // Telegram (optional): if present, validate
    // Accepts with or without '@', 5–32 symbols, letters/digits/underscore
    clearValidity(telegram);
    const tg = telegram.value.trim();
    if (tg) {
      const tgOk = /^@?[A-Za-z0-9_]{5,32}$/.test(tg);
      if (!tgOk) {
        setError(telegram, 'Ник в формате @username (5–32 символов, латиница/цифры/_)');
        ok = false;
      } else {
        // Normalize: auto-prepend '@' if missing
        if (!tg.startsWith('@')) telegram.value = '@' + tg;
      }
    }

    // Password: required, min 8, must have letter and number
    clearValidity(password);
    const pw = password.value;
    if (!pw || pw.length < 8 || !hasLetter(pw) || !hasDigit(pw)) {
      setError(password, 'Пароль: минимум 8 символов, буква и цифра');
      ok = false;
    }

    // Confirm: must match
    clearValidity(confirm);
    if (confirm.value !== pw) {
      setError(confirm, 'Пароли должны совпадать');
      ok = false;
    }

    return ok;
  }

  form.addEventListener('submit', (e) => {
    // Let the browser show messages using reportValidity
    const ok = validateForm();
    if (!ok) {
      e.preventDefault();
      form.reportValidity();
      return;
    }

    // For now: prevent real submit until backend is wired.
    e.preventDefault();

    // Preview payload (what we'll send to Django soon)
    const payload = {
      username: username.value.trim(),
      email: email.value.trim(),
      telegram: telegram.value.trim() || null,
      password: password.value, // will be sent over HTTPS in production
    };
    console.log('Registration payload (preview):', payload);
    alert('Форма валидна. Дальше подключим Django и отправку на сервер.');
  });
});
