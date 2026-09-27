**# Project Statement: VIT Bhopal Lost \& Found Campus Portal**



\## 1. Problem Statement

\* Misplaced personal belongings including scientific calculators, official ID cards, keys, and electronics are a recurring daily issue across academic blocks, laboratories, and hostel premises at VIT Bhopal\[cite: 1].

\* The campus currently lacks a dedicated, centralized lost-and-found repository or desk to handle recovered property\[cite: 1].

\* Informal broadcast channels such as WhatsApp and Telegram groups lead to scattered messages, rapid loss of visibility, zero verification, and low recovery rates\[cite: 1].

\* There is no structured, domain-verified system for students to search active listings or safely report misplaced items\[cite: 1, 2].



\## 2. Scope of the Project

\* Confines user access exclusively to students and staff possessing verified institutional email credentials\[cite: 1].

\* Implements a full lifecycle web portal featuring separate ingestion pipelines for lost item inquiries and found item registrations\[cite: 1, 2].

\* Stores structured item metadata including location, discovery timestamp, descriptions, contact data, and uploaded photographs\[cite: 1, 2].

\* Organizes entries into an e-commerce style catalog feed optimized for visual search and campus-wide browsing\[cite: 2].

\* Incorporates automated semantic evaluation using artificial intelligence to pair lost inquiries against existing records\[cite: 1].

\* Excludes external user access and manual administrative intervention by enabling direct peer-to-peer verification\[cite: 1].



\## 3. Target Users

\* Enrolled undergraduate and postgraduate students of VIT Bhopal holding active institutional email accounts\[cite: 1].

\* Campus faculty, laboratory assistants, and facility staff seeking to log misplaced items found in academic and shared spaces\[cite: 1].

\* Peer claimants attempting to identify, verify, and reclaim their lost personal belongings\[cite: 1, 2].



\## 4. High-Level Features

\* Institutional Domain Authentication: Restricts registration and login to institutional emails ending with the university domain\[cite: 1].

\* Interactive Split Dashboard: Provides a fifty-fifty visual split layout dividing the primary interface into dedicated Lost and Found paths\[cite: 2].

\* Lost Item Reporting Module: Captures item title, detailed characteristics, student registration number, contact info, and an optional reference photo\[cite: 1, 2].

\* Found Item Ingestion Module: Captures item title, detailed characteristics, mandatory photo upload, discovery location, and discovery time\[cite: 1, 2].

\* Amazon-Style Catalog Grid: Displays recovered and reported items in a clean multi-column responsive card gallery\[cite: 2].

\* On-Demand Contact Reveal: Keeps user contact information concealed on cards until explicitly clicked to prevent unauthorized contact access\[cite: 2].

\* Gemini AI Smart Matcher: Automatically performs semantic matching on text descriptions using Google Gemini 2.5 Flash to flag potential item matches above the feed\[cite: 1].

