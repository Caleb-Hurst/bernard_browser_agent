"""
Page analyzer for examining web page content and structure.
"""

import time
from langchain_core.tools import tool

# Global variables
page = None
page_elements = []

def initialize(browser_page):
    """Initialize the page analyzer."""
    global page
    page = browser_page

@tool
def analyze_page():
    """
    Extracts page content and interactive elements with ID references.
    
    Scans DOM for visible text and elements (buttons, links, inputs), 
    including modals/popups. Returns elements in [ID][type]Text format
    and creates internal map for precise targeting.
    
    Use after navigation/clicks or when page state changes.
    
    Returns: Formatted page content with element IDs.
    """
    global page_elements
    try:
            # Initialize page elements array to store detailed information
            page_elements = []

            print("Analyzing page content...")
            
            # Use JavaScript to directly analyze the DOM
            page_content = page.evaluate("""
            () => {
                // Helper function to check if element is visible
                function isVisible(el) {
                    if (!el.getBoundingClientRect) return false;
                    const rect = el.getBoundingClientRect();
                    
                    // Check if element has dimensions
                    if (rect.width <= 0 || rect.height <= 0) return false;
                    
                    // Check CSS properties that would make it invisible
                    const style = window.getComputedStyle(el);
                    if (style.display === 'none' || 
                        style.visibility === 'hidden' || 
                        parseFloat(style.opacity) <= 0.1) {
                        return false;
                    }
                    
                    return true;
                }
                
                // Helper to clean text
                function cleanText(text) {
                    if (!text) return '';
                    return text.replace(/\\s+/g, ' ').trim();
                }
                
                // In the analyze_page method, replace the current getElementType function with this enhanced version:
                function getElementType(el) {
                    const tagName = el.tagName.toLowerCase();
                    const type = el.getAttribute('type')?.toLowerCase();
                    const role = el.getAttribute('role')?.toLowerCase();
                    
                    // Interactive elements with specific types
                    if (tagName === 'a') return 'link';
                    if (tagName === 'button') return 'button';
                    
                    if (tagName === 'input') {
                        if (['submit', 'button', 'reset'].includes(type)) return 'button';
                        if (['text', 'email', 'password', 'search', 'tel', 'url'].includes(type)) return 'input';
                        if (type === 'checkbox') return 'checkbox';
                        if (type === 'radio') return 'radio';
                        return 'input'; // Default for other input types
                    }
                    
                    if (tagName === 'select') return 'dropdown';
                    if (tagName === 'textarea') return 'textarea';
                    
                    // Check for ARIA roles
                    if (role === 'button') return 'button';
                    if (role === 'link') return 'link';
                    if (role === 'checkbox') return 'checkbox';
                    if (role === 'radio') return 'radio';
                    if (role === 'textbox' || role === 'searchbox') return 'input';
                    if (role === 'combobox' || role === 'listbox') return 'dropdown';
                    if (role === 'tab') return 'tab';
                    
                    // Check for interactive divs/spans
                    const style = window.getComputedStyle(el);
                    const hasClickHandler = el.onclick || el.getAttribute('onclick');
                    const isPointable = style.cursor === 'pointer';
                    
                    if ((tagName === 'div' || tagName === 'span') && (hasClickHandler || isPointable)) {
                        // Try to determine a more specific type for divs/spans that are clickable
                        if (el.getAttribute('aria-haspopup') === 'true') return 'dropdown';
                        if (el.classList.contains('btn') || el.classList.contains('button')) return 'button';
                        if (el.getAttribute('href') || el.getAttribute('url')) return 'link';
                        
                        // If we can't determine a more specific type, default to button
                        return 'button';
                    }
                    
                    // Enhanced detection for additional interactive elements
                    if (el.getAttribute('onclick') || el.getAttribute('tabindex') === '0') return 'interactive';
                    if (style.cursor === 'pointer') return 'interactive';
                    
                    // Form label elements often need to be clickable
                    if (tagName === 'label') return 'label';
                    
                    // Interactive list items
                    if (tagName === 'li' && (isPointable || hasClickHandler)) return 'listitem';
                    
                    // Images that might be clickable
                    if (tagName === 'img' && (isPointable || hasClickHandler || el.parentElement?.tagName.toLowerCase() === 'a')) 
                        return 'image';
                    
                    // Headers that might be expandable
                    if (['h1','h2','h3','h4','h5','h6'].includes(tagName) && (isPointable || hasClickHandler))
                        return 'header';
                        
                    // For elements that aren't clearly interactive but have children that are
                    if (el.querySelector('a, button, input, select, textarea')) return 'container';
                    
                    // Last resort: any element with sufficient content should be identifiable
                    if (el.innerText && el.innerText.trim().length > 0 && 
                        ['div', 'span', 'p', 'section', 'article'].includes(tagName))
                        return 'content';
                        
                    return null; // Only truly non-interactive elements get null
                }
                
                // Get all attributes of an element
                function getElementAttributes(el) {
                    const result = {};
                    for (const attr of el.attributes) {
                        result[attr.name] = attr.value;
                    }
                    return result;
                }
                
                // Generate CSS selector for element
                function generateSelector(el) {
                    if (!el) return '';
                    if (el.id) return '#' + CSS.escape(el.id);
                    
                    let selector = el.tagName.toLowerCase();
                    
                    if (el.classList && el.classList.length) {
                        const classes = Array.from(el.classList).slice(0, 2);
                        selector += '.' + classes.join('.');
                    }
                    
                    return selector;
                }
                
                // Get parent info for context
                function getParentInfo(el) {
                    if (!el || !el.parentElement) return null;
                    
                    const parent = el.parentElement;
                    return {
                        tagName: parent.tagName.toLowerCase(),
                        id: parent.id || '',
                        className: parent.className || '',
                        text: cleanText(parent.innerText || parent.textContent || '').substring(0, 50)
                    };
                }
                
                // Find all modal/dialog/popup elements
                function findPopups() {
                    // Expanded selectors for modals/dialogs/popups
                    const selectors = [
                        // ARIA roles and attributes
                        '[role=dialog]', '[role=alertdialog]', '[role=drawer]', '[role=tooltip]', '[role=menu]',
                        '[aria-modal="true"]', '[aria-haspopup="dialog"]', '[aria-haspopup="menu"]',
                        
                        // Data attributes
                        '[data-modal="true"]', '[data-popup="true"]', '[data-dialog="true"]', '[data-overlay="true"]',
                        
                        // Common class patterns
                        '.modal', '.dialog', '.popup', '.overlay', '.pop-up', '.popover', '.tooltip', '.drawer',
                        '.toast', '.notification', '.alert-box',
                        
                        // Framework-specific selectors
                        '.ant-modal', '.ant-drawer', '.ant-popover', // Ant Design
                        '.MuiDialog-root', '.MuiDrawer-root', '.MuiPopover-root', // Material UI
                        '.ReactModal__Content', // React Modal
                        '.modal-dialog', '.modal-content', '.popover', // Bootstrap
                        '.chakra-modal', '.chakra-dialog', // Chakra UI
                        '.ui.modal', '.ui.popup', // Semantic UI
                        '.v-dialog', '.v-menu', // Vuetify
                        
                        // Generic patterns
                        '[class*="modal"]', '[class*="dialog"]', '[class*="popup"]', '[class*="overlay"]',
                        '[class*="drawer"]', '[class*="toast"]', '[class*="tooltip"]', '[class*="popover"]'
                    ];
                    
                    // Find all visible popups
                    const popups = [];
                    
                    // Check for elements matching our selectors
                    for (const sel of selectors) {
                        for (const el of document.querySelectorAll(sel)) {
                            if (isVisible(el)) popups.push(el);
                        }
                    }
                    
                    // Check for fixed/absolute positioned elements with high z-index
                    document.querySelectorAll('div, section, aside').forEach(el => {
                        if (!popups.includes(el) && isVisible(el)) {
                            const style = window.getComputedStyle(el);
                            const position = style.position;
                            const zIndex = parseInt(style.zIndex) || 0;
                            
                            // Fixed/absolute with high z-index are often modals/popups
                            if ((position === 'fixed' || position === 'absolute') && zIndex > 10) {
                                const rect = el.getBoundingClientRect();
                                if (rect.width > 50 && rect.height > 50) { // Reasonable size check
                                    popups.push(el);
                                }
                            }
                        }
                    });
                    
                    // Check for elements near known backdrops (often indicates a modal)
                    const backdrops = document.querySelectorAll('.modal-backdrop, .overlay, .backdrop, .dimmer, [class*="backdrop"], [class*="overlay"]');
                    for (const backdrop of backdrops) {
                        if (isVisible(backdrop)) {
                            const backdropRect = backdrop.getBoundingClientRect();
                            const viewportCenter = {
                                x: window.innerWidth / 2,
                                y: window.innerHeight / 2
                            };
                            
                            // Look for visible centered elements - often these are modals related to backdrops
                            document.querySelectorAll('div, section, aside').forEach(el => {
                                if (!popups.includes(el) && isVisible(el)) {
                                    const rect = el.getBoundingClientRect();
                                    const elementCenter = {
                                        x: rect.left + rect.width / 2,
                                        y: rect.top + rect.height / 2
                                    };
                                    
                                    // Is it centered, reasonable size, and contained within backdrop?
                                    const isCentered = Math.abs(elementCenter.x - viewportCenter.x) < viewportCenter.x / 3 &&
                                                      Math.abs(elementCenter.y - viewportCenter.y) < viewportCenter.y / 3;
                                    
                                    if (isCentered && rect.width > 50 && rect.height > 50) {
                                        popups.push(el);
                                    }
                                }
                            });
                        }
                    }
                    
                    // Remove duplicates
                    return Array.from(new Set(popups));
                }

                // Extract all visible content maintaining the document structure
                function extractStructuredContent() {
                    const extractedContent = [];
                    const detailedElements = [];
                    const processedNodes = new Set();
                    let elementId = 0;
                    
                    // Process elements in document order
                    function processNode(node, depth = 0) {
                        if (!node || processedNodes.has(node)) return;
                        processedNodes.add(node);
                        
                        // Only process elements (not text nodes or other node types)
                        if (node.nodeType !== Node.ELEMENT_NODE) return;
                        
                        // Skip invisible elements
                        if (!isVisible(node)) return;
                        
                        // Get element's own text (excluding child element text)
                        let ownText = '';
                        
                        for (const child of node.childNodes) {
                            if (child.nodeType === Node.TEXT_NODE) {
                                ownText += child.textContent;
                            }
                        }
                        ownText = cleanText(ownText);
                        
                        // Get element type
                        const elementType = getElementType(node);
                        
                        // Replace the conditional element processing block with this:
                        // For interactive elements, add with type prefix
                        if (elementType) {
                            // For input fields, use placeholder or name if there's no text
                            let displayText = ownText;
                            if ((elementType === 'input' || elementType === 'textarea') && !displayText) {
                                displayText = node.getAttribute('placeholder') || 
                                            node.getAttribute('name') || 
                                            node.getAttribute('aria-label') || 
                                            node.getAttribute('title') || '';
                            }
                            
                            // For images without text, use alt text
                            if (elementType === 'image' && !displayText) {
                                displayText = node.getAttribute('alt') || node.getAttribute('title') || 'image';
                            }
                            
                            // Only include elements that have text content or are interactive inputs
                            if (displayText || elementType === 'input' || elementType === 'button' || 
                                elementType === 'checkbox' || elementType === 'radio') {
                                if (!displayText) displayText = elementType; // Default text is the element type
                                
                                // Add element ID to the output
                                extractedContent.push(`[${elementId}][${elementType}]${displayText}`);
                                
                                // Get detailed information about the element
                                const rect = node.getBoundingClientRect();
                                const elementInfo = {
                                    id: elementId,
                                    tagName: node.tagName,
                                    type: elementType,
                                    text: displayText,
                                    x: rect.left + window.pageXOffset,
                                    y: rect.top + window.pageYOffset,
                                    width: rect.width,
                                    height: rect.height,
                                    center_x: rect.left + rect.width/2 + window.pageXOffset,
                                    center_y: rect.top + rect.height/2 + window.pageYOffset,
                                    inViewport: (
                                        rect.top >= 0 && 
                                        rect.left >= 0 && 
                                        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                                        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                                    ),
                                    attributes: getElementAttributes(node),
                                    cssSelector: generateSelector(node),
                                    parentInfo: getParentInfo(node),
                                    innerHTML: node.innerHTML.substring(0, 200),
                                    childElementCount: node.childElementCount,
                                    isDisabled: node.disabled || node.hasAttribute('disabled'),
                                    zIndex: parseInt(window.getComputedStyle(node).zIndex) || 0
                                };
                                
                                detailedElements.push(elementInfo);
                                elementId++;
                            }
                        } 
                        // For non-interactive elements with text, just add the text
                        else if (ownText && ownText.length > 1) {
                            extractedContent.push(ownText);
                        }
                        
                        // Process children in document order
                        for (const child of node.children) {
                            processNode(child, depth + 1);
                        }
                    }
                    
                    // Start processing from body
                    processNode(document.body);

                    // Now process popups/modals/dialogs
                    const popups = findPopups();
                    for (const popup of popups) {
                        // Mark popup start
                        extractedContent.push('--- Popup Window Detected ---');
                        processNode(popup);
                        extractedContent.push('--- End of Popup ---');
                    }
                    
                    return {
                        content: extractedContent,
                        elements: detailedElements
                    };
                }
                
                // Extract content in document structure order
                return extractStructuredContent();
            }
            """)
            
            # Store the detailed elements information
            page_elements = page_content['elements']
            
            # Post-process the content - clean up formatting and structure
            result = []
            current_line = ""
            
            # Add each item, grouping related content on the same line
            for item in page_content['content']:
                # Skip elements where type matches display text (e.g., "[49][button]button")
                if item.startswith('['):
                    # Parse the element format: [id][type]text
                    parts = item.split(']', 2)
                    if len(parts) >= 3:
                        element_type = parts[1][1:]  # Get the type without '['
                        display_text = parts[2]      # Get the display text
                        
                        # Skip if the element type exactly matches its display text
                        if display_text.strip() == element_type:
                            continue
                
                # Start a new line for interactive elements or if current line is empty
                if item.startswith('[') or not current_line:
                    if (current_line):  # Add the previous line if it exists
                        result.append(current_line)
                    current_line = item
                
                # Keep short content items together if they're related (price, ratings, etc.)
                elif len(item) < 30 and len(current_line) + len(item) + 1 < 80:
                    current_line += " " + item
                
                # Otherwise start a new line
                else:
                    result.append(current_line)
                    current_line = item
            
            # Don't forget the last line
            if current_line:
                result.append(current_line)
            
            # Format the result and limit length
            formatted_result = "\n".join(result).strip()
            
            return formatted_result
            
    except Exception as e:
        return f"Error analyzing page: {str(e)}"