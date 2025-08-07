<script>
  let email = '';
  let password = '';
  let isLoading = false;
  let message = '';

  async function handleLogin() {
    isLoading = true;
    message = '';
    
    try {
      // Backend expects form data with 'username' field (using email as username)
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        message = 'Login successful!';
        console.log('Login response:', data);
      } else {
        const errorData = await response.json();
        message = errorData.detail || 'Login failed. Please check your credentials.';
      }
    } catch (error) {
      message = 'Connection error. Please try again.';
      console.error('Login error:', error);
    } finally {
      isLoading = false;
    }
  }
</script>

<main class="min-h-screen bg-gray-100 flex items-center justify-center">
  <div class="bg-white p-8 rounded-lg shadow-md w-96">
    <h1 class="text-2xl font-bold text-center mb-6">Login</h1>
    
    <form on:submit|preventDefault={handleLogin} class="space-y-4">
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
        <input
          id="email"
          type="email"
          bind:value={email}
          required
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      
      <div>
        <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
        <input
          id="password"
          type="password"
          bind:value={password}
          required
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      
      <button
        type="submit"
        disabled={isLoading}
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
    </form>
    
    {#if message}
      <div class="mt-4 p-3 rounded-md {message.includes('successful') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">
        {message}
      </div>
    {/if}
  </div>
</main>
