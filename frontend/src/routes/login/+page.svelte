<script lang="ts">
    import { token, isAdmin, username, userRank, setPermissionsForUser } from '$lib/stores/auth.js';
    import { goto } from '$app/navigation';
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
    
    let inputEmail = '';     // Using email as the username for login purposes
    let inputUsername = '';  // field for registration username
    let password = '';
    let error = '';
    let showRegister = false;
    let info = '';
    let showForgotPassword = false;
    let resetEmailSent = false;

    // If token exists, redirect to dashboard.
    $: if ($token) {
        goto('/create');
    }

    async function login() {
        error = '';
        try {
            const formData = new URLSearchParams();
            formData.append('username', inputEmail);
            formData.append('password', password);

            const response = await fetch(`${API_BASE_URL}/api/login`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                },
                body: formData
            });
            
            if (!response.ok) {
                const errData = await response.json();
                console.log('Login error:', errData);
                error = errData.detail || 'Login failed. Please try again.';
                console.log('Error message set to:', error);
                return;
            }
            
            const data = await response.json();
            $token = data.access_token;
            $isAdmin = data.is_admin;
            $username = data.username || inputEmail;
            $userRank = data.rank;

            setPermissionsForUser(data);
            localStorage.setItem("token", data.access_token);
            goto("/create");
        } catch (err) {
            console.error('Login error:', err);
            error = "An unexpected error occurred. Please try again.";
        }
    }

    async function register() {
        error = '';
        info = '';
        // Validate that a username is provided when registering
        if (!inputUsername) {
            error = 'Please enter a username.';
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/api/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    email: inputEmail,
                    username: inputUsername,
                    password
                })
            });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to register');
            }
            const data = await response.json();
            // Show success message and clear form
            info = data.message;
            // Clear form fields after successful registration
            inputEmail = '';
            inputUsername = '';
            password = '';
        } catch (err) {
            error = err instanceof Error ? err.message : 'An error occurred';
        }
    }

    async function sendPasswordReset() {
        error = '';
        info = '';
        try {
            const response = await fetch(`${API_BASE_URL}/api/password-reset/request-simple`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: inputEmail })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to send reset email');
            }
            
            const data = await response.json();
            
            if (data.note) {
                // Email sending is disabled, show the token for testing
                info = `${data.message}. Token: ${data.token}`;
            } else {
                // Email was actually sent
                resetEmailSent = true;
                info = data.message;
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'An error occurred';
        }
    }

    function handleSubmit() {
        if (showForgotPassword) {
            sendPasswordReset();
        } else if (showRegister) {
            register();
        } else {
            login();
        }
    }
</script>

<div class="login-container">
    <form class="login-form" on:submit|preventDefault={handleSubmit}>
        <h1>{showForgotPassword ? 'Reset Password' : showRegister ? 'Register' : 'Login'}</h1>
        
        {#if showForgotPassword}
            <div class="form-group">
                <label for="email">Email:</label>
                <input
                    id="email" 
                    type="email" 
                    bind:value={inputEmail} 
                    placeholder="Enter your registered email"
                    required
                />
            </div>
            
            {#if error}
                <div class="error">{error}</div>
            {/if}
            {#if info}
                <div class="info">{info}</div>
            {/if}
            
            <button type="submit">Send Reset Instructions</button>
            <p>Remember your password? 
                <button type="button" on:click={() => { 
                    showForgotPassword = false; 
                    error = ''; 
                    info = '';
                }}>Back to Login</button>
            </p>
        {:else if showRegister}
            <div class="form-group">
                <label for="username">Username:</label>
                <input 
                    id="username" 
                    type="text" 
                    bind:value={inputUsername} 
                    placeholder="Enter your username"
                    required
                />
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input 
                    id="email" 
                    type="email" 
                    bind:value={inputEmail} 
                    placeholder="Enter your email"
                    required
                />
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input 
                    id="password" 
                    type="password" 
                    bind:value={password} 
                    placeholder="Create password"
                    required
                />
            </div>
            
            {#if error}
                <div class="error">{error}</div>
            {/if}
            {#if info}
                <div class="info">{info}</div>
            {/if}
            
            <button type="submit">Register</button>
            <p>Already have an account? 
                <button type="button" class="text-button" on:click={() => { 
                    showRegister = false; 
                    error = ''; 
                    info = '';
                }}>Back to Login</button>
            </p>
        {:else}
            <div class="form-group">
                <label for="email">Email:</label>
                <input 
                    id="email" 
                    type="email" 
                    bind:value={inputEmail} 
                    placeholder="Enter your email"
                    required
                />
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input 
                    id="password" 
                    type="password" 
                    bind:value={password} 
                    placeholder="Enter password"
                    required
                />
            </div>
            
            {#if error}
                <div class="error" role="alert">{error}</div>
            {/if}
            
            <button type="submit">Login</button>
            <div class="form-links">
                <p>New user? 
                    <button type="button" class="text-button" on:click={() => { 
                        showRegister = true; 
                        error = ''; 
                        info = '';
                        inputUsername = '';
                    }}>Create account</button>
                </p>
                <p>Forgot your password? 
                    <button type="button" class="text-button" on:click={() => { 
                        showForgotPassword = true; 
                        error = ''; 
                        info = '';
                    }}>Reset it here</button>
                </p>
            </div>
        {/if}
    </form>
</div>

<style>
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background-color: #f5f5f5;
    }
    .login-form {
        width: 100%;
        max-width: 400px;
        padding: 1.5em;
        margin: 0 auto;
        border: 1px solid #ccc;
        border-radius: 8px;
        background-color: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .form-group {
        margin-bottom: 1em;
    }
    label {
        display: block;
        margin-bottom: 0.5em;
        font-weight: bold;
    }
    input {
        width: 100%;
        padding: 0.5em;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 1em;
    }
    button {
        width: 100%;
        padding: 0.75em;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 1em;
    }
    button:hover {
        background-color: #0056b3;
    }
    .error {
        color: #dc3545;
        margin-bottom: 1em;
        text-align: center;
        padding: 0.75em;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 4px;
        font-weight: 500;
    }
    .info {
        color: green;
        margin-bottom: 1em;
        text-align: center;
    }
    h1 {
        text-align: center;
        margin-bottom: 1em;
    }
    .text-button {
        background: none;
        border: none;
        color: #007bff;
        text-decoration: underline;
        padding: 0;
        margin: 0;
        display: inline;
        cursor: pointer;
    }
    
    .form-links {
        margin-top: 1.5rem;
        text-align: center;
    }
    
    .form-links p {
        margin: 0.5rem 0;
    }
</style>