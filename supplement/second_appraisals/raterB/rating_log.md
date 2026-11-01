# PROBAST+AI second appraisal — AI rating log (Claude)

**These ratings were produced by an AI model (Claude, Anthropic), not by an independent human second assessor.**
Rated only from the 48 primary-paper PDFs in this folder (text extracted with pdftotext; figure pages viewed as images where needed). No review manuscript, review supplement or web search was used.

Disclosure: when first inspecting the workbook structure, a programmatic dump of all sheets briefly displayed the first ~15 rows of the `Extraction_Check` sheet (first rater's extracted numbers and a short "Detail" note for Banerjee 2010 – Liu X 2023). After noticing this, the sheet was not looked at again until all 48 ratings were complete. Ratings below were made from the papers.

## Operational rules applied consistently (in addition to the workbook rules)

**Step 0 – intended use.** Taken from the authors' stated purpose; where not stated, judged from the latest-timed predictor and framing ("as you judge it"). "not stated" used only when it cannot be inferred. All domains rated against that decision point.

**D1 Participants/data.**
- low: routinely collected cohort / registry / EHR data (retrospective is acceptable for a prognostic question) and inclusions/exclusions consistent with the intended use.
- unclear: data source or eligibility insufficiently described; substantial unexplained exclusions (e.g. loss to follow-up / unknown outcome >10% or not quantified when exclusions are clearly made).
- high: sample conditioned on a post-decision event inconsistent with the intended use (e.g. pre-treatment model built only on cycles reaching transfer), case-control-type sampling, or exclusions plainly related to the outcome.

**D2 Predictors.**
- high: any predictor not available at the intended decision point (e.g. embryos transferred / embryo quality in a pre-treatment model; post-transfer hCG in a pre-transfer model), or outcome-derived variables.
- unclear: predictor set not reported well enough to judge timing.
- otherwise low (routine clinical/lab variables recorded before the outcome).

**D3 Outcome.**
- low: live birth (or cumulative live birth) explicitly defined (any operational definition, e.g. delivery of ≥1 live-born infant, with or without gestational threshold; for CLBR the episode/denominator stated) and determined uniformly from records/follow-up.
- unclear: outcome only named, not defined, or CLBR follow-up window/censoring not described.
- high: surrogate/composite outcome, or sample conditioned on a later event (e.g. only clinical pregnancies).

**D4 Analysis.**
- high (any one): no calibration assessment at all (chosen option of decision rule 1 — recorded in Notes); apparent performance only; any preprocessing (imputation, scaling, feature selection, SMOTE/rebalancing) fitted on the whole dataset before the split / outside CV; evaluation on rebalanced or synthetic data; predictor selection by univariable significance testing (PROBAST 4.5); clear non-independence (same patients' cycles/embryos in train and test); hyperparameters tuned on the test set; too few events (dev EPV <10 candidate predictors, or the only hold-out/external test set <100 events with no resampling-based validation).
- unclear: missing-data handling not reported; complete-case exclusion >10% without justification (decision rule 2); patient-level independence not addressed where repeat cycles exist; other key details not reported.
- low only if none of the above.

**Additional consistency rules applied during rating (checked across all 48 at the end).**
- Studies with several models (stage-specific / pre- and post-treatment / multiple cohorts): each domain rated at the worse model; intended use recorded for the first-listed model.
- A Brier score counts as a calibration assessment (protocol rule; first pass did not accept Brier alone - see Revision); calibration "mentioned in Methods" but not reported = not assessed (-> D4 high, rule 1).
- Outcome including ongoing pregnancy (composite), or sample conditioned on clinical pregnancy -> D3 high.
- CLBR with remaining frozen embryos counted as failures, or follow-up/censoring not described -> D3 unclear.
- Test/validation set used to choose the final model -> D4 high.
- Contradictory description of whether preprocessing was fitted before or after the split -> D4 unclear (not high), e.g. Fatmawati 2026.
- Cohort restricted to oocyte-retrieval cycles (not transfer) for a pre-treatment model, with cancellations <10% and characterised -> D1 low (Cai 2024); exclusion of no-oocyte/no-transferable-embryo cycles -> D1 high (Xing 2025).

**Overall.** low only if all four low; high if any high; otherwise unclear.

**Full text read.** "yes" = entire article PDF read (main text, tables, figures). Supplementary files not contained in the PDF were not available; noted where it matters.

---

## Per-study evidence notes

### 01 Banerjee 2010
- Intended use: after failed cycle
- D1 unclear: Single-clinic database (appropriate), but exclusion criteria only in SI (not in PDF); 5,035 treatments -> 3,117 eligible, restricted to 'completed' cycles with complete embryo data, numbers excluded per reason not given (Results p.2; Methods p.6; Fig 1B).
- D2 low: For the intended after-failed-cycle use (IVFBT-C2), all predictors are C1 clinical/embryo data known once C1 has failed.
- D3 low: Live birth defined as delivery of live baby >24 wk after fresh or linked frozen transfers (Methods p.6).
- D4 high: External (temporal) validation of the C2 model used only 230 cycles (necessarily <100 events; C2 LBR ~18%) (Results p.4, Fig 3B/F); dev EPV ~486 events/52 candidate variables (<10); C2 adjustment fitted on returners only; missing-data handling not described. Calibration was assessed (HL + plot).
- Overall: **high**
- Notes: Two models: IVFBT (C1, uses transfer/embryo data) and IVFBT-C2 (after failed cycle; authors' stated clinical use, Discussion p.4-5); rated against the C2 use. Supplementary Information not in PDF.
- Evidence: PNAS 2010; 1,676 C1 train 2003-06; validation 634 C1/230 C2 2007-08; GBM 52 vars; AUC 0.80 (C1) / 0.68 (C2).

### 02 Qiu 2019
- Intended use: before treatment
- D1 unclear: 1,732 of 9,256 women (18.7%) excluded for no pregnancy-outcome follow-up; no comparison of excluded vs included (Results p.3).
- D2 low: Eight pre-treatment predictors only (age, AMH, BMI, infertility duration/type, obstetric history) (p.3-4).
- D3 unclear: CLB of first complete cycle (fresh + all FET from that stimulation) defined via WHO live birth, but cycles run to Dec 2018 and follow-up window/handling of women with remaining frozen embryos not described (Methods p.2).
- D4 low: Knowledge-based predictor selection; 2,797 events/~12 parameters; complete-case exclusion only 336 (3.6%); 70/30 stratified split with tuning by CV in training, nested CV; calibration plot on test set (Fig 2b).
- Overall: **unclear**
- Notes: Hyperparameters tuned on accuracy; calibration assessed only graphically. D1 rule: loss to follow-up >10% -> unclear.
- Evidence: J Transl Med 2019; 7,188 women, 39% CLB; XGBoost AUC 0.73 test.

### 03 Bras de Guimaraes 2020
- Intended use: before transfer
- D1 low: Single public-hospital IVF centre cohort 2012-2019; only cycles with LB or no surplus embryos left (complete follow-up), consistent with pre-transfer use.
- D2 low: Final inputs (age, AFC, gonadotropin dose, eggs, embryos) all available before first transfer.
- D3 low: Live birth = at least one infant born alive after 24 weeks, fresh + frozen transfers (Section 2.2 p.3).
- D4 high: SMOTE+Tomek links applied to whole 2012-18 dataset before split; ANN hold-out (15%) evaluated on rebalanced/synthetic data (Section 2.4 p.3-4); inputs chosen by univariable Pearson correlation p<0.05 (p.4, p.10); no calibration; participants excluded for missing AMH/AFC not quantified.
- Overall: **high**
- Notes: No calibration -> high (rule 1 option chosen). Decision rule 3 (synthetic data / pre-split rebalancing) applies.
- Evidence: Reprod Med 2020; 1,193 cycles, 387 LB; ANN AUC 0.752.

### 04 Goyal 2020
- Intended use: before treatment
- D1 unclear: HFEA registry is appropriate, but filtering from 495,630 to 141,160 records only vaguely described and unit is treatment-cycle records (fresh and frozen cycles mixed) despite 'complete IVF cycle' aim (Methodology p.2-3).
- D2 high: 'Pre-treatment' model includes eggs collected, eggs mixed with partner sperm, embryos transferred, fresh/frozen cycle (Table 1 p.4).
- D3 unclear: Outcome = HFEA 'live birth occurrence' field recoded ('greater than 1' = birth) per cycle record; no definition, inconsistent with complete-cycle framing (p.3).
- D4 high: Majority class undersampled to 1:1 before the 66/34 split, so test set is rebalanced; normalisation before split; no calibration; no missing-data handling reported (Preprocessing p.3).
- Overall: **high**
- Notes: No calibration -> high (rule 1). Decision rule 3 applies (evaluation on rebalanced data).
- Evidence: Sci Rep 2020; HFEA 2010-16; RF AUC 0.846.

### 05 Amini 2021
- Intended use: before treatment
- D1 high: Only women with a confirmed clinical pregnancy (gestational sac) were included, inconsistent with authors' stated pre-treatment use (Methods p.2; Discussion p.6).
- D2 high: Predictors include number of transferred embryos, embryo quality components, fertilization rate, injected oocytes, day of ET (Methods p.2).
- D3 high: Outcome 'successful delivery' (undefined) conditional on clinical pregnancy (81.2% event rate) (p.2-3).
- D4 high: PCA of embryo variables fitted on full dataset before 70/30 split; no calibration; missing-data handling not reported; very low discrimination (AUC 0.60) (Statistical analysis p.2).
- Overall: **high**
- Notes: Intended use taken from Discussion ('predict ... before the treatment procedure', p.6). No calibration -> high (rule 1).
- Evidence: IJFS 2021; 6,071 cycles with clinical pregnancy; RF AUC 0.60 (0.55-0.64).

### 06 Liang 2021
- Intended use: before transfer
- D1 low: Single-centre FET cycles 2012-2015 from medical records; donor and dropped-out cycles excluded, consistent with pre-FET use.
- D2 low: Predictors (age, BMI, HOMA-IR, basal hormones, endometrial thickness, embryos available/transferred) available before FET.
- D3 low: Live birth = delivery of any viable neonate at >=28 weeks, from medical records (Section 2.3 p.2).
- D4 high: Predictor screening by RF importance trained on all samples before 10-fold CV (Section 2.5 p.2); no calibration; only cycles 'with complete protocols and outcomes' (excluded number not reported); patient clustering of FET cycles not addressed.
- Overall: **high**
- Notes: No calibration -> high (rule 1). Decision rule 3 (feature selection before split).
- Evidence: CMPB 2021; 2,189 FET cycles, 815 LB; RF AUC 0.83 (10-fold CV).

### 07 Benchaib 2022
- Intended use: before transfer
- D1 high: Cycles with live birth were excluded when number of babies did not match number of blastocysts transferred, whereas failed multi-embryo transfers were kept: exclusion depends on outcome (Section 2.2 p.2; p.4); 876 -> 654 cycles.
- D2 low: ART and morphokinetic (tM, tSB, tB) variables and number transferred are available at the transfer decision; recorded prospectively.
- D3 unclear: Live birth/delivery not defined (gestational threshold, source); embryo-level labels derived from cycle-level delivery (KID) (p.4).
- D4 high: Validation set has only 49 deliveries (196 cycles) (Table 2 p.5); no calibration; missing data acknowledged but handling not reported (Discussion p.8).
- Overall: **high**
- Notes: No calibration -> high (rule 1).
- Evidence: RMB 2022; 654 cycles/1,027 blastocysts; MLP AUC 0.866 validation.

### 08 Chen Z 2022
- Intended use: after stimulation
- D1 low: Consecutive single-centre IVF/ICSI patients with tubal/male infertility 2014-2018; exclusions (donor gametes, endometriosis, endocrine disease) consistent with use.
- D2 low: Latest predictors are hormones on the day after trigger and total FSH, available at the judged decision point (after stimulation); no transfer variables.
- D3 unclear: Live birth >28 wk, cumulative over fresh + all FET from the same stimulation, but follow-up window and handling of patients with remaining frozen embryos (data to March 2018) not described (p.1-2).
- D4 high: No data split or resampling validation described: AUC 0.901 appears to be apparent performance on development data; patients with missing data excluded without numbers (p.1-2).
- Overall: **high**
- Notes: Short correspondence (3 pages); supplementary tables not in PDF. Calibration curve shown (Fig 1C). Intended use not stated by authors; judged from predictors (post-trigger hormones).
- Evidence: Chin Med J 2022; 3,012 patients; XGBoost AUC 0.901 (0.890-0.912) vs LR 0.724.

### 09 Zhang 2022
- Intended use: before treatment
- D1 high: Stated pre-treatment model, but only cycles 'with completed ET' were included (Data Acquisition p.2); HFEA cycle records with no stimulation (includes frozen cycles) labelled NC-IVF.
- D2 high: Feature list includes embryos transferred, elective single embryo transfer, fresh/frozen cycle, PGD/PGS (Table 1 p.4), not available before treatment.
- D3 low: HFEA field: one or more live births resulting from the cycle (Table 1), recorded uniformly in the registry.
- D4 high: Negatives undersampled to 1:1 and the 'best' balanced sub-dataset chosen by pre-training before 10-fold CV, so evaluation is on rebalanced data; z-score normalisation on whole data; no calibration; repeated cycles of the same patient not identifiable (p.3, p.9).
- Overall: **high**
- Notes: No calibration -> high (rule 1). Decision rule 3 applies.
- Evidence: Front Endocrinol 2022; 57,558 HFEA cycles; ANN AUC 0.794, LogitBoost 0.791.

### 10 Liu X 2023
- Intended use: before treatment
- D1 unclear: Temporal test cohort for 2021 contains only 78 women versus ~900/yr in 2019-2020, selection not explained (Fig 1 p.4).
- D2 high: The 'after first cycle' model includes serum hCG level (<5 vs >=5, i.e. the post-transfer pregnancy test; 508/509 hCG<5 had no LB, Table 1 p.6), plus transfer variables, while predicting the same cycle's live birth (p.3).
- D3 low: Live birth = delivery of >=1 live baby at >=24 weeks (Outcome p.3).
- D4 high: No calibration assessed; temporal test set 78 women (<100 events); 'bootstrap validation' resamples the total dataset including training data; complete-case deletion of 155/1,973 (7.9%) (Methods p.3, Fig 1, Table 2).
- Overall: **high**
- Notes: Two models (pre-cycle; pre+post-cycle). Rule: with several headline models, each domain rated at the worse of them; intended use recorded for the first (pre-treatment) model. No calibration -> high (rule 1).
- Evidence: BMC Preg Childbirth 2023; 1,857 women, 851 LB; LGBM AUC 0.612/0.634 (pre) and 0.816/0.835 (post).

### 11 Mourad 2023
- Intended use: after positive test
- D1 unclear: Positive-test e-SET patients 'with no loss to follow-up' selected (consistent with use) but number lost/excluded not reported (Methods p.2).
- D2 low: Age, beta-hCG 1 and 2 (48 h apart), treatment type are available at the intended point (after confirmed positive test).
- D3 low: Live birth = live fetus >=24 weeks vs non-viable pregnancy, from records (p.2).
- D4 high: Univariable screening (P<0.2) then backward stepwise selection (Methods p.2); missing data handled by pairwise deletion; calibration stated as evaluated but no calibration results reported (p.2-3); ML models only in supplement.
- Overall: **high**
- Notes: Final POPI-Plus is logistic regression; tree/RF/NN comparators (AUC>=0.7) in Supplemental Fig 1 (not in PDF). Univariable selection -> high (PROBAST 4.5).
- Evidence: Fertil Steril 2024; 1,995 pregnant e-SET patients; AUC 0.78 validation.

### 12 Cai 2024
- Intended use: before treatment
- D1 low: All OPU cycles 2013-2020 in one centre; exclusion of incomplete cycles (2,223, 7.7%) and non-medical cancellations is explained and characterised (Supp Table S1).
- D2 low: Only pre-treatment patient characteristics, history, diagnoses and basal endocrine profile/AFC.
- D3 low: Cumulative live birth per OPU over 2 years, first delivery counted, fresh + linked FET (Study cohort p.2).
- D4 high: Multiple imputation (MICE) applied to the full cohort of 28,743 cycles before the temporal split (Missing data p.2) - pre-split preprocessing. Otherwise strong: temporal validation (2,296 cycles, ~1,500 events), calibration slope/intercept reported.
- Overall: **high**
- Notes: D4 high driven only by decision rule 3 (imputation before split; 4.9% cycles imputed) - human verifier may judge this minor. Repeat OPUs of same patient across years not addressed. Final centre model = LASSO; XGBoost also developed.
- Evidence: Hum Reprod 2024; 26,382 OPU; centre-specific AUC 0.71 (0.71-0.72).

### 13 Liu L 2024a
- Intended use: before transfer
- D1 unclear: Single-centre fresh-transfer cycles; study period, consecutive sampling and number excluded not reported (Methods p.2).
- D2 low: Age, OSI, COS regimen, Gn start dose, endometrial thickness and P on hCG day, transfer strategy are all available at the transfer decision (the stated use: recommending transfer strategy).
- D3 low: Live birth = delivery of a live fetus at >=28 weeks surviving >=1 month (Methods p.2).
- D4 high: Predictors selected by univariable then multivariable P<0.05 on the full dataset before splitting (p.4-5); split ratio chosen by trial-and-error for best performance (p.3); no calibration on test set; calibration only in 82-patient application sample (<100 events) (p.8).
- Overall: **high**
- Notes: Univariable selection -> high (PROBAST 4.5). Model also used to recommend transfer strategy (causal use not supported by a prognostic model).
- Evidence: RBE 2024; 1,405 patients, 592 LB; SVM AUC 0.854 test, 0.862 in 82 new patients.

### 14 Liu L 2024b
- Intended use: before transfer
- D1 low: Two-centre AMA (>=35 y) single vitrified-warmed blastocyst transfer cycles 2016-2022 from ART database; consistent with use.
- D2 low: Patient, stimulation and embryo morphology variables known before FET.
- D3 low: Live birth = delivery of any viable infant at >=28 weeks (Clinical outcomes p.3).
- D4 high: SMOTE applied and the balanced (synthetic) data then split 75/25, so validation is on rebalanced data (Data pre-processing p.4); no calibration; repeat cycles of same patients treated as independent (Limitations p.10).
- Overall: **high**
- Notes: Decision rule 3 applies. No calibration -> high (rule 1).
- Evidence: RBE 2024; 1,168 SVBT cycles, 352 LB; stacking AUC 0.791.

### 15 Liu Z 2024
- Intended use: before transfer
- D1 low: All single-blastocyst transfers 2013-2019 in one centre with complete outcome; 23 excluded for follow-up flaws (p.2).
- D2 low: Cycle and embryo (D3 and blastocyst) morphology variables available at the transfer decision.
- D3 low: Live birth = delivery of >=1 viable infant after 27 weeks (p.2).
- D4 high: Reported AUCs (e.g. XGBoost 0.83) are computed on the full development dataset of 8,383 cycles (Table 3) - apparent performance; split-sample validation only in Supp Table S3 (not in PDF); XGBoost calibration suboptimal (Fig 2); multiple transfers per patient not accounted for.
- Overall: **high**
- Notes: Supplementary tables not in PDF. Primary aim is incremental value of D3 morphology.
- Evidence: JARG 2024; 8,383 SBT cycles, LBR 48%; XGBoost AUC 0.83.

### 16 Peng 2024
- Intended use: before treatment
- D1 low: All couples starting IVF 2015-2022 at one centre; lost to follow-up 452/11,938 (3.8%) (Fig 1, p.3).
- D2 high: Model intended 'at the beginning of IVF' / baseline triage (p.2, p.6) but includes E2, LH and P on hCG day (post-stimulation) (Results p.4).
- D3 unclear: Outcome 'whether a live birth occurred during a single ART cycle' not defined (no threshold) and which cycle per couple is used is unclear (Methods p.2).
- D4 high: Univariable (P<0.10) then multivariable screening and ML importance ranking on full data, ROC-optimal dichotomisation of predictors on full data, before CV/bootstrap (p.2-4); complete-case exclusion 1,682/13,620 (12.3%); calibration only as Brier score.
- Overall: **high**
- Notes: Final recommended model is logistic regression; RF AUC 0.674. Brier score alone not counted as calibration assessment.
- Evidence: Sci Rep 2024; 11,486 couples, 3,097 LB; RF AUC 0.674 CV.

### 17 Abdala 2025
- Intended use: before transfer
- D1 low: All autologous single euploid FET cycles Mar 2017-Dec 2023 in one clinic (p.2).
- D2 low: Final predictors (BMI, ICM/TE grade, biopsy day, endometrial preparation, endometrial thickness) available before transfer.
- D3 unclear: Live birth not defined (no gestational threshold or ascertainment described) (Methods p.2-3).
- D4 high: Predictors chosen from univariable then multivariable significance in the full dataset before repeated CV (Table 2, p.3-4); missing-data handling not reported. Strengths: patient-level splits, calibration intercept/slope reported.
- Overall: **high**
- Notes: Final model is LR; RF/SVM/XGBoost comparators overfitted. Univariable selection -> high (PROBAST 4.5).
- Evidence: JARG 2025; 1,979 seFET (1,459 couples); LR C 0.626, RFC 0.606.

### 18 Bai 2025
- Intended use: before transfer
- D1 high: 1,255 of 3,880 women (32%) excluded for missing data or loss to follow-up (p.2, Fig 1); live-birth model restricted to the 2,031 women with clinical pregnancy.
- D2 high: Feature set includes serum hCG result (post-transfer pregnancy test) (Data preprocessing p.6); pregnancy AUC 0.999 indicates leakage.
- D3 high: Live-birth model built only among clinical pregnancies (1,711 LB + 320 no LB = 2,031) (p.2); live birth not defined.
- D4 high: Complete-case analysis (32% excluded); z-score standardisation and LASSO selection before split; no calibration; 'test'/'training' sizes contradictory (p.6-7); abstract AUC 0.913 is training performance (test 0.746, Table 2).
- Overall: **high**
- Notes: Authors state model is not for pre-treatment counselling; aim to reduce unnecessary transfers (p.10). No calibration -> high (rule 1).
- Evidence: BMC Preg Childbirth 2025; 2,625 women; LightGBM LB AUC 0.913 train / 0.746 test.

### 19 Borji 2025
- Intended use: not stated
- D1 unclear: HFEA registry 2010-2018 (665,244 records) reduced to 115,012 by vague criteria (e.g. excluded if eSET field missing) without flow of numbers (Section 2.3 p.5).
- D2 high: PSO-selected predictors include outcome-derived fields: heart one delivery date, heart one weeks gestation, heart two delivery date, total live births (Table 6 p.16-18).
- D3 unclear: Outcome = HFEA 'live birth occurrence' field, not defined; cycle-level records (p.5).
- D4 high: Imputation, normalisation, PSO feature selection and PCA performed on full data before 10-fold CV (Section 2.2-2.3); no calibration; implausible AUC 0.99.
- Overall: **high**
- Notes: No decision point stated; predictors span pre-treatment to post-delivery fields. No calibration -> high (rule 1).
- Evidence: CMPB 2025; 115,012 HFEA records; PSO+TabTransformer AUC 0.9996.

### 20 Cumberbatch 2025
- Intended use: after stimulation
- D1 unclear: 213 cycle records from one clinic; 23 (10.8%) removed for missing/invalid outcome; period and selection not reported (Methodology p.2).
- D2 low: Age, AMH, AFC, BMI, prior attempts and MII eggs after retrieval - available at the judged point (after oocyte retrieval).
- D3 unclear: Live birth not defined (Methodology p.2).
- D4 high: 190 cycles (~55 events); hold-out 37 cycles with 11 live births (Table 2); median imputation and scaling before split; SMOTE; no calibration; repeat cycles treated as independent (p.2-4).
- Overall: **high**
- Notes: Intended use not stated by authors (counselling/embryo prioritisation, p.5); judged from MII eggs. No calibration -> high (rule 1).
- Evidence: JSCI 2025; 190 cycles; linear SVM AUC 0.72.

### 21 Jain 2025
- Intended use: not stated
- D1 unclear: 2,000 HFEA 2010-2016 records 'filtered' from the registry with no selection criteria reported (Section 3.1 p.4).
- D2 unclear: 62 of 95 HFEA fields retained incl. 'clinical treatment details and embryonic data', not listed; timing cannot be judged (near-perfect AUC 0.999-1.0 suggests outcome-proximal fields) (p.4).
- D3 unclear: Outcome = HFEA number of live births dichotomised; not defined (Section 3.2 p.6).
- D4 high: Median/mode imputation on whole dataset before split; SMOTE and RFECV; no calibration; implausible AUC 0.999-1.0 (Sections 3.1-3.2, Table 4).
- Overall: **high**
- Notes: No calibration -> high (rule 1).
- Evidence: Informatica 2025; 2,000 HFEA cases; stacking AUC 0.999.

### 22 Lantzi 2025
- Intended use: before treatment
- D1 unclear: Registry-type dataset (1.55 million attempts 1991-2018; 665,244 records 2010-2018) described only as 'the clinic'; includes donor insemination (DI), donor-egg and frozen cycles alongside IVF; selection steps not quantified (Sections 2.1, 2.3.1 p.10-11).
- D2 high: Headline/deployed 'complete features' model uses in-cycle variables (embryos transferred, total embryos created, embryos stored, fresh eggs collected, eggs mixed) (Table 9 p.20), while the stated aim is prediction before starting treatment; a separate pre-cycle model (AUC 0.672) was also built.
- D3 low: Registry field 'live birth occurrence' with WHO live-birth definition stated (Section 2.3.3 p.11).
- D4 unclear: DataRobot autopilot with CV + 20% holdout and lift-chart (binned) calibration on holdout (Fig 9); but repeated cycles of the same patients across folds not addressed, handling of remaining missing values not described, and deployed model refitted on 100% of data (Table 8).
- Overall: **high**
- Notes: Two models (complete-feature and pre-cycle); domains rated at the worse of the two. Lift chart counted as a (weak) calibration assessment. Text extraction of figure pages partly garbled; key methods/results read.
- Evidence: Biology 2025; 665,244 records 2010-2018; XGBoost AUC 0.747 (complete), Keras 0.672 (pre-cycle).

### 23 Liu Y 2025
- Intended use: before transfer
- D1 unclear: 48,514 fresh IVF cycles 2009-2018 from one EMR; no eligibility/exclusion criteria or numbers reported; a more recent dataset was discarded for missingness (Patient selection p.2; Results p.4-5).
- D2 low: Latest predictors are 2PN, transferable and high-quality embryo counts - available at the judged decision point (before fresh transfer); intended use not stated by authors.
- D3 unclear: Live birth not defined; reported precision 0.935 with recall ~1.0 implies ~93% of cycles labelled positive, inconsistent with a per-cycle live-birth rate, so outcome coding unclear (Table 1 p.8).
- D4 high: Mean imputation and min-max scaling on whole dataset before the 80/20 split; XGBoost importance-based feature selection apparently on full data; no calibration; AUC reported as CV on training data (Data preprocessing p.3).
- Overall: **high**
- Notes: No calibration -> high (rule 1). Decision rule 3 applies.
- Evidence: Front Endocrinol 2025; 48,514 cycles; CNN AUC 0.890, RF 0.973.

### 24 Sengupta 2025
- Intended use: before treatment
- D1 unclear: 2,908 records -> 1,993 (31% removed): embryo-level duplicate rows, retained 'only cases where a full IVF cycle was carried out or a successful live delivery occurred', no follow-up, PGD/donor/surrogacy (Data acquisition p.3-4).
- D2 high: Stated pre-treatment model includes beta-hCG, described by authors as the placental hormone indicating clinical pregnancy (p.2-3).
- D3 unclear: Cumulative live birth for the first complete cycle, but live birth and follow-up of remaining frozen embryos not defined (p.2-3).
- D4 high: Train/test split ratio chosen because other splits gave inferior metrics (Model training p.4); discretisation and encoding of predictors on full data; hCG leakage; calibration plot only.
- Overall: **high**
- Notes: 
- Evidence: IJCMPH 2025; 1,993 women; BoVe AUC 0.93.

### 25 Wu 2025
- Intended use: before transfer
- D1 unclear: 51,047 records -> 13,362 fresh-transfer records 'with fully tracked outcomes' -> 11,728; number lost to follow-up not reported; record (not patient) level (Results p.3, Fig 1).
- D2 low: Pre-transfer patient, stimulation and embryo variables for fresh cleavage-stage transfer.
- D3 unclear: Live birth not defined (threshold, ascertainment) (Methods p.2).
- D4 high: missForest imputation on the full dataset before splitting (p.3); feature reduction using P<=0.05 / RF importance on full data (p.3, Table 1); repeat cycles not addressed. Calibration curves and Brier score reported (Supp Fig S2).
- Overall: **high**
- Notes: Univariable selection -> high. Decision rule 3 applies.
- Evidence: J Transl Med 2025; 11,728 records, 3,971 LB; RF AUC 0.808 (80/20).

### 26 Xing 2025
- Intended use: before treatment
- D1 high: Stated pre-treatment model, but cycles with no oocytes retrieved or no transferable embryos (n=112) and interrupted/incomplete treatment (n=81) were excluded (Methods p.359; Fig 1 p.361).
- D2 low: Only pre-treatment clinical, ovarian reserve and semen variables (authors: variables obtainable before treatment, p.359).
- D3 low: CLBR per started cycle: >=1 live infant from fresh + all FET from that stimulation; incomplete cycles excluded (p.359).
- D4 high: Mean/mode imputation and z-standardisation of all data before the 70/30 split (Methods p.359-360); test set ~311 events; calibration curve shown (Fig 2B).
- Overall: **high**
- Notes: Chinese-language paper read in full from page images. Decision rule 3 applies.
- Evidence: Chin J Reprod Contracep 2025; 1,792 cycles, CLBR 57.8%; XGBoost AUC 0.775.

### 27 Yao 2025
- Intended use: before treatment
- D1 low: First IVF cycles from six US centres' EMR/SART CORS data; inclusion/exclusion criteria explicit and consistent with pre-treatment counselling (cancelled and no-blastocyst cycles kept as failures) (Methods p.10).
- D2 low: Pre-treatment predictors only (age, BMI, AMH, ovarian reserve, diagnoses, reproductive history).
- D3 high: MLCS training/test label 'live birth' includes clinical ongoing pregnancies (composite outcome) (IVF labeling criteria p.10; p.11); sensitivity test set DNMV2 removing these (~4.8%) gave similar results.
- D4 high: Calibration (Brier, plots), PR-AUC and F1 were computed with 'production model responses' on DNMV1, i.e. the deployed model trained on data that include the test cycles (p.11) - in-sample; ROC-AUC from internal CV; some centre datasets small (101-500 cycles). Out-of-time LMV for MLCS1 is a strength.
- Overall: **high**
- Notes: Commercial (Univfy) authors; GBM models. Composite outcome rule -> D3 high.
- Evidence: Nat Commun 2025; 4,645 first cycles, 6 centres; MLCS ROC-AUC median 0.66-0.67.

### 28 Zhu 2025a
- Intended use: before transfer
- D1 low: PCOS antagonist fresh-transfer cycles 2019-2023, one centre; exclusions quantified (1,431 -> 1,062; 87 for missing data) and clinically motivated (Fig 1 p.4).
- D2 low: Final predictors (embryos transferred, embryo type, age, infertility duration, BMI, testosterone, P on hCG day) available before fresh transfer.
- D3 low: Live birth = delivery >=28 weeks with >=1 vital sign (p.3).
- D4 high: missForest imputation performed during data preprocessing on the whole dataset before the 7:3 split (Data collection and preprocessing p.3); LASSO/RFE in training set; calibration curve and Brier score on test set (Fig 4); cycles of same patient not addressed.
- Overall: **high**
- Notes: D4 high driven by decision rule 3 (imputation before split).
- Evidence: J Ovarian Res 2025; 1,062 cycles, 466 LB; XGBoost AUC 0.822 test.

### 29 Zhu 2025b
- Intended use: before transfer
- D1 low: Endometriosis fresh-transfer patients 2018-2023, one centre; exclusions quantified (2,217 -> 1,836; 73 for missing data) (Fig 1 p.3).
- D2 low: Predictors (AMH, age, AFC, infertility duration, protocol, rAFS, fertilised oocytes, embryos transferred) known before transfer.
- D3 low: Live birth = viable neonate >=28 weeks with vital signs (also <28 w if sustained vital functions) (p.4).
- D4 high: Mean/mode imputation in data preparation on the whole dataset before the 70/30 split (Data preparation p.4); LASSO+RFE; calibration curves on validation set (Fig 3D).
- Overall: **high**
- Notes: D4 high driven by decision rule 3 (imputation before split).
- Evidence: JARG 2025; 1,836 patients, 739 LB; XGBoost AUC 0.852 test.

### 30 Alson 2026
- Intended use: before treatment
- D1 low: Prospective cohort of women starting first IVF/ICSI at one Swedish centre (2019-2022) with standardised pre-treatment ultrasound (p.2).
- D2 low: Pre-treatment predictors (age, BMI, AMH, AFC, MUSA ultrasound features, symptoms) assessed prospectively by one examiner before outcome.
- D3 low: Cumulative LB from all embryos of the index cycle, live birth >22 weeks (p.2).
- D4 high: No calibration assessed; ~30 candidate variables for 424 events; test set ~207 women (~85 events); variables removed using SHAP importance (stage unclear) (Model development p.2-3).
- Overall: **high**
- Notes: Pilot study; AUC 0.66 test. No calibration -> high (rule 1).
- Evidence: Sci Rep 2026; 1,037 women, CLBR 40.9%; XGBoost AUC 0.66 test.

### 31 Bai J 2026
- Intended use: before transfer
- D1 unclear: 2,872 PCOS first-FET patients -> 1,756: 477 (16.6%) excluded for incomplete follow-up and 306 for multiple missing variables; authors acknowledge selection bias (Fig 1 p.112; Discussion p.119).
- D2 low: Endocrine/metabolic/inflammatory indices from <=3 months before FET plus embryo stage/number transferred - available before transfer.
- D3 low: Live birth = birth >=28 weeks or >=1,000 g with vital signs (p.111).
- D4 high: Calibration curve listed in methods but no calibration results shown (only ROC/SHAP, Fig 4-7); mean imputation and SMOTE in preprocessing with order relative to split unclear (p.111); 306 complete-case exclusions plus 477 follow-up exclusions (27%).
- Overall: **high**
- Notes: Chinese-language paper read in full from page images. Final best model LR (AUC 0.745). Calibration not reported -> treated as not assessed (rule 1 option).
- Evidence: Chin J Reprod Contracep 2026; 1,756 PCOS FET; AUC 0.725-0.745.

### 32 Chen 2026
- Intended use: after stimulation
- D1 unclear: GH-treated women <40 y, one centre 2015-2023; exclusions (loss to follow-up >=1 y, incomplete data) only quantified in Supplementary Figure 1 (not in PDF) (Patients and methods p.2-3).
- D2 low: Predictors (age, AMH, AFC, ART cycle number, GH duration up to oocyte retrieval, Gn dose) available by the end of stimulation; intended use not stated by authors.
- D3 low: CLB = >=1 live birth from fresh + all frozen transfers of that retrieval until LB or embryos exhausted; cancellations counted as no CLB (Definitions p.2).
- D4 high: Univariable P<0.05 screening then multivariable P<0.05 selection on the full dataset; ML models used these variables, with performance by CV/bootstrap (Statistical analysis p.3); complete-case exclusion number not reported; calibration plots only in supplement.
- Overall: **high**
- Notes: Univariable selection -> high (PROBAST 4.5). Best model was LR (AUROC 0.782).
- Evidence: Front Endocrinol 2026; 1,782 women, 763 CLB; RF AUROC 0.729.

### 33 Fatmawati 2026
- Intended use: before transfer
- D1 unclear: Two Indonesian centres, first IVF/ICSI cycle in PCOS 2018-2023; records with >10% missing variables excluded a priori but number excluded not reported (Participants p.3; Data quality p.4).
- D2 low: Baseline, stimulation and embryology variables (oocytes, top-quality embryos) - available before first transfer (judged decision point; authors: counselling and cycle management).
- D3 unclear: CLB defined (>=24 wk, fresh + all FET), but women with unused cryopreserved embryos at data cut were classified as no live birth (p.3); extent not reported.
- D4 unclear: Contradictory description: pipeline states standardisation and KNN imputation before the 70/30 partition (p.4) whereas data-quality section says these were fitted within training folds only; predictor selection process not described. Calibration slope/intercept reported.
- Overall: **unclear**
- Notes: Information contradictory -> unclear rather than high (decision rule 'not reported -> unclear').
- Evidence: SJOG 2026; 1,245 PCOS women, CLBR 54.6%; XGBoost AUC 0.82.

### 34 Fraire-Zamora 2026
- Intended use: not stated
- D1 low: First autologous ICSI cycle per patient at three private clinics 2011-2023 from EMR; eligibility consistent with the explanatory aim.
- D2 high: Predictors include total number of D3/D5 embryos transferred (fresh + cryopreserved) across the completed cycle and number of transfers per cycle, which depend on the outcome (transfers stop at live birth) (Table 3 p.5; Table 1).
- D3 low: Cumulative LB per completed ICSI cycle, live birth >28 weeks, follow-up >=1 year (p.2).
- D4 high: 12,308 -> 8,066 cycles (34.5% excluded for missing data); kNN imputation and SHAP-based feature selection on the whole dataset outside the nested CV; missing donor-sperm values simulated; no calibration (p.2-4).
- Overall: **high**
- Notes: Authors state the main purpose is explanation, not building a predictive model (p.8). No calibration -> high (rule 1).
- Evidence: JARG 2026; 8,066 cycles, 40% LB; mean AUC 0.889.

### 35 Fu 2026
- Intended use: before transfer
- D1 unclear: OPU cycles 2019-2024 restricted to those with embryo transfer and defined outcome; numbers excluded not retained/reported (authors' Limitation 4, p.12); repeat cycles of same woman not identifiable.
- D2 low: Primary (Stage 3) predictors (age, embryo quality/number transferred, transfer type, cycle number, protocol, parity) available at the first transfer decision.
- D3 unclear: CLB per OPU, but 'conservative' definition counts cycles with untransferred cryopreserved embryos as no live birth and recent cycles had short follow-up (Methods p.2; Limitation 2 p.12).
- D4 high: Continuous variables z-score standardised before the 70/30 split (p.3) - pre-split preprocessing; feature ranking on training partition; calibration curves, temporal validation and benchmark are strengths; clustering of repeat cycles not addressable.
- Overall: **high**
- Notes: D4 high driven only by decision rule 3 (scaling before split; minor for tree models). Stage-specific models also reported.
- Evidence: Front Endocrinol 2026; 7,773 OPU cycles; GB AUC 0.762 test, 0.712 temporal.

### 36 Guo 2026
- Intended use: before treatment
- D1 high: Stage 1 'baseline' (pre-treatment) model developed only on first cycles that reached fresh embryo transfer; cancellations before OPU or ET excluded (Methods p.2).
- D2 low: Stage-specific predictor sets restricted to variables available at each stage (baseline / stimulation / embryo development) (p.2-3).
- D3 low: Live birth = >=1 live infant after 24 weeks (p.2).
- D4 low: All preprocessing (MissForest, scaling, feature selection) fitted on training set; Platt-scaled calibration; locked test set (~546 events) and temporal/geographic external validation (2,058 cycles, ~920 events) with calibration curves.
- Overall: **high**
- Notes: Three-stage model; rated at the worse model per domain (Stage 1 conditioned on reaching transfer). Stage 3 alone would be D1 low.
- Evidence: Front Endocrinol 2026; 8,389 dev + 2,058 external; SES AUC 0.731 test, 0.719 external (Stage 3).

### 37 Lin 2026
- Intended use: after positive test
- D1 unclear: 127 URSA patients with euploid single blastocyst FET 2019-2025 selected by strict criteria incl. 'complete clinical and follow-up data'; number screened/excluded not reported (p.2).
- D2 low: Day-14 beta-hCG and embryo quality are available at the judged decision point (after the post-transfer hCG test).
- D3 low: Live birth = viable infant after 28 weeks (p.3).
- D4 high: Univariable P<0.5 screening and backward stepwise selection on the whole dataset before the 70/30 split; 48 non-live births in total, test set ~38 patients; very wide AUC CI (0.778-1.000) (Statistical analysis p.3).
- Overall: **high**
- Notes: Univariable selection -> high (PROBAST 4.5).
- Evidence: Front Endocrinol 2026; 127 patients, 79 LB; RF AUC 0.917.

### 38 Liu B 2026
- Intended use: before treatment
- D1 unclear: 220 -> 194 patients with endometrioma after ethanol sclerotherapy; exclusions incl. missing data and loss to follow-up not quantified by reason (Results p.5).
- D2 low: Final predictors (AFC, P on Gn start day, downregulation, cyst diameter, previous LB) known at start of stimulation.
- D3 unclear: CLBR (>=24 wk) from all transfers of one retrieval, but handling of patients with remaining frozen embryos at end of follow-up (cycles to Dec 2024) not described (p.4).
- D4 high: Univariable logistic screening (P<0.10) before Boruta/RFE/mRMR (p.4); 97 events total, validation set 59 patients (~29 events); MICE imputation apparently on full dataset before split.
- Overall: **high**
- Notes: Univariable selection -> high (PROBAST 4.5).
- Evidence: Front Cell Dev Biol 2026; 194 patients, CLBR 50%; XGBoost AUC 0.830.

### 39 Liu L 2026
- Intended use: before treatment
- D1 high: Stage 1 baseline (pre-treatment) model developed only on DOR women who underwent embryo transfer (consecutive patients 'undergoing embryo transfer') (Methods p.2).
- D2 low: Stage-specific predictors (baseline / trigger day / pre-transfer) restricted to variables available at each stage.
- D3 unclear: CLB >=28 wk per retrieval, but cycles with remaining cryopreserved embryos and no further transfers counted as no live birth ('conservative') (p.2).
- D4 high: Best algorithm per stage selected by highest test-set AUC (Model selection p.3), so test set used for model selection; test set has 85 events; raw outputs miscalibrated (HL p<0.001) before Platt scaling.
- Overall: **high**
- Notes: Three-stage model; rated at the worse model per domain. Preprocessing confined to training set (strength).
- Evidence: Front Endocrinol 2026; 1,234 DOR cycles, CLB 22.8%; CatBoost AUC 0.759/0.755/0.793.

### 40 Luo 2026
- Intended use: before transfer
- D1 low: All FET cycles 2021-2023 (development) and 2024 (prospective temporal validation) at one centre; clinical exclusions.
- D2 low: Predictors (age, AMH, prior FET count, blastocysts/high-quality embryos transferred, E2 and EMT on hCG day, embryo type, IUA history) available before FET.
- D3 low: Live birth = infant with vital signs at >=28 weeks (Outcome p.4).
- D4 high: KNN imputation applied to all variables in data preprocessing before the 7:3 split (p.3-4); exclusions for >20% missing not quantified; multivariable significance screening after LASSO. Calibration and prospective temporal validation (1,467 patients) are strengths.
- Overall: **high**
- Notes: D4 high driven by decision rule 3 (imputation before split).
- Evidence: BMC Preg Childbirth 2026; 3,470 dev, 1,467 validation; XGBoost AUC 0.843 test, 0.809 external.

### 41 Minano Masip 2026
- Intended use: before transfer
- D1 unclear: 259 couples with >=1 blastocyst cultured in time-lapse at one clinic; study period stated inconsistently (2012-2019 vs 2016-2019) and selection/exclusion numbers not reported (Methods p.2-3).
- D2 low: 35 clinical/cycle variables and time-lapse frames up to blastocyst stage are available at the embryo-selection/transfer decision.
- D3 unclear: Live birth not defined (no gestational threshold or ascertainment); embryo-level outcome per single embryo transfer (p.3).
- D4 high: 355 transferred embryos (~127 live births) split 70/15/15, so test set ~53 embryos (<100 events); z-score normalisation and mean imputation before split; no calibration; performance reported mainly as accuracy (Sections 2.6-2.8, Table 3).
- Overall: **high**
- Notes: Patient-level partitioning (strength). No calibration -> high (rule 1).
- Evidence: Medicina 2026; 259 couples, 355 transferred embryos; combined SVM+CNN accuracy 0.72 for LB.

### 42 Nowak 2026
- Intended use: before transfer
- D1 unclear: 375 IVF cycles 2013-2022 from one clinic; eligibility criteria and selection not described; 29 'anomalous' records excluded (Methods p.2-3).
- D2 low: Morphokinetic, clinical and semen variables plus number of embryos transferred are available at the transfer decision.
- D3 unclear: Live birth not defined; text also refers to clinical pregnancy outcomes for a restricted SET subset, so the modelled outcome is ambiguous (p.2-3).
- D4 high: 144 expert-generated synthetic records added to the data before the 70/20/10 split, so validation includes synthetic data (p.3); ~80,000 candidate models evaluated against test/validation sets; no calibration (authors acknowledge, Abstract).
- Overall: **high**
- Notes: Decision rule 3 (synthetic data). No calibration -> high (rule 1).
- Evidence: JBRA 2026; 375 cycles; optimised XGBoost AUC 0.927.

### 43 Ortiz 2026
- Intended use: before transfer
- D1 low: All transferred mosaic embryos from PGT-A cycles 2017-2023 in a multicentre clinic group (prospectively maintained database); consistent with embryo-prioritisation use.
- D2 low: Embryo quality, biopsy day and mosaicism characteristics available before transfer.
- D3 unclear: Live birth not defined (threshold/ascertainment); embryo-level labels with some double embryo transfers (Table 1) make attribution unclear.
- D4 high: Class balancing applied to the dataset before the 80/20 split, so test performance is on rebalanced data (Methods p.2); calibration explicitly not assessed (p.7); 96 live births in total, test set ~53 embryos.
- Overall: **high**
- Notes: Decision rule 3 applies. No calibration -> high (rule 1). Final MosaicScore is LR-derived (AUC 0.61).
- Evidence: JARG 2026; 264 mosaic embryos; RF AUC 0.781.

### 44 Priya 2026
- Intended use: before treatment
- D1 high: Stated pre-IVF model, but HFEA records filtered to 'cycles with finished ET' (text copied from Zhang 2022; contradictory NC-IVF vs 'stimulation used' filtering) (Dataset details p.6-7).
- D2 high: Abstract states models incorporate 'both pre cycle and post cycle factors'; fresh/frozen cycle fields included (Abstract; p.7).
- D3 unclear: HFEA 'live birth occurrence' field recoded ('higher than 1' = birth), not defined (p.10).
- D4 high: Dataset balanced on the target before modelling (Fig 4), so evaluation on rebalanced data; split, tuning and missing-data handling not described; no calibration; AUC reported inconsistently (84.9 vs 0.89).
- Overall: **high**
- Notes: Decision rule 3 applies. No calibration -> high (rule 1).
- Evidence: JITM 2026; HFEA 2005-2016; ensemble AUC 0.849/0.89.

### 45 Shao 2026
- Intended use: before treatment
- D1 low: All couples starting IVF/ICSI with own gametes at one centre 2014-2023 (development to Apr 2021, temporal validation after), clinically motivated exclusions; flow in Supp Fig S1 (not in PDF).
- D2 low: Pre-treatment model uses diagnostic-stage variables; post-treatment model uses first-cycle variables (EM, oocytes, 2PN, EUR) available at that later decision point.
- D3 low: Live birth >=24 weeks per complete cycle, first live birth over up to six cycles, censoring handled by discrete-time survival analysis (Outcome p.7-8).
- D4 low: MissForest imputation and scaling fitted on development data only; patient-level CV; temporal validation (613 couples, 373 events) with calibration slope/plots reported (p.9-15). Calibration imperfect at cycles 1-2 but assessed.
- Overall: **low**
- Notes: Two models (pre- and post-treatment); both rated low. Long accrual period acknowledged.
- Evidence: Hum Reprod Open 2026; 1,429 dev / 613 validation couples; BART mean AUC 0.69 (pre) / 0.82 (post).

### 46 Sun 2026
- Intended use: before transfer
- D1 unclear: Endometrioma cohort augmented with 193 women without ovarian masses; external validation cohort is ~90% women without ovarian masses (1,331 of 1,475), inconsistent with the target population (Methods p.3; Fig 1/S1).
- D2 low: Model-1 (age, endometrioma treatment, endometrial thickness, 2PN) available after retrieval/before transfer; Model-2 uses pre-ART variables only.
- D3 low: CLB = live birth >=28 weeks after all embryos or up to three blastocysts of the first ART cycle within 1 year (p.4).
- D4 high: Calibration only via Brier score (no calibration plot/slope) after SMOTE + undersampling of training data without recalibration (p.4, p.11); large drop from test to external AUC (Model-2 0.88 -> 0.69) suggests overfitting; pairwise deletion for missing data.
- Overall: **high**
- Notes: Two models; intended use recorded for Model-1 (listed first). Brier score alone not counted as calibration -> high (rule 1).
- Evidence: Clin Epidemiol 2026; 1,705 dev, 1,475 external; XGBoost AUC 0.90/0.88 test, 0.80/0.69 external.

### 47 Zhang A 2026
- Intended use: before transfer
- D1 unclear: 1,824 -> 1,419 cycles; 194 (10.6%) incomplete cycles without live birth but with surplus embryos excluded, plus cancelled OPU (51) and no-usable-embryo (151) cycles (Fig 1 p.34); multiple cycles per couple.
- D2 low: Final predictors (age, BMI, AFC, AMH, male age, OPU order, usable embryos, high-quality blastocysts) available after embryo culture, before transfer (judged decision point).
- D3 low: CLBR per started cycle/OPU including fresh and all FETs until live birth or embryos exhausted, follow-up to Dec 2025 (p.6).
- D4 high: Final model chosen by an ABscore that combines internal CV and temporal-validation performance with equal weight (p.7), so the validation cohort informed model selection; repeat cycles of the same couple not addressed. Calibration assessed.
- Overall: **high**
- Notes: D1 exclusions >10% treated as unclear (threshold rule). Causal-inference add-ons not appraised.
- Evidence: J Ovarian Res 2026; 1,419 cycles (1,058 couples); GBM AUROC 0.851 temporal.

### 48 Zhao 2026
- Intended use: before transfer
- D1 unclear: Freeze-all FET records 2021-2025; 1,221 records reduced to 990/576/238 after excluding missing or non-adjudicable outcomes and duplicates without numbers per reason (Methods p.2).
- D2 low: Baseline endocrine, ovarian reserve, embryo and regimen variables (and interval days for the second-transfer model) available before the transfer.
- D3 unclear: Live birth not defined (threshold or ascertainment) anywhere in the paper.
- D4 high: MICE imputation and variable removal performed on the raw source table before cohort construction and CV (p.3); feature-ranking stage relative to CV not specified; calibration only on a 'final test split' not otherwise described; second-transfer cohort only 238 cycles.
- Overall: **high**
- Notes: Three cohort-specific models; rated at the worse model. Decision rule 3 (imputation before split).
- Evidence: Front Endocrinol 2026; 990/576/238 cycles; CatBoost AUC 0.704/0.812/0.825.



---

## Extraction_Check verification (done after all 48 ratings were complete)

66 rows checked against the primary PDFs. 60 = yes, 4 = no, 2 = not verifiable (Borji rows 25-26, preprint only; see Revision):
- Row 9 Benchaib 2022: AUC and n correct; blastocyst-level events (74) not reported - article gives 49 deliveries in 196 validation cycles (Table 2 p.5).
- Row 17 Cai 2024: events 16,675 (not 16,673) (Table 1 p.4); AUC 0.71 (0.71-0.72) correct (Table 2 p.7).
- Row 22 Peng 2024: Results/Table 3 give LR 0.671 (0.630-0.713) and RF 0.674 (0.627-0.720); abstract swaps them, so the extracted 0.674 is the RF value.
- Row 25 Borji 2025: PSO+TabTransformer AUC 0.99 (Table 5) / 99.96% (abstract, Table 7); 0.984 is a recall; evaluation by 10-fold CV, no 70/15/15 split.
- Row 26 Borji 2025: no temporal/geographic validation reported.
- Row 33 Wu 2025: test n = 2,345 (Table 3), not 2,346; AUC 0.807 correct.
"yes" rows where n/events were derived by the first rater (not stated in the article) are marked as unverifiable in column L. Internal inconsistencies within articles are noted (Liu L 2024a 81 vs 82; Luo 2026 1,467 vs 1,476; Priya 2026 0.89 vs 84.90; Abdala 2025 SVM/XGBoost order; Bai 2025 abstract quotes training AUC).

## Revision after checking against the ZIP appraisal prompt (29 Oct 2026)
- Borji 2025 set to NOT RATED: the supplied PDF is the author preprint (Word-generated, 27 Dec 2024, no journal header, no DOI), not the published CMPB version required by the protocol. The per-study notes for 19 Borji above are a provisional preprint-based appraisal kept for reference only. Extraction_Check rows 25-26 are now left blank with an explanation (the earlier "no" judgements compared the first rater's numbers with the preprint).
- Calibration rule aligned with the protocol: a Brier score now counts as a calibration assessment. Re-applied to all studies; only Sun 2026 changed (D4 high -> unclear; overall high -> unclear). Peng 2024 and Chen 2026 stay D4 high (univariable selection).
- New prompt-format outputs: second_assessor_ratings.csv, second_assessor_evidence.csv (verbatim quotations), second_assessor_extraction.csv (all live-birth AUCs per study), second_assessor_log.txt (DOI file-matching table, unreadable parts, rules).
- The rule note above that cites Cai 2024 and Xing 2025 by name describes how the D1 rule was worded; each study was rated on its own text.

## Final counts (AI ratings, after revision)
Overall: 43 high / 3 unclear (Qiu 2019, Fatmawati 2026, Sun 2026) / 1 low (Shao 2026) / 1 not rated (Borji 2025).
D1: 8 high / 23 unclear / 16 low. D2: 10 high / 1 unclear / 36 low. D3: 3 high / 20 unclear / 24 low. D4: 41 high / 3 unclear / 3 low. (Each excluding Borji, not rated.)
Extraction_Check: 60 yes / 4 no / 2 not verifiable (Borji rows 25-26).
