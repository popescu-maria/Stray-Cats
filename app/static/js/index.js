document.addEventListener('DOMContentLoaded', function() {
    if (window.flashedMessages && Array.isArray(window.flashedMessages)) {
        window.flashedMessages.forEach(msg => {
            if (msg.category === 'info' && msg.text.includes('Please log in to access this page.')) {
            } else {
                alert(msg.text);
            }
        });
        window.flashedMessages = [];
    }

    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');

    const loginBtn = document.getElementById('loginButton');
    const registerBtn = document.getElementById('registerButton');

    const closeButtons = document.querySelectorAll('.close-button');

    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    const loginMessage = document.getElementById('loginMessage');
    const registerMessage = document.getElementById('registerMessage');

    function showModal(modal, message = '') {
        modal.style.display = 'flex';
        if (modal === loginModal && message) {
            loginMessage.textContent = message;
            loginMessage.style.color = 'orange';
        }
    }

    function hideModal(modal) {
        modal.style.display = 'none';
        if (modal === loginModal) {
            loginMessage.textContent = '';
        } else if (modal === registerModal) {
            registerMessage.textContent = '';
        }
        modal.querySelector('form').reset();
    }

    if (loginBtn) {
        loginBtn.addEventListener('click', () => showModal(loginModal));
    }
    if (registerBtn) {
        registerBtn.addEventListener('click', () => showModal(registerModal));
    }

    closeButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            hideModal(event.target.closest('.modal'));
        });
    });

    window.addEventListener('click', (event) => {
        if (event.target === loginModal) {
            hideModal(loginModal);
        }
        if (event.target === registerModal) {
            hideModal(registerModal);
        }
    });

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            loginMessage.textContent = '';
            const formData = new FormData(loginForm);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch(loginForm.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    loginMessage.textContent = result.message;
                    loginMessage.style.color = 'green';
                    setTimeout(() => {
                        hideModal(loginModal);
                        if (result.redirect) {
                            window.location.href = result.redirect;
                        } else {
                            window.location.reload();
                        }
                    }, 1500);
                } else {
                    loginMessage.textContent = result.message || 'Login failed.';
                    loginMessage.style.color = 'red';
                }
            } catch (error) {
                console.error('Login request error:', error);
                loginMessage.textContent = 'Network error or server unavailable.';
                loginMessage.style.color = 'red';
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            registerMessage.textContent = '';
            const password = document.getElementById('reg_password').value;
            const confirmPassword = document.getElementById('reg_confirm_password').value;

            if (password !== confirmPassword) {
                registerMessage.textContent = 'Passwords do not match.';
                registerMessage.style.color = 'red';
                return;
            }

            const formData = new FormData(registerForm);
            const data = Object.fromEntries(formData.entries());
            delete data.confirm_password;

            try {
                const response = await fetch(registerForm.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    registerMessage.textContent = result.message;
                    registerMessage.style.color = 'green';
                    setTimeout(() => {
                        hideModal(registerModal);
                        if (result.redirect) {
                            window.location.href = result.redirect;
                        } else {
                            window.location.reload();
                        }
                    }, 1500);
                } else {
                    registerMessage.textContent = result.message || 'Registration failed.';
                    registerMessage.style.color = 'red';
                }
            } catch (error) {
                console.error('Registration request error:', error);
                registerMessage.textContent = 'Network error or server unavailable.';
                registerMessage.style.color = 'red';
            }
        });
    }

    if (window.flashedMessages && Array.isArray(window.flashedMessages)) {
        window.flashedMessages.forEach(msg => {
            if (msg.category === 'info' && msg.text.includes('Please log in to access this page.')) {
                showModal(loginModal, msg.text);
            } else {
                alert(msg.text);
            }
        });
        window.flashedMessages = [];
    }
});