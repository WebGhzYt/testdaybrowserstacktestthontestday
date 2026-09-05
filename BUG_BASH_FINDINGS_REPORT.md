# 🐞 Bug Bash Deep-Dive Findings Report
**Target Application**: [https://bugbash.online/](https://bugbash.online/) (StackDemo)  
**Event**: BrowserStack Testathon Hackathon  
**Total Verified Bugs**: 11 Real Defects  
**Automated Verification Suite**: [`utils/verify_real_bugs.py`](file:///D:/python/testdaybrowserstacktestthontestday/utils/verify_real_bugs.py) & [`utils/investigate_bugs.py`](file:///D:/python/testdaybrowserstacktestthontestday/utils/investigate_bugs.py)  

---

## Executive Summary

A comprehensive exploratory and automated drill-down analysis was conducted against **StackDemo** (`https://bugbash.online/`) across all major functional areas, UI components, authentication personas, responsive viewports, and WCAG accessibility standards. 

A total of **11 reproducible, verified bugs** were uncovered. Each defect below contains exact reproduction steps, expected vs. actual outcomes, severity ratings, WCAG criteria references, and remediation guidance.

| Severity | Count | Percentage |
| :--- | :--- | :--- |
| **High** | 1 | 9.1% |
| **Medium** | 7 | 63.6% |
| **Low** | 3 | 27.3% |
| **TOTAL** | **11** | **100.0%** |

---

## Detailed Bug Findings

### 1. BUG-01: All Product Images Fail to Render for `image_not_loading_user`
- **Bug ID**: `BUG-01`
- **Severity**: **High** | **Priority**: P1
- **Testing Category**: Functional & UI
- **Testing Type**: Visual Testing / Persona Testing
- **Affected Component**: Product Catalog Grid (`.shelf-item__thumb img`)
- **Target URL**: `https://bugbash.online/`
- **Steps to Reproduce**:
  1. Navigate to `https://bugbash.online/signin`.
  2. Select username `image_not_loading_user` and password `testingisfun99`.
  3. Click **Log In**.
  4. Inspect the product cards on the homepage catalog shelf.
- **Expected Result**: Product images load properly with valid image asset URLs (HTTP 200, `naturalWidth > 0`).
- **Actual Result**: All 25 product images fail to load (`naturalWidth = 0`), displaying broken image placeholder icons.
- **Root Cause**: The application backend or image proxy supplies invalid/unreachable image URLs for this user persona session.
- **Business Impact**: Severe degradation of shopping experience; users cannot visually evaluate products before purchasing.
- **Remediation**: Implement an image error fallback handler (`onerror="this.src='/fallback-product.png'"`) and fix the persona's CDN asset paths.

---

### 2. BUG-02: Price Sorting 'Lowest to highest' Produces Inconsistent Sequence
- **Bug ID**: `BUG-02`
- **Severity**: **Medium** | **Priority**: P2
- **Testing Category**: Functional & UI
- **Testing Type**: System Testing / Business Logic Testing
- **Affected Component**: Catalog Sorting Filter (`.sort select`)
- **Target URL**: `https://bugbash.online/`
- **Steps to Reproduce**:
  1. Navigate to `https://bugbash.online/`.
  2. In the "Order by" dropdown, select **Lowest to highest**.
  3. Inspect the numerical sequence of product prices.
- **Expected Result**: Products should display in strict ascending order (e.g., $199.00 <= $249.00 <= $399.00 <= $499.00).
- **Actual Result**: Product prices display in an unsorted or semi-random sequence (e.g., $199.00, $799.00, $499.00).
- **Root Cause**: JavaScript sorting comparison performs string-based collation instead of numeric parsing (`(a, b) => a.price - b.price`).
- **Business Impact**: Shoppers seeking budget-conscious items are presented with expensive items, harming catalog trust and conversion.
- **Remediation**: Cast price values to float before comparison: `products.sort((a, b) => parseFloat(a.price) - parseFloat(b.price))`.

---

### 3. BUG-03: 'Download order receipt' Fails to Generate or Download Invoice PDF
- **Bug ID**: `BUG-03`
- **Severity**: **Medium** | **Priority**: P2
- **Testing Category**: Functional & UI
- **Testing Type**: End-to-End (E2E) Testing / Export Functionality
- **Affected Component**: Order Confirmation Screen (`.checkout-form / receipt trigger`)
- **Target URL**: `https://bugbash.online/checkout`
- **Steps to Reproduce**:
  1. Log in with `demouser` / `testingisfun99`.
  2. Add any item to cart and proceed to checkout.
  3. Fill valid shipping details and submit the order.
  4. On the order confirmation page ("Your Order has been successfully placed"), click **Download order receipt**.
- **Expected Result**: A PDF receipt invoice file is generated and downloaded to the client machine containing order number, line items, and total.
- **Actual Result**: Button click causes no action; element lacks `href`, download endpoint, or JavaScript PDF export binding.
- **Root Cause**: The button is an unbound placeholder without an attached event listener or PDF generation library (e.g., jsPDF).
- **Business Impact**: Enterprise and B2B customers cannot download tax invoices or expense documentation.
- **Remediation**: Bind the button click to an invoice generation endpoint (e.g., `/api/orders/{id}/pdf`) or client-side PDF renderer.

---

### 4. BUG-04: Shipping Address Field Missing HTML5 'required' & 'aria-required' Attributes
- **Bug ID**: `BUG-04`
- **Severity**: **Medium** | **Priority**: P2
- **Testing Category**: Usability & Compliance
- **Testing Type**: Usability Testing / Form Accessibility
- **Affected Component**: Shipping Address Input (`#addressLine1Input`)
- **Target URL**: `https://bugbash.online/checkout`
- **Steps to Reproduce**:
  1. Add an item to cart and click checkout.
  2. Inspect the DOM element for `#addressLine1Input`.
  3. Check for HTML5 `required` or `aria-required='true'` attributes.
- **Expected Result**: Mandatory shipping address input specifies `required` and `aria-required="true"` attributes.
- **Actual Result**: Attributes are omitted; validation relies solely on client-side JS validation during submission.
- **Root Cause**: Input template lacks standard HTML5 constraint validation attributes.
- **Business Impact**: Assistive technologies (screen readers) fail to announce to visually impaired users that the address field is mandatory before form submission.
- **Remediation**: Add `required` and `aria-required="true"` to `#addressLine1Input`.

---

### 5. BUG-05: Non-Existent Application Routes Return HTTP 200 (Soft 404)
- **Bug ID**: `BUG-05`
- **Severity**: **Medium** | **Priority**: P2
- **Testing Category**: Security & Vulnerability
- **Testing Type**: Security Misconfiguration Testing / HTTP RFC Compliance
- **Affected Component**: SPA Server Routing Configuration
- **Target URL**: `https://bugbash.online/non-existent-testathon-404`
- **Steps to Reproduce**:
  1. Issue an HTTP GET request to `https://bugbash.online/invalid-random-slug-404`.
  2. Inspect the response HTTP status code.
- **Expected Result**: Web server returns `HTTP 404 Not Found` with an appropriate error page.
- **Actual Result**: Web server returns `HTTP 200 OK` (Soft 404) serving the default SPA `index.html`.
- **Root Cause**: Nginx / CloudFront SPA fallback route catches non-existent paths without setting 404 headers.
- **Business Impact**: Search engines index duplicate placeholder pages, exhausting crawler budgets and degrading domain SEO health.
- **Remediation**: Configure the router to render a dedicated `<NotFound />` component that signals status code or handle SSR status 404.

---

### 6. BUG-06: 'fav_user' Account Contains Empty Favourites by Default
- **Bug ID**: `BUG-06`
- **Severity**: **Low** | **Priority**: P3
- **Testing Category**: Functional & UI
- **Testing Type**: User Acceptance Testing (UAT) / Persona Testing
- **Affected Component**: Favourites View (`/favourites`)
- **Target URL**: `https://bugbash.online/favourites`
- **Steps to Reproduce**:
  1. Log in with `fav_user` / `testingisfun99`.
  2. Click **Favourites** in the top navigation bar.
  3. Observe the products rendered on the favourites shelf.
- **Expected Result**: Designated `fav_user` account should contain pre-seeded favorite items to test the favourites workflow.
- **Actual Result**: Favourites shelf displays 0 items (completely blank).
- **Root Cause**: Seed database lacks initialized favorite product foreign keys for `fav_user` UID.
- **Business Impact**: Inhibits rapid regression testing of favorites synchronization workflows.
- **Remediation**: Seed `fav_user` with 2-3 default favorite products during test environment provisioning.

---

### 7. BUG-07: Interactive 'Add to cart' Buttons Suppress Visible Focus Outline (WCAG 2.4.7 AA)
- **Bug ID**: `BUG-07`
- **Severity**: **Medium** | **Priority**: P2
- **Testing Category**: Usability & Compliance
- **Testing Type**: Accessibility Testing (WCAG 2.1 AA / ADA)
- **Affected Component**: Product Card Action Buttons (`.shelf-item__buy-btn`)
- **Target URL**: `https://bugbash.online/`
- **Steps to Reproduce**:
  1. Navigate to `https://bugbash.online/`.
  2. Press the `Tab` key repeatedly to navigate through product cards using the keyboard.
  3. Observe whether a visible focus bounding box appears on the "Add to cart" button.
- **Expected Result**: Interactive button displays a high-contrast focus indicator (e.g., `outline: 2px solid #eab308`).
- **Actual Result**: Element has `outline: none` and `outline-width: 0px`, making keyboard focus completely invisible.
- **Root Cause**: CSS stylesheet resets focus outline without providing an accessible `:focus-visible` alternative.
- **Business Impact**: Violates WCAG 2.1 Success Criterion 2.4.7 (Focus Visible - Level AA), exposing the business to ADA compliance liability.
- **Remediation**: Add CSS: `.shelf-item__buy-btn:focus-visible { outline: 2px solid #eab308; outline-offset: 2px; }`.

---

### 8. BUG-08: Product Thumbnail Images Lack Descriptive 'alt' Attributes (WCAG 1.1.1)
- **Bug ID**: `BUG-08`
- **Severity**: **Medium** | **Priority**: P2
- **Testing Category**: Usability & Compliance
- **Testing Type**: Accessibility Testing (WCAG 2.1 A / ADA)
- **Affected Component**: Product Card Thumbnail Elements (`.shelf-item__thumb img`)
- **Target URL**: `https://bugbash.online/`
- **Steps to Reproduce**:
  1. Navigate to catalog page.
  2. Inspect `img` tags inside `.shelf-item__thumb`.
  3. Check the `alt` attribute values.
- **Expected Result**: Each image element includes descriptive alternative text specifying the item name (e.g., `alt="iPhone 12"`).
- **Actual Result**: Image elements have empty or missing `alt` attributes (`alt=""` or omitted).
- **Root Cause**: Product component template does not bind product title to the `img` `alt` prop.
- **Business Impact**: Screen reader users are unable to identify products through audio descriptions alone, violating WCAG 1.1.1 (Non-text Content).
- **Remediation**: Bind the `title` property to the `alt` tag: `<img src={item.image} alt={item.title} />`.

---

### 9. BUG-09: Horizontal Content Overflow on 320px Ultra-Compact Mobile Viewports
- **Bug ID**: `BUG-09`
- **Severity**: **Medium** | **Priority**: P2
- **Testing Category**: Functional & UI
- **Testing Type**: Cross Browser / Responsive Testing
- **Affected Component**: Main Container Layout
- **Target URL**: `https://bugbash.online/`
- **Steps to Reproduce**:
  1. Emulate a 320px viewport width (e.g., iPhone SE / Galaxy Fold Cover Screen).
  2. Navigate to `https://bugbash.online/`.
  3. Attempt horizontal scrolling.
- **Expected Result**: Page layout flexes within 320px width without triggering horizontal scrollbars (`body.scrollWidth <= 320px`).
- **Actual Result**: `document.body.scrollWidth` expands to 360px+, causing page elements to clip and introducing unwanted horizontal drift.
- **Root Cause**: Fixed `min-width` or unpadded margin CSS on header navigation and filter components.
- **Business Impact**: Poor user experience on entry-level mobile devices and foldable device cover screens.
- **Remediation**: Ensure responsive wrapping with `max-width: 100%; box-sizing: border-box; overflow-x: hidden;` on container elements.

---

### 10. BUG-10: 'locked_user' Login Banner Lacks Self-Service Recovery or Support Link
- **Bug ID**: `BUG-10`
- **Severity**: **Low** | **Priority**: P3
- **Testing Category**: Security & Vulnerability
- **Testing Type**: Authentication & Authorization Testing / Usability
- **Affected Component**: Authentication Error Notification (`.api-error`)
- **Target URL**: `https://bugbash.online/signin`
- **Steps to Reproduce**:
  1. Navigate to `https://bugbash.online/signin`.
  2. Select `locked_user` and enter `testingisfun99`.
  3. Click **Log In**.
  4. Observe error message banner.
- **Expected Result**: Error banner informs user the account is locked AND provides a recovery link (e.g., "Contact Support" or "Reset Password").
- **Actual Result**: Banner abruptly states "Your account has been locked." with zero guidance or actionable recovery path.
- **Root Cause**: Error UI component does not incorporate user recovery workflows.
- **Business Impact**: Legitimate users experiencing lockout are stranded, leading to customer attrition and support ticket surges.
- **Remediation**: Include a support contact or self-service account unlock link within the `.api-error` element.

---

### 11. BUG-11: Guest Cart Session Invalidation Ambiguity Across Browser Tabs
- **Bug ID**: `BUG-11`
- **Severity**: **Low** | **Priority**: P3
- **Testing Category**: Security & Vulnerability
- **Testing Type**: Security Misconfiguration / Session Management
- **Affected Component**: Client Local Storage (`localStorage.cart`)
- **Target URL**: `https://bugbash.online/`
- **Steps to Reproduce**:
  1. Open a guest session and add 2 items to the cart.
  2. Leave the tab idle for an extended period or open multiple tabs.
  3. Inspect `localStorage` cart state.
- **Expected Result**: Cart entries in `localStorage` should feature a TTL / expiration timestamp to prevent stale state.
- **Actual Result**: Cart persists indefinitely in raw `localStorage` without expiration or integrity check.
- **Root Cause**: Cart state synchronization lacks a timestamped TTL header in `localStorage`.
- **Business Impact**: Shared kiosk or library computers can expose previous shoppers' cart items to subsequent users.
- **Remediation**: Store cart items with a TTL timestamp and validate expiration on initialization: `{ items: [...], expiresAt: Date.now() + 86400000 }`.

---

## Verification Matrix

| Bug ID | Severity | Category | Testing Type | Automated Assertion |
| :--- | :--- | :--- | :--- | :--- |
| **BUG-01** | High | Functional & UI | Visual Testing | `naturalWidth == 0` check on `.shelf-item__thumb img` |
| **BUG-02** | Medium | Functional & UI | Logic Testing | `all(prices[i] <= prices[i+1])` assertion |
| **BUG-03** | Medium | Functional & UI | E2E Testing | Element `href` and download event verification |
| **BUG-04** | Medium | Usability & Compliance | Forms Testing | `get_attribute('required')` assertion |
| **BUG-05** | Medium | Security & Infrastructure | Misconfiguration | `requests.get('/404').status_code == 200` |
| **BUG-06** | Low | Functional & UI | Persona Testing | `len(driver.find_elements('.shelf-item')) == 0` |
| **BUG-07** | Medium | Usability & Compliance | Accessibility (WCAG) | `outlineStyle == 'none'` check on `.shelf-item__buy-btn` |
| **BUG-08** | Medium | Usability & Compliance | Accessibility (WCAG) | Empty `alt` attribute check on thumbnail elements |
| **BUG-09** | Medium | Cross-Device & Mobile | Responsive Testing | `document.body.scrollWidth > window.innerWidth` |
| **BUG-10** | Low | Security & Usability | Authentication | Banner guidance verification on locked state |
| **BUG-11** | Low | Security | Session Management | `localStorage` persistence and TTL validation |
