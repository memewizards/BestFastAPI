import { writable } from 'svelte/store';

// Authentication stores
export const token = writable(null);
export const isAdmin = writable(false);
export const username = writable(null); // Can be null or string
export const userRank = writable(null);

// Initialize stores from localStorage if available
if (typeof window !== 'undefined') {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
        // @ts-ignore - We know storedToken is a string here
        token.set(storedToken);
    }
}

/**
 * Function to set permissions for user
 * @param {any} userData - User data object
 */
export function setPermissionsForUser(userData) {
    if (userData.is_admin !== undefined) {
        isAdmin.set(userData.is_admin);
    }
    if (userData.rank) {
        userRank.set(userData.rank);
    }
    if (userData.username) {
        username.set(userData.username);
    }
}

// Function to clear authentication data
export function clearAuth() {
    token.set(null);
    isAdmin.set(false);
    username.set(null);
    userRank.set(null);
    if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
    }
}
