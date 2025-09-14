// frontend/app.js
const API_BASE = 'http://localhost:5000/api';

// Navigation Functions
function showMainMenu() {
    hideAllSections();
    document.getElementById('main-menu').style.display = 'block';
}

function showSection(sectionId) {
    hideAllSections();
    document.getElementById(sectionId).style.display = 'block';
    
    // Initialize section-specific data
    if (sectionId === 'system-status') {
        refreshSystemStatus();
    }
}

function hideAllSections() {
    const sections = ['main-menu', 'login-account', 'create-account', 'search-account', 'system-status', 'guide'];
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.style.display = 'none';
    });
}

// Utility Functions
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    element.setSelectionRange(0, 99999); // For mobile devices
    document.execCommand('copy');
    
    // Show feedback
    const copyBtn = element.parentElement.querySelector('.copy-btn');
    if (copyBtn) {
        const originalText = copyBtn.textContent;
        copyBtn.textContent = '✅ Copied!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.classList.remove('copied');
        }, 2000);
    }
}

function setButtonLoading(buttonId, isLoading) {
    const button = document.getElementById(buttonId);
    if (button) {
        if (isLoading) {
            button.classList.add('loading');
            button.disabled = true;
        } else {
            button.classList.remove('loading');
            button.disabled = false;
        }
    }
}

function updateProgressStep(stepId, status) {
    const step = document.getElementById(stepId);
    if (step) {
        step.className = `progress-step ${status}`;
        const icon = step.querySelector('.step-icon');
        if (status === 'completed') {
            icon.textContent = '✅';
        } else if (status === 'active') {
            icon.textContent = '⏳';
        } else {
            icon.textContent = '⏳';
        }
    }
}

function toggleTechnicalDetails() {
    const details = document.getElementById('technical-details');
    details.classList.toggle('hidden');
}

function toggleSearchTechnical() {
    const details = document.getElementById('search-technical');
    details.classList.toggle('hidden');
}

function toggleSystemTechnical() {
    const details = document.getElementById('system-technical');
    details.classList.toggle('hidden');
}

// Create Account Functions
document.getElementById('create-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    setButtonLoading('create-btn', true);
    
    const formData = new FormData(e.target);
    const userInfo = {
        username: formData.get('username'),
        email: formData.get('email'),
        organization: formData.get('organization') || 'Not specified'
    };
    
    try {
        const response = await fetch(`${API_BASE}/register_did`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_info: userInfo })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Hide form and show success
            document.getElementById('create-form').style.display = 'none';
            document.getElementById('account-created').classList.remove('hidden');
            
            // Fill in the success information
            document.getElementById('created-account-id').value = data.did;
            document.getElementById('created-secret-key').value = data.private_key;
            document.getElementById('account-document').textContent = JSON.stringify(data.document, null, 2);
            
            // Store for quick access
            window.appState.currentAccountId = data.did;
            window.appState.currentSecretKey = data.private_key;
            
        } else {
            alert(`Error creating account: ${data.error}`);
        }
    } catch (error) {
        alert(`Network error: ${error.message}`);
    } finally {
        setButtonLoading('create-btn', false);
    }
});

function resetCreateAccount() {
    document.getElementById('create-form').style.display = 'block';
    document.getElementById('account-created').classList.add('hidden');
    document.getElementById('create-form').reset();
    document.getElementById('technical-details').classList.add('hidden');
}

function useNewAccount() {
    // Auto-fill login form and switch to login
    document.getElementById('login-account-id').value = window.appState.currentAccountId;
    document.getElementById('login-secret-key').value = window.appState.currentSecretKey;
    showSection('login-account');
}

// Search Account Functions
async function searchAccount() {
    const accountId = document.getElementById('search-account-id').value.trim();
    
    if (!accountId) {
        alert('Please enter an Account ID');
        return;
    }
    
    setButtonLoading('search-btn', true);
    
    try {
        const response = await fetch(`${API_BASE}/get_did/${encodeURIComponent(accountId)}`);
        const data = await response.json();
        
        if (data.success) {
            // Show account found
            document.getElementById('search-results').classList.remove('hidden');
            document.getElementById('account-found').classList.remove('hidden');
            document.getElementById('account-not-found').classList.add('hidden');
            
            // Fill in the found account information
            const userInfo = data.document.userInfo || {};
            document.getElementById('search-name').textContent = userInfo.username || 'Not specified';
            document.getElementById('search-email').textContent = userInfo.email || 'Not specified';
            document.getElementById('search-org').textContent = userInfo.organization || 'Not specified';
            document.getElementById('search-created').textContent = new Date(data.document.created).toLocaleString();
            document.getElementById('search-document').textContent = JSON.stringify(data.document, null, 2);
            
        } else {
            // Show account not found
            document.getElementById('search-results').classList.remove('hidden');
            document.getElementById('account-found').classList.add('hidden');
            document.getElementById('account-not-found').classList.remove('hidden');
        }
    } catch (error) {
        alert(`Network error: ${error.message}`);
    } finally {
        setButtonLoading('search-btn', false);
    }
}

// Login Functions
function resetLogin() {
    document.getElementById('login-step-1').classList.remove('hidden');
    document.getElementById('login-progress').classList.add('hidden');
    document.getElementById('login-result').classList.add('hidden');
    document.getElementById('login-success').classList.add('hidden');
    document.getElementById('login-failed').classList.add('hidden');
    
    // Auto-fill if we have stored credentials
    if (window.appState.currentAccountId) {
        document.getElementById('login-account-id').value = window.appState.currentAccountId;
    }
    if (window.appState.currentSecretKey) {
        document.getElementById('login-secret-key').value = window.appState.currentSecretKey;
    }
}

async function startLogin() {
    const accountId = document.getElementById('login-account-id').value.trim();
    const secretKey = document.getElementById('login-secret-key').value.trim();
    
    if (!accountId || !secretKey) {
        alert('Please enter both Account ID and Secret Key');
        return;
    }
    
    // Show progress
    document.getElementById('login-step-1').classList.add('hidden');
    document.getElementById('login-progress').classList.remove('hidden');
    
    try {
        // Step 1: Verify account exists
        updateProgressStep('step-verify', 'active');
        const verifyResponse = await fetch(`${API_BASE}/get_did/${encodeURIComponent(accountId)}`);
        const verifyData = await verifyResponse.json();
        
        if (!verifyData.success) {
            throw new Error('Account not found');
        }
        
        updateProgressStep('step-verify', 'completed');
        await sleep(500);
        
        // Step 2: Create challenge
        updateProgressStep('step-challenge', 'active');
        const challengeResponse = await fetch(`${API_BASE}/create_challenge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ did: accountId })
        });
        
        const challengeData = await challengeResponse.json();
        if (!challengeData.success) {
            throw new Error('Failed to create security challenge');
        }
        
        window.appState.authChallenge = challengeData.challenge;
        window.appState.authChallengeId = challengeData.challenge_id;
        
        updateProgressStep('step-challenge', 'completed');
        await sleep(500);
        
        // Step 3: Sign challenge
        updateProgressStep('step-sign', 'active');
        const signResponse = await fetch(`${API_BASE}/sign_challenge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                challenge: challengeData.challenge,
                private_key: secretKey
            })
        });
        
        const signData = await signResponse.json();
        if (!signData.success) {
            throw new Error('Failed to sign challenge - check your Secret Key');
        }
        
        window.appState.authSignature = signData.signature;
        
        updateProgressStep('step-sign', 'completed');
        await sleep(500);
        
        // Step 4: Authenticate
        updateProgressStep('step-authenticate', 'active');
        const authResponse = await fetch(`${API_BASE}/authenticate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                challenge_id: challengeData.challenge_id,
                signature: signData.signature
            })
        });
        
        const authData = await authResponse.json();
        if (!authData.success) {
            throw new Error('Authentication verification failed');
        }
        
        updateProgressStep('step-authenticate', 'completed');
        await sleep(500);
        
        // Show result
        document.getElementById('login-progress').classList.add('hidden');
        document.getElementById('login-result').classList.remove('hidden');
        
        if (authData.authenticated) {
            document.getElementById('login-success').classList.remove('hidden');
            document.getElementById('login-success-id').textContent = accountId;
            
            // Store successful credentials
            window.appState.currentAccountId = accountId;
            window.appState.currentSecretKey = secretKey;
        } else {
            document.getElementById('login-failed').classList.remove('hidden');
        }
        
    } catch (error) {
        // Show error
        document.getElementById('login-progress').classList.add('hidden');
        document.getElementById('login-result').classList.remove('hidden');
        document.getElementById('login-failed').classList.remove('hidden');
        
        alert(`Login failed: ${error.message}`);
    }
}

// System Status Functions
async function refreshSystemStatus() {
    setButtonLoading('refresh-btn', true);
    
    try {
        const response = await fetch(`${API_BASE}/blockchain_info`);
        const data = await response.json();
        
        if (data.success) {
            const info = data.blockchain_info;
            
            // Update status cards
            document.getElementById('total-accounts').textContent = Math.max(0, info.chain_length - 1);
            document.getElementById('total-blocks').textContent = info.chain_length;
            document.getElementById('network-status').innerHTML = info.is_valid ? '🟢 Online' : '🔴 Error';
            document.getElementById('chain-validity').innerHTML = info.is_valid ? '✅ Valid' : '❌ Invalid';
            
            // Update technical details
            const networkDetails = {
                chainLength: info.chain_length,
                isValid: info.is_valid,
                latestBlock: info.latest_block,
                fullChain: info.full_chain
            };
            
            document.getElementById('network-details').textContent = JSON.stringify(networkDetails, null, 2);
            
        } else {
            document.getElementById('network-status').innerHTML = '🔴 Error';
            document.getElementById('chain-validity').innerHTML = '❌ Error';
            alert(`Error getting system status: ${data.error}`);
        }
    } catch (error) {
        document.getElementById('network-status').innerHTML = '🔴 Offline';
        document.getElementById('chain-validity').innerHTML = '❌ Error';
        alert(`Network error: ${error.message}`);
    } finally {
        setButtonLoading('refresh-btn', false);
    }
}

// Utility function for delays
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    showMainMenu();
    
    // Auto-fill login if we have stored data
    if (window.appState.currentAccountId) {
        document.getElementById('login-account-id').value = window.appState.currentAccountId;
    }
    if (window.appState.currentSecretKey) {
        document.getElementById('login-secret-key').value = window.appState.currentSecretKey;
    }
});