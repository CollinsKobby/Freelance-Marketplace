document.addEventListener('DOMContentLoaded', function() {
    // Dropdown functionality for filters
    const filters = document.querySelectorAll('.filter');
    
    filters.forEach(filter => {
        filter.addEventListener('click', function() {
            // In a real app, this would show a dropdown with options
            console.log(`Filter by ${this.querySelector('span').textContent}`);
        });
    });

    // Search button functionality
    const searchBtn = document.querySelector('.btn-search');
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            // In a real app, this would trigger a search
            console.log('Searching tasks...');
            alert('Search functionality would be implemented here in a real application.');
        });
    }

    // Task card click functionality
    const taskCards = document.querySelectorAll('.task-card');
    taskCards.forEach(card => {
        card.addEventListener('click', function() {
            // In a real app, this would navigate to task details
            console.log('Viewing task details...');
        });
    });
});