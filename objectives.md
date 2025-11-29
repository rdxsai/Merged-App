# Domain I: Creating Accessible Web Solutions (40%)

## I.A. Guidelines, Principles, and Techniques for Meeting Success Criteria
1. **Explain** the structure of WCAG 2.2 by identifying the four principles (POUR), guidelines, and success criteria levels (A, AA, AAA).  
2. **Differentiate** between normative and non-normative parts of WCAG, WAI-ARIA, and ATAG, and **justify** why that distinction matters for conformance.  
3. **Apply** W3C-recommended techniques (e.g., sufficient techniques, failure techniques) to specific WCAG success criteria in real coding scenarios.  
4. **Compare** the scope of WCAG (2.0, 2.1, 2.2), ATAG 2.0, and EN 301 549, and **identify** how each set of requirements influences web accessibility design.  
5. **Summarize** the rationale for using the latest WCAG 2.2 and **evaluate** the impact of new success criteria (e.g., Focus Not Obscured) on website design.

## I.B. Basic Knowledge of Programming
1. **Demonstrate** how JavaScript event handlers can be made device-independent (e.g., supporting both pointer and keyboard input).  
2. **Explain** progressive enhancement and **outline** the implications of turning JavaScript off or using older browsers for accessibility.  
3. **Identify** common pitfalls in dynamic content updates (e.g., partial page refreshes with AJAX) and **implement** focus management or live regions to keep screen reader users informed.  
4. **Distinguish** between semantic HTML controls (e.g., `<button>`, `<a>`) and generic elements (e.g., `<div>`) in terms of built-in accessibility.  
5. **Analyze** how focus order, event handling (onClick, onKeyDown, etc.), and ARIA states can either improve or harm the user experience for assistive technology.

## I.C. Create Interactive Controls/Widgets Based on Best Practices
1. **Construct** a custom widget (e.g., a modal dialog or accordion) using the WAI-ARIA Authoring Practices, ensuring correct roles, states, and properties.  
2. **Demonstrate** correct keyboard interaction models (e.g., tab vs. arrow keys) for composite components such as menus, tabs, and disclosure widgets.  
3. **Evaluate** existing custom controls for missing or incorrect ARIA markup, and **recommend** solutions to align them with best practices.

## I.D. Using ARIA
1. **Explain** the five primary rules of ARIA usage (e.g., "use native HTML first," "do not change native semantics unless necessary").  
2. **Implement** accessible names and descriptions using `aria-label`, `aria-labelledby`, and `aria-describedby`, and **justify** which approach is most appropriate in a given scenario.  
3. **Demonstrate** correct focus management using `aria-activedescendant` or roving `tabindex` in interactive widgets.  
4. **Analyze** how the accessibility tree is exposed to assistive technology and **verify** ARIA roles, states, and properties in different screen reader/browser combinations.

## I.E. Accessibility-Supported Technologies
1. **Identify** how assistive technologies (e.g., screen readers, magnifiers, voice input) interact with browsers and what "accessibility-supported" means under WCAG.  
2. **Assess** the compatibility of a chosen technology stack (front-end framework, JS library) with major screen reader/browser pairs and **recommend** fallback or polyfill strategies.  
3. **Explain** how touch interaction changes with a screen reader turned on (e.g., iOS VoiceOver gestures) and **demonstrate** design patterns to support these gestures.

## I.F. Standard Controls vs. Custom Controls
1. **Compare** native HTML controls' built-in accessibility features with custom (ARIA-based) components, highlighting pros and cons.  
2. **Demonstrate** how to repurpose a non-semantic element into a fully accessible custom button or link using proper ARIA attributes, keyboard events, and visible focus.  
3. **Recommend** standard HTML controls whenever possible and **justify** the business and user benefits of reducing custom code for accessibility.

## I.G. Single-Page Applications (SPAs)
1. **Demonstrate** how to manage announcements of dynamic page updates (e.g., with `aria-live`) when navigation or content changes do not trigger a full page reload.  
2. **Implement** focus changes appropriately when new views or dialogs appear, ensuring screen-reader and keyboard-only users can track SPA updates.  
3. **Evaluate** the user experience of a single-page application with typical assistive technologies and **propose** solutions for any discovered gaps.

## I.H. Strategies of Persons with Disabilities in Using Web Solutions
1. **Describe** key strategies that users with blindness, low vision, motor disabilities, auditory disabilities, and cognitive/learning disabilities employ to interact with web content.  
2. **Analyze** design elements (e.g., headings, landmarks, color contrast) to determine their impact on diverse user groups' navigation and comprehension strategies.  
3. **Propose** layout or structural revisions (e.g., skip links, consistent navigation) that accommodate multiple disability groups.

---

# Domain II: Identify Accessibility Issues in Web Solutions (40%)

## II.A. Interoperability and Compatibility Issues
1. **Identify** potential issues arising from specific browser–screen reader combinations (e.g., JAWS + Chrome vs. NVDA + Firefox).  
2. **Explain** why certain ARIA roles or HTML5 elements might not be fully supported across older browsers, and how to mitigate these gaps.  
3. **Evaluate** a website's accessibility across multiple devices (desktop, tablet, mobile) and assistive technologies.

## II.B. Identifying Guidelines and Principles Regarding Issues
1. **Map** discovered accessibility barriers to the appropriate WCAG success criterion (or EN 301 549 clause) and **distinguish** conformance failures from best-practice gaps.  
2. **Apply** the WCAG-EM methodology to define scope, explore site content, select a representative sample, and evaluate conformance thoroughly.  
3. **Explain** the concept of conformance levels (A, AA, AAA) and **defend** the rationale for choosing a specific level in a project or legal context.  
4. **Describe** the limitations in WCAG (e.g., certain gaps for cognitive or motion-based issues) and **propose** best-practice enhancements.

## II.C. Testing with Assistive Technologies
1. **Conduct** screen reader testing to confirm that name, role, value, and state changes of interactive elements are conveyed properly.  
2. **Demonstrate** manual keyboard testing to detect missing focus indicators, incorrect tab order, or keyboard traps.  
3. **Use** magnifier or high-contrast settings to **detect** any text or interface elements that become unusable or unreadable.  
4. **Identify** common user needs for auditory disabilities (e.g., accurate captions, transcripts) and evaluate if they are met.

## II.D. Testing Tools for the Web
1. **Compare** the strengths and limitations of automated tools, browser-based linters, spider tools, and bookmarklets for accessibility testing.  
2. **Use** at least one site-wide scanning tool and one browser-based developer tool (e.g., Axe, WAVE, Lighthouse) to **detect** markup or ARIA errors.  
3. **Interpret** automated test results to confirm valid failures, eliminate false positives, and plan follow-up manual checks.

## II.E. Accessibility Quality Assurance
1. **Explain** how accessibility can be integrated into agile vs. waterfall lifecycles, focusing on early detection of issues.  
2. **Establish** a continuous testing process (automated + manual) that catches regressions after updates or new releases.  
3. **Coordinate** with product owners, designers, and developers to incorporate accessibility checks into acceptance criteria and "definition of done."

## II.F. Testing with Assistive Technologies (Extended)
1. **Demonstrate** usage of at least two popular screen reader/browser combinations (e.g., NVDA + Firefox, VoiceOver + Safari) to confirm consistent user experience.  
2. **Verify** that dynamically updated or hidden elements are properly announced or hidden from screen readers.  
3. **Assess** whether alternative input methods (switch control, voice input) can navigate and operate interactive elements effectively.

## II.G. Testing for End-User Impact (Low Vision, Cognitive, Mobile/Touch)
1. **Perform** usability walk-throughs with simulated low-vision settings (zoom, high contrast) to find layout or text-flow issues.  
2. **Assess** mobile interaction (touch gestures, orientation changes) to **ensure** elements remain accessible and do not require two-dimensional scrolling.  
3. **Identify** potential cognitive barriers (e.g., complex language or form instructions) and **recommend** simpler language or multi-step guidance.

## II.H. Testing Tools for the Web (Revisited)
1. **Demonstrate** how to use color-contrast analyzers, focus inspectors, or code validators to confirm partial compliance with WCAG criteria.  
2. **Explain** how ACT Rules can guide consistent test procedures across multiple tools and testers.

---

# Domain III: Remediating Issues in Web Solutions (20%)

## III.A. Level of Severity and Prioritization of Issues
1. **Categorize** accessibility issues based on severity (blockers vs. minor nuisances) and **formulate** a remediation timeline that balances user impact and resource constraints.  
2. **Justify** which issues must be addressed first by assessing legal risk, user impact, and overall usability.  
3. **Demonstrate** how to communicate high-impact barriers (e.g., no keyboard support, missing alt text on key images) to stakeholders and developers.

## III.B. Recommending Strategies and/or Techniques for Fixing Issues
1. **Propose** ARIA-based or native HTML solutions for each conformance failure, **explaining** why a given fix is both accessible and feasible.  
2. **Distinguish** between "quick fixes" that resolve localized errors and "redesign" approaches that address deeper structural problems.  
3. **Collaborate** with design and development teams to **implement** new UI patterns or code libraries that systematically eliminate repeated accessibility faults.

## III.C. Integrate Accessibility into the Procurement Process
1. **Evaluate** vendor Accessibility Conformance Reports (VPAT/ACR) to determine product compatibility with organizational accessibility standards.  
2. **Recommend** contract language that mandates the vendor to fix accessibility defects within specified timeframes and supply updated VPATs.  
3. **Develop** a procurement checklist incorporating EN 301 549 or WCAG references to ensure new products and services meet accessibility requirements.  
4. **Implement** a vendor management process that includes accessibility roadmap reviews, defect remediation, and ongoing conformance monitoring.

---

## How to Use These Objectives

- **Curriculum Planning**: Instructors can design modules around each domain and sub-topic.  
- **Self-Assessment**: Certification candidates can refer to each objective to gauge readiness.  
- **Team Readiness**: Organizations can integrate these objectives into job descriptions or training paths, clarifying exactly what "accessibility competence" entails for various roles.