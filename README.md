# CAMEX MOU Generator

Browser app that produces bilingual (English / 中文) MOUs for ASEAN trade agencies, associations and partners from the CAMEX base MOU (15 Jul 2026).

## Use
Open `app/mou-generator.html` in any browser, fill in the partner details, then click **Download MOU (.docx)**. No install or server needed.

## What is filled in
Partner name and description (EN/中文), country (fills every "… Pavilion" / …馆 reference), effective date, term, termination notice, signatories and their dates, optional Appendix A contacts. Missing items are flagged and left as marked `[TBC]` / `【待填】` placeholders, never guessed.

## Files
- `app/mou-generator.html` – the finished app (template embedded).
- `template/MOU_template.docx` – base MOU with `{placeholders}`.
- `base/MOU_base_15Jul2026.docx` – original base MOU.
- `tools/build_template.py` – turns the base MOU XML into the placeholder template (run from an unzipped base docx; see header notes).
- `tools/app-source.html` – app source; `__TEMPLATE_B64__` is replaced with the base64 of the template.

## Updating the base MOU
1. Unzip the new base docx, run `tools/build_template.py` (paragraph indexes may need checking if the wording or layout changes).
2. Zip the result to `template/MOU_template.docx`.
3. Base64-encode it into `tools/app-source.html` in place of `__TEMPLATE_B64__` and save as `app/mou-generator.html`.
