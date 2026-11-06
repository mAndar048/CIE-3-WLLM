# CIE3 individual submission checklist

**Per assignment:** choose one of five projects; deadline stated as **6 November, 10:00 AM**. Verify with your instructor whether late submissions are permitted.

- [x] One project selected: #4 Hinglish Smart Writing Assistant.
- [x] Complete Streamlit frontend, CLI and backend pipeline.
- [x] AI4Bharat IndicXlit adapter; optional IndicTrans2; optional BharatGen Param1 integration.
- [x] 45 representative example cases, reproducible evaluation program.
- [x] Failure analysis, architecture, README, test suite, CI.
- [x] Presentation slides and report delivered with package.
- [ ] Install and exercise **real AI4Bharat checkpoint**; save actual model outputs. (Not possible in the sandbox where only offline demo was tested.)
- [ ] Confirm Param1/IndicTrans2 integration on a GPU when presenting those optional features.
- [ ] Add your real name, USN/roll number, instructor, GitHub repository URL to cover pages.
- [ ] Publish this folder to your own GitHub; do not claim a remote repository until created.
- [ ] Capture a working Streamlit screenshot and link after deploying.
- [ ] Review human evaluation labels, test samples and research paper before final upload.

GitHub publish example:
```bash
git init
git add .
git commit -m "CS3235 BhashaWrite mini project"
# Create an empty GitHub repo in your account first, then:
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/bhashawrite-cs3235.git
git push -u origin main
```

Do not upload `.env`, auth keys, personal data, or model files.
