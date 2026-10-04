HOW TO ADD WEEKLY MATERIAL
==========================
Put each week's files in its folder, then rebuild and upload:

    teaching/ada/week01/   ... week15/     Design & Analysis of Algorithms
    teaching/ds/week01/    ... week15/     Data Structures
    teaching/os/week01/    ... week15/     Operating Systems
    teaching/cd/week01/    ... week15/     Compiler Design

  * Slides: any file, e.g.  Week1_Asymptotic_Notations.pptx  or .pdf
  * Practice questions: put one of these words in the file name -
        practice, question, assignment, quiz, tutorial, sheet, problem, exercise
    e.g.  practice_questions_week1.pdf
  * Tip: also save the PPT as PDF and upload both: PDFs open on any phone, PPTX needs PowerPoint.

Week topics and Google Classroom links are in  data/teaching.json  (gcr_link, gcr_code).
Then:   python3 build.py      and drag the new dist/ folder onto Netlify > Deploys.
