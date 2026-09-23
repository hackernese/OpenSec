# SPECS.md — Ausecurity Website (website1)

## Overview

**Company:** Ausecurity  
**Domain:** ausecurity.best  
**Industry:** Cybersecurity Consulting  
**Services:** Governance, Risk & Compliance (GRC) consulting, Penetration Testing  

---

## Company Story & Vision

Ausecurity was founded by a team of seasoned security professionals who saw a gap in the market: small and mid-sized businesses were being left behind in an increasingly hostile digital landscape, unable to afford the retainer fees of large consultancy firms yet too exposed to operate without expert guidance.

The company's philosophy is simple — security should be accessible, understandable, and actionable. The name "Ausecurity" reflects its roots and pride in delivering Australian-grade rigour in cybersecurity practice to clients across the region. Their consultants hold certifications across CISSP, CISM, OSCP, and CREST, and they operate with a "red team mindset, blue team discipline" ethos.

Ausecurity's two core pillars are:

1. **GRC (Governance, Risk & Compliance)** — Helping organisations understand their risk posture, align with frameworks such as ISO 27001, NIST, and the Australian ISM, and achieve or maintain compliance certifications.
2. **Penetration Testing** — Offensive security assessments across web applications, internal networks, cloud infrastructure, and social engineering, delivered as one-time engagements or ongoing retainer programs.

Their clients range from financial services and healthcare providers to government contractors and e-commerce platforms. Ausecurity positions itself as a trusted partner, not just a vendor — building long-term relationships through transparency, clear reporting, and genuine remediation support.

---

## Target Audience

- CTOs, CISOs, and IT managers at SMEs and mid-market companies
- Compliance officers seeking certification support (ISO 27001, SOC 2, PCI-DSS)
- Startups needing a first security review before launch or funding rounds
- Enterprises seeking an independent red team assessment

---

## Website Goals

- Establish credibility and trust with potential clients
- Clearly communicate service offerings (GRC and Pentesting)
- Generate inbound leads via a contact/enquiry form
- Showcase past work through case studies or testimonials
- Provide a clear call-to-action (CTA) to book a consultation

---

## Pages & Structure

### 1. Home (`/`)
- Hero section with a compelling headline and subheadline
  - Example: *"Secure Your Business. Know Your Risk."*
  - Subheadline: *"Expert GRC consulting and penetration testing for businesses that take security seriously."*
- Brief company introduction (2–3 sentences)
- Two primary CTA buttons: "Our Services" and "Get a Free Consultation"
- Service highlights (icon cards): GRC, Penetration Testing
- Trust signals: number of clients served, years of experience, certifications held
- Testimonials / client logos section
- Final CTA banner: "Ready to secure your business? Let's talk."

### 2. Services (`/services`)
- Overview of all service offerings
- **GRC Consulting** subsection:
  - Risk assessments
  - Policy and procedure development
  - Compliance gap analysis (ISO 27001, NIST CSF, PCI-DSS, Australian Privacy Act)
  - Security awareness training
  - Virtual CISO (vCISO) engagements
- **Penetration Testing** subsection:
  - Web application penetration testing
  - Internal / external network penetration testing
  - Cloud security assessment (AWS, Azure, GCP)
  - Social engineering / phishing simulations
  - Red team exercises
- Each service card should have a brief description, key deliverables, and a "Learn More" or "Enquire" button

### 3. About (`/about`)
- Company story (founding, mission, values)
- Team section: consultant profiles with name, role, certifications, and photo placeholder
- Company values: Integrity, Transparency, Excellence, Partnership
- Certifications and accreditations (CREST, OSCP, CISSP, ISO 27001 Lead Auditor, etc.)

### 4. Case Studies / Portfolio (`/case-studies`)
- Grid of anonymised case study cards
- Each card: industry, challenge, approach, outcome
- Example entries:
  - *Financial Services firm achieves ISO 27001 certification in 9 months*
  - *E-commerce platform: critical SQLi vulnerability discovered and remediated pre-launch*
  - *Healthcare provider: full GRC uplift program and staff security awareness training*

### 5. Contact (`/contact`)
- Contact form with fields:
  - Full Name (required)
  - Company Name (required)
  - Email Address (required)
  - Phone Number (optional)
  - Service of Interest: dropdown (GRC Consulting / Penetration Testing / Not Sure)
  - Message / Description of needs (textarea, required)
  - Submit button: "Send Enquiry"
- Office contact details (placeholder): email, phone
- Business hours
- Optional: embedded map or location reference

### 6. (Optional) Blog / Resources (`/blog`)
- Note: blog.ausecurity.best runs a separate WordPress instance; this page can simply be a redirect or a teaser with a link to the blog subdomain

---

## Design Direction

- **Tone:** Professional, trustworthy, technical but approachable
- **Color palette:**
  - Primary: Dark navy (`#0D1B2A`) — conveys security and authority
  - Accent: Electric blue (`#00A8E8`) — tech-forward energy
  - Secondary: Slate grey (`#4A5568`)
  - Background: Off-white (`#F7F8FC`) for light sections, dark navy for hero/CTA sections
- **Typography:**
  - Headings: Clean sans-serif (e.g., Inter, Montserrat)
  - Body: Readable sans-serif (e.g., Inter, Open Sans)
- **Imagery:** Abstract cybersecurity visuals, padlock/shield motifs, dark-themed tech aesthetics
- **Logo:** Shield or lock icon combined with "Ausecurity" wordmark

---

## Technical Requirements

- **Stack:** Any modern stack is acceptable (e.g., plain HTML/CSS/JS, React, Next.js, Vue, or a static site generator like Hugo/Eleventy)
- **Hosting context:** Served from a cPanel-managed server at `ausecurity.best`
- **Responsive:** Fully mobile-responsive design (mobile-first preferred)
- **Forms:** Contact form must submit correctly; backend handler or mailto fallback acceptable for MVP
- **SEO basics:** Semantic HTML, meta title/description per page, Open Graph tags
- **Performance:** Lightweight, fast-loading pages
- **Accessibility:** WCAG 2.1 AA compliance minimum
- **No CMS required** for website1 (WordPress is handled separately on blog.ausecurity.best)

---

## Navigation

```
Ausecurity [logo]   |   Home   Services   About   Case Studies   Contact   [Book a Consultation – CTA button]
```

Footer:
- Logo + tagline
- Quick links (Home, Services, About, Case Studies, Contact)
- Services list
- Contact details
- Social links (LinkedIn, Twitter/X)
- Copyright notice: © 2026 Ausecurity. All rights reserved.

---

## Content Tone & Voice

- Confident and authoritative without being arrogant
- Technical accuracy where needed, but explained in plain language for non-technical executives
- Action-oriented: every section should guide the visitor toward making contact
- Avoid vague buzzwords; prefer specific, credible claims

---

## Out of Scope

- `blog.ausecurity.best` (WordPress, separate system — do not build or modify)
- Email server / cPanel configuration
- Any server-side infrastructure beyond what is needed to serve the site

---

## Deliverable Summary

Build a complete, production-ready public-facing website for **ausecurity.best** that:
1. Communicates Ausecurity's GRC and penetration testing services clearly
2. Builds trust through professional design, team/certification highlights, and case studies
3. Drives lead generation via a prominent contact/enquiry form
4. Is fully responsive, accessible, and performant
5. Can be deployed to a cPanel-hosted server as static files or a Node/PHP-compatible app
