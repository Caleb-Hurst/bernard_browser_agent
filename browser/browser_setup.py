from playwright.sync_api import sync_playwright

def inject_cursor_script():
    return """
    // Create a custom cursor element
    const cursor = document.createElement('div');
    cursor.id = 'ai-agent-cursor';
    cursor.style.position = 'absolute';
    cursor.style.width = '20px';
    cursor.style.height = '20px';
    cursor.style.backgroundColor = 'rgba(255, 0, 0, 0.3)';
    cursor.style.border = '2px solid red';
    cursor.style.borderRadius = '50%';
    cursor.style.transform = 'translate(-50%, -50%)';
    cursor.style.pointerEvents = 'none';
    cursor.style.zIndex = '999999';
    cursor.style.transition = 'left 0.05s, top 0.05s';

    // Add cursor to the page
    document.addEventListener('DOMContentLoaded', function() {
        document.body.appendChild(cursor);
    });

    // If page already loaded, add cursor now
    if (document.body) {
        document.body.appendChild(cursor);
    }

    // Function to update cursor position
    window.updateAICursor = function(x, y) {
        if (cursor && document.body && document.body.contains(cursor)) {
            cursor.style.left = x + 'px';
            cursor.style.top = y + 'px';
        } else if (document.body) {
            document.body.appendChild(cursor);
            cursor.style.left = x + 'px';
            cursor.style.top = y + 'px';
        }
    };
    """

def initialize_browser(options, connection_options=None):
    from playwright.sync_api import sync_playwright
    import os

    playwright = sync_playwright().start()
    print(f"Launching new browser with options: {options}")
    browser = playwright.chromium.launch(**options)
    context = browser.new_context(
        viewport=None,
        record_video_dir="videos/",
        record_video_size={"width": 1280, "height": 720}
    )
    print(f"[DEBUG] Context video dir: {context._options.get('record_video_dir', None)}")
    page = context.new_page()
    print(f"[DEBUG] Page video property (should be None until closed): {getattr(page, 'video', None)}")

    # Inject cursor visualization CSS and JavaScript
    page.add_init_script(inject_cursor_script())

    # Add script to prevent new tabs from opening
    page.add_init_script("""
        window.open = function(url, name, features) {
            console.log('Intercepted window.open call for URL:', url);
            if (url) {
                window.location.href = url;
            }
            return window;
        };

        // Override link behavior to prevent target="_blank"
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a');
            if (link && link.target === '_blank') {
                e.preventDefault();
                console.log('Intercepted _blank link click for URL:', link.href);
                window.location.href = link.href;
            }
        }, true);
    """)

    # Navigate to a blank page first to ensure script loading
    page.goto('about:blank')

    # Ensure cursor is created and function is available
    page.evaluate("""
        () => {
            if (!document.getElementById('ai-agent-cursor')) {
                const cursor = document.createElement('div');
                cursor.id = 'ai-agent-cursor';
                cursor.style.position = 'absolute';
                cursor.style.width = '20px';
                cursor.style.height = '20px';
                cursor.style.backgroundColor = 'rgba(255, 0, 0, 0.3)';
                cursor.style.border = '2px solid red';
                cursor.style.borderRadius = '50%';
                cursor.style.transform = 'translate(-50%, -50%)';
                cursor.style.pointerEvents = 'none';
                cursor.style.zIndex = '999999';
                cursor.style.transition = 'left 0.05s, top 0.05s';
                document.body.appendChild(cursor);
            }

            if (typeof window.updateAICursor !== 'function') {
                window.updateAICursor = function(x, y) {
                    const cursor = document.getElementById('ai-agent-cursor');
                    if (cursor) {
                        cursor.style.left = x + 'px';
                        cursor.style.top = y + 'px';
                    } else {
                        console.error('Cursor element not found');
                    }
                };
            }
        }
    """)

    user_agent = page.evaluate('() => navigator.userAgent')
    print(f"Browser setup successful. User agent: {user_agent}")

    # After test, close page and context to finalize video
    video_path = None
    try:
        page.close()
        context.close()
        print(f"[DEBUG] Page video property after close: {getattr(page, 'video', None)}")
        if hasattr(page, 'video') and page.video:
            video_path = page.video.path()
            print(f"[DEBUG] video_path after close: {video_path}")
        else:
            print("[DEBUG] No video property on page after close.")
    except Exception as e:
        print(f"Warning: Could not get video path: {e}")

    videos_dir = os.path.join(os.getcwd(), "videos")
    if os.path.exists(videos_dir):
        print(f"[DEBUG] Listing files in videos/: {os.listdir(videos_dir)}")
    else:
        print("[DEBUG] videos/ directory does not exist.")

    return playwright, browser, page, video_path

def close_browser(playwright, browser, is_connected=False):
    try:
        if is_connected:
            # If connected to existing browser, just disconnect
            print("Disconnecting from browser (browser will remain open)")
            playwright.stop()
            return "Disconnected from browser successfully"
        else:
            # If browser was launched by us, close it
            browser.close()
            playwright.stop()
            return "Browser closed successfully"
    except Exception as e:
        return f"Error closing browser: {str(e)}"
