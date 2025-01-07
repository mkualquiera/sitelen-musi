document.addEventListener('DOMContentLoaded', function () {
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: function (node) {
                // Skip if parent is one of our special tags
                if (['CT', 'TN', 'PI'].includes(node.parentElement?.tagName)) {
                    return NodeFilter.FILTER_REJECT;
                }
                // Only skip if text is PURELY whitespace
                if (!node.textContent) {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            }
        }
    );

    const nodes = [];
    let node;
    while (node = walker.nextNode()) {
        nodes.push(node);
    }

    nodes.forEach(node => {
        const span = document.createElement('span');
        span.innerHTML = Array.from(node.textContent).map(char => {
            if (char.trim() === '') {
                return char;
            }
            if (char === ',') {
                // disable ligatures
                return `<span class="comma" style="display: inline-block; min-width: 1em; font-feature-settings: 'liga' 0, 'calt' 0, 'kern' 0;">${char}</span>`;
            }
            // Add min-width to all character spans to prevent collapse
            return `<span style="display: inline-block; min-width: 1em;">${char}</span>`;
        }).join('');
        node.parentNode.replaceChild(span, node);
    });

    // Delete all spans that just contain whitespace
    document.querySelectorAll('span').forEach(span => {
        if (span.textContent.trim() === '') {
            span.remove();
        }
    });
});