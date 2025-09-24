// Main JavaScript for Chase Bank Online Banking

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert) {
                bootstrap.Alert.getInstance(alert).close();
            }
        }, 5000);
    });

    // Format currency inputs
    const currencyInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });

    // Confirm destructive actions
    const destructiveButtons = document.querySelectorAll('[data-confirm]');
    destructiveButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Enhanced form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Real-time balance formatting
    const balanceElements = document.querySelectorAll('.balance-format');
    balanceElements.forEach(element => {
        const balance = parseFloat(element.textContent.replace(/[^0-9.-]+/g, ""));
        if (!isNaN(balance)) {
            element.textContent = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(balance);
        }
    });
});

// API Functions
const BankingAPI = {
    // Transfer money between accounts
    async transferMoney(fromAccount, toAccount, amount, description) {
        try {
            const response = await fetch('/api/transfer/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    from_account: fromAccount,
                    to_account: toAccount,
                    amount: amount,
                    description: description
                })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Transfer error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    },

    // Pay a bill
    async payBill(accountId, payeeName, payeeAccount, amount, scheduledDate) {
        try {
            const response = await fetch('/api/billpay/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    account: accountId,
                    payee_name: payeeName,
                    payee_account: payeeAccount,
                    amount: amount,
                    scheduled_date: scheduledDate
                })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Bill pay error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    },

    // Mark alert as read
    async markAlertRead(alertId) {
        try {
            const response = await fetch(`/api/alerts/${alertId}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Mark alert read error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    },

    // Get account transactions
    async getAccountTransactions(accountId, page = 1) {
        try {
            const response = await fetch(`/api/accounts/${accountId}/transactions/?page=${page}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Get transactions error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    },

    // Utility function to get CSRF token
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
};

// UI Helper Functions
const UIHelpers = {
    // Show loading state
    showLoading(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="loading"></span> Processing...';
        button.disabled = true;
        return originalText;
    },

    // Hide loading state
    hideLoading(button, originalText) {
        button.innerHTML = originalText;
        button.disabled = false;
    },

    // Show success message
    showSuccess(message) {
        this.showMessage(message, 'success');
    },

    // Show error message
    showError(message) {
        this.showMessage(message, 'danger');
    },

    // Show generic message
    showMessage(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.container-fluid') || document.body;
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },

    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    // Format date
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
};

// Export for use in other modules
window.BankingAPI = BankingAPI;
window.UIHelpers = UIHelpers;