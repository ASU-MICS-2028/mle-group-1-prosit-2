# Lecture 1: Machine Learning Course Introduction

> Summary of an audio recording of the lecture. The full transcript is not published. Speech-to-text was imperfect, so check important details against the slide notes in `../lectures/`.

## Recording summary

### Flow Summary
This session introduced the machine learning course: a round of introductions, the curriculum structure, learning outcomes and assessment methods. The lecturer also described their own research background in deep learning and image processing.

### Participant Backgrounds
- Students introduced themselves and their prior institutions and backgrounds (details omitted here).
- The lecturer has a background in computing and engineering, with PhD work on deep learning for high-resolution images.

### Course Content and Pedagogy
- Machine learning is described as "learning by examples": building systems that learn from data to make predictions or inferences.
- The teaching approach is problem-based learning (PBL). There are no exams; assessment is through projects, quizzes and literature reviews.
- Key topics include:
    - Formulating machine learning tasks from real-world problems.
    - Implementing end-to-end machine learning pipelines, from data preparation to deployment.
    - Deriving core ML algorithms from mathematical principles (e.g., gradient descent, backpropagation).
    - Designing mitigation strategies for bias, fairness and ethical issues in ML.

### Next Steps
- The lecturer will introduce the first project (Prosit 1) on Friday.
- Day two will include a short lecture on probability distributions and sampling.

### Decisions Made
- Course assessment breakdown: PBL portfolios (20%), quizzes (20%), literature review assignment (10%), advanced-topic review paper (10%), custom project (50%).

## Our summary

The session was an orientation lecture. It contained no technical content beyond a definition of machine learning, but it set expectations for every prosit, including Prosit 2.

### 1. Lecturer background (brief)
- All of the lecturer's degrees are in computing and engineering: telecoms/VoIP at undergraduate level, then optical communication systems (correction algorithms for nonlinear impairments in optical fibre), then a PhD in deep learning for computer vision.
- The PhD worked on very high-resolution histopathology images (tissue slides used for cancer diagnosis). A single image can be around 2 GB. Downsampling to fit standard model input sizes throws away detail that matters in high-stakes settings like health.
- The approach used wavelet transforms to move images into the frequency domain, kept only the sub-bands (groups of frequencies) relevant to the task, and fed that compact representation to a model. The aim was comparable accuracy on a single GPU instead of several.
- The lecturer noted that a research contribution usually ends up written down mathematically (e.g., a new loss function), which is why the math matters for students on the research track.

### 2. What the course is
- Machine learning is "learning by examples": a system is given examples, learns from them, and makes predictions or inferences on new data.
- **Pedagogy: hybrid problem-based learning.** Students learn by solving real-world problems (prosits) in groups. Short "mini lectures" fill in theory where needed, since many students lack a strong ML background. The lecturer believes solving problems teaches better than lectures. There are no exams and no labs.
- **Structure:** a lot of autonomous time (individual or group), scheduled group sessions for prosits (sometimes facilitated by the lecturer), plus lectures and class activities.
- **Compute:** coursework should fit within free resources such as Google Colab. The department has a GPU cluster for projects that need more.
- **Textbooks:** *An Introduction to Statistical Learning* (the link in the syllabus was wrong, but the book is available online) and *Hands-On Machine Learning* with Python and PyTorch. The class will use PyTorch.
- **Additional reading:** Goodfellow et al., *Deep Learning*; *Interpretable Machine Learning*; *Fairness and Machine Learning*. Responsible-AI papers: *Datasheets for Datasets* (standard dataset documentation to improve transparency and reduce dataset-level bias), *Model Cards for Model Reporting*, and *Gender Shades* (accuracy gaps by gender and skin type in commercial face classifiers). The lecturer used these to explain why models trained on biased data reproduce that bias, for example surveillance systems built abroad that disproportionately flag Black people.

### 3. Learning outcomes (as stated)
1. Formulate real-world problems as ML tasks.
2. Implement **end-to-end** ML pipelines: data preparation, feature engineering, model selection, evaluation **and deployment**. The lecturer stressed that a model that only runs in a notebook is not end-to-end. It should end in something usable, such as a web or mobile app. MLOps will be touched on near the end of the course. In answer to a student's question, the lecturer said MLOps is not strictly required of an ML engineer but is worth learning, and that AI agents now make deployment easier.
3. Derive core ML algorithms from mathematical principles (gradient descent, backpropagation). This is assessed through quizzes, the technical documentation in PBL portfolios, and model evaluation.
4. Design mitigation strategies for bias, fairness and ethics. The lecturer called this "very important": datasets naturally contain bias, so do not take data as-is and train on it, and every ML project should include an ethics discussion.
5. Communicate concepts and results to technical and non-technical audiences, through video presentations and the final capstone defence.
6. Read and critically evaluate ML research papers, especially important for the research (MPhil) track.

The course also maps to the institution's broader learning goals: ethics and civic engagement, critical thinking, communication, leadership and teamwork, and technological competence.

### 4. Assessment
| Component | Weight | Notes |
|---|---|---|
| PBL portfolios (prosits, group work) | 20% | Each prosit runs about three weeks and ends with a short presentation |
| Quizzes | 20% | About three, testing the fundamentals |
| Literature review assignment | 10% | Synthesis on a topic set by the lecturer |
| Advanced-topic review paper | 10% | Group review and presentation on a trending advanced ML/DL topic |
| Custom project | 50% | End-to-end ML project, starts after the mid-semester break (about 6–7 weeks), small groups (around 3), topics proposed by students |

On literature reviews, the lecturer said a proper review **critiques** the work instead of summarising it: limitations, what could have been done better, what the authors should have considered. Use the analogy of finding the missing brick in a wall, i.e. the research gap. Tip: when entering a field, start with review papers and read their "future work" and "limitations" sections to find gaps.

### 5. Preview of Prosit 1
- Day two would bring a 45–60 minute lecture on probability distributions and sampling, because Prosit 1 relies on them. Prosit 1 would also involve data preprocessing and looking out for data issues. The transcript is garbled here (it reads "digitality"), which may mean data quality or leakage.
- The lecturer wanted students to work with **real data**. The planned theme was malaria in Africa: donors and partners fund governments to distribute mosquito nets and run other interventions. The recording ends mid-sentence at this point.

### What the lecturer said about the prosits
- Prosits are group problems of about three weeks each. They are graded as PBL portfolios (20% of the course) and each ends with a short presentation. Being able to explain the work to non-technical people is an explicitly assessed skill.
- Portfolios should include **technical documentation**. That documentation, together with model evaluation, is one of the ways the "derive from math" outcome is assessed.
- **Deployment is expected** in the end-to-end sense. Do not stop at the notebook.
- **Bias, fairness and ethics are expected in every project**, not as an afterthought. Raw data is biased, and a model trained on it will perpetuate that bias.
- Real (not toy) datasets will be used wherever possible.

### Relevance to Prosit 2
- **End-to-end, including deployment:** the Prosit 2 scorer with reason codes is the "not just a notebook" deliverable the lecturer described. It should be runnable and usable, and ideally wrapped as a small app or CLI.
- **Fairness audit:** this matches outcome 4 and the *Gender Shades* / *Datasheets* / *Model Cards* readings. Report error rates and approval rates by group, explain the mitigation, and consider writing a model card and a datasheet for the Kenyan loan data.
- **Kenya to Ghana shift:** this echoes the lecturer's warning that models built in one population can fail or discriminate in another (the surveillance example). Treat the shift analysis as an ethics issue as well as a technical one.
- **Communication:** the presentation must make calibration, the cost-based threshold and the bootstrap confidence intervals understandable to a non-technical lending panel.
- **Math grounding:** be ready to explain the loss and objective behind the models, calibration and threshold choice from first principles, since quizzes and documentation assess this.
