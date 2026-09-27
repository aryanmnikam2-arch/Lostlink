**# VIT Bhopal Lost \& Found Campus Portal**



\## Project Overview

\* A specialized campus platform engineered to manage lost belongings and simplify item recovery across academic blocks, labs, and residential hostels at VIT Bhopal University\[cite: 1].

\* Resolves the absence of a unified campus lost-and-found system by centralizing verified inquiries and recovered posts into a single interface\[cite: 1].

\* Replaces unstructured campus messaging groups with an organized, role-separated catalog feed\[cite: 1, 2].



\## Key Features

\* Institutional Email Authentication: Access is strictly gated to verified institutional email addresses ending with the domain @vitbhopal.ac.in\[cite: 1].

\* Verification Code Verification: Incorporates a 4-digit verification code step for local session validation and user credibility\[cite: 1].

\* Dual Action Split Dashboard: Presents a full-screen 50/50 split layout separated by a central line divider, routing users to either the Lost or Found intake flow\[cite: 2].

\* Lost Item Ingestion: Collects item name, description, optional image upload, contact details, and student registration ID\[cite: 1, 2].

\* Found Item Ingestion: Collects item name, description, mandatory image upload, discovery location, discovery timestamp, and contact details\[cite: 1, 2].

\* Amazon-Style Catalog Feed: Renders registered items in a responsive multi-column grid with clear product-style visual cards\[cite: 2].

\* Contact Concealment: Hides finder and claimant phone numbers behind an interactive toggle button on each card to limit unnecessary exposure\[cite: 2].

\* Gemini AI Smart Matcher: Automatically analyzes lost item queries against active found item descriptions using Google Gemini 2.5 Flash to highlight probable matches\[cite: 1].



\## Technologies and Tools Used

\* Backend Framework: Python Flask\[cite: 1]

\* Database: SQLite3\[cite: 1]

\* Frontend: Semantic HTML5, CSS3, Vanilla JavaScript\[cite: 1]

\* AI Platform: Google GenAI SDK (Model: gemini-2.5-flash)\[cite: 1]

\* Version Control: Git and GitHub\[cite: 1]



\## Steps to Install and Run

\* Clone the project repository to your local computer using git clone.

\* Open a terminal inside the project root folder.

\* Create a Python virtual environment:

&#x20; \* python -m venv venv

\* Activate the virtual environment:

&#x20; \* Windows: venv\\Scripts\\activate

&#x20; \* Linux or macOS: source venv/bin/activate

\* Install required project dependencies:

&#x20; \* pip install flask google-genai pillow

\* Configure the Gemini API key as an environment variable:

&#x20; \* Windows Command Prompt: set GEMINI\_API\_KEY=your\_actual\_key

&#x20; \* Windows PowerShell: $env:GEMINI\_API\_KEY="your\_actual\_key"

&#x20; \* Linux or macOS: export GEMINI\_API\_KEY="your\_actual\_key"

\* Launch the application server:

&#x20; \* python app.py

\* Open your browser and navigate to http://127.0.0.1:5000 to interact with the platform.



\## Instructions for Testing

\* Test Domain Verification:

&#x20; \* Enter a non-campus email address such as user@gmail.com and confirm the system rejects the entry.

&#x20; \* Enter an authorized campus email ending with @vitbhopal.ac.in and verify the verification step opens.

\* Test Split Dashboard Navigation:

&#x20; \* Log into the platform and confirm the screen divides into two distinct halves\[cite: 2].

&#x20; \* Click anywhere on the left section to confirm redirection to the Lost Form\[cite: 2].

&#x20; \* Return and click anywhere on the right section to confirm redirection to the Found Form\[cite: 2].

\* Test Found Item Upload:

&#x20; \* Fill out the Found form, attach an image file, and submit the entry\[cite: 2].

&#x20; \* Verify the submission is stored in the database and visible in the Amazon-style catalog grid\[cite: 2].

\* Test Lost Item AI Match:

&#x20; \* Submit a lost report matching the description of the previously saved found item\[cite: 2].

&#x20; \* Verify redirection to the feed and confirm the Gemini banner displays a probable item match\[cite: 1, 2].

\* Test Contact Reveal:

&#x20; \* Locate any card in the catalog grid and click Get Contact Info\[cite: 2].

&#x20; \* Verify the masked contact information becomes visible\[cite: 2].

