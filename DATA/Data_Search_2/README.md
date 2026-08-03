# Extraction & Scraping History Log

A running log of every extraction run in this project. **Book-repo conversions are numbered by *book repo* only** and stored under `books/link n/`, where *n* is the nth GitHub book repository processed. Non-book web scrapes are logged separately at the bottom.

| link | Source | Date (UTC) | Items | Output folder | Status |
|------|--------|-----------|-------|---------------|--------|
| link 3 | GitHub `manjunath5496/Human-Anatomy-Books` | 2026-07-27 | 14 books | `books/link 3/` | ✅ 14/14 converted |
| link 2 | GitHub `manjunath5496/Physiology-Books` | 2026-07-27 | 31 books | `books/link 2/` | ✅ 31/31 converted |
| link 1 | GitHub `manjunath5496/Medical-Books` | 2026-07-26 | 80 books | `books/link 1/` | ✅ 80/80 converted |
| — | chorcha.net Medical Admission Question Bank | 2026-07-26 | 0 questions | `chorcha_ques.md` | ⚠️ content access-gated |

### Method & fidelity notes (all runs)

- Each Markdown file starts with an H1 title and a source/pages/date header, then the full text with `<!-- ===== Page N ===== -->` markers so every original page is accounted for and completeness is verifiable.
- Text, reading order, and lists are preserved. Because PDFs carry no semantic structure, headings/tables/equations are **best-effort** — recovered as text but not always as native Markdown constructs. Images are not embedded; pure-image pages are flagged inline as `_[No extractable text on this page …]_` rather than dropped.
- Folder scheme (book repos only): `books/link 1/` = Medical-Books, `books/link 2/` = Physiology-Books, `books/link 3/` = Human-Anatomy-Books. Each new book repo gets the next `books/link n/`.
- RAR archives are extracted with `bsdtar`/libarchive (RAR5-capable) and converted like PDFs. A file present in a repo but absent from that repo's README is still processed, with its title derived from PDF metadata.

---

## link 3 — manjunath5496/Human-Anatomy-Books → Markdown

Conversion of every book in [`manjunath5496/Human-Anatomy-Books`](https://github.com/manjunath5496/Human-Anatomy-Books/tree/master) into clean Markdown. Each book's full text was extracted **page by page** and written to `books/link 3/<Book Title>.md`.

- **Run date:** 2026-07-27 06:48 UTC
- **Source repo files:** 14 books (12 PDF, 2 RAR)
- **Converted to Markdown:** 14 / 14 books
  - direct PDF conversions: 11
  - extracted from RAR archive, then converted: 2
- **Skipped:** 0
- **Failed:** 0
- **Image-heavy books** (≥15 pages without extractable text): 3 (listed below)
- **Total pages processed:** 6,665
- **Total characters extracted:** 13,790,575
- **Output folder:** `books/link 3/`
- **Extraction tool:** pdftotext (poppler/xpdf) 4.06, UTF-8, page-by-page (form-feed split); page counts cross-checked with pypdf.

### Books — link 3

| # | Book title | Source path | Pages | Output file | Status | Issues / notes |
|---|------------|-------------|------:|-------------|--------|----------------|
| 1 | Anatomy 101: From Muscles and Bones to Organs and Systems, Your Guide to How the Human Body Works | `um(1).pdf` | 345 | `books/link 3/Anatomy 101 - From Muscles and Bones to Organs and Systems, Your Guide to How the Human Body Works.md` | converted | 1/345 pages had no extractable text. |
| 2 | Anatomy of the Human Body | `um(2).pdf` | 852 | `books/link 3/Anatomy of the Human Body.md` | converted | 4/852 pages had no extractable text. |
| 3 | Pocket Atlas of Human Anatomy | `um(3).pdf` | 509 | `books/link 3/Pocket Atlas of Human Anatomy.md` | converted | 1/509 pages had no extractable text. |
| 4 | BD Chaurasia's Human Anatomy Regional and Applied Dissection and Clinical: Vol. 2 | `um(4).pdf` | 518 | `books/link 3/BD Chaurasia's Human Anatomy Regional and Applied Dissection and Clinical - Vol. 2.md` | converted | 20/518 pages had no extractable text. |
| 5 | Essentials of Anatomy and Physiology | `um(5).pdf` | 622 | `books/link 3/Essentials of Anatomy and Physiology.md` | converted | All pages yielded text. |
| 6 | Holistic Anatomy | `um(6).pdf` | 576 | `books/link 3/Holistic Anatomy.md` | converted | 3/575 pages had no extractable text. |
| 7 | Ross and Wilson Anatomy and Physiology in Health and Illness | `um(7).pdf` | 1,094 | `books/link 3/Ross and Wilson Anatomy and Physiology in Health and Illness.md` | converted | 41/1094 pages had no extractable text. |
| 8 | Schaum's Outline of Human Anatomy and Physiology | `um(8).pdf` | 193 | `books/link 3/Schaum's Outline of Human Anatomy and Physiology.md` | converted | 8/193 pages had no extractable text. |
| 9 | Color Atlas of Cytology, Histology, and Microscopic Anatomy | `um(9).rar` | 543 | `books/link 3/Color Atlas of Cytology, Histology, and Microscopic Anatomy.md` | converted (from RAR archive) | Extracted from RAR archive with bsdtar/libarchive, then converted. 1/543 pages had no extractable text. |
| 10 | Human Biology | `um(10).rar` | 457 | `books/link 3/Human Biology.md` | converted (from RAR archive) | Extracted from RAR archive with bsdtar/libarchive, then converted. All pages yielded text. |
| 11 | Anatomy Essentials For Dummies | `um(11).pdf` | 195 | `books/link 3/Anatomy Essentials For Dummies.md` | converted | 9/195 pages had no extractable text. |
| 12 | Basic Human Anatomy | `um(12).pdf` | 255 | `books/link 3/Basic Human Anatomy.md` | converted | All pages yielded text. |
| 13 | Understanding the Human Body: An Introduction to Anatomy and Physiology, 2nd Edition | `um(13).PDF` | 219 | `books/link 3/Understanding the Human Body - An Introduction to Anatomy and Physiology, 2nd Edition.md` | converted | All pages yielded text. (Title not in repo README; derived from PDF metadata.) |
| 14 | Anatomy and Physiology Laboratory Textbook | `um(14).pdf` | 287 | `books/link 3/Anatomy and Physiology Laboratory Textbook.md` | converted (no text — scanned/image PDF; OCR required) | Fully scanned/image-only PDF: no text layer (pdffonts=0 fonts, pdftotext=0 chars). 287/287 pages are scanned images; OCR required to recover text. Page-by-page scaffold written so no page is omitted. |

> **RAR note:** 2 book(s) were shipped as RAR archives; each was extracted with `bsdtar`/libarchive 3.8.4 (RAR5-capable) and then converted like the other PDFs — nothing skipped.

### Image-heavy books — link 3

Converted fully as text where text exists, but some pages are image-only (atlases/diagrams/plates), marked in-file and needing OCR to recover embedded labels:

- **Anatomy and Physiology Laboratory Textbook** (`um(14).pdf`) — 287 of 287 pages are image-only.
- **Ross and Wilson Anatomy and Physiology in Health and Illness** (`um(7).pdf`) — 41 of 1094 pages are image-only.
- **BD Chaurasia's Human Anatomy Regional and Applied Dissection and Clinical: Vol. 2** (`um(4).pdf`) — 20 of 518 pages are image-only.


---

## link 2 — manjunath5496/Physiology-Books → Markdown

Conversion of every book in [`manjunath5496/Physiology-Books`](https://github.com/manjunath5496/Physiology-Books/tree/master) into clean Markdown. Each book's full text was extracted **page by page** and written to `books/link 2/<Book Title>.md`.

- **Run date:** 2026-07-27
- **Source repo files:** 31 books (31 PDF)
- **Converted to Markdown:** 31 / 31 books
  - direct PDF conversions: 31
- **Skipped:** 0
- **Failed:** 0
- **Image-heavy books** (≥15 pages without extractable text): 4 (listed below)
- **Total pages processed:** 15,178
- **Total characters extracted:** 38,369,937
- **Output folder:** `books/link 2/`
- **Extraction tool:** pdftotext (poppler/xpdf) 4.06, UTF-8, page-by-page (form-feed split); page counts cross-checked with pypdf.

### Books — link 2

| # | Book title | Source path | Pages | Output file | Status | Issues / notes |
|---|------------|-------------|------:|-------------|--------|----------------|
| 1 | Essentials of Anatomy and Physiology | `phs(1).pdf` | 622 | `books/link 2/Essentials of Anatomy and Physiology.md` | converted | All pages yielded text. |
| 2 | Ross and Wilson Anatomy and Physiology in Health and Illness | `phs(2).pdf` | 1,094 | `books/link 2/Ross and Wilson Anatomy and Physiology in Health and Illness.md` | converted | 41/1094 pages had no extractable text. |
| 3 | Color Atlas of Physiology | `phs(3).pdf` | 455 | `books/link 2/Color Atlas of Physiology.md` | converted | 1/455 pages had no extractable text. |
| 4 | Introduction to Plant Physiology | `phs(4).pdf` | 523 | `books/link 2/Introduction to Plant Physiology.md` | converted | 2/523 pages had no extractable text. |
| 5 | Master Medicine: Physiology | `phs(5).pdf` | 329 | `books/link 2/Master Medicine - Physiology.md` | converted | 1/329 pages had no extractable text. |
| 6 | Ganong's Review of Medical Physiology | `phs(6).pdf` | 727 | `books/link 2/Ganong's Review of Medical Physiology.md` | converted | 1/727 pages had no extractable text. |
| 7 | Metabolism of Human Diseases: Organ Physiology and Pathophysiology | `phs(7).pdf` | 382 | `books/link 2/Metabolism of Human Diseases - Organ Physiology and Pathophysiology.md` | converted | 8/382 pages had no extractable text. |
| 8 | Schaum's Outline of Human Anatomy and Physiology | `phs(8).pdf` | 425 | `books/link 2/Schaum's Outline of Human Anatomy and Physiology.md` | converted | 1/425 pages had no extractable text. |
| 9 | Rapid Review Physiology | `phs(9).pdf` | 283 | `books/link 2/Rapid Review Physiology.md` | converted | 1/283 pages had no extractable text. |
| 10 | A Textbook of Practical Physiology | `phs(10).pdf` | 406 | `books/link 2/A Textbook of Practical Physiology.md` | converted | 13/406 pages had no extractable text. |
| 11 | Cardiovascular physiology | `phs(11).pdf` | 398 | `books/link 2/Cardiovascular physiology.md` | converted | 5/398 pages had no extractable text. |
| 12 | Handbook of Plant and Crop Physiology | `phs(12).pdf` | 997 | `books/link 2/Handbook of Plant and Crop Physiology.md` | converted | 34/996 pages had no extractable text. |
| 13 | Pocket Companion to Guyton and Hall Textbook of Medical Physiology | `phs(13).pdf` | 1,315 | `books/link 2/Pocket Companion to Guyton and Hall Textbook of Medical Physiology.md` | converted | 30/1315 pages had no extractable text. |
| 14 | Physiological Systems in Insects | `phs(14).pdf` | 699 | `books/link 2/Physiological Systems in Insects.md` | converted | 1/699 pages had no extractable text. |
| 15 | The Physiology of Flowering Plants | `phs(15).pdf` | 404 | `books/link 2/The Physiology of Flowering Plants.md` | converted | 5/411 pages had no extractable text. NOTE: pypdf pages=404 vs extracted=411. |
| 16 | Anatomy and Physiology of Animals | `phs(16).pdf` | 204 | `books/link 2/Anatomy and Physiology of Animals.md` | converted | 7/204 pages had no extractable text. |
| 17 | Physiology PreTest Self-Assessment and Review 14-E | `phs(17).pdf` | 396 | `books/link 2/Physiology PreTest Self-Assessment and Review 14-E.md` | converted | 1/396 pages had no extractable text. |
| 18 | Examination Questions and Answers in Basic Anatomy and Physiology | `phs(18).pdf` | 508 | `books/link 2/Examination Questions and Answers in Basic Anatomy and Physiology.md` | converted | All pages yielded text. |
| 19 | Pulmonary Physiology | `phs(19).pdf` | 291 | `books/link 2/Pulmonary Physiology.md` | converted | 1/291 pages had no extractable text. |
| 20 | Physiology and Molecular Biology of Stress Tolerance in Plants | `phs(20).pdf` | 351 | `books/link 2/Physiology and Molecular Biology of Stress Tolerance in Plants.md` | converted | 1/351 pages had no extractable text. |
| 21 | Multiple choice questions in Medical Physiology | `phs(21).pdf` | 138 | `books/link 2/Multiple choice questions in Medical Physiology.md` | converted | All pages yielded text. |
| 22 | Physiology Question-Based Learning | `phs(22).pdf` | 237 | `books/link 2/Physiology Question-Based Learning.md` | converted | 1/237 pages had no extractable text. |
| 23 | Functional Anatomy and Physiology of Domestic Animals | `phs(23).pdf` | 593 | `books/link 2/Functional Anatomy and Physiology of Domestic Animals.md` | converted | 5/593 pages had no extractable text. |
| 24 | Photosynthesis: Physiology and Metabolism | `phs(24).pdf` | 654 | `books/link 2/Photosynthesis - Physiology and Metabolism.md` | converted | 13/654 pages had no extractable text. |
| 25 | Fluid Physiology and Pathology in Traditional Chinese Medicine | `phs(25).pdf` | 627 | `books/link 2/Fluid Physiology and Pathology in Traditional Chinese Medicine.md` | converted | 1/627 pages had no extractable text. |
| 26 | BRS Physiology | `phs(26).pdf` | 330 | `books/link 2/BRS Physiology.md` | converted | 8/330 pages had no extractable text. |
| 27 | Anatomy and physiology of farm animals | `phs(27).pdf` | 536 | `books/link 2/Anatomy and physiology of farm animals.md` | converted | 23/536 pages had no extractable text. |
| 28 | Anatomy and Physiology For Dummies | `phs(28).pdf` | 367 | `books/link 2/Anatomy and Physiology For Dummies.md` | converted | 4/367 pages had no extractable text. |
| 29 | Essential Physiological Biochemistry | `phs(29).pdf` | 344 | `books/link 2/Essential Physiological Biochemistry.md` | converted | 10/344 pages had no extractable text. |
| 30 | Physiology for Engineers: Applying Engineering Methods to Physiological Systems | `phs(30).pdf` | 176 | `books/link 2/Physiology for Engineers - Applying Engineering Methods to Physiological Systems.md` | converted | All pages yielded text. |
| 31 | Applied Physiology in Intensive Care Medicine | `phs(31).pdf` | 367 | `books/link 2/Applied Physiology in Intensive Care Medicine.md` | converted | 1/367 pages had no extractable text. |

### Image-heavy books — link 2

Converted fully as text where text exists, but some pages are image-only (atlases/diagrams/plates), marked in-file and needing OCR to recover embedded labels:

- **Ross and Wilson Anatomy and Physiology in Health and Illness** (`phs(2).pdf`) — 41 of 1094 pages are image-only.
- **Handbook of Plant and Crop Physiology** (`phs(12).pdf`) — 34 of 996 pages are image-only.
- **Pocket Companion to Guyton and Hall Textbook of Medical Physiology** (`phs(13).pdf`) — 30 of 1315 pages are image-only.
- **Anatomy and physiology of farm animals** (`phs(27).pdf`) — 23 of 536 pages are image-only.


---

## link 1 — manjunath5496/Medical-Books → Markdown

Conversion of every book in [`manjunath5496/Medical-Books`](https://github.com/manjunath5496/Medical-Books/tree/master) into clean Markdown. Each book's full text was extracted **page by page** and written to `books/link 1/<Book Title>.md`.

- **Run date:** 2026-07-26
- **Source repo files:** 80 books (78 PDF, 2 RAR)
- **Converted to Markdown:** 80 / 80 books
  - direct PDF conversions: 78
  - extracted from RAR archive, then converted: 2
- **Skipped:** 0
- **Failed:** 0
- **Image-heavy books** (≥15 pages without extractable text): 12 (listed below)
- **Total pages processed:** 48,097
- **Total characters extracted:** 134,169,183
- **Output folder:** `books/link 1/`
- **Extraction tool:** pdftotext (poppler/xpdf) 4.06, UTF-8, page-by-page (form-feed split); page counts cross-checked with pypdf.

### Books — link 1

| # | Book title | Source path | Pages | Output file | Status | Issues / notes |
|---|------------|-------------|------:|-------------|--------|----------------|
| 1 | Color Atlas of Cytology, Histology and Microscopic Anatomy | `elm(1).rar` | 543 | `books/link 1/Color Atlas of Cytology, Histology and Microscopic Anatomy.md` | converted (from RAR archive) | Extracted from RAR archive with bsdtar/libarchive, then converted. 1/543 pages had no extractable text. |
| 2 | Text Book of Immunology | `elm(2).pdf` | 554 | `books/link 1/Text Book of Immunology.md` | converted | 1/554 pages had no extractable text. |
| 3 | Color Atlas of Physiology | `elm(3).pdf` | 455 | `books/link 1/Color Atlas of Physiology.md` | converted | 1/455 pages had no extractable text. |
| 4 | Medicinal Chemistry: A Molecular and Biochemical Approach | `elm(4).pdf` | 664 | `books/link 1/Medicinal Chemistry - A Molecular and Biochemical Approach.md` | converted | 1/664 pages had no extractable text. |
| 5 | An Introduction to Clinical Emergency Medicine | `elm(5).pdf` | 818 | `books/link 1/An Introduction to Clinical Emergency Medicine.md` | converted | 24/818 pages had no extractable text. |
| 6 | 2016 Current Medical Diagnosis and Treatment | `elm(6).pdf` | 1,921 | `books/link 1/2016 Current Medical Diagnosis and Treatment.md` | converted | All pages yielded text. |
| 7 | Color Atlas of Neurology | `elm(7).pdf` | 448 | `books/link 1/Color Atlas of Neurology.md` | converted | All pages yielded text. |
| 8 | Color Atlas of Genetics | `elm(8).pdf` | 497 | `books/link 1/Color Atlas of Genetics.md` | converted | 1/497 pages had no extractable text. |
| 9 | Ganong's Review of Medical Physiology | `elm(9).pdf` | 727 | `books/link 1/Ganong's Review of Medical Physiology.md` | converted | 1/727 pages had no extractable text. |
| 10 | The Gale Encyclopedia of Medicine | `elm(10).pdf` | 637 | `books/link 1/The Gale Encyclopedia of Medicine.md` | converted | 1/637 pages had no extractable text. |
| 11 | Color Atlas of Biochemistry | `elm(11).pdf` | 476 | `books/link 1/Color Atlas of Biochemistry.md` | converted | 1/476 pages had no extractable text. |
| 12 | 100 CASES in Clinical Medicine | `elm(12).pdf` | 274 | `books/link 1/100 CASES in Clinical Medicine.md` | converted | 1/274 pages had no extractable text. |
| 13 | Dewhurst's Textbook of Obstetrics and Gynaecology | `elm(13).pdf` | 732 | `books/link 1/Dewhurst's Textbook of Obstetrics and Gynaecology.md` | converted | 3/732 pages had no extractable text. |
| 14 | Simpson's Forensic Medicine | `elm(14).pdf` | 264 | `books/link 1/Simpson's Forensic Medicine.md` | converted | 1/264 pages had no extractable text. |
| 15 | Cognitive Psychology | `elm(15).pdf` | 714 | `books/link 1/Cognitive Psychology.md` | converted | 30/750 pages had no extractable text. NOTE: pypdf pages=714 vs extracted=750. |
| 16 | Current Diagnosis and Treatment Pediatrics | `elm(16).pdf` | 1,323 | `books/link 1/Current Diagnosis and Treatment Pediatrics.md` | converted | 1/1323 pages had no extractable text. |
| 17 | Essentials of Medical Pharmacology | `elm(17).pdf` | 957 | `books/link 1/Essentials of Medical Pharmacology.md` | converted | 32/957 pages had no extractable text. |
| 18 | The Encyclopedia of Natural Medicine | `elm(18).pdf` | 1,332 | `books/link 1/The Encyclopedia of Natural Medicine.md` | converted | 4/1332 pages had no extractable text. |
| 19 | Textbook of Microbiology and Immunology | `elm(19).rar` | 682 | `books/link 1/Textbook of Microbiology and Immunology.md` | converted (from RAR archive) | Extracted from RAR archive with bsdtar/libarchive, then converted. 3/682 pages had no extractable text. |
| 20 | The Gale Encyclopedia of Alternative Medicine | `elm(20).pdf` | 602 | `books/link 1/The Gale Encyclopedia of Alternative Medicine.md` | converted | All pages yielded text. |
| 21 | Color Atlas of Pharmacology | `elm(21).pdf` | 394 | `books/link 1/Color Atlas of Pharmacology.md` | converted | 1/394 pages had no extractable text. |
| 22 | Introduction to Veterinary and Comparative Forensic Medicine | `elm(22).pdf` | 442 | `books/link 1/Introduction to Veterinary and Comparative Forensic Medicine.md` | converted | 1/442 pages had no extractable text. |
| 23 | Medical-Surgical Nursing: Assessment and Management of Clinical Problems | `elm(23).pdf` | 477 | `books/link 1/Medical-Surgical Nursing - Assessment and Management of Clinical Problems.md` | converted | 1/477 pages had no extractable text. |
| 24 | Emergency Medicine: PreTest Self-Assessment and Review | `elm(24).pdf` | 588 | `books/link 1/Emergency Medicine - PreTest Self-Assessment and Review.md` | converted | 2/588 pages had no extractable text. |
| 25 | Encyclopedia of Human Body Systems | `elm(25).pdf` | 751 | `books/link 1/Encyclopedia of Human Body Systems.md` | converted | 1/751 pages had no extractable text. |
| 26 | Handbook of Medicinal Herbs | `elm(26).pdf` | 893 | `books/link 1/Handbook of Medicinal Herbs.md` | converted | 24/893 pages had no extractable text. |
| 27 | Textbook of Forensic Medicine and Toxicology | `elm(27).pdf` | 612 | `books/link 1/Textbook of Forensic Medicine and Toxicology.md` | converted | 1/612 pages had no extractable text. |
| 28 | Principles and Practice of Pharmaceutical Medicine | `elm(28).pdf` | 780 | `books/link 1/Principles and Practice of Pharmaceutical Medicine.md` | converted | 44/780 pages had no extractable text. |
| 29 | Clinical Psychology | `elm(29).pdf` | 690 | `books/link 1/Clinical Psychology.md` | converted | 1/690 pages had no extractable text. |
| 30 | Lippincott's Review for Medical-Surgical Nursing Certification | `elm(30).pdf` | 450 | `books/link 1/Lippincott's Review for Medical-Surgical Nursing Certification.md` | converted | 3/450 pages had no extractable text. |
| 31 | Pediatric Nutrition in Practice | `elm(31).pdf` | 350 | `books/link 1/Pediatric Nutrition in Practice.md` | converted | All pages yielded text. |
| 32 | Treatment of Pediatric Neurologic Disorders | `elm(32).pdf` | 608 | `books/link 1/Treatment of Pediatric Neurologic Disorders.md` | converted | 39/607 pages had no extractable text. |
| 33 | Atlas of musculoskeletal ultrasound anatomy | `elm(33).pdf` | 273 | `books/link 1/Atlas of musculoskeletal ultrasound anatomy.md` | converted | 16/273 pages had no extractable text. |
| 34 | Antimicrobial Therapy in Veterinary Medicine | `elm(34).pdf` | 675 | `books/link 1/Antimicrobial Therapy in Veterinary Medicine.md` | converted | 3/679 pages had no extractable text. NOTE: pypdf pages=675 vs extracted=679. |
| 35 | The Practice of Chinese Medicine | `elm(35).pdf` | 1,741 | `books/link 1/The Practice of Chinese Medicine.md` | converted | All pages yielded text. |
| 36 | Timeless Secrets of Health and Rejuvenation | `elm(36).pdf` | 543 | `books/link 1/Timeless Secrets of Health and Rejuvenation.md` | converted | 1/543 pages had no extractable text. |
| 37 | Biology Atlas of Skeletal Muscles | `elm(37).pdf` | 237 | `books/link 1/Biology Atlas of Skeletal Muscles.md` | converted | 2/236 pages had no extractable text. |
| 38 | RN Adult Medical Surgical Nursing Review Module Edition 9.0 | `elm(38).pdf` | 1,139 | `books/link 1/RN Adult Medical Surgical Nursing Review Module Edition 9.0.md` | converted | 1/1139 pages had no extractable text. |
| 39 | Medicine and surgery: A concise textbook | `elm(39).pdf` | 552 | `books/link 1/Medicine and surgery - A concise textbook.md` | converted | All pages yielded text. |
| 40 | Handbook for Brunner and Suddarth's Textbook of Medical Surgical Nursing | `elm(40).pdf` | 738 | `books/link 1/Handbook for Brunner and Suddarth's Textbook of Medical Surgical Nursing.md` | converted | 3/737 pages had no extractable text. |
| 41 | Medical Laboratory Science Review | `elm(41).pdf` | 601 | `books/link 1/Medical Laboratory Science Review.md` | converted | 18/588 pages had no extractable text. NOTE: pypdf pages=601 vs extracted=588. |
| 42 | Herbal Medicine: Biomolecular and Clinical Aspects | `elm(42).pdf` | 488 | `books/link 1/Herbal Medicine - Biomolecular and Clinical Aspects.md` | converted | 14/488 pages had no extractable text. |
| 43 | Clinical Forensic Medicine | `elm(43).pdf` | 492 | `books/link 1/Clinical Forensic Medicine.md` | converted | 14/492 pages had no extractable text. |
| 44 | Peptide Chemistry and Drug Design | `elm(44).pdf` | 338 | `books/link 1/Peptide Chemistry and Drug Design.md` | converted | All pages yielded text. |
| 45 | Handbook of Psychology | `elm(45).pdf` | 690 | `books/link 1/Handbook of Psychology.md` | converted | 14/690 pages had no extractable text. |
| 46 | Handbook Of Pediatric Emergency Medicine | `elm(46).pdf` | 451 | `books/link 1/Handbook Of Pediatric Emergency Medicine.md` | converted | 23/451 pages had no extractable text. |
| 47 | Fundamentals of Forensic DNA Typing | `elm(47).pdf` | 519 | `books/link 1/Fundamentals of Forensic DNA Typing.md` | converted | 1/519 pages had no extractable text. |
| 48 | Dictionary of Pharmaceutical Medicine | `elm(48).pdf` | 404 | `books/link 1/Dictionary of Pharmaceutical Medicine.md` | converted | All pages yielded text. |
| 49 | 100 CASES in Obstetrics and Gynaecology | `elm(49).pdf` | 282 | `books/link 1/100 CASES in Obstetrics and Gynaecology.md` | converted | 1/282 pages had no extractable text. |
| 50 | Research Methods In Clinical Psychology | `elm(50).pdf` | 304 | `books/link 1/Research Methods In Clinical Psychology.md` | converted | 5/306 pages had no extractable text. |
| 51 | The Human Body: Building Blocks And Nutrition | `elm(51).pdf` | 286 | `books/link 1/The Human Body - Building Blocks And Nutrition.md` | converted | 4/286 pages had no extractable text. |
| 52 | Current Essentials of Medicine | `elm(52).pdf` | 607 | `books/link 1/Current Essentials of Medicine.md` | converted | 1/606 pages had no extractable text. |
| 53 | Essential Evidence-Based Medicine | `elm(53).pdf` | 457 | `books/link 1/Essential Evidence-Based Medicine.md` | converted | 3/457 pages had no extractable text. |
| 54 | Medical-Surgical Nursing Demystified | `elm(54).pdf` | 626 | `books/link 1/Medical-Surgical Nursing Demystified.md` | converted | 1/626 pages had no extractable text. |
| 55 | Clinical Forensic Medicine - A Physician's Guide | `elm(55).pdf` | 458 | `books/link 1/Clinical Forensic Medicine - A Physician's Guide.md` | converted | 12/458 pages had no extractable text. |
| 56 | Core Clinical Cases in Medicine and Surgery | `elm(56).pdf` | 353 | `books/link 1/Core Clinical Cases in Medicine and Surgery.md` | converted | 1/353 pages had no extractable text. |
| 57 | Emergency Medicine Clinical Guidelines | `elm(57).pdf` | 310 | `books/link 1/Emergency Medicine Clinical Guidelines.md` | converted | 1/310 pages had no extractable text. |
| 58 | Wilson and Gisvold's Textbook of Organic Medicinal and Pharmaceutical Chemistry | `elm(58).pdf` | 1,022 | `books/link 1/Wilson and Gisvold's Textbook of Organic Medicinal and Pharmaceutical Chemistry.md` | converted | 2/1022 pages had no extractable text. |
| 59 | Absolute Beginner's Guide to Alternative Medicine | `elm(59).pdf` | 382 | `books/link 1/Absolute Beginner's Guide to Alternative Medicine.md` | converted | 21/382 pages had no extractable text. |
| 60 | The transmission of Chinese medicine | `elm(60).pdf` | 307 | `books/link 1/The transmission of Chinese medicine.md` | converted | 1/307 pages had no extractable text. |
| 61 | Oxford Dictionary of Medical Quotations | `elm(61).pdf` | 225 | `books/link 1/Oxford Dictionary of Medical Quotations.md` | converted | 1/225 pages had no extractable text. |
| 62 | MCQs and EMQs in Human Physiology | `elm(62).pdf` | 361 | `books/link 1/MCQs and EMQs in Human Physiology.md` | converted | All pages yielded text. |
| 63 | Community Medicine Important MCQs | `elm(63).pdf` | 355 | `books/link 1/Community Medicine Important MCQs.md` | converted | All pages yielded text. |
| 64 | The Complete Home Guide to Herbs, Natural Healing, and Nutrition | `elm(64).pdf` | 317 | `books/link 1/The Complete Home Guide to Herbs, Natural Healing, and Nutrition.md` | converted | All pages yielded text. |
| 65 | Multiple Choice Questions in Medical Physiology | `elm(65).pdf` | 138 | `books/link 1/Multiple Choice Questions in Medical Physiology.md` | converted | All pages yielded text. |
| 66 | Being Mortal: Illness, Medicine and What Matters | `elm(66).pdf` | 333 | `books/link 1/Being Mortal - Illness, Medicine and What Matters.md` | converted | 1/333 pages had no extractable text. |
| 67 | MCQs in Tropical Medicine | `elm(67).pdf` | 76 | `books/link 1/MCQs in Tropical Medicine.md` | converted | All pages yielded text. |
| 68 | MCQs in Pathology | `elm(68).pdf` | 69 | `books/link 1/MCQs in Pathology.md` | converted | All pages yielded text. |
| 69 | MCQs and EMQs in Surgery | `elm(69).pdf` | 25 | `books/link 1/MCQs and EMQs in Surgery.md` | converted | All pages yielded text. |
| 70 | Physics of the Human Body | `elm(70).pdf` | 780 | `books/link 1/Physics of the Human Body.md` | converted | 1/780 pages had no extractable text. |
| 71 | Harrison's Manual of Medicine | `elm(71).pdf` | 1,571 | `books/link 1/Harrison's Manual of Medicine.md` | converted | 1/1571 pages had no extractable text. |
| 72 | Cambridge Pocket Clinician - Internal Medicine | `elm(72).pdf` | 1,591 | `books/link 1/Cambridge Pocket Clinician - Internal Medicine.md` | converted | 4/1591 pages had no extractable text. |
| 73 | Pocket Medicine | `elm(73).pdf` | 282 | `books/link 1/Pocket Medicine.md` | converted | 4/281 pages had no extractable text. |
| 74 | The Survival Medicine Handbook | `elm(74).pdf` | 1,911 | `books/link 1/The Survival Medicine Handbook.md` | converted | 51/1911 pages had no extractable text. |
| 75 | What Your Doctor Doesn't Know About Nutritional Medicine | `elm(75).pdf` | 151 | `books/link 1/What Your Doctor Doesn't Know About Nutritional Medicine.md` | converted | 2/151 pages had no extractable text. |
| 76 | Approach to Internal Medicine: Resource Book for Clinical Practice | `elm(76).pdf` | 480 | `books/link 1/Approach to Internal Medicine - Resource Book for Clinical Practice.md` | converted | 7/480 pages had no extractable text. |
| 77 | Decision Making in Medicine: An Algorithmic Approach | `elm(77).pdf` | 753 | `books/link 1/Decision Making in Medicine - An Algorithmic Approach.md` | converted | 1/753 pages had no extractable text. |
| 78 | Infectious Diseases in Critical Care Medicine | `elm(78).pdf` | 612 | `books/link 1/Infectious Diseases in Critical Care Medicine.md` | converted | 14/628 pages had no extractable text. NOTE: pypdf pages=612 vs extracted=628. |
| 79 | Principles and Practice of Clinical Trial Medicine | `elm(79).pdf` | 536 | `books/link 1/Principles and Practice of Clinical Trial Medicine.md` | converted | 67/536 pages had no extractable text. |
| 80 | Burket's Oral Medicine | `elm(80).pdf` | 601 | `books/link 1/Burket's Oral Medicine.md` | converted | 13/601 pages had no extractable text. |

> **RAR note:** 2 book(s) were shipped as RAR archives; each was extracted with `bsdtar`/libarchive 3.8.4 (RAR5-capable) and then converted like the other PDFs — nothing skipped.

### Image-heavy books — link 1

Converted fully as text where text exists, but some pages are image-only (atlases/diagrams/plates), marked in-file and needing OCR to recover embedded labels:

- **Principles and Practice of Clinical Trial Medicine** (`elm(79).pdf`) — 67 of 536 pages are image-only.
- **The Survival Medicine Handbook** (`elm(74).pdf`) — 51 of 1911 pages are image-only.
- **Principles and Practice of Pharmaceutical Medicine** (`elm(28).pdf`) — 44 of 780 pages are image-only.
- **Treatment of Pediatric Neurologic Disorders** (`elm(32).pdf`) — 39 of 607 pages are image-only.
- **Essentials of Medical Pharmacology** (`elm(17).pdf`) — 32 of 957 pages are image-only.
- **Cognitive Psychology** (`elm(15).pdf`) — 30 of 750 pages are image-only.
- **An Introduction to Clinical Emergency Medicine** (`elm(5).pdf`) — 24 of 818 pages are image-only.
- **Handbook of Medicinal Herbs** (`elm(26).pdf`) — 24 of 893 pages are image-only.
- **Handbook Of Pediatric Emergency Medicine** (`elm(46).pdf`) — 23 of 451 pages are image-only.
- **Absolute Beginner's Guide to Alternative Medicine** (`elm(59).pdf`) — 21 of 382 pages are image-only.
- **Medical Laboratory Science Review** (`elm(41).pdf`) — 18 of 588 pages are image-only.
- **Atlas of musculoskeletal ultrasound anatomy** (`elm(33).pdf`) — 16 of 273 pages are image-only.


---

## Web scrape (not a book repo) — chorcha.net Medical Admission Question Bank

Attempted scrape of the medical-admission question bank at <https://chorcha.net/question-bank/medical-admission-question-bank>. Not assigned a `link n` because it is not a book repository and produced no book files.

| Field | Value |
|-------|-------|
| Target URL | https://chorcha.net/question-bank/medical-admission-question-bank |
| Date/time (UTC) | 2026-07-26 20:13 UTC |
| Pages / resources visited | 4 (question-bank page, `/question-bank` index, `robots.txt`, `sitemap.xml` + 3 sub-sitemaps) |
| Question sets catalogued | 25 year-sets, 2,474 questions (counts only — no text) |
| **Questions extracted** | **0 — question text is access-gated** |
| Output file | `chorcha_ques.md` |
| Status | ⚠️ Completed; no question content available to anonymous scraping |

**Issues / why no text was extracted:**
- The rendered page shows *"No questions found"* for every year to anonymous visitors.
- The embedded Next.js data masks the `questions` field as `"AAAA…"` and marks content `visibility: "batch_only_archive"` (enrolled students only).
- The question API lives under `/api/` and `/api-v1/`, which the site's `robots.txt` disallows — not scraped.
- `sitemap.xml` sub-sitemaps are empty — no public question pages exist.
- No authentication or `robots.txt` restriction was bypassed; no questions were fabricated. See `chorcha_ques.md` for the full breakdown.
