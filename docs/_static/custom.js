// Custom JavaScript for Canvas Quiz Manager Documentation

// Add smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function () {
    // Smooth scrolling for internal links
    const internalLinks = document.querySelectorAll('a[href^="#"]');
    internalLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add copy button to code blocks
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach((codeBlock, index) => {
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Copy';
        copyButton.className = 'copy-button';
        copyButton.style.cssText = `
            position: absolute;
            top: 5px;
            right: 5px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 2px 8px;
            font-size: 12px;
            cursor: pointer;
            opacity: 0.8;
        `;

        copyButton.addEventListener('click', function () {
            navigator.clipboard.writeText(codeBlock.textContent).then(() => {
                this.textContent = 'Copied!';
                setTimeout(() => {
                    this.textContent = 'Copy';
                }, 2000);
            });
        });

        // Make code block container relative for absolute positioning
        const preElement = codeBlock.parentElement;
        preElement.style.position = 'relative';
        preElement.appendChild(copyButton);
    });

    // Add syntax highlighting for HTTP methods
    const httpMethods = document.querySelectorAll('.http-get, .http-post, .http-put, .http-delete');
    httpMethods.forEach(method => {
        const methodType = method.className.split('-')[1].toUpperCase();
        const header = method.querySelector('h3');
        if (header) {
            const methodBadge = document.createElement('span');
            methodBadge.textContent = methodType;
            methodBadge.style.cssText = `
                background: #007bff;
                color: white;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
                margin-right: 10px;
            `;
            header.insertBefore(methodBadge, header.firstChild);
        }
    });

    // Add collapsible sections for long content
    const longSections = document.querySelectorAll('h2, h3');
    longSections.forEach(section => {
        const content = section.nextElementSibling;
        if (content && content.tagName !== 'H2' && content.tagName !== 'H3') {
            const toggleButton = document.createElement('button');
            toggleButton.textContent = '▼';
            toggleButton.className = 'toggle-section';
            toggleButton.style.cssText = `
                background: none;
                border: none;
                font-size: 16px;
                cursor: pointer;
                margin-left: 10px;
                color: #007bff;
            `;

            section.appendChild(toggleButton);

            toggleButton.addEventListener('click', function () {
                const isCollapsed = content.style.display === 'none';
                content.style.display = isCollapsed ? 'block' : 'none';
                this.textContent = isCollapsed ? '▼' : '▶';
            });
        }
    });

    // Add search functionality for API endpoints
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Search API endpoints...';
    searchInput.style.cssText = `
        width: 100%;
        padding: 8px;
        margin: 10px 0;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    `;

    const apiSection = document.querySelector('#web-interface-endpoints');
    if (apiSection) {
        apiSection.parentNode.insertBefore(searchInput, apiSection);

        searchInput.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase();
            const endpoints = document.querySelectorAll('.http-get, .http-post, .http-put, .http-delete');

            endpoints.forEach(endpoint => {
                const text = endpoint.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    endpoint.style.display = 'block';
                } else {
                    endpoint.style.display = 'none';
                }
            });
        });
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', function (e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[placeholder*="Search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape to clear search
    if (e.key === 'Escape') {
        const searchInput = document.querySelector('input[placeholder*="Search"]');
        if (searchInput) {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
        }
    }
});
