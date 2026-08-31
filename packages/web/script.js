// Simple script for Novacode web app
document.addEventListener('DOMContentLoaded', function() {
    // Add any interactive functionality here
    console.log('Novacode web app loaded');
    
    // Example: Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});