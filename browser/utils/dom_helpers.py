"""
DOM helper utilities for working with browser elements.
"""

import re
import asyncio

# Global variable to store the page
page = None

def initialize(browser_page):
    """Initialize the DOM helpers module."""
    global page
    page = browser_page

def _parse_click_target(target_description):
    """Parse target description into ID, type and text components."""
    target_id = None
    target_type = None
    target_text = None
    is_structured = False
    
    # Try to parse structured input (dict or JSON format)
    if isinstance(target_description, dict):
        # Handle case where input is already a dictionary
        target_id = target_description.get('id')
        target_type = target_description.get('type', '').lower() if target_description.get('type') else None
        target_text = target_description.get('text', '').lower() if target_description.get('text') else None
        if target_id or target_type or target_text:
            is_structured = True
            print(f"Using dictionary input: id='{target_id}', type='{target_type}', text='{target_text}'")
    # Handle JSON string input
    elif isinstance(target_description, str) and target_description.startswith('{') and target_description.endswith('}'):
        try:
            # First try to parse as JSON
            import json
            try:
                parsed_input = json.loads(target_description)
                if isinstance(parsed_input, dict):
                    target_id = parsed_input.get('id')
                    target_type = parsed_input.get('type', '').lower() if parsed_input.get('type') else None
                    target_text = parsed_input.get('text', '').lower() if parsed_input.get('text') else None
                    if target_id or target_type or target_text:
                        is_structured = True
                        print(f"Using JSON structured input: id='{target_id}', type='{target_type}', text='{target_text}'")
            except json.JSONDecodeError:
                # If not valid JSON, fall back to simple parsing
                content = target_description.strip('{}').strip()
                parts = [part.strip() for part in content.split(',')]
                
                for part in parts:
                    if ':' in part:
                        key, value = [item.strip() for item in part.split(':', 1)]
                        if key.lower() == 'id':
                            target_id = value
                        elif key.lower() == 'type':
                            target_type = value.lower()
                        elif key.lower() == 'text':
                            target_text = value.lower()
                
                if target_id or target_type or target_text:
                    is_structured = True
                    print(f"Using structured input: id='{target_id}', type='{target_type}', text='{target_text}'")
        except Exception as e:
            print(f"Error parsing input: {e}, using as free text instead")
    
    # Handle direct ID pattern extraction (like [3][button]Submit)
    if not is_structured and isinstance(target_description, str):
        id_type_pattern = re.match(r'\[(\d+)\]\[(.*?)\](.*)', target_description)
        if id_type_pattern:
            target_id = id_type_pattern.group(1)
            target_type = id_type_pattern.group(2).lower()
            target_text = id_type_pattern.group(3)
            is_structured = True
            print(f"Extracted from pattern: id='{target_id}', type='{target_type}', text='{target_text}'")
    
    return target_id, target_type, target_text, is_structured

async def _find_element(target_type, target_text, is_structured, relaxed=False, target_description=None):
    """Find an element based on type and text with improved selection logic."""
    js_code = """
        (params) => {
            const { targetType, targetText, isStructured, relaxed } = params;
            
            // Helper function to check if element is visible
            function isVisible(el) {
                if (!el.getBoundingClientRect) return false;
                const rect = el.getBoundingClientRect();
                if (rect.width <= 0 || rect.height <= 0) return false;
                const style = window.getComputedStyle(el);
                return !(style.display === 'none' || style.visibility === 'hidden' || 
                    parseFloat(style.opacity) <= 0.1);
            }
            
            // Helper to normalize and clean text
            function normalizeText(text) {
                if (!text) return '';
                // First normalize spaces
                text = text.replace(/\\s+/g, ' ').trim().toLowerCase();
                // Then normalize common separators to help with matching
                text = text.replace(/\\s*\\/\\s*/g, '/'); // Normalize "Cash on Delivery / Pay on Delivery" -> "Cash on Delivery/Pay on Delivery"
                return text;
            }
            
            // Helper to get element type with better categorization
            function getElementType(el) {
                const tagName = el.tagName.toLowerCase();
                const type = el.getAttribute('type')?.toLowerCase();
                const role = el.getAttribute('role')?.toLowerCase();
                
                // Basic element types
                if (tagName === 'a') return 'link';
                if (tagName === 'button') return 'button';
                
                // Input elements
                if (tagName === 'input') {
                    if (['submit', 'button', 'reset'].includes(type)) return 'button';
                    if (['text', 'email', 'password', 'search', 'tel', 'url'].includes(type)) return 'input';
                    if (type === 'checkbox') return 'checkbox';
                    if (type === 'radio') return 'radio';
                    return 'input';
                }
                
                // Other form elements
                if (tagName === 'select') return 'dropdown';
                if (tagName === 'textarea') return 'textarea';
                
                // ARIA roles
                if (role === 'button') return 'button';
                if (role === 'link') return 'link';
                if (role === 'checkbox') return 'checkbox';
                if (role === 'radio') return 'radio';
                if (role === 'textbox' || role === 'searchbox') return 'input';
                if (role === 'combobox' || role === 'listbox') return 'dropdown';
                if (role === 'tab') return 'tab';
                
                // Look for common payment method patterns
                if ((tagName === 'div' || tagName === 'label' || tagName === 'span') && 
                    (el.innerText || '').toLowerCase().includes('cash on delivery')) {
                    return 'button';
                }
                
                // Interactive elements detection (improved)
                if ((tagName === 'div' || tagName === 'span')) {
                    if (el.onclick || el.getAttribute('onclick')) return 'button';
                    if (window.getComputedStyle(el).cursor === 'pointer') return 'button';
                    if (el.getAttribute('tabindex') === '0') return 'button';
                    // Special case for payment selection - likely a clickable div/label
                    if (el.classList.contains('payment-option') || 
                        el.classList.contains('payment-method') || 
                        el.parentElement?.classList.contains('payment-methods')) {
                        return 'button';
                    }
                }
                
                return null;
            }
            
            // Enhanced function to get element text from all possible sources
            function getElementText(el) {
                // Check for actual content first (innerText is most reliable)
                let text = normalizeText(el.innerText || '');
                
                // If no innerText, try textContent (includes hidden text)
                if (!text) text = normalizeText(el.textContent || '');
                
                // For labels that are associated with inputs (common for payment methods)
                if (el.tagName.toLowerCase() === 'label') {
                    const forId = el.getAttribute('for');
                    if (forId) {
                        const input = document.getElementById(forId);
                        if (input && input.value) {
                            text = normalizeText(text + ' ' + input.value);
                        }
                    }
                }
                
                // For elements without visible text, check attributes
                if (!text) {
                    // Check all possible text attributes in priority order
                    text = normalizeText(
                        el.getAttribute('aria-label') || 
                        el.getAttribute('placeholder') || 
                        el.getAttribute('value') ||
                        el.getAttribute('title') ||
                        el.getAttribute('name') || 
                        el.getAttribute('alt') ||
                        el.id || ''
                    );
                }
                
                // Special case for payment elements with images
                if (!text && (el.classList.contains('payment-option') || el.parentElement?.classList.contains('payment-methods'))) {
                    // Look for images with alt text inside the element
                    const images = el.querySelectorAll('img[alt]');
                    for (const img of images) {
                        const altText = img.getAttribute('alt');
                        if (altText) text = normalizeText(altText);
                    }
                }
                
                return text;
            }
            
            // Generate a unique CSS selector for an element
            function generateSelector(el) {
                if (!el) return '';
                if (el.id) return '#' + CSS.escape(el.id);
                
                let selector = el.tagName.toLowerCase();
                
                // Add classes (up to 2 for specificity without being too specific)
                if (el.classList && el.classList.length) {
                    const classes = Array.from(el.classList).slice(0, 2);
                    selector += '.' + classes.join('.');
                }
                
                // Add common attributes that help identification
                ['type', 'name', 'placeholder', 'role'].forEach(attr => {
                    if (el.hasAttribute(attr)) {
                        selector += `[${attr}="${CSS.escape(el.getAttribute(attr))}"]`;
                    }
                });
                
                return selector;
            }
            
            // Generate XPath for element (useful for rare edge cases)
            function getXPath(el) {
                if (!el) return '';
                
                const parts = [];
                let current = el;
                
                while (current && current.nodeType === Node.ELEMENT_NODE) {
                    let idx = 0;
                    let sibling = current.previousSibling;
                    
                    while (sibling) {
                        if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === current.tagName) {
                            idx++;
                        }
                        sibling = sibling.previousSibling;
                    }
                    
                    const tagName = current.tagName.toLowerCase();
                    let idxStr = '';
                    
                    if (idx > 0 || current.nextSibling && current.nextSibling.nodeType === Node.ELEMENT_NODE && 
                        current.nextSibling.tagName === current.tagName) {
                        idxStr = `[${idx + 1}]`;
                    }
                    
                    parts.unshift(tagName + idxStr);
                    current = current.parentNode;
                    
                    // Limit XPath length to avoid extremely long paths
                    if (parts.length >= 8) {
                        parts.unshift('...');
                        break;
                    }
                }
                
                return '/' + parts.join('/');
            }
            
            // Extract important attributes from element
            function getElementAttributes(el) {
                if (!el) return {};
                
                const result = {};
                const importantAttrs = [
                    'id', 'class', 'name', 'type', 'role', 'aria-label', 'href', 
                    'value', 'placeholder', 'for', 'title', 'alt', 'data-testid'
                ];
                
                importantAttrs.forEach(attr => {
                    if (el.hasAttribute(attr)) {
                        result[attr] = el.getAttribute(attr);
                    }
                });
                
                // Add any data-* attributes
                for (let i = 0; i < el.attributes.length; i++) {
                    const attr = el.attributes[i];
                    if (attr.name.startsWith('data-') && !result[attr.name]) {
                        result[attr.name] = attr.value;
                    }
                });
                
                return result;
            }
            
            // Get parent information for context
            function getParentInfo(el) {
                if (!el || !el.parentElement) return null;
                
                const parent = el.parentElement;
                return {
                    tagName: parent.tagName.toLowerCase(),
                    id: parent.id || '',
                    className: parent.className || '',
                    text: normalizeText(parent.innerText || '').substring(0, 50)
                };
            }
            
            // Look for child elements with matching text
            function findTextInChildren(el, targetDesc) {
                const normalizedTarget = normalizeText(targetDesc);
                let foundText = '';
                
                // Check all child nodes recursively
                function checkNode(node) {
                    if (node.nodeType === Node.TEXT_NODE) {
                        const nodeText = normalizeText(node.textContent);
                        if (nodeText.includes(normalizedTarget)) {
                            foundText = nodeText;
                            return true;
                        }
                    } else if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check this element's text
                        const elText = normalizeText(node.innerText || node.textContent || '');
                        if (elText.includes(normalizedTarget)) {
                            foundText = elText;
                            return true;
                        }
                        
                        // Check child elements
                        for (const child of node.childNodes) {
                            if (checkNode(child)) return true;
                        }
                    }
                    return false;
                }
                
                checkNode(el);
                return foundText;
            }
            
            // Element scoring with improved algorithm
            function scoreElement(el, elementType, elementText) {
                if (!isVisible(el)) return 0;
                if (!elementType) return 0;
                
                const targetDesc = normalizeText(isStructured ? targetText || '' : targetText || '');
                if (!targetDesc && !targetType) return 0;
                
                // Skip elements with no text unless they're the right type and we're in relaxed mode
                if (!elementText && !relaxed) return 0;
                
                let score = 0;
                
                // Type matching (30% of scoring weight)
                if (targetType) {
                    if (elementType === targetType) {
                        score += 150; // Exact type match
                    }
                    else if (relaxed && (elementType.includes(targetType) || targetType.includes(elementType))) {
                        score += 40; // Partial type match when relaxed
                    }
                    else if (!relaxed) {
                        return 0; // No match on type when not relaxed
                    }
                }
                
                // Text matching (70% of scoring weight)
                if (targetDesc) {
                    // Reject empty text elements if target has text
                    if (!elementText && targetDesc) {
                        if (relaxed) {
                            // Check text in children
                            const childText = findTextInChildren(el, targetDesc);
                            if (!childText) return 0;
                            elementText = childText;
                        } else {
                            return 0;
                        }
                    }
                    
                    // Exact match - highest priority
                    if (elementText === targetDesc) {
                        score += 450; // Increased priority for exact match
                    }
                    // Full match with case/whitespace differences
                    else if (elementText.replace(/[^a-z0-9]/gi, '') === targetDesc.replace(/[^a-z0-9]/gi, '')) {
                        score += 400;
                    }
                    // Element contains target text completely
                    else if (elementText.includes(targetDesc)) {
                        // Prioritize by precision of match
                        const precision = targetDesc.length / elementText.length;
                        score += Math.round(300 * precision);
                    }
                    // Special case for composite texts like "Cash on Delivery/Pay on Delivery"
                    else if (targetDesc.includes('/')) {
                        const targetParts = targetDesc.split('/');
                        for (const part of targetParts) {
                            if (part.length > 3 && elementText.includes(part)) {
                                const precision = part.length / elementText.length;
                                score += Math.round(200 * precision);
                            }
                        }
                    }
                    // Target contains element text (if element text is substantial)
                    else if (targetDesc.includes(elementText) && elementText.length > 3) {
                        const coverage = elementText.length / targetDesc.length;
                        score += Math.round(100 * coverage);
                    }
                    // Word matching (for partial matches)
                    else if (relaxed || targetDesc.length > 15) {
                        const targetWords = targetDesc.split(' ');
                        const elementWords = elementText.split(' ');
                        
                        let matchCount = 0;
                        for (const word of targetWords) {
                            if (word.length > 2 && 
                                elementWords.some(w => w.includes(word) || word.includes(w))) {
                                matchCount++;
                            }
                        }
                        
                        score += matchCount * (relaxed ? 15 : 25);
                    }
                }
                
                // Boost for elements in viewport (accessibility bonus)
                const rect = el.getBoundingClientRect();
                const inViewport = (
                    rect.top >= 0 && 
                    rect.left >= 0 && 
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
                
                if (inViewport) {
                    score += 25; // Visible elements are preferred
                }
                
                // Penalty for elements at the top-left corner (likely navigation elements, not content)
                if (rect.top < 50 && rect.left < 50) {
                    score -= 50;
                }
                
                // Extra penalty for empty text
                if (!elementText) {
                    score -= 100;
                }
                
                return score;
            }
            
            // Find all elements and evaluate them
            const candidates = [];
            const allElements = document.querySelectorAll('*');
            
            allElements.forEach(el => {
                const elementType = getElementType(el);
                if (!elementType) return; // Skip non-interactive elements
                
                // Skip disabled elements unless explicitly requested
                if (el.disabled && !targetText?.includes('disabled')) return;
                
                const elementText = getElementText(el);
                
                // Calculate match score
                const score = scoreElement(el, elementType, elementText);
                
                // Only include elements with some match
                if (score > 0) {
                    const rect = el.getBoundingClientRect();
                    
                    candidates.push({
                        score: score,
                        tagName: el.tagName,
                        type: elementType,
                        text: elementText.substring(0, 100), // Limit text length
                        x: rect.left + window.pageXOffset,
                        y: rect.top + window.pageYOffset,
                        width: rect.width,
                        height: rect.height,
                        center_x: rect.left + rect.width/2 + window.pageXOffset,
                        center_y: rect.top + rect.height/2 + window.pageYOffset,
                        inViewport: rect.top >= 0 && rect.left >= 0 && 
                                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                                rect.right <= (window.innerWidth || document.documentElement.clientWidth),
                        // Enhanced element identification
                        attributes: getElementAttributes(el),
                        cssSelector: generateSelector(el),
                        xpath: getXPath(el),
                        parentInfo: getParentInfo(el),
                        innerHTML: el.innerHTML.substring(0, 200), // Limited for size
                        childElementCount: el.childElementCount,
                        isDisabled: el.disabled || el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true',
                        zIndex: parseInt(window.getComputedStyle(el).zIndex) || 0
                    });
                }
            });
            
            // Sort candidates by score (highest first)
            candidates.sort((a, b) => b.score - a.score);
            
            // Include top candidates for debugging
            const alternatives = candidates.slice(1, 4).map(c => ({
                text: c.text, 
                type: c.type,
                score: c.score,
                cssSelector: c.cssSelector
            }));
            
            // Return best match with debug info
            return candidates.length > 0 ? {...candidates[0], alternatives} : null;
        }
    """
    
    free_text = None if is_structured else (target_text or target_description or "")
    return await page.evaluate(js_code, {
        "targetType": target_type,
        "targetText": target_text if is_structured else free_text,
        "isStructured": is_structured,
        "relaxed": relaxed
    })

async def _scroll_element_into_view(element):
    """
    Scroll an element into view using DOM methods.
    
    Args:
        element (dict): Element information with at least center_x, center_y
    """
    try:
        # Use scrollIntoView via JS for more reliable scrolling
        await page.evaluate("""
            (coords) => {
                const element = document.elementFromPoint(
                    coords.x - window.pageXOffset, 
                    coords.y - window.pageYOffset
                );
                
                if (element) {
                    // Use smooth scrolling with centering
                    element.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center',
                        inline: 'center'
                    });
                    return true;
                } else {
                    // Fallback to coordinate-based scrolling
                    window.scrollTo({
                        top: coords.y - (window.innerHeight / 2),
                        left: coords.x - (window.innerWidth / 2),
                        behavior: 'smooth'
                    });
                    return false;
                }
            }
        """, {
            'x': element['center_x'],
            'y': element['center_y']
        })
    except Exception as e:
        print(f"Error scrolling element into view: {e}")
        # Fallback to regular scrolling
        await page.evaluate(f"""
            () => window.scrollTo({{
                top: {element['center_y']} - (window.innerHeight / 2),
                behavior: 'smooth'
            }})
        """)