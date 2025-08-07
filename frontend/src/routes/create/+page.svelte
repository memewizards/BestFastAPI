<script lang="ts">
    import { token, username, isAdmin, clearAuth } from '$lib/stores/auth.js';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';

    onMount(() => {
        // If no token, redirect to login
        if (!$token) {
            goto('/login');
        }
    });

    function logout() {
        clearAuth();
        goto('/login');
    }
</script>

<div class="dashboard">
    <header class="header">
        <h1>Welcome, {$username || 'User'}!</h1>
        <button class="logout-btn" on:click={logout}>Logout</button>
    </header>
    
    <main class="main-content">
        <div class="user-info">
            <h2>User Information</h2>
            <p><strong>Username:</strong> {$username}</p>
            <p><strong>Admin:</strong> {$isAdmin ? 'Yes' : 'No'}</p>
            <p><strong>Token:</strong> {$token ? 'Present' : 'None'}</p>
        </div>
        
        <div class="actions">
            <h2>Available Actions</h2>
            <p>This is your dashboard. Add your application features here.</p>
        </div>
    </main>
</div>

<style>
    .dashboard {
        min-height: 100vh;
        background-color: #f5f5f5;
    }
    
    .header {
        background-color: #007bff;
        color: white;
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logout-btn {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
    }
    
    .logout-btn:hover {
        background-color: #c82333;
    }
    
    .main-content {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .user-info, .actions {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    h2 {
        margin-top: 0;
        color: #333;
    }
</style>
